from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .config import DEFAULT_MODEL
from .context_completion import FORBIDDEN_CONTEXT_DECISION_KEYS
from .dynamic_router import (
    verify_base_model_passthrough_certificate,
    verify_learned_route_model_certificate,
    verify_learned_route_score_certificate,
    verify_route_decision_certificate,
)
from .executable_fusion import (
    EXECUTABLE_FUSION_CERTIFICATE_SCHEMA_VERSION,
    FUSION_DECISION_ACCOUNTING_SCHEMA_VERSION,
    build_fusion_trust_dependencies,
    build_fusion_decision_accounting,
    build_executable_fusion_certificate_hash,
    executable_dynamic_label as recompute_executable_dynamic_label,
    trusted_executable_evidence as recompute_trusted_executable_evidence,
    verify_context_payload_schema_certificate,
    verify_context_added_context_artifact,
    verify_context_probe_execution_path_artifact,
    verify_context_source_safety_artifact,
    verify_dynamic_outcome_for_trust,
    verify_executed_source_matches_artifact,
    verify_java_execution_sandbox_for_trust,
    verify_java_toolchain_for_trust,
    verify_probe_payload_schema_certificate,
    verify_probe_source_binding_artifact,
    verify_source_fingerprint_matches_card,
    verify_source_artifact,
)
from .executable_composition import (
    EXECUTABLE_COMPOSITION_HASH_FIELD,
    EXECUTABLE_COMPOSITION_SCHEMA_VERSION,
    verify_executable_composition_spec,
)
from .executable_modules import (
    EXECUTABLE_MODULE_GRAPH_HASH_FIELD,
    EXECUTABLE_MODULE_GRAPH_SCHEMA_VERSION,
    verify_executable_module_graph,
)
from .executor import (
    EXECUTION_RESULT_ORACLE_SCHEMA_VERSION,
    FRAMEWORK_MOCK_CONTRACT_HASH_FIELD,
    FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
    JAVA_EXECUTION_CERTIFICATE_SCHEMA_VERSION,
    MODULE_COMPOSITION_LOWERING_HASH_FIELD,
    MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION,
    PROBE_ADEQUACY_HASH_FIELD,
    PROBE_ADEQUACY_SCHEMA_VERSION,
    PROBE_CONTRACT_HASH_FIELD,
    PROBE_CONTRACT_SCHEMA_VERSION,
    RUNTIME_FIXTURE_HASH_FIELD,
    RUNTIME_FIXTURE_SPECS,
    RUNTIME_SOURCE_SAFETY_SCHEMA_VERSION,
    build_framework_mock_contract_hash,
    build_module_composition_lowering_hash,
    build_runtime_fixture_hash,
    build_probe_adequacy_certificate,
    build_probe_adequacy_certificate_hash,
    build_probe_contract_hash,
    count_probe_result_lines,
    parse_probe_output,
)
from .expert_invocation import (
    INVOCATION_HASH_FIELD,
    INPUT_FIREWALL_POLICY,
    INPUT_FIREWALL_HASH_FIELD,
    INPUT_FIREWALL_SCHEMA_VERSION,
    MODEL_CONFIG_SCHEMA_VERSION,
    MODULE_GRAPH_INPUT_BINDING_HASH_FIELD,
    MODULE_GRAPH_INPUT_BINDING_SCHEMA_VERSION,
    build_expert_invocation_hash,
    build_input_firewall_hash,
    build_module_graph_input_binding,
    find_forbidden_key_paths,
    normalize_key,
)
from .functional_blocks import (
    FUNCTIONAL_BLOCK_PAIR_HASH_FIELD,
    FUNCTIONAL_BLOCK_PAIR_SCHEMA_VERSION,
    verify_pair_functional_block_ir,
)
from .pipeline_trace import (
    ARCHITECTURE_CONTRACT_SCHEMA_VERSION,
    COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION,
    FINAL_DECISION_BINDING_SCHEMA_VERSION,
)
from .pipeline_trace import SCHEMA_VERSION as PIPELINE_TRACE_SCHEMA_VERSION
from .pipeline_trace import build_pipeline_contract, build_pipeline_trace
from .probe_synthesis import FORBIDDEN_PROBE_DECISION_KEYS
from .probe_planner import (
    MODULE_PROBE_PLAN_HASH_FIELD,
    MODULE_PROBE_PLAN_SCHEMA_VERSION,
    verify_module_probe_plan,
)


SCHEMA_VERSION = "eviclone-dynamic-evidence-contract-verification/v1"
FUSION_POLICY = "routed_executable_evidence_fusion/v1"
CONTEXT_EXPERT_CONTRACT = "context_completion_only_no_clone_judgment/v1"
PROBE_EXPERT_CONTRACT = "probe_body_only_no_clone_judgment/v1"

ROUTED_LLM_FORBIDDEN_KEYS = {
    "verdict",
    "pred_label",
    "prediction",
    "clone_label",
    "is_clone",
    "final_label",
    "final_decision",
    "semantic_verdict",
    "bcb_gold_verdict",
    "benchmark_label",
    "decision",
}

ROUTED_LEGACY_DECISION_ARTIFACTS = {
    "bcb_alignment": "BCB alignment can rewrite the final decision outside executable_fusion.",
    "annotation_preference": "Annotation preference can rewrite the final decision outside executable_fusion.",
    "llm_adjudication": "LLM adjudication can rewrite the final decision outside executable_fusion.",
}

ROUTED_LEGACY_OVERRIDE_RISK_FLAGS = {
    "bcb_alignment_override",
    "annotation_preference_override",
    "llm_adjudication_override",
}

ROUTED_ALLOWED_DYNAMIC_LLM_EXPERT_KEYS = {
    "llm_context_completion",
    "llm_probe_synthesis",
}

ROUTED_FORBIDDEN_DECISION_SOURCE_TOKENS = {
    "llm",
    "llm_judge",
    "llm_adjudication",
    "human",
    "manual",
    "bcb_alignment",
    "annotation_preference",
}


def verify_dynamic_evidence_contract(
    card: dict[str, Any],
    *,
    replay: bool = False,
    timeout_sec: float = 8.0,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    checks: Counter[str] = Counter()
    replay_result: dict[str, Any] | None = None

    route = as_dict(card.get("dynamic_route"))
    fusion = as_dict(card.get("executable_fusion"))
    dynamic = as_dict(card.get("dynamic_evidence"))
    decision = as_dict(card.get("decision"))
    base = base_prediction(card, route)
    base_label = coerce_binary_label(base.get("label"))
    decision_label = coerce_binary_label(decision.get("pred_label"))

    verify_card_source_fingerprint(card, issues=issues, checks=checks)

    if route:
        checks["routed_cards"] += 1
        verify_route_contract(
            card=card,
            route=route,
            fusion=fusion,
            dynamic=dynamic,
            base_label=base_label,
            decision_label=decision_label,
            issues=issues,
            checks=checks,
        )
        verify_base_prediction_consistency(card=card, route=route, issues=issues, checks=checks)
        verify_routed_llm_boundary(card, issues=issues, checks=checks)
        verify_routed_dynamic_llm_role_boundary(dynamic, issues=issues, checks=checks)
        verify_routed_legacy_decision_boundary(card, issues=issues, checks=checks)
        verify_routed_decision_provenance_boundary(
            card=card,
            route=route,
            fusion=fusion,
            issues=issues,
            checks=checks,
        )
        verify_pipeline_architecture_contract(card, issues=issues, checks=checks)
        verify_pipeline_trace_contract(card, issues=issues, checks=checks)

    if fusion:
        checks["fusion_cards"] += 1
        verify_fusion_contract(
            card=card,
            fusion=fusion,
            dynamic=dynamic,
            base_label=base_label,
            decision_label=decision_label,
            issues=issues,
            checks=checks,
        )

    verify_llm_expert_contracts(card, dynamic, issues=issues, checks=checks)
    verify_java_execution_certificate(dynamic, issues=issues, checks=checks)
    verify_functional_block_ir_binding(dynamic, issues=issues, checks=checks)
    verify_module_probe_plan_binding(dynamic, issues=issues, checks=checks)
    verify_executable_composition_binding(dynamic, issues=issues, checks=checks)
    verify_module_composition_lowering_binding(dynamic, issues=issues, checks=checks)
    verify_probe_contract(dynamic, issues=issues, checks=checks)
    verify_framework_mock_contracts(dynamic, issues=issues, checks=checks)

    if replay:
        artifact = replayable_source_artifact(dynamic)
        expected_same = parsed_same(dynamic)
        if artifact:
            replay_result = replay_source_artifact(artifact, expected_same=expected_same, timeout_sec=timeout_sec)
            checks[f"replay_{replay_result['status']}"] += 1
            if replay_result["status"] == "matched":
                checks["replay_same_matched"] += 1
            elif replay_result["status"] == "executed":
                add_issue(
                    issues,
                    "warning",
                    "replay_executed_without_expected_same",
                    "Retained source replay executed, but the original card has no boolean parsed.same to compare.",
                )
            else:
                add_issue(
                    issues,
                    "error",
                    f"replay_{replay_result['status']}",
                    replay_result.get("message") or "Retained source replay did not match the recorded evidence.",
                )
        else:
            replay_result = {"status": "skipped", "message": "No retained source_artifact is available for replay."}
            checks["replay_skipped"] += 1
            add_issue(
                issues,
                "warning",
                "replay_source_artifact_missing",
                "Replay was requested, but no retained source_artifact was available.",
            )

    issue_counts = issue_counts_for(issues)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "verified" if issue_counts.get("error", 0) == 0 else "issues_found",
        "checks": dict(checks),
        "issue_counts": issue_counts,
        "issues": issues,
        "replay": replay_result,
    }


def verify_dynamic_evidence_contracts(
    cards: list[dict[str, Any]],
    *,
    replay: bool = False,
    timeout_sec: float = 8.0,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    checks: Counter[str] = Counter()
    issues: list[dict[str, Any]] = []
    for index, card in enumerate(cards, start=1):
        result = verify_dynamic_evidence_contract(card, replay=replay, timeout_sec=timeout_sec)
        results.append({"index": index, "verification": result, "pair": compact_pair(card)})
        for key, value in result.get("checks", {}).items():
            checks[key] += int(value)
        for issue in result.get("issues", []):
            item = dict(issue)
            item.setdefault("card_index", index)
            item.setdefault("pair", compact_pair(card))
            issues.append(item)

    checks["cards"] = len(cards)
    checks["verified_cards"] = sum(1 for result in results if result["verification"]["status"] == "verified")
    checks["issue_cards"] = len(cards) - checks["verified_cards"]
    counts = issue_counts_for(issues)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "verified" if counts.get("error", 0) == 0 else "issues_found",
        "summary": dict(checks),
        "issue_counts": counts,
        "issues": issues,
        "cards": [compact_verification_result(result) for result in results],
        "examples": {
            "issues": issues[:20],
            "failed_cards": [result for result in results if result["verification"]["status"] != "verified"][:10],
        },
    }


def verify_cards(
    cards: list[dict[str, Any]],
    *,
    replay: bool = False,
    timeout_sec: float = 8.0,
) -> dict[str, Any]:
    return verify_dynamic_evidence_contracts(cards, replay=replay, timeout_sec=timeout_sec)


