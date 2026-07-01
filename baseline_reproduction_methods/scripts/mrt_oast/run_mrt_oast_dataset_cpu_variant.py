from __future__ import annotations

import argparse
import builtins
import csv
import json
import os
import runpy
import shutil
import sys
import time
from pathlib import Path
from typing import Any

from run_mrt_oast_ojclone_cpu_smoke import parse_new_result_row, subset_csv, write_json


DEFAULT_ROOT = Path("external") / "MRT-OAST"
DEFAULT_REPORT_DIR = Path("eviclone_runs") / "baseline_reproduction"

DATASET_CONFIG = {
    "BCB": {
        "data": "BCB_with_AST+OAST.csv",
        "train": "BCB_train.csv",
        "valid": "BCB_valid.csv",
        "test": "BCB_test.csv",
        "dictionary_prefix": "BCB",
    },
    "GCJ": {
        "data": "GCJ_with_AST+OAST.csv",
        "train": "GCJ_train11.csv",
        "valid": "GCJ_valid.csv",
        "test": "GCJ_test.csv",
        "dictionary_prefix": "GCJ",
    },
    "OJClone": {
        "data": "OJClone_with_AST+OAST.csv",
        "train": "OJClone_train.csv",
        "valid": "OJClone_valid.csv",
        "test": "OJClone_test.csv",
        "dictionary_prefix": "OJClone",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an MRT-OAST dataset variant with retained reproduction artifacts.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--dataset", choices=sorted(DATASET_CONFIG), required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--train-rows", type=int, default=512)
    parser.add_argument("--valid-rows", type=int, default=256)
    parser.add_argument("--test-rows", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--sen-max-len", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--valid-step", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument(
        "--valid-threshold",
        type=int,
        default=None,
        help="Optional MRT-OAST validation threshold override. Omit to keep main_batch.py's default.",
    )
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    dataset = args.dataset
    run_suffix = "cpu_variant" if args.device == "cpu" else "cuda_variant"
    output_dir = (args.output_dir or DEFAULT_REPORT_DIR / f"mrt_oast_{dataset.lower()}_{run_suffix}").resolve()
    input_dir = output_dir / "input"
    model_dir = output_dir / "model"
    output_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    config = DATASET_CONFIG[dataset]
    source_dir = repo_root / "origindata"
    required = [
        source_dir / config["data"],
        source_dir / config["train"],
        source_dir / config["valid"],
        source_dir / config["test"],
        source_dir / f"{config['dictionary_prefix']}_OAST_dictionary.txt",
    ]
    missing = [str(path) for path in required if not path.exists()]
    json_path = output_dir / f"mrt_oast_{dataset.lower()}_{run_suffix}.json"
    report_path = output_dir / f"mrt_oast_{dataset.lower()}_{run_suffix}.md"
    if missing:
        summary = {
            "schema_version": "eviclone-mrt-oast-dataset-variant/v2",
            "status": "missing_required_input",
            "dataset": dataset,
            "missing": missing,
        }
        write_outputs(summary, json_path, report_path)
        return 2

    dict_dst = input_dir / f"{config['dictionary_prefix']}_OAST_dictionary.txt"
    data_dst = input_dir / config["data"]
    train_dst = input_dir / f"{dataset}_train_{run_suffix}.csv"
    valid_dst = input_dir / f"{dataset}_valid_{run_suffix}.csv"
    test_dst = input_dir / f"{dataset}_test_{run_suffix}.csv"
    shutil.copy2(source_dir / f"{config['dictionary_prefix']}_OAST_dictionary.txt", dict_dst)
    prepare_pairs(source_dir / config["train"], train_dst, args.train_rows)
    prepare_pairs(source_dir / config["valid"], valid_dst, args.valid_rows)
    prepare_pairs(source_dir / config["test"], test_dst, args.test_rows)
    subset_data_csv(source_dir / config["data"], data_dst, pair_keys([train_dst, valid_dst, test_dst]))

    start = time.time()
    status = "unknown"
    error: str | None = None
    old_cwd = Path.cwd()
    old_argv = sys.argv[:]
    old_sys_path = sys.path[:]
    original_open = builtins.open
    result_csv = repo_root / "model" / "result.csv"
    before_result_size = result_csv.stat().st_size if result_csv.exists() else 0
    try:
        os.chdir(repo_root)
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        (repo_root / "pic").mkdir(exist_ok=True)
        (repo_root / "model").mkdir(exist_ok=True)
        patch_torch_runtime(force_cpu_cuda_methods=args.device == "cpu")
        monkeypatch_text_open_utf8()
        sys.argv = [
            "main_batch.py",
            "--save",
            str(model_dir),
            "--tag",
            f"{dataset}_{args.device.upper()}_VARIANT",
            "--data",
            str(data_dst),
            "--train_pair",
            str(train_dst),
            "--valid_pair",
            str(valid_dst),
            "--test_pair",
            str(test_dst),
            "--dictionary",
            str(input_dir / f"{config['dictionary_prefix']}_XXX_dictionary.txt"),
            "--ast_type",
            "OAST",
            "--epochs",
            str(args.epochs),
            "--batch_size",
            str(args.batch_size),
            "--sen_max_len",
            str(args.sen_max_len),
            "--valid_step",
            str(args.valid_step),
            "--threshold",
            str(args.threshold),
        ]
        if args.valid_threshold is not None:
            sys.argv.extend(["--valid_threshold", str(args.valid_threshold)])
        if args.device == "cuda":
            sys.argv.append("--cuda")
        runpy.run_path(str(repo_root / "main_batch.py"), run_name="__main__")
        status = "completed"
    except Exception as exc:  # pragma: no cover - retained diagnostic artifact path
        status = "failed"
        error = repr(exc)
    finally:
        builtins.open = original_open
        sys.argv = old_argv
        sys.path = old_sys_path
        os.chdir(old_cwd)

    retained_outputs = copy_wrong_outputs(repo_root, output_dir, dataset)
    summary = {
        "schema_version": "eviclone-mrt-oast-dataset-variant/v2",
        "status": status,
        "error": error,
        "dataset": dataset,
        "elapsed_seconds": round(time.time() - start, 3),
        "repo_root": str(repo_root),
        "output_dir": str(output_dir),
        "model_dir": str(model_dir),
        "input_dir": str(input_dir),
        "rows": {
            "data": count_csv_records(data_dst),
            "train": count_csv_records(train_dst),
            "valid": count_csv_records(valid_dst),
            "test": count_csv_records(test_dst),
        },
        "source_files": {
            "data": str(source_dir / config["data"]),
            "train": str(source_dir / config["train"]),
            "valid": str(source_dir / config["valid"]),
            "test": str(source_dir / config["test"]),
        },
        "retained_outputs": retained_outputs,
        "protocol": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "sen_max_len": args.sen_max_len,
            "valid_step": args.valid_step,
            "ast_type": "OAST",
            "threshold": args.threshold,
            "valid_threshold": args.valid_threshold if args.valid_threshold is not None else "main_batch_default",
            "device": args.device,
            "cuda_patch": "torch Tensor/Module cuda methods return self" if args.device == "cpu" else None,
            "split": split_label(args.train_rows, args.valid_rows, args.test_rows),
            "full_split": args.train_rows <= 0 and args.valid_rows <= 0 and args.test_rows <= 0,
        },
        "runtime": collect_torch_runtime(args.device),
        "metrics": parse_new_result_row(result_csv, before_result_size) if status == "completed" else None,
        "table_policy": table_policy(args),
    }
    write_outputs(summary, json_path, report_path)
    print(json.dumps({"status": status, "output": str(json_path), "report": str(report_path)}, sort_keys=True))
    return 0 if status == "completed" else 2


def prepare_pairs(src: Path, dst: Path, rows: int) -> None:
    if rows <= 0:
        shutil.copy2(src, dst)
        return
    subset_csv(src, dst, rows)


def patch_torch_runtime(force_cpu_cuda_methods: bool) -> None:
    import torch

    original_load = torch.load

    def _load_with_legacy_default(*args, **kwargs):  # noqa: ANN002, ANN003
        kwargs.setdefault("weights_only", False)
        return original_load(*args, **kwargs)

    torch.load = _load_with_legacy_default  # type: ignore[assignment]

    if not force_cpu_cuda_methods:
        return

    def _identity_cuda(self, *args, **kwargs):  # noqa: ANN001, ANN202
        return self

    torch.Tensor.cuda = _identity_cuda  # type: ignore[method-assign]
    torch.nn.Module.cuda = _identity_cuda  # type: ignore[method-assign]


def monkeypatch_text_open_utf8() -> None:
    original_open = builtins.open

    def _open_with_utf8_default(file, mode="r", buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):  # noqa: ANN001, ANN202
        if "b" not in mode and encoding is None:
            encoding = "utf-8"
            if any(flag in mode for flag in ("w", "a", "x")) and errors is None:
                errors = "replace"
        return original_open(file, mode, buffering, encoding, errors, newline, closefd, opener)

    builtins.open = _open_with_utf8_default


def count_csv_records(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def copy_wrong_outputs(repo_root: Path, output_dir: Path, dataset: str) -> dict[str, str]:
    wrong_dir = repo_root / "wrong"
    artifacts = {
        "predictions": wrong_dir / "preds.csv",
        "wrong_list_detail": wrong_dir / "wrong_list_detail.csv",
        "wronglist": wrong_dir / "wronglist.txt",
    }
    retained: dict[str, str] = {}
    for key, src in artifacts.items():
        if not src.exists():
            continue
        dst = output_dir / f"mrt_oast_{dataset.lower()}_{key}{src.suffix}"
        shutil.copy2(src, dst)
        retained[key] = str(dst)
    return retained


def pair_keys(pair_paths: list[Path]) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for path in pair_paths:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.reader(handle)
            next(reader, None)
            for row in reader:
                if len(row) >= 4:
                    keys.add((row[0], row[1]))
                    keys.add((row[2], row[3]))
    return keys


def subset_data_csv(src: Path, dst: Path, keys: set[tuple[str, str]]) -> None:
    with src.open("r", encoding="utf-8", errors="replace", newline="") as in_handle:
        reader = csv.reader(in_handle)
        header = next(reader)
        rows = [row for row in reader if len(row) >= 2 and (row[0], row[1]) in keys]
    found = {(row[0], row[1]) for row in rows}
    missing = sorted(keys - found)
    if missing:
        raise ValueError(f"{len(missing)} pair data records missing from {src}")
    with dst.open("w", encoding="utf-8", newline="") as out_handle:
        writer = csv.writer(out_handle)
        writer.writerow(header)
        writer.writerows(rows)


def write_outputs(summary: dict[str, Any], json_path: Path, report_path: Path) -> None:
    write_json(json_path, summary)
    report_path.write_text(render_markdown(summary), encoding="utf-8")


def split_label(train_rows: int, valid_rows: int, test_rows: int) -> str:
    if train_rows <= 0 and valid_rows <= 0 and test_rows <= 0:
        return "full official split"
    return "row-limited official split"


def table_policy(args: argparse.Namespace) -> str:
    if args.device == "cuda" and args.train_rows <= 0 and args.valid_rows <= 0 and args.test_rows <= 0:
        return (
            "CUDA run over the full official split from the official MRT-OAST code/data. Use as a reproduced variant "
            "cell unless all hyperparameters exactly match the paper/default protocol."
        )
    return (
        "Variant run from the official MRT-OAST code/data. This is execution evidence; only use as a formal paper "
        "SOTA A/P/R/F1 cell when the split and hyperparameters match the claimed protocol."
    )


def collect_torch_runtime(requested_device: str) -> dict[str, Any]:
    try:
        import torch

        runtime: dict[str, Any] = {
            "python": sys.version,
            "torch": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "requested_device": requested_device,
        }
        if torch.cuda.is_available():
            runtime["gpu_name"] = torch.cuda.get_device_name(0)
            runtime["gpu_total_memory_bytes"] = torch.cuda.get_device_properties(0).total_memory
            runtime["gpu_allocated_bytes"] = torch.cuda.memory_allocated(0)
            runtime["gpu_reserved_bytes"] = torch.cuda.memory_reserved(0)
        return runtime
    except Exception as exc:  # pragma: no cover - diagnostic artifact path
        return {"requested_device": requested_device, "error": repr(exc)}


def render_markdown(summary: dict[str, Any]) -> str:
    metrics = summary.get("metrics") or {}
    rows = summary.get("rows") or {}
    protocol = summary.get("protocol") or {}
    return "\n".join(
        [
            f"# MRT-OAST {summary.get('dataset')} Variant",
            "",
            f"Status: `{summary.get('status')}`",
            "",
            str(summary.get("table_policy", "")),
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| data rows | {rows.get('data', '')} |",
            f"| train rows | {rows.get('train', '')} |",
            f"| valid rows | {rows.get('valid', '')} |",
            f"| test rows | {rows.get('test', '')} |",
            f"| epochs | {protocol.get('epochs', '')} |",
            f"| batch size | {protocol.get('batch_size', '')} |",
            f"| sen_max_len | {protocol.get('sen_max_len', '')} |",
            f"| valid_step | {protocol.get('valid_step', '')} |",
            f"| device | {protocol.get('device', '')} |",
            f"| split | {protocol.get('split', '')} |",
            f"| threshold | {protocol.get('threshold', '')} |",
            f"| elapsed seconds | {summary.get('elapsed_seconds', '')} |",
            f"| accuracy | {metrics.get('accuracy', '')} |",
            f"| precision | {metrics.get('precision', '')} |",
            f"| recall | {metrics.get('recall', '')} |",
            f"| f1 | {metrics.get('f1', '')} |",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
