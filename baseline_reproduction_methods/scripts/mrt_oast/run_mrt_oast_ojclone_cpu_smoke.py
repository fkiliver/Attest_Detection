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


DEFAULT_ROOT = Path("external") / "MRT-OAST"
DEFAULT_OUTPUT = Path("eviclone_runs") / "baseline_reproduction" / "mrt_oast_ojclone_cpu_smoke"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a small MRT-OAST OJClone CPU smoke reproduction.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--train-rows", type=int, default=64)
    parser.add_argument("--valid-rows", type=int, default=32)
    parser.add_argument("--test-rows", type=int, default=32)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--sen-max-len", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=1)
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
    if missing:
        write_json(
            output_dir / "mrt_oast_ojclone_cpu_smoke.json",
            {
                "schema_version": "eviclone-mrt-oast-ojclone-cpu-smoke/v1",
                "status": "missing_required_input",
                "missing": missing,
            },
        )
        return 2

    shutil.copy2(source_dir / "OJClone_with_AST+OAST.csv", input_dir / "OJClone_with_AST+OAST.csv")
    shutil.copy2(source_dir / "OJClone_OAST_dictionary.txt", input_dir / "OJClone_OAST_dictionary.txt")
    subset_csv(source_dir / "OJClone_train.csv", input_dir / "OJClone_train_smoke.csv", args.train_rows)
    subset_csv(source_dir / "OJClone_valid.csv", input_dir / "OJClone_valid_smoke.csv", args.valid_rows)
    subset_csv(source_dir / "OJClone_test.csv", input_dir / "OJClone_test_smoke.csv", args.test_rows)

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
            "OJClone_CPU_SMOKE",
            "--data",
            str(input_dir / "OJClone_with_AST+OAST.csv"),
            "--train_pair",
            str(input_dir / "OJClone_train_smoke.csv"),
            "--valid_pair",
            str(input_dir / "OJClone_valid_smoke.csv"),
            "--test_pair",
            str(input_dir / "OJClone_test_smoke.csv"),
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
            "0.5",
            "--valid_threshold",
            "0",
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
    metrics = parse_new_result_row(result_csv, before_result_size)
    summary = {
        "schema_version": "eviclone-mrt-oast-ojclone-cpu-smoke/v1",
        "status": status,
        "error": error,
        "elapsed_seconds": round(elapsed, 3),
        "repo_root": str(repo_root),
        "output_dir": str(output_dir),
        "model_dir": str(model_dir),
        "input_dir": str(input_dir),
        "rows": {
            "train": count_data_rows(input_dir / "OJClone_train_smoke.csv"),
            "valid": count_data_rows(input_dir / "OJClone_valid_smoke.csv"),
            "test": count_data_rows(input_dir / "OJClone_test_smoke.csv"),
        },
        "protocol": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "sen_max_len": args.sen_max_len,
            "ast_type": "OAST",
            "cuda_patch": "torch Tensor/Module cuda methods return self when CUDA is unavailable",
        },
        "metrics": metrics,
        "table_policy": (
            "CPU smoke only. Do not use this as a paper SOTA cell; use it only as evidence that the official "
            "MRT-OAST OJClone code path can execute locally after dependency installation and CPU compatibility patching."
        ),
    }
    write_json(output_dir / "mrt_oast_ojclone_cpu_smoke.json", summary)
    (output_dir / "mrt_oast_ojclone_cpu_smoke.md").write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps({"status": status, "output": str(output_dir / "mrt_oast_ojclone_cpu_smoke.json")}, sort_keys=True))
    return 0 if status == "completed" else 2


def monkeypatch_cuda_to_cpu() -> None:
    import torch

    original_load = torch.load

    def _load_with_legacy_default(*args, **kwargs):  # noqa: ANN002, ANN003
        kwargs.setdefault("weights_only", False)
        return original_load(*args, **kwargs)

    torch.load = _load_with_legacy_default  # type: ignore[assignment]

    if torch.cuda.is_available():
        return

    def _identity_cuda(self, *args, **kwargs):  # noqa: ANN001
        return self

    torch.Tensor.cuda = _identity_cuda  # type: ignore[method-assign]
    torch.nn.Module.cuda = _identity_cuda  # type: ignore[method-assign]


def subset_csv(src: Path, dst: Path, rows: int) -> None:
    with src.open("r", encoding="utf-8", errors="replace", newline="") as in_handle:
        reader = csv.reader(in_handle)
        header = next(reader)
        selected = []
        positives = []
        negatives = []
        for row in reader:
            if len(row) < 5:
                continue
            label = row[4]
            if label == "1":
                positives.append(row)
            else:
                negatives.append(row)
            if len(positives) >= rows // 2 and len(negatives) >= rows - rows // 2:
                break
        selected.extend(positives[: rows // 2])
        selected.extend(negatives[: rows - rows // 2])
    with dst.open("w", encoding="utf-8", newline="") as out_handle:
        writer = csv.writer(out_handle)
        writer.writerow(header)
        writer.writerows(selected)


def count_data_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def parse_new_result_row(path: Path, previous_size: int) -> dict[str, Any] | None:
    if not path.exists():
        return None
    raw_bytes = path.read_bytes()
    if previous_size and previous_size < len(raw_bytes):
        raw_bytes = raw_bytes[previous_size:]
    text = raw_bytes.decode("utf-8", errors="replace")
    rows = [row for row in csv.reader(text.splitlines()) if row]
    if not rows:
        return None
    header = rows[0] if rows[0][0] == "model" else None
    data_rows = rows[1:] if header else rows
    if not data_rows:
        return None
    row = data_rows[-1]
    if header and len(row) == len(header):
        obj = dict(zip(header, row))
        return {
            "accuracy": to_float(obj.get("accuracy")),
            "precision": to_float(obj.get("p_1")),
            "recall": to_float(obj.get("r_1")),
            "f1": to_float(obj.get("f1_1")),
            "raw": obj,
        }
    if len(row) >= 4:
        return {
            "precision": to_float(row[-4]),
            "recall": to_float(row[-3]),
            "f1": to_float(row[-2]),
            "accuracy": to_float(row[-1]),
            "raw": row,
        }
    return {"raw": row}


def to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_markdown(summary: dict[str, Any]) -> str:
    metrics = summary.get("metrics") or {}
    return "\n".join(
        [
            "# MRT-OAST OJClone CPU Smoke",
            "",
            f"Status: `{summary['status']}`",
            "",
            summary["table_policy"],
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| train rows | {summary['rows']['train']} |",
            f"| valid rows | {summary['rows']['valid']} |",
            f"| test rows | {summary['rows']['test']} |",
            f"| elapsed seconds | {summary['elapsed_seconds']} |",
            f"| accuracy | {metrics.get('accuracy', '')} |",
            f"| precision | {metrics.get('precision', '')} |",
            f"| recall | {metrics.get('recall', '')} |",
            f"| f1 | {metrics.get('f1', '')} |",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
