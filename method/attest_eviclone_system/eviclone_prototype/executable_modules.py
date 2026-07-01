from __future__ import annotations

import hashlib
import json
from typing import Any


EXECUTABLE_MODULE_GRAPH_SCHEMA_VERSION = "eviclone-executable-module-graph/v1"
EXECUTABLE_MODULE_GRAPH_HASH_FIELD = "module_graph_sha256"

MODULE_EXECUTION_ROLES = {
    "input_normalization": "normalize_or_parse_input",
    "branch_guard": "select_control_path",
    "collection_iteration": "iterate_collection_elements",
    "iteration": "iterate_control_flow",
    "state_update": "update_local_or_observable_state",
    "collection_transform": "transform_collection_values",
    "environment_interaction": "call_environment_adapter",
    "exception_boundary": "model_exception_boundary",
    "return_mapping": "produce_observable_return",
    "pure_computation": "compute_pure_value",
}


def build_executable_module_graph(functional_block_pair_ir: dict[str, Any]) -> dict[str, Any]:
    side_graphs = {
        "a": build_side_module_graph("a", functional_block_pair_ir.get("a") if isinstance(functional_block_pair_ir.get("a"), dict) else {}),
        "b": build_side_module_graph("b", functional_block_pair_ir.get("b") if isinstance(functional_block_pair_ir.get("b"), dict) else {}),
    }
    graph: dict[str, Any] = {
        "schema_version": EXECUTABLE_MODULE_GRAPH_SCHEMA_VERSION,
        "source_ir_schema_version": functional_block_pair_ir.get("schema_version"),
        "source_pair_ir_sha256": canonical_sha256(functional_block_pair_ir) if functional_block_pair_ir else None,
        "source_pair_ir_self_hash": functional_block_pair_ir.get("pair_ir_sha256"),
        "construction_policy": "deterministic_functional_blocks_to_standard_modules/v1",
        "side_graphs": side_graphs,
        "alignment_hints": build_alignment_hints(side_graphs),
        "execution_plan": {
            "a": [node["module_id"] for node in side_graphs["a"]["nodes"]],
            "b": [node["module_id"] for node in side_graphs["b"]["nodes"]],
            "plan_kind": "side_by_side_shared_probe_execution",
            "requires_compilation_verification": True,
            "requires_runtime_oracle": True,
        },
        "llm_contract": {
            "clone_decision_allowed": False,
            "raw_source_patch_allowed": False,
            "allowed_roles": ["module_interface_disambiguation", "missing_context_completion", "probe_synthesis"],
            "must_preserve_module_io": True,
        },
        "limitations": [
            "module graph is derived from deterministic functional blocks and inherits their lexical approximation limits",
            "graph execution remains certified only after generated Java harness compilation and runtime oracle verification",
        ],
    }
    graph[EXECUTABLE_MODULE_GRAPH_HASH_FIELD] = canonical_sha256(
        {key: value for key, value in graph.items() if key != EXECUTABLE_MODULE_GRAPH_HASH_FIELD}
    )
    return graph


def build_side_module_graph(side: str, side_ir: dict[str, Any]) -> dict[str, Any]:
    blocks = [block for block in side_ir.get("blocks") or [] if isinstance(block, dict)]
    nodes = [build_module_node(side, block) for block in blocks]
    block_to_module = {node["source_block_id"]: node["module_id"] for node in nodes}
    edges = []
    for edge in side_ir.get("edges") or []:
        if not isinstance(edge, dict):
            continue
        src = block_to_module.get(str(edge.get("src") or ""))
        dst = block_to_module.get(str(edge.get("dst") or ""))
        if not src or not dst:
            continue
        module_edge = {
            "src": src,
            "dst": dst,
            "kind": edge.get("kind"),
            "variables": list(edge.get("variables") or []),
            "source_edge_sha256": edge.get("edge_sha256"),
        }
        module_edge["edge_sha256"] = canonical_sha256(module_edge)
        edges.append(module_edge)
    graph = {
        "side": side,
        "source_ir_sha256": canonical_sha256(side_ir) if side_ir else None,
        "source_ir_self_hash": side_ir.get("ir_sha256"),
        "method": side_ir.get("method"),
        "nodes": nodes,
        "edges": edges,
        "module_signature": [node["module_type"] for node in nodes],
        "module_count": len(nodes),
        "edge_count": len(edges),
    }
    graph["side_graph_sha256"] = canonical_sha256(graph)
    return graph


