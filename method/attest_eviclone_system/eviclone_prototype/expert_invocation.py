from __future__ import annotations

import hashlib
from typing import Any


SCHEMA_VERSION = "eviclone-llm-expert-invocation/v1"
INVOCATION_HASH_FIELD = "invocation_sha256"
INPUT_FIREWALL_SCHEMA_VERSION = "eviclone-llm-expert-input-firewall/v1"
INPUT_FIREWALL_POLICY = "no_gold_base_or_final_decision_inputs/v1"
INPUT_FIREWALL_HASH_FIELD = "firewall_sha256"
MODEL_CONFIG_SCHEMA_VERSION = "eviclone-llm-expert-model-config/v1"
MODULE_GRAPH_INPUT_BINDING_SCHEMA_VERSION = "eviclone-llm-expert-module-graph-input-binding/v1"
MODULE_GRAPH_INPUT_BINDING_HASH_FIELD = "binding_sha256"

SENSITIVE_DECISION_INPUT_KEYS = {
    "gold",
    "gold_label",
    "bcb_gold",
    "bcb_gold_label",
    "bcb_gold_verdict",
    "benchmark_label",
    "label",
    "pred",
    "pred_label",
    "prediction",
    "base_prediction",
    "base_model_prediction",
    "clone_label",
    "is_clone",
    "semantic_verdict",
    "decision",
    "final_label",
    "final_decision",
    "final_pred",
}


