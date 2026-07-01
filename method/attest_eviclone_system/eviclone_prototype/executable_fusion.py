from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import DEFAULT_MODEL
from .context_completion import (
    CONTEXT_ADDED_CONTEXT_HASH_FIELD,
    CONTEXT_ADDED_CONTEXT_SCHEMA_VERSION,
    CONTEXT_ALLOWED_OUTPUT,
    CONTEXT_COMPONENT_ROLE,
    CONTEXT_EXPERT_CONTRACT,
    CONTEXT_OUTPUT_KIND,
    CONTEXT_PAYLOAD_SCHEMA_VERSION,
    CONTEXT_PROBE_EXECUTION_PATH_SCHEMA_VERSION,
    CONTEXT_SOURCE_SAFETY_SCHEMA_VERSION,
    build_context_added_context_certificate,
    build_context_payload_schema_certificate,
    build_context_probe_execution_path_certificate,
    build_context_source_safety_certificate,
)
from .dynamic_router import BaseModelPrediction, clamp01
from .evidence import VERDICT_TO_LABEL, append_reason, safe_float
from .executor import (
    EXECUTION_RESULT_ORACLE_SCHEMA_VERSION,
    DYNAMIC_OUTCOME_CERTIFICATE_SCHEMA_VERSION,
    DYNAMIC_OUTCOME_HASH_FIELD,
    FRAMEWORK_MOCK_CONTRACT_HASH_FIELD,
    FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
    JAVA_EXECUTION_CERTIFICATE_SCHEMA_VERSION,
    JAVA_EXECUTION_SANDBOX_SCHEMA_VERSION,
    JAVA_TOOLCHAIN_CERTIFICATE_SCHEMA_VERSION,
    JAVA_TOOLCHAIN_HASH_FIELD,
    PROBE_ADEQUACY_HASH_FIELD,
    PROBE_ADEQUACY_SCHEMA_VERSION,
    RUNTIME_SOURCE_SAFETY_SCHEMA_VERSION,
    RUNTIME_FIXTURE_HASH_FIELD,
    RUNTIME_FIXTURE_SPECS,
    SOURCE_ARTIFACT_HASH_FIELD,
    SOURCE_ARTIFACT_SCHEMA_VERSION,
    PROBE_CONTRACT_HASH_FIELD,
    PROBE_CONTRACT_SCHEMA_VERSION,
    build_runtime_fixture_hash,
    build_framework_mock_contract_hash,
    build_dynamic_outcome_certificate,
    build_dynamic_outcome_certificate_hash,
    build_java_toolchain_certificate_hash,
    build_probe_adequacy_certificate,
    build_probe_adequacy_certificate_hash,
    build_probe_contract_hash,
    build_source_artifact_hash,
    count_probe_result_lines,
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
)
from .probe_synthesis import (
    PROBE_ALLOWED_OUTPUT,
    PROBE_COMPONENT_ROLE,
    PROBE_EXPERT_CONTRACT,
    PROBE_OUTPUT_KIND,
    PROBE_PAYLOAD_SCHEMA_VERSION,
    PROBE_SOURCE_BINDING_SCHEMA_VERSION,
    build_probe_payload_schema_certificate,
    build_probe_source_binding_certificate,
)
from .probe_planner import (
    MODULE_PROBE_PLAN_HASH_FIELD,
    MODULE_PROBE_PLAN_SCHEMA_VERSION,
    verify_module_probe_plan,
)


EXECUTABLE_FUSION_CERTIFICATE_SCHEMA_VERSION = "eviclone-executable-fusion-certificate/v1"
FUSION_DECISION_ACCOUNTING_SCHEMA_VERSION = "eviclone-fusion-decision-accounting/v1"
FUSION_POLICY = "routed_executable_evidence_fusion/v1"


@dataclass(frozen=True)
class ExecutableFusionCertificate:
    policy: str
    final_label: int | None
    final_source: str
    dynamic_label: int | None
    dynamic_trusted: bool
    base_label: int | None
    reasons: list[str]
    trust_dependencies: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        certificate = {
            "schema_version": EXECUTABLE_FUSION_CERTIFICATE_SCHEMA_VERSION,
            "policy": self.policy,
            "final_label": self.final_label,
            "final_source": self.final_source,
            "dynamic_label": self.dynamic_label,
            "dynamic_trusted": self.dynamic_trusted,
            "base_label": self.base_label,
            "reasons": self.reasons,
            "trust_dependencies": self.trust_dependencies,
            "decision_accounting": build_fusion_decision_accounting(
                final_label=self.final_label,
                final_source=self.final_source,
                dynamic_label=self.dynamic_label,
                dynamic_trusted=self.dynamic_trusted,
                base_label=self.base_label,
            ),
        }
        certificate["fusion_sha256"] = build_executable_fusion_certificate_hash(certificate)
        return certificate


def apply_executable_fusion(
    card: dict[str, Any],
    *,
    base_prediction: BaseModelPrediction | None,
) -> dict[str, Any]:
    """Fuse routed executable evidence without asking the LLM for a final label.

    The only branch allowed to override the base model here is a trusted Java
    execution result. LLM context completion is treated as an expert-produced
    artifact that must pass validation before the execution result can be used.
    """
    dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    dynamic_label = executable_dynamic_label(dynamic)
    source_fingerprint = card.get("source_fingerprint") if isinstance(card.get("source_fingerprint"), dict) else None
    source_fingerprint_ok, source_fingerprint_reasons = verify_source_fingerprint_matches_card(card, source_fingerprint)
    trusted, trust_reasons = trusted_executable_evidence(dynamic, source_fingerprint=source_fingerprint)
    if not source_fingerprint_ok:
        trusted = False
        trust_reasons = source_fingerprint_reasons
    base_label = base_prediction.label if base_prediction and base_prediction.label in (0, 1) else None
    reasons = list(trust_reasons)

    if dynamic_label in (0, 1) and trusted:
        if base_label in (0, 1) and dynamic_label != base_label:
            final_source = "trusted_executable_override"
            reasons.append("trusted_executable_result_conflicts_with_base_model")
        elif base_label in (0, 1):
            final_source = "trusted_executable_confirmation"
            reasons.append("trusted_executable_result_confirms_base_model")
        else:
            final_source = "trusted_executable_without_base_prediction"
            reasons.append("trusted_executable_result_used_without_base_model")
        final_label = int(dynamic_label)
    elif base_label in (0, 1):
        final_source = "base_model_passthrough_after_untrusted_dynamic"
        final_label = int(base_label)
        reasons.append("dynamic_evidence_not_trusted_keep_base_model")
    else:
        final_source = "no_reliable_final_label"
        final_label = None
        reasons.append("neither_base_model_nor_trusted_executable_label_available")

    certificate = ExecutableFusionCertificate(
        policy=FUSION_POLICY,
        final_label=final_label,
        final_source=final_source,
        dynamic_label=dynamic_label,
        dynamic_trusted=trusted,
        base_label=base_label,
        reasons=dedupe(reasons),
        trust_dependencies=build_fusion_trust_dependencies(dynamic, source_fingerprint=source_fingerprint),
    )
    return apply_certificate(card, certificate, base_prediction=base_prediction)


def build_executable_fusion_certificate_hash(fusion: dict[str, Any]) -> str:
    return canonical_sha256({key: value for key, value in fusion.items() if key != "fusion_sha256"})


def build_fusion_decision_accounting(
    *,
    final_label: int | None,
    final_source: str,
    dynamic_label: int | None,
    dynamic_trusted: bool,
    base_label: int | None,
) -> dict[str, Any]:
    override_eligible = bool(dynamic_trusted and dynamic_label in (0, 1))
    accounting = {
        "schema_version": FUSION_DECISION_ACCOUNTING_SCHEMA_VERSION,
        "policy": FUSION_POLICY,
        "decision_owner": "executable_fusion",
        "programmatic_fusion_only": True,
        "llm_final_decision_allowed": False,
        "dynamic_trusted": bool(dynamic_trusted),
        "dynamic_label": dynamic_label if dynamic_label in (0, 1) else None,
        "base_label": base_label if base_label in (0, 1) else None,
        "final_label": final_label if final_label in (0, 1) else None,
        "final_source": final_source,
        "dynamic_override_eligible": override_eligible,
        "override_applied": final_source == "trusted_executable_override",
        "confirmation_applied": final_source == "trusted_executable_confirmation",
        "trusted_without_base_applied": final_source == "trusted_executable_without_base_prediction",
        "base_passthrough_applied": final_source == "base_model_passthrough_after_untrusted_dynamic",
        "no_reliable_label": final_source == "no_reliable_final_label",
    }
    accounting["accounting_sha256"] = canonical_sha256(
        {key: value for key, value in accounting.items() if key != "accounting_sha256"}
    )
    return accounting


def executable_dynamic_label(dynamic: dict[str, Any]) -> int | None:
    parsed = parsed_execution(dynamic)
    if dynamic.get("status") != "executed" or not isinstance(parsed, dict):
        return None
    parsed_status = str(parsed.get("status") or "").strip().lower()
    if parsed_status in {"compile_only", "inconclusive", "not_recoverable"}:
        return None
    same = parsed.get("same")
    if same is True:
        return 1
    if same is False:
        return 0
    return None


