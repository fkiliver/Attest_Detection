from __future__ import annotations

import hashlib
import json
from typing import Any

from .context_completion import CONTEXT_ADDED_CONTEXT_HASH_FIELD
from .expert_invocation import INPUT_FIREWALL_HASH_FIELD, INVOCATION_HASH_FIELD
from .executor import (
    FRAMEWORK_MOCK_CONTRACT_HASH_FIELD,
    DYNAMIC_OUTCOME_HASH_FIELD,
    JAVA_TOOLCHAIN_HASH_FIELD,
    PROBE_ADEQUACY_HASH_FIELD,
    PROBE_CONTRACT_HASH_FIELD,
    SOURCE_ARTIFACT_HASH_FIELD,
)


SCHEMA_VERSION = "eviclone-pipeline-trace/v1"
ARCHITECTURE_CONTRACT_SCHEMA_VERSION = "eviclone-pipeline-architecture-contract/v1"
FINAL_DECISION_BINDING_SCHEMA_VERSION = "eviclone-final-decision-binding/v1"
COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION = "eviclone-component-interaction-contract/v1"


def attach_pipeline_trace(card: dict[str, Any]) -> dict[str, Any]:
    updated = dict(card)
    updated["pipeline_contract"] = build_pipeline_contract(updated)
    updated["pipeline_trace"] = build_pipeline_trace(updated)
    return updated


def build_pipeline_contract(card: dict[str, Any]) -> dict[str, Any]:
    route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
    fusion = card.get("executable_fusion") if isinstance(card.get("executable_fusion"), dict) else {}
    routed = bool(route)
    run_dynamic = route.get("run_dynamic") if routed else None
    final_owner = final_decision_owner(card)
    payload = {
        "schema_version": ARCHITECTURE_CONTRACT_SCHEMA_VERSION,
        "policy": "routed_dynamic_programmatic_evidence/v1" if routed else "legacy_evidence_pipeline/v1",
        "routed": routed,
        "dynamic_execution_required": bool(run_dynamic) if routed else None,
        "programmatic_fusion_required": bool(run_dynamic) if routed else None,
        "llm_role": "bounded_expert_context_or_probe_only" if routed else None,
        "llm_final_decision_allowed": False if routed else None,
        "legacy_llm_judge_allowed": False if routed else None,
        "allowed_llm_expert_roles": ["context_completion", "probe_synthesis"] if routed else [],
        "allowed_final_sources": allowed_final_sources(routed=bool(routed), run_dynamic=run_dynamic),
        "deployable_final_sources": deployable_final_sources(routed=bool(routed), run_dynamic=run_dynamic),
        "final_decision_owner": final_owner,
        "route_policy": route.get("policy"),
        "fusion_policy": fusion.get("policy"),
        "base_passthrough_required": run_dynamic is False if routed else None,
        "final_decision_binding": build_final_decision_binding(card),
        "component_dataflow": build_component_dataflow_edges(card),
        "component_interaction_contract": build_component_interaction_contract(card),
    }
    payload["contract_sha256"] = contract_sha256(payload)
    return payload


def final_decision_owner(card: dict[str, Any]) -> str:
    route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
    fusion = card.get("executable_fusion") if isinstance(card.get("executable_fusion"), dict) else {}
    llm = card.get("llm_evidence") if isinstance(card.get("llm_evidence"), dict) else {}
    if route:
        if route.get("run_dynamic") is False:
            return "base_model_passthrough"
        if fusion:
            return "executable_fusion"
        return "missing_executable_fusion"
    if llm and str(llm.get("status") or "").lower() == "success":
        return "legacy_llm_judge"
    return "local_static_pipeline"


def allowed_final_sources(*, routed: bool, run_dynamic: Any) -> list[str]:
    if not routed:
        return ["legacy_local_or_llm_pipeline"]
    if run_dynamic is False:
        return ["base_model_passthrough"]
    return [
        "trusted_executable_override",
        "trusted_executable_confirmation",
        "trusted_executable_without_base_prediction",
        "base_model_passthrough_after_untrusted_dynamic",
        "no_reliable_final_label",
    ]


def deployable_final_sources(*, routed: bool, run_dynamic: Any) -> list[str]:
    if not routed:
        return ["legacy_local_or_llm_pipeline"]
    if run_dynamic is False:
        return ["base_model_passthrough"]
    return [
        "trusted_executable_override",
        "trusted_executable_confirmation",
        "trusted_executable_without_base_prediction",
        "base_model_passthrough_after_untrusted_dynamic",
    ]


def build_final_decision_binding(card: dict[str, Any]) -> dict[str, Any]:
    route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
    fusion = card.get("executable_fusion") if isinstance(card.get("executable_fusion"), dict) else {}
    passthrough = card.get("base_model_passthrough") if isinstance(card.get("base_model_passthrough"), dict) else {}
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    owner = final_decision_owner(card)
    if route.get("run_dynamic") is False:
        source = "base_model_passthrough"
        source_final_label = passthrough.get("final_label") if passthrough else None
        source_certificate_sha256 = passthrough.get("passthrough_sha256") if passthrough else None
    elif fusion:
        source = fusion.get("final_source")
        source_final_label = fusion.get("final_label")
        source_certificate_sha256 = fusion.get("fusion_sha256")
    else:
        source = owner
        source_final_label = None
        source_certificate_sha256 = None
    binding = {
        "schema_version": FINAL_DECISION_BINDING_SCHEMA_VERSION,
        "policy": "bind_final_label_to_programmatic_certificate/v1",
        "decision_owner": owner,
        "source": source,
        "source_final_label": source_final_label,
        "source_certificate_sha256": source_certificate_sha256,
        "decision_pred_label": decision.get("pred_label"),
        "decision_verdict": decision.get("verdict"),
        "decision_recommended_next_step": decision.get("recommended_next_step"),
        "decision_sha256": canonical_sha256(
            {
                "pred_label": decision.get("pred_label"),
                "verdict": decision.get("verdict"),
                "confidence": decision.get("confidence"),
                "recommended_next_step": decision.get("recommended_next_step"),
                "risk_flags": decision.get("risk_flags") if isinstance(decision.get("risk_flags"), list) else [],
            }
        )
        if decision
        else None,
        "llm_final_decision_allowed": False if route else None,
    }
    binding["binding_sha256"] = canonical_sha256(
        {key: value for key, value in binding.items() if key != "binding_sha256"}
    )
    return binding