def verify_card_source_fingerprint(card: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    source_fingerprint = as_dict(card.get("source_fingerprint"))
    if not source_fingerprint:
        return
    checks["source_fingerprint_present"] += 1
    ok, reasons = verify_source_fingerprint_matches_card(card, source_fingerprint)
    if ok:
        checks["source_fingerprint_matches_card_identity"] += 1
        return
    checks["source_fingerprint_untrusted"] += 1
    for reason in reasons:
        add_issue(
            issues,
            "error",
            reason,
            "source_fingerprint does not match the evidence card pair_id/function_ids or its own certificate hash.",
        )


def verify_route_contract(
    *,
    card: dict[str, Any],
    route: dict[str, Any],
    fusion: dict[str, Any],
    dynamic: dict[str, Any],
    base_label: int | None,
    decision_label: int | None,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    route_certificate_ok, route_certificate_reasons = verify_route_decision_certificate(route)
    if route_certificate_ok:
        checks["dynamic_route_certificate_verified"] += 1
    elif isinstance(route.get("route_decision_certificate"), dict):
        checks["dynamic_route_certificate_unverified"] += 1
        add_issue(
            issues,
            "error",
            route_certificate_reasons[0] if route_certificate_reasons else "dynamic_route_certificate_untrusted",
            "dynamic_route route_decision_certificate failed verifier recomputation.",
        )
    else:
        checks["dynamic_route_certificate_missing"] += 1
        add_issue(
            issues,
            "warning",
            "dynamic_route_certificate_missing",
            "dynamic_route has no route_decision_certificate; route score/features are not bound to a replayable certificate.",
        )

    model_certificate = as_dict(route.get("route_model_certificate"))
    if str(route.get("policy") or "") == "learned_expected_dynamic_evidence_utility/v1":
        model_ok, model_reasons = verify_learned_route_model_certificate(model_certificate)
        if model_ok:
            checks["learned_route_model_certificate_verified"] += 1
            if model_certificate.get("threshold") != route.get("threshold"):
                add_issue(
                    issues,
                    "error",
                    "learned_route_model_certificate_threshold_mismatch",
                    "learned route model certificate threshold differs from dynamic_route.threshold.",
                )
        else:
            checks["learned_route_model_certificate_unverified"] += 1
            add_issue(
                issues,
                "error",
                model_reasons[0] if model_reasons else "learned_route_model_certificate_untrusted",
                "learned dynamic route model certificate failed verifier recomputation.",
            )
        score_ok, score_reasons = verify_learned_route_score_certificate(route)
        if score_ok:
            checks["learned_route_score_certificate_verified"] += 1
        else:
            checks["learned_route_score_certificate_unverified"] += 1
            add_issue(
                issues,
                "error",
                score_reasons[0] if score_reasons else "learned_route_score_certificate_untrusted",
                "learned dynamic route score certificate failed verifier recomputation.",
            )
    elif model_certificate:
        checks["unexpected_route_model_certificate"] += 1
        add_issue(
            issues,
            "error",
            "unexpected_route_model_certificate",
            "heuristic dynamic route carried a learned route model certificate.",
        )
    elif as_dict(route.get("route_score_certificate")):
        checks["unexpected_route_score_certificate"] += 1
        add_issue(
            issues,
            "error",
            "unexpected_route_score_certificate",
            "heuristic dynamic route carried a learned route score certificate.",
        )

    run_dynamic = route.get("run_dynamic")
    if run_dynamic is False:
        checks["route_passthrough_cards"] += 1
        if fusion:
            add_issue(issues, "error", "route_passthrough_has_executable_fusion", "A non-dynamic route produced executable_fusion.")
        if dynamic:
            add_issue(issues, "error", "route_passthrough_has_dynamic_evidence", "A non-dynamic route produced dynamic_evidence.")
        passthrough = as_dict(card.get("base_model_passthrough"))
        if passthrough:
            passthrough_ok, passthrough_reasons = verify_base_model_passthrough_certificate(card)
            if passthrough_ok:
                checks["base_model_passthrough_certificate_verified"] += 1
            else:
                checks["base_model_passthrough_certificate_unverified"] += 1
                add_issue(
                    issues,
                    "error",
                    passthrough_reasons[0] if passthrough_reasons else "base_model_passthrough_certificate_untrusted",
                    "base_model_passthrough certificate failed verifier recomputation.",
                )
        else:
            checks["base_model_passthrough_certificate_missing"] += 1
            add_issue(
                issues,
                "warning",
                "base_model_passthrough_certificate_missing",
                "A non-dynamic route has no base_model_passthrough certificate binding the final label to the base prediction.",
            )
        if base_label in (0, 1) and decision_label != base_label:
            add_issue(
                issues,
                "error",
                "route_passthrough_decision_differs_from_base",
                f"Passthrough decision pred_label={decision_label} differs from base label={base_label}.",
            )
    elif run_dynamic is True:
        checks["route_dynamic_cards"] += 1
        if not fusion:
            add_issue(issues, "error", "route_dynamic_missing_executable_fusion", "A dynamic route has no executable_fusion certificate.")
    else:
        add_issue(issues, "error", "dynamic_route_run_dynamic_missing", "dynamic_route.run_dynamic is missing or non-boolean.")

    route_base = base_prediction(card, route)
    if base_label is None and route_base:
        add_issue(issues, "warning", "base_prediction_label_unusable", "Base prediction exists but has no binary label.")


def verify_base_prediction_consistency(
    *,
    card: dict[str, Any],
    route: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    card_base = as_dict(card.get("base_model_prediction"))
    route_base = as_dict(route.get("base_prediction"))
    if not card_base and not route_base:
        checks["base_prediction_missing"] += 1
        add_issue(
            issues,
            "warning",
            "base_prediction_missing",
            "routed card has no base_model_prediction or dynamic_route.base_prediction; pass-through and fusion cannot be tied to a concrete base model output.",
        )
        return
    if not card_base or not route_base:
        checks["base_prediction_single_source"] += 1
        return
    checks["base_prediction_dual_source"] += 1
    card_label = coerce_binary_label(card_base.get("label"))
    route_label = coerce_binary_label(route_base.get("label"))
    if card_label != route_label:
        add_issue(
            issues,
            "error",
            "base_prediction_label_mismatch",
            f"base_model_prediction.label={card_label!r} differs from dynamic_route.base_prediction.label={route_label!r}.",
        )
    for key in ["source", "confidence", "margin"]:
        if key in card_base and key in route_base and card_base.get(key) != route_base.get(key):
            add_issue(
                issues,
                "error",
                f"base_prediction_{key}_mismatch",
                f"base_model_prediction.{key} differs from dynamic_route.base_prediction.{key}.",
            )


def verify_routed_llm_boundary(card: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    llm = card.get("llm_evidence")
    if llm in (None, {}):
        checks["routed_cards_without_llm_final_evidence"] += 1
        return
    if not isinstance(llm, dict):
        add_issue(issues, "error", "routed_card_llm_evidence_non_object", "routed card has non-object llm_evidence.")
        return
    forbidden = sorted(item["path"] for item in find_forbidden_key_paths(llm, ROUTED_LLM_FORBIDDEN_KEYS))
    if forbidden:
        add_issue(
            issues,
            "error",
            "routed_card_has_llm_final_decision",
            f"routed card contains forbidden final-decision LLM fields: {', '.join(forbidden)}.",
        )
        return
    status = str(llm.get("status") or "").strip().lower()
    if status and status != "failed":
        add_issue(
            issues,
            "warning",
            "routed_card_has_legacy_llm_evidence",
            f"routed card has llm_evidence status={status}; routed mode should rely on executable_fusion instead.",
        )


def verify_routed_dynamic_llm_role_boundary(
    dynamic: dict[str, Any],
    *,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    if not dynamic:
        return
    unauthorized = [
        str(key)
        for key in dynamic
        if normalize_key(str(key)).startswith("llm_")
        and normalize_key(str(key)) not in ROUTED_ALLOWED_DYNAMIC_LLM_EXPERT_KEYS
    ]
    if not unauthorized:
        checks["routed_dynamic_llm_roles_authorized"] += 1
        return
    checks["routed_dynamic_unauthorized_llm_artifacts"] += len(unauthorized)
    nested_forbidden: list[str] = []
    for key in unauthorized:
        value = dynamic.get(key)
        for item in find_forbidden_key_paths(value, ROUTED_LLM_FORBIDDEN_KEYS):
            nested_forbidden.append(f"{key}.{item['path']}")
    detail = "; forbidden decision fields: " + ", ".join(sorted(nested_forbidden)) if nested_forbidden else ""
    add_issue(
        issues,
        "error",
        "routed_dynamic_has_unauthorized_llm_artifact",
        (
            "routed dynamic_evidence may only contain bounded LLM expert roles "
            f"{sorted(ROUTED_ALLOWED_DYNAMIC_LLM_EXPERT_KEYS)}; found {sorted(unauthorized)}{detail}."
        ),
    )


def verify_routed_legacy_decision_boundary(
    card: dict[str, Any],
    *,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    present = [
        key
        for key in sorted(ROUTED_LEGACY_DECISION_ARTIFACTS)
        if isinstance(card.get(key), dict) and card.get(key)
    ]
    if present:
        checks["routed_legacy_decision_artifacts_present"] += len(present)
        add_issue(
            issues,
            "error",
            "routed_card_has_legacy_decision_artifact",
            (
                "routed cards must not carry legacy final-decision override artifacts outside executable_fusion: "
                + ", ".join(f"{key} ({ROUTED_LEGACY_DECISION_ARTIFACTS[key]})" for key in present)
            ),
        )
    decision = as_dict(card.get("decision"))
    risk_flags = {str(flag) for flag in decision.get("risk_flags") or []}
    legacy_flags = sorted(risk_flags & ROUTED_LEGACY_OVERRIDE_RISK_FLAGS)
    if legacy_flags:
        checks["routed_legacy_override_risk_flags"] += len(legacy_flags)
        add_issue(
            issues,
            "error",
            "routed_card_has_legacy_override_risk_flag",
            "routed decision risk_flags indicate a legacy non-executable override: " + ", ".join(legacy_flags),
        )


def verify_routed_decision_provenance_boundary(
    *,
    card: dict[str, Any],
    route: dict[str, Any],
    fusion: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    decision = as_dict(card.get("decision"))
    if not decision:
        return
    checks["routed_decision_provenance_checked"] += 1
    expected_owner = "base_model_passthrough" if route.get("run_dynamic") is False else "executable_fusion"
    expected_final_source = (
        "base_model_passthrough"
        if route.get("run_dynamic") is False
        else str(fusion.get("final_source") or "")
        if fusion
        else ""
    )

    if decision.get("decision_owner") is not None and str(decision.get("decision_owner")) != expected_owner:
        add_issue(
            issues,
            "error",
            "routed_decision_owner_mismatch",
            f"decision.decision_owner={decision.get('decision_owner')!r} expected {expected_owner!r}.",
        )
    if expected_final_source and decision.get("final_source") is not None and str(decision.get("final_source")) != expected_final_source:
        add_issue(
            issues,
            "error",
            "routed_decision_final_source_mismatch",
            f"decision.final_source={decision.get('final_source')!r} expected {expected_final_source!r}.",
        )

    suspicious_sources = routed_decision_nonprogrammatic_source_paths(decision)
    if suspicious_sources:
        checks["routed_decision_nonprogrammatic_source_fields"] += len(suspicious_sources)
        add_issue(
            issues,
            "error",
            "routed_decision_has_nonprogrammatic_source",
            "routed final decision provenance points to non-programmatic decision source: "
            + ", ".join(suspicious_sources),
        )


def routed_decision_nonprogrammatic_source_paths(decision: dict[str, Any]) -> list[str]:
    source_fields = {"source", "decision_source", "provenance"}
    findings: list[str] = []
    for key in sorted(source_fields):
        if key not in decision:
            continue
        for path, value in string_leaves(decision.get(key), prefix=key):
            normalized = normalize_key(value)
            if any(token in normalized for token in ROUTED_FORBIDDEN_DECISION_SOURCE_TOKENS):
                findings.append(f"{path}={value!r}")
    return findings


def verify_pipeline_trace_contract(card: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    trace = as_dict(card.get("pipeline_trace"))
    if not trace:
        checks["pipeline_trace_missing"] += 1
        add_issue(
            issues,
            "warning",
            "pipeline_trace_missing",
            "routed card has no pipeline_trace certificate; stage-level route/executor/expert/fusion flow is unaudited.",
        )
        return
    checks["pipeline_trace_present"] += 1
    expected = build_pipeline_trace(card)
    if trace.get("schema_version") != PIPELINE_TRACE_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "pipeline_trace_schema_mismatch",
            f"pipeline_trace.schema_version={trace.get('schema_version')!r} expected {PIPELINE_TRACE_SCHEMA_VERSION}.",
        )
    if trace.get("pipeline") != expected.get("pipeline"):
        add_issue(
            issues,
            "error",
            "pipeline_trace_pipeline_mismatch",
            f"pipeline_trace.pipeline={trace.get('pipeline')!r} expected {expected.get('pipeline')!r}.",
        )
    if trace.get("dataflow_edges") != expected.get("dataflow_edges"):
        add_issue(
            issues,
            "error",
            "pipeline_trace_dataflow_edges_mismatch",
            "pipeline_trace.dataflow_edges do not match verifier-recomputed component dataflow.",
        )
    verify_pipeline_trace_component_interaction_summary(
        actual=as_dict(trace.get("component_interaction_summary")),
        expected=as_dict(expected.get("component_interaction_summary")),
        route=as_dict(card.get("dynamic_route")),
        issues=issues,
        checks=checks,
    )
    trace_stage_ids = [str(stage.get("id") or "") for stage in trace.get("stages") or [] if isinstance(stage, dict)]
    expected_stage_ids = [str(stage.get("id") or "") for stage in expected.get("stages") or [] if isinstance(stage, dict)]
    if trace_stage_ids != expected_stage_ids:
        add_issue(
            issues,
            "error",
            "pipeline_trace_stage_sequence_mismatch",
            f"pipeline_trace stages={trace_stage_ids!r} expected {expected_stage_ids!r}.",
        )
    if trace.get("trace_sha256") != expected.get("trace_sha256"):
        add_issue(
            issues,
            "error",
            "pipeline_trace_sha_mismatch",
            "pipeline_trace.trace_sha256 does not match the verifier-recomputed stage trace.",
        )
    if trace.get("llm_final_decision_allowed") is not False:
        add_issue(
            issues,
            "error",
            "pipeline_trace_allows_llm_final_decision",
            "routed pipeline trace must record llm_final_decision_allowed=false.",
        )


def verify_pipeline_trace_component_interaction_summary(
    *,
    actual: dict[str, Any],
    expected: dict[str, Any],
    route: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    if not actual:
        checks["pipeline_trace_component_interaction_summary_missing"] += 1
        add_issue(
            issues,
            "error",
            "pipeline_trace_component_interaction_summary_missing",
            "pipeline_trace has no component_interaction_summary binding execution trace to component permissions.",
        )
        return
    checks["pipeline_trace_component_interaction_summary_present"] += 1
    expected_actual_sha = canonical_sha256({key: value for key, value in actual.items() if key != "summary_sha256"})
    if actual.get("summary_sha256") != expected_actual_sha:
        add_issue(
            issues,
            "error",
            "pipeline_trace_component_interaction_summary_sha_mismatch",
            "pipeline_trace component_interaction_summary.summary_sha256 does not match its own payload.",
        )
    if actual != expected:
        add_issue(
            issues,
            "error",
            "pipeline_trace_component_interaction_summary_mismatch",
            "pipeline_trace component_interaction_summary differs from verifier-recomputed component permissions summary.",
        )
    if route:
        if actual.get("llm_final_decision_output_allowed") is not False:
            add_issue(
                issues,
                "error",
                "pipeline_trace_component_interaction_summary_allows_llm_final_decision",
                "routed pipeline_trace summary must record llm_final_decision_output_allowed=false.",
            )
        if actual.get("llm_clone_label_output_allowed") is not False:
            add_issue(
                issues,
                "error",
                "pipeline_trace_component_interaction_summary_allows_llm_clone_label",
                "routed pipeline_trace summary must record llm_clone_label_output_allowed=false.",
            )


def verify_pipeline_architecture_contract(card: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    contract = as_dict(card.get("pipeline_contract"))
    if not contract:
        checks["pipeline_contract_missing"] += 1
        add_issue(
            issues,
            "warning",
            "pipeline_contract_missing",
            "routed card has no pipeline_contract; architecture-level role and decision-owner constraints are unaudited.",
        )
        return
    checks["pipeline_contract_present"] += 1
    expected = build_pipeline_contract(card)
    if contract.get("schema_version") != ARCHITECTURE_CONTRACT_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "pipeline_contract_schema_mismatch",
            f"pipeline_contract.schema_version={contract.get('schema_version')!r} expected {ARCHITECTURE_CONTRACT_SCHEMA_VERSION}.",
        )
    for key in [
        "policy",
        "routed",
        "dynamic_execution_required",
        "programmatic_fusion_required",
        "llm_role",
        "llm_final_decision_allowed",
        "legacy_llm_judge_allowed",
        "final_decision_owner",
        "route_policy",
        "fusion_policy",
        "base_passthrough_required",
    ]:
        if contract.get(key) != expected.get(key):
            add_issue(
                issues,
                "error",
                f"pipeline_contract_{key}_mismatch",
                f"pipeline_contract.{key}={contract.get(key)!r} expected {expected.get(key)!r}.",
            )
    if contract.get("allowed_llm_expert_roles") != expected.get("allowed_llm_expert_roles"):
        add_issue(
            issues,
            "error",
            "pipeline_contract_allowed_llm_expert_roles_mismatch",
            "pipeline_contract allowed LLM expert roles do not match the routed architecture.",
        )
    if contract.get("allowed_final_sources") != expected.get("allowed_final_sources"):
        add_issue(
            issues,
            "error",
            "pipeline_contract_allowed_final_sources_mismatch",
            "pipeline_contract allowed final decision sources do not match the routed architecture.",
        )
    if contract.get("deployable_final_sources") != expected.get("deployable_final_sources"):
        add_issue(
            issues,
            "error",
            "pipeline_contract_deployable_final_sources_mismatch",
            "pipeline_contract deployable final decision sources do not match the deployment architecture.",
        )
    verify_pipeline_final_decision_binding(
        actual=as_dict(contract.get("final_decision_binding")),
        expected=as_dict(expected.get("final_decision_binding")),
        issues=issues,
        checks=checks,
    )
    if contract.get("component_dataflow") != expected.get("component_dataflow"):
        add_issue(
            issues,
            "error",
            "pipeline_contract_component_dataflow_mismatch",
            "pipeline_contract component_dataflow does not match verifier-recomputed component dataflow.",
        )
    verify_component_interaction_contract(
        actual=as_dict(contract.get("component_interaction_contract")),
        expected=as_dict(expected.get("component_interaction_contract")),
        route=as_dict(card.get("dynamic_route")),
        issues=issues,
        checks=checks,
    )
    if contract.get("contract_sha256") != expected.get("contract_sha256"):
        add_issue(
            issues,
            "error",
            "pipeline_contract_sha_mismatch",
            "pipeline_contract.contract_sha256 does not match the verifier-recomputed architecture contract.",
        )
    if contract.get("llm_final_decision_allowed") is not False:
        add_issue(
            issues,
            "error",
            "pipeline_contract_allows_llm_final_decision",
            "routed pipeline contract must record llm_final_decision_allowed=false.",
        )
    if contract.get("legacy_llm_judge_allowed") is not False:
        add_issue(
            issues,
            "error",
            "pipeline_contract_allows_legacy_llm_judge",
            "routed pipeline contract must record legacy_llm_judge_allowed=false.",
        )
    if expected.get("final_decision_owner") == "missing_executable_fusion":
        add_issue(
            issues,
            "error",
            "pipeline_contract_missing_required_executable_fusion",
            "routed dynamic branch must end in executable_fusion.",
        )


def verify_component_interaction_contract(
    *,
    actual: dict[str, Any],
    expected: dict[str, Any],
    route: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    if not actual:
        checks["component_interaction_contract_missing"] += 1
        add_issue(
            issues,
            "error",
            "component_interaction_contract_missing",
            "pipeline_contract has no component_interaction_contract permission table.",
        )
        return
    checks["component_interaction_contract_present"] += 1
    if actual.get("schema_version") != COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "component_interaction_contract_schema_mismatch",
            (
                "component_interaction_contract.schema_version="
                f"{actual.get('schema_version')!r} expected {COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION}."
            ),
        )
    expected_actual_sha = canonical_sha256(
        {key: value for key, value in actual.items() if key != "interaction_contract_sha256"}
    )
    if actual.get("interaction_contract_sha256") != expected_actual_sha:
        add_issue(
            issues,
            "error",
            "component_interaction_contract_sha_mismatch",
            "component_interaction_contract.interaction_contract_sha256 does not match its own payload.",
        )
    if actual != expected:
        add_issue(
            issues,
            "error",
            "component_interaction_contract_recomputed_mismatch",
            "pipeline_contract component_interaction_contract differs from verifier-recomputed component permissions.",
        )
    if route:
        if actual.get("llm_clone_label_output_allowed") is not False:
            add_issue(
                issues,
                "error",
                "component_interaction_contract_allows_llm_clone_label",
                "routed component_interaction_contract must record llm_clone_label_output_allowed=false.",
            )
        if actual.get("llm_final_decision_output_allowed") is not False:
            add_issue(
                issues,
                "error",
                "component_interaction_contract_allows_llm_final_decision",
                "routed component_interaction_contract must record llm_final_decision_output_allowed=false.",
            )
        final_decision_components = actual.get("final_decision_components")
        expected_final_components = ["base_model_passthrough"] if route.get("run_dynamic") is False else ["executable_fusion"]
        if final_decision_components != expected_final_components:
            add_issue(
                issues,
                "error",
                "component_interaction_contract_final_decision_components_mismatch",
                f"final_decision_components={final_decision_components!r} expected {expected_final_components!r}.",
            )
        bounded_expert_components = actual.get("bounded_expert_components")
        expected_bounded_components = [] if route.get("run_dynamic") is False else [
            "llm_context_completion",
            "llm_probe_synthesis",
        ]
        if bounded_expert_components != expected_bounded_components:
            add_issue(
                issues,
                "error",
                "component_interaction_contract_bounded_expert_components_mismatch",
                f"bounded_expert_components={bounded_expert_components!r} expected {expected_bounded_components!r}.",
            )
        allowed_bounded = set(expected_bounded_components)
        unauthorized_bounded = [
            str(component.get("component"))
            for component in actual.get("components") or []
            if isinstance(component, dict)
            and component.get("may_emit_bounded_expert_artifact") is True
            and str(component.get("component") or "") not in allowed_bounded
        ]
        if unauthorized_bounded:
            add_issue(
                issues,
                "error",
                "component_interaction_contract_unauthorized_bounded_expert_artifact_component",
                "Only bounded LLM expert tools may emit bounded expert artifacts: "
                + ", ".join(sorted(unauthorized_bounded)),
            )
        unauthorized_llm_final = [
            str(component.get("component"))
            for component in actual.get("components") or []
            if isinstance(component, dict)
            and str(component.get("component") or "").startswith("llm_")
            and component.get("may_emit_final_decision") is not False
        ]
        if unauthorized_llm_final:
            add_issue(
                issues,
                "error",
                "component_interaction_contract_llm_component_can_emit_final_decision",
                "LLM expert components must not be permitted to emit final decisions: "
                + ", ".join(sorted(unauthorized_llm_final)),
            )


def verify_pipeline_final_decision_binding(
    *,
    actual: dict[str, Any],
    expected: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    if not actual:
        checks["pipeline_final_decision_binding_missing"] += 1
        add_issue(
            issues,
            "error",
            "pipeline_final_decision_binding_missing",
            "pipeline_contract has no final_decision_binding certificate.",
        )
        return
    checks["pipeline_final_decision_binding_present"] += 1
    if actual.get("schema_version") != FINAL_DECISION_BINDING_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "pipeline_final_decision_binding_schema_mismatch",
            f"final_decision_binding.schema_version={actual.get('schema_version')!r} expected {FINAL_DECISION_BINDING_SCHEMA_VERSION}.",
        )
    expected_actual_sha = canonical_sha256({key: value for key, value in actual.items() if key != "binding_sha256"})
    if actual.get("binding_sha256") != expected_actual_sha:
        add_issue(
            issues,
            "error",
            "pipeline_final_decision_binding_sha_mismatch",
            "final_decision_binding.binding_sha256 does not match its own payload.",
        )
    if actual != expected:
        add_issue(
            issues,
            "error",
            "pipeline_final_decision_binding_recomputed_mismatch",
            "pipeline_contract final_decision_binding differs from verifier-recomputed final decision binding.",
        )


def verify_fusion_contract(
    *,
    card: dict[str, Any],
    fusion: dict[str, Any],
    dynamic: dict[str, Any],
    base_label: int | None,
    decision_label: int | None,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    checks["executable_fusion_certificate_present"] += 1
    if fusion.get("schema_version") != EXECUTABLE_FUSION_CERTIFICATE_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "executable_fusion_schema_mismatch",
            f"executable_fusion.schema_version={fusion.get('schema_version')!r} expected {EXECUTABLE_FUSION_CERTIFICATE_SCHEMA_VERSION}.",
        )
    expected_fusion_sha = build_executable_fusion_certificate_hash(fusion)
    if fusion.get("fusion_sha256") != expected_fusion_sha:
        add_issue(
            issues,
            "error",
            "executable_fusion_sha_mismatch",
            "executable_fusion.fusion_sha256 does not match the verifier-recomputed fusion certificate payload.",
        )

    if fusion.get("policy") != FUSION_POLICY:
        add_issue(
            issues,
            "error",
            "executable_fusion_policy_mismatch",
            f"executable_fusion.policy={fusion.get('policy')!r} expected {FUSION_POLICY}.",
        )

    final_label = coerce_binary_label(fusion.get("final_label"))
    dynamic_label = coerce_binary_label(fusion.get("dynamic_label"))
    fusion_base_label = coerce_binary_label(fusion.get("base_label"))
    final_source = str(fusion.get("final_source") or "")
    dynamic_trusted = fusion.get("dynamic_trusted") is True
    parsed_label = executable_dynamic_label(dynamic)
    recomputed_dynamic_label = recompute_executable_dynamic_label(dynamic)
    source_fingerprint = as_dict(card.get("source_fingerprint"))
    source_fingerprint_ok, source_fingerprint_reasons = verify_source_fingerprint_matches_card(
        card,
        source_fingerprint or None,
    )
    recomputed_trusted, recomputed_trust_reasons = recompute_trusted_executable_evidence(
        dynamic,
        source_fingerprint=source_fingerprint or None,
    )
    if not source_fingerprint_ok:
        recomputed_trusted = False
        recomputed_trust_reasons = source_fingerprint_reasons
    checks["fusion_trust_recomputed"] += 1

    if dynamic_label != recomputed_dynamic_label:
        add_issue(
            issues,
            "error",
            "fusion_dynamic_label_differs_from_recomputed_executable_label",
            f"fusion dynamic_label={dynamic_label} differs from recomputed executable label={recomputed_dynamic_label}.",
        )
    if dynamic_trusted != recomputed_trusted:
        add_issue(
            issues,
            "error",
            "fusion_dynamic_trusted_differs_from_recomputed_trust",
            (
                f"fusion dynamic_trusted={dynamic_trusted} differs from recomputed trust={recomputed_trusted}; "
                f"reasons={'; '.join(recomputed_trust_reasons)}"
            ),
        )
    verify_fusion_trust_dependencies(
        fusion=fusion,
        dynamic=dynamic,
        source_fingerprint=source_fingerprint or None,
        issues=issues,
        checks=checks,
    )
    verify_fusion_decision_accounting(
        fusion=fusion,
        issues=issues,
        checks=checks,
    )

    if base_label in (0, 1) and fusion_base_label != base_label:
        add_issue(
            issues,
            "error",
            "fusion_base_label_differs_from_base_prediction",
            f"fusion base_label={fusion_base_label!r} differs from routed base prediction label={base_label!r}.",
        )
    if base_label is None and fusion_base_label in (0, 1):
        add_issue(
            issues,
            "error",
            "fusion_base_label_without_base_prediction",
            "fusion records a binary base_label but the routed card has no usable base prediction.",
        )

    if final_label in (0, 1) and decision_label != final_label:
        add_issue(
            issues,
            "error",
            "fusion_final_label_differs_from_decision",
            f"fusion final_label={final_label} differs from decision pred_label={decision_label}.",
        )

    if dynamic_trusted:
        checks["fusion_dynamic_trusted"] += 1
        if dynamic.get("status") != "executed":
            add_issue(
                issues,
                "error",
                "trusted_fusion_dynamic_status_not_executed",
                f"dynamic_trusted=true but dynamic_evidence.status={dynamic.get('status')!r}.",
            )
        if parsed_same(dynamic) not in (True, False):
            add_issue(issues, "error", "trusted_fusion_missing_boolean_same", "dynamic_trusted=true but parsed.same is not boolean.")
        if parsed_label in (0, 1) and dynamic_label != parsed_label:
            add_issue(
                issues,
                "error",
                "fusion_dynamic_label_differs_from_parsed_execution",
                f"fusion dynamic_label={dynamic_label} differs from parsed dynamic label={parsed_label}.",
            )
    else:
        checks["fusion_dynamic_untrusted"] += 1

    if final_source == "trusted_executable_override":
        require_trusted_dynamic(final_source, dynamic_trusted, issues)
        if fusion_base_label not in (0, 1) or dynamic_label not in (0, 1) or fusion_base_label == dynamic_label:
            add_issue(issues, "error", "trusted_override_requires_base_dynamic_disagreement", "trusted override requires binary base/dynamic labels that disagree.")
        if final_label != dynamic_label:
            add_issue(issues, "error", "trusted_override_final_label_not_dynamic", "trusted override final_label must equal dynamic_label.")
    elif final_source == "trusted_executable_confirmation":
        require_trusted_dynamic(final_source, dynamic_trusted, issues)
        if fusion_base_label not in (0, 1) or dynamic_label not in (0, 1) or fusion_base_label != dynamic_label:
            add_issue(issues, "error", "trusted_confirmation_requires_base_dynamic_agreement", "trusted confirmation requires binary base/dynamic labels that agree.")
        if final_label != dynamic_label:
            add_issue(issues, "error", "trusted_confirmation_final_label_not_dynamic", "trusted confirmation final_label must equal dynamic_label.")
    elif final_source == "trusted_executable_without_base_prediction":
        require_trusted_dynamic(final_source, dynamic_trusted, issues)
        if fusion_base_label is not None:
            add_issue(issues, "error", "trusted_without_base_has_base_label", "trusted executable without base prediction recorded a base label.")
        if final_label != dynamic_label:
            add_issue(issues, "error", "trusted_without_base_final_label_not_dynamic", "final_label must equal dynamic_label when no base label is available.")
    elif final_source == "base_model_passthrough_after_untrusted_dynamic":
        if dynamic_trusted:
            add_issue(issues, "error", "base_passthrough_marked_dynamic_trusted", "base passthrough after dynamic evidence must have dynamic_trusted=false.")
        if fusion_base_label in (0, 1) and final_label != fusion_base_label:
            add_issue(issues, "error", "base_passthrough_final_label_not_base", "base passthrough final_label must equal base_label.")
    elif final_source == "no_reliable_final_label":
        if final_label is not None:
            add_issue(issues, "error", "no_reliable_final_label_has_binary_label", "no_reliable_final_label must not record a binary final_label.")
    else:
        add_issue(issues, "error", "unknown_executable_fusion_final_source", f"Unknown executable_fusion.final_source={final_source!r}.")


def verify_fusion_trust_dependencies(
    *,
    fusion: dict[str, Any],
    dynamic: dict[str, Any],
    source_fingerprint: dict[str, Any] | None = None,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    dependencies = as_dict(fusion.get("trust_dependencies"))
    if not dependencies:
        checks["fusion_trust_dependencies_missing"] += 1
        add_issue(
            issues,
            "warning",
            "fusion_trust_dependencies_missing",
            "executable_fusion has no trust_dependencies certificate; fusion trust inputs are unaudited.",
        )
        return
    checks["fusion_trust_dependencies_present"] += 1
    expected = build_fusion_trust_dependencies(dynamic, source_fingerprint=source_fingerprint)
    if dependencies.get("schema_version") != "eviclone-fusion-trust-dependencies/v1":
        add_issue(
            issues,
            "error",
            "fusion_trust_dependencies_schema_mismatch",
            "fusion trust_dependencies schema_version is invalid.",
        )
    if dependencies.get("trust_policy") != expected.get("trust_policy"):
        add_issue(
            issues,
            "error",
            "fusion_trust_dependencies_policy_mismatch",
            "fusion trust_dependencies trust_policy does not match the verifier policy.",
        )
    actual_dependencies_sha = canonical_sha256(
        {key: value for key, value in dependencies.items() if key != "dependencies_sha256"}
    )
    if dependencies.get("dependencies_sha256") != actual_dependencies_sha:
        add_issue(
            issues,
            "error",
            "fusion_trust_dependencies_sha_mismatch",
            "fusion trust_dependencies hash does not match its own payload.",
        )
    if dependencies.get("dependencies_sha256") != expected.get("dependencies_sha256"):
        add_issue(
            issues,
            "error",
            "fusion_trust_dependencies_recomputed_sha_mismatch",
            "fusion trust_dependencies hash differs from verifier-recomputed dependencies.",
        )
    for key in [
        "dynamic_status",
        "dynamic_label",
        "parsed",
        "case_summary",
        "compile",
        "execution",
        "java_execution_certificate",
        "llm_context_completion",
        "llm_probe_synthesis",
        "source_fingerprint",
    ]:
        if dependencies.get(key) != expected.get(key):
            add_issue(
                issues,
                "error",
                f"fusion_trust_dependencies_{key}_mismatch",
                f"fusion trust_dependencies.{key} differs from verifier-recomputed value.",
            )


def verify_fusion_decision_accounting(
    *,
    fusion: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    accounting = as_dict(fusion.get("decision_accounting"))
    if not accounting:
        checks["fusion_decision_accounting_missing"] += 1
        add_issue(
            issues,
            "error",
            "fusion_decision_accounting_missing",
            "executable_fusion has no decision_accounting certificate.",
        )
        return
    checks["fusion_decision_accounting_present"] += 1
    expected = build_fusion_decision_accounting(
        final_label=coerce_binary_label(fusion.get("final_label")),
        final_source=str(fusion.get("final_source") or ""),
        dynamic_label=coerce_binary_label(fusion.get("dynamic_label")),
        dynamic_trusted=fusion.get("dynamic_trusted") is True,
        base_label=coerce_binary_label(fusion.get("base_label")),
    )
    if accounting.get("schema_version") != FUSION_DECISION_ACCOUNTING_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "fusion_decision_accounting_schema_mismatch",
            "fusion decision_accounting schema_version is invalid.",
        )
    actual_sha = canonical_sha256({key: value for key, value in accounting.items() if key != "accounting_sha256"})
    if accounting.get("accounting_sha256") != actual_sha:
        add_issue(
            issues,
            "error",
            "fusion_decision_accounting_sha_mismatch",
            "fusion decision_accounting hash does not match its own payload.",
        )
    if accounting != expected:
        add_issue(
            issues,
            "error",
            "fusion_decision_accounting_recomputed_mismatch",
            "fusion decision_accounting differs from verifier-recomputed final-source accounting.",
        )


def verify_llm_expert_contracts(
    card: dict[str, Any],
    dynamic: dict[str, Any],
    *,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    source_fingerprint = as_dict(card.get("source_fingerprint"))
    context = as_dict(dynamic.get("llm_context_completion"))
    if context:
        checks["llm_context_completion_seen"] += 1
        verify_context_completion_contract(
            context,
            dynamic=dynamic,
            source_fingerprint=source_fingerprint,
            issues=issues,
            checks=checks,
        )
    probe = as_dict(dynamic.get("llm_probe_synthesis"))
    if probe:
        checks["llm_probe_synthesis_seen"] += 1
        verify_probe_synthesis_contract(
            probe,
            dynamic=dynamic,
            source_fingerprint=source_fingerprint,
            issues=issues,
            checks=checks,
        )


def verify_framework_mock_contracts(dynamic: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    meta = as_dict(dynamic.get("meta"))
    mock_ids = [str(item) for item in meta.get("framework_mocks") or [] if str(item)]
    if not mock_ids:
        return
    checks["framework_mock_cards"] += 1
    checks["framework_mock_ids"] += len(mock_ids)
    contracts = [item for item in meta.get("framework_mock_contracts") or [] if isinstance(item, dict)]
    by_id = {str(item.get("mock_id") or ""): item for item in contracts}
    if not contracts:
        add_issue(
            issues,
            "warning",
            "framework_mock_contracts_missing",
            "dynamic evidence uses framework_mocks but does not record framework_mock_contracts.",
        )
        return
    for mock_id in mock_ids:
        contract = by_id.get(mock_id)
        if not contract:
            add_issue(
                issues,
                "warning",
                "framework_mock_contract_missing_for_id",
                f"framework mock {mock_id!r} has no matching contract certificate.",
            )
            continue
        checks["framework_mock_contracts_verified"] += 1
        if contract.get("schema_version") != FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION:
            add_issue(
                issues,
                "error",
                "framework_mock_contract_schema_mismatch",
                f"framework mock {mock_id!r} has invalid schema_version.",
            )
        if contract.get("mock_id") != mock_id:
            add_issue(
                issues,
                "error",
                "framework_mock_contract_id_mismatch",
                f"framework mock contract id={contract.get('mock_id')!r} expected {mock_id!r}.",
            )
        if contract.get("deterministic") is not True:
            add_issue(
                issues,
                "error",
                "framework_mock_contract_not_deterministic",
                f"framework mock {mock_id!r} must declare deterministic=true.",
            )
        if contract.get("no_external_services") is not True:
            add_issue(
                issues,
                "error",
                "framework_mock_contract_allows_external_services",
                f"framework mock {mock_id!r} must declare no_external_services=true.",
            )
        if not contract.get("version"):
            add_issue(
                issues,
                "error",
                "framework_mock_contract_version_missing",
                f"framework mock {mock_id!r} has no version.",
            )
        if not isinstance(contract.get("limitations"), list) or not contract.get("limitations"):
            add_issue(
                issues,
                "error",
                "framework_mock_contract_limitations_missing",
                f"framework mock {mock_id!r} must record limitations.",
            )
        contract_hash = contract.get(FRAMEWORK_MOCK_CONTRACT_HASH_FIELD)
        if contract_hash is None:
            add_issue(
                issues,
                "warning",
                "framework_mock_contract_sha_missing",
                f"framework mock {mock_id!r} does not carry a self hash certificate.",
            )
        elif contract_hash != build_framework_mock_contract_hash(contract):
            add_issue(
                issues,
                "error",
                "framework_mock_contract_sha_mismatch",
                f"framework mock {mock_id!r} contract_sha256 differs from verifier recomputation.",
            )


def verify_java_execution_certificate(dynamic: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    if not dynamic:
        return
    certificate = as_dict(dynamic.get("execution_certificate"))
    status = str(dynamic.get("status") or "")
    has_observable_execution_surface = bool(dynamic.get("compile")) or bool(dynamic.get("execution")) or status in {
        "executed",
        "compile_success",
        "compile_failed",
        "execution_failed",
        "timeout",
        "llm_context_compile_success",
        "llm_context_compile_failed",
        "llm_probe_compile_failed",
    }
    if not certificate:
        if has_observable_execution_surface:
            checks["java_execution_certificate_missing"] += 1
            add_issue(
                issues,
                "warning",
                "java_execution_certificate_missing",
                "dynamic evidence has compile/execution observations but no java execution certificate.",
            )
        return
    checks["java_execution_certificate_present"] += 1
    if certificate.get("schema_version") != JAVA_EXECUTION_CERTIFICATE_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_schema_mismatch",
            f"execution_certificate.schema_version={certificate.get('schema_version')!r} expected {JAVA_EXECUTION_CERTIFICATE_SCHEMA_VERSION}.",
        )
    if certificate.get("status") != status:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_status_mismatch",
            f"execution_certificate.status={certificate.get('status')!r} expected dynamic.status={status!r}.",
        )
    if dynamic.get("engine") is not None and certificate.get("engine") != dynamic.get("engine"):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_engine_mismatch",
            "execution_certificate.engine does not match dynamic.engine.",
        )
    if dynamic.get("mode") is not None and certificate.get("mode") != dynamic.get("mode"):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_mode_mismatch",
            "execution_certificate.mode does not match dynamic.mode.",
        )
    sandbox_ok, sandbox_reasons = verify_java_execution_sandbox_for_trust(certificate)
    checks["java_execution_sandbox_verified" if sandbox_ok else "java_execution_sandbox_unverified"] += 1
    if not sandbox_ok:
        add_issue(
            issues,
            "error",
            sandbox_reasons[0] if sandbox_reasons else "java_execution_sandbox_untrusted",
            "execution_certificate.execution_sandbox failed sandbox policy verification.",
        )
    toolchain_ok, toolchain_reasons = verify_java_toolchain_for_trust(certificate)
    if toolchain_ok:
        reason = toolchain_reasons[0] if toolchain_reasons else "java_toolchain_verified"
        checks[reason] += 1
    else:
        checks["java_toolchain_unverified"] += 1
        add_issue(
            issues,
            "error",
            toolchain_reasons[0] if toolchain_reasons else "java_toolchain_untrusted",
            "execution_certificate.java_toolchain failed toolchain certificate verification.",
        )
    outcome_ok, outcome_reasons = verify_dynamic_outcome_for_trust(certificate, dynamic)
    if outcome_ok:
        checks["dynamic_outcome_verified"] += 1
    else:
        checks["dynamic_outcome_unverified"] += 1
        add_issue(
            issues,
            "error",
            outcome_reasons[0] if outcome_reasons else "dynamic_outcome_untrusted",
            "execution_certificate.dynamic_outcome failed outcome certificate verification.",
        )

    compile_info = as_dict(dynamic.get("compile"))
    compile_cert = as_dict(certificate.get("compile"))
    if compile_cert:
        if compile_cert.get("returncode") != compile_info.get("returncode"):
            add_issue(issues, "error", "java_execution_certificate_compile_returncode_mismatch", "compile returncode differs from certificate.")
        if compile_cert.get("stdout_sha256") != sha256_text(str(compile_info.get("stdout") or "")):
            add_issue(issues, "error", "java_execution_certificate_compile_stdout_sha_mismatch", "compile stdout hash differs from certificate.")
        if compile_cert.get("stderr_sha256") != sha256_text(str(compile_info.get("stderr") or "")):
            add_issue(issues, "error", "java_execution_certificate_compile_stderr_sha_mismatch", "compile stderr hash differs from certificate.")
        if compile_info.get("label") is not None and compile_cert.get("attempt_name") != compile_info.get("label"):
            add_issue(issues, "error", "java_execution_certificate_compile_attempt_mismatch", "compile attempt name differs from certificate.")
    elif compile_info:
        add_issue(issues, "error", "java_execution_certificate_compile_section_missing", "compile certificate section is missing.")

    execution_info = as_dict(dynamic.get("execution"))
    execution_cert = as_dict(certificate.get("execution"))
    if execution_cert:
        if execution_cert.get("returncode") != execution_info.get("returncode"):
            add_issue(issues, "error", "java_execution_certificate_execution_returncode_mismatch", "execution returncode differs from certificate.")
        if execution_cert.get("timeout") != (execution_info.get("timeout") is True):
            add_issue(issues, "error", "java_execution_certificate_timeout_mismatch", "execution timeout flag differs from certificate.")
        if execution_cert.get("stdout_sha256") != sha256_text(str(execution_info.get("stdout") or "")):
            add_issue(issues, "error", "java_execution_certificate_execution_stdout_sha_mismatch", "execution stdout hash differs from certificate.")
        if execution_cert.get("stderr_sha256") != sha256_text(str(execution_info.get("stderr") or "")):
            add_issue(issues, "error", "java_execution_certificate_execution_stderr_sha_mismatch", "execution stderr hash differs from certificate.")
        result_line_count = count_probe_result_lines(str(execution_info.get("stdout") or ""))
        if execution_cert.get("result_line_count") != result_line_count:
            add_issue(issues, "error", "java_execution_certificate_result_line_count_mismatch", "execution EVICLONE_RESULT line count differs from certificate.")
        if status == "executed" and result_line_count != 1:
            add_issue(issues, "error", "java_execution_certificate_result_line_count_not_one", "executed dynamic evidence must contain exactly one EVICLONE_RESULT line.")
        parsed = execution_info.get("parsed") if isinstance(execution_info.get("parsed"), dict) else None
        expected_parsed_sha = canonical_sha256(parsed) if parsed is not None else None
        if execution_cert.get("parsed_sha256") != expected_parsed_sha:
            add_issue(issues, "error", "java_execution_certificate_parsed_sha_mismatch", "parsed execution hash differs from certificate.")
        if parsed is not None and execution_cert.get("parsed_same") != parsed.get("same"):
            add_issue(issues, "error", "java_execution_certificate_parsed_same_mismatch", "parsed.same differs from certificate.")
        if parsed is not None and execution_cert.get("parsed_status") != parsed.get("status"):
            add_issue(issues, "error", "java_execution_certificate_parsed_status_mismatch", "parsed.status differs from certificate.")
    elif execution_info:
        add_issue(issues, "error", "java_execution_certificate_execution_section_missing", "execution certificate section is missing.")

    verify_execution_result_oracle_certificate(
        certificate=certificate,
        dynamic=dynamic,
        issues=issues,
        checks=checks,
    )
    verify_probe_adequacy_certificate(
        certificate=certificate,
        dynamic=dynamic,
        issues=issues,
        checks=checks,
    )
    verify_java_execution_framework_mock_binding(
        certificate=certificate,
        dynamic=dynamic,
        issues=issues,
        checks=checks,
    )
    verify_java_execution_runtime_fixture_binding(
        certificate=certificate,
        dynamic=dynamic,
        issues=issues,
        checks=checks,
    )
    verify_runtime_source_safety_certificate(
        certificate=certificate,
        issues=issues,
        checks=checks,
    )

    expected_certificate_sha = canonical_sha256({key: value for key, value in certificate.items() if key != "certificate_sha256"})
    if certificate.get("certificate_sha256") != expected_certificate_sha:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_sha_mismatch",
            "execution_certificate.certificate_sha256 does not match the verifier-recomputed certificate payload.",
        )


def verify_functional_block_ir_binding(dynamic: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    meta = as_dict(dynamic.get("meta"))
    pair_ir = as_dict(meta.get("functional_block_pair_ir"))
    module_graph = as_dict(meta.get("executable_module_graph"))
    if not pair_ir:
        checks["functional_block_ir_absent"] += 1
        if module_graph:
            add_issue(
                issues,
                "error",
                "executable_module_graph_without_functional_block_ir",
                "dynamic.meta.executable_module_graph is present without dynamic.meta.functional_block_pair_ir.",
            )
        return

    checks["functional_block_ir_present"] += 1
    if pair_ir.get("schema_version") != FUNCTIONAL_BLOCK_PAIR_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "functional_block_pair_ir_schema_mismatch",
            f"functional_block_pair_ir.schema_version={pair_ir.get('schema_version')!r} expected {FUNCTIONAL_BLOCK_PAIR_SCHEMA_VERSION}.",
        )
    pair_result = verify_pair_functional_block_ir(pair_ir)
    if pair_result.get("status") == "verified":
        checks["functional_block_ir_verified"] += 1
    else:
        checks["functional_block_ir_unverified"] += 1
        for issue in pair_result.get("issues") or []:
            add_issue(
                issues,
                "error",
                f"functional_block_pair_ir_{issue}",
                f"functional_block_pair_ir verifier rejected the block graph: {issue}.",
            )

    llm_contract = as_dict(pair_ir.get("llm_contract"))
    if llm_contract.get("clone_decision_allowed") is not False:
        add_issue(
            issues,
            "error",
            "functional_block_pair_ir_allows_llm_clone_decision",
            "functional_block_pair_ir must record clone_decision_allowed=false.",
        )
    for side in ("a", "b"):
        side_ir = as_dict(pair_ir.get(side))
        side_llm = as_dict(side_ir.get("llm_contract"))
        if side_llm.get("raw_source_patch_allowed") is not False:
            add_issue(
                issues,
                "error",
                f"functional_block_{side}_allows_raw_source_patch",
                f"functional_block_pair_ir.{side}.llm_contract must record raw_source_patch_allowed=false.",
            )

    if not module_graph:
        add_issue(
            issues,
            "error",
            "executable_module_graph_missing",
            "dynamic.meta.functional_block_pair_ir is present but dynamic.meta.executable_module_graph is missing.",
        )
    else:
        checks["executable_module_graph_present"] += 1
        if module_graph.get("schema_version") != EXECUTABLE_MODULE_GRAPH_SCHEMA_VERSION:
            add_issue(
                issues,
                "error",
                "executable_module_graph_schema_mismatch",
                f"executable_module_graph.schema_version={module_graph.get('schema_version')!r} expected {EXECUTABLE_MODULE_GRAPH_SCHEMA_VERSION}.",
            )
        module_result = verify_executable_module_graph(module_graph, functional_block_pair_ir=pair_ir)
        if module_result.get("status") == "verified":
            checks["executable_module_graph_verified"] += 1
        else:
            checks["executable_module_graph_unverified"] += 1
            for issue in module_result.get("issues") or []:
                add_issue(
                    issues,
                    "error",
                    f"executable_module_graph_{issue}",
                    f"executable_module_graph verifier rejected the standardized module graph: {issue}.",
                )
        if module_graph.get("llm_contract", {}).get("clone_decision_allowed") is not False:
            add_issue(
                issues,
                "error",
                "executable_module_graph_allows_llm_clone_decision",
                "executable_module_graph must record clone_decision_allowed=false.",
            )

    certificate = as_dict(dynamic.get("execution_certificate"))
    if not certificate:
        checks["functional_block_ir_certificate_binding_missing_certificate"] += 1
        return
    binding = as_dict(certificate.get("functional_blocks"))
    if not binding:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_functional_blocks_missing",
            "dynamic.meta.functional_block_pair_ir is present but execution_certificate.functional_blocks is missing.",
        )
        return
    checks["functional_block_ir_certificate_binding_seen"] += 1
    expected_pair_ir_sha = canonical_sha256(pair_ir)
    if binding.get("pair_ir_present") is not True:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_functional_block_ir_not_present",
            "execution_certificate.functional_blocks must record pair_ir_present=true when meta.functional_block_pair_ir exists.",
        )
    if binding.get("pair_ir_sha256") != expected_pair_ir_sha:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_functional_block_ir_sha_mismatch",
            "execution_certificate.functional_blocks.pair_ir_sha256 does not match dynamic.meta.functional_block_pair_ir.",
        )
    if binding.get("pair_ir_self_hash") != pair_ir.get(FUNCTIONAL_BLOCK_PAIR_HASH_FIELD):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_functional_block_ir_self_hash_mismatch",
            "execution_certificate.functional_blocks.pair_ir_self_hash does not match functional_block_pair_ir self hash.",
        )
    if binding.get("module_signature_a") != list(pair_ir.get("module_signature_a") or []):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_functional_block_signature_a_mismatch",
            "execution_certificate.functional_blocks.module_signature_a does not match the current functional block IR.",
        )
    if binding.get("module_signature_b") != list(pair_ir.get("module_signature_b") or []):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_functional_block_signature_b_mismatch",
            "execution_certificate.functional_blocks.module_signature_b does not match the current functional block IR.",
        )
    if binding.get("llm_clone_decision_allowed") is not False:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_functional_blocks_allows_llm_clone_decision",
            "execution_certificate.functional_blocks must bind llm_clone_decision_allowed=false.",
        )
    if module_graph:
        expected_module_graph_sha = canonical_sha256(module_graph)
        if binding.get("module_graph_present") is not True:
            add_issue(
                issues,
                "error",
                "java_execution_certificate_executable_module_graph_not_present",
                "execution_certificate.functional_blocks must record module_graph_present=true when meta.executable_module_graph exists.",
            )
        if binding.get("module_graph_sha256") != expected_module_graph_sha:
            add_issue(
                issues,
                "error",
                "java_execution_certificate_executable_module_graph_sha_mismatch",
                "execution_certificate.functional_blocks.module_graph_sha256 does not match dynamic.meta.executable_module_graph.",
            )
        if binding.get("module_graph_self_hash") != module_graph.get(EXECUTABLE_MODULE_GRAPH_HASH_FIELD):
            add_issue(
                issues,
                "error",
                "java_execution_certificate_executable_module_graph_self_hash_mismatch",
                "execution_certificate.functional_blocks.module_graph_self_hash does not match executable_module_graph self hash.",
            )
        if binding.get("module_graph_source_pair_ir_sha256") != module_graph.get("source_pair_ir_sha256"):
            add_issue(
                issues,
                "error",
                "java_execution_certificate_executable_module_graph_source_ir_mismatch",
                "execution_certificate.functional_blocks.module_graph_source_pair_ir_sha256 does not match executable_module_graph source IR binding.",
            )
    checks["functional_block_ir_certificate_binding_verified"] += 1