def trusted_executable_evidence(
    dynamic: dict[str, Any],
    *,
    source_fingerprint: dict[str, Any] | None = None,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    parsed = parsed_execution(dynamic)
    if dynamic.get("status") != "executed":
        return False, [f"dynamic_status_not_executed:{dynamic.get('status') or 'missing'}"]
    if not isinstance(parsed, dict):
        return False, ["missing_parsed_execution_result"]
    if parsed.get("same") not in (True, False):
        return False, ["parsed_execution_missing_boolean_same"]
    compile_info = dynamic.get("compile") if isinstance(dynamic.get("compile"), dict) else {}
    if compile_info and compile_info.get("returncode") not in (0, "0", None):
        return False, ["compile_returncode_not_success"]
    certificate_ok, certificate_reasons = verify_java_execution_certificate_for_trust(dynamic)
    if not certificate_ok:
        return False, certificate_reasons
    reasons.extend(certificate_reasons)
    module_probe_ok, module_probe_reasons = verify_module_probe_plan_for_trust(dynamic)
    if not module_probe_ok:
        return False, module_probe_reasons
    reasons.extend(module_probe_reasons)

    probe_synthesis = dynamic.get("llm_probe_synthesis")
    used_llm_probe_synthesis = isinstance(probe_synthesis, dict) and probe_synthesis.get("status") == "completed"
    if used_llm_probe_synthesis:
        payload = probe_synthesis.get("payload") if isinstance(probe_synthesis.get("payload"), dict) else {}
        artifact = probe_synthesis.get("source_artifact") if isinstance(probe_synthesis.get("source_artifact"), dict) else {}
        artifact_ok, artifact_reasons = verify_source_artifact(artifact, expected_sha=None)
        if not artifact_ok:
            return False, artifact_reasons
        reasons.extend(artifact_reasons)
        source_match_ok, source_match_reasons = verify_executed_source_matches_artifact(
            dynamic,
            artifact,
            issue_prefix="probe_synthesis",
        )
        if not source_match_ok:
            return False, source_match_reasons
        reasons.extend(source_match_reasons)
        preservation_ok, preservation_reasons = verify_source_preservation_certificate(
            artifact,
            source_fingerprint=source_fingerprint,
        )
        if not preservation_ok:
            return False, preservation_reasons
        reasons.extend(preservation_reasons)
        if payload.get("validation_errors"):
            return False, ["probe_synthesis_payload_has_validation_errors"]
        payload_schema_ok, payload_schema_reasons = verify_probe_payload_schema_certificate(payload)
        if not payload_schema_ok:
            return False, payload_schema_reasons
        reasons.extend(payload_schema_reasons)
        invocation_ok, invocation_reasons = verify_llm_expert_invocation_output(
            probe_synthesis.get("expert_invocation"),
            issue_prefix="probe_synthesis",
            expected_role="probe_synthesis",
            expected_contract="probe_body_only_no_clone_judgment/v1",
            expected_output_kind="probe_body",
            expected_output_sha=payload.get("probe_body_sha256"),
        )
        if not invocation_ok:
            return False, invocation_reasons
        reasons.extend(invocation_reasons)
        binding_ok, binding_reasons = verify_probe_source_binding_artifact(artifact, payload)
        if not binding_ok:
            return False, binding_reasons
        reasons.extend(binding_reasons)
        firewall_ok, firewall_reasons = verify_llm_input_firewall(
            probe_synthesis.get("expert_invocation"),
            issue_prefix="probe_synthesis",
        )
        if not firewall_ok:
            return False, firewall_reasons
        reasons.extend(firewall_reasons)
        model_config_ok, model_config_reasons = verify_llm_model_config(
            probe_synthesis.get("expert_invocation"),
            issue_prefix="probe_synthesis",
        )
        if not model_config_ok:
            return False, model_config_reasons
        reasons.extend(model_config_reasons)
        reasons.append("trusted_llm_probe_synthesis_with_verified_executed_source_artifact_preserved_snippets_probe_binding_input_firewall_and_model_config")

    context = dynamic.get("llm_context_completion")
    if not isinstance(context, dict) or context.get("status") in {None, "none"}:
        if not used_llm_probe_synthesis:
            reasons.append("trusted_builtin_or_original_harness")
        if boundary_only_divergence(dynamic):
            reasons.append("boundary_only_divergence_not_decisive_for_override")
            return False, reasons
        return True, reasons
    if context.get("status") != "completed":
        return False, [f"context_completion_not_completed:{context.get('status') or 'missing'}"]

    payload = context.get("payload") if isinstance(context.get("payload"), dict) else {}
    preservation = payload.get("semantic_preservation") if isinstance(payload.get("semantic_preservation"), dict) else {}
    level = str(preservation.get("level") or "").strip().lower()
    if level == "low":
        return False, ["context_semantic_preservation_low"]
    changed = preservation.get("changed_original_logic")
    if changed is True or str(changed).strip().lower() in {"true", "yes", "1"}:
        return False, ["context_changed_original_logic"]
    if payload.get("validation_errors"):
        return False, ["context_payload_has_validation_errors"]
    payload_schema_ok, payload_schema_reasons = verify_context_payload_schema_certificate(payload)
    if not payload_schema_ok:
        return False, payload_schema_reasons

    artifact = context.get("source_artifact") if isinstance(context.get("source_artifact"), dict) else {}
    artifact_ok, artifact_reasons = verify_source_artifact(artifact, expected_sha=payload.get("java_source_sha256"))
    if not artifact_ok:
        return False, artifact_reasons
    source_match_ok, source_match_reasons = verify_executed_source_matches_artifact(
        dynamic,
        artifact,
        issue_prefix="context_completion",
    )
    if not source_match_ok:
        return False, source_match_reasons
    preservation_ok, preservation_reasons = verify_source_preservation_certificate(
        artifact,
        source_fingerprint=source_fingerprint,
    )
    if not preservation_ok:
        return False, preservation_reasons
    safety_ok, safety_reasons = verify_context_source_safety_artifact(artifact)
    if not safety_ok:
        return False, safety_reasons
    added_context_ok, added_context_reasons = verify_context_added_context_artifact(artifact, payload)
    if not added_context_ok:
        return False, added_context_reasons
    execution_path_ok, execution_path_reasons = verify_context_probe_execution_path_artifact(artifact, payload)
    if not execution_path_ok:
        return False, execution_path_reasons
    invocation_ok, invocation_reasons = verify_llm_expert_invocation_output(
        context.get("expert_invocation"),
        issue_prefix="context_completion",
        expected_role="context_completion",
        expected_contract="context_completion_only_no_clone_judgment/v1",
        expected_output_kind="java_source",
        expected_output_sha=payload.get("java_source_sha256"),
    )
    if not invocation_ok:
        return False, invocation_reasons
    firewall_ok, firewall_reasons = verify_llm_input_firewall(
        context.get("expert_invocation"),
        issue_prefix="context_completion",
    )
    if not firewall_ok:
        return False, firewall_reasons
    model_config_ok, model_config_reasons = verify_llm_model_config(
        context.get("expert_invocation"),
        issue_prefix="context_completion",
    )
    if not model_config_ok:
        return False, model_config_reasons

    reasons.extend(artifact_reasons)
    reasons.extend(source_match_reasons)
    reasons.extend(preservation_reasons)
    reasons.extend(payload_schema_reasons)
    reasons.extend(invocation_reasons)
    reasons.extend(safety_reasons)
    reasons.extend(added_context_reasons)
    reasons.extend(execution_path_reasons)
    reasons.extend(firewall_reasons)
    reasons.extend(model_config_reasons)
    reasons.append("trusted_llm_completed_context_with_verified_executed_safe_source_artifact_preserved_snippets_execution_path_input_firewall_and_model_config")
    if boundary_only_divergence(dynamic):
        reasons.append("boundary_only_divergence_not_decisive_for_override")
        return False, reasons
    return True, reasons


def verify_module_probe_plan_for_trust(dynamic: dict[str, Any]) -> tuple[bool, list[str]]:
    meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    module_graph = meta.get("executable_module_graph") if isinstance(meta.get("executable_module_graph"), dict) else {}
    if not module_graph:
        return True, ["module_probe_plan_not_required_without_executable_module_graph"]
    plan = meta.get("module_probe_plan") if isinstance(meta.get("module_probe_plan"), dict) else {}
    if not plan:
        return False, ["module_probe_plan_missing_for_executable_module_graph"]
    probe_contract = meta.get("probe_contract") if isinstance(meta.get("probe_contract"), dict) else {}
    verification = verify_module_probe_plan(
        plan,
        executable_module_graph=module_graph,
        probe_contract=probe_contract,
    )
    if verification.get("status") != "verified":
        issues = [str(issue) for issue in verification.get("issues") or []]
        return False, [f"module_probe_plan_untrusted:{'|'.join(issues) or 'unknown_issue'}"]

    certificate = dynamic.get("execution_certificate") if isinstance(dynamic.get("execution_certificate"), dict) else {}
    probe_cert = certificate.get("probe") if isinstance(certificate.get("probe"), dict) else {}
    if certificate and probe_cert:
        plan_sha = canonical_sha256(plan)
        if probe_cert.get("module_probe_plan_present") is not True:
            return False, ["java_execution_certificate_module_probe_plan_missing"]
        if probe_cert.get("module_probe_plan_sha256") != plan_sha:
            return False, ["java_execution_certificate_module_probe_plan_sha_mismatch"]
        if probe_cert.get("module_probe_plan_self_hash") != plan.get(MODULE_PROBE_PLAN_HASH_FIELD):
            return False, ["java_execution_certificate_module_probe_plan_self_hash_mismatch"]

    risk = plan.get("risk") if isinstance(plan.get("risk"), dict) else {}
    risk_level = str(risk.get("level") or "unknown").strip().lower()
    uncovered = [str(item) for item in risk.get("uncovered_obligations") or [] if str(item)]
    if risk_level == "high":
        detail = "|".join(uncovered) if uncovered else "unknown_obligation"
        return False, [f"module_probe_plan_high_risk_uncovered_obligations:{detail}"]
    return True, [
        "module_probe_plan_verified_for_trust",
        f"module_probe_plan_risk_{risk_level or 'unknown'}",
    ]


def module_probe_plan_dependency_summary(dynamic: dict[str, Any]) -> dict[str, Any]:
    meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    module_graph = meta.get("executable_module_graph") if isinstance(meta.get("executable_module_graph"), dict) else {}
    plan = meta.get("module_probe_plan") if isinstance(meta.get("module_probe_plan"), dict) else {}
    probe_contract = meta.get("probe_contract") if isinstance(meta.get("probe_contract"), dict) else {}
    certificate = dynamic.get("execution_certificate") if isinstance(dynamic.get("execution_certificate"), dict) else {}
    probe_cert = certificate.get("probe") if isinstance(certificate.get("probe"), dict) else {}
    trust_ok, trust_reasons = verify_module_probe_plan_for_trust(dynamic)
    verification = (
        verify_module_probe_plan(plan, executable_module_graph=module_graph, probe_contract=probe_contract)
        if plan and module_graph
        else {"status": "not_applicable" if not module_graph else "missing", "issues": [] if not module_graph else ["missing_plan"]}
    )
    risk = plan.get("risk") if isinstance(plan.get("risk"), dict) else {}
    coverage = plan.get("coverage") if isinstance(plan.get("coverage"), dict) else {}
    return {
        "present": bool(plan),
        "required": bool(module_graph),
        "schema_version": plan.get("schema_version") if plan else None,
        "schema_version_expected": MODULE_PROBE_PLAN_SCHEMA_VERSION,
        "plan_sha256": canonical_sha256(plan) if plan else None,
        "plan_self_hash": plan.get(MODULE_PROBE_PLAN_HASH_FIELD) if plan else None,
        "source_module_graph_sha256": plan.get("source_module_graph_sha256") if plan else None,
        "source_module_graph_self_hash": plan.get("source_module_graph_self_hash") if plan else None,
        "source_probe_contract_sha256": plan.get("source_probe_contract_sha256") if plan else None,
        "source_probe_contract_self_hash": plan.get("source_probe_contract_self_hash") if plan else None,
        "verification_status": verification.get("status"),
        "verification_issues": list(verification.get("issues") or []),
        "trust_allowed": trust_ok,
        "trust_reasons": list(trust_reasons),
        "risk_level": risk.get("level") if risk else None,
        "uncovered_obligations": list(risk.get("uncovered_obligations") or []) if risk else [],
        "coverage_ratio": coverage.get("coverage_ratio") if coverage else None,
        "requires_llm_probe_synthesis": coverage.get("requires_llm_probe_synthesis") if coverage else None,
        "certificate_plan_sha256": probe_cert.get("module_probe_plan_sha256") if probe_cert else None,
        "certificate_plan_self_hash": probe_cert.get("module_probe_plan_self_hash") if probe_cert else None,
        "certificate_plan_present": probe_cert.get("module_probe_plan_present") if probe_cert else None,
    }


def case_summary_dependency(parsed: dict[str, Any] | None, oracle: dict[str, Any]) -> dict[str, Any]:
    summary = parsed.get("case_summary") if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict) else {}
    return {
        "present": bool(summary),
        "schema_version": summary.get("schema_version") if summary else None,
        "status": summary.get("status") if summary else None,
        "case_summary_sha256": canonical_sha256(summary) if summary else None,
        "case_count": summary.get("case_count") if summary else None,
        "mismatch_count": summary.get("mismatch_count") if summary else None,
        "boundary_case_count": summary.get("boundary_case_count") if summary else None,
        "boundary_mismatch_count": summary.get("boundary_mismatch_count") if summary else None,
        "non_boundary_mismatch_count": summary.get("non_boundary_mismatch_count") if summary else None,
        "boundary_only_divergence": summary.get("boundary_only_divergence") if summary else None,
        "oracle_present": oracle.get("case_summary_present") if oracle else None,
        "oracle_status": oracle.get("case_summary_status") if oracle else None,
        "oracle_case_summary_sha256": oracle.get("case_summary_sha256") if oracle else None,
        "oracle_case_count": oracle.get("case_summary_case_count") if oracle else None,
        "oracle_mismatch_count": oracle.get("case_summary_mismatch_count") if oracle else None,
        "oracle_boundary_mismatch_count": oracle.get("case_summary_boundary_mismatch_count") if oracle else None,
        "oracle_non_boundary_mismatch_count": oracle.get("case_summary_non_boundary_mismatch_count") if oracle else None,
        "oracle_boundary_only_divergence": oracle.get("boundary_only_divergence") if oracle else None,
    }


