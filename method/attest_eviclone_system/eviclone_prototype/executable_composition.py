from __future__ import annotations

import hashlib
import json
from typing import Any


EXECUTABLE_COMPOSITION_SCHEMA_VERSION = "eviclone-executable-composition-spec/v1"
EXECUTABLE_COMPOSITION_HASH_FIELD = "composition_sha256"

MODULE_COMBINATORS = {
    "input_normalization": "normalize_input",
    "branch_guard": "select_guarded_path",
    "collection_iteration": "iterate_collection_elements",
    "iteration": "iterate_control_flow",
    "state_update": "apply_state_transition",
    "collection_transform": "transform_collection_values",
    "environment_interaction": "call_environment_adapter",
    "exception_boundary": "model_exception_boundary",
    "return_mapping": "project_return_value",
    "pure_computation": "compute_pure_value",
}

MODULE_OBLIGATIONS = {
    "branch_guard": ["branch_path"],
    "collection_iteration": ["collection_iteration_path"],
    "environment_interaction": ["environment_effect"],
    "return_mapping": ["return_value"],
    "state_update": ["state_mutation"],
}


def build_executable_composition_spec(
    executable_module_graph: dict[str, Any],
    module_probe_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    module_probe_plan = module_probe_plan if isinstance(module_probe_plan, dict) else {}
    execution_plan = (
        executable_module_graph.get("execution_plan")
        if isinstance(executable_module_graph.get("execution_plan"), dict)
        else {}
    )
    side_compositions = {
        side: build_side_composition(
            side,
            executable_module_graph.get("side_graphs", {}).get(side)
            if isinstance(executable_module_graph.get("side_graphs"), dict)
            else {},
            list(execution_plan.get(side) or []),
        )
        for side in ("a", "b")
    }
    spec: dict[str, Any] = {
        "schema_version": EXECUTABLE_COMPOSITION_SCHEMA_VERSION,
        "composition_policy": "module_graph_to_standard_module_pipeline/v1",
        "composition_model": "side_by_side_standard_module_pipeline",
        "source_module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "source_module_graph_self_hash": executable_module_graph.get("module_graph_sha256")
        if executable_module_graph
        else None,
        "source_pair_ir_sha256": executable_module_graph.get("source_pair_ir_sha256")
        if executable_module_graph
        else None,
        "source_probe_plan_sha256": canonical_sha256(module_probe_plan) if module_probe_plan else None,
        "source_probe_plan_self_hash": module_probe_plan.get("plan_sha256") if module_probe_plan else None,
        "execution_plan_binding": {
            "plan_kind": execution_plan.get("plan_kind") if execution_plan else None,
            "a": list(execution_plan.get("a") or []) if execution_plan else [],
            "b": list(execution_plan.get("b") or []) if execution_plan else [],
            "requires_compilation_verification": execution_plan.get("requires_compilation_verification")
            if execution_plan
            else None,
            "requires_runtime_oracle": execution_plan.get("requires_runtime_oracle") if execution_plan else None,
        },
        "side_compositions": side_compositions,
        "cross_side_alignment": build_cross_side_alignment(executable_module_graph),
        "observation_requirements": build_observation_requirements(module_probe_plan),
        "environment_requirements": build_environment_requirements(side_compositions),
        "lowering_contract": {
            "semantic_source": "executable_module_graph",
            "programmatic_lowering_required": True,
            "raw_source_patch_allowed": False,
            "llm_module_rewrite_allowed": False,
            "method_fragment_retained_for_compilation_boundary": True,
            "target_backend": "module_graph_generated_harness",
            "current_backend_boundary": "retained_snippet_methods_called_through_standard_module_plan",
        },
        "llm_contract": {
            "clone_decision_allowed": False,
            "raw_source_patch_allowed": False,
            "allowed_roles": ["module_interface_disambiguation", "probe_synthesis_for_uncovered_obligations"],
        },
        "limitations": [
            "composition steps bind the standard module order and ports; the current Java backend still retains original method bodies as compilation boundaries",
            "full elimination of SnippetA/SnippetB wrappers requires a later module-graph-to-Java lowering backend",
        ],
    }
    spec[EXECUTABLE_COMPOSITION_HASH_FIELD] = canonical_sha256(
        {key: value for key, value in spec.items() if key != EXECUTABLE_COMPOSITION_HASH_FIELD}
    )
    return spec


def build_side_composition(side: str, side_graph: dict[str, Any], plan: list[Any]) -> dict[str, Any]:
    nodes = [node for node in side_graph.get("nodes") or [] if isinstance(node, dict)]
    by_id = {str(node.get("module_id")): node for node in nodes}
    ordered_ids = [str(module_id) for module_id in plan if str(module_id) in by_id]
    if not ordered_ids:
        ordered_ids = [str(node.get("module_id")) for node in nodes if node.get("module_id")]
    steps = [build_module_step(index, by_id[module_id]) for index, module_id in enumerate(ordered_ids)]
    side_spec = {
        "side": side,
        "source_side_graph_sha256": canonical_sha256(side_graph) if side_graph else None,
        "source_side_graph_self_hash": side_graph.get("side_graph_sha256") if side_graph else None,
        "method": side_graph.get("method") if side_graph else None,
        "module_count": len(steps),
        "steps": steps,
        "input_ports": sorted(unique_ports(steps, "input_ports")),
        "state_channels": sorted(
            port
            for step in steps
            for port in step.get("output_ports") or []
            if isinstance(port, str) and port != "return"
        ),
        "environment_adapters": sorted(unique_ports(steps, "environment_ports")),
        "observation_sinks": sorted(
            {
                obligation
                for step in steps
                for obligation in step.get("observation_obligations") or []
                if isinstance(obligation, str)
            }
        ),
    }
    side_spec["side_composition_sha256"] = canonical_sha256(
        {key: value for key, value in side_spec.items() if key != "side_composition_sha256"}
    )
    return side_spec


def build_module_step(index: int, node: dict[str, Any]) -> dict[str, Any]:
    module_type = str(node.get("module_type") or "pure_computation")
    interface = node.get("interface") if isinstance(node.get("interface"), dict) else {}
    step = {
        "step_index": index,
        "step_id": f"{node.get('module_id')}.step",
        "module_id": node.get("module_id"),
        "module_type": module_type,
        "execution_role": node.get("execution_role"),
        "standard_combinator": MODULE_COMBINATORS.get(module_type, "compute_pure_value"),
        "source_block_sha256": node.get("source_block_sha256"),
        "source_statement_sha256": node.get("source_statement_sha256"),
        "input_ports": port_names(interface.get("input_ports")),
        "output_ports": port_names(interface.get("output_ports")),
        "environment_ports": port_names(interface.get("environment_ports")),
        "observation_obligations": list(MODULE_OBLIGATIONS.get(module_type, [])),
        "lowering_requirements": lowering_requirements(module_type),
    }
    step["step_sha256"] = canonical_sha256({key: value for key, value in step.items() if key != "step_sha256"})
    return step


def lowering_requirements(module_type: str) -> list[str]:
    requirements = ["preserve_input_output_ports", "preserve_source_block_hash"]
    if module_type == "environment_interaction":
        requirements.append("bind_environment_adapter_or_fixture")
    if module_type in {"branch_guard", "collection_iteration", "iteration"}:
        requirements.append("preserve_control_path_observation")
    if module_type == "return_mapping":
        requirements.append("bind_return_observation")
    return requirements


def build_cross_side_alignment(executable_module_graph: dict[str, Any]) -> dict[str, Any]:
    hints = (
        executable_module_graph.get("alignment_hints")
        if isinstance(executable_module_graph.get("alignment_hints"), dict)
        else {}
    )
    return {
        "alignment_sha256": hints.get("alignment_sha256") if hints else None,
        "aligned_module_count": hints.get("aligned_module_count") if hints else 0,
        "aligned_modules": list(hints.get("aligned_modules") or []) if hints else [],
        "unmatched_a": list(hints.get("unmatched_a") or []) if hints else [],
        "unmatched_b": list(hints.get("unmatched_b") or []) if hints else [],
    }


def build_observation_requirements(module_probe_plan: dict[str, Any]) -> dict[str, Any]:
    obligations = (
        module_probe_plan.get("obligations")
        if isinstance(module_probe_plan.get("obligations"), dict)
        else {}
    )
    coverage = module_probe_plan.get("coverage") if isinstance(module_probe_plan.get("coverage"), dict) else {}
    risk = module_probe_plan.get("risk") if isinstance(module_probe_plan.get("risk"), dict) else {}
    return {
        "required_observations": list(obligations.get("required_observations") or []),
        "covered_obligations": list(coverage.get("covered_obligations") or []),
        "uncovered_obligations": list(coverage.get("uncovered_obligations") or []),
        "requires_llm_probe_synthesis": coverage.get("requires_llm_probe_synthesis") if coverage else None,
        "risk_level": risk.get("level") if risk else None,
    }


def build_environment_requirements(side_compositions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    by_side = {
        side: list(spec.get("environment_adapters") or [])
        for side, spec in side_compositions.items()
        if isinstance(spec, dict)
    }
    all_adapters = sorted({adapter for adapters in by_side.values() for adapter in adapters})
    return {
        "required_environment_adapters": all_adapters,
        "by_side": by_side,
        "fixture_or_mock_required": bool(all_adapters),
    }


def verify_executable_composition_spec(
    spec: dict[str, Any],
    *,
    executable_module_graph: dict[str, Any] | None = None,
    module_probe_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues: list[str] = []
    if spec.get("schema_version") != EXECUTABLE_COMPOSITION_SCHEMA_VERSION:
        issues.append("schema_version_mismatch")
    expected = canonical_sha256({key: value for key, value in spec.items() if key != EXECUTABLE_COMPOSITION_HASH_FIELD})
    if spec.get(EXECUTABLE_COMPOSITION_HASH_FIELD) != expected:
        issues.append("composition_sha256_mismatch")
    llm_contract = spec.get("llm_contract") if isinstance(spec.get("llm_contract"), dict) else {}
    if llm_contract.get("clone_decision_allowed") is not False:
        issues.append("llm_clone_decision_not_forbidden")
    if llm_contract.get("raw_source_patch_allowed") is not False:
        issues.append("llm_raw_source_patch_not_forbidden")
    lowering_contract = spec.get("lowering_contract") if isinstance(spec.get("lowering_contract"), dict) else {}
    if lowering_contract.get("raw_source_patch_allowed") is not False:
        issues.append("lowering_allows_raw_source_patch")
    if lowering_contract.get("llm_module_rewrite_allowed") is not False:
        issues.append("lowering_allows_llm_module_rewrite")

    if executable_module_graph is not None:
        if spec.get("source_module_graph_sha256") != canonical_sha256(executable_module_graph):
            issues.append("source_module_graph_sha256_mismatch")
        if spec.get("source_module_graph_self_hash") != executable_module_graph.get("module_graph_sha256"):
            issues.append("source_module_graph_self_hash_mismatch")
        execution_plan = (
            executable_module_graph.get("execution_plan")
            if isinstance(executable_module_graph.get("execution_plan"), dict)
            else {}
        )
        plan_binding = spec.get("execution_plan_binding") if isinstance(spec.get("execution_plan_binding"), dict) else {}
        if list(plan_binding.get("a") or []) != list(execution_plan.get("a") or []):
            issues.append("execution_plan_a_mismatch")
        if list(plan_binding.get("b") or []) != list(execution_plan.get("b") or []):
            issues.append("execution_plan_b_mismatch")
        issues.extend(verify_side_compositions(spec, executable_module_graph))

    if module_probe_plan is not None:
        expected_plan_sha = canonical_sha256(module_probe_plan) if module_probe_plan else None
        if spec.get("source_probe_plan_sha256") != expected_plan_sha:
            issues.append("source_probe_plan_sha256_mismatch")
        if module_probe_plan and spec.get("source_probe_plan_self_hash") != module_probe_plan.get("plan_sha256"):
            issues.append("source_probe_plan_self_hash_mismatch")
    return {"status": "verified" if not issues else "rejected", "issues": issues}


def verify_side_compositions(spec: dict[str, Any], executable_module_graph: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    side_specs = spec.get("side_compositions") if isinstance(spec.get("side_compositions"), dict) else {}
    side_graphs = (
        executable_module_graph.get("side_graphs")
        if isinstance(executable_module_graph.get("side_graphs"), dict)
        else {}
    )
    for side in ("a", "b"):
        side_spec = side_specs.get(side) if isinstance(side_specs.get(side), dict) else {}
        if not side_spec:
            issues.append(f"{side}:side_composition_missing")
            continue
        expected_side_sha = canonical_sha256(
            {key: value for key, value in side_spec.items() if key != "side_composition_sha256"}
        )
        if side_spec.get("side_composition_sha256") != expected_side_sha:
            issues.append(f"{side}:side_composition_sha256_mismatch")
        side_graph = side_graphs.get(side) if isinstance(side_graphs.get(side), dict) else {}
        if side_spec.get("source_side_graph_sha256") != canonical_sha256(side_graph):
            issues.append(f"{side}:source_side_graph_sha256_mismatch")
        node_count = len([node for node in side_graph.get("nodes") or [] if isinstance(node, dict)])
        if side_spec.get("module_count") != node_count:
            issues.append(f"{side}:module_count_mismatch")
        for step in side_spec.get("steps") or []:
            if not isinstance(step, dict):
                issues.append(f"{side}:step_not_object")
                continue
            expected_step_sha = canonical_sha256({key: value for key, value in step.items() if key != "step_sha256"})
            if step.get("step_sha256") != expected_step_sha:
                issues.append(f"{side}:step_sha256_mismatch")
    return issues


def port_names(ports: Any) -> list[str]:
    return [
        str(port.get("name"))
        for port in ports or []
        if isinstance(port, dict) and port.get("name")
    ]


def unique_ports(steps: list[dict[str, Any]], key: str) -> set[str]:
    return {
        str(port)
        for step in steps
        for port in step.get(key) or []
        if isinstance(port, str) and port
    }


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
