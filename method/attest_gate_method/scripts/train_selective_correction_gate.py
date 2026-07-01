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
    LearnedGateModel,
    evaluate_learned_gate,
    load_baseline_rows,
    load_cards,
    tune_learned_gate_threshold,
    train_learned_gate,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train and evaluate a learned selective correction gate.")
    parser.add_argument("--train-cards", type=Path, required=True)
    parser.add_argument("--calibration-cards", type=Path, action="append", default=[])
    parser.add_argument("--guard-cards", type=Path, action="append", default=[])
    parser.add_argument("--eval-cards", type=Path, action="append", default=[])
    parser.add_argument("--actual", type=Path, default=Path("attest_runs/codexglue_original/test.txt"))
    parser.add_argument(
        "--predictions",
        type=Path,
        default=DEFAULT_BASE_PREDICTIONS,
    )
    parser.add_argument("--base-model", type=str, default=DEFAULT_BASE_MODEL)
    parser.add_argument("--output-model", type=Path, required=True)
    parser.add_argument("--output-summary", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--learning-rate", type=float, default=0.08)
    parser.add_argument("--l2", type=float, default=0.001)
    parser.add_argument("--min-override-precision", type=float, default=0.95)
    parser.add_argument("--max-guard-harm-rate", type=float, default=0.0)
    parser.add_argument("--max-guard-harm-count", type=int, default=0)
    args = parser.parse_args()

    baseline = load_baseline_rows(args.actual, args.predictions)
    train_cards = load_cards(args.train_cards)
    fit = train_learned_gate(
        train_cards,
        baseline,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        l2=args.l2,
        min_override_precision=args.min_override_precision,
    )
    model = fit["model"]

    calibration_result: dict[str, Any] | None = None
    guard_result: dict[str, Any] | None = None
    if args.calibration_cards or args.guard_cards:
        calibration_cards: list[dict[str, Any]] = []
        for path in args.calibration_cards:
            calibration_cards.extend(load_cards(path))
        if not calibration_cards:
            calibration_cards = train_cards
        if args.guard_cards:
            guard_sets = [(path, load_cards(path)) for path in args.guard_cards]
            tuned = tune_learned_gate_threshold_with_guards(
                model,
                calibration_cards,
                baseline,
                guard_sets=guard_sets,
                min_override_precision=args.min_override_precision,
                max_guard_harm_rate=args.max_guard_harm_rate,
                max_guard_harm_count=args.max_guard_harm_count,
            )
            guard_result = tuned["guard_result"]
        else:
            tuned = tune_learned_gate_threshold(
                model,
                calibration_cards,
                baseline,
                min_override_precision=args.min_override_precision,
            )
        model = tuned["model"]
        calibration_result = {
            "cards": [str(path.resolve()) for path in args.calibration_cards],
            "total_cards": len(calibration_cards),
            "best": compact_result(tuned["best"]),
        }

    args.output_model.parent.mkdir(parents=True, exist_ok=True)
    args.output_model.write_text(json.dumps(model.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    train_eval = evaluate_learned_gate(train_cards, baseline, model)
    eval_results: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    for path in args.eval_cards:
        cards = load_cards(path)
        result = evaluate_learned_gate(cards, baseline, model)
        rows = result.pop("rows")
        eval_results.append({"cards": str(path.resolve()), "result": result})
        for row in rows:
            row = dict(row)
            row["eval_cards"] = str(path)
            csv_rows.append(row)

    train_rows = train_eval.pop("rows")
    for row in train_rows:
        row = dict(row)
        row["eval_cards"] = str(args.train_cards)
        csv_rows.append(row)

    summary = {
        "model_path": str(args.output_model.resolve()),
        "train_cards": str(args.train_cards.resolve()),
        "calibration_cards": [str(path.resolve()) for path in args.calibration_cards],
        "guard_cards": [str(path.resolve()) for path in args.guard_cards],
        "actual": str(args.actual.resolve()),
        "predictions": str(args.predictions.resolve()),
        "base_model": args.base_model,
        "training_examples": fit["training_examples"],
        "positive_examples": fit["positive_examples"],
        "negative_examples": fit["negative_examples"],
        "selected_threshold": model.threshold,
        "training_selected_threshold": fit["model"].threshold,
        "calibration_result": calibration_result,
        "guard_result": guard_result,
        "max_guard_harm_rate": args.max_guard_harm_rate,
        "max_guard_harm_count": args.max_guard_harm_count,
        "train_result": train_eval,
        "eval_results": eval_results,
        "model": model.to_dict(),
    }
    args.output_summary.parent.mkdir(parents=True, exist_ok=True)
    args.output_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    if args.report:
        write_report(args.report, summary)
    if args.csv:
        write_csv(args.csv, csv_rows)
    print(json.dumps({k: v for k, v in summary.items() if k != "model"}, ensure_ascii=False, indent=2))
    return 0


def tune_learned_gate_threshold_with_guards(
    model: LearnedGateModel,
    calibration_cards: list[dict[str, Any]],
    baseline: dict[Any, Any],
    *,
    guard_sets: list[tuple[Path, list[dict[str, Any]]]],
    min_override_precision: float,
    max_guard_harm_rate: float,
    max_guard_harm_count: int,
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    best_guard_results: list[dict[str, Any]] = []
    for threshold in [i / 100 for i in range(0, 101)]:
        candidate = LearnedGateModel(model.feature_names, model.weights, threshold)
        calibration_result = evaluate_learned_gate(calibration_cards, baseline, candidate)
        if (
            calibration_result["override_count"]
            and calibration_result["override_precision"] < min_override_precision
        ):
            continue

        guard_results: list[dict[str, Any]] = []
        violates_guard = False
        for path, cards in guard_sets:
            guard_result = evaluate_learned_gate(cards, baseline, candidate)
            compact = compact_result(guard_result)
            guard_results.append({"cards": str(path.resolve()), "result": compact})
            harm_rate = guard_result["harm"] / guard_result["total"] if guard_result["total"] else 0.0
            if guard_result["harm"] > max_guard_harm_count or harm_rate > max_guard_harm_rate:
                violates_guard = True
                break
        if violates_guard:
            continue
        if best is None or guarded_sort_key(calibration_result, guard_results) > guarded_sort_key(best, best_guard_results):
            best = calibration_result
            best_guard_results = guard_results

    if best is None:
        fallback = LearnedGateModel(model.feature_names, model.weights, 1.0)
        best = evaluate_learned_gate(calibration_cards, baseline, fallback)
        best_guard_results = [
            {"cards": str(path.resolve()), "result": compact_result(evaluate_learned_gate(cards, baseline, fallback))}
            for path, cards in guard_sets
        ]

    tuned_model = LearnedGateModel(model.feature_names, model.weights, float(best["threshold"]))
    return {
        "model": tuned_model,
        "best": best,
        "guard_result": {
            "guards": best_guard_results,
            "max_guard_harm_rate": max_guard_harm_rate,
            "max_guard_harm_count": max_guard_harm_count,
        },
    }


def guarded_sort_key(calibration_result: dict[str, Any], guard_results: list[dict[str, Any]]) -> tuple[Any, ...]:
    guard_harm = sum(item["result"].get("harm", 0) for item in guard_results)
    guard_overrides = sum(item["result"].get("override_count", 0) for item in guard_results)
    return (
        calibration_result.get("net_gain", 0),
        calibration_result.get("gate_correct", 0),
        calibration_result.get("override_precision", 0.0),
        -guard_harm,
        -guard_overrides,
        -calibration_result.get("override_count", 0),
    )


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "rows"}


def write_report(path: Path, summary: dict[str, Any]) -> None:
    train = summary["train_result"]
    lines = [
        "# Learned Selective Correction Gate",
        "",
        "## Training",
        "",
        f"- Train cards: `{summary['train_cards']}`",
        f"- Calibration cards: `{summary['calibration_cards']}`",
        f"- Guard cards: `{summary['guard_cards']}`",
        f"- Training examples: `{summary['training_examples']}`",
        f"- Positive examples: `{summary['positive_examples']}`",
        f"- Negative examples: `{summary['negative_examples']}`",
        f"- Training-selected threshold: `{summary['training_selected_threshold']}`",
        f"- Selected threshold: `{summary['selected_threshold']}`",
        f"- Max guard harm rate: `{summary['max_guard_harm_rate']}`",
        f"- Max guard harm count: `{summary['max_guard_harm_count']}`",
        "",
    ]
    if summary.get("calibration_result"):
        lines.extend(
            [
                "## Calibration Result",
                "",
                result_table(summary["calibration_result"]["best"]),
                "",
            ]
        )
    if summary.get("guard_result"):
        lines.extend(["## Guard Result", ""])
        for item in summary["guard_result"]["guards"]:
            lines.extend([f"### {item['cards']}", "", result_table(item["result"]), ""])
    lines.extend(
        [
            "## Train Result",
            "",
            result_table(train),
        ]
    )
    if summary["eval_results"]:
        lines.extend(["", "## Evaluation", ""])
        for item in summary["eval_results"]:
            lines.extend([f"### {item['cards']}", "", result_table(item["result"]), ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def result_table(result: dict[str, Any]) -> str:
    keys = [
        "total",
        "baseline_correct",
        "attest_full_correct",
        "gate_correct",
        "candidate_disagreement",
        "override_count",
        "benefit",
        "harm",
        "net_gain",
        "override_precision",
        "baseline_accuracy",
        "attest_full_accuracy",
        "gate_accuracy",
    ]
    lines = ["| metric | value |", "| --- | ---: |"]
    for key in keys:
        lines.append(f"| {key} | {result.get(key)} |")
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "eval_cards",
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


if __name__ == "__main__":
    raise SystemExit(main())