def verify_module_probe_plan_binding(dynamic: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    meta = as_dict(dynamic.get("meta"))
    module_graph = as_dict(meta.get("executable_module_graph"))
    probe_contract = as_dict(meta.get("probe_contract"))
    plan = as_dict(meta.get("module_probe_plan"))
    if not module_graph:
        if plan:
            add_issue(
                issues,
                "error",
                "module_probe_plan_without_executable_module_graph",
                "dynamic.meta.module_probe_plan is present without dynamic.meta.executable_module_graph.",
            )
        return
    checks["module_probe_plan_required"] += 1
    if not plan:
        add_issue(
            issues,
            "error",
            "module_probe_plan_missing",
            "dynamic.meta.executable_module_graph is present but dynamic.meta.module_probe_plan is missing.",
        )
        return
    checks["module_probe_plan_present"] += 1
    if plan.get("schema_version") != MODULE_PROBE_PLAN_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "module_probe_plan_schema_mismatch",
            f"module_probe_plan.schema_version={plan.get('schema_version')!r} expected {MODULE_PROBE_PLAN_SCHEMA_VERSION}.",
        )
    verification = verify_module_probe_plan(plan, executable_module_graph=module_graph, probe_contract=probe_contract)
    if verification.get("status") == "verified":
        checks["module_probe_plan_verified"] += 1
    else:
        checks["module_probe_plan_unverified"] += 1
        for issue in verification.get("issues") or []:
            add_issue(
                issues,
                "error",
                f"module_probe_plan_{issue}",
                f"module_probe_plan verifier rejected the plan: {issue}.",
            )
    if plan.get("llm_contract", {}).get("clone_decision_allowed") is not False:
        add_issue(
            issues,
            "error",
            "module_probe_plan_allows_llm_clone_decision",
            "module_probe_plan must record clone_decision_allowed=false.",
        )
    if plan.get("llm_contract", {}).get("raw_source_patch_allowed") is not False:
        add_issue(
            issues,
            "error",
            "module_probe_plan_allows_raw_source_patch",
            "module_probe_plan must record raw_source_patch_allowed=false.",
        )

    certificate = as_dict(dynamic.get("execution_certificate"))
    if not certificate:
        checks["module_probe_plan_certificate_binding_missing_certificate"] += 1
        return
    probe_cert = as_dict(certificate.get("probe"))
    if not probe_cert:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_probe_section_missing",
            "execution_certificate.probe is missing but dynamic evidence records module_probe_plan.",
        )
        return
    expected_plan_sha = canonical_sha256(plan)
    if probe_cert.get("module_probe_plan_present") is not True:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_probe_plan_not_present",
            "execution_certificate.probe must record module_probe_plan_present=true when meta.module_probe_plan exists.",
        )
    if probe_cert.get("module_probe_plan_sha256") != expected_plan_sha:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_probe_plan_sha_mismatch",
            "execution_certificate.probe.module_probe_plan_sha256 does not match dynamic.meta.module_probe_plan.",
        )
    if probe_cert.get("module_probe_plan_self_hash") != plan.get(MODULE_PROBE_PLAN_HASH_FIELD):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_probe_plan_self_hash_mismatch",
            "execution_certificate.probe.module_probe_plan_self_hash does not match module_probe_plan self hash.",
        )
    risk = plan.get("risk") if isinstance(plan.get("risk"), dict) else {}
    if probe_cert.get("module_probe_plan_risk") != risk.get("level"):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_probe_plan_risk_mismatch",
            "execution_certificate.probe.module_probe_plan_risk does not match current module_probe_plan risk.",
        )
    coverage = plan.get("coverage") if isinstance(plan.get("coverage"), dict) else {}
    expected_uncovered = list(coverage.get("uncovered_obligations") or [])
    if probe_cert.get("module_probe_plan_uncovered_obligations") != expected_uncovered:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_probe_plan_uncovered_mismatch",
            "execution_certificate.probe.module_probe_plan_uncovered_obligations does not match current module_probe_plan coverage.",
        )
    checks["module_probe_plan_certificate_binding_verified"] += 1


