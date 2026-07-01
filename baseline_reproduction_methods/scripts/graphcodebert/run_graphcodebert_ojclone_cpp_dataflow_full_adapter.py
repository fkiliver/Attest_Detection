from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASELINE_ROOT = ROOT / "eviclone_runs" / "baseline_reproduction"
DEFAULT_SOURCE = BASELINE_ROOT / "graphcodebert_dsfm_splits" / "OJClone"
DEFAULT_DATASET = BASELINE_ROOT / "graphcodebert_ojclone_cpp_dataflow_full_adapter_dataset"
DEFAULT_OUTPUT = BASELINE_ROOT / "graphcodebert_ojclone_cpp_dataflow_full_adapter_model"
DEFAULT_METRICS = BASELINE_ROOT / "graphcodebert_ojclone_cpp_dataflow_full_adapter_metrics.json"
DEFAULT_REPORT = BASELINE_ROOT / "graphcodebert_ojclone_cpp_dataflow_full_adapter_metrics.md"
RUN_DIR = ROOT.parent / "source_snapshots" / "GraphCodeBERT" / "clonedetection"
PYTHON = Path(sys.executable)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full OJClone through a retained GraphCodeBERT C++ data-flow adapter.")
    parser.add_argument("--source-data-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metrics-path", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--metrics-report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--code-length", type=int, default=512)
    parser.add_argument("--data-flow-length", type=int, default=128)
    parser.add_argument("--train-batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--keep-step-checkpoints",
        action="store_true",
        help="Keep upstream checkpoint-step-* model saves. By default, step checkpoints are skipped to avoid filling disk.",
    )
    args = parser.parse_args()

    source_data_dir = resolve_path(args.source_data_dir)
    dataset_dir = resolve_path(args.dataset_dir)
    output_dir = resolve_path(args.output_dir)
    metrics_path = resolve_path(args.metrics_path)
    metrics_report_path = resolve_path(args.metrics_report_path)
    for path in [dataset_dir, output_dir, metrics_path, metrics_report_path]:
        ensure_under_baseline(path)
    if not PYTHON.exists():
        raise FileNotFoundError(PYTHON)
    if not RUN_DIR.exists():
        raise FileNotFoundError(RUN_DIR)

    clean_dir(dataset_dir)
    clean_dir(output_dir)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    source_summary = read_json(source_data_dir / "export_summary.json")
    copy_full_dataset(source_data_dir=source_data_dir, dataset_dir=dataset_dir)
    split_rows = extract_split_rows(source_summary)
    manifest = write_adapter_manifest(dataset_dir=dataset_dir, source_summary=source_summary, args=args)

    start = time.time()
    run_log = output_dir / "train_eval_test.log"
    wrapper_path = output_dir / "graphcodebert_cpp_adapter_wrapper.py"
    timing_path = output_dir / "run_timing.json"
    skip_step_checkpoints = not args.keep_step_checkpoints
    wrapper_path.write_text(wrapper_source(skip_step_checkpoints=skip_step_checkpoints), encoding="utf-8")

    run_cmd = [
        str(PYTHON),
        str(wrapper_path),
        "--train_data_file",
        str(dataset_dir / "train.txt"),
        "--eval_data_file",
        str(dataset_dir / "valid.txt"),
        "--test_data_file",
        str(dataset_dir / "test.txt"),
        "--output_dir",
        str(output_dir),
        "--model_name_or_path",
        "microsoft/graphcodebert-base",
        "--config_name",
        "microsoft/graphcodebert-base",
        "--tokenizer_name",
        "microsoft/graphcodebert-base",
        "--do_train",
        "--do_eval",
        "--do_test",
        "--code_length",
        str(args.code_length),
        "--data_flow_length",
        str(args.data_flow_length),
        "--train_batch_size",
        str(args.train_batch_size),
        "--eval_batch_size",
        str(args.eval_batch_size),
        "--gradient_accumulation_steps",
        str(args.gradient_accumulation_steps),
        "--learning_rate",
        "2e-5",
        "--epochs",
        str(args.epochs),
        "--num_workers",
        "0",
        "--seed",
        str(args.seed),
    ]
    run_proc = run_logged(run_cmd, cwd=RUN_DIR, log_path=run_log)
    elapsed = time.time() - start
    if run_proc.returncode != 0:
        write_timing(
            path=timing_path,
            args=args,
            run_cmd=run_cmd,
            elapsed=elapsed,
            exit_code=run_proc.returncode,
            status="graphcodebert_failed",
            split_rows=split_rows,
            manifest=manifest,
            skip_step_checkpoints=skip_step_checkpoints,
        )
        return run_proc.returncode

    eval_cmd = [
        str(PYTHON),
        str(ROOT / "scripts" / "evaluate_triplet_predictions.py"),
        "--gold",
        str(dataset_dir / "test.txt"),
        "--predictions",
        str(output_dir / "predictions.txt"),
        "--output",
        str(metrics_path),
        "--report",
        str(metrics_report_path),
        "--dataset",
        "OJClone",
        "--method",
        "GraphCodeBERT-C++-adapter",
        "--source",
        "tree_sitter_languages/cpp adapter over official GraphCodeBERT clonedetection run.py",
    ]
    eval_proc = subprocess.run(eval_cmd, cwd=ROOT, text=True)
    status = "completed" if eval_proc.returncode == 0 else "evaluation_failed"
    write_timing(
        path=timing_path,
        args=args,
        run_cmd=run_cmd,
        elapsed=elapsed,
        exit_code=eval_proc.returncode,
        status=status,
        split_rows=split_rows,
        manifest=manifest,
        skip_step_checkpoints=skip_step_checkpoints,
    )
    print(
        json.dumps(
            {
                "status": status,
                "dataset_dir": str(dataset_dir),
                "output_dir": str(output_dir),
                "metrics": str(metrics_path),
                "timing": str(timing_path),
                "rows": split_rows,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return eval_proc.returncode


def wrapper_source(*, skip_step_checkpoints: bool) -> str:
    return textwrap.dedent(
        f"""
        from __future__ import annotations

        import sys
        from pathlib import Path

        run_dir = Path.cwd()
        if str(run_dir) not in sys.path:
            sys.path.insert(0, str(run_dir))

        import torch
        import run as graphcodebert_run
        from tree_sitter_languages import get_parser

        graphcodebert_run.parsers["java"] = [get_parser("cpp"), graphcodebert_run.DFG_java]
        _SKIP_STEP_CHECKPOINTS = {skip_step_checkpoints!r}
        _ORIGINAL_TORCH_SAVE = torch.save

        def _eviclone_torch_save(obj, f, *args, **kwargs):
            path = str(f).replace("\\\\", "/")
            if _SKIP_STEP_CHECKPOINTS and "/checkpoint-step-" in path:
                return None
            return _ORIGINAL_TORCH_SAVE(obj, f, *args, **kwargs)

        torch.save = _eviclone_torch_save

        if __name__ == "__main__":
            graphcodebert_run.main()
        """
    ).lstrip()


def copy_full_dataset(*, source_data_dir: Path, dataset_dir: Path) -> None:
    for name in ["data.jsonl", "train.txt", "valid.txt", "test.txt", "export_summary.json"]:
        src = source_data_dir / name
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copyfile(src, dataset_dir / name)


def write_adapter_manifest(*, dataset_dir: Path, source_summary: dict[str, Any], args: argparse.Namespace) -> str:
    manifest_path = dataset_dir / "adapter_manifest.json"
    payload = {
        "schema_version": "eviclone-graphcodebert-ojclone-cpp-adapter-dataset/v1",
        "dataset": "OJClone",
        "method": "GraphCodeBERT-C++-adapter",
        "source_export_summary": source_summary,
        "adapter": {
            "type": "runtime parser adapter",
            "parser": "tree_sitter_languages.get_parser('cpp')",
            "dfg_function": "GraphCodeBERT DFG_java reused as a best-effort adapter",
            "upstream_slot": "graphcodebert_run.parsers['java']",
            "official_upstream_supported": False,
        },
        "run_protocol": {
            "split": "full OJClone train/valid/test from DSFM export",
            "code_length": args.code_length,
            "data_flow_length": args.data_flow_length,
            "train_batch_size": args.train_batch_size,
            "eval_batch_size": args.eval_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "epochs": args.epochs,
            "seed": args.seed,
        },
        "claim_boundary": (
            "This is a project-defined C/C++ adapter for GraphCodeBERT on OJClone, not a documented official "
            "Microsoft GraphCodeBERT OJClone protocol. It can fill an adapter/variant cell only with an explicit label."
        ),
    }
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(manifest_path)


def extract_split_rows(source_summary: dict[str, Any]) -> dict[str, int]:
    splits = source_summary.get("splits") if isinstance(source_summary.get("splits"), dict) else {}
    return {
        "train": int(splits.get("train", {}).get("rows") or 0),
        "valid": int(splits.get("val", splits.get("valid", {})).get("rows") or 0),
        "test": int(splits.get("test", {}).get("rows") or 0),
    }


def run_logged(cmd: list[str], *, cwd: Path, log_path: Path) -> subprocess.CompletedProcess[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write("COMMAND " + json.dumps(cmd, ensure_ascii=False) + "\n\n")
        log.flush()
        proc = subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, text=True)
    return proc


def write_timing(
    *,
    path: Path,
    args: argparse.Namespace,
    run_cmd: list[str],
    elapsed: float,
    exit_code: int,
    status: str,
    split_rows: dict[str, int],
    manifest: str,
    skip_step_checkpoints: bool,
) -> None:
    payload: dict[str, Any] = {
        "schema_version": "eviclone-graphcodebert-ojclone-cpp-adapter-full/v1",
        "status": status,
        "exit_code": exit_code,
        "elapsed_seconds": round(elapsed, 3),
        "run_command": run_cmd,
        "split_rows": split_rows,
        "code_length": args.code_length,
        "data_flow_length": args.data_flow_length,
        "train_batch_size": args.train_batch_size,
        "eval_batch_size": args.eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "epochs": args.epochs,
        "seed": args.seed,
        "skip_step_checkpoints": skip_step_checkpoints,
        "adapter_manifest": manifest,
        "parser_patch": "tree_sitter_languages.get_parser('cpp') assigned to graphcodebert_run.parsers['java']",
        "claim_boundary": (
            "This is a full-split project-defined C/C++ adapter run for GraphCodeBERT on OJClone. It is not a "
            "documented official Microsoft GraphCodeBERT OJClone protocol and must be labeled as an adapter/variant."
        ),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj


def resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else (ROOT / path).resolve()


def ensure_under_baseline(path: Path) -> None:
    resolved = path.resolve()
    baseline = BASELINE_ROOT.resolve()
    if resolved == baseline:
        raise ValueError(f"refusing to operate on baseline root directly: {resolved}")
    if baseline not in resolved.parents:
        raise ValueError(f"refusing to write outside baseline_reproduction: {resolved}")


def clean_dir(path: Path) -> None:
    if path.exists():
        ensure_under_baseline(path)
        shutil.rmtree(path)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
