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
DEFAULT_SOURCE = ROOT / "eviclone_runs" / "baseline_reproduction" / "graphcodebert_dsfm_splits" / "OJClone"
DEFAULT_SUBSET = ROOT / "eviclone_runs" / "baseline_reproduction" / "graphcodebert_ojclone_cpp_dataflow_smoke_dataset"
DEFAULT_OUTPUT = ROOT / "eviclone_runs" / "baseline_reproduction" / "graphcodebert_ojclone_cpp_dataflow_smoke_model"
DEFAULT_METRICS = ROOT / "eviclone_runs" / "baseline_reproduction" / "graphcodebert_ojclone_cpp_dataflow_smoke_metrics.json"
DEFAULT_REPORT = ROOT / "eviclone_runs" / "baseline_reproduction" / "graphcodebert_ojclone_cpp_dataflow_smoke_metrics.md"
BASELINE_ROOT = ROOT / "eviclone_runs" / "baseline_reproduction"
RUN_DIR = ROOT.parent / "source_snapshots" / "GraphCodeBERT" / "clonedetection"
PYTHON = Path(sys.executable)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an OJClone C++ data-flow smoke for the official GraphCodeBERT clone script.")
    parser.add_argument("--source-data-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--subset-dir", type=Path, default=DEFAULT_SUBSET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metrics-path", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--metrics-report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--train-rows", type=int, default=64)
    parser.add_argument("--valid-rows", type=int, default=32)
    parser.add_argument("--test-rows", type=int, default=32)
    parser.add_argument("--code-length", type=int, default=128)
    parser.add_argument("--data-flow-length", type=int, default=32)
    parser.add_argument("--train-batch-size", type=int, default=1)
    parser.add_argument("--eval-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--dfg-adapter",
        choices=["java", "csharp", "empty"],
        default="java",
        help="DFG function paired with the C++ parser. java preserves the original shim; empty disables DFG nodes.",
    )
    parser.add_argument(
        "--keep-step-checkpoints",
        action="store_true",
        help="Keep upstream checkpoint-step-* model saves. By default, step checkpoints are skipped to avoid filling disk.",
    )
    args = parser.parse_args()

    source_data_dir = resolve_path(args.source_data_dir)
    subset_dir = resolve_path(args.subset_dir)
    output_dir = resolve_path(args.output_dir)
    metrics_path = resolve_path(args.metrics_path)
    metrics_report_path = resolve_path(args.metrics_report_path)
    ensure_under_baseline(subset_dir)
    ensure_under_baseline(output_dir)
    ensure_under_baseline(metrics_path)
    ensure_under_baseline(metrics_report_path)

    if not PYTHON.exists():
        raise FileNotFoundError(PYTHON)
    if not RUN_DIR.exists():
        raise FileNotFoundError(RUN_DIR)

    clean_dir(subset_dir)
    clean_dir(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    subset_dir.mkdir(parents=True, exist_ok=True)

    subset_log = output_dir / "subset_build.log"
    run_log = output_dir / "train_eval_test.log"
    wrapper_path = output_dir / "graphcodebert_cpp_wrapper.py"
    timing_path = output_dir / "run_timing.json"
    skip_step_checkpoints = not args.keep_step_checkpoints
    wrapper_path.write_text(
        wrapper_source(skip_step_checkpoints=skip_step_checkpoints, dfg_adapter=args.dfg_adapter),
        encoding="utf-8",
    )

    start = time.time()
    subset_cmd = [
        str(PYTHON),
        str(ROOT / "scripts" / "build_triplet_split_subset.py"),
        "--source-dir",
        str(source_data_dir),
        "--output-dir",
        str(subset_dir),
        "--dataset-name",
        "OJClone-cpp-dataflow-smoke",
        "--train-rows",
        str(args.train_rows),
        "--valid-rows",
        str(args.valid_rows),
        "--test-rows",
        str(args.test_rows),
        "--seed",
        "20260627",
        "--balanced",
    ]
    subset_proc = run_logged(subset_cmd, cwd=ROOT, log_path=subset_log)
    if subset_proc.returncode != 0:
        write_timing(timing_path, args, subset_cmd, [], time.time() - start, subset_proc.returncode, "subset_failed", skip_step_checkpoints)
        return subset_proc.returncode

    run_cmd = [
        str(PYTHON),
        str(wrapper_path),
        "--train_data_file",
        str(subset_dir / "train.txt"),
        "--eval_data_file",
        str(subset_dir / "valid.txt"),
        "--test_data_file",
        str(subset_dir / "test.txt"),
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
        write_timing(timing_path, args, subset_cmd, run_cmd, elapsed, run_proc.returncode, "graphcodebert_failed", skip_step_checkpoints)
        return run_proc.returncode

    eval_cmd = [
        str(PYTHON),
        str(ROOT / "scripts" / "evaluate_triplet_predictions.py"),
        "--gold",
        str(subset_dir / "test.txt"),
        "--predictions",
        str(output_dir / "predictions.txt"),
        "--output",
        str(metrics_path),
        "--report",
        str(metrics_report_path),
        "--dataset",
        "OJClone-cpp-dataflow-smoke",
        "--method",
        "GraphCodeBERT-C++-dataflow-smoke",
        "--source",
        "tree_sitter_languages/cpp runtime patch over official GraphCodeBERT clonedetection run.py",
    ]
    eval_proc = subprocess.run(eval_cmd, cwd=ROOT, text=True)
    status = "completed" if eval_proc.returncode == 0 else "evaluation_failed"
    write_timing(timing_path, args, subset_cmd, run_cmd, elapsed, eval_proc.returncode, status, skip_step_checkpoints)
    print(
        json.dumps(
            {
                "status": status,
                "subset_dir": str(subset_dir),
                "output_dir": str(output_dir),
                "metrics": str(metrics_path),
                "timing": str(timing_path),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return eval_proc.returncode


def wrapper_source(*, skip_step_checkpoints: bool, dfg_adapter: str) -> str:
    if dfg_adapter == "java":
        dfg_source = 'graphcodebert_run.DFG_java'
    elif dfg_adapter == "csharp":
        dfg_source = 'DFG_csharp'
    else:
        dfg_source = '_eviclone_empty_dfg'
    return textwrap.dedent(
        f"""
        from __future__ import annotations

        import sys
        from pathlib import Path

        run_dir = Path({str(RUN_DIR)!r})
        if str(run_dir) not in sys.path:
            sys.path.insert(0, str(run_dir))

        import torch
        import run as graphcodebert_run
        from parser import DFG_csharp
        from tree_sitter_languages import get_parser

        def _eviclone_empty_dfg(root_node, index_to_code, states):
            return [], states

        graphcodebert_run.parsers["java"] = [get_parser("cpp"), {dfg_source}]
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


def run_logged(cmd: list[str], *, cwd: Path, log_path: Path) -> subprocess.CompletedProcess[str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write("COMMAND " + json.dumps(cmd, ensure_ascii=False) + "\n\n")
        log.flush()
        proc = subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, text=True)
    return proc


def write_timing(
    path: Path,
    args: argparse.Namespace,
    subset_cmd: list[str],
    run_cmd: list[str],
    elapsed: float,
    exit_code: int,
    status: str,
    skip_step_checkpoints: bool,
) -> None:
    payload: dict[str, Any] = {
        "schema_version": "eviclone-graphcodebert-ojclone-cpp-dataflow-smoke/v1",
        "status": status,
        "exit_code": exit_code,
        "elapsed_seconds": round(elapsed, 3),
        "subset_command": subset_cmd,
        "run_command": run_cmd,
        "train_rows": args.train_rows,
        "valid_rows": args.valid_rows,
        "test_rows": args.test_rows,
        "code_length": args.code_length,
        "data_flow_length": args.data_flow_length,
        "train_batch_size": args.train_batch_size,
        "eval_batch_size": args.eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "epochs": args.epochs,
        "seed": args.seed,
        "skip_step_checkpoints": skip_step_checkpoints,
        "parser_patch": "tree_sitter_languages.get_parser('cpp') assigned to graphcodebert_run.parsers['java']",
        "claim_boundary": (
            "This is a smoke test for local C/C++ parser feasibility on OJClone. It is not a manuscript "
            "GraphCodeBERT/OJClone table cell because it uses a small subset and a runtime parser shim."
        ),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


if __name__ == "__main__":
    raise SystemExit(main())
