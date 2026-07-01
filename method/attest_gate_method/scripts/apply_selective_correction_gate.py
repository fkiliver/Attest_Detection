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

from attest_gate.selective_gate import (
    BaselineRow,
    card_features,
    card_pair_key,
    coerce_label,
    default_override_score,
    load_cards,
    read_triplet_file,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply a selective correction gate to baseline clone predictions without using gold labels."
    )
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--cards", type=Path, action="append", default=[])
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--policy-file", type=Path, default=None)
    parser.add_argument("--actual", type=Path, default=None, help="optional labels for post-hoc metrics only")
    parser.add_argument("--output-predictions", type=Path, required=True)
    parser.add_argument("--output-summary", type=Path, required=True)
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--override-csv", type=Path, default=None)
    args = parser.parse_args()

    prediction_rows = read_triplet_file(args.predictions)
    cards = []
    for path in args.cards:
        cards.extend(load_cards(path))
    actual_rows = read_triplet_file(args.actual) if args.actual else None
    policy = load_policy(args.policy_file) if args.policy_file else None
    threshold = resolve_threshold(args.threshold, policy)
    result = apply_gate_to_predictions(
        prediction_rows,
        cards,
        threshold=threshold,
        actual_rows=actual_rows,
    )

    args.output_predictions.parent.mkdir(parents=True, exist_ok=True)
    with args.output_predictions.open("w", encoding="utf-8", newline="\n") as f:
        for row in result["prediction_rows"]:
            f.write(f"{row['function_id_a']}\t{row['function_id_b']}\t{row['final_pred']}\n")

    summary = {
        "predictions": str(args.predictions.resolve()),
        "cards": [str(path.resolve()) for path in args.cards],
        "threshold": threshold,
        "policy_file": str(args.policy_file.resolve()) if args.policy_file else None,
        "policy": policy,
        "actual": str(args.actual.resolve()) if args.actual else None,
        "output_predictions": str(args.output_predictions.resolve()),
        "output_csv": str(args.csv.resolve()) if args.csv else None,
        "output_override_csv": str(args.override_csv.resolve()) if args.override_csv else None,
        **result["summary"],
    }
    args.output_summary.parent.mkdir(parents=True, exist_ok=True)
    args.output_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    if args.csv:
        write_csv(args.csv, result["rows"])
    if args.override_csv:
        write_csv(args.override_csv, override_rows(result["rows"]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_policy(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema_version") != "attest-selective-gate-policy/v1":
        raise ValueError(f"unsupported selective gate policy schema: {obj.get('schema_version')}")
    if obj.get("gate_type") != "heuristic_override_score":
        raise ValueError(f"unsupported selective gate type: {obj.get('gate_type')}")
    if "threshold" not in obj:
        raise ValueError("selective gate policy is missing threshold")
    return obj


def resolve_threshold(cli_threshold: float | None, policy: dict[str, Any] | None) -> float:
    if cli_threshold is not None:
        return float(cli_threshold)
    if policy is not None:
        return float(policy["threshold"])
    return 1.49


def apply_gate_to_predictions(
    prediction_rows: list[tuple[str, str, int]],
    cards: list[dict[str, Any]],
    *,
    threshold: float,
    actual_rows: list[tuple[str, str, int]] | None = None,
) -> dict[str, Any]:
    card_by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    duplicate_cards = 0
    duplicate_cards_ignored_unusable = 0
    for card in cards:
        key = card_pair_key(card)
        if key in card_by_pair:
            duplicate_cards += 1
            if not should_replace_effective_card(card_by_pair[key], card):
                duplicate_cards_ignored_unusable += 1
                continue
        card_by_pair[key] = card

    actual_by_pair: dict[tuple[str, str], int] = {}
    if actual_rows is not None:
        for function_id_a, function_id_b, gold in actual_rows:
            actual_by_pair[(function_id_a, function_id_b)] = int(gold)

    counters = Counter()
    by_dynamic = Counter()
    by_context = Counter()
    output_predictions: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    seen_prediction_keys: set[tuple[str, str]] = set()

    for function_id_a, function_id_b, base_pred in prediction_rows:
        key = (str(function_id_a), str(function_id_b))
        seen_prediction_keys.add(key)
        counters["total_predictions"] += 1
        card = card_by_pair.get(key)
        final_pred = int(base_pred)
        score: float | None = None
        override = False
        attest_pred: int | None = None
        dynamic_status = "missing_card"
        context_status = "missing_card"
        if card is None:
            counters["missing_card"] += 1
        else:
            counters["matched_card"] += 1
            baseline = BaselineRow(key[0], key[1], gold=-1, prediction=int(base_pred))
            features = card_features(card, baseline)
            score = default_override_score(features)
            attest_pred = features.get("attest_pred")
            override = bool(features.get("base_attest_disagree")) and score >= threshold
            dynamic_status = str(features.get("dynamic_status"))
            context_status = str(features.get("context_status"))
            if override and attest_pred in (0, 1):
                final_pred = int(attest_pred)
                counters["override"] += 1
                by_dynamic[dynamic_status] += 1
                by_context[context_status] += 1
            else:
                counters["keep"] += 1

        gold = actual_by_pair.get(key)
        baseline_correct = None
        final_correct = None
        if gold in (0, 1):
            baseline_correct = int(base_pred) == gold
            final_correct = final_pred == gold
            counters["actual_available"] += 1
            if baseline_correct and not final_correct:
                counters["damage"] += 1
            elif not baseline_correct and final_correct:
                counters["correction"] += 1

        output_predictions.append(
            {
                "function_id_a": key[0],
                "function_id_b": key[1],
                "baseline_pred": int(base_pred),
                "final_pred": final_pred,
            }
        )
        rows.append(
            {
                "function_id_a": key[0],
                "function_id_b": key[1],
                "gold": gold,
                "baseline_pred": int(base_pred),
                "attest_pred": attest_pred,
                "score": score,
                "override": override,
                "final_pred": final_pred,
                "baseline_correct": baseline_correct,
                "final_correct": final_correct,
                "dynamic_status": dynamic_status,
                "context_status": context_status,
            }
        )

    unmatched_cards = len(set(card_by_pair) - seen_prediction_keys)
    summary: dict[str, Any] = {
        "total_predictions": counters["total_predictions"],
        "card_count": len(cards),
        "duplicate_cards": duplicate_cards,
        "duplicate_cards_ignored_unusable": duplicate_cards_ignored_unusable,
        "card_selection_rule": "usable_card_priority_last_usable_wins",
        "matched_cards": counters["matched_card"],
        "missing_cards": counters["missing_card"],
        "unmatched_cards": unmatched_cards,
        "override_count": counters["override"],
        "override_rate": ratio(counters["override"], counters["total_predictions"]),
        "override_by_dynamic_status": dict(by_dynamic.most_common()),
        "override_by_context_status": dict(by_context.most_common()),
    }
    if actual_rows is not None:
        summary.update(
            {
                "actual_available": counters["actual_available"],
                "corrections": counters["correction"],
                "damage": counters["damage"],
                "net_gain": counters["correction"] - counters["damage"],
                "baseline_metrics": metrics(rows, pred_key="baseline_pred"),
                "final_metrics": metrics(rows, pred_key="final_pred"),
            }
        )
    return {
        "prediction_rows": output_predictions,
        "rows": rows,
        "summary": summary,
    }


def card_is_usable_for_gate(card: dict[str, Any]) -> bool:
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    return coerce_label(decision.get("pred_label")) in (0, 1)


def should_replace_effective_card(existing: dict[str, Any], candidate: dict[str, Any]) -> bool:
    existing_usable = card_is_usable_for_gate(existing)
    candidate_usable = card_is_usable_for_gate(candidate)
    return candidate_usable or not existing_usable


def metrics(rows: list[dict[str, Any]], *, pred_key: str) -> dict[str, float]:
    counts = Counter()
    for row in rows:
        gold = row.get("gold")
        pred = row.get(pred_key)
        if gold not in (0, 1) or pred not in (0, 1):
            continue
        if gold == 1 and pred == 1:
            counts["tp"] += 1
        elif gold == 0 and pred == 0:
            counts["tn"] += 1
        elif gold == 0 and pred == 1:
            counts["fp"] += 1
        else:
            counts["fn"] += 1
    tp = counts["tp"]
    tn = counts["tn"]
    fp = counts["fp"]
    fn = counts["fn"]
    total = tp + tn + fp + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": round((tp + tn) / total, 6) if total else 0.0,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round((2 * precision * recall / (precision + recall)), 6) if precision + recall else 0.0,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "function_id_a",
        "function_id_b",
        "gold",
        "baseline_pred",
        "attest_pred",
        "score",
        "override",
        "final_pred",
        "baseline_correct",
        "final_correct",
        "dynamic_status",
        "context_status",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def override_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("override") is True]


def ratio(num: int | float, den: int | float) -> float:
    return round(float(num) / float(den), 6) if den else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