def build_component_dataflow_edges(card: dict[str, Any]) -> list[dict[str, Any]]:
    route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
    dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    fusion = card.get("executable_fusion") if isinstance(card.get("executable_fusion"), dict) else {}
    passthrough = card.get("base_model_passthrough") if isinstance(card.get("base_model_passthrough"), dict) else {}
    base_prediction = (
        card.get("base_model_prediction")
        if isinstance(card.get("base_model_prediction"), dict)
        else route.get("base_prediction")
        if isinstance(route.get("base_prediction"), dict)
        else {}
    )
    source_fingerprint = card.get("source_fingerprint") if isinstance(card.get("source_fingerprint"), dict) else {}

    edges: list[dict[str, Any]] = []
    if not route:
        return edges

    route_certificate = route.get("route_decision_certificate") if isinstance(route.get("route_decision_certificate"), dict) else {}
    route_score_certificate = route.get("route_score_certificate") if isinstance(route.get("route_score_certificate"), dict) else {}
    edges.append(
        dataflow_edge(
            "base_model_prediction",
            "dynamic_route",
            "base_prediction_snapshot",
            {
                "base_prediction_sha256": canonical_sha256(base_prediction) if base_prediction else None,
                "source": base_prediction.get("source") if base_prediction else None,
                "label": base_prediction.get("label") if base_prediction else None,
                "route_certificate_sha256": route_certificate.get("certificate_sha256") if route_certificate else None,
                "route_score_certificate_sha256": route_score_certificate.get("score_certificate_sha256")
                if route_score_certificate
                else None,
                "source_fingerprint_sha256": source_fingerprint.get("fingerprint_sha256") if source_fingerprint else None,
            },
        )
    )

    if route.get("run_dynamic") is False:
        binding = build_final_decision_binding(card)
        edges.append(
            dataflow_edge(
                "dynamic_route",
                "base_model_passthrough",
                "route_passthrough_decision",
                {
                    "route_certificate_sha256": route_certificate.get("certificate_sha256") if route_certificate else None,
                    "passthrough_sha256": passthrough.get("passthrough_sha256") if passthrough else None,
                    "final_label": passthrough.get("final_label") if passthrough else None,
                    "final_decision_binding_sha256": binding.get("binding_sha256"),
                    "decision_sha256": binding.get("decision_sha256"),
                },
            )
        )
        return edges

    edges.append(
        dataflow_edge(
            "dynamic_route",
            "dynamic_executor",
            "execute_route_decision",
            {
                "route_certificate_sha256": route_certificate.get("certificate_sha256") if route_certificate else None,
                "run_dynamic": route.get("run_dynamic"),
                "policy": route.get("policy"),
            },
        )
    )

    dynamic_meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    probe_contract = dynamic_meta.get("probe_contract") if isinstance(dynamic_meta.get("probe_contract"), dict) else {}
    probe_adequacy = (
        dynamic_meta.get("probe_adequacy_certificate")
        if isinstance(dynamic_meta.get("probe_adequacy_certificate"), dict)
        else {}
    )
    framework_mock_contracts = [
        item for item in dynamic_meta.get("framework_mock_contracts") or [] if isinstance(item, dict)
    ]
    execution_certificate = (
        dynamic.get("execution_certificate")
        if isinstance(dynamic.get("execution_certificate"), dict)
        else {}
    )
    java_toolchain = (
        execution_certificate.get("java_toolchain")
        if isinstance(execution_certificate.get("java_toolchain"), dict)
        else {}
    )
    dynamic_outcome = (
        execution_certificate.get("dynamic_outcome")
        if isinstance(execution_certificate.get("dynamic_outcome"), dict)
        else {}
    )
    case_summary = execution_case_summary(dynamic)
    functional_pair_ir = (
        dynamic_meta.get("functional_block_pair_ir")
        if isinstance(dynamic_meta.get("functional_block_pair_ir"), dict)
        else {}
    )
    if functional_pair_ir:
        edges.append(
            dataflow_edge(
                "functional_block_ir",
                "dynamic_executor",
                "standardized_core_logic_modules",
                {
                    "pair_ir_sha256": canonical_sha256(functional_pair_ir),
                    "pair_ir_self_hash": functional_pair_ir.get("pair_ir_sha256"),
                    "module_signature_a": list(functional_pair_ir.get("module_signature_a") or []),
                    "module_signature_b": list(functional_pair_ir.get("module_signature_b") or []),
                    "module_signature_equal": functional_pair_ir.get("module_signature_equal"),
                    "llm_clone_decision_allowed": (
                        functional_pair_ir.get("llm_contract", {}).get("clone_decision_allowed")
                        if isinstance(functional_pair_ir.get("llm_contract"), dict)
                        else None
                    ),
                },
            )
        )
    executable_module_graph = (
        dynamic_meta.get("executable_module_graph")
        if isinstance(dynamic_meta.get("executable_module_graph"), dict)
        else {}
    )
    if executable_module_graph:
        execution_plan = (
            executable_module_graph.get("execution_plan")
            if isinstance(executable_module_graph.get("execution_plan"), dict)
            else {}
        )
        edges.append(
            dataflow_edge(
                "executable_module_graph",
                "dynamic_executor",
                "standard_module_execution_plan",
                {
                    "module_graph_sha256": canonical_sha256(executable_module_graph),
                    "module_graph_self_hash": executable_module_graph.get("module_graph_sha256"),
                    "source_pair_ir_sha256": executable_module_graph.get("source_pair_ir_sha256"),
                    "plan_a": list(execution_plan.get("a") or []),
                    "plan_b": list(execution_plan.get("b") or []),
                    "llm_clone_decision_allowed": (
                        executable_module_graph.get("llm_contract", {}).get("clone_decision_allowed")
                        if isinstance(executable_module_graph.get("llm_contract"), dict)
                        else None
                    ),
                },
            )
        )
    module_probe_plan = (
        dynamic_meta.get("module_probe_plan")
        if isinstance(dynamic_meta.get("module_probe_plan"), dict)
        else {}
    )
    if module_probe_plan:
        coverage = (
            module_probe_plan.get("coverage")
            if isinstance(module_probe_plan.get("coverage"), dict)
            else {}
        )
        risk = module_probe_plan.get("risk") if isinstance(module_probe_plan.get("risk"), dict) else {}
        edges.append(
            dataflow_edge(
                "module_probe_plan",
                "dynamic_executor",
                "module_graph_probe_obligations",
                {
                    "module_probe_plan_sha256": canonical_sha256(module_probe_plan),
                    "module_probe_plan_self_hash": module_probe_plan.get("plan_sha256"),
                    "source_module_graph_sha256": module_probe_plan.get("source_module_graph_sha256"),
                    "source_probe_contract_sha256": module_probe_plan.get("source_probe_contract_sha256"),
                    "covered_obligations": list(coverage.get("covered_obligations") or []),
                    "uncovered_obligations": list(coverage.get("uncovered_obligations") or []),
                    "risk_level": risk.get("level"),
                    "requires_llm_probe_synthesis": coverage.get("requires_llm_probe_synthesis"),
                },
            )
        )
    executable_composition = (
        dynamic_meta.get("executable_composition_spec")
        if isinstance(dynamic_meta.get("executable_composition_spec"), dict)
        else {}
    )
    if executable_composition:
        plan_binding = (
            executable_composition.get("execution_plan_binding")
            if isinstance(executable_composition.get("execution_plan_binding"), dict)
            else {}
        )
        lowering_contract = (
            executable_composition.get("lowering_contract")
            if isinstance(executable_composition.get("lowering_contract"), dict)
            else {}
        )
        side_specs = (
            executable_composition.get("side_compositions")
            if isinstance(executable_composition.get("side_compositions"), dict)
            else {}
        )
        side_a = side_specs.get("a") if isinstance(side_specs.get("a"), dict) else {}
        side_b = side_specs.get("b") if isinstance(side_specs.get("b"), dict) else {}
        edges.append(
            dataflow_edge(
                "executable_composition_spec",
                "dynamic_executor",
                "standard_module_composition_lowering",
                {
                    "composition_sha256": canonical_sha256(executable_composition),
                    "composition_self_hash": executable_composition.get("composition_sha256"),
                    "source_module_graph_sha256": executable_composition.get("source_module_graph_sha256"),
                    "source_probe_plan_sha256": executable_composition.get("source_probe_plan_sha256"),
                    "composition_model": executable_composition.get("composition_model"),
                    "plan_a": list(plan_binding.get("a") or []),
                    "plan_b": list(plan_binding.get("b") or []),
                    "step_count_a": len(side_a.get("steps") or []),
                    "step_count_b": len(side_b.get("steps") or []),
                    "raw_source_patch_allowed": lowering_contract.get("raw_source_patch_allowed"),
                    "llm_module_rewrite_allowed": lowering_contract.get("llm_module_rewrite_allowed"),
                },
            )
        )
    module_lowering = (
        dynamic_meta.get("module_composition_lowering")
        if isinstance(dynamic_meta.get("module_composition_lowering"), dict)
        else {}
    )
    if module_lowering:
        edges.append(
            dataflow_edge(
                "module_composition_lowering",
                "dynamic_executor",
                "deterministic_standard_module_lowering_backend",
                {
                    "lowering_sha256": canonical_sha256(module_lowering),
                    "lowering_self_hash": module_lowering.get("lowering_sha256"),
                    "backend": module_lowering.get("backend"),
                    "source_composition_sha256": module_lowering.get("source_composition_sha256"),
                    "source_probe_plan_sha256": module_lowering.get("source_probe_plan_sha256"),
                    "probe_contract_sha256": module_lowering.get("probe_contract_sha256"),
                    "probe_body_sha256": module_lowering.get("probe_body_sha256"),
                    "probe_invokes_original_snippet_methods": module_lowering.get(
                        "probe_invokes_original_snippet_methods"
                    ),
                    "llm_used": module_lowering.get("llm_used"),
                    "raw_source_patch_allowed": module_lowering.get("raw_source_patch_allowed"),
                },
            )
        )
    if probe_contract:
        edges.append(
            dataflow_edge(
                "probe_contract",
                "dynamic_executor",
                "execution_observation_contract",
                {
                    "probe_contract_sha256": probe_contract.get(PROBE_CONTRACT_HASH_FIELD),
                    "probe_family": probe_contract.get("probe_family"),
                    "probe_factory": probe_contract.get("probe_factory"),
                    "probe_adequacy_sha256": probe_adequacy.get(PROBE_ADEQUACY_HASH_FIELD) if probe_adequacy else None,
                    "probe_adequacy_status": probe_adequacy.get("status") if probe_adequacy else None,
                    "probe_adequacy_tier": probe_adequacy.get("adequacy_tier") if probe_adequacy else None,
                    "probe_case_count": probe_adequacy.get("case_count") if probe_adequacy else None,
                },
            )
        )
    if framework_mock_contracts:
        edges.append(
            dataflow_edge(
                "framework_mock_contracts",
                "dynamic_executor",
                "programmatic_context_contracts",
                {
                    "framework_mocks": list(dynamic_meta.get("framework_mocks") or []),
                    "framework_mock_contract_sha256s": [canonical_sha256(item) for item in framework_mock_contracts],
                    "framework_mock_contract_self_hashes": [
                        item.get(FRAMEWORK_MOCK_CONTRACT_HASH_FIELD) for item in framework_mock_contracts
                    ],
                },
            )
        )

    for stage_id in ["llm_probe_synthesis", "llm_context_completion"]:
        expert = dynamic.get(stage_id) if isinstance(dynamic.get(stage_id), dict) else {}
        if not expert:
            continue
        invocation = expert.get("expert_invocation") if isinstance(expert.get("expert_invocation"), dict) else {}
        artifact = expert.get("source_artifact") if isinstance(expert.get("source_artifact"), dict) else {}
        added_context = (
            artifact.get("context_added_context")
            if isinstance(artifact.get("context_added_context"), dict)
            else {}
        )
        payload = expert.get("payload") if isinstance(expert.get("payload"), dict) else {}
        edges.append(
            dataflow_edge(
                stage_id,
                "dynamic_executor",
                "bounded_expert_artifact",
                {
                    "expert_contract": payload.get("expert_contract") or invocation.get("expert_contract"),
                    "expert_invocation_sha256": invocation.get(INVOCATION_HASH_FIELD),
                    "input_firewall_sha256": (
                        invocation.get("input_firewall", {}).get(INPUT_FIREWALL_HASH_FIELD)
                        if isinstance(invocation.get("input_firewall"), dict)
                        else None
                    ),
                    "context_added_context_sha256": (
                        added_context.get(CONTEXT_ADDED_CONTEXT_HASH_FIELD) if added_context else None
                    ),
                    "context_added_context_declared_item_count": (
                        added_context.get("declared_item_count") if added_context else None
                    ),
                    "source_artifact_sha256": artifact.get(SOURCE_ARTIFACT_HASH_FIELD),
                    "source_sha256": artifact.get("sha256"),
                    "llm_final_decision_allowed": False,
                },
            )
        )

    certificate = dynamic.get("execution_certificate") if isinstance(dynamic.get("execution_certificate"), dict) else {}
    oracle = certificate.get("execution_result_oracle") if isinstance(certificate.get("execution_result_oracle"), dict) else {}
    case_summary = execution_case_summary(dynamic)
    certificate_probe = certificate.get("probe") if isinstance(certificate.get("probe"), dict) else {}
    java_toolchain = certificate.get("java_toolchain") if isinstance(certificate.get("java_toolchain"), dict) else {}
    dynamic_outcome = certificate.get("dynamic_outcome") if isinstance(certificate.get("dynamic_outcome"), dict) else {}
    if certificate:
        edges.append(
            dataflow_edge(
                "dynamic_executor",
                "executable_fusion",
                "java_execution_certificate",
                {
                    "execution_certificate_sha256": certificate.get("certificate_sha256"),
                    "source_sha256": certificate.get("source_sha256"),
                    "java_toolchain_sha256": java_toolchain.get(JAVA_TOOLCHAIN_HASH_FIELD) if java_toolchain else None,
                    "java_toolchain_status": java_toolchain.get("status") if java_toolchain else None,
                    "dynamic_outcome_sha256": (
                        dynamic_outcome.get(DYNAMIC_OUTCOME_HASH_FIELD) if dynamic_outcome else None
                    ),
                    "dynamic_outcome_class": dynamic_outcome.get("outcome_class") if dynamic_outcome else None,
                    "dynamic_failure_family": dynamic_outcome.get("failure_family") if dynamic_outcome else None,
                    "execution_result_oracle_sha256": oracle.get("oracle_sha256") if oracle else None,
                    "execution_result_oracle_final_label_available": oracle.get("final_label_available") if oracle else None,
                    "case_summary_sha256": canonical_sha256(case_summary) if case_summary else None,
                    "case_summary_mismatch_count": case_summary.get("mismatch_count") if case_summary else None,
                    "case_summary_boundary_mismatch_count": (
                        case_summary.get("boundary_mismatch_count") if case_summary else None
                    ),
                    "case_summary_non_boundary_mismatch_count": (
                        case_summary.get("non_boundary_mismatch_count") if case_summary else None
                    ),
                    "boundary_only_divergence": case_summary.get("boundary_only_divergence") if case_summary else None,
                    "probe_adequacy_sha256": certificate_probe.get("probe_adequacy_sha256") if certificate_probe else None,
                    "probe_adequacy_status": certificate_probe.get("probe_adequacy_status") if certificate_probe else None,
                    "probe_adequacy_tier": certificate_probe.get("probe_adequacy_tier") if certificate_probe else None,
                },
            )
        )

    if fusion:
        dependencies = fusion.get("trust_dependencies") if isinstance(fusion.get("trust_dependencies"), dict) else {}
        case_summary = fusion_case_summary(fusion)
        binding = build_final_decision_binding(card)
        edges.append(
            dataflow_edge(
                "executable_fusion",
                "final_decision",
                "programmatic_final_decision",
                {
                    "fusion_sha256": fusion.get("fusion_sha256"),
                    "trust_dependencies_sha256": dependencies.get("dependencies_sha256") if dependencies else None,
                    "final_source": fusion.get("final_source"),
                    "final_label": fusion.get("final_label"),
                    "dynamic_trusted": fusion.get("dynamic_trusted"),
                    "boundary_only_divergence": case_summary.get("boundary_only_divergence") if case_summary else None,
                    "case_summary_mismatch_count": case_summary.get("mismatch_count") if case_summary else None,
                    "case_summary_non_boundary_mismatch_count": (
                        case_summary.get("non_boundary_mismatch_count") if case_summary else None
                    ),
                    "llm_final_decision_allowed": False,
                    "final_decision_binding_sha256": binding.get("binding_sha256"),
                    "decision_sha256": binding.get("decision_sha256"),
                },
            )
        )
    return edges