def verify_executable_composition_binding(
    dynamic: dict[str, Any],
    *,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    meta = as_dict(dynamic.get("meta"))
    module_graph = as_dict(meta.get("executable_module_graph"))
    module_probe_plan = as_dict(meta.get("module_probe_plan"))
    composition = as_dict(meta.get("executable_composition_spec"))
    if not module_graph:
        if composition:
            add_issue(
                issues,
                "error",
                "executable_composition_without_module_graph",
                "dynamic.meta.executable_composition_spec is present without dynamic.meta.executable_module_graph.",
            )
        return
    checks["executable_composition_required"] += 1
    if not composition:
        add_issue(
            issues,
            "error",
            "executable_composition_missing",
            "dynamic.meta.executable_module_graph is present but dynamic.meta.executable_composition_spec is missing.",
        )
        return
    checks["executable_composition_present"] += 1
    if composition.get("schema_version") != EXECUTABLE_COMPOSITION_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "executable_composition_schema_mismatch",
            f"executable_composition_spec.schema_version={composition.get('schema_version')!r} expected {EXECUTABLE_COMPOSITION_SCHEMA_VERSION}.",
        )
    verification = verify_executable_composition_spec(
        composition,
        executable_module_graph=module_graph,
        module_probe_plan=module_probe_plan,
    )
    if verification.get("status") == "verified":
        checks["executable_composition_verified"] += 1
    else:
        checks["executable_composition_unverified"] += 1
        for issue in verification.get("issues") or []:
            add_issue(
                issues,
                "error",
                f"executable_composition_{issue}",
                f"executable_composition_spec verifier rejected the module composition: {issue}.",
            )
    if composition.get("llm_contract", {}).get("clone_decision_allowed") is not False:
        add_issue(
            issues,
            "error",
            "executable_composition_allows_llm_clone_decision",
            "executable_composition_spec must record clone_decision_allowed=false.",
        )
    lowering_contract = composition.get("lowering_contract") if isinstance(composition.get("lowering_contract"), dict) else {}
    if lowering_contract.get("raw_source_patch_allowed") is not False:
        add_issue(
            issues,
            "error",
            "executable_composition_allows_raw_source_patch",
            "executable_composition_spec lowering contract must record raw_source_patch_allowed=false.",
        )
    if lowering_contract.get("llm_module_rewrite_allowed") is not False:
        add_issue(
            issues,
            "error",
            "executable_composition_allows_llm_module_rewrite",
            "executable_composition_spec lowering contract must record llm_module_rewrite_allowed=false.",
        )

    certificate = as_dict(dynamic.get("execution_certificate"))
    if not certificate:
        checks["executable_composition_certificate_binding_missing_certificate"] += 1
        return
    composition_cert = as_dict(certificate.get("executable_composition"))
    if not composition_cert:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_executable_composition_missing",
            "execution_certificate.executable_composition is missing but dynamic evidence records executable_composition_spec.",
        )
        return
    expected_composition_sha = canonical_sha256(composition)
    if composition_cert.get("composition_present") is not True:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_executable_composition_not_present",
            "execution_certificate.executable_composition must record composition_present=true when meta.executable_composition_spec exists.",
        )
    if composition_cert.get("composition_sha256") != expected_composition_sha:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_executable_composition_sha_mismatch",
            "execution_certificate.executable_composition.composition_sha256 does not match dynamic.meta.executable_composition_spec.",
        )
    if composition_cert.get("composition_self_hash") != composition.get(EXECUTABLE_COMPOSITION_HASH_FIELD):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_executable_composition_self_hash_mismatch",
            "execution_certificate.executable_composition.composition_self_hash does not match executable_composition_spec self hash.",
        )
    if composition_cert.get("module_graph_sha256") != canonical_sha256(module_graph):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_executable_composition_module_graph_sha_mismatch",
            "execution_certificate.executable_composition.module_graph_sha256 does not match dynamic.meta.executable_module_graph.",
        )
    if composition_cert.get("module_probe_plan_sha256") != (canonical_sha256(module_probe_plan) if module_probe_plan else None):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_executable_composition_probe_plan_sha_mismatch",
            "execution_certificate.executable_composition.module_probe_plan_sha256 does not match dynamic.meta.module_probe_plan.",
        )
    if composition_cert.get("raw_source_patch_allowed") is not False:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_executable_composition_allows_raw_source_patch",
            "execution_certificate.executable_composition must bind raw_source_patch_allowed=false.",
        )
    if composition_cert.get("llm_module_rewrite_allowed") is not False:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_executable_composition_allows_llm_module_rewrite",
            "execution_certificate.executable_composition must bind llm_module_rewrite_allowed=false.",
        )
    checks["executable_composition_certificate_binding_verified"] += 1


