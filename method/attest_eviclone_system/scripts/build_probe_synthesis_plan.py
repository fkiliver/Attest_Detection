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

from scripts.build_executable_trace_gap_audit import trace_gap_bucket  # noqa: E402
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

DEFAULT_OUTPUT = DEFAULT_RUN_DIR / "probe_synthesis_plan.json"
DEFAULT_REPORT = DEFAULT_RUN_DIR / "probe_synthesis_plan.md"
DEFAULT_CANDIDATES = DEFAULT_RUN_DIR / "probe_synthesis_candidates.jsonl"

SIMPLE_ARG_TYPES = {
    "String",
    "File",
    "Path",
    "URL",
    "URI",
    "InputStream",
    "OutputStream",
    "Reader",
    "Writer",
    "BufferedReader",
    "BufferedWriter",
    "byte[]",
    "char[]",
    "int[]",
    "Map",
    "HashMap",
    "List",
    "ArrayList",
    "Vector",
    "Properties",
    "boolean",
    "Boolean",
    "int",
    "Integer",
    "long",
    "Long",
}

FRAMEWORK_TOKENS = {
    "Servlet",
    "HttpServletRequest",
    "HttpServletResponse",
    "JFrame",
    "JPanel",
    "Component",
    "Control",
    "Composite",
    "View",
    "Event",
    "Connection",
    "Statement",
    "ResultSet",
    "Session",
    "Context",
    "Request",
    "Response",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a probe-synthesis plan for T3/T7 compile-only no-probe cases.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--taxonomy-csv", type=Path, default=DEFAULT_TAXONOMY_CSV)
    parser.add_argument("--error-cases-jsonl", type=Path, default=DEFAULT_ERROR_CASES_JSONL)
    parser.add_argument("--error-rows", type=Path, default=DEFAULT_ERROR_ROWS)
    parser.add_argument("--error-cards", type=Path, default=DEFAULT_ERROR_CARDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    args = parser.parse_args()

    plan = build_probe_synthesis_plan(
        run_dir=args.run_dir,
        taxonomy_csv=args.taxonomy_csv,
        error_cases_jsonl=args.error_cases_jsonl,
        error_rows_csv=args.error_rows,
        error_cards_jsonl=args.error_cards,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_candidates(args.candidates, plan["candidates"])
    write_report(args.report, plan)
    print(
        json.dumps(
            {
                "status": plan["status"],
                "output": str(args.output.resolve()),
                "candidates": str(args.candidates.resolve()),
            },
            ensure_ascii=False,
        )
    )
    return 0 if plan["status"] in {"plan_ready", "no_candidates"} else 2


def build_probe_synthesis_plan(
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
    candidates: list[dict[str, Any]] = []
    for family, point_id in TARGET_FAMILIES.items():
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
            if trace_gap_bucket(item) != "probe_synthesis_needed":
                continue
            candidates.append(build_candidate(item=item, card=card or {}))

    summary = summarize_candidates(candidates)
    return {
        "schema_version": "eviclone-probe-synthesis-plan/v1",
        "status": plan_status(summary),
        "created_at_utc": now.isoformat(),
        "run_dir": str(run_dir.resolve()),
        "inputs": {
            "taxonomy_csv": input_state(taxonomy_csv),
            "error_cases_jsonl": input_state(error_cases_jsonl),
            "error_rows_csv": input_state(error_rows_csv),
            "error_cards_jsonl": input_state(error_cards_jsonl),
        },
        "summary": summary,
        "pain_points": summarize_by_pain_point(candidates),
        "probe_modes": summarize_by_key(candidates, "probe_mode"),
        "generation_routes": summarize_by_key(candidates, "generation_route"),
        "risk_tiers": summarize_by_key(candidates, "risk_tier"),
        "candidates": candidates,
        "interpretation": {
            "what_this_adds": (
                "The 860 T3/T7 compile-success/no-probe cases are converted into explicit probe contracts with "
                "generation routes and risk tiers."
            ),
            "execution_boundary": (
                "This artifact does not claim executed traces. It defines the next executable-trace work queue and "
                "the evidence contract each future probe must satisfy."
            ),
        },
    }


def build_candidate(*, item: dict[str, Any], card: dict[str, Any]) -> dict[str, Any]:
    llm = card.get("llm_evidence") if isinstance(card.get("llm_evidence"), dict) else {}
    local = card.get("local_evidence") if isinstance(card.get("local_evidence"), dict) else {}
    dyn = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    context = dyn.get("llm_context_completion") if isinstance(dyn.get("llm_context_completion"), dict) else {}
    payload = context.get("payload") if isinstance(context.get("payload"), dict) else {}
    meta = dyn.get("meta") if isinstance(dyn.get("meta"), dict) else {}
    method_a = meta.get("method_a") if isinstance(meta.get("method_a"), dict) else {}
    method_b = meta.get("method_b") if isinstance(meta.get("method_b"), dict) else {}
    shared_tests = llm.get("shared_test_intentions") if isinstance(llm.get("shared_test_intentions"), list) else []
    shared_features = list_of_strings(local.get("shared_feature_families"))
    observations = observation_texts(shared_tests)
    probe_mode = classify_probe_mode(shared_features, observations, method_a, method_b)
    arg_support = method_arg_support(method_a, method_b)
    risk_flags = context_risk_flags(payload)
    risk_tier, risk_reasons = classify_risk_tier(
        probe_mode=probe_mode,
        arg_support=arg_support,
        risk_flags=risk_flags,
        slice_alignment=item.get("slice_alignment"),
        method_a=method_a,
        method_b=method_b,
    )
    generation_route = generation_route_for(probe_mode=probe_mode, arg_support=arg_support, risk_tier=risk_tier)
    return {
        "case_id": item.get("case_id"),
        "pain_point": item.get("point_id"),
        "family": item.get("family"),
        "pair": item.get("pair"),
        "candidate_correct": item.get("candidate_correct"),
        "gate_override": item.get("gate_override"),
        "positive_slice_localized": item.get("positive_slice_localized"),
        "source_sink_signal": item.get("source_sink_signal"),
        "slice_alignment": item.get("slice_alignment"),
        "shared_features": shared_features,
        "expected_observations": observations,
        "method_a": method_summary(method_a),
        "method_b": method_summary(method_b),
        "probe_mode": probe_mode,
        "probe_contract": probe_contract(probe_mode),
        "generation_route": generation_route,
        "risk_tier": risk_tier,
        "risk_reasons": risk_reasons,
        "arg_support": arg_support,
        "context_completion": {
            "status": context.get("status"),
            "probe_strategy": payload.get("probe_strategy"),
            "risk_flags": risk_flags,
            "java_source_sha256": payload.get("java_source_sha256"),
        },
        "next_action": next_action_for(generation_route, probe_mode),
    }


def classify_probe_mode(
    shared_features: list[str],
    observations: list[str],
    method_a: dict[str, Any],
    method_b: dict[str, Any],
) -> str:
    text = " | ".join(observations).lower()
    features = set(shared_features)
    if "copy_file" in features or "file_effect" in text or "file" in text and "effect" in text:
        return "file_effect_probe"
    if "download_web" in features or "ftp" in features or "stream" in text or "http" in text or "url" in text:
        return "stream_or_http_probe"
    if "zip_decompress" in features or "zip" in text or "decompress" in text:
        return "archive_probe"
    if "exception" in text:
        return "exception_probe"
    if "state_change" in text or "state change" in text:
        return "state_change_probe"
    if "return_value" in text or both_return_values(method_a, method_b):
        return "return_value_probe"
    return "llm_probe_contract"


def method_arg_support(method_a: dict[str, Any], method_b: dict[str, Any]) -> dict[str, Any]:
    unsupported = []
    framework = []
    supported = []
    for side, method in (("a", method_a), ("b", method_b)):
        params = method.get("params") if isinstance(method.get("params"), list) else []
        for param in params:
            if not isinstance(param, dict):
                continue
            raw = str(param.get("type") or "")
            simple = simple_type(raw)
            entry = {"side": side, "type": raw, "simple_type": simple, "name": param.get("name")}
            if has_framework_token(raw):
                framework.append(entry)
            elif simple in SIMPLE_ARG_TYPES:
                supported.append(entry)
            else:
                unsupported.append(entry)
    return {
        "all_params_supported": not unsupported and not framework,
        "supported_params": supported,
        "unsupported_params": unsupported,
        "framework_params": framework,
    }


def classify_risk_tier(
    *,
    probe_mode: str,
    arg_support: dict[str, Any],
    risk_flags: list[str],
    slice_alignment: Any,
    method_a: dict[str, Any],
    method_b: dict[str, Any],
) -> tuple[str, list[str]]:
    reasons = []
    if probe_mode == "llm_probe_contract":
        reasons.append("no_specific_probe_mode")
    if arg_support.get("framework_params"):
        reasons.append("framework_or_ui_params")
    if arg_support.get("unsupported_params"):
        reasons.append("unsupported_param_types")
    if str(slice_alignment or "") in {"not_aligned", "unclear"}:
        reasons.append(f"slice_alignment={slice_alignment}")
    if any("stub" in flag.lower() or "framework" in flag.lower() for flag in risk_flags):
        reasons.append("stub_or_framework_context")
    if method_summary(method_a)["return_type"] == "void" and method_summary(method_b)["return_type"] == "void" and probe_mode == "return_value_probe":
        reasons.append("return_value_requested_for_void_methods")
    if not reasons and arg_support.get("all_params_supported") and probe_mode in {
        "file_effect_probe",
        "stream_or_http_probe",
        "archive_probe",
        "return_value_probe",
        "exception_probe",
    }:
        return "low", []
    if len(reasons) <= 2 and probe_mode != "llm_probe_contract":
        return "medium", reasons
    return "high", reasons


def generation_route_for(*, probe_mode: str, arg_support: dict[str, Any], risk_tier: str) -> str:
    if probe_mode == "llm_probe_contract":
        return "llm_probe_completion"
    if risk_tier == "low" and arg_support.get("all_params_supported"):
        return "deterministic_template"
    if risk_tier == "medium":
        return "deterministic_template_with_review"
    return "llm_probe_completion"


def probe_contract(probe_mode: str) -> dict[str, str]:
    contracts = {
        "file_effect_probe": {
            "input_setup": "Create paired temporary source/destination files or streams.",
            "observation": "Capture written bytes, returned file handles, or output stream contents.",
            "equivalence": "Compare normalized destination bytes and relevant return values.",
        },
        "stream_or_http_probe": {
            "input_setup": "Serve deterministic local HTTP/stream payloads; avoid external network.",
            "observation": "Capture returned text/bytes or response-side writes.",
            "equivalence": "Compare normalized stream contents or observable response state.",
        },
        "archive_probe": {
            "input_setup": "Create deterministic zip/archive inputs with nested entries.",
            "observation": "Capture extracted files or returned archive metadata.",
            "equivalence": "Compare extracted tree fingerprints.",
        },
        "return_value_probe": {
            "input_setup": "Build deterministic primitive, string, collection, or object inputs.",
            "observation": "Capture normalized return values.",
            "equivalence": "Compare normalized return values.",
        },
        "state_change_probe": {
            "input_setup": "Build deterministic receiver/mutable arguments with observable fields.",
            "observation": "Capture field, collection, file, or response state after invocation.",
            "equivalence": "Compare normalized post-state.",
        },
        "exception_probe": {
            "input_setup": "Build valid and boundary inputs.",
            "observation": "Capture exception class/message plus return state.",
            "equivalence": "Compare exception behavior and normalized outputs.",
        },
        "llm_probe_contract": {
            "input_setup": "Ask LLM to propose a conservative deterministic probe over existing completed context.",
            "observation": "Require EVICLONE_RESULT JSON with status, same, out_a, and out_b.",
            "equivalence": "Accept only if original snippet logic is preserved and execution is deterministic.",
        },
    }
    return contracts.get(probe_mode, contracts["llm_probe_contract"])


def summarize_candidates(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    mode_counts = Counter(str(item["probe_mode"]) for item in candidates)
    route_counts = Counter(str(item["generation_route"]) for item in candidates)
    risk_counts = Counter(str(item["risk_tier"]) for item in candidates)
    return {
        "candidate_count": len(candidates),
        "pain_point_counts": sorted_counter(Counter(str(item["pain_point"]) for item in candidates)),
        "probe_mode_counts": sorted_counter(mode_counts),
        "generation_route_counts": sorted_counter(route_counts),
        "risk_tier_counts": sorted_counter(risk_counts),
        "deterministic_template_candidates": route_counts.get("deterministic_template", 0),
        "deterministic_template_with_review_candidates": route_counts.get("deterministic_template_with_review", 0),
        "llm_probe_completion_candidates": route_counts.get("llm_probe_completion", 0),
        "low_risk_candidates": risk_counts.get("low", 0),
        "medium_risk_candidates": risk_counts.get("medium", 0),
        "high_risk_candidates": risk_counts.get("high", 0),
        "candidate_correct": sum(1 for item in candidates if item.get("candidate_correct")),
        "localized": sum(1 for item in candidates if item.get("positive_slice_localized") or item.get("source_sink_signal")),
        "top_probe_mode": most_common_key(mode_counts),
        "top_generation_route": most_common_key(route_counts),
    }


def summarize_by_pain_point(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for pain_point in sorted({str(item["pain_point"]) for item in candidates}):
        items = [item for item in candidates if str(item["pain_point"]) == pain_point]
        rows.append(
            {
                "id": pain_point,
                "candidate_count": len(items),
                "probe_mode_counts": sorted_counter(Counter(str(item["probe_mode"]) for item in items)),
                "generation_route_counts": sorted_counter(Counter(str(item["generation_route"]) for item in items)),
                "risk_tier_counts": sorted_counter(Counter(str(item["risk_tier"]) for item in items)),
                "candidate_correct": sum(1 for item in items if item.get("candidate_correct")),
                "localized": sum(1 for item in items if item.get("positive_slice_localized") or item.get("source_sink_signal")),
                "examples": [compact_candidate(item) for item in items[:5]],
            }
        )
    return rows


def summarize_by_key(candidates: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    rows = []
    for value in sorted({str(item[key]) for item in candidates}):
        items = [item for item in candidates if str(item[key]) == value]
        rows.append(
            {
                key: value,
                "count": len(items),
                "pain_point_counts": sorted_counter(Counter(str(item["pain_point"]) for item in items)),
                "candidate_correct": sum(1 for item in items if item.get("candidate_correct")),
                "risk_tier_counts": sorted_counter(Counter(str(item["risk_tier"]) for item in items)),
                "examples": [compact_candidate(item) for item in items[:5]],
            }
        )
    return rows


def plan_status(summary: dict[str, Any]) -> str:
    if summary["candidate_count"] == 0:
        return "no_candidates"
    if summary["probe_mode_counts"].get("llm_probe_contract", 0) == summary["candidate_count"]:
        return "plan_partial"
    return "plan_ready"


def next_action_for(route: str, mode: str) -> str:
    if route == "deterministic_template":
        return f"Generate and run the built-in {mode} template over the completed context."
    if route == "deterministic_template_with_review":
        return f"Generate the {mode} template, then require review because framework or alignment risk is present."
    return "Use configured LLM probe completion to create a custom deterministic EVICLONE_RESULT probe."


def compact_candidate(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": item["case_id"],
        "pair": item["pair"],
        "probe_mode": item["probe_mode"],
        "generation_route": item["generation_route"],
        "risk_tier": item["risk_tier"],
    }


def write_candidates(path: Path, candidates: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in candidates:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def write_report(path: Path, plan: dict[str, Any]) -> None:
    lines = [
        "# Probe Synthesis Plan",
        "",
        f"Status: `{plan['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| candidate_count | {plan['summary']['candidate_count']} |",
        f"| deterministic_template_candidates | {plan['summary']['deterministic_template_candidates']} |",
        f"| deterministic_template_with_review_candidates | {plan['summary']['deterministic_template_with_review_candidates']} |",
        f"| llm_probe_completion_candidates | {plan['summary']['llm_probe_completion_candidates']} |",
        f"| low_risk_candidates | {plan['summary']['low_risk_candidates']} |",
        f"| medium_risk_candidates | {plan['summary']['medium_risk_candidates']} |",
        f"| high_risk_candidates | {plan['summary']['high_risk_candidates']} |",
        f"| candidate_correct | {plan['summary']['candidate_correct']} |",
        f"| localized | {plan['summary']['localized']} |",
        "",
        "## Probe Modes",
        "",
        "| mode | count |",
        "| --- | ---: |",
    ]
    for mode, count in plan["summary"]["probe_mode_counts"].items():
        lines.append(f"| {mode} | {count} |")
    lines.extend(["", "## Generation Routes", "", "| route | count |", "| --- | ---: |"])
    for route, count in plan["summary"]["generation_route_counts"].items():
        lines.append(f"| {route} | {count} |")
    lines.extend(["", "## Pain Points", "", "| id | candidates | top mode | top route |", "| --- | ---: | --- | --- |"])
    for point in plan["pain_points"]:
        top_mode = most_common_key(Counter(point["probe_mode_counts"]))
        top_route = most_common_key(Counter(point["generation_route_counts"]))
        lines.append(f"| {point['id']} | {point['candidate_count']} | {top_mode} | {top_route} |")
    lines.extend(
        [
            "",
            "## Execution Boundary",
            "",
            plan["interpretation"]["execution_boundary"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def method_summary(method: dict[str, Any]) -> dict[str, Any]:
    params = method.get("params") if isinstance(method.get("params"), list) else []
    return {
        "name": method.get("name"),
        "return_type": method.get("return_type"),
        "param_count": len(params),
        "params": [
            {"type": param.get("type"), "name": param.get("name")}
            for param in params
            if isinstance(param, dict)
        ],
    }


def observation_texts(shared_tests: list[Any]) -> list[str]:
    result = []
    for item in shared_tests:
        if not isinstance(item, dict):
            continue
        text = " | ".join(
            str(item.get(field) or "")
            for field in ("expected_observation", "intent", "input_shape", "why_discriminative")
            if item.get(field) is not None
        ).strip()
        if text:
            result.append(text)
    return result


def context_risk_flags(payload: dict[str, Any]) -> list[str]:
    preservation = payload.get("semantic_preservation") if isinstance(payload.get("semantic_preservation"), dict) else {}
    return list_of_strings(preservation.get("risk_flags"))


def both_return_values(method_a: dict[str, Any], method_b: dict[str, Any]) -> bool:
    return str(method_a.get("return_type") or "void") != "void" and str(method_b.get("return_type") or "void") != "void"


def simple_type(type_name: str) -> str:
    text = type_name.replace("java.io.", "").replace("java.net.", "").replace("java.nio.file.", "")
    text = text.replace("final ", "").strip()
    if "<" in text:
        text = text.split("<", 1)[0]
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text.strip()


def has_framework_token(type_name: str) -> bool:
    return any(token in type_name for token in FRAMEWORK_TOKENS)


def list_of_strings(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def most_common_key(counter: Counter | dict[str, int]) -> str | None:
    if not counter:
        return None
    return sorted(dict(counter).items(), key=lambda item: (-int(item[1]), item[0]))[0][0]


if __name__ == "__main__":
    raise SystemExit(main())