def build_component_interaction_contract(card: dict[str, Any]) -> dict[str, Any]:
    route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
    dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    routed = bool(route)
    run_dynamic = route.get("run_dynamic") if routed else None
    components: list[dict[str, Any]] = []

    if not routed:
        payload = {
            "schema_version": COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION,
            "policy": "legacy_component_interaction/v1",
            "routed": False,
            "decision_authority": "legacy_pipeline",
            "llm_clone_label_output_allowed": None,
            "llm_final_decision_output_allowed": None,
            "final_decision_components": ["legacy_local_or_llm_pipeline"],
            "components": components,
            "dataflow_edges_sha256": canonical_sha256([]),
        }
        payload["interaction_contract_sha256"] = canonical_sha256(
            {key: value for key, value in payload.items() if key != "interaction_contract_sha256"}
        )
        return payload

    components.append(
        component_permission(
            "base_model_prediction",
            role="base_clone_detector_snapshot",
            active=True,
            allowed_inputs=["source_pair"],
            allowed_outputs=["base_prediction_label", "confidence", "margin"],
            may_emit_base_prediction=True,
            downstream_consumers=["dynamic_route", "base_model_passthrough", "executable_fusion"],
        )
    )
    components.append(
        component_permission(
            "dynamic_route",
            role="dynamic_evidence_router",
            active=True,
            allowed_inputs=["base_prediction_snapshot", "pre_execution_static_features"],
            allowed_outputs=["run_dynamic", "route_score", "route_reasons", "route_certificate"],
            may_emit_route_decision=True,
            downstream_consumers=["dynamic_executor"] if run_dynamic is True else ["base_model_passthrough"],
        )
    )
    if run_dynamic is False:
        components.append(
            component_permission(
                "base_model_passthrough",
                role="programmatic_base_prediction_acceptor",
                active=True,
                allowed_inputs=["base_prediction_snapshot", "route_passthrough_decision"],
                allowed_outputs=["final_label", "passthrough_certificate"],
                may_emit_final_decision=True,
                downstream_consumers=["final_decision"],
            )
        )
        final_components = ["base_model_passthrough"]
        bounded_expert_components: list[str] = []
    else:
        components.append(
            component_permission(
                "dynamic_executor",
                role="java_execution_observer",
                active=True,
                allowed_inputs=["source_pair", "route_dynamic_decision", "bounded_expert_artifacts"],
                allowed_outputs=["execution_observation", "execution_certificate", "runtime_contracts"],
                may_emit_executable_observation=True,
                downstream_consumers=["executable_fusion"],
            )
        )
        components.append(
            component_permission(
                "llm_context_completion",
                role="llm_context_completion_expert",
                active=isinstance(dynamic.get("llm_context_completion"), dict),
                allowed_inputs=["method_snippets", "compile_diagnostics", "current_harness_without_decision_inputs"],
                allowed_outputs=["context_completed_java_harness", "context_payload_schema", "expert_invocation"],
                may_emit_bounded_expert_artifact=True,
                downstream_consumers=["dynamic_executor"],
            )
        )
        components.append(
            component_permission(
                "llm_probe_synthesis",
                role="llm_probe_synthesis_expert",
                active=isinstance(dynamic.get("llm_probe_synthesis"), dict),
                allowed_inputs=["method_snippets", "generated_harness_without_decision_inputs", "compile_metadata"],
                allowed_outputs=["main_body_probe", "probe_payload_schema", "expert_invocation"],
                may_emit_bounded_expert_artifact=True,
                downstream_consumers=["dynamic_executor"],
            )
        )
        components.append(
            component_permission(
                "executable_fusion",
                role="programmatic_evidence_fusion",
                active=True,
                allowed_inputs=["base_prediction_snapshot", "java_execution_certificate", "trust_dependencies"],
                allowed_outputs=["final_label", "final_source", "fusion_certificate", "decision_accounting"],
                may_emit_final_decision=True,
                downstream_consumers=["final_decision"],
            )
        )
        final_components = ["executable_fusion"]
        bounded_expert_components = ["llm_context_completion", "llm_probe_synthesis"]

    components.append(
        component_permission(
            "final_decision",
            role="bound_output_record",
            active=True,
            allowed_inputs=["final_decision_binding"],
            allowed_outputs=["decision_record"],
            may_emit_final_decision=True,
            downstream_consumers=[],
        )
    )
    payload = {
        "schema_version": COMPONENT_INTERACTION_CONTRACT_SCHEMA_VERSION,
        "policy": "bounded_programmatic_component_interaction/v1",
        "routed": True,
        "decision_authority": "programmatic_fusion_or_base_passthrough",
        "llm_clone_label_output_allowed": False,
        "llm_final_decision_output_allowed": False,
        "final_decision_components": final_components,
        "bounded_expert_components": bounded_expert_components,
        "components": components,
        "dataflow_edges_sha256": canonical_sha256(build_component_dataflow_edges(card)),
    }
    payload["interaction_contract_sha256"] = canonical_sha256(
        {key: value for key, value in payload.items() if key != "interaction_contract_sha256"}
    )
    return payload