def verify_module_composition_lowering_binding(
    dynamic: dict[str, Any],
    *,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    meta = as_dict(dynamic.get("meta"))
    lowering = as_dict(meta.get("module_composition_lowering"))
    if not lowering:
        checks["module_composition_lowering_not_used"] += 1
        certificate = as_dict(dynamic.get("execution_certificate"))
        composition_cert = as_dict(certificate.get("executable_composition"))
        if composition_cert and composition_cert.get("module_composition_lowering_present") is True:
            add_issue(
                issues,
                "error",
                "java_execution_certificate_module_composition_lowering_unexpected",
                "execution_certificate.executable_composition records a module lowering artifact that is absent from dynamic.meta.",
            )
        return
    checks["module_composition_lowering_present"] += 1
    if lowering.get("schema_version") != MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "module_composition_lowering_schema_mismatch",
            f"module_composition_lowering.schema_version={lowering.get('schema_version')!r} expected {MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION}.",
        )
    expected_lowering_hash = build_module_composition_lowering_hash(lowering)
    if lowering.get(MODULE_COMPOSITION_LOWERING_HASH_FIELD) != expected_lowering_hash:
        add_issue(
            issues,
            "error",
            "module_composition_lowering_sha_mismatch",
            "module_composition_lowering lowering_sha256 does not match verifier recomputation.",
        )
    composition = as_dict(meta.get("executable_composition_spec"))
    if not composition:
        add_issue(
            issues,
            "error",
            "module_composition_lowering_without_composition",
            "module_composition_lowering exists without executable_composition_spec.",
        )
    else:
        if lowering.get("source_composition_sha256") != canonical_sha256(composition):
            add_issue(
                issues,
                "error",
                "module_composition_lowering_composition_sha_mismatch",
                "module_composition_lowering source_composition_sha256 does not match executable_composition_spec.",
            )
        if lowering.get("source_composition_self_hash") != composition.get(EXECUTABLE_COMPOSITION_HASH_FIELD):
            add_issue(
                issues,
                "error",
                "module_composition_lowering_composition_self_hash_mismatch",
                "module_composition_lowering source_composition_self_hash does not match executable_composition_spec self hash.",
            )
    module_probe_plan = as_dict(meta.get("module_probe_plan"))
    if module_probe_plan and lowering.get("source_probe_plan_sha256") != canonical_sha256(module_probe_plan):
        add_issue(
            issues,
            "error",
            "module_composition_lowering_probe_plan_sha_mismatch",
            "module_composition_lowering source_probe_plan_sha256 does not match module_probe_plan.",
        )
    probe_contract = as_dict(meta.get("probe_contract"))
    if probe_contract:
        if lowering.get("probe_contract_sha256") != canonical_sha256(probe_contract):
            add_issue(
                issues,
                "error",
                "module_composition_lowering_probe_contract_sha_mismatch",
                "module_composition_lowering probe_contract_sha256 does not match probe_contract.",
            )
        if lowering.get("probe_body_sha256") != probe_contract.get("probe_body_sha256"):
            add_issue(
                issues,
                "error",
                "module_composition_lowering_probe_body_sha_mismatch",
                "module_composition_lowering probe_body_sha256 does not match probe_contract.probe_body_sha256.",
            )
    if lowering.get("probe_invokes_original_snippet_methods") is not False:
        add_issue(
            issues,
            "error",
            "module_composition_lowering_invokes_original_snippets",
            "module_composition_lowering must record probe_invokes_original_snippet_methods=false.",
        )
    if lowering.get("raw_source_patch_allowed") is not False:
        add_issue(
            issues,
            "error",
            "module_composition_lowering_allows_raw_source_patch",
            "module_composition_lowering must record raw_source_patch_allowed=false.",
        )
    if lowering.get("llm_used") is not False:
        add_issue(
            issues,
            "error",
            "module_composition_lowering_uses_llm",
            "module_composition_lowering must be deterministic and record llm_used=false.",
        )

    certificate = as_dict(dynamic.get("execution_certificate"))
    composition_cert = as_dict(certificate.get("executable_composition"))
    if not composition_cert:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_composition_lowering_missing_composition_cert",
            "execution_certificate.executable_composition is missing but module_composition_lowering is present.",
        )
        return
    if composition_cert.get("module_composition_lowering_present") is not True:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_composition_lowering_not_present",
            "execution_certificate.executable_composition must record module_composition_lowering_present=true.",
        )
    if composition_cert.get("module_composition_lowering_sha256") != canonical_sha256(lowering):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_composition_lowering_sha_mismatch",
            "execution_certificate.executable_composition.module_composition_lowering_sha256 does not match dynamic.meta.module_composition_lowering.",
        )
    if composition_cert.get("module_composition_lowering_self_hash") != lowering.get(MODULE_COMPOSITION_LOWERING_HASH_FIELD):
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_composition_lowering_self_hash_mismatch",
            "execution_certificate.executable_composition.module_composition_lowering_self_hash does not match lowering self hash.",
        )
    if composition_cert.get("module_composition_lowering_calls_original_snippets") is not False:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_module_composition_lowering_calls_original_snippets",
            "execution_certificate.executable_composition must bind module lowering calls_original_snippets=false.",
        )
    checks["module_composition_lowering_certificate_binding_verified"] += 1


def verify_java_execution_framework_mock_binding(
    *,
    certificate: dict[str, Any],
    dynamic: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    meta = as_dict(dynamic.get("meta"))
    mock_ids = [str(item) for item in meta.get("framework_mocks") or [] if str(item)]
    contracts = [item for item in meta.get("framework_mock_contracts") or [] if isinstance(item, dict)]
    if not mock_ids and not contracts:
        checks["java_execution_framework_mock_binding_not_used"] += 1
        return
    probe_cert = as_dict(certificate.get("probe"))
    if not probe_cert:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_probe_section_missing",
            "execution_certificate.probe is missing but dynamic evidence records framework mocks.",
        )
        return
    checks["java_execution_framework_mock_binding_seen"] += 1
    if probe_cert.get("framework_mocks") != mock_ids:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_framework_mocks_mismatch",
            "execution_certificate.probe.framework_mocks does not match dynamic.meta.framework_mocks.",
        )
    expected_contract_hashes = [canonical_sha256(contract) for contract in contracts]
    if probe_cert.get("framework_mock_contract_sha256s") != expected_contract_hashes:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_framework_mock_contract_sha_mismatch",
            "execution_certificate.probe.framework_mock_contract_sha256s does not match current dynamic.meta.framework_mock_contracts.",
        )
    expected_self_hashes = [contract.get(FRAMEWORK_MOCK_CONTRACT_HASH_FIELD) for contract in contracts]
    if probe_cert.get("framework_mock_contract_self_hashes") != expected_self_hashes:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_framework_mock_contract_self_hash_mismatch",
            "execution_certificate.probe.framework_mock_contract_self_hashes does not match current dynamic.meta.framework_mock_contracts.",
        )
    checks["java_execution_framework_mock_binding_verified"] += 1


