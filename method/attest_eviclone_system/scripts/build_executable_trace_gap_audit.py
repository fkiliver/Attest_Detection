from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_trace_slice_localization_audit import (  # noqa: E402
    DEFAULT_ERROR_CARDS,
    DEFAULT_ERROR_CASES_JSONL,
    DEFAULT_ERROR_ROWS,
    DEFAULT_RUN_DIR,
    DEFAULT_TAXONOMY_CSV,
    TARGET_FAMILIES,
    classify_case,
    input_state,
    load_cards_by_pair,
    load_pair_by_case,
    load_rows_by_pair,
    load_taxonomy_by_case,
    nested_get,
    sorted_counter,
)

DEFAULT_OUTPUT = DEFAULT_RUN_DIR / "executable_trace_gap_audit.json"
DEFAULT_REPORT = DEFAULT_RUN_DIR / "executable_trace_gap_audit.md"

BUCKETS: dict[str, dict[str, Any]] = {
    "trace_ready": {
        "priority": 0,
        "action": "No trace repair needed.",
    },
    "probe_synthesis_needed": {
        "priority": 1,
        "action": "Generate source/sink or return-value probes for cases where LLM-completed context already compiles.",
    },
    "runtime_harness_repair": {
        "priority": 2,
        "action": "Repair harness inputs, mocks, or environment assumptions for cases that compile but fail at execution.",
    },
    "timeout_runtime_repair": {
        "priority": 3,
        "action": "Add bounded inputs, timeouts, or side-effect guards for cases that hang during execution.",
    },
    "context_compile_repair": {
        "priority": 4,
        "action": "Repair LLM-completed contexts that were generated but still fail javac compilation.",
    },
    "context_completion_needed": {
        "priority": 5,
        "action": "Rerun or redesign LLM context completion for rejected, not-recoverable, failed, or missing contexts.",
    },
    "compile_retry_needed": {
        "priority": 6,
        "action": "Retry original compile failures whose context state is ambiguous or unexpectedly complete.",
    },
    "missing_card": {
        "priority": 7,
        "action": "Generate a usable evidence card before trace repair can be classified.",
    },
    "unclassified_missing_trace": {
        "priority": 8,
        "action": "Inspect this case manually and add a new trace-gap bucket if the status is recurring.",
    },
}