def component_permission(
    component: str,
    *,
    role: str,
    active: bool,
    allowed_inputs: list[str],
    allowed_outputs: list[str],
    downstream_consumers: list[str],
    may_emit_base_prediction: bool = False,
    may_emit_route_decision: bool = False,
    may_emit_executable_observation: bool = False,
    may_emit_bounded_expert_artifact: bool = False,
    may_emit_final_decision: bool = False,
) -> dict[str, Any]:
    return {
        "component": component,
        "role": role,
        "active": active,
        "allowed_inputs": allowed_inputs,
        "allowed_outputs": allowed_outputs,
        "may_emit_base_prediction": may_emit_base_prediction,
        "may_emit_route_decision": may_emit_route_decision,
        "may_emit_executable_observation": may_emit_executable_observation,
        "may_emit_bounded_expert_artifact": may_emit_bounded_expert_artifact,
        "may_emit_final_decision": may_emit_final_decision,
        "downstream_consumers": downstream_consumers,
    }


def dataflow_edge(source: str, target: str, artifact: str, payload: dict[str, Any]) -> dict[str, Any]:
    edge = {
        "source": source,
        "target": target,
        "artifact": artifact,
        "payload": payload,
    }
    edge["edge_sha256"] = canonical_sha256(edge)
    return edge