def verify_java_execution_runtime_fixture_binding(
    *,
    certificate: dict[str, Any],
    dynamic: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    meta = as_dict(dynamic.get("meta"))
    mock_ids = {str(item) for item in meta.get("framework_mocks") or [] if str(item)}
    certificate_fixtures = as_dict(certificate.get("runtime_fixtures"))
    sandbox = as_dict(certificate.get("execution_sandbox"))
    fixture_seen = False
    binding_ok = True

    for fixture_id, spec in RUNTIME_FIXTURE_SPECS.items():
        top_fixture = as_dict(dynamic.get(fixture_id))
        certificate_fixture = as_dict(certificate_fixtures.get(fixture_id))
        sandbox_fixture = as_dict(sandbox.get(fixture_id))
        fixture_used = bool(top_fixture or certificate_fixture or sandbox_fixture or fixture_id in mock_ids)
        if not fixture_used:
            continue

        fixture_seen = True
        checks["java_execution_runtime_fixture_binding_seen"] += 1
        checks[f"java_execution_runtime_fixture_{fixture_id}_seen"] += 1

        if not top_fixture:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_top_level_missing",
                f"dynamic evidence uses {fixture_id!r} but the top-level fixture manifest is missing.",
            )
        if not certificate_fixture:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_certificate_missing",
                f"execution_certificate.runtime_fixtures is missing {fixture_id!r}.",
            )
        if not sandbox_fixture:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_sandbox_missing",
                f"execution_certificate.execution_sandbox is missing {fixture_id!r}.",
            )

        reference_fixture = top_fixture or certificate_fixture or sandbox_fixture
        expected_schema = spec.get("schema_version")
        if reference_fixture.get("schema_version") != expected_schema:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_schema_mismatch",
                f"{fixture_id} schema_version={reference_fixture.get('schema_version')!r} expected {expected_schema!r}.",
            )
        fixture_hash = reference_fixture.get(RUNTIME_FIXTURE_HASH_FIELD)
        if fixture_hash is None:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_sha_missing",
                f"{fixture_id} is missing fixture_sha256.",
            )
        elif fixture_hash != build_runtime_fixture_hash(reference_fixture):
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_sha_mismatch",
                f"{fixture_id}.fixture_sha256 differs from verifier recomputation.",
            )
        if reference_fixture.get("deterministic") is not True:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_not_deterministic",
                f"{fixture_id} must declare deterministic=True.",
            )
        if reference_fixture.get("no_external_services") is not True:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_allows_external_services",
                f"{fixture_id} must declare no_external_services=True.",
            )
        if top_fixture and certificate_fixture and top_fixture != certificate_fixture:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_certificate_mismatch",
                f"execution_certificate.runtime_fixtures.{fixture_id} does not match the top-level dynamic fixture manifest.",
            )
        if certificate_fixture and sandbox_fixture and certificate_fixture != sandbox_fixture:
            binding_ok = False
            add_issue(
                issues,
                "error",
                f"runtime_fixture_{fixture_id}_sandbox_mismatch",
                f"execution_certificate.execution_sandbox.{fixture_id} does not match runtime_fixtures.{fixture_id}.",
            )

    if not fixture_seen:
        checks["java_execution_runtime_fixture_binding_not_used"] += 1
    elif binding_ok:
        checks["java_execution_runtime_fixture_binding_verified"] += 1


def verify_probe_adequacy_certificate(
    *,
    certificate: dict[str, Any],
    dynamic: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    meta = as_dict(dynamic.get("meta"))
    probe_contract = as_dict(meta.get("probe_contract"))
    if not probe_contract:
        checks["probe_adequacy_not_applicable"] += 1
        return
    checks["probe_adequacy_required_cards"] += 1
    probe_cert = as_dict(certificate.get("probe"))
    if not probe_cert:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_probe_section_missing",
            "execution_certificate.probe is missing but dynamic evidence records a probe_contract.",
        )
        return
    expected_contract_sha = canonical_sha256(probe_contract)
    if probe_cert.get("probe_contract_sha256") != expected_contract_sha:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_probe_contract_sha_mismatch",
            "execution_certificate.probe.probe_contract_sha256 does not match current dynamic.meta.probe_contract.",
        )
    contract_hash = probe_contract.get(PROBE_CONTRACT_HASH_FIELD)
    if probe_cert.get("probe_contract_self_hash") != contract_hash:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_probe_contract_self_hash_mismatch",
            "execution_certificate.probe.probe_contract_self_hash does not match current dynamic.meta.probe_contract.",
        )

    adequacy = as_dict(probe_cert.get("probe_adequacy_certificate"))
    if not adequacy:
        checks["probe_adequacy_missing"] += 1
        add_issue(
            issues,
            "error",
            "probe_adequacy_certificate_missing",
            "execution_certificate.probe has no probe_adequacy_certificate.",
        )
        return
    checks["probe_adequacy_present"] += 1
    if adequacy.get("schema_version") != PROBE_ADEQUACY_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "probe_adequacy_schema_mismatch",
            f"probe_adequacy schema_version={adequacy.get('schema_version')!r} expected {PROBE_ADEQUACY_SCHEMA_VERSION}.",
        )
    adequacy_hash = adequacy.get(PROBE_ADEQUACY_HASH_FIELD)
    if adequacy_hash is None:
        add_issue(issues, "error", "probe_adequacy_sha_missing", "probe_adequacy certificate_sha256 is missing.")
    elif adequacy_hash != build_probe_adequacy_certificate_hash(adequacy):
        add_issue(
            issues,
            "error",
            "probe_adequacy_sha_mismatch",
            "probe_adequacy certificate_sha256 differs from verifier recomputation.",
        )
    if probe_cert.get("probe_adequacy_sha256") != adequacy_hash:
        add_issue(
            issues,
            "error",
            "java_execution_certificate_probe_adequacy_sha_mismatch",
            "execution_certificate.probe.probe_adequacy_sha256 does not match nested probe_adequacy_certificate.",
        )
    if adequacy.get("probe_contract_sha256") != expected_contract_sha:
        add_issue(
            issues,
            "error",
            "probe_adequacy_probe_contract_sha_mismatch",
            "probe_adequacy.probe_contract_sha256 does not match current dynamic.meta.probe_contract.",
        )
    expected_adequacy = build_probe_adequacy_certificate(probe_contract)
    if expected_adequacy and adequacy != expected_adequacy:
        add_issue(
            issues,
            "error",
            "probe_adequacy_recomputed_mismatch",
            "probe_adequacy certificate differs from verifier-recomputed adequacy certificate for the current probe_contract.",
        )
    if adequacy.get("status") == "verified":
        checks["probe_adequacy_verified"] += 1
    elif adequacy.get("status") == "rejected":
        checks["probe_adequacy_rejected"] += 1
        add_issue(
            issues,
            "error",
            "probe_adequacy_unverified",
            "executed dynamic evidence requires a verified probe adequacy certificate.",
        )
    else:
        checks["probe_adequacy_invalid_status"] += 1
        add_issue(
            issues,
            "error",
            "probe_adequacy_status_invalid",
            f"probe_adequacy status={adequacy.get('status')!r} expected 'verified' or 'rejected'.",
        )


def verify_runtime_source_safety_certificate(
    *,
    certificate: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    safety = as_dict(certificate.get("runtime_source_safety"))
    if not safety:
        checks["runtime_source_safety_missing"] += 1
        add_issue(
            issues,
            "error",
            "runtime_source_safety_missing",
            "execution_certificate has no runtime_source_safety certificate.",
        )
        return
    checks["runtime_source_safety_present"] += 1
    if safety.get("schema_version") != RUNTIME_SOURCE_SAFETY_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "runtime_source_safety_schema_mismatch",
            f"runtime_source_safety.schema_version={safety.get('schema_version')!r} expected {RUNTIME_SOURCE_SAFETY_SCHEMA_VERSION}.",
        )
    expected_sha = canonical_sha256({key: value for key, value in safety.items() if key != "certificate_sha256"})
    if safety.get("certificate_sha256") != expected_sha:
        add_issue(
            issues,
            "error",
            "runtime_source_safety_certificate_sha_mismatch",
            "runtime_source_safety.certificate_sha256 does not match the verifier-recomputed certificate payload.",
        )
    if safety.get("source_sha256") != certificate.get("source_sha256"):
        add_issue(
            issues,
            "error",
            "runtime_source_safety_source_sha_mismatch",
            "runtime_source_safety.source_sha256 differs from execution_certificate.source_sha256.",
        )
    status = str(safety.get("status") or "")
    if status == "verified":
        checks["runtime_source_safety_verified"] += 1
    elif status == "rejected":
        checks["runtime_source_safety_rejected"] += 1
    else:
        checks["runtime_source_safety_invalid_status"] += 1
        add_issue(
            issues,
            "error",
            "runtime_source_safety_status_invalid",
            f"runtime_source_safety.status={status!r} expected 'verified' or 'rejected'.",
        )


def verify_execution_result_oracle_certificate(
    *,
    certificate: dict[str, Any],
    dynamic: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    oracle = as_dict(certificate.get("execution_result_oracle"))
    status = str(dynamic.get("status") or "")
    if not oracle:
        checks["execution_result_oracle_missing"] += 1
        add_issue(
            issues,
            "error" if status == "executed" else "warning",
            "execution_result_oracle_missing",
            "execution_certificate has no execution_result_oracle certificate.",
        )
        return
    checks["execution_result_oracle_present"] += 1
    if oracle.get("schema_version") != EXECUTION_RESULT_ORACLE_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "execution_result_oracle_schema_mismatch",
            f"execution_result_oracle.schema_version={oracle.get('schema_version')!r} expected {EXECUTION_RESULT_ORACLE_SCHEMA_VERSION}.",
        )
    expected_sha = canonical_sha256({key: value for key, value in oracle.items() if key != "oracle_sha256"})
    if oracle.get("oracle_sha256") != expected_sha:
        add_issue(
            issues,
            "error",
            "execution_result_oracle_sha_mismatch",
            "execution_result_oracle.oracle_sha256 does not match the verifier-recomputed oracle payload.",
        )
    execution_info = as_dict(dynamic.get("execution"))
    stdout = str(execution_info.get("stdout") or "")
    if oracle.get("stdout_sha256") != sha256_text(stdout):
        add_issue(issues, "error", "execution_result_oracle_stdout_sha_mismatch", "execution_result_oracle stdout hash differs from execution stdout.")
    parsed = execution_info.get("parsed") if isinstance(execution_info.get("parsed"), dict) else None
    expected_parsed_sha = canonical_sha256(parsed) if parsed is not None else None
    if oracle.get("parsed_sha256") != expected_parsed_sha:
        add_issue(issues, "error", "execution_result_oracle_parsed_sha_mismatch", "execution_result_oracle parsed hash differs from parsed execution.")
    if parsed is not None and oracle.get("parsed_status") != parsed.get("status"):
        add_issue(issues, "error", "execution_result_oracle_parsed_status_mismatch", "execution_result_oracle parsed status differs from parsed execution.")
    if parsed is not None and oracle.get("parsed_same") != parsed.get("same"):
        add_issue(issues, "error", "execution_result_oracle_parsed_same_mismatch", "execution_result_oracle parsed same differs from parsed execution.")
    verify_execution_result_case_summary_oracle_fields(
        oracle=oracle,
        parsed=parsed,
        issues=issues,
        checks=checks,
    )
    meta = as_dict(dynamic.get("meta"))
    probe_contract = as_dict(meta.get("probe_contract"))
    if probe_contract:
        if probe_contract.get("schema_version") != PROBE_CONTRACT_SCHEMA_VERSION:
            add_issue(issues, "error", "probe_contract_schema_mismatch", "probe_contract schema_version is invalid.")
        contract_hash = probe_contract.get(PROBE_CONTRACT_HASH_FIELD)
        if contract_hash is not None and contract_hash != build_probe_contract_hash(probe_contract):
            add_issue(issues, "error", "probe_contract_sha_mismatch", "probe_contract contract_sha256 differs from verifier recomputation.")
        expected_probe_contract_sha = canonical_sha256(probe_contract)
        if oracle.get("probe_contract_sha256") != expected_probe_contract_sha:
            add_issue(
                issues,
                "error",
                "execution_result_oracle_probe_contract_sha_mismatch",
                "execution_result_oracle.probe_contract_sha256 does not match current dynamic.meta.probe_contract.",
            )
    if status == "executed":
        if oracle.get("status") != "verified":
            add_issue(issues, "error", "execution_result_oracle_unverified", "executed dynamic evidence requires verified execution_result_oracle.")
        if oracle.get("final_label_available") is not True:
            add_issue(issues, "error", "execution_result_oracle_final_label_unavailable", "executed dynamic evidence requires oracle final_label_available=true.")


def verify_execution_result_case_summary_oracle_fields(
    *,
    oracle: dict[str, Any],
    parsed: dict[str, Any] | None,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    summary = parsed.get("case_summary") if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict) else {}
    if not summary:
        checks["execution_result_case_summary_absent"] += 1
        if oracle.get("case_summary_present") not in (False, None):
            add_issue(
                issues,
                "error",
                "execution_result_oracle_case_summary_presence_mismatch",
                "execution_result_oracle records case_summary_present but parsed execution has no case_summary.",
            )
        return
    checks["execution_result_case_summary_present"] += 1
    expected_fields = {
        "case_summary_present": True,
        "case_summary_status": summary.get("status"),
        "case_summary_sha256": canonical_sha256(summary),
        "case_summary_case_count": summary.get("case_count"),
        "case_summary_mismatch_count": summary.get("mismatch_count"),
        "case_summary_boundary_mismatch_count": summary.get("boundary_mismatch_count"),
        "case_summary_non_boundary_mismatch_count": summary.get("non_boundary_mismatch_count"),
        "boundary_only_divergence": summary.get("boundary_only_divergence"),
    }
    for key, expected in expected_fields.items():
        if oracle.get(key) != expected:
            add_issue(
                issues,
                "error",
                f"execution_result_oracle_{key}_mismatch",
                f"execution_result_oracle.{key} does not match parsed case_summary.",
            )
    if summary.get("status") == "verified":
        checks["execution_result_case_summary_verified"] += 1
    else:
        checks["execution_result_case_summary_unverified"] += 1
        add_issue(
            issues,
            "error",
            "execution_result_case_summary_unverified",
            "parsed case_summary must be verified when present.",
        )