def build_module_node(side: str, block: dict[str, Any]) -> dict[str, Any]:
    module_type = str(block.get("kind") or "pure_computation")
    node = {
        "module_id": f"{side}.{block.get('block_id')}",
        "side": side,
        "source_block_id": block.get("block_id"),
        "source_block_sha256": block.get("block_sha256"),
        "module_type": module_type,
        "execution_role": MODULE_EXECUTION_ROLES.get(module_type, "compute_pure_value"),
        "interface": {
            "input_ports": [{"name": name, "port_type": "value"} for name in block.get("reads") or []],
            "output_ports": module_output_ports(block),
            "environment_ports": [
                {"name": marker, "port_type": "environment_adapter"} for marker in block.get("api_markers") or []
            ],
        },
        "observability": {
            "can_affect_return": module_type == "return_mapping",
            "can_affect_state": bool(block.get("writes")),
            "environment_dependent": "environment_dependent" in set(block.get("side_effect_markers") or []),
            "side_effect_markers": list(block.get("side_effect_markers") or []),
        },
        "source_statement_sha256": canonical_sha256(str(block.get("statement") or "")),
    }
    node["module_sha256"] = canonical_sha256(node)
    return node


def module_output_ports(block: dict[str, Any]) -> list[dict[str, str]]:
    outputs = [{"name": name, "port_type": "state"} for name in block.get("writes") or []]
    if block.get("kind") == "return_mapping":
        outputs.append({"name": "return", "port_type": "return_value"})
    if block.get("kind") == "environment_interaction":
        outputs.append({"name": "environment_observation", "port_type": "environment"})
    return outputs


def build_alignment_hints(side_graphs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    nodes_a = side_graphs["a"]["nodes"]
    nodes_b = side_graphs["b"]["nodes"]
    by_kind_b: dict[str, list[dict[str, Any]]] = {}
    for node in nodes_b:
        by_kind_b.setdefault(str(node.get("module_type")), []).append(node)
    consumed: set[str] = set()
    aligned = []
    for node_a in nodes_a:
        kind = str(node_a.get("module_type"))
        candidate = next((node for node in by_kind_b.get(kind, []) if str(node.get("module_id")) not in consumed), None)
        if candidate is None:
            continue
        consumed.add(str(candidate.get("module_id")))
        aligned.append(
            {
                "a_module_id": node_a.get("module_id"),
                "b_module_id": candidate.get("module_id"),
                "module_type": kind,
                "match_policy": "same_standard_module_type_first_unconsumed/v1",
            }
        )
    hints = {
        "aligned_module_count": len(aligned),
        "aligned_modules": aligned,
        "unmatched_a": [node["module_id"] for node in nodes_a if node["module_id"] not in {item["a_module_id"] for item in aligned}],
        "unmatched_b": [node["module_id"] for node in nodes_b if node["module_id"] not in {item["b_module_id"] for item in aligned}],
    }
    hints["alignment_sha256"] = canonical_sha256(hints)
    return hints


def verify_executable_module_graph(
    graph: dict[str, Any],
    *,
    functional_block_pair_ir: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues: list[str] = []
    if graph.get("schema_version") != EXECUTABLE_MODULE_GRAPH_SCHEMA_VERSION:
        issues.append("schema_version_mismatch")
    expected = canonical_sha256({key: value for key, value in graph.items() if key != EXECUTABLE_MODULE_GRAPH_HASH_FIELD})
    if graph.get(EXECUTABLE_MODULE_GRAPH_HASH_FIELD) != expected:
        issues.append("module_graph_sha256_mismatch")
    if graph.get("llm_contract", {}).get("clone_decision_allowed") is not False:
        issues.append("llm_clone_decision_not_forbidden")
    if graph.get("llm_contract", {}).get("raw_source_patch_allowed") is not False:
        issues.append("llm_raw_source_patch_not_forbidden")
    if functional_block_pair_ir is not None:
        expected_source_sha = canonical_sha256(functional_block_pair_ir)
        if graph.get("source_pair_ir_sha256") != expected_source_sha:
            issues.append("source_pair_ir_sha256_mismatch")
        if graph.get("source_pair_ir_self_hash") != functional_block_pair_ir.get("pair_ir_sha256"):
            issues.append("source_pair_ir_self_hash_mismatch")
    for side in ("a", "b"):
        side_graph = graph.get("side_graphs", {}).get(side) if isinstance(graph.get("side_graphs"), dict) else {}
        if not isinstance(side_graph, dict) or not side_graph:
            issues.append(f"{side}:side_graph_missing")
            continue
        expected_side_sha = canonical_sha256({key: value for key, value in side_graph.items() if key != "side_graph_sha256"})
        if side_graph.get("side_graph_sha256") != expected_side_sha:
            issues.append(f"{side}:side_graph_sha256_mismatch")
        for node in side_graph.get("nodes") or []:
            if not isinstance(node, dict):
                issues.append(f"{side}:node_not_object")
                continue
            expected_node_sha = canonical_sha256({key: value for key, value in node.items() if key != "module_sha256"})
            if node.get("module_sha256") != expected_node_sha:
                issues.append(f"{side}:module_sha256_mismatch")
    return {"status": "verified" if not issues else "rejected", "issues": issues}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
