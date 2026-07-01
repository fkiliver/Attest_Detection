from __future__ import annotations

import hashlib
import json
from typing import Any


DYNAMIC_CONTRACT_DEPLOYMENT_POLICY_SCHEMA_VERSION = "eviclone-dynamic-contract-deployment-policy/v1"
DEPLOYMENT_POLICY_DECISION_HASH_FIELD = "decision_sha256"


def dynamic_contract_deployment_decision(
    dynamic_contracts: dict[str, Any],
    *,
    allow_dynamic_contract_issues: bool,
) -> dict[str, Any]:
    blockers = dynamic_contract_deployment_blockers(
        dynamic_contracts,
        allow_dynamic_contract_issues=allow_dynamic_contract_issues,
    )
    decision = {
        "schema_version": DYNAMIC_CONTRACT_DEPLOYMENT_POLICY_SCHEMA_VERSION,
        "policy": "verified_dynamic_evidence_contracts_required_for_ready/v1",
        "decision_owner": "programmatic_deployment_policy",
        "allow_dynamic_contract_issues": bool(allow_dynamic_contract_issues),
        "dynamic_contract_inputs_sha256": dynamic_contract_policy_inputs_sha256(dynamic_contracts),
        "blocking": bool(blockers),
        "blocker_count": len(blockers),
        "blocker_ids": [str(item.get("id") or "") for item in blockers],
        "blockers": blockers,
        "component_blocking": {
            "dynamic_contract": dynamic_contracts.get("status") != "verified",
            "dynamic_route": dynamic_route_certificates_block_deployment(dynamic_contracts),
            "architecture_contract": architecture_contracts_block_deployment(dynamic_contracts),
            "executable_fusion": fusion_decision_contracts_block_deployment(dynamic_contracts),
            "executable_evidence_integrity": executable_evidence_integrity_blocks_deployment(dynamic_contracts),
            "llm_expert_contract": llm_expert_contracts_block_deployment(dynamic_contracts),
            "runtime_fixture_contract": runtime_fixture_contracts_block_deployment(dynamic_contracts),
        },
    }
    decision[DEPLOYMENT_POLICY_DECISION_HASH_FIELD] = canonical_sha256(
        {key: value for key, value in decision.items() if key != DEPLOYMENT_POLICY_DECISION_HASH_FIELD}
    )
    return decision


def verify_dynamic_contract_deployment_decision(
    decision: dict[str, Any],
    dynamic_contracts: dict[str, Any],
    *,
    allow_dynamic_contract_issues: bool,
) -> tuple[bool, list[str]]:
    if not isinstance(decision, dict) or not decision:
        return False, ["deployment_policy_decision_missing"]
    reasons: list[str] = []
    if decision.get("schema_version") != DYNAMIC_CONTRACT_DEPLOYMENT_POLICY_SCHEMA_VERSION:
        reasons.append("deployment_policy_decision_schema_mismatch")
    if decision.get("decision_owner") != "programmatic_deployment_policy":
        reasons.append("deployment_policy_decision_owner_mismatch")
    expected_inputs_sha = dynamic_contract_policy_inputs_sha256(dynamic_contracts)
    if decision.get("dynamic_contract_inputs_sha256") != expected_inputs_sha:
        reasons.append("deployment_policy_decision_inputs_sha_mismatch")
    expected_decision = dynamic_contract_deployment_decision(
        dynamic_contracts,
        allow_dynamic_contract_issues=allow_dynamic_contract_issues,
    )
    actual_sha = canonical_sha256(
        {key: value for key, value in decision.items() if key != DEPLOYMENT_POLICY_DECISION_HASH_FIELD}
    )
    if decision.get(DEPLOYMENT_POLICY_DECISION_HASH_FIELD) != actual_sha:
        reasons.append("deployment_policy_decision_sha_mismatch")
    if decision.get(DEPLOYMENT_POLICY_DECISION_HASH_FIELD) != expected_decision.get(DEPLOYMENT_POLICY_DECISION_HASH_FIELD):
        reasons.append("deployment_policy_decision_recomputed_sha_mismatch")
    for key in [
        "policy",
        "allow_dynamic_contract_issues",
        "blocking",
        "blocker_count",
        "blocker_ids",
        "blockers",
        "component_blocking",
    ]:
        if decision.get(key) != expected_decision.get(key):
            reasons.append(f"deployment_policy_decision_{key}_mismatch")
    return not reasons, reasons or ["deployment_policy_decision_verified"]