def verify_probe_contract(dynamic: dict[str, Any], *, issues: list[dict[str, Any]], checks: Counter[str]) -> None:
    meta = as_dict(dynamic.get("meta"))
    probe_factory = str(meta.get("probe_factory") or "")
    probe_family = str(meta.get("probe_family") or "")
    if not probe_factory or probe_factory == "none":
        return
    checks["probe_contract_required_cards"] += 1
    contract = as_dict(meta.get("probe_contract"))
    if not contract:
        checks["probe_contract_missing"] += 1
        add_issue(
            issues,
            "warning",
            "probe_contract_missing",
            f"dynamic evidence uses probe_factory={probe_factory!r} but has no meta.probe_contract.",
        )
        return
    checks["probe_contract_present"] += 1
    if contract.get("schema_version") != PROBE_CONTRACT_SCHEMA_VERSION:
        add_issue(issues, "error", "probe_contract_schema_mismatch", "probe_contract schema_version is invalid.")
    contract_hash = contract.get(PROBE_CONTRACT_HASH_FIELD)
    if contract_hash is not None and contract_hash != build_probe_contract_hash(contract):
        add_issue(issues, "error", "probe_contract_sha_mismatch", "probe_contract contract_sha256 differs from verifier recomputation.")
    if contract.get("probe_factory") != probe_factory:
        add_issue(
            issues,
            "error",
            "probe_contract_factory_mismatch",
            f"probe_contract factory={contract.get('probe_factory')!r} expected {probe_factory!r}.",
        )
    if probe_family and contract.get("probe_family") != probe_family:
        add_issue(
            issues,
            "error",
            "probe_contract_family_mismatch",
            f"probe_contract family={contract.get('probe_family')!r} expected {probe_family!r}.",
        )
    if contract.get("deterministic") is not True:
        add_issue(issues, "error", "probe_contract_not_deterministic", "probe_contract must declare deterministic=true.")
    if contract.get("no_external_services") is not True:
        add_issue(issues, "error", "probe_contract_allows_external_services", "probe_contract must declare no_external_services=true.")
    result_fields = contract.get("result_fields") if isinstance(contract.get("result_fields"), list) else []
    for required in ["status", "same", "out_a", "out_b"]:
        if required not in result_fields:
            add_issue(
                issues,
                "error",
                "probe_contract_result_field_missing",
                f"probe_contract result_fields is missing {required!r}.",
            )
    if not contract.get("observation_kind"):
        add_issue(issues, "error", "probe_contract_observation_kind_missing", "probe_contract observation_kind is missing.")
    if not isinstance(contract.get("input_profile"), dict):
        add_issue(issues, "error", "probe_contract_input_profile_missing", "probe_contract input_profile must be an object.")
    output_sha = contract.get("probe_body_sha256")
    if output_sha is not None and not looks_like_sha256(output_sha):
        add_issue(issues, "error", "probe_contract_probe_body_sha_invalid", "probe_contract probe_body_sha256 is not a sha256 digest.")
    probe_synthesis = as_dict(dynamic.get("llm_probe_synthesis"))
    if probe_factory == "llm_probe_synthesis" and probe_synthesis.get("status") == "completed":
        payload = as_dict(probe_synthesis.get("payload"))
        expected = payload.get("probe_body_sha256")
        if expected and contract.get("probe_body_sha256") != expected:
            add_issue(
                issues,
                "error",
                "probe_contract_llm_probe_sha_mismatch",
                "LLM probe contract hash does not match payload.probe_body_sha256.",
            )
        invocation = as_dict(probe_synthesis.get("expert_invocation"))
        expected_invocation_sha = invocation.get(INVOCATION_HASH_FIELD)
        if expected_invocation_sha and contract.get("expert_invocation_sha256") != expected_invocation_sha:
            add_issue(
                issues,
                "error",
                "probe_contract_llm_probe_expert_invocation_sha_mismatch",
                "LLM probe contract expert_invocation_sha256 does not match current llm_probe_synthesis expert invocation.",
            )
    elif probe_factory == "llm_probe_synthesis":
        add_issue(
            issues,
            "error",
            "probe_contract_llm_probe_completion_missing",
            "probe_contract declares llm_probe_synthesis, but no completed llm_probe_synthesis artifact is present.",
        )
    context = as_dict(dynamic.get("llm_context_completion"))
    if probe_factory == "llm_context_completion" and context.get("status") == "completed":
        payload = as_dict(context.get("payload"))
        expected = payload.get("java_source_sha256")
        if expected and contract.get("probe_body_sha256") != expected:
            add_issue(
                issues,
                "error",
                "probe_contract_llm_context_sha_mismatch",
                "LLM context probe contract hash does not match payload.java_source_sha256.",
            )
        invocation = as_dict(context.get("expert_invocation"))
        expected_invocation_sha = invocation.get(INVOCATION_HASH_FIELD)
        if expected_invocation_sha and contract.get("expert_invocation_sha256") != expected_invocation_sha:
            add_issue(
                issues,
                "error",
                "probe_contract_llm_context_expert_invocation_sha_mismatch",
                "LLM context probe contract expert_invocation_sha256 does not match current llm_context_completion expert invocation.",
            )
    elif probe_factory == "llm_context_completion":
        add_issue(
            issues,
            "error",
            "probe_contract_llm_context_completion_missing",
            "probe_contract declares llm_context_completion, but no completed llm_context_completion artifact is present.",
        )


def verify_context_completion_contract(
    context: dict[str, Any],
    *,
    dynamic: dict[str, Any],
    source_fingerprint: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    if context.get("status") != "completed":
        return
    checks["llm_context_completion_completed"] += 1
    payload = as_dict(context.get("payload"))
    verify_expert_payload(
        payload,
        expected_contract=CONTEXT_EXPERT_CONTRACT,
        forbidden_keys=FORBIDDEN_CONTEXT_DECISION_KEYS,
        issue_prefix="context_completion",
        issues=issues,
    )
    if payload.get("validation_errors"):
        add_issue(issues, "error", "context_completion_payload_has_validation_errors", "completed context payload contains validation_errors.")
    artifact = as_dict(context.get("source_artifact"))
    if artifact or payload.get("context_payload_schema"):
        payload_schema_ok, payload_schema_reasons = verify_context_payload_schema_certificate(payload)
        checks["llm_context_payload_schema_verified" if payload_schema_ok else "llm_context_payload_schema_unverified"] += 1
        if not payload_schema_ok:
            add_issue(
                issues,
                "error",
                payload_schema_reasons[0] if payload_schema_reasons else "context_payload_schema_untrusted",
                "completed context payload failed required schema verification.",
            )
    verify_expert_invocation_contract(
        owner=context,
        payload=payload,
        dynamic_meta=as_dict(dynamic.get("meta")),
        expected_contract=CONTEXT_EXPERT_CONTRACT,
        expected_role="context_completion",
        expected_status="completed",
        output_hash_field="java_source_sha256",
        issue_prefix="context_completion",
        issues=issues,
        checks=checks,
    )
    ok, reasons = verify_source_artifact(artifact, expected_sha=payload.get("java_source_sha256"))
    checks["llm_context_source_artifact_verified" if ok else "llm_context_source_artifact_unverified"] += 1
    if not ok:
        add_issue(issues, "error", reasons[0] if reasons else "context_source_artifact_unverified", "completed context source_artifact failed verification.")
    verify_source_preservation_artifact(
        artifact,
        source_fingerprint=source_fingerprint,
        issue_prefix="context_completion",
        issues=issues,
        checks=checks,
    )
    if ok:
        source_match_ok, source_match_reasons = verify_executed_source_matches_artifact(
            dynamic,
            artifact,
            issue_prefix="context_completion",
        )
        checks["llm_context_executed_source_matches_artifact" if source_match_ok else "llm_context_executed_source_mismatch"] += 1
        if not source_match_ok:
            add_issue(
                issues,
                "error",
                source_match_reasons[0] if source_match_reasons else "context_completion_executed_source_artifact_mismatch",
                "completed context source_artifact does not match the Java source recorded in the execution certificate.",
            )
        safety_ok, safety_reasons = verify_context_source_safety_artifact(artifact)
        checks["llm_context_source_safety_verified" if safety_ok else "llm_context_source_safety_unverified"] += 1
        if not safety_ok:
            add_issue(
                issues,
                "error",
                safety_reasons[0] if safety_reasons else "context_source_safety_untrusted",
                "completed context source_artifact failed harness safety verification.",
            )
        added_context_ok, added_context_reasons = verify_context_added_context_artifact(artifact, payload)
        checks[
            "llm_context_added_context_verified"
            if added_context_ok
            else "llm_context_added_context_unverified"
        ] += 1
        if not added_context_ok:
            add_issue(
                issues,
                "error",
                added_context_reasons[0] if added_context_reasons else "context_added_context_untrusted",
                "completed context source_artifact failed added-context grounding verification.",
            )
        path_ok, path_reasons = verify_context_probe_execution_path_artifact(artifact, payload)
        checks["llm_context_probe_execution_path_verified" if path_ok else "llm_context_probe_execution_path_unverified"] += 1
        if not path_ok:
            add_issue(
                issues,
                "error",
                path_reasons[0] if path_reasons else "context_probe_execution_path_untrusted",
                "completed context source_artifact failed execution-path verification.",
            )


def verify_probe_synthesis_contract(
    probe: dict[str, Any],
    *,
    dynamic: dict[str, Any],
    source_fingerprint: dict[str, Any],
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    if probe.get("status") != "completed":
        return
    checks["llm_probe_synthesis_completed"] += 1
    payload = as_dict(probe.get("payload"))
    verify_expert_payload(
        payload,
        expected_contract=PROBE_EXPERT_CONTRACT,
        forbidden_keys=FORBIDDEN_PROBE_DECISION_KEYS,
        issue_prefix="probe_synthesis",
        issues=issues,
    )
    if payload.get("validation_errors"):
        add_issue(issues, "error", "probe_synthesis_payload_has_validation_errors", "completed probe payload contains validation_errors.")
    artifact = as_dict(probe.get("source_artifact"))
    if artifact or payload.get("probe_payload_schema"):
        payload_schema_ok, payload_schema_reasons = verify_probe_payload_schema_certificate(payload)
        checks["llm_probe_payload_schema_verified" if payload_schema_ok else "llm_probe_payload_schema_unverified"] += 1
        if not payload_schema_ok:
            add_issue(
                issues,
                "error",
                payload_schema_reasons[0] if payload_schema_reasons else "probe_payload_schema_untrusted",
                "completed probe payload failed required schema verification.",
            )
    verify_expert_invocation_contract(
        owner=probe,
        payload=payload,
        dynamic_meta=as_dict(dynamic.get("meta")),
        expected_contract=PROBE_EXPERT_CONTRACT,
        expected_role="probe_synthesis",
        expected_status="completed",
        output_hash_field="probe_body_sha256",
        issue_prefix="probe_synthesis",
        issues=issues,
        checks=checks,
    )
    ok, reasons = verify_source_artifact(artifact, expected_sha=None)
    checks["llm_probe_source_artifact_verified" if ok else "llm_probe_source_artifact_unverified"] += 1
    if not ok:
        add_issue(issues, "error", reasons[0] if reasons else "probe_source_artifact_unverified", "completed probe source_artifact failed verification.")
    verify_source_preservation_artifact(
        artifact,
        source_fingerprint=source_fingerprint,
        issue_prefix="probe_synthesis",
        issues=issues,
        checks=checks,
    )
    if ok:
        source_match_ok, source_match_reasons = verify_executed_source_matches_artifact(
            dynamic,
            artifact,
            issue_prefix="probe_synthesis",
        )
        checks["llm_probe_executed_source_matches_artifact" if source_match_ok else "llm_probe_executed_source_mismatch"] += 1
        if not source_match_ok:
            add_issue(
                issues,
                "error",
                source_match_reasons[0] if source_match_reasons else "probe_synthesis_executed_source_artifact_mismatch",
                "completed probe source_artifact does not match the Java source recorded in the execution certificate.",
            )
        binding_ok, binding_reasons = verify_probe_source_binding_artifact(artifact, payload)
        checks["llm_probe_source_binding_verified" if binding_ok else "llm_probe_source_binding_unverified"] += 1
        if not binding_ok:
            add_issue(
                issues,
                "error",
                binding_reasons[0] if binding_reasons else "probe_source_binding_untrusted",
                "completed probe source_artifact failed probe-body binding verification.",
            )


def verify_source_preservation_artifact(
    artifact: dict[str, Any],
    *,
    source_fingerprint: dict[str, Any],
    issue_prefix: str,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    preservation = as_dict(artifact.get("source_preservation"))
    if not preservation:
        checks[f"{issue_prefix}_source_preservation_missing"] += 1
        add_issue(
            issues,
            "warning",
            f"{issue_prefix}_source_preservation_missing",
            "source_artifact has no source_preservation certificate; retained source is hash-verified but original snippet retention is unaudited.",
        )
        return
    checks[f"{issue_prefix}_source_preservation_present"] += 1
    if preservation.get("schema_version") != "eviclone-source-preservation/v1":
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_preservation_schema_mismatch",
            "source_preservation schema_version is invalid.",
        )
    expected_sha = canonical_sha256({key: value for key, value in preservation.items() if key != "certificate_sha256"})
    if preservation.get("certificate_sha256") != expected_sha:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_preservation_certificate_sha_mismatch",
            "source_preservation.certificate_sha256 does not match the verifier-recomputed preservation payload.",
        )
    artifact_sha = str(artifact.get("sha256") or "")
    if preservation.get("source_sha256") != artifact_sha:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_preservation_source_sha_mismatch",
            "source_preservation.source_sha256 differs from source_artifact.sha256.",
        )
    verify_source_preservation_fingerprint_binding(
        preservation,
        source_fingerprint=source_fingerprint,
        issue_prefix=issue_prefix,
        issues=issues,
        checks=checks,
    )
    status = str(preservation.get("status") or "")
    if status in {"exact", "normalized", "identifier_supported"}:
        checks[f"{issue_prefix}_source_preservation_{status}"] += 1
    else:
        checks[f"{issue_prefix}_source_preservation_weak"] += 1
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_preservation_weak",
            f"source_preservation status={status!r}; original snippets are not sufficiently retained in the generated source.",
        )
    for side in ["snippet_a", "snippet_b"]:
        snippet = as_dict(preservation.get(side))
        if not snippet:
            add_issue(
                issues,
                "error",
                f"{issue_prefix}_source_preservation_{side}_missing",
                f"source_preservation.{side} is missing.",
            )
            continue
        if not looks_like_sha256(snippet.get("sha256")):
            add_issue(
                issues,
                "error",
                f"{issue_prefix}_source_preservation_{side}_sha_invalid",
                f"source_preservation.{side}.sha256 is missing or invalid.",
            )
        if snippet.get("nonempty") is not True:
            add_issue(
                issues,
                "error",
                f"{issue_prefix}_source_preservation_{side}_empty",
                f"source_preservation.{side} records an empty original snippet.",
            )
        exact_present = snippet.get("exact_present") is True
        normalized_present = snippet.get("normalized_present") is True
        retention = as_dict(snippet.get("identifier_retention"))
        identifier_supported = retention.get("status") == "sufficient"
        if not (exact_present or normalized_present or identifier_supported):
            add_issue(
                issues,
                "error",
                f"{issue_prefix}_source_preservation_{side}_not_retained",
                f"source_preservation.{side} is not exact, normalized, or identifier-supported.",
            )


def verify_source_preservation_fingerprint_binding(
    preservation: dict[str, Any],
    *,
    source_fingerprint: dict[str, Any],
    issue_prefix: str,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    if not source_fingerprint:
        checks[f"{issue_prefix}_source_fingerprint_missing"] += 1
        return
    expected_sha = canonical_sha256(
        {key: value for key, value in source_fingerprint.items() if key != "fingerprint_sha256"}
    )
    if source_fingerprint.get("fingerprint_sha256") != expected_sha:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_fingerprint_sha_mismatch",
            "source_fingerprint.fingerprint_sha256 does not match the verifier-recomputed source fingerprint.",
        )
    if preservation.get("pair_id") != source_fingerprint.get("pair_id"):
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_preservation_pair_id_mismatch",
            "source_preservation.pair_id differs from source_fingerprint.pair_id.",
        )
    if preservation.get("function_ids") != source_fingerprint.get("function_ids"):
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_preservation_function_ids_mismatch",
            "source_preservation.function_ids differs from source_fingerprint.function_ids.",
        )
    snippet_a = as_dict(preservation.get("snippet_a"))
    snippet_b = as_dict(preservation.get("snippet_b"))
    if snippet_a.get("sha256") != source_fingerprint.get("code_a_sha256"):
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_preservation_snippet_a_pair_hash_mismatch",
            "source_preservation.snippet_a.sha256 differs from source_fingerprint.code_a_sha256.",
        )
    if snippet_b.get("sha256") != source_fingerprint.get("code_b_sha256"):
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_source_preservation_snippet_b_pair_hash_mismatch",
            "source_preservation.snippet_b.sha256 differs from source_fingerprint.code_b_sha256.",
        )
    checks[f"{issue_prefix}_source_preservation_fingerprint_binding_checked"] += 1


def verify_expert_payload(
    payload: dict[str, Any],
    *,
    expected_contract: str,
    forbidden_keys: set[str],
    issue_prefix: str,
    issues: list[dict[str, Any]],
) -> None:
    if payload.get("expert_contract") != expected_contract:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_contract_mismatch",
            f"{issue_prefix} expert_contract={payload.get('expert_contract')!r} expected {expected_contract}.",
        )
    forbidden = sorted(item["path"] for item in find_forbidden_key_paths(payload, forbidden_keys))
    if forbidden:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_payload_has_forbidden_decision_fields",
            f"{issue_prefix} payload contains forbidden decision fields: {', '.join(forbidden)}.",
        )


