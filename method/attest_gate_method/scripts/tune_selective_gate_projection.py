from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from attest_gate.config import DEFAULT_BASE_MODEL, DEFAULT_BASE_PREDICTIONS
from attest_gate.selective_gate import evaluate_gate, load_baseline_rows, load_cards, threshold_grid
from scripts.project_selective_gate_full_test import (
    add_delta,
    confusion_from_triplets,
    delta_from_rows,
    load_triplets,
    metrics,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Tune selective gate threshold by projected full-test precision/recall/F1."
    )
    parser.add_argument("--error-cards", type=Path, required=True)
    parser.add_argument("--guard-cards", type=Path, action="append", default=[])
    parser.add_argument("--actual", type=Path, default=Path("attest_runs/codexglue_original/test.txt"))
    parser.add_argument(
        "--predictions",
        type=Path,
        default=DEFAULT_BASE_PREDICTIONS,
    )
    parser.add_argument("--base-model", type=str, default=DEFAULT_BASE_MODEL)
    parser.add_argument("--grid-start", type=float, default=0.0)
    parser.add_argument("--grid-stop", type=float, default=1.6)
    parser.add_argument("--grid-step", type=float, default=0.01)
    parser.add_argument("--guard-aggregation", choices=["mean", "max_harm"], default="mean")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--output-policy", type=Path, default=None)
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    actual_prediction_rows = load_triplets(args.actual, args.predictions)
    baseline_confusion = confusion_from_triplets(actual_prediction_rows)
    baseline_metrics = metrics(baseline_confusion)
    baseline_correct = sum(1 for row in actual_prediction_rows if row["gold"] == row["pred"])
    baseline = load_baseline_rows(args.actual, args.predictions)
    error_cards = load_cards(args.error_cards)
    guard_sets = [(path, load_cards(path)) for path in args.guard_cards]

    grid_rows: list[dict[str, Any]] = []
    for threshold in threshold_grid(args.grid_start, args.grid_stop, args.grid_step):
        error_result = evaluate_gate(error_cards, baseline, threshold=threshold)
        error_delta = delta_from_rows(error_result["rows"], scale=1.0)
        guard_deltas = []
        guard_rows = []
        for path, cards in guard_sets:
            guard_result = evaluate_gate(cards, baseline, threshold=threshold)
            valid_rows = [row for row in guard_result["rows"] if row["baseline_correct"]]
            scale = baseline_correct / len(valid_rows) if valid_rows else 0.0
            guard_delta = delta_from_rows(valid_rows, scale=scale)
            guard_deltas.append(guard_delta)
            guard_rows.append(
                {
                    "path": str(path.resolve()),
                    "rows": len(guard_result["rows"]),
                    "baseline_correct_rows": len(valid_rows),
                    "scale": round(scale, 6),
                    "harm": guard_result["harm"],
                    "override_count": guard_result["override_count"],
                    "scaled_delta": guard_delta["delta"],
                }
            )

        projected_delta = Counter(error_delta["delta"])
        guard_projected_delta = aggregate_guard_delta(guard_deltas, mode=args.guard_aggregation)
        projected_delta.update(guard_projected_delta)
        projected_confusion = add_delta(baseline_confusion, projected_delta)
        projected_metrics = metrics(projected_confusion)
        grid_rows.append(
            {
                "threshold": threshold,
                "error_corrections": error_delta["corrections"],
                "error_overrides": error_delta["override_count"],
                "guard_harm": sum(row["harm"] for row in guard_rows),
                "guard_overrides": sum(row["override_count"] for row in guard_rows),
                "guard_projected_delta": dict(guard_projected_delta),
                "projected_delta": dict(projected_delta),
                "projected_confusion": dict(projected_confusion),
                "projected_metrics": projected_metrics,
                "guard_rows": guard_rows,
            }
        )

    best = select_best(grid_rows)
    summary = {
        "error_cards": str(args.error_cards.resolve()),
        "guard_cards": [str(path.resolve()) for path in args.guard_cards],
        "actual": str(args.actual.resolve()),
        "predictions": str(args.predictions.resolve()),
        "base_model": args.base_model,
        "guard_aggregation": args.guard_aggregation,
        "baseline_confusion": dict(baseline_confusion),
        "baseline_metrics": baseline_metrics,
        "baseline_correct": baseline_correct,
        "best": best,
        "grid": grid_rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    if args.output_policy:
        write_policy(args.output_policy, summary)
    if args.csv:
        write_csv(args.csv, grid_rows)
    if args.report:
        write_report(args.report, summary)
    print(json.dumps({"best": compact_row(best), "baseline_metrics": baseline_metrics}, ensure_ascii=False, indent=2))
    return 0


def write_policy(path: Path, summary: dict[str, Any]) -> None:
    best = summary["best"]
    policy = {
        "schema_version": "attest-selective-gate-policy/v1",
        "gate_type": "heuristic_override_score",
        "threshold": best["threshold"],
        "selection_objective": "maximize_projected_full_test_f1",
        "guard_aggregation": summary["guard_aggregation"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "error_cards": summary["error_cards"],
            "guard_cards": summary["guard_cards"],
            "actual": summary["actual"],
            "predictions": summary["predictions"],
        },
        "baseline_metrics": summary["baseline_metrics"],
        "projected_metrics": best["projected_metrics"],
        "selected_threshold_evidence": {
            "error_corrections": best["error_corrections"],
            "error_overrides": best["error_overrides"],
            "guard_harm": best["guard_harm"],
            "guard_overrides": best["guard_overrides"],
            "projected_delta": best["projected_delta"],
            "projected_confusion": best["projected_confusion"],
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(policy, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def aggregate_guard_delta(items: list[dict[str, Any]], *, mode: str) -> Counter:
    if not items:
        return Counter()
    keys = {"tp", "tn", "fp", "fn"}
    if mode == "mean":
        return Counter({key: sum(float(item["delta"].get(key, 0.0)) for item in items) / len(items) for key in keys})
    if mode == "max_harm":
        return Counter(max(items, key=lambda item: projected_harm_key(item))["delta"])
    raise ValueError(f"unknown guard aggregation mode: {mode}")


def projected_harm_key(item: dict[str, Any]) -> tuple[float, float]:
    delta = item["delta"]
    return (
        float(delta.get("fp", 0.0)) + float(delta.get("fn", 0.0)),
        -(float(delta.get("tp", 0.0)) + float(delta.get("tn", 0.0))),
    )


def select_best(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        rows,
        key=lambda row: (
            row["projected_metrics"]["f1"],
            row["projected_metrics"]["accuracy"],
            row["projected_metrics"]["precision"],
            -row["guard_harm"],
            row["error_corrections"],
            -row["threshold"],
        ),
    )


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "threshold": row["threshold"],
        "error_corrections": row["error_corrections"],
        "guard_harm": row["guard_harm"],
        "guard_overrides": row["guard_overrides"],
        "projected_metrics": row["projected_metrics"],
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "threshold",
        "error_corrections",
        "error_overrides",
        "guard_harm",
        "guard_overrides",
        "accuracy",
        "precision",
        "recall",
        "f1",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            metrics_row = row["projected_metrics"]
            writer.writerow(
                {
                    "threshold": row["threshold"],
                    "error_corrections": row["error_corrections"],
                    "error_overrides": row["error_overrides"],
                    "guard_harm": row["guard_harm"],
                    "guard_overrides": row["guard_overrides"],
                    "accuracy": metrics_row["accuracy"],
                    "precision": metrics_row["precision"],
                    "recall": metrics_row["recall"],
                    "f1": metrics_row["f1"],
                }
            )


def write_report(path: Path, summary: dict[str, Any]) -> None:
    best = summary["best"]
    lines = [
        "# Projected-F1 Selective Gate Tuning",
        "",
        "## Baseline",
        "",
        "| metric | value |",
        "| --- | ---: |",
    ]
    for key, value in summary["baseline_metrics"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Best Threshold",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| threshold | {best['threshold']} |",
            f"| error_corrections | {best['error_corrections']} |",
            f"| guard_harm | {best['guard_harm']} |",
            f"| projected_accuracy | {best['projected_metrics']['accuracy']} |",
            f"| projected_precision | {best['projected_metrics']['precision']} |",
            f"| projected_recall | {best['projected_metrics']['recall']} |",
            f"| projected_f1 | {best['projected_metrics']['f1']} |",
            "",
            "## Top Thresholds",
            "",
            "| threshold | corrections | guard_harm | precision | recall | f1 |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    top_rows = sorted(
        summary["grid"],
        key=lambda row: (row["projected_metrics"]["f1"], row["projected_metrics"]["accuracy"]),
        reverse=True,
    )[:20]
    for row in top_rows:
        m = row["projected_metrics"]
        lines.append(
            f"| {row['threshold']} | {row['error_corrections']} | {row['guard_harm']} | {m['precision']} | {m['recall']} | {m['f1']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