def build_expert_invocation(
    *,
    expert_role: str,
    expert_contract: str,
    system_prompt: str,
    user_prompt: str,
    status: str,
    output_kind: str,
    output_sha256: str | None = None,
    raw_response: str | None = None,
    validation_errors: list[str] | None = None,
    input_firewall: dict[str, Any] | None = None,
    model_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a non-secret provenance certificate for an LLM expert call."""
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "expert_role": expert_role,
        "expert_contract": expert_contract,
        "status": status,
        "output_kind": output_kind,
        "system_prompt_sha256": sha256_text(system_prompt),
        "user_prompt_sha256": sha256_text(user_prompt),
        "prompt_pair_sha256": sha256_text(system_prompt + "\n---USER---\n" + user_prompt),
        "raw_response_sha256": sha256_text(raw_response or "") if raw_response is not None else None,
        "output_sha256": output_sha256,
        "validation_passed": status == "completed" and not validation_errors,
        "validation_errors": validation_errors or [],
    }
    if isinstance(input_firewall, dict):
        firewall = dict(input_firewall)
        firewall.setdefault("user_prompt_sha256", result["user_prompt_sha256"])
        firewall[INPUT_FIREWALL_HASH_FIELD] = build_input_firewall_hash(firewall)
        result["input_firewall"] = firewall
    if isinstance(model_config, dict):
        result["model_config"] = model_config
    result[INVOCATION_HASH_FIELD] = build_expert_invocation_hash(result)
    return result


def build_expert_invocation_hash(invocation: dict[str, Any]) -> str:
    """Hash an expert invocation certificate excluding its self-hash field."""
    return sha256_json({key: value for key, value in invocation.items() if key != INVOCATION_HASH_FIELD})


def build_input_firewall_hash(input_firewall: dict[str, Any]) -> str:
    """Hash an input firewall certificate excluding its self-hash field."""
    return sha256_json({key: value for key, value in input_firewall.items() if key != INPUT_FIREWALL_HASH_FIELD})


def build_model_config_certificate(client: Any) -> dict[str, Any]:
    """Record non-secret LLM runtime configuration for expert provenance."""
    config = getattr(client, "config", None)
    if config is None:
        payload: dict[str, Any] = {
            "schema_version": MODEL_CONFIG_SCHEMA_VERSION,
            "available": False,
            "client_class": type(client).__name__,
            "reason": "client_has_no_config",
        }
        payload["config_sha256"] = sha256_json({key: value for key, value in payload.items() if key != "config_sha256"})
        return payload

    endpoint_url = str(getattr(config, "endpoint_url", "") or "")
    payload = {
        "schema_version": MODEL_CONFIG_SCHEMA_VERSION,
        "available": True,
        "client_class": type(client).__name__,
        "base_url": str(getattr(config, "base_url", "") or ""),
        "endpoint_url": endpoint_url,
        "endpoint_url_sha256": sha256_text(endpoint_url),
        "model": str(getattr(config, "model", "") or ""),
        "temperature": getattr(config, "temperature", None),
        "max_tokens": getattr(config, "max_tokens", None),
        "thinking_type": getattr(config, "thinking_type", None),
        "timeout_sec": getattr(config, "timeout_sec", None),
        "api_key_env": str(getattr(config, "api_key_env", "") or ""),
    }
    payload["config_sha256"] = sha256_json({key: value for key, value in payload.items() if key != "config_sha256"})
    return payload


def sanitize_expert_input_fragment(value: Any, *, root: str) -> tuple[Any, list[dict[str, str]], list[dict[str, str]]]:
    """Remove answer-bearing metadata before it can be sent to an LLM expert.

    The scanner works on structured prompt metadata, not arbitrary source text.
    Java snippets are passed as strings elsewhere, so user code identifiers are
    not mistaken for benchmark labels.
    """
    redacted: list[dict[str, str]] = []
    renamed: list[dict[str, str]] = []

    def visit(node: Any, path: tuple[str, ...]) -> Any:
        if isinstance(node, dict):
            output: dict[str, Any] = {}
            for key, child in node.items():
                key_text = str(key)
                normalized = normalize_key(key_text)
                current_path = path + (key_text,)
                if normalized == "label" and root == "compile_info" and path == (root,):
                    new_path = path + ("attempt_name",)
                    renamed.append({"from": dotted_path(current_path), "to": dotted_path(new_path)})
                    output["attempt_name"] = visit(child, new_path)
                    continue
                if normalized in SENSITIVE_DECISION_INPUT_KEYS:
                    redacted.append({"path": dotted_path(current_path), "key": key_text})
                    continue
                output[key_text] = visit(child, current_path)
            return output
        if isinstance(node, list):
            return [visit(item, path + (str(index),)) for index, item in enumerate(node)]
        return node

    return visit(value, (root,)), redacted, renamed


def build_input_firewall_certificate(
    *,
    expert_role: str,
    prompt_obj: dict[str, Any],
    redacted_sensitive_paths: list[dict[str, str]] | None = None,
    renamed_nonsemantic_paths: list[dict[str, str]] | None = None,
    module_graph_input_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    visible = find_visible_sensitive_input_paths(prompt_obj)
    result = {
        "schema_version": INPUT_FIREWALL_SCHEMA_VERSION,
        "policy": INPUT_FIREWALL_POLICY,
        "expert_role": expert_role,
        "status": "passed" if not visible else "failed",
        "decision_inputs_visible": bool(visible),
        "visible_sensitive_paths": visible[:50],
        "redacted_sensitive_paths": (redacted_sensitive_paths or [])[:50],
        "renamed_nonsemantic_paths": (renamed_nonsemantic_paths or [])[:50],
    }
    if isinstance(module_graph_input_binding, dict):
        result["module_graph_input_binding"] = module_graph_input_binding
    result[INPUT_FIREWALL_HASH_FIELD] = build_input_firewall_hash(result)
    return result


def build_module_graph_input_binding(meta: dict[str, Any]) -> dict[str, Any]:
    module_graph = meta.get("executable_module_graph") if isinstance(meta.get("executable_module_graph"), dict) else {}
    pair_ir = meta.get("functional_block_pair_ir") if isinstance(meta.get("functional_block_pair_ir"), dict) else {}
    if not module_graph:
        binding = {
            "schema_version": MODULE_GRAPH_INPUT_BINDING_SCHEMA_VERSION,
            "present": False,
            "source": "current_harness_meta.executable_module_graph",
            "module_graph_sha256": None,
            "module_graph_self_hash": None,
            "source_pair_ir_sha256": None,
            "source_pair_ir_self_hash": pair_ir.get("pair_ir_sha256") if pair_ir else None,
            "execution_plan_sha256": None,
            "llm_clone_decision_allowed": None,
            "raw_source_patch_allowed": None,
        }
        binding[MODULE_GRAPH_INPUT_BINDING_HASH_FIELD] = sha256_json(
            {key: value for key, value in binding.items() if key != MODULE_GRAPH_INPUT_BINDING_HASH_FIELD}
        )
        return binding

    execution_plan = module_graph.get("execution_plan") if isinstance(module_graph.get("execution_plan"), dict) else {}
    llm_contract = module_graph.get("llm_contract") if isinstance(module_graph.get("llm_contract"), dict) else {}
    binding = {
        "schema_version": MODULE_GRAPH_INPUT_BINDING_SCHEMA_VERSION,
        "present": True,
        "source": "current_harness_meta.executable_module_graph",
        "module_graph_sha256": sha256_json(module_graph),
        "module_graph_self_hash": module_graph.get("module_graph_sha256"),
        "source_pair_ir_sha256": module_graph.get("source_pair_ir_sha256"),
        "source_pair_ir_self_hash": module_graph.get("source_pair_ir_self_hash") or (pair_ir.get("pair_ir_sha256") if pair_ir else None),
        "execution_plan_sha256": sha256_json(execution_plan),
        "plan_a_count": len(execution_plan.get("a") or []) if isinstance(execution_plan.get("a"), list) else 0,
        "plan_b_count": len(execution_plan.get("b") or []) if isinstance(execution_plan.get("b"), list) else 0,
        "llm_clone_decision_allowed": llm_contract.get("clone_decision_allowed"),
        "raw_source_patch_allowed": llm_contract.get("raw_source_patch_allowed"),
        "allowed_roles": list(llm_contract.get("allowed_roles") or []),
    }
    binding[MODULE_GRAPH_INPUT_BINDING_HASH_FIELD] = sha256_json(
        {key: value for key, value in binding.items() if key != MODULE_GRAPH_INPUT_BINDING_HASH_FIELD}
    )
    return binding


def input_firewall_block_reasons(input_firewall: dict[str, Any] | None) -> list[str]:
    if not isinstance(input_firewall, dict):
        return ["input_firewall_missing"]
    reasons: list[str] = []
    if input_firewall.get("status") != "passed":
        reasons.append("input_firewall_not_passed")
    if input_firewall.get("decision_inputs_visible") is not False:
        reasons.append("input_firewall_decision_inputs_visible")
    if input_firewall.get("visible_sensitive_paths") not in (None, []):
        reasons.append("input_firewall_visible_sensitive_paths")
    return reasons


def find_visible_sensitive_input_paths(value: Any) -> list[dict[str, str]]:
    visible: list[dict[str, str]] = []

    def visit(node: Any, path: tuple[str, ...]) -> None:
        if path and path[0] in {"expert_input_policy", "required_json_schema", "forbidden_json_fields"}:
            return
        if isinstance(node, dict):
            for key, child in node.items():
                key_text = str(key)
                current_path = path + (key_text,)
                if normalize_key(key_text) in SENSITIVE_DECISION_INPUT_KEYS:
                    visible.append({"path": dotted_path(current_path), "key": key_text})
                    continue
                visit(child, current_path)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                visit(item, path + (str(index),))

    visit(value, ())
    return visible


def find_forbidden_key_paths(value: Any, forbidden_keys: set[str]) -> list[dict[str, str]]:
    forbidden = {normalize_key(key) for key in forbidden_keys}
    visible: list[dict[str, str]] = []

    def visit(node: Any, path: tuple[str, ...]) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                key_text = str(key)
                current_path = path + (key_text,)
                if normalize_key(key_text) in forbidden:
                    visible.append({"path": dotted_path(current_path), "key": key_text})
                    continue
                visit(child, current_path)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                visit(item, path + (str(index),))

    visit(value, ())
    return visible


def expert_input_policy(role: str) -> dict[str, Any]:
    return {
        "schema_version": INPUT_FIREWALL_SCHEMA_VERSION,
        "policy": INPUT_FIREWALL_POLICY,
        "expert_role": role,
        "allowed_semantic_inputs": [
            "method snippets",
            "benchmark-style functionality description",
            "current generated Java harness",
            "compiler diagnostics",
            "harness metadata that is not a prediction or gold label",
            "functional block IR and executable module graph certificates",
            "standard module interfaces, execution plans, and environment adapter hints",
        ],
        "hidden_semantic_inputs": [
            "benchmark gold label",
            "base model prediction",
            "current final decision",
            "clone/non-clone labels from any upstream judge",
        ],
    }


def normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def dotted_path(path: tuple[str, ...]) -> str:
    return ".".join(path)


def failed_expert_invocation(
    *,
    expert_role: str,
    expert_contract: str,
    system_prompt: str,
    user_prompt: str,
    error: Exception,
    model_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_expert_invocation(
        expert_role=expert_role,
        expert_contract=expert_contract,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        status="failed",
        output_kind="none",
        raw_response=None,
        validation_errors=[str(error)],
        model_config=model_config,
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()


def sha256_json(value: Any) -> str:
    import json

    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()