def dynamic_contract_policy_inputs_sha256(dynamic_contracts: dict[str, Any]) -> str:
    return canonical_sha256(
        {
            "status": dynamic_contracts.get("status"),
            "issue_counts": dynamic_contracts.get("issue_counts"),
            "dynamic_route_accounting": dynamic_contracts.get("dynamic_route_accounting"),
            "architecture_contract_accounting": dynamic_contracts.get("architecture_contract_accounting"),
            "fusion_decision_accounting": dynamic_contracts.get("fusion_decision_accounting"),
            "executable_evidence_integrity_accounting": dynamic_contracts.get("executable_evidence_integrity_accounting"),
            "llm_expert_contract_accounting": dynamic_contracts.get("llm_expert_contract_accounting"),
            "runtime_fixture_accounting": dynamic_contracts.get("runtime_fixture_accounting"),
        }
    )


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def dynamic_contracts_block_deployment(
    dynamic_contracts: dict[str, Any],
    *,
    allow_dynamic_contract_issues: bool,
) -> bool:
    return bool(dynamic_contract_deployment_decision(dynamic_contracts, allow_dynamic_contract_issues=allow_dynamic_contract_issues)["blocking"])


def dynamic_contract_deployment_blockers(
    dynamic_contracts: dict[str, Any],
    *,
    allow_dynamic_contract_issues: bool,
) -> list[dict[str, Any]]:
    if allow_dynamic_contract_issues:
        return []
    blockers: list[dict[str, Any]] = []
    if dynamic_contracts.get("status") != "verified":
        blockers.append(
            blocker(
                "dynamic_contract_status_not_verified",
                "dynamic_contract",
                status=dynamic_contracts.get("status"),
            )
        )
    if dynamic_route_certificates_block_deployment(dynamic_contracts):
        blockers.append(route_certificate_blocker(dynamic_contracts))
    if architecture_contracts_block_deployment(dynamic_contracts):
        blockers.append(accounting_blocker("architecture_contract_blocking", "architecture_contract", dynamic_contracts.get("architecture_contract_accounting")))
    if fusion_decision_contracts_block_deployment(dynamic_contracts):
        blockers.append(accounting_blocker("fusion_decision_contract_blocking", "executable_fusion", dynamic_contracts.get("fusion_decision_accounting")))
    if executable_evidence_integrity_blocks_deployment(dynamic_contracts):
        blockers.append(
            accounting_blocker(
                "executable_evidence_integrity_blocking",
                "executable_evidence_integrity",
                dynamic_contracts.get("executable_evidence_integrity_accounting"),
            )
        )
    if llm_expert_contracts_block_deployment(dynamic_contracts):
        blockers.append(accounting_blocker("llm_expert_contract_blocking", "llm_expert_contract", dynamic_contracts.get("llm_expert_contract_accounting")))
    if runtime_fixture_contracts_block_deployment(dynamic_contracts):
        blockers.append(accounting_blocker("runtime_fixture_contract_blocking", "runtime_fixture_contract", dynamic_contracts.get("runtime_fixture_accounting")))
    return blockers


def blocker(blocker_id: str, component: str, **detail: Any) -> dict[str, Any]:
    return {
        "id": blocker_id,
        "component": component,
        "detail": {key: value for key, value in detail.items() if value is not None},
    }


def accounting_blocker(blocker_id: str, component: str, accounting: Any) -> dict[str, Any]:
    detail: dict[str, Any] = {}
    if isinstance(accounting, dict):
        for key, value in accounting.items():
            if isinstance(value, (int, float, str, bool)) and value not in (0, 0.0, "", False):
                detail[key] = value
    return blocker(blocker_id, component, **detail)


def route_certificate_blocker(dynamic_contracts: dict[str, Any]) -> dict[str, Any]:
    accounting = dynamic_contracts.get("dynamic_route_accounting")
    if not isinstance(accounting, dict):
        return blocker("dynamic_route_certificate_blocking", "dynamic_route")
    fields = [
        "route_cards",
        "missing_route_decision_certificate",
        "unverified_route_decision_certificate",
        "pass_through",
        "verified_base_model_passthrough_certificate",
        "missing_base_model_passthrough_certificate",
        "unverified_base_model_passthrough_certificate",
        "learned_route_cards",
        "missing_learned_route_model_certificate",
        "unverified_learned_route_model_certificate",
        "missing_learned_route_score_certificate",
        "unverified_learned_route_score_certificate",
    ]
    return blocker(
        "dynamic_route_certificate_blocking",
        "dynamic_route",
        **{key: accounting.get(key) for key in fields},
    )