LOCAL_REPAIR_BUCKETS = {
    "probe_synthesis_needed",
    "runtime_harness_repair",
    "timeout_runtime_repair",
    "context_compile_repair",
    "compile_retry_needed",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage missing executable traces for T3/T7 cases.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--taxonomy-csv", type=Path, default=DEFAULT_TAXONOMY_CSV)
    parser.add_argument("--error-cases-jsonl", type=Path, default=DEFAULT_ERROR_CASES_JSONL)
    parser.add_argument("--error-rows", type=Path, default=DEFAULT_ERROR_ROWS)
    parser.add_argument("--error-cards", type=Path, default=DEFAULT_ERROR_CARDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    audit = build_executable_trace_gap_audit(
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
    return 0 if audit["status"] in {"trace_ready", "trace_gap_triaged"} else 2


def build_executable_trace_gap_audit(
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
    all_items: list[dict[str, Any]] = []
    for family, point_id in TARGET_FAMILIES.items():
        items = []
        case_ids = sorted(case_id for case_id, row in taxonomy_by_case.items() if row.get("static_failure_family") == family)
        for case_id in case_ids:
            pair = pair_by_case.get(case_id)
            row = rows_by_pair.get(pair) if pair else None
            if row is None and pair:
                row = rows_by_pair.get((pair[1], pair[0]))
            card = cards_by_pair.get(pair) if pair else None
            if card is None and pair:
                card = cards_by_pair.get((pair[1], pair[0]))
            item = classify_case(case_id=case_id, point_id=point_id, family=family, pair=pair, row=row, card=card)
            item["trace_gap_bucket"] = trace_gap_bucket(item)
            item["trace_gap_priority"] = BUCKETS[item["trace_gap_bucket"]]["priority"]
            items.append(item)
        all_items.extend(items)
        pain_points.append(summarize_point_gap(point_id=point_id, family=family, items=items))

    summary = summarize_all(all_items)
    return {
        "schema_version": "eviclone-executable-trace-gap/v1",
        "status": audit_status(summary),
        "created_at_utc": now.isoformat(),
        "run_dir": str(run_dir.resolve()),
        "inputs": {
            "taxonomy_csv": input_state(taxonomy_csv),
            "error_cases_jsonl": input_state(error_cases_jsonl),
            "error_rows_csv": input_state(error_rows_csv),
            "error_cards_jsonl": input_state(error_cards_jsonl),
        },
        "summary": summary,
        "pain_points": pain_points,
        "bucket_definitions": {
            key: {"priority": value["priority"], "action": value["action"]} for key, value in BUCKETS.items()
        },
        "interpretation": {
            "what_this_adds": (
                "This audit separates T3/T7 executable-trace gaps by repair surface instead of treating all missing "
                "traces as one undifferentiated blocker."
            ),
            "main_repair_surface": main_repair_surface(summary),
        },
    }


def trace_gap_bucket(item: dict[str, Any]) -> str:
    if not item.get("card_available"):
        return "missing_card"
    if item.get("execution_trace_available"):
        return "trace_ready"
    status = str(item.get("execution_status") or "missing")
    context_status = str(item.get("context_status") or "missing")
    if status == "llm_context_compile_success_no_probe":
        return "probe_synthesis_needed"
    if status == "llm_context_execution_failed":
        return "runtime_harness_repair"
    if status == "timeout":
        return "timeout_runtime_repair"
    if status == "llm_context_compile_failed":
        return "context_compile_repair"
    if status == "compile_failed":
        if context_status in {"completed"}:
            return "compile_retry_needed"
        return "context_completion_needed"
    if context_status in {"not_recoverable", "rejected", "failed", "none", "missing"}:
        return "context_completion_needed"
    return "unclassified_missing_trace"


def summarize_all(items: list[dict[str, Any]]) -> dict[str, Any]:
    missing = [item for item in items if item.get("trace_gap_bucket") != "trace_ready"]
    buckets = Counter(str(item.get("trace_gap_bucket") or "unclassified_missing_trace") for item in items)
    return {
        "target_pain_points": ["T3", "T7"],
        "case_count": len(items),
        "card_available": sum(1 for item in items if item.get("card_available")),
        "execution_trace_available": buckets.get("trace_ready", 0),
        "missing_trace": len(missing),
        "missing_trace_rate": len(missing) / len(items) if items else 0.0,
        "bucket_counts": sorted_counter(buckets),
        "local_trace_repair_candidates": sum(1 for item in items if item.get("trace_gap_bucket") in LOCAL_REPAIR_BUCKETS),
        "probe_synthesis_candidates": buckets.get("probe_synthesis_needed", 0),
        "context_compile_repair_candidates": buckets.get("context_compile_repair", 0),
        "runtime_repair_candidates": buckets.get("runtime_harness_repair", 0) + buckets.get("timeout_runtime_repair", 0),
        "context_completion_needed": buckets.get("context_completion_needed", 0),
        "unclassified_missing_trace": buckets.get("unclassified_missing_trace", 0),
        "candidate_correct_missing_trace": sum(1 for item in missing if item.get("candidate_correct")),
        "localized_missing_trace": sum(
            1
            for item in missing
            if item.get("positive_slice_localized") or item.get("source_sink_signal") or item.get("shared_test_intentions", 0) > 0
        ),
    }


def summarize_point_gap(*, point_id: str, family: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = Counter(str(item.get("trace_gap_bucket") or "unclassified_missing_trace") for item in items)
    bucket_rows = []
    for bucket, count in sorted(buckets.items(), key=lambda entry: (BUCKETS.get(entry[0], BUCKETS["unclassified_missing_trace"])["priority"], entry[0])):
        bucket_items = [item for item in items if item.get("trace_gap_bucket") == bucket]
        missing_bucket_items = [item for item in bucket_items if bucket != "trace_ready"]
        bucket_rows.append(
            {
                "bucket": bucket,
                "priority": BUCKETS.get(bucket, BUCKETS["unclassified_missing_trace"])["priority"],
                "count": count,
                "candidate_correct": sum(1 for item in bucket_items if item.get("candidate_correct")),
                "gate_overrides": sum(1 for item in bucket_items if item.get("gate_override")),
                "localized": sum(
                    1
                    for item in bucket_items
                    if item.get("positive_slice_localized") or item.get("source_sink_signal") or item.get("shared_test_intentions", 0) > 0
                ),
                "source_sink_signal": sum(1 for item in bucket_items if item.get("source_sink_signal")),
                "execution_status_counts": sorted_counter(Counter(str(item.get("execution_status") or "missing") for item in bucket_items)),
                "context_status_counts": sorted_counter(Counter(str(item.get("context_status") or "missing") for item in bucket_items)),
                "next_action": BUCKETS.get(bucket, BUCKETS["unclassified_missing_trace"])["action"],
                "examples": [example_item(item) for item in (missing_bucket_items or bucket_items)[:5]],
            }
        )
    missing = [item for item in items if item.get("trace_gap_bucket") != "trace_ready"]
    return {
        "id": point_id,
        "family": family,
        "case_count": len(items),
        "execution_trace_available": buckets.get("trace_ready", 0),
        "missing_trace": len(missing),
        "missing_trace_rate": len(missing) / len(items) if items else 0.0,
        "bucket_counts": sorted_counter(buckets),
        "local_trace_repair_candidates": sum(1 for item in items if item.get("trace_gap_bucket") in LOCAL_REPAIR_BUCKETS),
        "candidate_correct_missing_trace": sum(1 for item in missing if item.get("candidate_correct")),
        "localized_missing_trace": sum(
            1
            for item in missing
            if item.get("positive_slice_localized") or item.get("source_sink_signal") or item.get("shared_test_intentions", 0) > 0
        ),
        "priority_buckets": bucket_rows,
    }


def audit_status(summary: dict[str, Any]) -> str:
    if summary["card_available"] != summary["case_count"]:
        return "incomplete"
    if summary["missing_trace"] == 0:
        return "trace_ready"
    if summary["unclassified_missing_trace"] == 0:
        return "trace_gap_triaged"
    return "trace_gap_partial"


def main_repair_surface(summary: dict[str, Any]) -> str:
    counts = summary.get("bucket_counts") if isinstance(summary.get("bucket_counts"), dict) else {}
    ranked = [
        (BUCKETS.get(bucket, BUCKETS["unclassified_missing_trace"])["priority"], bucket, count)
        for bucket, count in counts.items()
        if bucket != "trace_ready" and count
    ]
    if not ranked:
        return "All target cases already have executable traces."
    _, bucket, count = sorted(ranked)[0]
    return f"{bucket}: {count} cases. {BUCKETS.get(bucket, BUCKETS['unclassified_missing_trace'])['action']}"


def example_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": item.get("case_id"),
        "pair": item.get("pair"),
        "candidate_correct": item.get("candidate_correct"),
        "gate_override": item.get("gate_override"),
        "positive_slice_localized": item.get("positive_slice_localized"),
        "source_sink_signal": item.get("source_sink_signal"),
        "execution_status": item.get("execution_status"),
        "context_status": item.get("context_status"),
        "trace_gap_bucket": item.get("trace_gap_bucket"),
    }


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Executable Trace Gap Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| case_count | {audit['summary']['case_count']} |",
        f"| execution_trace_available | {audit['summary']['execution_trace_available']} |",
        f"| missing_trace | {audit['summary']['missing_trace']} |",
        f"| missing_trace_rate | {audit['summary']['missing_trace_rate']:.6g} |",
        f"| local_trace_repair_candidates | {audit['summary']['local_trace_repair_candidates']} |",
        f"| probe_synthesis_candidates | {audit['summary']['probe_synthesis_candidates']} |",
        f"| context_compile_repair_candidates | {audit['summary']['context_compile_repair_candidates']} |",
        f"| runtime_repair_candidates | {audit['summary']['runtime_repair_candidates']} |",
        f"| context_completion_needed | {audit['summary']['context_completion_needed']} |",
        f"| candidate_correct_missing_trace | {audit['summary']['candidate_correct_missing_trace']} |",
        f"| localized_missing_trace | {audit['summary']['localized_missing_trace']} |",
        "",
        "## Bucket Counts",
        "",
        "| bucket | count | priority | next action |",
        "| --- | ---: | ---: | --- |",
    ]
    for bucket, count in audit["summary"]["bucket_counts"].items():
        meta = audit["bucket_definitions"].get(bucket, audit["bucket_definitions"]["unclassified_missing_trace"])
        lines.append(f"| {bucket} | {count} | {meta['priority']} | {meta['action']} |")
    lines.extend(
        [
            "",
            "## Pain Points",
            "",
            "| id | cases | traces | missing | local repair | candidate-correct missing | localized missing | top missing bucket |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for point in audit["pain_points"]:
        top_bucket = next((row["bucket"] for row in point["priority_buckets"] if row["bucket"] != "trace_ready"), "none")
        lines.append(
            f"| {point['id']} | {point['case_count']} | {point['execution_trace_available']} | {point['missing_trace']} | "
            f"{point['local_trace_repair_candidates']} | {point['candidate_correct_missing_trace']} | "
            f"{point['localized_missing_trace']} | {top_bucket} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            audit["interpretation"]["what_this_adds"],
            "",
            audit["interpretation"]["main_repair_surface"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
