from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_BASELINE = Path("eviclone_runs") / "baseline_reproduction" / "dsfm_ojclone_test_metrics.json"
DEFAULT_GOLD = Path("eviclone_runs") / "baseline_reproduction" / "dsfm_ojclone_test_actual.txt"
DEFAULT_BASELINE_PREDICTIONS = Path("eviclone_runs") / "baseline_reproduction" / "dsfm_ojclone_test_predictions.txt"
DEFAULT_RUN_DIR = Path("eviclone_runs") / "baseline_reproduction" / "ojclone_program_adapter_dsfm_errors_v2"
DEFAULT_CARDS = DEFAULT_RUN_DIR / "cards.jsonl"
DEFAULT_OUTPUT = DEFAULT_RUN_DIR / "projection.json"
DEFAULT_REPORT = DEFAULT_RUN_DIR / "projection.md"
DEFAULT_PREDICTIONS_OUTPUT = (
    DEFAULT_RUN_DIR / "eviclone_on_dsfm_ojclone_projected_predictions.txt"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Project OJClone DSFM adapter predictions onto full-test confusion.")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--baseline-predictions", type=Path, default=DEFAULT_BASELINE_PREDICTIONS)
    parser.add_argument("--cards", type=Path, default=DEFAULT_CARDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--predictions-output", type=Path, default=DEFAULT_PREDICTIONS_OUTPUT)
    args = parser.parse_args()

    projection = build_projection(
        baseline_path=args.baseline,
        gold_path=args.gold,
        baseline_predictions_path=args.baseline_predictions,
        cards_path=args.cards,
        predictions_output_path=args.predictions_output,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_markdown(projection), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": projection["status"],
                "binary_predictions": projection["adapter_binary_predictions"],
                "corrected_errors": projection["corrected_baseline_errors"],
                "projected_f1": projection["projected_metrics"]["f1"],
                "output": str(args.output),
                "report": str(args.report),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def build_projection(
    *,
    baseline_path: Path,
    gold_path: Path,
    baseline_predictions_path: Path,
    cards_path: Path,
    predictions_output_path: Path,
) -> dict[str, Any]:
    baseline = read_json(baseline_path)
    cards = read_jsonl(cards_path)
    base_confusion = {key: int((baseline.get("confusion") or {}).get(key, 0)) for key in ["tp", "tn", "fp", "fn"]}
    projected_confusion = dict(base_confusion)
    adapter_confusion: Counter[str] = Counter()
    transition_counts: Counter[str] = Counter()
    binary = 0
    corrected = 0
    unchanged_wrong = 0
    harmful = 0
    seen_pairs: set[tuple[str, str]] = set()
    examples = []
    for card in cards:
        decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
        pred = decision.get("pred_label")
        if pred not in (0, 1):
            continue
        function_ids = card.get("function_ids") if isinstance(card.get("function_ids"), dict) else {}
        pair_key = (str(function_ids.get("a")), str(function_ids.get("b")))
        if pair_key in seen_pairs:
            raise ValueError(f"duplicate adapter prediction for pair {pair_key}")
        seen_pairs.add(pair_key)
        gold = int((card.get("gold") or {}).get("label"))
        old_pred = int((card.get("baseline") or {}).get("prediction"))
        new_pred = int(pred)
        before = confusion_key(gold, old_pred)
        after = confusion_key(gold, new_pred)
        projected_confusion[before] -= 1
        projected_confusion[after] += 1
        transition_counts[f"{before}->{after}"] += 1
        adapter_confusion[after] += 1
        binary += 1
        if old_pred != gold and new_pred == gold:
            corrected += 1
        elif old_pred != gold and new_pred != gold:
            unchanged_wrong += 1
        elif old_pred == gold and new_pred != gold:
            harmful += 1
        if len(examples) < 10:
            examples.append(
                {
                    "pair_id": card.get("pair_id"),
                    "function_ids": function_ids,
                    "baseline_prediction": old_pred,
                    "adapter_prediction": new_pred,
                    "gold": gold,
                    "transition": f"{before}->{after}",
                    "verdict": decision.get("verdict"),
                    "families": card.get("families"),
                }
            )
    if any(value < 0 for value in projected_confusion.values()):
        raise ValueError(f"invalid projected confusion: {projected_confusion}")
    baseline_error_count = base_confusion["fp"] + base_confusion["fn"]
    prediction_export = write_projected_predictions(
        gold_path=gold_path,
        baseline_predictions_path=baseline_predictions_path,
        cards=cards,
        output_path=predictions_output_path,
    )
    return {
        "schema_version": "eviclone-ojclone-dsfm-adapter-projection/v1",
        "status": "projected_full_test_with_abstain_as_baseline_fallback",
        "baseline_metrics_path": str(baseline_path),
        "gold_path": str(gold_path),
        "baseline_predictions_path": str(baseline_predictions_path),
        "cards_path": str(cards_path),
        "projected_predictions_path": str(predictions_output_path),
        "dataset": baseline.get("dataset"),
        "baseline_method": baseline.get("method"),
        "projection_method": "EviClone-OJClone-program-adapter with abstain-as-baseline fallback",
        "rows": baseline.get("rows"),
        "baseline_confusion": base_confusion,
        "baseline_metrics": baseline.get("metrics") or {},
        "baseline_error_count": baseline_error_count,
        "adapter_binary_predictions": binary,
        "adapter_abstentions_on_error_cohort": len(cards) - binary,
        "adapter_error_cohort_coverage": round(binary / len(cards), 6) if cards else 0.0,
        "adapter_binary_coverage_of_baseline_errors": round(binary / baseline_error_count, 6) if baseline_error_count else 0.0,
        "corrected_baseline_errors": corrected,
        "unchanged_baseline_errors": unchanged_wrong,
        "introduced_harm_on_adapter_scope": harmful,
        "transition_counts": dict(sorted(transition_counts.items())),
        "adapter_scope_confusion": {key: int(adapter_confusion.get(key, 0)) for key in ["tp", "tn", "fp", "fn"]},
        "projected_confusion": projected_confusion,
        "projected_metrics": metrics_from_confusion(projected_confusion),
        "prediction_export": prediction_export,
        "examples": examples,
        "table_impact": (
            "This is a full-test projected prediction export for a conservative EviClone-on-DSFM policy: apply "
            "auditable adapter predictions on retained DSFM baseline-error rows and leave abstentions plus all other "
            "rows as the DSFM baseline. It is a projected table cell, not an exact end-to-end deployed selector run."
        ),
    }


def read_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            obj = json.loads(text)
            if not isinstance(obj, dict):
                raise ValueError(f"expected JSON object at {path}:{line_no}")
            rows.append(obj)
    return rows


def read_triplets(path: Path) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            parts = text.replace(",", " ").split()
            if len(parts) < 3:
                raise ValueError(f"expected at least id_a id_b label at {path}:{line_no}")
            rows.append((parts[0], parts[1], int(parts[2])))
    return rows


def write_projected_predictions(
    *,
    gold_path: Path,
    baseline_predictions_path: Path,
    cards: list[dict[str, Any]],
    output_path: Path,
) -> dict[str, Any]:
    gold_rows = read_triplets(gold_path)
    baseline_rows = read_triplets(baseline_predictions_path)
    if len(gold_rows) != len(baseline_rows):
        raise ValueError(f"gold/prediction row mismatch: {len(gold_rows)} != {len(baseline_rows)}")

    corrections: dict[tuple[str, str], int] = {}
    abstentions = 0
    for card in cards:
        function_ids = card.get("function_ids") if isinstance(card.get("function_ids"), dict) else {}
        pair = (str(function_ids.get("a")), str(function_ids.get("b")))
        decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
        pred = decision.get("pred_label")
        if pred not in (0, 1):
            abstentions += 1
            continue
        if pair in corrections:
            raise ValueError(f"duplicate adapter correction for pair {pair}")
        corrections[pair] = int(pred)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    applied = 0
    pair_mismatches = 0
    with output_path.open("w", encoding="utf-8", newline="\n") as sink:
        for (gold_a, gold_b, _gold), (pred_a, pred_b, baseline_pred) in zip(gold_rows, baseline_rows):
            if (gold_a, gold_b) != (pred_a, pred_b):
                pair_mismatches += 1
            pair = (gold_a, gold_b)
            reverse_pair = (gold_b, gold_a)
            if pair in corrections:
                label = corrections[pair]
                applied += 1
            elif reverse_pair in corrections:
                label = corrections[reverse_pair]
                applied += 1
            else:
                label = baseline_pred
            sink.write(f"{gold_a}\t{gold_b}\t{label}\n")

    return {
        "gold_rows": len(gold_rows),
        "baseline_prediction_rows": len(baseline_rows),
        "pair_mismatches": pair_mismatches,
        "adapter_binary_corrections_available": len(corrections),
        "adapter_binary_corrections_applied": applied,
        "adapter_abstentions": abstentions,
        "output": str(output_path),
    }


def confusion_key(gold: int, pred: int) -> str:
    if gold == 1 and pred == 1:
        return "tp"
    if gold == 0 and pred == 0:
        return "tn"
    if gold == 0 and pred == 1:
        return "fp"
    return "fn"


def metrics_from_confusion(confusion: dict[str, int]) -> dict[str, float]:
    tp = float(confusion.get("tp", 0))
    tn = float(confusion.get("tn", 0))
    fp = float(confusion.get("fp", 0))
    fn = float(confusion.get("fn", 0))
    total = tp + tn + fp + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "accuracy": round((tp + tn) / total, 6) if total else 0.0,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }


def render_markdown(projection: dict[str, Any]) -> str:
    lines = [
        "# OJClone DSFM Adapter Projection",
        "",
        f"Status: `{projection['status']}`",
        "",
        projection["table_impact"],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| rows | {projection['rows']} |",
        f"| baseline_error_count | {projection['baseline_error_count']} |",
        f"| adapter_binary_predictions | {projection['adapter_binary_predictions']} |",
        f"| corrected_baseline_errors | {projection['corrected_baseline_errors']} |",
        f"| introduced_harm_on_adapter_scope | {projection['introduced_harm_on_adapter_scope']} |",
        f"| adapter_error_cohort_coverage | {projection['adapter_error_cohort_coverage']} |",
        f"| baseline_f1 | {projection['baseline_metrics'].get('f1')} |",
        f"| projected_f1 | {projection['projected_metrics'].get('f1')} |",
        f"| projected_predictions_rows | {projection['prediction_export']['gold_rows']} |",
        f"| projected_predictions_applied_corrections | {projection['prediction_export']['adapter_binary_corrections_applied']} |",
        "",
        "## Confusion",
        "",
        "| Scope | TP | TN | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: |",
        confusion_row("baseline", projection["baseline_confusion"]),
        confusion_row("projected", projection["projected_confusion"]),
        "",
        "## Transition Counts",
        "",
        "| Transition | Count |",
        "| --- | ---: |",
    ]
    for key, value in projection["transition_counts"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
            f"- `{projection['baseline_metrics_path']}`",
            f"- `{projection['gold_path']}`",
            f"- `{projection['baseline_predictions_path']}`",
            f"- `{projection['cards_path']}`",
            f"- `{projection['projected_predictions_path']}`",
            "",
        ]
    )
    return "\n".join(lines)


def confusion_row(label: str, confusion: dict[str, int]) -> str:
    return "| {label} | {tp} | {tn} | {fp} | {fn} |".format(
        label=label,
        tp=confusion.get("tp", 0),
        tn=confusion.get("tn", 0),
        fp=confusion.get("fp", 0),
        fn=confusion.get("fn", 0),
    )


if __name__ == "__main__":
    raise SystemExit(main())