def build_pipeline_trace(card: dict[str, Any]) -> dict[str, Any]:
    stages = build_trace_stages(card)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "pipeline": "routed_dynamic_evidence_pipeline/v1" if isinstance(card.get("dynamic_route"), dict) else "legacy_evidence_pipeline/v1",
        "llm_role": "bounded_expert_context_or_probe_only",
        "llm_final_decision_allowed": False if isinstance(card.get("dynamic_route"), dict) else None,
        "dataflow_edges": build_component_dataflow_edges(card),
        "component_interaction_summary": component_interaction_summary(card),
        "stages": stages,
        "final_decision": final_decision_summary(card),
        "final_decision_binding": build_final_decision_binding(card),
    }
    payload["trace_sha256"] = trace_sha256(payload)
    return payload


def component_interaction_summary(card: dict[str, Any]) -> dict[str, Any]:
    contract = build_component_interaction_contract(card)
    components = [item for item in contract.get("components") or [] if isinstance(item, dict)]
    final_permission_components = [
        str(item.get("component") or "")
        for item in components
        if item.get("may_emit_final_decision") is True
    ]
    bounded_expert_components = [
        str(item.get("component") or "")
        for item in components
        if item.get("may_emit_bounded_expert_artifact") is True
    ]
    active_components = [
        str(item.get("component") or "")
        for item in components
        if item.get("active") is True
    ]
    summary = {
        "schema_version": "eviclone-component-interaction-summary/v1",
        "interaction_contract_schema_version": contract.get("schema_version"),
        "interaction_contract_sha256": contract.get("interaction_contract_sha256"),
        "decision_authority": contract.get("decision_authority"),
        "llm_clone_label_output_allowed": contract.get("llm_clone_label_output_allowed"),
        "llm_final_decision_output_allowed": contract.get("llm_final_decision_output_allowed"),
        "final_decision_components": contract.get("final_decision_components") or [],
        "final_permission_components": final_permission_components,
        "bounded_expert_components": bounded_expert_components,
        "active_components": active_components,
        "component_count": len(components),
        "active_component_count": len(active_components),
        "dataflow_edges_sha256": contract.get("dataflow_edges_sha256"),
    }
    summary["summary_sha256"] = canonical_sha256(
        {key: value for key, value in summary.items() if key != "summary_sha256"}
    )
    return summary


