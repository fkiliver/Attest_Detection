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

DEFAULT_RUN_DIR = REPO_ROOT / "eviclone_runs" / "codebert_error_cases_full"
DEFAULT_TAXONOMY_CSV = (
    REPO_ROOT
    / "release_inputs"
    / "case_studies"
    / "static_analysis_failure_full_case_study"
    / "per_case_static_failure_case_studies_compact.csv"
)
DEFAULT_ERROR_CASES_JSONL = REPO_ROOT / "release_inputs" / "case_studies" / "all_error_case_studies" / "all_error_case_studies.jsonl"
DEFAULT_ERROR_ROWS = DEFAULT_RUN_DIR / "pipeline_threshold149" / "threshold149_error_cards_only.rows.csv"
DEFAULT_ERROR_CARDS = DEFAULT_RUN_DIR / "configured_llm_llm_context_full_6550_final_merged.jsonl"
DEFAULT_OUTPUT = DEFAULT_RUN_DIR / "trace_slice_localization_audit.json"
DEFAULT_REPORT = DEFAULT_RUN_DIR / "trace_slice_localization_audit.md"

TARGET_FAMILIES = {
    "subfunction_granularity_false_negative": "T3",
    "dataflow_side_effect_failure": "T7",
}
SOURCE_SINK_FEATURES = {
    "copy_file",
    "download_web",
    "zip_decompress",
    "secure_hash",
    "ftp",
    "db_query",
    "database",
    "json_parse",
}
SOURCE_SINK_OBSERVATIONS = {
    "file_effect",
    "state_change",
    "stream_reading",
    "trace",
    "return_value|state_change",
    "side_effect",
    "source_sink",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit T3/T7 slice and source-sink localization evidence.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--taxonomy-csv", type=Path, default=DEFAULT_TAXONOMY_CSV)
    parser.add_argument("--error-cases-jsonl", type=Path, default=DEFAULT_ERROR_CASES_JSONL)
    parser.add_argument("--error-rows", type=Path, default=DEFAULT_ERROR_ROWS)
    parser.add_argument("--error-cards", type=Path, default=DEFAULT_ERROR_CARDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    audit = build_trace_slice_localization_audit(
        run_dir=args.run_dir,
        taxonomy_csv=args.taxonomy_csv,
        error_cases_jsonl=args.error_cases_jsonl,
        error_rows_csv=args.error_rows,
        error_cards_jsonl=args.error_cards,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_report(args.report, audit)
    print(json.dumps({"status": audit["status"], "output": str(args.output.resolve())}, ensure_ascii=False))
    return 0 if audit["status"] in {"slice_localized_partial_trace", "trace_ready"} else 2


def build_trace_slice_localization_audit(
    *,
    run_dir: Path,
    taxonomy_csv: Path,
    error_cases_jsonl: Path,
    error_rows_csv: Path,
    error_cards_jsonl: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    taxonomy_by_case = load_taxonomy_by_case(taxonomy_csv)
    pair_by_case = load_pair_by_case(error_cases_jsonl)
    rows_by_pair = load_rows_by_pair(error_rows_csv)
    cards_by_pair = load_cards_by_pair(error_cards_jsonl)
    pain_points = []
    all_cases = 0
    all_joined = 0
    all_cards = 0
    all_slice = 0
    all_trace = 0
    for family, point_id in TARGET_FAMILIES.items():
        case_ids = sorted(case_id for case_id, row in taxonomy_by_case.items() if row.get("static_failure_family") == family)
        items = []
        for case_id in case_ids:
            pair = pair_by_case.get(case_id)
            row = rows_by_pair.get(pair) if pair else None
            if row is None and pair:
                row = rows_by_pair.get((pair[1], pair[0]))
            card = cards_by_pair.get(pair) if pair else None
            if card is None and pair:
                card = cards_by_pair.get((pair[1], pair[0]))
            items.append(classify_case(case_id=case_id, point_id=point_id, family=family, pair=pair, row=row, card=card))
        summary = summarize_point(point_id=point_id, family=family, items=items)
        pain_points.append(summary)
        all_cases += summary["case_count"]
        all_joined += summary["joined_rows"]
        all_cards += summary["card_available"]
        all_slice += summary["positive_slice_localized"]
        all_trace += summary["execution_trace_available"]
    status = overall_status(pain_points)
    return {
        "schema_version": "eviclone-trace-slice-localization/v1",
        "status": status,
        "created_at_utc": now.isoformat(),
        "run_dir": str(run_dir.resolve()),
        "inputs": {
            "taxonomy_csv": input_state(taxonomy_csv),
            "error_cases_jsonl": input_state(error_cases_jsonl),
            "error_rows_csv": input_state(error_rows_csv),
            "error_cards_jsonl": input_state(error_cards_jsonl),
        },
        "summary": {
            "target_pain_points": ["T3", "T7"],
            "case_count": all_cases,
            "joined_rows": all_joined,
            "card_available": all_cards,
            "positive_slice_localized": all_slice,
            "execution_trace_available": all_trace,
            "positive_slice_rate": all_slice / all_cards if all_cards else 0.0,
            "execution_trace_rate": all_trace / all_cards if all_cards else 0.0,
        },
        "pain_points": pain_points,
        "interpretation": {
            "what_is_covered": (
                "Existing evidence cards already localize many T3/T7 cases to shared functional slices, source/sink "
                "signals, shared test intentions, or counterexamples."
            ),
            "what_remains": (
                "Most localized evidence is still card-level or compile-only. Executed trace evidence is sparse, so "
                "full top-conference claims still need executable source/sink traces after repair cards are available."
            ),
        },
    }


def classify_case(
    *,
    case_id: int,
    point_id: str,
    family: str,
    pair: tuple[str, str] | None,
    row: dict[str, str] | None,
    card: dict[str, Any] | None,
) -> dict[str, Any]:
    llm = card.get("llm_evidence") if isinstance(card, dict) and isinstance(card.get("llm_evidence"), dict) else {}
    local = card.get("local_evidence") if isinstance(card, dict) and isinstance(card.get("local_evidence"), dict) else {}
    dyn = card.get("dynamic_evidence") if isinstance(card, dict) and isinstance(card.get("dynamic_evidence"), dict) else {}
    shared_slice = llm.get("shared_functional_slice") if isinstance(llm.get("shared_functional_slice"), dict) else {}
    execution = dyn.get("execution") if isinstance(dyn.get("execution"), dict) else {}
    parsed = execution.get("parsed") if isinstance(execution.get("parsed"), dict) else None
    context = dyn.get("llm_context_completion") if isinstance(dyn.get("llm_context_completion"), dict) else {}
    shared_tests = llm.get("shared_test_intentions") if isinstance(llm.get("shared_test_intentions"), list) else []
    counterexamples = llm.get("counterexample_ideas") if isinstance(llm.get("counterexample_ideas"), list) else []
    shared_features = list_or_empty(local.get("shared_feature_families"))
    feature_a = list_or_empty(nested_get(local, ["code_a", "feature_families"]))
    feature_b = list_or_empty(nested_get(local, ["code_b", "feature_families"]))
    observation_terms = shared_test_observation_terms(shared_tests)
    source_sink_signal = bool((set(map(str, shared_features + feature_a + feature_b)) & SOURCE_SINK_FEATURES) or observation_terms)
    candidate_correct = row is not None and row.get("gold") in {"0", "1"} and row.get("ours_pred") == row.get("gold")
    gate_override = row is not None and parse_bool(row.get("override"))
    return {
        "case_id": case_id,
        "point_id": point_id,
        "family": family,
        "pair": pair,
        "joined_row": row is not None,
        "card_available": card is not None,
        "candidate_correct": candidate_correct,
        "gate_override": gate_override,
        "slice_description_available": bool(shared_slice.get("description")),
        "positive_slice_localized": bool(shared_slice.get("exists") is True and shared_slice.get("description")),
        "slice_alignment": shared_slice.get("bcb_target_alignment"),
        "source_sink_signal": source_sink_signal,
        "source_sink_observation_terms": sorted(observation_terms),
        "shared_feature_families": shared_features,
        "shared_test_intentions": len(shared_tests),
        "counterexample_ideas": len(counterexamples),
        "execution_trace_available": dyn.get("status") == "executed" and parsed is not None,
        "execution_status": dyn.get("status"),
        "execution_parsed_status": parsed.get("status") if isinstance(parsed, dict) else None,
        "context_completed": context.get("status") == "completed",
        "context_status": context.get("status") or (row.get("context_status") if row else None),
    }


def summarize_point(*, point_id: str, family: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    card_items = [item for item in items if item["card_available"]]
    candidate_correct = [item for item in items if item["candidate_correct"]]
    override_items = [item for item in items if item["gate_override"]]
    positive_slice = [item for item in items if item["positive_slice_localized"]]
    traces = [item for item in items if item["execution_trace_available"]]
    source_sink = [item for item in items if item["source_sink_signal"]]
    shared_tests = [item for item in items if item["shared_test_intentions"] > 0]
    counterexamples = [item for item in items if item["counterexample_ideas"] > 0]
    return {
        "id": point_id,
        "family": family,
        "case_count": len(items),
        "joined_rows": sum(1 for item in items if item["joined_row"]),
        "card_available": len(card_items),
        "candidate_correct": len(candidate_correct),
        "gate_overrides": len(override_items),
        "positive_slice_localized": len(positive_slice),
        "slice_description_available": sum(1 for item in items if item["slice_description_available"]),
        "source_sink_signal": len(source_sink),
        "shared_test_intentions": len(shared_tests),
        "counterexample_ideas": len(counterexamples),
        "execution_trace_available": len(traces),
        "context_completed": sum(1 for item in items if item["context_completed"]),
        "positive_slice_rate": len(positive_slice) / len(card_items) if card_items else 0.0,
        "source_sink_signal_rate": len(source_sink) / len(card_items) if card_items else 0.0,
        "execution_trace_rate": len(traces) / len(card_items) if card_items else 0.0,
        "alignment_counts": sorted_counter(Counter(str(item["slice_alignment"] or "none") for item in items)),
        "execution_status_counts": sorted_counter(Counter(str(item["execution_status"] or "missing") for item in items)),
        "context_status_counts": sorted_counter(Counter(str(item["context_status"] or "missing") for item in items)),
        "localization_status": point_status(items),
        "examples": [example_item(item) for item in items if item["positive_slice_localized"] or item["execution_trace_available"]][:5],
    }


def point_status(items: list[dict[str, Any]]) -> str:
    card_items = [item for item in items if item["card_available"]]
    if not items or len(card_items) != len(items):
        return "incomplete"
    if all(item["execution_trace_available"] for item in card_items):
        return "trace_ready"
    if any(item["positive_slice_localized"] or item["source_sink_signal"] or item["shared_test_intentions"] for item in card_items):
        return "slice_localized_partial_trace"
    return "card_level_only"


def overall_status(pain_points: list[dict[str, Any]]) -> str:
    statuses = {point["localization_status"] for point in pain_points}
    if "incomplete" in statuses:
        return "incomplete"
    if statuses == {"trace_ready"}:
        return "trace_ready"
    if any(status == "slice_localized_partial_trace" for status in statuses):
        return "slice_localized_partial_trace"
    return "card_level_only"


def example_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": item["case_id"],
        "pair": item["pair"],
        "candidate_correct": item["candidate_correct"],
        "gate_override": item["gate_override"],
        "positive_slice_localized": item["positive_slice_localized"],
        "slice_alignment": item["slice_alignment"],
        "source_sink_signal": item["source_sink_signal"],
        "execution_trace_available": item["execution_trace_available"],
        "execution_status": item["execution_status"],
    }


def shared_test_observation_terms(shared_tests: list[Any]) -> set[str]:
    terms = set()
    for item in shared_tests:
        if not isinstance(item, dict):
            continue
        expected = str(item.get("expected_observation") or "").lower()
        for term in SOURCE_SINK_OBSERVATIONS:
            if term in expected:
                terms.add(term)
    return terms


def load_taxonomy_by_case(path: Path) -> dict[int, dict[str, str]]:
    rows = {}
    for row in load_csv_rows(path):
        case_id = int_or_none(row.get("case_id"))
        if case_id is not None:
            rows[case_id] = row
    return rows


def load_pair_by_case(path: Path) -> dict[int, tuple[str, str]]:
    pairs = {}
    if not path.exists():
        return pairs
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            case_id = int_or_none(row.get("case_id"))
            a = str(row.get("function_id_a") or "")
            b = str(row.get("function_id_b") or "")
            if case_id is not None and a and b:
                pairs[case_id] = (a, b)
    return pairs


def load_rows_by_pair(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows = {}
    for row in load_csv_rows(path):
        a = str(row.get("function_id_a") or "")
        b = str(row.get("function_id_b") or "")
        if a and b:
            rows[(a, b)] = row
    return rows


def load_cards_by_pair(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    cards = {}
    if not path.exists():
        return cards
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            card = json.loads(line)
            a = str(nested_get(card, ["function_ids", "a"]) or "")
            b = str(nested_get(card, ["function_ids", "b"]) or "")
            if a and b:
                cards[(a, b)] = card
    return cards


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Trace/Slice Localization Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| case_count | {audit['summary']['case_count']} |",
        f"| card_available | {audit['summary']['card_available']} |",
        f"| positive_slice_localized | {audit['summary']['positive_slice_localized']} |",
        f"| execution_trace_available | {audit['summary']['execution_trace_available']} |",
        f"| positive_slice_rate | {audit['summary']['positive_slice_rate']:.6g} |",
        f"| execution_trace_rate | {audit['summary']['execution_trace_rate']:.6g} |",
        "",
        "## Pain Points",
        "",
        "| id | cases | cards | candidate-correct | overrides | slice | source/sink | shared tests | traces | status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for point in audit["pain_points"]:
        lines.append(
            f"| {point['id']} | {point['case_count']} | {point['card_available']} | {point['candidate_correct']} | "
            f"{point['gate_overrides']} | {point['positive_slice_localized']} | {point['source_sink_signal']} | "
            f"{point['shared_test_intentions']} | {point['execution_trace_available']} | {point['localization_status']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            audit["interpretation"]["what_is_covered"],
            "",
            audit["interpretation"]["what_remains"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def input_state(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0}


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def int_or_none(value: Any) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def nested_get(obj: Any, keys: list[str]) -> Any:
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def list_or_empty(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def sorted_counter(counter: Counter | dict[str, int]) -> dict[str, int]:
    return {key: int(value) for key, value in sorted(dict(counter).items(), key=lambda item: (-int(item[1]), item[0]))}


if __name__ == "__main__":
    raise SystemExit(main())
