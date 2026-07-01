from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from attest_gate.config import DEFAULT_BASE_MODEL, DEFAULT_BASE_PREDICTIONS


def main() -> int:
    parser = argparse.ArgumentParser(description="Project selective gate deltas onto the full CodeXGLUE test set.")
    parser.add_argument("--actual", type=Path, default=Path("attest_runs/codexglue_original/test.txt"))
    parser.add_argument(
        "--predictions",
        type=Path,
        default=DEFAULT_BASE_PREDICTIONS,
    )
    parser.add_argument("--base-model", type=str, default=DEFAULT_BASE_MODEL)
    parser.add_argument("--error-rows", type=Path, required=True)
    parser.add_argument("--guard-rows", type=Path, action="append", default=[])
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    baseline_rows = load_triplets(args.actual, args.predictions)
    baseline_confusion = confusion_from_triplets(baseline_rows)
    baseline_counts = Counter({"correct": 0, "wrong": 0})
    for row in baseline_rows:
        baseline_counts["correct" if row["gold"] == row["pred"] else "wrong"] += 1

    error_rows = load_gate_rows(args.error_rows)
    error_delta = delta_from_rows(error_rows, scale=1.0)
    guard_results = []
    projected_delta = Counter(error_delta["delta"])
    for path in args.guard_rows:
        rows = load_gate_rows(path)
        valid_rows = [row for row in rows if row["baseline_correct"]]
        scale = (baseline_counts["correct"] / len(valid_rows)) if valid_rows else 0.0
        guard_delta = delta_from_rows(valid_rows, scale=scale)
        projected_delta.update(guard_delta["delta"])
        guard_results.append(
            {
                "path": str(path.resolve()),
                "rows": len(rows),
                "baseline_correct_rows": len(valid_rows),
                "scale_to_full_correct_set": round(scale, 6),
                **guard_delta,
            }
        )

    projected_confusion = add_delta(baseline_confusion, projected_delta)
    summary = {
        "name": args.name,
        "actual": str(args.actual.resolve()),
        "predictions": str(args.predictions.resolve()),
        "base_model": args.base_model,
        "baseline_counts": dict(baseline_counts),
        "baseline_confusion": dict(baseline_confusion),
        "baseline_metrics": metrics(baseline_confusion),
        "error_rows": str(args.error_rows.resolve()),
        "error_delta": error_delta,
        "guard_results": guard_results,
        "projected_delta": dict(projected_delta),
        "projected_confusion": dict(projected_confusion),
        "projected_metrics": metrics(projected_confusion),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    if args.report:
        write_report(args.report, summary)
    print(json.dumps(summary["projected_metrics"], ensure_ascii=False, indent=2))
    return 0


def load_triplets(actual_path: Path, predictions_path: Path) -> list[dict[str, int]]:
    actual_rows = read_triplet_file(actual_path)
    pred_rows = read_triplet_file(predictions_path)
    if len(actual_rows) != len(pred_rows):
        raise ValueError(f"actual/prediction row count mismatch: {len(actual_rows)} != {len(pred_rows)}")
    result = []
    for idx, (actual, pred) in enumerate(zip(actual_rows, pred_rows), start=1):
        if actual[0] != pred[0] or actual[1] != pred[1]:
            raise ValueError(f"pair mismatch at row {idx}")
        result.append({"gold": int(actual[2]), "pred": int(pred[2])})
    return result


def read_triplet_file(path: Path) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) < 3:
                raise ValueError(f"expected at least 3 columns at {path}:{line_no}, got {len(parts)}")
            rows.append((parts[0], parts[1], int(parts[2])))
    return rows


def load_gate_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [coerce_row(row) for row in csv.DictReader(f)]


def coerce_row(row: dict[str, str]) -> dict[str, Any]:
    return {
        **row,
        "gold": int(row["gold"]),
        "base_pred": int(row["base_pred"]),
        "final_pred": int(row["final_pred"]),
        "baseline_correct": parse_bool(row["baseline_correct"]),
        "final_correct": parse_bool(row["final_correct"]),
        "override": parse_bool(row["override"]),
    }


def parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"true", "1", "yes"}


def confusion_from_triplets(rows: list[dict[str, int]]) -> Counter:
    counter: Counter = Counter()
    for row in rows:
        counter[confusion_key(row["gold"], row["pred"])] += 1
    return counter


def delta_from_rows(rows: list[dict[str, Any]], *, scale: float) -> dict[str, Any]:
    baseline = Counter()
    final = Counter()
    overrides = 0
    corrections = 0
    damage = 0
    for row in rows:
        gold = int(row["gold"])
        base_pred = int(row["base_pred"])
        final_pred = int(row["final_pred"])
        baseline[confusion_key(gold, base_pred)] += 1
        final[confusion_key(gold, final_pred)] += 1
        if row.get("override"):
            overrides += 1
        if base_pred != gold and final_pred == gold:
            corrections += 1
        if base_pred == gold and final_pred != gold:
            damage += 1
    delta = Counter()
    for key in {"tp", "tn", "fp", "fn"}:
        delta[key] = (final[key] - baseline[key]) * scale
    return {
        "rows": len(rows),
        "scale": round(scale, 6),
        "override_count": overrides,
        "corrections": corrections,
        "damage": damage,
        "baseline_confusion": dict(baseline),
        "final_confusion": dict(final),
        "delta": dict(delta),
        "scaled_delta": dict(delta),
    }


def add_delta(confusion: Counter, delta: Counter) -> Counter:
    result = Counter({key: float(confusion.get(key, 0)) for key in {"tp", "tn", "fp", "fn"}})
    for key, value in delta.items():
        result[key] += float(value)
    return result


def confusion_key(gold: int, pred: int) -> str:
    if gold == 1 and pred == 1:
        return "tp"
    if gold == 0 and pred == 0:
        return "tn"
    if gold == 0 and pred == 1:
        return "fp"
    return "fn"


def metrics(confusion: Counter) -> dict[str, float]:
    tp = float(confusion.get("tp", 0.0))
    tn = float(confusion.get("tn", 0.0))
    fp = float(confusion.get("fp", 0.0))
    fn = float(confusion.get("fn", 0.0))
    total = tp + tn + fp + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "accuracy": round((tp + tn) / total, 6) if total else 0.0,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round((2 * precision * recall / (precision + recall)), 6) if precision + recall else 0.0,
    }


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        f"# Selective Gate Full-Test Projection: {summary['name']}",
        "",
        "## Metrics",
        "",
        "| metric | baseline | projected |",
        "| --- | ---: | ---: |",
    ]
    for key in ["accuracy", "precision", "recall", "f1"]:
        lines.append(f"| {key} | {summary['baseline_metrics'][key]} | {summary['projected_metrics'][key]} |")
    lines.extend(["", "## Confusion Matrix", "", "| cell | baseline | projected | delta |", "| --- | ---: | ---: | ---: |"])
    for key in ["tp", "tn", "fp", "fn"]:
        baseline = summary["baseline_confusion"].get(key, 0)
        projected = summary["projected_confusion"].get(key, 0.0)
        delta = summary["projected_delta"].get(key, 0.0)
        lines.append(f"| {key} | {baseline} | {round(projected, 3)} | {round(delta, 3)} |")
    lines.extend(["", "## Guard Inputs", "", "| rows | scale | overrides | damage |", "| ---: | ---: | ---: | ---: |"])
    for item in summary["guard_results"]:
        lines.append(
            f"| {item['rows']} | {item['scale_to_full_correct_set']} | {item['override_count']} | {item['damage']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