def boundary_only_divergence(dynamic: dict[str, Any]) -> bool:
    parsed = parsed_execution(dynamic)
    summary = parsed.get("case_summary") if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict) else {}
    return summary.get("boundary_only_divergence") is True


def build_fusion_trust_dependencies(
    dynamic: dict[str, Any],
    *,
    source_fingerprint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    certificate = dynamic.get("execution_certificate") if isinstance(dynamic.get("execution_certificate"), dict) else {}
    sandbox = certificate.get("execution_sandbox") if isinstance(certificate.get("execution_sandbox"), dict) else {}
    toolchain = certificate.get("java_toolchain") if isinstance(certificate.get("java_toolchain"), dict) else {}
    outcome = certificate.get("dynamic_outcome") if isinstance(certificate.get("dynamic_outcome"), dict) else {}
    parsed = parsed_execution(dynamic)
    compile_info = dynamic.get("compile") if isinstance(dynamic.get("compile"), dict) else {}
    execution_info = dynamic.get("execution") if isinstance(dynamic.get("execution"), dict) else {}
    oracle = certificate.get("execution_result_oracle") if isinstance(certificate.get("execution_result_oracle"), dict) else {}
    runtime_safety = certificate.get("runtime_source_safety") if isinstance(certificate.get("runtime_source_safety"), dict) else {}
    probe_cert = certificate.get("probe") if isinstance(certificate.get("probe"), dict) else {}
    probe_adequacy = (
        probe_cert.get("probe_adequacy_certificate")
        if isinstance(probe_cert.get("probe_adequacy_certificate"), dict)
        else {}
    )
    dynamic_meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    framework_contracts = [
        item for item in dynamic_meta.get("framework_mock_contracts") or [] if isinstance(item, dict)
    ]
    context = dynamic.get("llm_context_completion") if isinstance(dynamic.get("llm_context_completion"), dict) else {}
    probe = dynamic.get("llm_probe_synthesis") if isinstance(dynamic.get("llm_probe_synthesis"), dict) else {}
    module_probe_plan_summary = module_probe_plan_dependency_summary(dynamic)
    case_summary = case_summary_dependency(parsed, oracle)
    dependencies: dict[str, Any] = {
        "schema_version": "eviclone-fusion-trust-dependencies/v1",
        "trust_policy": "requires_java_execution_certificate_and_bounded_llm_artifacts/v1",
        "dynamic_status": dynamic.get("status"),
        "dynamic_label": executable_dynamic_label(dynamic),
        "parsed": {
            "same": parsed.get("same") if isinstance(parsed, dict) else None,
            "status": parsed.get("status") if isinstance(parsed, dict) else None,
            "sha256": canonical_sha256(parsed) if isinstance(parsed, dict) else None,
        },
        "case_summary": case_summary,
        "compile": {
            "returncode": compile_info.get("returncode"),
            "stdout_sha256": sha256_text(str(compile_info.get("stdout") or "")),
            "stderr_sha256": sha256_text(str(compile_info.get("stderr") or "")),
        },
        "execution": {
            "returncode": execution_info.get("returncode"),
            "stdout_sha256": sha256_text(str(execution_info.get("stdout") or "")),
            "stderr_sha256": sha256_text(str(execution_info.get("stderr") or "")),
        },
        "java_execution_certificate": {
            "present": bool(certificate),
            "schema_version": certificate.get("schema_version") if certificate else None,
            "certificate_sha256": certificate.get("certificate_sha256") if certificate else None,
            "source_sha256": certificate.get("source_sha256") if certificate else None,
            "sandbox_schema_version": sandbox.get("schema_version") if sandbox else None,
            "sandbox_sha256": sandbox.get("sandbox_sha256") if sandbox else None,
            "sandbox_cwd_policy": sandbox.get("cwd_policy") if sandbox else None,
            "sandbox_work_dir_argument_within_cwd": sandbox.get("work_dir_argument_within_cwd") if sandbox else None,
            "sandbox_real_external_services_allowed": sandbox.get("real_external_services_allowed") if sandbox else None,
            "java_toolchain_status": toolchain.get("status") if toolchain else None,
            "java_toolchain_sha256": toolchain.get(JAVA_TOOLCHAIN_HASH_FIELD) if toolchain else None,
            "java_toolchain_javac_available": (
                (toolchain.get("compile_tool") or {}).get("available")
                if isinstance(toolchain.get("compile_tool"), dict)
                else None
            ),
            "java_toolchain_java_available": (
                (toolchain.get("execution_tool") or {}).get("available")
                if isinstance(toolchain.get("execution_tool"), dict)
                else None
            ),
            "dynamic_outcome_status": outcome.get("status") if outcome else None,
            "dynamic_outcome_sha256": outcome.get(DYNAMIC_OUTCOME_HASH_FIELD) if outcome else None,
            "dynamic_outcome_class": outcome.get("outcome_class") if outcome else None,
            "dynamic_failure_family": outcome.get("failure_family") if outcome else None,
            "dynamic_final_label_available": outcome.get("final_label_available") if outcome else None,
            "execution_result_oracle_status": oracle.get("status") if oracle else None,
            "execution_result_oracle_sha256": oracle.get("oracle_sha256") if oracle else None,
            "execution_result_oracle_final_label_available": oracle.get("final_label_available") if oracle else None,
            "probe_contract_sha256": probe_cert.get("probe_contract_sha256") if probe_cert else None,
            "probe_adequacy_status": probe_adequacy.get("status") if probe_adequacy else None,
            "probe_adequacy_sha256": probe_adequacy.get(PROBE_ADEQUACY_HASH_FIELD) if probe_adequacy else None,
            "probe_adequacy_tier": probe_adequacy.get("adequacy_tier") if probe_adequacy else None,
            "probe_case_count": probe_adequacy.get("case_count") if probe_adequacy else None,
            "runtime_source_safety_status": runtime_safety.get("status") if runtime_safety else None,
            "runtime_source_safety_sha256": runtime_safety.get("certificate_sha256") if runtime_safety else None,
            "framework_mocks": list(dynamic_meta.get("framework_mocks") or []),
            "framework_mock_contract_sha256s": [canonical_sha256(contract) for contract in framework_contracts],
            "framework_mock_contract_self_hashes": [
                contract.get(FRAMEWORK_MOCK_CONTRACT_HASH_FIELD) for contract in framework_contracts
            ],
            "certificate_framework_mock_contract_sha256s": probe_cert.get("framework_mock_contract_sha256s")
            if probe_cert
            else None,
        },
        "llm_context_completion": llm_dependency_summary(
            context,
            executed_source_sha256=certificate.get("source_sha256") if certificate else None,
        ),
        "llm_probe_synthesis": llm_dependency_summary(
            probe,
            executed_source_sha256=certificate.get("source_sha256") if certificate else None,
        ),
        "module_probe_plan": module_probe_plan_summary,
        "source_fingerprint": source_fingerprint_summary(source_fingerprint),
    }
    dependencies["dependencies_sha256"] = canonical_sha256(
        {key: value for key, value in dependencies.items() if key != "dependencies_sha256"}
    )
    return dependencies


def source_fingerprint_summary(source_fingerprint: dict[str, Any] | None) -> dict[str, Any]:
    if not source_fingerprint:
        return {"present": False}
    return {
        "present": True,
        "schema_version": source_fingerprint.get("schema_version"),
        "fingerprint_sha256": source_fingerprint.get("fingerprint_sha256"),
        "pair_id": source_fingerprint.get("pair_id"),
        "function_ids": source_fingerprint.get("function_ids"),
        "code_a_sha256": source_fingerprint.get("code_a_sha256"),
        "code_b_sha256": source_fingerprint.get("code_b_sha256"),
    }


def verify_source_fingerprint_matches_card(
    card: dict[str, Any],
    source_fingerprint: dict[str, Any] | None,
) -> tuple[bool, list[str]]:
    if not source_fingerprint:
        return True, ["source_fingerprint_not_available"]
    if source_fingerprint.get("schema_version") != "eviclone-source-pair-fingerprint/v1":
        return False, ["source_fingerprint_schema_mismatch"]
    expected_sha = canonical_sha256(
        {key: value for key, value in source_fingerprint.items() if key != "fingerprint_sha256"}
    )
    if source_fingerprint.get("fingerprint_sha256") != expected_sha:
        return False, ["source_fingerprint_sha_mismatch"]
    pair_id = card.get("pair_id")
    if pair_id is not None and source_fingerprint.get("pair_id") != pair_id:
        return False, ["source_fingerprint_pair_id_mismatch"]
    function_ids = card.get("function_ids") if isinstance(card.get("function_ids"), dict) else {}
    if function_ids and source_fingerprint.get("function_ids") != function_ids:
        return False, ["source_fingerprint_function_ids_mismatch"]
    return True, ["source_fingerprint_matches_card_identity"]


def llm_dependency_summary(expert: dict[str, Any], *, executed_source_sha256: Any = None) -> dict[str, Any]:
    if not expert:
        return {"used": False}
    payload = expert.get("payload") if isinstance(expert.get("payload"), dict) else {}
    payload_schema = payload.get("context_payload_schema") if isinstance(payload.get("context_payload_schema"), dict) else {}
    probe_payload_schema = payload.get("probe_payload_schema") if isinstance(payload.get("probe_payload_schema"), dict) else {}
    invocation = expert.get("expert_invocation") if isinstance(expert.get("expert_invocation"), dict) else {}
    firewall = invocation.get("input_firewall") if isinstance(invocation.get("input_firewall"), dict) else {}
    model_config = invocation.get("model_config") if isinstance(invocation.get("model_config"), dict) else {}
    artifact = expert.get("source_artifact") if isinstance(expert.get("source_artifact"), dict) else {}
    artifact_sha = artifact.get("sha256") if artifact else None
    preservation = artifact.get("source_preservation") if isinstance(artifact.get("source_preservation"), dict) else {}
    added_context = artifact.get("context_added_context") if isinstance(artifact.get("context_added_context"), dict) else {}
    source_safety = artifact.get("context_source_safety") if isinstance(artifact.get("context_source_safety"), dict) else {}
    execution_path = artifact.get("context_probe_execution_path") if isinstance(artifact.get("context_probe_execution_path"), dict) else {}
    probe_binding = artifact.get("probe_source_binding") if isinstance(artifact.get("probe_source_binding"), dict) else {}
    return {
        "used": True,
        "status": expert.get("status"),
        "expert_contract": payload.get("expert_contract") or invocation.get("expert_contract"),
        "payload_validation_errors": len(payload.get("validation_errors") or []),
        "context_payload_schema_status": payload_schema.get("status") if payload_schema else None,
        "context_payload_schema_sha256": payload_schema.get("certificate_sha256") if payload_schema else None,
        "probe_payload_schema_status": probe_payload_schema.get("status") if probe_payload_schema else None,
        "probe_payload_schema_sha256": probe_payload_schema.get("certificate_sha256") if probe_payload_schema else None,
        "expert_invocation_status": invocation.get("status"),
        "expert_invocation_output_kind": invocation.get("output_kind"),
        "expert_invocation_sha256": invocation.get(INVOCATION_HASH_FIELD),
        "expert_invocation_output_sha256": invocation.get("output_sha256"),
        "expert_invocation_raw_response_sha256": invocation.get("raw_response_sha256"),
        "expert_invocation_prompt_pair_sha256": invocation.get("prompt_pair_sha256"),
        "expert_invocation_validation_passed": invocation.get("validation_passed"),
        "expert_invocation_validation_error_count": len(invocation.get("validation_errors") or []),
        "input_firewall_status": firewall.get("status"),
        "input_firewall_policy": firewall.get("policy"),
        "input_firewall_sha256": firewall.get(INPUT_FIREWALL_HASH_FIELD),
        "input_firewall_prompt_sha256": firewall.get("user_prompt_sha256"),
        "model_config_present": bool(model_config),
        "model_config_available": model_config.get("available") if model_config else None,
        "model_config_schema_version": model_config.get("schema_version") if model_config else None,
        "model_config_model": model_config.get("model") if model_config else None,
        "model_config_temperature": model_config.get("temperature") if model_config else None,
        "model_config_endpoint_url_sha256": model_config.get("endpoint_url_sha256") if model_config else None,
        "model_config_sha256": model_config.get("config_sha256") if model_config else None,
        "source_artifact_retained": artifact.get("retained") is True if artifact else False,
        "source_artifact_schema_version": artifact.get("schema_version") if artifact else None,
        "source_artifact_certificate_sha256": artifact.get(SOURCE_ARTIFACT_HASH_FIELD) if artifact else None,
        "source_artifact_sha256": artifact_sha,
        "executed_source_sha256": executed_source_sha256,
        "executed_source_matches_artifact": bool(executed_source_sha256 and artifact_sha and executed_source_sha256 == artifact_sha),
        "source_preservation_status": preservation.get("status"),
        "source_preservation_sha256": preservation.get("certificate_sha256"),
        "context_added_context_present": bool(added_context),
        "context_added_context_status": added_context.get("status") if added_context else None,
        "context_added_context_sha256": added_context.get(CONTEXT_ADDED_CONTEXT_HASH_FIELD) if added_context else None,
        "context_added_context_declared_item_count": added_context.get("declared_item_count") if added_context else None,
        "context_added_context_grounded_item_count": added_context.get("grounded_item_count") if added_context else None,
        "context_source_safety_present": bool(source_safety),
        "context_source_safety_status": source_safety.get("status") if source_safety else None,
        "context_source_safety_sha256": source_safety.get("certificate_sha256") if source_safety else None,
        "context_probe_execution_path_present": bool(execution_path),
        "context_probe_execution_path_status": execution_path.get("status") if execution_path else None,
        "context_probe_execution_path_sha256": execution_path.get("certificate_sha256") if execution_path else None,
        "context_probe_execution_path_hardcoded_same": execution_path.get("hardcoded_executed_same_result") if execution_path else None,
        "probe_source_binding_present": bool(probe_binding),
        "probe_source_binding_status": probe_binding.get("status") if probe_binding else None,
        "probe_source_binding_sha256": probe_binding.get("certificate_sha256") if probe_binding else None,
    }


def verify_java_execution_certificate_for_trust(dynamic: dict[str, Any]) -> tuple[bool, list[str]]:
    certificate = dynamic.get("execution_certificate") if isinstance(dynamic.get("execution_certificate"), dict) else {}
    if not certificate:
        return False, ["java_execution_certificate_missing"]
    if certificate.get("schema_version") != JAVA_EXECUTION_CERTIFICATE_SCHEMA_VERSION:
        return False, ["java_execution_certificate_schema_mismatch"]
    if certificate.get("status") != dynamic.get("status"):
        return False, ["java_execution_certificate_status_mismatch"]
    if dynamic.get("engine") is not None and certificate.get("engine") != dynamic.get("engine"):
        return False, ["java_execution_certificate_engine_mismatch"]
    if dynamic.get("mode") is not None and certificate.get("mode") != dynamic.get("mode"):
        return False, ["java_execution_certificate_mode_mismatch"]
    sandbox_ok, sandbox_reasons = verify_java_execution_sandbox_for_trust(certificate)
    if not sandbox_ok:
        return False, sandbox_reasons
    toolchain_ok, toolchain_reasons = verify_java_toolchain_for_trust(certificate)
    if not toolchain_ok:
        return False, toolchain_reasons
    runtime_safety_ok, runtime_safety_reasons = verify_runtime_source_safety_for_trust(certificate)
    if not runtime_safety_ok:
        return False, runtime_safety_reasons
    outcome_ok, outcome_reasons = verify_dynamic_outcome_for_trust(certificate, dynamic)
    if not outcome_ok:
        return False, outcome_reasons

    compile_info = dynamic.get("compile") if isinstance(dynamic.get("compile"), dict) else {}
    compile_cert = certificate.get("compile") if isinstance(certificate.get("compile"), dict) else {}
    if not compile_cert:
        return False, ["java_execution_certificate_compile_section_missing"]
    if compile_cert.get("returncode") != compile_info.get("returncode"):
        return False, ["java_execution_certificate_compile_returncode_mismatch"]
    if compile_cert.get("stdout_sha256") != sha256_text(str(compile_info.get("stdout") or "")):
        return False, ["java_execution_certificate_compile_stdout_sha_mismatch"]
    if compile_cert.get("stderr_sha256") != sha256_text(str(compile_info.get("stderr") or "")):
        return False, ["java_execution_certificate_compile_stderr_sha_mismatch"]
    if compile_info.get("label") is not None and compile_cert.get("attempt_name") != compile_info.get("label"):
        return False, ["java_execution_certificate_compile_attempt_mismatch"]

    execution_info = dynamic.get("execution") if isinstance(dynamic.get("execution"), dict) else {}
    execution_cert = certificate.get("execution") if isinstance(certificate.get("execution"), dict) else {}
    if not execution_cert:
        return False, ["java_execution_certificate_execution_section_missing"]
    if execution_cert.get("returncode") != execution_info.get("returncode"):
        return False, ["java_execution_certificate_execution_returncode_mismatch"]
    if execution_cert.get("timeout") != (execution_info.get("timeout") is True):
        return False, ["java_execution_certificate_timeout_mismatch"]
    if execution_cert.get("stdout_sha256") != sha256_text(str(execution_info.get("stdout") or "")):
        return False, ["java_execution_certificate_execution_stdout_sha_mismatch"]
    if execution_cert.get("stderr_sha256") != sha256_text(str(execution_info.get("stderr") or "")):
        return False, ["java_execution_certificate_execution_stderr_sha_mismatch"]
    result_line_count = count_probe_result_lines(str(execution_info.get("stdout") or ""))
    if execution_cert.get("result_line_count") != result_line_count:
        return False, ["java_execution_certificate_result_line_count_mismatch"]
    if dynamic.get("status") == "executed" and result_line_count != 1:
        return False, ["java_execution_certificate_result_line_count_not_one"]
    oracle_ok, oracle_reasons = verify_execution_result_oracle_for_trust(certificate, dynamic)
    if not oracle_ok:
        return False, oracle_reasons
    adequacy_ok, adequacy_reasons = verify_probe_adequacy_for_trust(certificate, dynamic)
    if not adequacy_ok:
        return False, adequacy_reasons
    llm_binding_ok, llm_binding_reasons = verify_llm_probe_contract_invocation_for_trust(dynamic)
    if not llm_binding_ok:
        return False, llm_binding_reasons
    framework_ok, framework_reasons = verify_framework_mock_contracts_for_trust(certificate, dynamic)
    if not framework_ok:
        return False, framework_reasons
    runtime_fixture_ok, runtime_fixture_reasons = verify_runtime_fixtures_for_trust(certificate, dynamic)
    if not runtime_fixture_ok:
        return False, runtime_fixture_reasons
    parsed = execution_info.get("parsed") if isinstance(execution_info.get("parsed"), dict) else None
    expected_parsed_sha = canonical_sha256(parsed) if parsed is not None else None
    if execution_cert.get("parsed_sha256") != expected_parsed_sha:
        return False, ["java_execution_certificate_parsed_sha_mismatch"]
    if parsed is not None and execution_cert.get("parsed_same") != parsed.get("same"):
        return False, ["java_execution_certificate_parsed_same_mismatch"]
    if parsed is not None and execution_cert.get("parsed_status") != parsed.get("status"):
        return False, ["java_execution_certificate_parsed_status_mismatch"]

    expected_certificate_sha = canonical_sha256({key: value for key, value in certificate.items() if key != "certificate_sha256"})
    if certificate.get("certificate_sha256") != expected_certificate_sha:
        return False, ["java_execution_certificate_sha_mismatch"]
    return True, [
        "java_execution_certificate_verified",
        *sandbox_reasons,
        *toolchain_reasons,
        *runtime_safety_reasons,
        *outcome_reasons,
        *oracle_reasons,
        *adequacy_reasons,
        *llm_binding_reasons,
        *framework_reasons,
        *runtime_fixture_reasons,
    ]


def verify_execution_result_oracle_for_trust(certificate: dict[str, Any], dynamic: dict[str, Any]) -> tuple[bool, list[str]]:
    oracle = certificate.get("execution_result_oracle") if isinstance(certificate.get("execution_result_oracle"), dict) else {}
    if not oracle:
        return False, ["execution_result_oracle_missing"]
    if oracle.get("schema_version") != EXECUTION_RESULT_ORACLE_SCHEMA_VERSION:
        return False, ["execution_result_oracle_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in oracle.items() if key != "oracle_sha256"})
    if oracle.get("oracle_sha256") != expected_sha:
        return False, ["execution_result_oracle_sha_mismatch"]
    if dynamic.get("status") == "executed":
        if oracle.get("status") != "verified":
            return False, ["execution_result_oracle_unverified"]
        if oracle.get("final_label_available") is not True:
            return False, ["execution_result_oracle_final_label_unavailable"]
    execution_info = dynamic.get("execution") if isinstance(dynamic.get("execution"), dict) else {}
    parsed = execution_info.get("parsed") if isinstance(execution_info.get("parsed"), dict) else None
    stdout = str(execution_info.get("stdout") or "")
    if oracle.get("stdout_sha256") != sha256_text(stdout):
        return False, ["execution_result_oracle_stdout_sha_mismatch"]
    if oracle.get("parsed_sha256") != (canonical_sha256(parsed) if parsed is not None else None):
        return False, ["execution_result_oracle_parsed_sha_mismatch"]
    if parsed is not None and oracle.get("parsed_same") != parsed.get("same"):
        return False, ["execution_result_oracle_parsed_same_mismatch"]
    if parsed is not None and oracle.get("parsed_status") != parsed.get("status"):
        return False, ["execution_result_oracle_parsed_status_mismatch"]
    case_summary_ok, case_summary_reasons = verify_case_summary_oracle_fields(parsed, oracle)
    if not case_summary_ok:
        return False, case_summary_reasons
    meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    probe_contract = meta.get("probe_contract") if isinstance(meta.get("probe_contract"), dict) else {}
    if probe_contract:
        if probe_contract.get("schema_version") != PROBE_CONTRACT_SCHEMA_VERSION:
            return False, ["probe_contract_schema_mismatch"]
        contract_hash = probe_contract.get(PROBE_CONTRACT_HASH_FIELD)
        if contract_hash is not None and contract_hash != build_probe_contract_hash(probe_contract):
            return False, ["probe_contract_sha_mismatch"]
        expected_probe_contract_sha = canonical_sha256(probe_contract)
        if oracle.get("probe_contract_sha256") != expected_probe_contract_sha:
            return False, ["execution_result_oracle_probe_contract_sha_mismatch"]
    return True, ["execution_result_oracle_verified", *case_summary_reasons]


def verify_case_summary_oracle_fields(
    parsed: dict[str, Any] | None,
    oracle: dict[str, Any],
) -> tuple[bool, list[str]]:
    summary = parsed.get("case_summary") if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict) else {}
    if not summary:
        if oracle.get("case_summary_present") not in (False, None):
            return False, ["execution_result_oracle_case_summary_presence_mismatch"]
        return True, ["case_summary_not_present"]
    checks = [
        ("case_summary_present", True, "execution_result_oracle_case_summary_presence_mismatch"),
        ("case_summary_status", summary.get("status"), "execution_result_oracle_case_summary_status_mismatch"),
        ("case_summary_sha256", canonical_sha256(summary), "execution_result_oracle_case_summary_sha_mismatch"),
        ("case_summary_case_count", summary.get("case_count"), "execution_result_oracle_case_summary_count_mismatch"),
        ("case_summary_mismatch_count", summary.get("mismatch_count"), "execution_result_oracle_case_summary_mismatch_count_mismatch"),
        (
            "case_summary_boundary_mismatch_count",
            summary.get("boundary_mismatch_count"),
            "execution_result_oracle_case_summary_boundary_mismatch_count_mismatch",
        ),
        (
            "case_summary_non_boundary_mismatch_count",
            summary.get("non_boundary_mismatch_count"),
            "execution_result_oracle_case_summary_non_boundary_mismatch_count_mismatch",
        ),
        ("boundary_only_divergence", summary.get("boundary_only_divergence"), "execution_result_oracle_boundary_only_divergence_mismatch"),
    ]
    for key, expected, reason in checks:
        if oracle.get(key) != expected:
            return False, [reason]
    if summary.get("status") != "verified":
        return False, ["execution_result_case_summary_unverified"]
    return True, ["case_summary_oracle_fields_verified"]


def verify_probe_adequacy_for_trust(certificate: dict[str, Any], dynamic: dict[str, Any]) -> tuple[bool, list[str]]:
    meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    probe_contract = meta.get("probe_contract") if isinstance(meta.get("probe_contract"), dict) else {}
    if not probe_contract:
        return True, ["probe_adequacy_not_applicable"]
    if probe_contract.get("schema_version") != PROBE_CONTRACT_SCHEMA_VERSION:
        return False, ["probe_contract_schema_mismatch"]
    contract_hash = probe_contract.get(PROBE_CONTRACT_HASH_FIELD)
    if contract_hash is None:
        return False, ["probe_contract_sha_missing"]
    if contract_hash != build_probe_contract_hash(probe_contract):
        return False, ["probe_contract_sha_mismatch"]

    probe_cert = certificate.get("probe") if isinstance(certificate.get("probe"), dict) else {}
    if not probe_cert:
        return False, ["java_execution_certificate_probe_section_missing"]
    expected_contract_sha = canonical_sha256(probe_contract)
    if probe_cert.get("probe_contract_sha256") != expected_contract_sha:
        return False, ["java_execution_certificate_probe_contract_sha_mismatch"]
    if probe_cert.get("probe_contract_self_hash") != contract_hash:
        return False, ["java_execution_certificate_probe_contract_self_hash_mismatch"]

    adequacy = (
        probe_cert.get("probe_adequacy_certificate")
        if isinstance(probe_cert.get("probe_adequacy_certificate"), dict)
        else {}
    )
    if not adequacy:
        return False, ["probe_adequacy_certificate_missing"]
    if adequacy.get("schema_version") != PROBE_ADEQUACY_SCHEMA_VERSION:
        return False, ["probe_adequacy_schema_mismatch"]
    adequacy_hash = adequacy.get(PROBE_ADEQUACY_HASH_FIELD)
    if adequacy_hash is None:
        return False, ["probe_adequacy_sha_missing"]
    if adequacy_hash != build_probe_adequacy_certificate_hash(adequacy):
        return False, ["probe_adequacy_sha_mismatch"]
    if probe_cert.get("probe_adequacy_sha256") != adequacy_hash:
        return False, ["java_execution_certificate_probe_adequacy_sha_mismatch"]
    if adequacy.get("probe_contract_sha256") != expected_contract_sha:
        return False, ["probe_adequacy_probe_contract_sha_mismatch"]
    expected_adequacy = build_probe_adequacy_certificate(probe_contract)
    if not expected_adequacy:
        return False, ["probe_adequacy_recompute_failed"]
    if adequacy != expected_adequacy:
        return False, ["probe_adequacy_recomputed_mismatch"]
    if adequacy.get("status") != "verified":
        return False, ["probe_adequacy_unverified"]
    return True, ["probe_adequacy_verified"]


def verify_llm_probe_contract_invocation_for_trust(dynamic: dict[str, Any]) -> tuple[bool, list[str]]:
    meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    probe_contract = meta.get("probe_contract") if isinstance(meta.get("probe_contract"), dict) else {}
    probe_factory = str(probe_contract.get("probe_factory") or "")
    if probe_factory not in {"llm_probe_synthesis", "llm_context_completion"}:
        return True, ["llm_probe_contract_invocation_binding_not_applicable"]
    expert = dynamic.get(probe_factory) if isinstance(dynamic.get(probe_factory), dict) else {}
    if expert.get("status") != "completed":
        return False, [f"probe_contract_{probe_factory}_completion_missing"]
    invocation = expert.get("expert_invocation") if isinstance(expert.get("expert_invocation"), dict) else {}
    invocation_sha = invocation.get(INVOCATION_HASH_FIELD)
    if not invocation_sha:
        return False, [f"probe_contract_{probe_factory}_expert_invocation_sha_missing"]
    if probe_contract.get("expert_invocation_sha256") != invocation_sha:
        return False, [f"probe_contract_{probe_factory}_expert_invocation_sha_mismatch"]
    return True, [f"probe_contract_{probe_factory}_expert_invocation_bound"]


def verify_framework_mock_contracts_for_trust(
    certificate: dict[str, Any],
    dynamic: dict[str, Any],
) -> tuple[bool, list[str]]:
    meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    mock_ids = [str(item) for item in meta.get("framework_mocks") or [] if str(item)]
    contracts = [item for item in meta.get("framework_mock_contracts") or [] if isinstance(item, dict)]
    if not mock_ids and not contracts:
        return True, ["framework_mock_contracts_not_used"]
    if mock_ids and not contracts:
        return False, ["framework_mock_contracts_missing"]
    by_id = {str(item.get("mock_id") or ""): item for item in contracts}
    for mock_id in mock_ids:
        contract = by_id.get(mock_id)
        if not contract:
            return False, ["framework_mock_contract_missing_for_id"]
        if contract.get("schema_version") != FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION:
            return False, ["framework_mock_contract_schema_mismatch"]
        if contract.get("mock_id") != mock_id:
            return False, ["framework_mock_contract_id_mismatch"]
        if contract.get("deterministic") is not True:
            return False, ["framework_mock_contract_not_deterministic"]
        if contract.get("no_external_services") is not True:
            return False, ["framework_mock_contract_allows_external_services"]
        if not contract.get("version"):
            return False, ["framework_mock_contract_version_missing"]
        if not isinstance(contract.get("limitations"), list) or not contract.get("limitations"):
            return False, ["framework_mock_contract_limitations_missing"]
        contract_hash = contract.get(FRAMEWORK_MOCK_CONTRACT_HASH_FIELD)
        if contract_hash is None:
            return False, ["framework_mock_contract_sha_missing"]
        if contract_hash != build_framework_mock_contract_hash(contract):
            return False, ["framework_mock_contract_sha_mismatch"]

    probe_cert = certificate.get("probe") if isinstance(certificate.get("probe"), dict) else {}
    if probe_cert.get("framework_mocks") != mock_ids:
        return False, ["java_execution_certificate_framework_mocks_mismatch"]
    expected_contract_hashes = [canonical_sha256(contract) for contract in contracts]
    if probe_cert.get("framework_mock_contract_sha256s") != expected_contract_hashes:
        return False, ["java_execution_certificate_framework_mock_contract_sha_mismatch"]
    expected_self_hashes = [contract.get(FRAMEWORK_MOCK_CONTRACT_HASH_FIELD) for contract in contracts]
    if probe_cert.get("framework_mock_contract_self_hashes") != expected_self_hashes:
        return False, ["java_execution_certificate_framework_mock_contract_self_hash_mismatch"]
    return True, ["framework_mock_contracts_verified", "java_execution_certificate_framework_mock_contracts_verified"]


def verify_runtime_fixtures_for_trust(
    certificate: dict[str, Any],
    dynamic: dict[str, Any],
) -> tuple[bool, list[str]]:
    meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    mock_ids = {str(item) for item in meta.get("framework_mocks") or [] if str(item)}
    certificate_fixtures = (
        certificate.get("runtime_fixtures") if isinstance(certificate.get("runtime_fixtures"), dict) else {}
    )
    sandbox = certificate.get("execution_sandbox") if isinstance(certificate.get("execution_sandbox"), dict) else {}
    fixture_reasons: list[str] = []

    for fixture_id, spec in RUNTIME_FIXTURE_SPECS.items():
        top_fixture = dynamic.get(fixture_id) if isinstance(dynamic.get(fixture_id), dict) else {}
        certificate_fixture = (
            certificate_fixtures.get(fixture_id)
            if isinstance(certificate_fixtures.get(fixture_id), dict)
            else {}
        )
        sandbox_fixture = sandbox.get(fixture_id) if isinstance(sandbox.get(fixture_id), dict) else {}
        fixture_used = bool(top_fixture or certificate_fixture or sandbox_fixture or fixture_id in mock_ids)
        if not fixture_used:
            continue
        if not top_fixture:
            return False, [f"runtime_fixture_{fixture_id}_top_level_missing"]
        if not certificate_fixture:
            return False, [f"runtime_fixture_{fixture_id}_certificate_missing"]
        if not sandbox_fixture:
            return False, [f"runtime_fixture_{fixture_id}_sandbox_missing"]
        if certificate_fixture != top_fixture:
            return False, [f"runtime_fixture_{fixture_id}_certificate_mismatch"]
        if sandbox_fixture != certificate_fixture:
            return False, [f"runtime_fixture_{fixture_id}_sandbox_mismatch"]
        if top_fixture.get("schema_version") != spec.get("schema_version"):
            return False, [f"runtime_fixture_{fixture_id}_schema_mismatch"]
        fixture_hash = top_fixture.get(RUNTIME_FIXTURE_HASH_FIELD)
        if not fixture_hash:
            return False, [f"runtime_fixture_{fixture_id}_sha_missing"]
        if fixture_hash != build_runtime_fixture_hash(top_fixture):
            return False, [f"runtime_fixture_{fixture_id}_sha_mismatch"]
        if top_fixture.get("deterministic") is not True:
            return False, [f"runtime_fixture_{fixture_id}_not_deterministic"]
        if top_fixture.get("no_external_services") is not True:
            return False, [f"runtime_fixture_{fixture_id}_allows_external_services"]
        fixture_reasons.append(f"runtime_fixture_{fixture_id}_verified")

    if not fixture_reasons:
        return True, ["runtime_fixtures_not_used"]
    return True, ["runtime_fixtures_verified", *fixture_reasons]


def verify_java_execution_sandbox_for_trust(certificate: dict[str, Any]) -> tuple[bool, list[str]]:
    sandbox = certificate.get("execution_sandbox") if isinstance(certificate.get("execution_sandbox"), dict) else {}
    if not sandbox:
        return False, ["java_execution_sandbox_missing"]
    if sandbox.get("schema_version") != JAVA_EXECUTION_SANDBOX_SCHEMA_VERSION:
        return False, ["java_execution_sandbox_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in sandbox.items() if key != "sandbox_sha256"})
    if sandbox.get("sandbox_sha256") != expected_sha:
        return False, ["java_execution_sandbox_sha_mismatch"]
    if sandbox.get("cwd_policy") != "dedicated_pair_workdir":
        return False, ["java_execution_sandbox_cwd_policy_untrusted"]
    if sandbox.get("work_dir_argument_policy") != "dedicated_child_work_dir":
        return False, ["java_execution_sandbox_work_dir_policy_untrusted"]
    if sandbox.get("work_dir_argument_within_cwd") is not True:
        return False, ["java_execution_sandbox_work_dir_not_within_cwd"]
    if sandbox.get("source_filename") != "EviProbe.java":
        return False, ["java_execution_sandbox_source_filename_mismatch"]
    if sandbox.get("compile_uses_shell") is not False or sandbox.get("execution_uses_shell") is not False:
        return False, ["java_execution_sandbox_shell_enabled"]
    if sandbox.get("compile_command_policy") != "javac_utf8_single_source":
        return False, ["java_execution_sandbox_compile_policy_mismatch"]
    if sandbox.get("execution_command_policy") != "java_classpath_current_dir_single_work_arg":
        return False, ["java_execution_sandbox_execution_policy_mismatch"]
    if sandbox.get("classpath_policy") != "current_workdir_only":
        return False, ["java_execution_sandbox_classpath_policy_mismatch"]
    if sandbox.get("real_external_services_allowed") is not False:
        return False, ["java_execution_sandbox_external_services_allowed"]
    try:
        timeout = float(sandbox.get("timeout_sec"))
    except (TypeError, ValueError):
        return False, ["java_execution_sandbox_timeout_invalid"]
    if timeout <= 0:
        return False, ["java_execution_sandbox_timeout_invalid"]
    return True, ["java_execution_sandbox_verified"]


def verify_java_toolchain_for_trust(certificate: dict[str, Any]) -> tuple[bool, list[str]]:
    toolchain = certificate.get("java_toolchain") if isinstance(certificate.get("java_toolchain"), dict) else {}
    if not toolchain:
        return False, ["java_toolchain_certificate_missing"]
    if toolchain.get("schema_version") != JAVA_TOOLCHAIN_CERTIFICATE_SCHEMA_VERSION:
        return False, ["java_toolchain_schema_mismatch"]
    expected_sha = build_java_toolchain_certificate_hash(toolchain)
    if toolchain.get(JAVA_TOOLCHAIN_HASH_FIELD) != expected_sha:
        return False, ["java_toolchain_certificate_sha_mismatch"]
    compile_tool = toolchain.get("compile_tool") if isinstance(toolchain.get("compile_tool"), dict) else {}
    execution_tool = toolchain.get("execution_tool") if isinstance(toolchain.get("execution_tool"), dict) else {}
    if compile_tool.get("command_name") != "javac":
        return False, ["java_toolchain_compile_tool_mismatch"]
    if execution_tool.get("command_name") != "java":
        return False, ["java_toolchain_execution_tool_mismatch"]
    if toolchain.get("compile_command_prefix") != ["javac", "-encoding", "UTF-8"]:
        return False, ["java_toolchain_compile_command_prefix_mismatch"]
    if toolchain.get("execution_command_prefix") != ["java", "-cp", "."]:
        return False, ["java_toolchain_execution_command_prefix_mismatch"]
    if toolchain.get("version_probe_uses_shell") is not False:
        return False, ["java_toolchain_version_probe_shell_enabled"]
    status = str(toolchain.get("status") or "")
    if status == "verified":
        return True, ["java_toolchain_verified"]
    if status == "unavailable":
        return True, ["java_toolchain_recorded_unavailable"]
    return False, ["java_toolchain_status_invalid"]


def verify_runtime_source_safety_for_trust(certificate: dict[str, Any]) -> tuple[bool, list[str]]:
    safety = certificate.get("runtime_source_safety") if isinstance(certificate.get("runtime_source_safety"), dict) else {}
    if not safety:
        return False, ["runtime_source_safety_missing"]
    if safety.get("schema_version") != RUNTIME_SOURCE_SAFETY_SCHEMA_VERSION:
        return False, ["runtime_source_safety_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in safety.items() if key != "certificate_sha256"})
    if safety.get("certificate_sha256") != expected_sha:
        return False, ["runtime_source_safety_certificate_sha_mismatch"]
    if safety.get("source_sha256") != certificate.get("source_sha256"):
        return False, ["runtime_source_safety_source_sha_mismatch"]
    if safety.get("status") != "verified":
        errors = safety.get("validation_errors") if isinstance(safety.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or str(safety.get("status") or "unknown")
        return False, [f"runtime_source_safety_untrusted:{suffix}"]
    return True, ["runtime_source_safety_verified"]


def verify_dynamic_outcome_for_trust(
    certificate: dict[str, Any],
    dynamic: dict[str, Any],
) -> tuple[bool, list[str]]:
    outcome = certificate.get("dynamic_outcome") if isinstance(certificate.get("dynamic_outcome"), dict) else {}
    if not outcome:
        return False, ["dynamic_outcome_certificate_missing"]
    if outcome.get("schema_version") != DYNAMIC_OUTCOME_CERTIFICATE_SCHEMA_VERSION:
        return False, ["dynamic_outcome_schema_mismatch"]
    if outcome.get(DYNAMIC_OUTCOME_HASH_FIELD) != build_dynamic_outcome_certificate_hash(outcome):
        return False, ["dynamic_outcome_certificate_sha_mismatch"]
    compile_info = dynamic.get("compile") if isinstance(dynamic.get("compile"), dict) else {}
    execution_info = dynamic.get("execution") if isinstance(dynamic.get("execution"), dict) else {}
    meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    expected = build_dynamic_outcome_certificate(
        status=str(dynamic.get("status") or ""),
        mode=str(dynamic.get("mode") or certificate.get("mode") or ""),
        engine=str(dynamic.get("engine") or certificate.get("engine") or ""),
        compile_info=compile_info,
        execution_info=execution_info,
        meta=meta,
        llm_context_completion=dynamic.get("llm_context_completion")
        if isinstance(dynamic.get("llm_context_completion"), dict)
        else None,
        llm_probe_synthesis=dynamic.get("llm_probe_synthesis")
        if isinstance(dynamic.get("llm_probe_synthesis"), dict)
        else None,
        compile_attempts=dynamic.get("compile_attempts") if isinstance(dynamic.get("compile_attempts"), list) else None,
    )
    if outcome != expected:
        return False, ["dynamic_outcome_recomputed_mismatch"]
    return True, ["dynamic_outcome_verified"]


def verify_llm_input_firewall(invocation: Any, *, issue_prefix: str) -> tuple[bool, list[str]]:
    if not isinstance(invocation, dict):
        return False, [f"{issue_prefix}_expert_invocation_missing"]
    firewall = invocation.get("input_firewall")
    if not isinstance(firewall, dict):
        return False, [f"{issue_prefix}_input_firewall_missing"]
    reasons: list[str] = []
    if firewall.get("schema_version") != INPUT_FIREWALL_SCHEMA_VERSION:
        return False, [f"{issue_prefix}_input_firewall_schema_mismatch"]
    expected_firewall_sha = build_input_firewall_hash(firewall)
    if firewall.get(INPUT_FIREWALL_HASH_FIELD) != expected_firewall_sha:
        return False, [f"{issue_prefix}_input_firewall_sha_mismatch"]
    if firewall.get("policy") != INPUT_FIREWALL_POLICY:
        return False, [f"{issue_prefix}_input_firewall_policy_mismatch"]
    if firewall.get("expert_role") not in {issue_prefix, "context_completion", "probe_synthesis"}:
        return False, [f"{issue_prefix}_input_firewall_role_mismatch"]
    if firewall.get("status") != "passed":
        return False, [f"{issue_prefix}_input_firewall_not_passed"]
    if firewall.get("decision_inputs_visible") is not False:
        return False, [f"{issue_prefix}_input_firewall_decision_inputs_visible"]
    if firewall.get("visible_sensitive_paths") not in (None, []):
        return False, [f"{issue_prefix}_input_firewall_visible_sensitive_paths"]
    module_binding = firewall.get("module_graph_input_binding") if isinstance(firewall.get("module_graph_input_binding"), dict) else {}
    if module_binding:
        if module_binding.get("schema_version") != MODULE_GRAPH_INPUT_BINDING_SCHEMA_VERSION:
            return False, [f"{issue_prefix}_module_graph_input_binding_schema_mismatch"]
        expected_binding_sha = canonical_sha256(
            {key: value for key, value in module_binding.items() if key != MODULE_GRAPH_INPUT_BINDING_HASH_FIELD}
        )
        if module_binding.get(MODULE_GRAPH_INPUT_BINDING_HASH_FIELD) != expected_binding_sha:
            return False, [f"{issue_prefix}_module_graph_input_binding_sha_mismatch"]
        if module_binding.get("present") is True:
            if module_binding.get("llm_clone_decision_allowed") is not False:
                return False, [f"{issue_prefix}_module_graph_input_binding_allows_llm_clone_decision"]
            if module_binding.get("raw_source_patch_allowed") is not False:
                return False, [f"{issue_prefix}_module_graph_input_binding_allows_raw_source_patch"]
        reasons.append(f"{issue_prefix}_module_graph_input_binding_verified")
    reasons.append(f"{issue_prefix}_input_firewall_sha_verified")
    reasons.append(f"{issue_prefix}_input_firewall_verified")
    return True, reasons


def verify_llm_expert_invocation_output(
    invocation: Any,
    *,
    issue_prefix: str,
    expected_role: str,
    expected_contract: str,
    expected_output_kind: str,
    expected_output_sha: Any,
) -> tuple[bool, list[str]]:
    if not isinstance(invocation, dict):
        return False, [f"{issue_prefix}_expert_invocation_missing"]
    if invocation.get("schema_version") != "eviclone-llm-expert-invocation/v1":
        return False, [f"{issue_prefix}_expert_invocation_schema_mismatch"]
    expected_invocation_sha = build_expert_invocation_hash(invocation)
    if invocation.get(INVOCATION_HASH_FIELD) != expected_invocation_sha:
        return False, [f"{issue_prefix}_expert_invocation_sha_mismatch"]
    if invocation.get("expert_role") != expected_role:
        return False, [f"{issue_prefix}_expert_invocation_role_mismatch"]
    if invocation.get("expert_contract") != expected_contract:
        return False, [f"{issue_prefix}_expert_invocation_contract_mismatch"]
    if invocation.get("status") != "completed":
        return False, [f"{issue_prefix}_expert_invocation_status_mismatch"]
    if invocation.get("output_kind") != expected_output_kind:
        return False, [f"{issue_prefix}_expert_invocation_output_kind_mismatch"]
    expected_sha = str(expected_output_sha or "")
    if not looks_like_sha256(expected_sha):
        return False, [f"{issue_prefix}_expert_invocation_expected_output_sha_invalid"]
    if invocation.get("output_sha256") != expected_sha:
        return False, [f"{issue_prefix}_expert_invocation_output_sha_mismatch"]
    for hash_field in ["system_prompt_sha256", "user_prompt_sha256", "prompt_pair_sha256", "raw_response_sha256"]:
        value = invocation.get(hash_field)
        if value is not None and not looks_like_sha256(value):
            return False, [f"{issue_prefix}_expert_invocation_{hash_field}_invalid"]
    if invocation.get("validation_passed") is not True:
        return False, [f"{issue_prefix}_expert_invocation_validation_not_passed"]
    if invocation.get("validation_errors") not in (None, []):
        return False, [f"{issue_prefix}_expert_invocation_has_validation_errors"]
    return True, [
        f"{issue_prefix}_expert_invocation_sha_verified",
        f"{issue_prefix}_expert_invocation_output_verified",
    ]


def verify_llm_model_config(invocation: Any, *, issue_prefix: str) -> tuple[bool, list[str]]:
    if not isinstance(invocation, dict):
        return False, [f"{issue_prefix}_expert_invocation_missing"]
    model_config = invocation.get("model_config")
    if not isinstance(model_config, dict):
        return False, [f"{issue_prefix}_expert_model_config_missing"]
    if model_config.get("schema_version") != MODEL_CONFIG_SCHEMA_VERSION:
        return False, [f"{issue_prefix}_expert_model_config_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in model_config.items() if key != "config_sha256"})
    if model_config.get("config_sha256") != expected_sha:
        return False, [f"{issue_prefix}_expert_model_config_sha_mismatch"]
    if model_config.get("available") is not True:
        return False, [f"{issue_prefix}_expert_model_config_unavailable"]
    if model_config.get("model") != DEFAULT_MODEL:
        return False, [f"{issue_prefix}_expert_model_config_model_mismatch"]
    try:
        temperature = float(model_config.get("temperature"))
    except (TypeError, ValueError):
        return False, [f"{issue_prefix}_expert_model_config_temperature_invalid"]
    if temperature != 0.0:
        return False, [f"{issue_prefix}_expert_model_config_temperature_not_zero"]
    if not str(model_config.get("endpoint_url") or ""):
        return False, [f"{issue_prefix}_expert_model_config_endpoint_url_missing"]
    return True, [f"{issue_prefix}_expert_model_config_verified"]


def looks_like_sha256(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text.lower())


def verify_context_payload_schema_certificate(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    expected = build_context_payload_schema_certificate(payload)
    if expected.get("status") != "verified":
        errors = expected.get("validation_errors") if isinstance(expected.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or "unknown"
        return False, [f"context_payload_schema_untrusted:{suffix}"]
    embedded = payload.get("context_payload_schema") if isinstance(payload.get("context_payload_schema"), dict) else {}
    if not embedded:
        return True, ["context_payload_schema_recomputed_verified"]
    if embedded.get("schema_version") != CONTEXT_PAYLOAD_SCHEMA_VERSION:
        return False, ["context_payload_schema_schema_mismatch"]
    if embedded.get("component_role") != CONTEXT_COMPONENT_ROLE:
        return False, ["context_payload_schema_component_role_mismatch"]
    if embedded.get("expert_contract") != CONTEXT_EXPERT_CONTRACT:
        return False, ["context_payload_schema_expert_contract_mismatch"]
    if embedded.get("output_kind") != CONTEXT_OUTPUT_KIND:
        return False, ["context_payload_schema_output_kind_mismatch"]
    if embedded.get("allowed_output") != CONTEXT_ALLOWED_OUTPUT:
        return False, ["context_payload_schema_allowed_output_mismatch"]
    if embedded.get("clone_label_output_allowed") is not False:
        return False, ["context_payload_schema_allows_clone_label_output"]
    if embedded.get("final_decision_allowed") is not False:
        return False, ["context_payload_schema_allows_final_decision"]
    actual_sha = canonical_sha256({key: value for key, value in embedded.items() if key != "certificate_sha256"})
    if embedded.get("certificate_sha256") != actual_sha:
        return False, ["context_payload_schema_certificate_sha_mismatch"]
    if embedded.get("certificate_sha256") != expected.get("certificate_sha256"):
        return False, ["context_payload_schema_recomputed_sha_mismatch"]
    return True, ["context_payload_schema_verified"]


def verify_probe_payload_schema_certificate(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    expected = build_probe_payload_schema_certificate(payload)
    if expected.get("status") != "verified":
        errors = expected.get("validation_errors") if isinstance(expected.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or "unknown"
        return False, [f"probe_payload_schema_untrusted:{suffix}"]
    embedded = payload.get("probe_payload_schema") if isinstance(payload.get("probe_payload_schema"), dict) else {}
    if not embedded:
        return True, ["probe_payload_schema_recomputed_verified"]
    if embedded.get("schema_version") != PROBE_PAYLOAD_SCHEMA_VERSION:
        return False, ["probe_payload_schema_schema_mismatch"]
    if embedded.get("component_role") != PROBE_COMPONENT_ROLE:
        return False, ["probe_payload_schema_component_role_mismatch"]
    if embedded.get("expert_contract") != PROBE_EXPERT_CONTRACT:
        return False, ["probe_payload_schema_expert_contract_mismatch"]
    if embedded.get("output_kind") != PROBE_OUTPUT_KIND:
        return False, ["probe_payload_schema_output_kind_mismatch"]
    if embedded.get("allowed_output") != PROBE_ALLOWED_OUTPUT:
        return False, ["probe_payload_schema_allowed_output_mismatch"]
    if embedded.get("clone_label_output_allowed") is not False:
        return False, ["probe_payload_schema_allows_clone_label_output"]
    if embedded.get("final_decision_allowed") is not False:
        return False, ["probe_payload_schema_allows_final_decision"]
    actual_sha = canonical_sha256({key: value for key, value in embedded.items() if key != "certificate_sha256"})
    if embedded.get("certificate_sha256") != actual_sha:
        return False, ["probe_payload_schema_certificate_sha_mismatch"]
    if embedded.get("certificate_sha256") != expected.get("certificate_sha256"):
        return False, ["probe_payload_schema_recomputed_sha_mismatch"]
    return True, ["probe_payload_schema_verified"]


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def verify_source_artifact(artifact: dict[str, Any], *, expected_sha: Any = None) -> tuple[bool, list[str]]:
    if not artifact:
        return False, ["context_source_artifact_missing"]
    reasons: list[str] = []
    artifact_certificate_sha = artifact.get(SOURCE_ARTIFACT_HASH_FIELD)
    if artifact_certificate_sha is not None or artifact.get("schema_version") is not None:
        if artifact.get("schema_version") != SOURCE_ARTIFACT_SCHEMA_VERSION:
            return False, ["context_source_artifact_schema_mismatch"]
        expected_artifact_sha = build_source_artifact_hash(artifact)
        if artifact_certificate_sha != expected_artifact_sha:
            return False, ["context_source_artifact_certificate_sha_mismatch"]
        reasons.append("context_source_artifact_certificate_sha_verified")
    if artifact.get("retained") is not True:
        return False, ["context_source_artifact_not_retained"]
    path_text = str(artifact.get("path") or "")
    if not path_text:
        return False, ["context_source_artifact_path_missing"]
    source_path = Path(path_text)
    if not source_path.exists() or not source_path.is_file():
        return False, ["context_source_artifact_file_missing"]
    bytes_data = source_path.read_bytes()
    actual_sha = hashlib.sha256(bytes_data).hexdigest()
    artifact_sha = str(artifact.get("sha256") or "")
    if not artifact_sha:
        return False, ["context_source_artifact_sha_missing"]
    if artifact_sha != actual_sha:
        return False, ["context_source_artifact_sha_mismatch"]
    expected_text = str(expected_sha or "")
    if expected_text and expected_text != actual_sha:
        return False, ["context_payload_source_sha_mismatch"]
    artifact_bytes = artifact.get("bytes")
    if artifact_bytes is not None:
        try:
            if int(artifact_bytes) != len(bytes_data):
                return False, ["context_source_artifact_byte_count_mismatch"]
        except (TypeError, ValueError):
            return False, ["context_source_artifact_byte_count_invalid"]
    reasons.append("context_source_artifact_verified")
    return True, reasons


def verify_source_preservation_certificate(
    artifact: dict[str, Any],
    *,
    source_fingerprint: dict[str, Any] | None = None,
) -> tuple[bool, list[str]]:
    preservation = artifact.get("source_preservation") if isinstance(artifact.get("source_preservation"), dict) else {}
    if not preservation:
        return False, ["context_source_preservation_missing"]
    if preservation.get("schema_version") != "eviclone-source-preservation/v1":
        return False, ["context_source_preservation_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in preservation.items() if key != "certificate_sha256"})
    if preservation.get("certificate_sha256") != expected_sha:
        return False, ["context_source_preservation_certificate_sha_mismatch"]
    artifact_sha = str(artifact.get("sha256") or "")
    if preservation.get("source_sha256") != artifact_sha:
        return False, ["context_source_preservation_source_sha_mismatch"]
    fingerprint_ok, fingerprint_reasons = verify_source_preservation_matches_fingerprint(
        preservation,
        source_fingerprint,
    )
    if not fingerprint_ok:
        return False, fingerprint_reasons
    status = str(preservation.get("status") or "")
    if status not in {"exact", "normalized", "identifier_supported"}:
        return False, [f"context_source_preservation_untrusted:{status or 'missing'}"]
    for side in ["snippet_a", "snippet_b"]:
        snippet = preservation.get(side) if isinstance(preservation.get(side), dict) else {}
        ok, reason = verify_preserved_snippet(snippet, side=side)
        if not ok:
            return False, [reason]
    return True, [f"context_source_preservation_verified:{status}"]


def verify_source_preservation_matches_fingerprint(
    preservation: dict[str, Any],
    source_fingerprint: dict[str, Any] | None,
) -> tuple[bool, list[str]]:
    if not source_fingerprint:
        return True, ["source_fingerprint_not_available"]
    expected_sha = canonical_sha256(
        {key: value for key, value in source_fingerprint.items() if key != "fingerprint_sha256"}
    )
    if source_fingerprint.get("fingerprint_sha256") != expected_sha:
        return False, ["source_fingerprint_sha_mismatch"]
    if preservation.get("pair_id") != source_fingerprint.get("pair_id"):
        return False, ["source_preservation_pair_id_mismatch"]
    if preservation.get("function_ids") != source_fingerprint.get("function_ids"):
        return False, ["source_preservation_function_ids_mismatch"]
    snippet_a = preservation.get("snippet_a") if isinstance(preservation.get("snippet_a"), dict) else {}
    snippet_b = preservation.get("snippet_b") if isinstance(preservation.get("snippet_b"), dict) else {}
    if snippet_a.get("sha256") != source_fingerprint.get("code_a_sha256"):
        return False, ["source_preservation_snippet_a_pair_hash_mismatch"]
    if snippet_b.get("sha256") != source_fingerprint.get("code_b_sha256"):
        return False, ["source_preservation_snippet_b_pair_hash_mismatch"]
    return True, ["source_preservation_matches_source_fingerprint"]


def verify_executed_source_matches_artifact(
    dynamic: dict[str, Any],
    artifact: dict[str, Any],
    *,
    issue_prefix: str,
) -> tuple[bool, list[str]]:
    certificate = dynamic.get("execution_certificate") if isinstance(dynamic.get("execution_certificate"), dict) else {}
    executed_source_sha = str(certificate.get("source_sha256") or "")
    artifact_sha = str(artifact.get("sha256") or "")
    if not executed_source_sha:
        return False, [f"{issue_prefix}_executed_source_sha_missing"]
    if not artifact_sha:
        return False, [f"{issue_prefix}_source_artifact_sha_missing"]
    if executed_source_sha != artifact_sha:
        return False, [f"{issue_prefix}_executed_source_artifact_sha_mismatch"]
    return True, [f"{issue_prefix}_executed_source_matches_artifact"]


def verify_context_probe_execution_path_artifact(
    artifact: dict[str, Any],
    payload: dict[str, Any],
) -> tuple[bool, list[str]]:
    source_path = Path(str(artifact.get("path") or ""))
    try:
        source_text = source_path.read_text(encoding="utf-8")
    except OSError:
        return False, ["context_probe_execution_path_source_unreadable"]

    recomputed = build_context_probe_execution_path_certificate(source_text, payload)
    if recomputed.get("status") != "verified":
        errors = recomputed.get("validation_errors") if isinstance(recomputed.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or "unknown"
        return False, [f"context_probe_execution_path_untrusted:{suffix}"]

    embedded = artifact.get("context_probe_execution_path") if isinstance(artifact.get("context_probe_execution_path"), dict) else {}
    if not embedded:
        return True, ["context_probe_execution_path_recomputed_verified"]
    if embedded.get("schema_version") != CONTEXT_PROBE_EXECUTION_PATH_SCHEMA_VERSION:
        return False, ["context_probe_execution_path_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in embedded.items() if key != "certificate_sha256"})
    if embedded.get("certificate_sha256") != expected_sha:
        return False, ["context_probe_execution_path_certificate_sha_mismatch"]
    if embedded.get("certificate_sha256") != recomputed.get("certificate_sha256"):
        return False, ["context_probe_execution_path_recomputed_sha_mismatch"]
    return True, ["context_probe_execution_path_verified"]


def verify_context_source_safety_artifact(artifact: dict[str, Any]) -> tuple[bool, list[str]]:
    source_path = Path(str(artifact.get("path") or ""))
    try:
        source_text = source_path.read_text(encoding="utf-8")
    except OSError:
        return False, ["context_source_safety_source_unreadable"]

    recomputed = build_context_source_safety_certificate(source_text)
    if recomputed.get("status") != "verified":
        errors = recomputed.get("validation_errors") if isinstance(recomputed.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or "unknown"
        return False, [f"context_source_safety_untrusted:{suffix}"]

    embedded = artifact.get("context_source_safety") if isinstance(artifact.get("context_source_safety"), dict) else {}
    if not embedded:
        return True, ["context_source_safety_recomputed_verified"]
    if embedded.get("schema_version") != CONTEXT_SOURCE_SAFETY_SCHEMA_VERSION:
        return False, ["context_source_safety_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in embedded.items() if key != "certificate_sha256"})
    if embedded.get("certificate_sha256") != expected_sha:
        return False, ["context_source_safety_certificate_sha_mismatch"]
    if embedded.get("certificate_sha256") != recomputed.get("certificate_sha256"):
        return False, ["context_source_safety_recomputed_sha_mismatch"]
    return True, ["context_source_safety_verified"]


def verify_context_added_context_artifact(
    artifact: dict[str, Any],
    payload: dict[str, Any],
) -> tuple[bool, list[str]]:
    source_path = Path(str(artifact.get("path") or ""))
    try:
        source_text = source_path.read_text(encoding="utf-8")
    except OSError:
        return False, ["context_added_context_source_unreadable"]

    recomputed = build_context_added_context_certificate(source_text, payload)
    if recomputed.get("status") != "verified":
        errors = recomputed.get("validation_errors") if isinstance(recomputed.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or "unknown"
        return False, [f"context_added_context_untrusted:{suffix}"]

    embedded = artifact.get("context_added_context") if isinstance(artifact.get("context_added_context"), dict) else {}
    if not embedded:
        return True, ["context_added_context_recomputed_verified"]
    if embedded.get("schema_version") != CONTEXT_ADDED_CONTEXT_SCHEMA_VERSION:
        return False, ["context_added_context_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in embedded.items() if key != CONTEXT_ADDED_CONTEXT_HASH_FIELD})
    if embedded.get(CONTEXT_ADDED_CONTEXT_HASH_FIELD) != expected_sha:
        return False, ["context_added_context_certificate_sha_mismatch"]
    if embedded.get("source_sha256") != artifact.get("sha256"):
        return False, ["context_added_context_source_sha_mismatch"]
    if embedded.get(CONTEXT_ADDED_CONTEXT_HASH_FIELD) != recomputed.get(CONTEXT_ADDED_CONTEXT_HASH_FIELD):
        return False, ["context_added_context_recomputed_sha_mismatch"]
    return True, ["context_added_context_verified"]


def verify_probe_source_binding_artifact(
    artifact: dict[str, Any],
    payload: dict[str, Any],
) -> tuple[bool, list[str]]:
    source_path = Path(str(artifact.get("path") or ""))
    try:
        source_text = source_path.read_text(encoding="utf-8")
    except OSError:
        return False, ["probe_source_binding_source_unreadable"]

    embedded = artifact.get("probe_source_binding") if isinstance(artifact.get("probe_source_binding"), dict) else {}
    if not embedded:
        return False, ["probe_source_binding_missing"]
    if embedded.get("schema_version") != PROBE_SOURCE_BINDING_SCHEMA_VERSION:
        return False, ["probe_source_binding_schema_mismatch"]
    expected_sha = canonical_sha256({key: value for key, value in embedded.items() if key != "certificate_sha256"})
    if embedded.get("certificate_sha256") != expected_sha:
        return False, ["probe_source_binding_certificate_sha_mismatch"]
    probe_body = str(embedded.get("retained_probe_body") or "")
    if not probe_body:
        return False, ["probe_source_binding_retained_probe_body_missing"]
    recomputed = build_probe_source_binding_certificate(source_text, probe_body, payload)
    if recomputed.get("status") != "verified":
        errors = recomputed.get("validation_errors") if isinstance(recomputed.get("validation_errors"), list) else []
        suffix = "|".join(str(error) for error in errors[:3]) or "unknown"
        return False, [f"probe_source_binding_untrusted:{suffix}"]
    if embedded.get("certificate_sha256") != recomputed.get("certificate_sha256"):
        return False, ["probe_source_binding_recomputed_sha_mismatch"]
    return True, ["probe_source_binding_verified"]


def verify_preserved_snippet(snippet: dict[str, Any], *, side: str) -> tuple[bool, str]:
    if not snippet:
        return False, f"context_source_preservation_{side}_missing"
    if not looks_like_sha256(snippet.get("sha256")):
        return False, f"context_source_preservation_{side}_sha_invalid"
    if snippet.get("nonempty") is not True:
        return False, f"context_source_preservation_{side}_empty"
    exact_present = snippet.get("exact_present") is True
    normalized_present = snippet.get("normalized_present") is True
    retention = snippet.get("identifier_retention") if isinstance(snippet.get("identifier_retention"), dict) else {}
    identifier_supported = retention.get("status") == "sufficient"
    if not (exact_present or normalized_present or identifier_supported):
        return False, f"context_source_preservation_{side}_not_retained"
    return True, f"context_source_preservation_{side}_verified"


def looks_like_sha256(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text.lower())


def apply_certificate(
    card: dict[str, Any],
    certificate: ExecutableFusionCertificate,
    *,
    base_prediction: BaseModelPrediction | None,
) -> dict[str, Any]:
    updated = dict(card)
    updated["executable_fusion"] = certificate.to_dict()
    if base_prediction is not None:
        updated["base_model_prediction"] = base_prediction.to_dict()

    if certificate.final_label not in (0, 1):
        decision = dict(updated.get("decision") or {})
        risk_flags = list(decision.get("risk_flags") or [])
        risk_flags.append("executable_fusion_no_reliable_label")
        decision.update(
            {
                "verdict": "context_insufficient",
                "pred_label": None,
                "confidence": min(safe_float(decision.get("confidence"), 0.5), 0.3),
                "rationale": append_reason(
                    str(decision.get("rationale") or ""),
                    "Executable fusion could not obtain a trusted dynamic label or a usable base prediction.",
                ),
                "risk_flags": dedupe(risk_flags),
                "recommended_next_step": "manual_audit_or_repair_execution",
            }
        )
        updated["decision"] = decision
        return updated

    label = int(certificate.final_label)
    verdict = "behaviorally_supported_clone" if label == 1 else "likely_non_clone"
    confidence = fusion_confidence(certificate, base_prediction)
    decision = dict(updated.get("decision") or {})
    risk_flags = list(decision.get("risk_flags") or [])
    risk_flags.append(certificate.final_source)
    decision.update(
        {
            "verdict": verdict,
            "pred_label": VERDICT_TO_LABEL[verdict],
            "confidence": confidence,
            "rationale": append_reason(
                str(decision.get("rationale") or ""),
                fusion_rationale(certificate),
            ),
            "risk_flags": dedupe(risk_flags),
            "recommended_next_step": fusion_next_step(certificate),
        }
    )
    updated["decision"] = decision
    return updated


def fusion_confidence(certificate: ExecutableFusionCertificate, base_prediction: BaseModelPrediction | None) -> float:
    base_conf = base_prediction.confidence if base_prediction else None
    if base_conf is None and base_prediction and base_prediction.margin is not None:
        base_conf = 0.5 + 0.5 * clamp01(base_prediction.margin)
    if certificate.final_source == "trusted_executable_override":
        return 0.86
    if certificate.final_source == "trusted_executable_confirmation":
        return round(max(clamp01(base_conf), 0.82), 4)
    if certificate.final_source == "trusted_executable_without_base_prediction":
        return 0.82
    return round(clamp01(base_conf) if base_conf is not None else 0.5, 4)


def fusion_rationale(certificate: ExecutableFusionCertificate) -> str:
    if certificate.final_source == "trusted_executable_override":
        return "Trusted Java execution produced a behavioral result that conflicts with the base model, so the programmatic executable certificate overrides the base prediction."
    if certificate.final_source == "trusted_executable_confirmation":
        return "Trusted Java execution confirms the base model prediction."
    if certificate.final_source == "base_model_passthrough_after_untrusted_dynamic":
        if "boundary_only_divergence_not_decisive_for_override" in certificate.reasons:
            return "Executable evidence found only boundary-neighborhood divergence, so fusion records the counterexample but keeps the base prediction instead of applying a negative dynamic override."
        return "Dynamic evidence did not satisfy the executable trust contract; final output keeps the base model prediction."
    if certificate.final_source == "trusted_executable_without_base_prediction":
        return "Trusted Java execution produced a behavioral result and no usable base model prediction was available."
    return "Executable fusion did not produce a reliable final label."


def fusion_next_step(certificate: ExecutableFusionCertificate) -> str:
    if certificate.final_source == "trusted_executable_override":
        return "inspect_executable_counterexample"
    if certificate.final_source == "base_model_passthrough_after_untrusted_dynamic":
        if "boundary_only_divergence_not_decisive_for_override" in certificate.reasons:
            return "inspect_boundary_only_divergence"
        return "repair_execution_or_accept_base_model"
    return "human_audit_optional"


def parsed_execution(dynamic: dict[str, Any]) -> dict[str, Any] | None:
    execution = dynamic.get("execution") if isinstance(dynamic.get("execution"), dict) else {}
    parsed = execution.get("parsed") if isinstance(execution, dict) else None
    return parsed if isinstance(parsed, dict) else None


def dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        text = str(item)
        if text not in seen:
            seen.add(text)
            result.append(text)
    return result