def build_trace_stages(card: dict[str, Any]) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = [
        {
            "id": "local_static_evidence",
            "status": "completed" if isinstance(card.get("local_evidence"), dict) else "missing",
            "outputs": compact_local_outputs(card),
        }
    ]
    route = card.get("dynamic_route") if isinstance(card.get("dynamic_route"), dict) else {}
    dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    fusion = card.get("executable_fusion") if isinstance(card.get("executable_fusion"), dict) else {}
    dynamic_meta = dynamic.get("meta") if isinstance(dynamic.get("meta"), dict) else {}
    probe_contract = dynamic_meta.get("probe_contract") if isinstance(dynamic_meta.get("probe_contract"), dict) else {}
    probe_adequacy = (
        dynamic_meta.get("probe_adequacy_certificate")
        if isinstance(dynamic_meta.get("probe_adequacy_certificate"), dict)
        else {}
    )
    framework_mock_contracts = [
        item for item in dynamic_meta.get("framework_mock_contracts") or [] if isinstance(item, dict)
    ]
    execution_certificate = (
        dynamic.get("execution_certificate")
        if isinstance(dynamic.get("execution_certificate"), dict)
        else {}
    )
    java_toolchain = (
        execution_certificate.get("java_toolchain")
        if isinstance(execution_certificate.get("java_toolchain"), dict)
        else {}
    )
    dynamic_outcome = (
        execution_certificate.get("dynamic_outcome")
        if isinstance(execution_certificate.get("dynamic_outcome"), dict)
        else {}
    )
    case_summary = execution_case_summary(dynamic)

    if route:
        route_certificate = route.get("route_decision_certificate") if isinstance(route.get("route_decision_certificate"), dict) else {}
        score_certificate = route.get("route_score_certificate") if isinstance(route.get("route_score_certificate"), dict) else {}
        stages.append(
            {
                "id": "dynamic_route",
                "status": "route_to_dynamic" if route.get("run_dynamic") is True else "base_model_passthrough",
                "policy": route.get("policy"),
                "outputs": {
                    "component_role": route_certificate.get("component_role") if route_certificate else None,
                    "decision_kind": route_certificate.get("decision_kind") if route_certificate else None,
                    "run_dynamic": route.get("run_dynamic"),
                    "score": route.get("score"),
                    "threshold": route.get("threshold"),
                    "tier": route.get("tier"),
                    "base_label": ((route.get("base_prediction") or {}) if isinstance(route.get("base_prediction"), dict) else {}).get("label"),
                    "reason_count": len(route.get("reasons") or []),
                    "route_certificate_status": route_certificate.get("status") if route_certificate else None,
                    "route_certificate_sha256": route_certificate.get("certificate_sha256") if route_certificate else None,
                    "route_score_certificate_schema_version": score_certificate.get("schema_version") if score_certificate else None,
                    "route_score_certificate_status": score_certificate.get("status") if score_certificate else None,
                    "route_score_certificate_sha256": score_certificate.get("score_certificate_sha256") if score_certificate else None,
                },
            }
        )
        if route.get("run_dynamic") is False:
            stages.append(
                {
                    "id": "base_model_passthrough",
                    "status": "completed",
                    "outputs": final_decision_summary(card),
                }
            )
            return stages

    if dynamic:
        stages.append(
            {
                "id": "dynamic_executor",
                "status": str(dynamic.get("status") or "missing"),
                "outputs": {
                    "engine": dynamic.get("engine"),
                    "compile_returncode": (dynamic.get("compile") or {}).get("returncode")
                    if isinstance(dynamic.get("compile"), dict)
                    else None,
                    "parsed_same": ((dynamic.get("execution") or {}).get("parsed") or {}).get("same")
                    if isinstance(dynamic.get("execution"), dict)
                    and isinstance((dynamic.get("execution") or {}).get("parsed"), dict)
                    else None,
                    "execution_certificate_present": bool(execution_certificate),
                    "java_toolchain_status": java_toolchain.get("status") if java_toolchain else None,
                    "java_toolchain_sha256": java_toolchain.get(JAVA_TOOLCHAIN_HASH_FIELD) if java_toolchain else None,
                    "dynamic_outcome_class": dynamic_outcome.get("outcome_class") if dynamic_outcome else None,
                    "dynamic_failure_family": dynamic_outcome.get("failure_family") if dynamic_outcome else None,
                    "dynamic_final_label_available": (
                        dynamic_outcome.get("final_label_available") if dynamic_outcome else None
                    ),
                    "probe_factory": dynamic_meta.get("probe_factory"),
                    "probe_contract_present": bool(probe_contract),
                    "probe_contract_sha256": probe_contract.get(PROBE_CONTRACT_HASH_FIELD) if probe_contract else None,
                    "probe_adequacy_present": bool(probe_adequacy),
                    "probe_adequacy_sha256": probe_adequacy.get(PROBE_ADEQUACY_HASH_FIELD) if probe_adequacy else None,
                    "probe_adequacy_status": probe_adequacy.get("status") if probe_adequacy else None,
                    "probe_adequacy_tier": probe_adequacy.get("adequacy_tier") if probe_adequacy else None,
                    "probe_case_count": probe_adequacy.get("case_count") if probe_adequacy else None,
                    "case_summary_present": bool(case_summary),
                    "case_summary_sha256": canonical_sha256(case_summary) if case_summary else None,
                    "case_summary_mismatch_count": case_summary.get("mismatch_count") if case_summary else None,
                    "case_summary_boundary_mismatch_count": (
                        case_summary.get("boundary_mismatch_count") if case_summary else None
                    ),
                    "case_summary_non_boundary_mismatch_count": (
                        case_summary.get("non_boundary_mismatch_count") if case_summary else None
                    ),
                    "boundary_only_divergence": case_summary.get("boundary_only_divergence") if case_summary else None,
                    "framework_mock_count": len(dynamic_meta.get("framework_mocks") or []),
                    "framework_mock_contract_sha256s": [canonical_sha256(item) for item in framework_mock_contracts],
                    "framework_mock_contract_self_hashes": [
                        item.get(FRAMEWORK_MOCK_CONTRACT_HASH_FIELD) for item in framework_mock_contracts
                    ],
                },
            }
        )
        probe = dynamic.get("llm_probe_synthesis") if isinstance(dynamic.get("llm_probe_synthesis"), dict) else {}
        if probe:
            stages.append(expert_stage("llm_probe_synthesis", probe))
        context = dynamic.get("llm_context_completion") if isinstance(dynamic.get("llm_context_completion"), dict) else {}
        if context:
            stages.append(expert_stage("llm_context_completion", context))

    if fusion:
        trust_dependencies = fusion.get("trust_dependencies") if isinstance(fusion.get("trust_dependencies"), dict) else {}
        case_summary = fusion_case_summary(fusion)
        decision_accounting = fusion_decision_accounting_summary(fusion)
        stages.append(
            {
                "id": "executable_fusion",
                "status": str(fusion.get("final_source") or "missing"),
                "policy": fusion.get("policy"),
                "outputs": {
                    "fusion_schema_version": fusion.get("schema_version"),
                    "fusion_sha256": fusion.get("fusion_sha256"),
                    "final_label": fusion.get("final_label"),
                    "dynamic_label": fusion.get("dynamic_label"),
                    "dynamic_trusted": fusion.get("dynamic_trusted"),
                    "base_label": fusion.get("base_label"),
                    "reason_count": len(fusion.get("reasons") or []),
                    "trust_dependencies_sha256": trust_dependencies.get("dependencies_sha256") if trust_dependencies else None,
                    "case_summary_present": case_summary.get("present") if case_summary else None,
                    "case_summary_mismatch_count": case_summary.get("mismatch_count") if case_summary else None,
                    "case_summary_boundary_mismatch_count": (
                        case_summary.get("boundary_mismatch_count") if case_summary else None
                    ),
                    "case_summary_non_boundary_mismatch_count": (
                        case_summary.get("non_boundary_mismatch_count") if case_summary else None
                    ),
                    "boundary_only_divergence": case_summary.get("boundary_only_divergence") if case_summary else None,
                    "decision_accounting_sha256": decision_accounting.get("accounting_sha256"),
                    "dynamic_override_eligible": decision_accounting.get("dynamic_override_eligible"),
                    "override_applied": decision_accounting.get("override_applied"),
                    "confirmation_applied": decision_accounting.get("confirmation_applied"),
                    "base_passthrough_applied": decision_accounting.get("base_passthrough_applied"),
                    "no_reliable_label": decision_accounting.get("no_reliable_label"),
                },
            }
        )
    return stages


