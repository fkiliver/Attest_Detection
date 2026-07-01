from __future__ import annotations

import argparse
import glob
import json
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


def read_triplet_pairs(path: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            parts = text.replace(",", " ").split()
            if len(parts) < 3:
                raise ValueError(f"expected id_a id_b label at {path}:{line_no}")
            pairs.append((parts[0], parts[1]))
    return pairs


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                yield json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_no}") from exc


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

    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    pred = decision.get("pred_label") if isinstance(decision, dict) else None
    coerced = coerce_label(pred)
    if coerced in (0, 1):
        return coerced
    direct = card.get("llm_direct_label")
    return coerce_label(direct)


def has_prediction(card: dict[str, Any], *, decision_source: str, abstain_label: int | None) -> bool:
    label = label_from_card(card, decision_source=decision_source)
    if label in (0, 1):
        return True
    return abstain_label in (0, 1)


def expand_patterns(patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    for pattern in patterns:
        matches = glob.glob(pattern)
        if not matches:
            candidate = Path(pattern)
            if candidate.exists():
                matches = [str(candidate)]
        for match in matches:
            path = Path(match)
            key = str(path.resolve())
            if path.is_file() and key not in seen:
                paths.append(path)
                seen.add(key)
    return sorted(paths, key=lambda p: str(p))


def audit_coverage(
    *,
    hardset_dir: Path,
    card_patterns: list[str],
    output: Path,
    decision_source: str,
    abstain_label: int | None,
) -> dict[str, Any]:
    hard_pairs = read_triplet_pairs(hardset_dir / "test.txt")
    hard_pair_set = set(hard_pairs) | {(b, a) for a, b in hard_pairs}
    files = expand_patterns(card_patterns)
    file_summaries: list[dict[str, Any]] = []
    global_covered: set[tuple[str, str]] = set()
    global_usable: set[tuple[str, str]] = set()

    for path in files:
        rows = 0
        covered: set[tuple[str, str]] = set()
        usable: set[tuple[str, str]] = set()
        examples: list[dict[str, Any]] = []
        for card in iter_jsonl(path):
            if not isinstance(card, dict):
                continue
            rows += 1
            pair = pair_from_card(card)
            if pair is None or pair not in hard_pair_set:
                continue
            canonical = pair if pair in hard_pairs else (pair[1], pair[0])
            covered.add(canonical)
            global_covered.add(canonical)
            if has_prediction(card, decision_source=decision_source, abstain_label=abstain_label):
                usable.add(canonical)
                global_usable.add(canonical)
            if len(examples) < 5:
                examples.append(
                    {
                        "pair": list(canonical),
                        "pair_id": card.get("pair_id"),
                        "has_prediction": has_prediction(
                            card,
                            decision_source=decision_source,
                            abstain_label=abstain_label,
                        ),
                    }
                )
        if covered:
            file_summaries.append(
                {
                    "path": str(path),
                    "rows": rows,
                    "covered_pairs": len(covered),
                    "usable_prediction_pairs": len(usable),
                    "examples": examples,
                }
            )

    summary = {
        "schema_version": "eviclone-llm-direct-hardset-coverage/v1",
        "status": "audited",
        "hardset_dir": str(hardset_dir),
        "hardset_rows": len(hard_pairs),
        "candidate_files": len(files),
        "decision_source": decision_source,
        "abstain_label": abstain_label,
        "files_with_coverage": len(file_summaries),
        "covered_pairs": len(global_covered),
        "usable_prediction_pairs": len(global_usable),
        "complete_usable_coverage": len(global_usable) == len(hard_pairs),
        "file_summaries": file_summaries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit whether existing LLM card files cover a HardSet.")
    parser.add_argument("--hardset-dir", type=Path, required=True)
    parser.add_argument("--card-glob", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--decision-source",
        choices=["decision", "llm_pred", "llm_bcb_gold", "llm_semantic"],
        default="decision",
    )
    parser.add_argument(
        "--abstain-label",
        choices=["error", "0", "1"],
        default="error",
        help="Count abstentions as usable when the downstream export maps them to this label.",
    )
    args = parser.parse_args()

    abstain_label = None if args.abstain_label == "error" else int(args.abstain_label)
    summary = audit_coverage(
        hardset_dir=args.hardset_dir,
        card_patterns=args.card_glob,
        output=args.output,
        decision_source=args.decision_source,
        abstain_label=abstain_label,
    )
    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_files": summary["candidate_files"],
                "covered_pairs": summary["covered_pairs"],
                "usable_prediction_pairs": summary["usable_prediction_pairs"],
                "complete_usable_coverage": summary["complete_usable_coverage"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
