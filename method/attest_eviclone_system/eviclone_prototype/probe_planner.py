from __future__ import annotations

import hashlib
import json
from typing import Any


MODULE_PROBE_PLAN_SCHEMA_VERSION = "eviclone-module-probe-plan/v1"
MODULE_PROBE_PLAN_HASH_FIELD = "plan_sha256"


def build_module_probe_plan(
    executable_module_graph: dict[str, Any],
    probe_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    probe_contract = probe_contract if isinstance(probe_contract, dict) else {}
    obligations = derive_probe_obligations(executable_module_graph)
    coverage = evaluate_probe_coverage(obligations, probe_contract)
    plan: dict[str, Any] = {
        "schema_version": MODULE_PROBE_PLAN_SCHEMA_VERSION,
        "construction_policy": "deterministic_module_graph_probe_obligation_mapping/v1",
        "source_module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "source_module_graph_self_hash": executable_module_graph.get("module_graph_sha256") if executable_module_graph else None,
        "source_pair_ir_sha256": executable_module_graph.get("source_pair_ir_sha256") if executable_module_graph else None,
        "source_probe_contract_sha256": canonical_sha256(probe_contract) if probe_contract else None,
        "source_probe_contract_self_hash": probe_contract.get("contract_sha256") if probe_contract else None,
        "probe_family": probe_contract.get("probe_family") if probe_contract else None,
        "probe_factory": probe_contract.get("probe_factory") if probe_contract else None,
        "obligations": obligations,
        "coverage": coverage,
        "risk": probe_plan_risk(coverage),
        "llm_contract": {
            "clone_decision_allowed": False,
            "raw_source_patch_allowed": False,
            "allowed_roles": ["probe_synthesis_for_uncovered_obligations", "module_interface_disambiguation"],
        },
        "limitations": [
            "probe obligations are derived from standardized module graph categories, not a full path-sensitive Java semantics proof",
            "coverage is bounded evidence planning; compile and runtime certificates remain required for trust",
        ],
    }
    plan[MODULE_PROBE_PLAN_HASH_FIELD] = canonical_sha256(
        {key: value for key, value in plan.items() if key != MODULE_PROBE_PLAN_HASH_FIELD}
    )
    return plan


def derive_probe_obligations(executable_module_graph: dict[str, Any]) -> dict[str, Any]:
    nodes = all_module_nodes(executable_module_graph)
    module_types = sorted({str(node.get("module_type")) for node in nodes if node.get("module_type")})
    observation_obligations: list[str] = []
    if any(node.get("module_type") == "return_mapping" for node in nodes):
        observation_obligations.append("return_value")
    if any(node.get("observability", {}).get("can_affect_state") for node in nodes):
        observation_obligations.append("state_mutation")
    if any(node.get("observability", {}).get("environment_dependent") for node in nodes):
        observation_obligations.append("environment_effect")
    if any(node.get("module_type") == "branch_guard" for node in nodes):
        observation_obligations.append("branch_path")
    if any(node.get("module_type") == "collection_iteration" for node in nodes):
        observation_obligations.append("collection_iteration_path")
    environment_adapters = sorted(
        {
            str(port.get("name"))
            for node in nodes
            for port in node.get("interface", {}).get("environment_ports", [])
            if isinstance(port, dict) and port.get("name")
        }
    )
    input_ports = sorted(
        {
            str(port.get("name"))
            for node in nodes
            for port in node.get("interface", {}).get("input_ports", [])
            if isinstance(port, dict) and port.get("name")
        }
    )
    return {
        "module_types": module_types,
        "required_observations": observation_obligations,
        "required_environment_adapters": environment_adapters,
        "required_input_ports": input_ports,
        "side_a_module_count": side_module_count(executable_module_graph, "a"),
        "side_b_module_count": side_module_count(executable_module_graph, "b"),
    }


def evaluate_probe_coverage(obligations: dict[str, Any], probe_contract: dict[str, Any]) -> dict[str, Any]:
    observation_kind = str(probe_contract.get("observation_kind") or "")
    input_profile = probe_contract.get("input_profile") if isinstance(probe_contract.get("input_profile"), dict) else {}
    framework_mocks = [str(item) for item in probe_contract.get("framework_mocks") or [] if str(item)]
    observable_count = len(input_profile.get("observable_parameter_indexes") or [])
    case_count = input_profile.get("case_count") if isinstance(input_profile.get("case_count"), int) else None
    required = [str(item) for item in obligations.get("required_observations") or []]
    covered: list[str] = []
    if "return_value" in required and ("return_value" in observation_kind or "value_equivalence" in observation_kind):
        covered.append("return_value")
    if "state_mutation" in required and (
        observable_count > 0 or "state" in observation_kind or "mutation" in observation_kind
    ):
        covered.append("state_mutation")
    if "environment_effect" in required and (
        framework_mocks or "file_effect" in observation_kind or "http" in observation_kind or "effect" in observation_kind
    ):
        covered.append("environment_effect")
    if "branch_path" in required and case_count is not None and case_count >= 2:
        covered.append("branch_path")
    if "collection_iteration_path" in required and case_count is not None and case_count >= 1:
        covered.append("collection_iteration_path")
    uncovered = [item for item in required if item not in covered]
    return {
        "observation_kind": observation_kind or None,
        "case_count": case_count,
        "observable_parameter_count": observable_count,
        "covered_obligations": covered,
        "uncovered_obligations": uncovered,
        "coverage_ratio": len(covered) / len(required) if required else 1.0,
        "requires_llm_probe_synthesis": bool(uncovered),
    }


def probe_plan_risk(coverage: dict[str, Any]) -> dict[str, Any]:
    uncovered = [str(item) for item in coverage.get("uncovered_obligations") or []]
    if not uncovered:
        level = "low"
    elif "environment_effect" in uncovered:
        level = "high"
    else:
        level = "medium"
    return {
        "level": level,
        "uncovered_obligation_count": len(uncovered),
        "uncovered_obligations": uncovered,
    }


def verify_module_probe_plan(
    plan: dict[str, Any],
    *,
    executable_module_graph: dict[str, Any] | None = None,
    probe_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues: list[str] = []
    if plan.get("schema_version") != MODULE_PROBE_PLAN_SCHEMA_VERSION:
        issues.append("schema_version_mismatch")
    expected_plan_sha = canonical_sha256({key: value for key, value in plan.items() if key != MODULE_PROBE_PLAN_HASH_FIELD})
    if plan.get(MODULE_PROBE_PLAN_HASH_FIELD) != expected_plan_sha:
        issues.append("plan_sha256_mismatch")
    if plan.get("llm_contract", {}).get("clone_decision_allowed") is not False:
        issues.append("llm_clone_decision_not_forbidden")
    if plan.get("llm_contract", {}).get("raw_source_patch_allowed") is not False:
        issues.append("llm_raw_source_patch_not_forbidden")
    if executable_module_graph is not None:
        expected_graph_sha = canonical_sha256(executable_module_graph)
        if plan.get("source_module_graph_sha256") != expected_graph_sha:
            issues.append("source_module_graph_sha256_mismatch")
        if plan.get("source_module_graph_self_hash") != executable_module_graph.get("module_graph_sha256"):
            issues.append("source_module_graph_self_hash_mismatch")
    if probe_contract is not None:
        expected_contract_sha = canonical_sha256(probe_contract) if probe_contract else None
        if plan.get("source_probe_contract_sha256") != expected_contract_sha:
            issues.append("source_probe_contract_sha256_mismatch")
        if probe_contract and plan.get("source_probe_contract_self_hash") != probe_contract.get("contract_sha256"):
            issues.append("source_probe_contract_self_hash_mismatch")
    return {"status": "verified" if not issues else "rejected", "issues": issues}


def all_module_nodes(executable_module_graph: dict[str, Any]) -> list[dict[str, Any]]:
    side_graphs = executable_module_graph.get("side_graphs") if isinstance(executable_module_graph.get("side_graphs"), dict) else {}
    nodes: list[dict[str, Any]] = []
    for side in ("a", "b"):
        side_graph = side_graphs.get(side) if isinstance(side_graphs.get(side), dict) else {}
        nodes.extend([node for node in side_graph.get("nodes") or [] if isinstance(node, dict)])
    return nodes


def side_module_count(executable_module_graph: dict[str, Any], side: str) -> int:
    side_graphs = executable_module_graph.get("side_graphs") if isinstance(executable_module_graph.get("side_graphs"), dict) else {}
    side_graph = side_graphs.get(side) if isinstance(side_graphs.get(side), dict) else {}
    return len(side_graph.get("nodes") or [])


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