def expert_stage(stage_id: str, expert: dict[str, Any]) -> dict[str, Any]:
    payload = expert.get("payload") if isinstance(expert.get("payload"), dict) else {}
    invocation = expert.get("expert_invocation") if isinstance(expert.get("expert_invocation"), dict) else {}
    firewall = invocation.get("input_firewall") if isinstance(invocation.get("input_firewall"), dict) else {}
    model_config = invocation.get("model_config") if isinstance(invocation.get("model_config"), dict) else {}
    artifact = expert.get("source_artifact") if isinstance(expert.get("source_artifact"), dict) else {}
    preservation = artifact.get("source_preservation") if isinstance(artifact.get("source_preservation"), dict) else {}
    added_context = (
        artifact.get("context_added_context")
        if isinstance(artifact.get("context_added_context"), dict)
        else {}
    )
    context_payload_schema = payload.get("context_payload_schema") if isinstance(payload.get("context_payload_schema"), dict) else {}
    probe_payload_schema = payload.get("probe_payload_schema") if isinstance(payload.get("probe_payload_schema"), dict) else {}
    return {
        "id": stage_id,
        "status": str(expert.get("status") or "missing"),
        "expert_contract": payload.get("expert_contract") or invocation.get("expert_contract"),
        "outputs": {
            "validation_errors": len(payload.get("validation_errors") or []),
            "expert_invocation_status": invocation.get("status"),
            "expert_invocation_present": bool(invocation),
            "expert_invocation_sha256": invocation.get(INVOCATION_HASH_FIELD),
            "expert_invocation_output_kind": invocation.get("output_kind"),
            "expert_invocation_output_sha256": invocation.get("output_sha256"),
            "expert_invocation_raw_response_sha256": invocation.get("raw_response_sha256"),
            "expert_invocation_validation_passed": invocation.get("validation_passed"),
            "input_firewall_status": firewall.get("status") if firewall else None,
            "input_firewall_sha256": firewall.get(INPUT_FIREWALL_HASH_FIELD) if firewall else None,
            "model_config_sha256": model_config.get("config_sha256") if model_config else None,
            "context_payload_schema_status": context_payload_schema.get("status") if context_payload_schema else None,
            "probe_payload_schema_status": probe_payload_schema.get("status") if probe_payload_schema else None,
            "source_artifact_retained": artifact.get("retained") is True,
            "source_artifact_sha_present": bool(artifact.get("sha256")),
            "source_artifact_certificate_sha256": artifact.get(SOURCE_ARTIFACT_HASH_FIELD),
            "source_preservation_status": preservation.get("status"),
            "context_added_context_status": added_context.get("status") if added_context else None,
            "context_added_context_sha256": (
                added_context.get(CONTEXT_ADDED_CONTEXT_HASH_FIELD) if added_context else None
            ),
            "context_added_context_declared_item_count": (
                added_context.get("declared_item_count") if added_context else None
            ),
            "context_added_context_grounded_item_count": (
                added_context.get("grounded_item_count") if added_context else None
            ),
        },
    }