def dynamic_route_certificates_block_deployment(dynamic_contracts: dict[str, Any]) -> bool:
    accounting = dynamic_contracts.get("dynamic_route_accounting")
    if not isinstance(accounting, dict):
        return False
    route_cards = int(accounting.get("route_cards") or 0)
    if route_cards <= 0:
        return False
    missing = int(accounting.get("missing_route_decision_certificate") or 0)
    unverified = int(accounting.get("unverified_route_decision_certificate") or 0)
    if missing + unverified > 0:
        return True
    pass_through = int(accounting.get("pass_through") or 0)
    if pass_through > 0:
        verified_passthrough = int(accounting.get("verified_base_model_passthrough_certificate") or 0)
        if verified_passthrough < pass_through:
            return True
        required_zero_passthrough = [
            "missing_base_model_passthrough_certificate",
            "unverified_base_model_passthrough_certificate",
        ]
        if any(int(accounting.get(key) or 0) > 0 for key in required_zero_passthrough):
            return True
    learned_route_cards = int(accounting.get("learned_route_cards") or 0)
    if learned_route_cards <= 0:
        return False
    required_verified = [
        "verified_learned_route_model_certificate",
        "verified_learned_route_score_certificate",
    ]
    if any(int(accounting.get(key) or 0) < learned_route_cards for key in required_verified):
        return True
    required_zero = [
        "missing_learned_route_model_certificate",
        "unverified_learned_route_model_certificate",
        "missing_learned_route_score_certificate",
        "unverified_learned_route_score_certificate",
    ]
    return any(int(accounting.get(key) or 0) > 0 for key in required_zero)


def architecture_contracts_block_deployment(dynamic_contracts: dict[str, Any]) -> bool:
    accounting = dynamic_contracts.get("architecture_contract_accounting")
    if not isinstance(accounting, dict):
        return False
    routed_cards = int(accounting.get("routed_cards") or 0)
    if routed_cards <= 0:
        return False
    required_zero = [
        "missing_pipeline_contract",
        "missing_final_decision_binding",
        "final_decision_binding_schema_invalid",
        "final_decision_binding_self_hash_unverified",
        "final_decision_binding_recomputed_mismatch",
        "missing_component_interaction_contract",
        "component_interaction_schema_invalid",
        "component_interaction_self_hash_unverified",
        "pipeline_contract_llm_final_decision_allowed_violations",
        "deployable_final_sources_include_no_reliable_label",
        "llm_clone_label_output_allowed_violations",
        "llm_final_decision_output_allowed_violations",
        "llm_component_final_decision_permission_violations",
        "final_decision_components_mismatch_route",
        "bounded_expert_components_mismatch_route",
        "unauthorized_bounded_expert_artifact_permission_violations",
        "malformed_component_permission",
    ]
    if any(int(accounting.get(key) or 0) > 0 for key in required_zero):
        return True
    if int(accounting.get("final_decision_binding_verified") or 0) < routed_cards:
        return True
    clean_cards = int(accounting.get("clean_component_interaction_contract_cards") or 0)
    interaction_cards = int(accounting.get("component_interaction_contract_cards") or 0)
    matched = int(accounting.get("final_decision_components_match_route") or 0)
    bounded_matched = int(accounting.get("bounded_expert_components_match_route") or 0)
    return (
        interaction_cards < routed_cards
        or clean_cards < routed_cards
        or matched < routed_cards
        or bounded_matched < routed_cards
    )


def fusion_decision_contracts_block_deployment(dynamic_contracts: dict[str, Any]) -> bool:
    accounting = dynamic_contracts.get("fusion_decision_accounting")
    if not isinstance(accounting, dict):
        return False
    fusion_cards = int(accounting.get("fusion_cards") or 0)
    if fusion_cards <= 0:
        return False
    if int(accounting.get("missing_decision_accounting") or 0) > 0:
        return True
    accounted_cards = int(accounting.get("accounted_cards") or 0)
    if accounted_cards < fusion_cards:
        return True
    if int(accounting.get("no_reliable_label") or 0) > 0:
        return True
    allowed_sources = {
        "trusted_executable_override",
        "trusted_executable_confirmation",
        "trusted_executable_without_base_prediction",
        "base_model_passthrough_after_untrusted_dynamic",
    }
    final_sources = accounting.get("final_source_counts")
    if not isinstance(final_sources, dict):
        return True
    return any(str(source) not in allowed_sources for source in final_sources)


