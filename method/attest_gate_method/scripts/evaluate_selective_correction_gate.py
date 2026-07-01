from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from attest_gate.config import DEFAULT_BASE_MODEL, DEFAULT_BASE_PREDICTIONS
from attest_gate.selective_gate import (
    evaluate_gate,
    load_baseline_rows,
    load_cards,
    threshold_grid,
    tune_threshold,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a selective correction gate over Attest cards.")
    parser.add_argument("--cards", type=Path, required=True)
    parser.add_argument("--guard-cards", type=Path, action="append", default=[])
    parser.add_argument("--actual", type=Path, default=Path("attest_runs/codexglue_original/test.txt"))
    parser.add_argument(
        "--predictions",
        type=Path,
        default=DEFAULT_BASE_PREDICTIONS,
    )
    parser.add_argument("--base-model", type=str, default=DEFAULT_BASE_MODEL)
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--grid-start", type=float, default=0.0)
    parser.add_argument("--grid-stop", type=float, default=1.5)
    parser.add_argument("--grid-step", type=float, default=0.01)
    parser.add_argument("--min-override-precision", type=float, default=0.0)
    parser.add_argument("--max-guard-harm-rate", type=float, default=0.0)
    parser.add_argument("--max-guard-harm-count", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True, help="summary JSON path")
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--csv", type=Path, default=None)
    args = parser.parse_args()

    cards = load_cards(args.cards)
    guard_sets = [(path, load_cards(path)) for path in args.guard_cards]
    baseline = load_baseline_rows(args.actual, args.predictions)
    if args.threshold is None:
        thresholds = threshold_grid(args.grid_start, args.grid_stop, args.grid_step)
        if guard_sets:
            tuned = tune_threshold_with_guards(
                cards,
                baseline,
                thresholds=thresholds,
                guard_sets=guard_sets,
                min_override_precision=args.min_override_precision,
                max_guard_harm_rate=args.max_guard_harm_rate,
                max_guard_harm_count=args.max_guard_harm_count,
            )
        else:
            tuned = tune_threshold(
                cards,
                baseline,
                thresholds=thresholds,
                min_override_precision=args.min_override_precision,
            )
        result = tuned["best"]
        grid = tuned["grid"]
        guard_results = tuned.get("guard_results", [])
    else:
        result = evaluate_gate(cards, baseline, threshold=args.threshold)
        grid = []
        guard_results = [
            {"cards": str(path.resolve()), "result": compact_result(evaluate_gate(guard_cards, baseline, threshold=args.threshold))}
            for path, guard_cards in guard_sets
        ]

    rows = result.pop("rows")
    summary = {
        "cards": str(args.cards.resolve()),
        "guard_cards": [str(path.resolve()) for path in args.guard_cards],
        "actual": str(args.actual.resolve()),
        "predictions": str(args.predictions.resolve()),
        "base_model": args.base_model,
        "max_guard_harm_rate": args.max_guard_harm_rate,
        "max_guard_harm_count": args.max_guard_harm_count,
        "selection_note": (
            "Gate evaluation is only valid for the card distribution supplied. "
            "If cards are base-detector error-only cases, harm on originally correct cases is unmeasured."
        ),
        "result": result,
        "guard_results": guard_results,
        "threshold_grid": grid,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    if args.report:
        write_report(args.report, summary)
    if args.csv:
        write_rows_csv(args.csv, rows)
    print(json.dumps(summary["result"], ensure_ascii=False, indent=2))
    return 0


def tune_threshold_with_guards(
    cards: list[dict[str, Any]],
    baseline: dict[Any, Any],
    *,
    thresholds: list[float],
    guard_sets: list[tuple[Path, list[dict[str, Any]]]],
    min_override_precision: float,
    max_guard_harm_rate: float,
    max_guard_harm_count: int,
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    best_guard_results: list[dict[str, Any]] = []
    grid: list[dict[str, Any]] = []
    for threshold in thresholds:
        result = evaluate_gate(cards, baseline, threshold=threshold)
        compact = compact_result(result)
        grid.append(compact)
        if result["override_count"] and result["override_precision"] < min_override_precision:
            continue

        guard_results: list[dict[str, Any]] = []
        violates_guard = False
        for path, guard_cards in guard_sets:
            guard_result = evaluate_gate(guard_cards, baseline, threshold=threshold)
            guard_compact = compact_result(guard_result)
            guard_results.append({"cards": str(path.resolve()), "result": guard_compact})
            harm_rate = guard_result["harm"] / guard_result["total"] if guard_result["total"] else 0.0
            if guard_result["harm"] > max_guard_harm_count or harm_rate > max_guard_harm_rate:
                violates_guard = True
                break
        if violates_guard:
            continue
        if best is None or guarded_sort_key(result, guard_results) > guarded_sort_key(best, best_guard_results):
            best = result
            best_guard_results = guard_results

    if best is None:
        best = evaluate_gate(cards, baseline, threshold=1_000_000.0)
        best_guard_results = [
            {"cards": str(path.resolve()), "result": compact_result(evaluate_gate(guard_cards, baseline, threshold=1_000_000.0))}
            for path, guard_cards in guard_sets
        ]
    return {"best": best, "grid": grid, "guard_results": best_guard_results}


def guarded_sort_key(result: dict[str, Any], guard_results: list[dict[str, Any]]) -> tuple[Any, ...]:
    guard_harm = sum(item["result"].get("harm", 0) for item in guard_results)
    guard_overrides = sum(item["result"].get("override_count", 0) for item in guard_results)
    return (
        result.get("net_gain", 0),
        result.get("gate_correct", 0),
        result.get("override_precision", 0.0),
        -guard_harm,
        -guard_overrides,
        -result.get("override_count", 0),
    )


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "rows"}


def write_report(path: Path, summary: dict[str, Any]) -> None:
    result = summary["result"]
    lines = [
        "# Selective Correction Gate Evaluation",
        "",
        "## Inputs",
        "",
        f"- Cards: `{summary['cards']}`",
        f"- Guard cards: `{summary['guard_cards']}`",
        f"- Actual labels: `{summary['actual']}`",
        f"- Baseline predictions: `{summary['predictions']}`",
        f"- Max guard harm rate: `{summary['max_guard_harm_rate']}`",
        f"- Max guard harm count: `{summary['max_guard_harm_count']}`",
        "",
        "## Result",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| threshold | {result['threshold']} |",
        f"| total | {result['total']} |",
        f"| baseline_correct | {result['baseline_correct']} |",
        f"| attest_full_correct | {result['attest_full_correct']} |",
        f"| gate_correct | {result['gate_correct']} |",
        f"| candidate_disagreement | {result['candidate_disagreement']} |",
        f"| override_count | {result['override_count']} |",
        f"| benefit | {result['benefit']} |",
        f"| harm | {result['harm']} |",
        f"| net_gain | {result['net_gain']} |",
        f"| override_precision | {result['override_precision']} |",
        f"| baseline_accuracy | {result['baseline_accuracy']} |",
        f"| attest_full_accuracy | {result['attest_full_accuracy']} |",
        f"| gate_accuracy | {result['gate_accuracy']} |",
        "",
        "## Override Status Distribution",
        "",
        "```json",
        json.dumps(
            {
                "dynamic": result.get("override_by_dynamic_status", {}),
                "context": result.get("override_by_context_status", {}),
            },
            ensure_ascii=False,
            indent=2,
        ),
        "```",
        "",
    ]
    if summary.get("guard_results"):
        lines.extend(["## Guard Results", ""])
        for item in summary["guard_results"]:
            guard = item["result"]
            lines.extend(
                [
                    f"### {item['cards']}",
                    "",
                    "| metric | value |",
                    "| --- | ---: |",
                    f"| threshold | {guard['threshold']} |",
                    f"| total | {guard['total']} |",
                    f"| baseline_correct | {guard['baseline_correct']} |",
                    f"| attest_full_correct | {guard['attest_full_correct']} |",
                    f"| gate_correct | {guard['gate_correct']} |",
                    f"| candidate_disagreement | {guard['candidate_disagreement']} |",
                    f"| override_count | {guard['override_count']} |",
                    f"| benefit | {guard['benefit']} |",
                    f"| harm | {guard['harm']} |",
                    f"| net_gain | {guard['net_gain']} |",
                    f"| override_precision | {guard['override_precision']} |",
                    f"| baseline_accuracy | {guard['baseline_accuracy']} |",
                    f"| attest_full_accuracy | {guard['attest_full_accuracy']} |",
                    f"| gate_accuracy | {guard['gate_accuracy']} |",
                    "",
                ]
            )
    lines.extend(
        [
        "## Caveat",
        "",
        summary["selection_note"],
        "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_rows_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "pair_id",
        "function_id_a",
        "function_id_b",
        "gold",
        "base_pred",
        "attest_pred",
        "score",
        "override",
        "final_pred",
        "baseline_correct",
        "ours_correct",
        "final_correct",
        "dynamic_status",
        "context_status",
        "attest_confidence",
        "attest_verdict",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


if __name__ == "__main__":
    raise SystemExit(main())
