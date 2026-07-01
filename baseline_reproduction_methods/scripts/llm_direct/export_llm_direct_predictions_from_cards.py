from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


VERDICT_TO_LABEL = {
    "behaviorally_supported_clone": 1,
    "likely_clone": 1,
    "benchmark_supported_clone": 1,
    "clone": 1,
    "behaviorally_supported_non_clone": 0,
    "likely_non_clone": 0,
    "benchmark_supported_non_clone": 0,
    "non_clone_supported": 0,
    "non_clone": 0,
    "context_insufficient": None,
    "unknown": None,
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_no}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"expected object at {path}:{line_no}")
            rows.append(value)
    return rows


def read_triplets(path: Path) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            parts = text.replace(",", " ").split()
            if len(parts) < 3:
                raise ValueError(f"expected id_a id_b label at {path}:{line_no}")
            rows.append((parts[0], parts[1], int(parts[2])))
    return rows


def coerce_label(value: Any) -> int | None:
    if value in (0, 1):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text in {"0", "1"}:
            return int(text)
        return VERDICT_TO_LABEL.get(text)
    return None


def label_from_card(card: dict[str, Any], *, decision_source: str) -> int | None:
    llm = card.get("llm_evidence") if isinstance(card.get("llm_evidence"), dict) else {}
    if decision_source == "llm_pred":
        pred = coerce_label(llm.get("pred_label"))
        return pred if pred in (0, 1) else coerce_label(llm.get("verdict"))
    if decision_source == "llm_bcb_gold":
        return coerce_label(llm.get("bcb_gold_verdict"))
    if decision_source == "llm_semantic":
        return coerce_label(llm.get("semantic_verdict"))

    # Evidence-card schema from scripts/run_llm_unordered.py.
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    pred = decision.get("pred_label") if isinstance(decision, dict) else None
    coerced = coerce_label(pred)
    if coerced in (0, 1):
        return coerced

    # Direct audit schema used by older DSFM-error runs.
    direct = card.get("llm_direct_label")
    return coerce_label(direct)


def pair_from_card(card: dict[str, Any]) -> tuple[str, str] | None:
    function_ids = card.get("function_ids") if isinstance(card.get("function_ids"), dict) else {}
    if function_ids:
        a = function_ids.get("a")
        b = function_ids.get("b")
        if a is not None and b is not None:
            return str(a), str(b)
    a = card.get("function_id_a")
    b = card.get("function_id_b")
    if a is not None and b is not None:
        return str(a), str(b)
    return None


def export_predictions(
    *,
    cards_path: Path,
    gold_path: Path,
    output_path: Path,
    abstain_label: int | None = None,
    decision_source: str = "decision",
) -> dict[str, Any]:
    gold_rows = read_triplets(gold_path)
    cards = read_jsonl(cards_path)
    by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    duplicate_pairs: Counter[tuple[str, str]] = Counter()
    for card in cards:
        pair = pair_from_card(card)
        if pair is None:
            continue
        if pair in by_pair:
            duplicate_pairs[pair] += 1
        by_pair[pair] = card

    output_path.parent.mkdir(parents=True, exist_ok=True)
    missing: list[dict[str, Any]] = []
    abstained: list[dict[str, Any]] = []
    prediction_counts: Counter[int] = Counter()
    with output_path.open("w", encoding="utf-8", newline="\n") as sink:
        for row_index, (id_a, id_b, _gold) in enumerate(gold_rows, start=1):
            card = by_pair.get((id_a, id_b)) or by_pair.get((id_b, id_a))
            if card is None:
                missing.append({"row": row_index, "pair": [id_a, id_b]})
                continue
            label = label_from_card(card, decision_source=decision_source)
            if label is None:
                abstained.append({"row": row_index, "pair": [id_a, id_b], "card_pair_id": card.get("pair_id")})
                if abstain_label is None:
                    continue
                label = abstain_label
            prediction_counts[label] += 1
            sink.write(f"{id_a}\t{id_b}\t{label}\n")

    exported_rows = sum(prediction_counts.values())
    summary = {
        "schema_version": "eviclone-llm-direct-prediction-export/v1",
        "status": "exported" if exported_rows == len(gold_rows) else "incomplete",
        "cards": str(cards_path),
        "gold": str(gold_path),
        "output": str(output_path),
        "decision_source": decision_source,
        "gold_rows": len(gold_rows),
        "card_rows": len(cards),
        "exported_rows": exported_rows,
        "missing_rows": len(missing),
        "abstained_rows": len(abstained),
        "abstain_label": abstain_label,
        "prediction_counts": {"0": int(prediction_counts[0]), "1": int(prediction_counts[1])},
        "duplicate_pair_count": int(sum(duplicate_pairs.values())),
        "missing_examples": missing[:20],
        "abstained_examples": abstained[:20],
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Export LLM-direct evidence-card decisions as triplet predictions.")
    parser.add_argument("--cards", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-path", type=Path, default=None)
    parser.add_argument(
        "--abstain-label",
        choices=["error", "0", "1"],
        default="error",
        help="How to export cards with no binary LLM decision. Default keeps export incomplete.",
    )
    parser.add_argument(
        "--decision-source",
        choices=["decision", "llm_pred", "llm_bcb_gold", "llm_semantic"],
        default="decision",
        help=(
            "Which retained card field to export. Use llm_bcb_gold for a direct LLM-as-judge baseline; "
            "the default preserves the post-processed system decision."
        ),
    )
    args = parser.parse_args()

    abstain_label = None if args.abstain_label == "error" else int(args.abstain_label)
    summary = export_predictions(
        cards_path=args.cards,
        gold_path=args.gold,
        output_path=args.output,
        abstain_label=abstain_label,
        decision_source=args.decision_source,
    )
    summary_path = args.summary_path or args.output.with_suffix(".summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "exported_rows": summary["exported_rows"],
                "missing_rows": summary["missing_rows"],
                "abstained_rows": summary["abstained_rows"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if summary["status"] == "exported" else 1


if __name__ == "__main__":
    raise SystemExit(main())