def compact_local_outputs(card: dict[str, Any]) -> dict[str, Any]:
    local = card.get("local_evidence") if isinstance(card.get("local_evidence"), dict) else {}
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    return {
        "target_family": local.get("target_family"),
        "shared_family_count": len(local.get("shared_feature_families") or []),
        "risk_count": len(local.get("risk_flags") or []),
        "initial_pred_label": decision.get("pred_label"),
    }


def execution_case_summary(dynamic: dict[str, Any]) -> dict[str, Any]:
    execution = dynamic.get("execution") if isinstance(dynamic.get("execution"), dict) else {}
    parsed = execution.get("parsed") if isinstance(execution.get("parsed"), dict) else {}
    summary = parsed.get("case_summary") if isinstance(parsed.get("case_summary"), dict) else {}
    return summary


def fusion_case_summary(fusion: dict[str, Any]) -> dict[str, Any]:
    dependencies = fusion.get("trust_dependencies") if isinstance(fusion.get("trust_dependencies"), dict) else {}
    summary = dependencies.get("case_summary") if isinstance(dependencies.get("case_summary"), dict) else {}
    return summary


def final_decision_summary(card: dict[str, Any]) -> dict[str, Any]:
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    fusion = card.get("executable_fusion") if isinstance(card.get("executable_fusion"), dict) else {}
    passthrough = card.get("base_model_passthrough") if isinstance(card.get("base_model_passthrough"), dict) else {}
    contract = card.get("pipeline_contract") if isinstance(card.get("pipeline_contract"), dict) else {}
    decision_accounting = fusion_decision_accounting_summary(fusion)
    case_summary = fusion_case_summary(fusion)
    binding = build_final_decision_binding(card)
    source = binding.get("source")
    deployable_sources = (
        contract.get("deployable_final_sources")
        if isinstance(contract.get("deployable_final_sources"), list)
        else deployable_final_sources(
            routed=isinstance(card.get("dynamic_route"), dict),
            run_dynamic=card.get("dynamic_route", {}).get("run_dynamic")
            if isinstance(card.get("dynamic_route"), dict)
            else None,
        )
    )
    return {
        "pred_label": decision.get("pred_label"),
        "verdict": decision.get("verdict"),
        "confidence": decision.get("confidence"),
        "recommended_next_step": decision.get("recommended_next_step"),
        "decision_sha256": binding.get("decision_sha256"),
        "final_decision_binding_sha256": binding.get("binding_sha256"),
        "final_source": source,
        "deployable_final_sources": deployable_sources,
        "final_source_deployable": source in deployable_sources,
        "final_label_available": binding.get("source_final_label") in (0, 1),
        "base_passthrough_schema_version": passthrough.get("schema_version"),
        "base_passthrough_sha256": passthrough.get("passthrough_sha256"),
        "fusion_final_source": fusion.get("final_source"),
        "fusion_schema_version": fusion.get("schema_version"),
        "fusion_sha256": fusion.get("fusion_sha256"),
        "fusion_decision_accounting_sha256": decision_accounting.get("accounting_sha256"),
        "case_summary_present": case_summary.get("present") if case_summary else None,
        "case_summary_mismatch_count": case_summary.get("mismatch_count") if case_summary else None,
        "case_summary_boundary_mismatch_count": case_summary.get("boundary_mismatch_count") if case_summary else None,
        "case_summary_non_boundary_mismatch_count": (
            case_summary.get("non_boundary_mismatch_count") if case_summary else None
        ),
        "boundary_only_divergence": case_summary.get("boundary_only_divergence") if case_summary else None,
        "dynamic_override_eligible": decision_accounting.get("dynamic_override_eligible"),
        "override_applied": decision_accounting.get("override_applied"),
        "confirmation_applied": decision_accounting.get("confirmation_applied"),
        "base_passthrough_applied": decision_accounting.get("base_passthrough_applied"),
        "no_reliable_label": decision_accounting.get("no_reliable_label"),
    }


def fusion_decision_accounting_summary(fusion: dict[str, Any]) -> dict[str, Any]:
    accounting = fusion.get("decision_accounting") if isinstance(fusion.get("decision_accounting"), dict) else {}
    return accounting if isinstance(accounting, dict) else {}


def trace_sha256(trace: dict[str, Any]) -> str:
    payload = {key: value for key, value in trace.items() if key != "trace_sha256"}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def contract_sha256(contract: dict[str, Any]) -> str:
    payload = {key: value for key, value in contract.items() if key != "contract_sha256"}
    return canonical_sha256(payload)


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()
