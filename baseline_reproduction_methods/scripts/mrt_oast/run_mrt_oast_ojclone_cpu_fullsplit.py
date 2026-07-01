from __future__ import annotations

import argparse
import csv
import json
import os
import runpy
import shutil
import sys
import time
from pathlib import Path
from typing import Any

from run_mrt_oast_ojclone_cpu_smoke import count_data_rows, monkeypatch_cuda_to_cpu, parse_new_result_row, subset_csv, write_json


DEFAULT_ROOT = Path("external") / "MRT-OAST"
DEFAULT_OUTPUT = Path("eviclone_runs") / "baseline_reproduction" / "mrt_oast_ojclone_cpu_fullsplit_1epoch"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run MRT-OAST OJClone on the full official split with CPU compatibility patching.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--train-rows", type=int, default=0, help="0 means full official train split.")
    parser.add_argument("--valid-rows", type=int, default=0, help="0 means full official valid split.")
    parser.add_argument("--test-rows", type=int, default=0, help="0 means full official test split.")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--sen-max-len", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--valid-threshold", type=int, default=0)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
    input_dir = output_dir / "input"
    model_dir = output_dir / "model"
    output_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    source_dir = repo_root / "origindata"
    required = [
        source_dir / "OJClone_with_AST+OAST.csv",
        source_dir / "OJClone_train.csv",
        source_dir / "OJClone_valid.csv",
        source_dir / "OJClone_test.csv",
        source_dir / "OJClone_OAST_dictionary.txt",
    ]
    missing = [str(path) for path in required if not path.exists()]
    json_path = output_dir / "mrt_oast_ojclone_cpu_fullsplit_1epoch.json"
    report_path = output_dir / "mrt_oast_ojclone_cpu_fullsplit_1epoch.md"
    if missing:
        summary = {
            "schema_version": "eviclone-mrt-oast-ojclone-cpu-fullsplit/v1",
            "status": "missing_required_input",
            "missing": missing,
        }
        write_json(json_path, summary)
        report_path.write_text(render_markdown(summary), encoding="utf-8")
        return 2

    shutil.copy2(source_dir / "OJClone_with_AST+OAST.csv", input_dir / "OJClone_with_AST+OAST.csv")
    shutil.copy2(source_dir / "OJClone_OAST_dictionary.txt", input_dir / "OJClone_OAST_dictionary.txt")
    prepare_pairs(source_dir / "OJClone_train.csv", input_dir / "OJClone_train_cpu.csv", args.train_rows)
    prepare_pairs(source_dir / "OJClone_valid.csv", input_dir / "OJClone_valid_cpu.csv", args.valid_rows)
    prepare_pairs(source_dir / "OJClone_test.csv", input_dir / "OJClone_test_cpu.csv", args.test_rows)

    start = time.time()
    status = "unknown"
    error: str | None = None
    old_cwd = Path.cwd()
    old_argv = sys.argv[:]
    old_sys_path = sys.path[:]
    result_csv = repo_root / "model" / "result.csv"
    before_result_size = result_csv.stat().st_size if result_csv.exists() else 0
    try:
        os.chdir(repo_root)
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        (repo_root / "pic").mkdir(exist_ok=True)
        (repo_root / "model").mkdir(exist_ok=True)
        monkeypatch_cuda_to_cpu()
        sys.argv = [
            "main_batch.py",
            "--save",
            str(model_dir),
            "--tag",
            "OJClone_CPU_FULLSPLIT_1EPOCH",
            "--data",
            str(input_dir / "OJClone_with_AST+OAST.csv"),
            "--train_pair",
            str(input_dir / "OJClone_train_cpu.csv"),
            "--valid_pair",
            str(input_dir / "OJClone_valid_cpu.csv"),
            "--test_pair",
            str(input_dir / "OJClone_test_cpu.csv"),
            "--dictionary",
            str(input_dir / "OJClone_XXX_dictionary.txt"),
            "--ast_type",
            "OAST",
            "--epochs",
            str(args.epochs),
            "--batch_size",
            str(args.batch_size),
            "--sen_max_len",
            str(args.sen_max_len),
            "--valid_step",
            "0",
            "--threshold",
            str(args.threshold),
            "--valid_threshold",
            str(args.valid_threshold),
        ]
        runpy.run_path(str(repo_root / "main_batch.py"), run_name="__main__")
        status = "completed"
    except Exception as exc:  # pragma: no cover - diagnostic artifact path
        status = "failed"
        error = repr(exc)
    finally:
        sys.argv = old_argv
        sys.path = old_sys_path
        os.chdir(old_cwd)

    elapsed = time.time() - start
    summary = {
        "schema_version": "eviclone-mrt-oast-ojclone-cpu-fullsplit/v1",
        "status": status,
        "error": error,
        "elapsed_seconds": round(elapsed, 3),
        "repo_root": str(repo_root),
        "output_dir": str(output_dir),
        "model_dir": str(model_dir),
        "input_dir": str(input_dir),
        "rows": {
            "train": count_data_rows(input_dir / "OJClone_train_cpu.csv"),
            "valid": count_data_rows(input_dir / "OJClone_valid_cpu.csv"),
            "test": count_data_rows(input_dir / "OJClone_test_cpu.csv"),
        },
        "protocol": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "sen_max_len": args.sen_max_len,
            "ast_type": "OAST",
            "threshold": args.threshold,
            "valid_threshold": args.valid_threshold,
            "cuda_patch": "torch Tensor/Module cuda methods return self when CUDA is unavailable",
            "split": "full official OJClone split" if args.train_rows == args.valid_rows == args.test_rows == 0 else "row-limited split",
        },
        "metrics": parse_new_result_row(result_csv, before_result_size),
        "table_policy": (
            "CPU-compatible full-split reproduction attempt. This uses the official MRT-OAST OJClone data files and "
            "official code path, but it is not the paper's CUDA/full-epoch protocol unless epochs, sequence length, "
            "and runtime match the paper setting. Keep status labels when using this evidence."
        ),
    }
    write_json(json_path, summary)
    report_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps({"status": status, "output": str(json_path), "report": str(report_path)}, sort_keys=True))
    return 0 if status == "completed" else 2


def prepare_pairs(src: Path, dst: Path, rows: int) -> None:
    if rows <= 0:
        shutil.copy2(src, dst)
        return
    subset_csv(src, dst, rows)


def render_markdown(summary: dict[str, Any]) -> str:
    metrics = summary.get("metrics") or {}
    rows = summary.get("rows") or {}
    protocol = summary.get("protocol") or {}
    return "\n".join(
        [
            "# MRT-OAST OJClone CPU Full-Split Reproduction",
            "",
            f"Status: `{summary.get('status')}`",
            "",
            str(summary.get("table_policy", "")),
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| train rows | {rows.get('train', '')} |",
            f"| valid rows | {rows.get('valid', '')} |",
            f"| test rows | {rows.get('test', '')} |",
            f"| epochs | {protocol.get('epochs', '')} |",
            f"| batch size | {protocol.get('batch_size', '')} |",
            f"| sen_max_len | {protocol.get('sen_max_len', '')} |",
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