def verify_expert_invocation_contract(
    *,
    owner: dict[str, Any],
    payload: dict[str, Any],
    dynamic_meta: dict[str, Any] | None = None,
    expected_contract: str,
    expected_role: str,
    expected_status: str,
    output_hash_field: str,
    issue_prefix: str,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    invocation = as_dict(owner.get("expert_invocation"))
    if not invocation:
        checks[f"{issue_prefix}_expert_invocation_missing"] += 1
        add_issue(
            issues,
            "warning",
            f"{issue_prefix}_expert_invocation_missing",
            f"{issue_prefix} completed output has no expert_invocation provenance certificate.",
        )
        return
    checks[f"{issue_prefix}_expert_invocation_present"] += 1
    if invocation.get("schema_version") != "eviclone-llm-expert-invocation/v1":
        add_issue(issues, "error", f"{issue_prefix}_expert_invocation_schema_mismatch", "expert_invocation schema_version is invalid.")
    expected_invocation_sha = build_expert_invocation_hash(invocation)
    if invocation.get(INVOCATION_HASH_FIELD) != expected_invocation_sha:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_invocation_sha_mismatch",
            "expert_invocation.invocation_sha256 does not match the verifier-recomputed certificate hash.",
        )
    if invocation.get("expert_contract") != expected_contract:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_invocation_contract_mismatch",
            f"expert_invocation contract={invocation.get('expert_contract')!r} expected {expected_contract}.",
        )
    if invocation.get("expert_role") != expected_role:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_invocation_role_mismatch",
            f"expert_invocation role={invocation.get('expert_role')!r} expected {expected_role}.",
        )
    if invocation.get("status") != expected_status:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_invocation_status_mismatch",
            f"expert_invocation status={invocation.get('status')!r} expected {expected_status}.",
        )
    expected_output_sha = str(payload.get(output_hash_field) or "")
    if expected_output_sha and invocation.get("output_sha256") != expected_output_sha:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_invocation_output_sha_mismatch",
            f"expert_invocation output_sha256 does not match payload.{output_hash_field}.",
        )
    for hash_field in ["system_prompt_sha256", "user_prompt_sha256", "prompt_pair_sha256"]:
        if not looks_like_sha256(invocation.get(hash_field)):
            add_issue(
                issues,
                "error",
                f"{issue_prefix}_expert_invocation_{hash_field}_invalid",
                f"expert_invocation.{hash_field} is missing or not a sha256 digest.",
            )
    if invocation.get("validation_passed") is not True:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_invocation_validation_not_passed",
            "completed expert output must record validation_passed=true.",
        )
    if invocation.get("validation_errors") not in (None, []):
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_invocation_has_validation_errors",
            "completed expert invocation must not retain validation errors.",
        )
    verify_expert_model_config_contract(
        invocation=invocation,
        issue_prefix=issue_prefix,
        issues=issues,
        checks=checks,
    )
    verify_expert_input_firewall_contract(
        invocation=invocation,
        dynamic_meta=dynamic_meta or {},
        expected_role=expected_role,
        issue_prefix=issue_prefix,
        issues=issues,
        checks=checks,
    )


def verify_expert_model_config_contract(
    *,
    invocation: dict[str, Any],
    issue_prefix: str,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    model_config = as_dict(invocation.get("model_config"))
    if not model_config:
        checks[f"{issue_prefix}_model_config_missing"] += 1
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_model_config_missing",
            "completed LLM expert invocation has no model_config provenance certificate.",
        )
        return
    checks[f"{issue_prefix}_model_config_present"] += 1
    if model_config.get("schema_version") != MODEL_CONFIG_SCHEMA_VERSION:
        add_issue(issues, "error", f"{issue_prefix}_expert_model_config_schema_mismatch", "model_config schema_version is invalid.")
    expected_sha = canonical_sha256({key: value for key, value in model_config.items() if key != "config_sha256"})
    if model_config.get("config_sha256") != expected_sha:
        add_issue(issues, "error", f"{issue_prefix}_expert_model_config_sha_mismatch", "model_config hash differs from verifier recomputation.")
    if model_config.get("available") is not True:
        checks[f"{issue_prefix}_model_config_unavailable"] += 1
        add_issue(
            issues,
            "warning",
            f"{issue_prefix}_expert_model_config_unavailable",
            "LLM client did not expose a structured runtime config; model/provider provenance is incomplete.",
        )
        return
    if not str(model_config.get("base_url") or ""):
        add_issue(issues, "error", f"{issue_prefix}_expert_model_config_base_url_missing", "model_config.base_url is missing.")
    if not str(model_config.get("endpoint_url") or ""):
        add_issue(issues, "error", f"{issue_prefix}_expert_model_config_endpoint_url_missing", "model_config.endpoint_url is missing.")
    endpoint_url = str(model_config.get("endpoint_url") or "")
    if model_config.get("endpoint_url_sha256") != sha256_text(endpoint_url):
        add_issue(issues, "error", f"{issue_prefix}_expert_model_config_endpoint_sha_mismatch", "model_config.endpoint_url_sha256 is invalid.")
    if model_config.get("model") != DEFAULT_MODEL:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_expert_model_config_model_mismatch",
            f"LLM expert model={model_config.get('model')!r} expected {DEFAULT_MODEL!r}.",
        )
    try:
        temperature = float(model_config.get("temperature"))
    except (TypeError, ValueError):
        add_issue(issues, "error", f"{issue_prefix}_expert_model_config_temperature_invalid", "model_config.temperature is not numeric.")
    else:
        if temperature != 0.0:
            add_issue(issues, "error", f"{issue_prefix}_expert_model_config_temperature_not_zero", "LLM expert temperature must be 0.0 for deterministic evidence construction.")
    try:
        timeout_sec = float(model_config.get("timeout_sec"))
    except (TypeError, ValueError):
        add_issue(issues, "error", f"{issue_prefix}_expert_model_config_timeout_invalid", "model_config.timeout_sec is not numeric.")
    else:
        if timeout_sec <= 0:
            add_issue(issues, "error", f"{issue_prefix}_expert_model_config_timeout_invalid", "model_config.timeout_sec must be positive.")


def verify_expert_input_firewall_contract(
    *,
    invocation: dict[str, Any],
    dynamic_meta: dict[str, Any],
    expected_role: str,
    issue_prefix: str,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    firewall = as_dict(invocation.get("input_firewall"))
    if not firewall:
        checks[f"{issue_prefix}_input_firewall_missing"] += 1
        add_issue(
            issues,
            "warning",
            f"{issue_prefix}_input_firewall_missing",
            "completed LLM expert invocation has no input_firewall certificate; prompt input leakage is unaudited.",
        )
        return
    checks[f"{issue_prefix}_input_firewall_present"] += 1
    if firewall.get("schema_version") != INPUT_FIREWALL_SCHEMA_VERSION:
        add_issue(issues, "error", f"{issue_prefix}_input_firewall_schema_mismatch", "input_firewall schema_version is invalid.")
    expected_firewall_sha = build_input_firewall_hash(firewall)
    if firewall.get(INPUT_FIREWALL_HASH_FIELD) != expected_firewall_sha:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_input_firewall_sha_mismatch",
            "input_firewall.firewall_sha256 does not match the verifier-recomputed certificate hash.",
        )
    if firewall.get("policy") != INPUT_FIREWALL_POLICY:
        add_issue(issues, "error", f"{issue_prefix}_input_firewall_policy_mismatch", "input_firewall policy is invalid.")
    if firewall.get("expert_role") != expected_role:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_input_firewall_role_mismatch",
            f"input_firewall expert_role={firewall.get('expert_role')!r} expected {expected_role}.",
        )
    if firewall.get("status") != "passed":
        add_issue(issues, "error", f"{issue_prefix}_input_firewall_not_passed", "input_firewall status must be passed.")
    if firewall.get("decision_inputs_visible") is not False:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_input_firewall_decision_inputs_visible",
            "input_firewall reports that answer-bearing decision inputs were visible to the LLM expert.",
        )
    if firewall.get("visible_sensitive_paths") not in (None, []):
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_input_firewall_visible_sensitive_paths",
            "input_firewall retains visible sensitive input paths.",
        )
    firewall_prompt_sha = firewall.get("user_prompt_sha256")
    if firewall_prompt_sha is not None and firewall_prompt_sha != invocation.get("user_prompt_sha256"):
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_input_firewall_prompt_sha_mismatch",
            "input_firewall.user_prompt_sha256 does not match expert_invocation.user_prompt_sha256.",
        )
    verify_expert_module_graph_input_binding(
        firewall=firewall,
        dynamic_meta=dynamic_meta,
        issue_prefix=issue_prefix,
        issues=issues,
        checks=checks,
    )


def verify_expert_module_graph_input_binding(
    *,
    firewall: dict[str, Any],
    dynamic_meta: dict[str, Any],
    issue_prefix: str,
    issues: list[dict[str, Any]],
    checks: Counter[str],
) -> None:
    expected = build_module_graph_input_binding(dynamic_meta)
    module_graph = as_dict(dynamic_meta.get("executable_module_graph"))
    binding = as_dict(firewall.get("module_graph_input_binding"))
    if not module_graph:
        if binding:
            checks[f"{issue_prefix}_module_graph_input_binding_unneeded"] += 1
        return
    checks[f"{issue_prefix}_module_graph_input_binding_required"] += 1
    if not binding:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_module_graph_input_binding_missing",
            "LLM expert input firewall must bind the executable_module_graph visible to the expert.",
        )
        return
    checks[f"{issue_prefix}_module_graph_input_binding_present"] += 1
    if binding.get("schema_version") != MODULE_GRAPH_INPUT_BINDING_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_module_graph_input_binding_schema_mismatch",
            "module_graph_input_binding schema_version is invalid.",
        )
    expected_binding_sha = build_module_graph_input_binding_hash(binding)
    if binding.get(MODULE_GRAPH_INPUT_BINDING_HASH_FIELD) != expected_binding_sha:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_module_graph_input_binding_sha_mismatch",
            "module_graph_input_binding self hash differs from verifier recomputation.",
        )
    if binding != expected:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_module_graph_input_binding_recomputed_mismatch",
            "module_graph_input_binding differs from verifier recomputation for dynamic.meta.executable_module_graph.",
        )
    if binding.get("llm_clone_decision_allowed") is not False:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_module_graph_input_binding_allows_llm_clone_decision",
            "module_graph_input_binding must record llm_clone_decision_allowed=false.",
        )
    if binding.get("raw_source_patch_allowed") is not False:
        add_issue(
            issues,
            "error",
            f"{issue_prefix}_module_graph_input_binding_allows_raw_source_patch",
            "module_graph_input_binding must record raw_source_patch_allowed=false.",
        )
    checks[f"{issue_prefix}_module_graph_input_binding_verified"] += 1


def build_module_graph_input_binding_hash(binding: dict[str, Any]) -> str:
    return canonical_sha256({key: value for key, value in binding.items() if key != MODULE_GRAPH_INPUT_BINDING_HASH_FIELD})


def looks_like_sha256(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text.lower())


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def string_leaves(value: Any, *, prefix: str) -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(prefix, value)]
    if isinstance(value, dict):
        leaves: list[tuple[str, str]] = []
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}"
            leaves.extend(string_leaves(child, prefix=child_prefix))
        return leaves
    if isinstance(value, list):
        leaves = []
        for index, child in enumerate(value):
            leaves.extend(string_leaves(child, prefix=f"{prefix}.{index}"))
        return leaves
    return []


def replay_source_artifact(
    artifact: dict[str, Any],
    *,
    expected_same: bool | None,
    timeout_sec: float = 8.0,
) -> dict[str, Any]:
    ok, reasons = verify_source_artifact(artifact, expected_sha=None)
    if not ok:
        return {"status": "artifact_unverified", "message": "; ".join(reasons)}
    javac = shutil.which("javac")
    java = shutil.which("java")
    if not javac or not java:
        return {"status": "tool_missing", "message": "javac/java was not found on PATH."}

    source_path = Path(str(artifact.get("path") or ""))
    source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        dst = root / "EviProbe.java"
        shutil.copy2(source_path, dst)
        try:
            compile_proc = subprocess.run(
                [javac, "-encoding", "UTF-8", str(dst.name)],
                cwd=root,
                text=True,
                capture_output=True,
                timeout=timeout_sec,
                check=False,
            )
            if compile_proc.returncode != 0:
                return {
                    "status": "compile_failed",
                    "message": "Retained EviProbe.java failed to compile during replay.",
                    "source_sha256": source_sha,
                    "compile": proc_excerpt(compile_proc),
                }
            run_proc = subprocess.run(
                [java, "-cp", str(root), "EviProbe", str(root)],
                cwd=root,
                text=True,
                capture_output=True,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {"status": "timeout", "message": f"Replay timed out after {timeout_sec}s.", "cmd": exc.cmd, "source_sha256": source_sha}
        except OSError as exc:
            return {"status": "execution_error", "message": str(exc), "source_sha256": source_sha}

    parsed = parse_probe_output(run_proc.stdout or "")
    same = parsed.get("same") if isinstance(parsed, dict) else None
    result = {
        "status": "executed",
        "source_sha256": source_sha,
        "execution": proc_excerpt(run_proc),
        "parsed": parsed,
        "expected_same": expected_same,
        "replayed_same": same,
    }
    if run_proc.returncode != 0:
        result["status"] = "execution_failed"
        result["message"] = "Retained EviProbe.java exited non-zero during replay."
    elif expected_same in (True, False):
        if same == expected_same:
            result["status"] = "matched"
            result["message"] = "Replay matched the recorded parsed.same value."
        else:
            result["status"] = "mismatch"
            result["message"] = f"Replay same={same!r} differs from recorded parsed.same={expected_same!r}."
    return result


def replayable_source_artifact(dynamic: dict[str, Any]) -> dict[str, Any]:
    probe = as_dict(dynamic.get("llm_probe_synthesis"))
    if probe.get("status") == "completed" and isinstance(probe.get("source_artifact"), dict):
        return probe["source_artifact"]
    context = as_dict(dynamic.get("llm_context_completion"))
    if context.get("status") == "completed" and isinstance(context.get("source_artifact"), dict):
        return context["source_artifact"]
    return {}


def parsed_same(dynamic: dict[str, Any]) -> bool | None:
    parsed = as_dict(as_dict(dynamic.get("execution")).get("parsed"))
    same = parsed.get("same")
    return same if same in (True, False) else None


def executable_dynamic_label(dynamic: dict[str, Any]) -> int | None:
    same = parsed_same(dynamic)
    if dynamic.get("status") != "executed":
        return None
    if same is True:
        return 1
    if same is False:
        return 0
    return None


def base_prediction(card: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    base = as_dict(card.get("base_model_prediction"))
    if base:
        return base
    return as_dict(route.get("base_prediction"))


def coerce_binary_label(value: Any) -> int | None:
    if value in (0, 1):
        return int(value)
    if isinstance(value, str) and value.strip() in {"0", "1"}:
        return int(value.strip())
    return None


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def proc_excerpt(proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[-4000:],
        "stderr": (proc.stderr or "")[-4000:],
    }


def require_trusted_dynamic(final_source: str, dynamic_trusted: bool, issues: list[dict[str, Any]]) -> None:
    if not dynamic_trusted:
        add_issue(issues, "error", f"{final_source}_requires_dynamic_trusted", f"{final_source} requires dynamic_trusted=true.")


def issue_counts_for(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(issue.get("severity") or "unknown") for issue in issues)
    counts.setdefault("error", 0)
    counts.setdefault("warning", 0)
    return dict(counts)


def compact_pair(card: dict[str, Any]) -> dict[str, Any]:
    function_ids = as_dict(card.get("function_ids"))
    return {
        "pair_id": card.get("pair_id"),
        "function_id_a": card.get("function_id_a") or function_ids.get("a"),
        "function_id_b": card.get("function_id_b") or function_ids.get("b"),
    }


def compact_verification_result(result: dict[str, Any]) -> dict[str, Any]:
    verification = result.get("verification") if isinstance(result.get("verification"), dict) else {}
    issues = verification.get("issues") if isinstance(verification.get("issues"), list) else []
    replay = verification.get("replay") if isinstance(verification.get("replay"), dict) else {}
    return {
        "index": result.get("index"),
        "pair": result.get("pair") if isinstance(result.get("pair"), dict) else {},
        "status": verification.get("status"),
        "checks": verification.get("checks") if isinstance(verification.get("checks"), dict) else {},
        "issue_counts": verification.get("issue_counts") if isinstance(verification.get("issue_counts"), dict) else {},
        "error_codes": [issue.get("code") for issue in issues if isinstance(issue, dict) and issue.get("severity") == "error"],
        "warning_codes": [issue.get("code") for issue in issues if isinstance(issue, dict) and issue.get("severity") == "warning"],
        "replay_status": replay.get("status"),
    }


def add_issue(issues: list[dict[str, Any]], severity: str, code: str, message: str) -> None:
    issues.append({"severity": severity, "code": code, "message": message})