def executable_evidence_integrity_blocks_deployment(dynamic_contracts: dict[str, Any]) -> bool:
    accounting = dynamic_contracts.get("executable_evidence_integrity_accounting")
    if not isinstance(accounting, dict):
        return False
    required_artifacts = int(accounting.get("completed_expert_source_artifacts_required") or 0)
    if required_artifacts > 0:
        required_equal = [
            "source_artifact_verified",
            "source_artifact_retained",
            "source_preservation_verified",
            "executed_source_matches_artifact",
        ]
        if any(int(accounting.get(key) or 0) < required_artifacts for key in required_equal):
            return True
        required_zero = [
            "source_artifact_missing",
            "source_artifact_unverified",
            "source_artifact_not_retained",
            "source_artifact_certificate_missing",
            "source_preservation_missing",
            "source_preservation_unverified",
            "executed_source_mismatch",
        ]
        if any(int(accounting.get(key) or 0) > 0 for key in required_zero):
            return True
    component_counts = accounting.get("component_counts") if isinstance(accounting.get("component_counts"), dict) else {}
    context_completion_count = int(component_counts.get("context_completion") or 0)
    if context_completion_count > 0:
        required_context_verified = [
            "context_source_safety_verified",
            "context_added_context_verified",
            "context_probe_execution_path_verified",
        ]
        if any(int(accounting.get(key) or 0) < context_completion_count for key in required_context_verified):
            return True
    probe_synthesis_count = int(component_counts.get("probe_synthesis") or 0)
    if probe_synthesis_count > 0 and int(accounting.get("probe_source_binding_verified") or 0) < probe_synthesis_count:
        return True
    required_zero_expert_bindings = [
        "context_source_safety_unverified",
        "context_added_context_unverified",
        "context_probe_execution_path_unverified",
        "probe_source_binding_unverified",
    ]
    if any(int(accounting.get(key) or 0) > 0 for key in required_zero_expert_bindings):
        return True
    adequacy_required = int(accounting.get("probe_adequacy_required_cards") or 0)
    if adequacy_required <= 0:
        return False
    if int(accounting.get("probe_adequacy_verified") or 0) < adequacy_required:
        return True
    return any(int(accounting.get(key) or 0) > 0 for key in ["probe_adequacy_missing", "probe_adequacy_unverified"])


def llm_expert_contracts_block_deployment(dynamic_contracts: dict[str, Any]) -> bool:
    accounting = dynamic_contracts.get("llm_expert_contract_accounting")
    if not isinstance(accounting, dict):
        return False
    expert_outputs = int(accounting.get("expert_outputs") or 0)
    if expert_outputs <= 0:
        return False
    if int(accounting.get("clone_label_output_allowed_violations") or 0):
        return True
    if int(accounting.get("final_decision_allowed_violations") or 0):
        return True
    if int(accounting.get("free_text_decision_language_violations") or 0):
        return True
    required_verified = [
        "payload_schema_verified",
        "expert_invocation_verified",
        "input_firewall_verified",
        "model_config_verified",
    ]
    return any(int(accounting.get(key) or 0) < expert_outputs for key in required_verified)


def runtime_fixture_contracts_block_deployment(dynamic_contracts: dict[str, Any]) -> bool:
    accounting = dynamic_contracts.get("runtime_fixture_accounting")
    if not isinstance(accounting, dict):
        return False
    fixture_bindings = int(accounting.get("fixture_bindings") or 0)
    if fixture_bindings <= 0:
        return False
    cards_with_fixtures = int(accounting.get("cards_with_runtime_fixtures") or 0)
    clean_cards = int(accounting.get("clean_runtime_fixture_cards") or 0)
    if clean_cards < cards_with_fixtures:
        return True
    required_zero = [
        "framework_contract_missing",
        "top_level_manifest_missing",
        "certificate_manifest_missing",
        "sandbox_manifest_missing",
        "fixture_schema_unverified",
        "fixture_hash_missing",
        "fixture_hash_mismatch",
        "nondeterministic_fixture_manifests",
        "external_service_fixture_manifests",
        "top_level_certificate_mismatch",
        "certificate_sandbox_mismatch",
    ]
    return any(int(accounting.get(key) or 0) > 0 for key in required_zero)
