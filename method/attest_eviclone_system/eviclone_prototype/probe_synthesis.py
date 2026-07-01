from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any

from .dataset import ClonePair
from .expert_invocation import (
    build_expert_invocation,
    build_input_firewall_certificate,
    build_module_graph_input_binding,
    build_model_config_certificate,
    expert_input_policy,
    find_forbidden_key_paths,
    input_firewall_block_reasons,
    sanitize_expert_input_fragment,
)
from .llm import LLMError, extract_json_object, is_non_retryable_llm_error


PROBE_EXPERT_CONTRACT = "probe_body_only_no_clone_judgment/v1"
PROBE_PAYLOAD_SCHEMA_VERSION = "eviclone-probe-payload-schema/v1"
PROBE_SOURCE_BINDING_SCHEMA_VERSION = "eviclone-probe-source-binding/v1"
PROBE_COMPONENT_ROLE = "llm_probe_synthesis_expert"
PROBE_OUTPUT_KIND = "probe_body"
PROBE_ALLOWED_OUTPUT = "main_body_probe_only"
VALID_PROBE_KINDS = {"value_equivalence", "file_effect", "state_effect", "compile_only"}

PROBE_SYNTHESIS_SYSTEM_PROMPT = """You are a Java dynamic-analysis probe expert.

Your task is to synthesize only the body of EviProbe.main for a deterministic behavior probe.

Rules:
- Return JSON only.
- Do not decide whether the pair is clone or non-clone.
- Do not return verdict, pred_label, clone label, benchmark label, or final decision fields.
- Do not modify SnippetA, SnippetB, imports, helper classes, class fields, or method bodies.
- The probe_body must be Java statements that run inside EviProbe.main.
- Treat the functional block IR and executable module graph as immutable semantic boundaries for choosing inputs and
  observable outputs; do not invent new module behavior.
- The probe_body must call both SnippetA and SnippetB with shared deterministic inputs.
- The probe_body must report through printResult(same, outA, outB) or printStatus(status).
- Do not use external services, real network access, subprocesses, reflection, random, current time, or System.exit.
- If a faithful deterministic shared-input probe cannot be written, return status not_recoverable.
"""


FORBIDDEN_PROBE_DECISION_KEYS = {
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


FORBIDDEN_PROBE_BODY_PATTERNS = [
    r"\bclass\s+\w+",
    r"\binterface\s+\w+",
    r"\bimport\s+",
    r"\bpackage\s+",
    r"\bSystem\.exit\s*\(",
    r"\bRuntime\.getRuntime\s*\(",
    r"\bProcessBuilder\s*\(",
    r"\bnew\s+URL\s*\(",
    r"\bSocket\s*\(",
    r"https?://",
    r"\bRandom\s*\(",
    r"\bSystem\.currentTimeMillis\s*\(",
    r"\bSystem\.nanoTime\s*\(",
    r"\bEVICLONE_RESULT\b",
]


def synthesize_probe_with_llm(
    pair: ClonePair,
    *,
    generated_source: str,
    compile_info: dict[str, Any],
    meta: dict[str, Any],
    client: Any,
    retries: int = 1,
) -> dict[str, Any]:
    prompt, input_firewall = build_probe_synthesis_prompt_with_firewall(
        pair,
        generated_source=generated_source,
        compile_info=compile_info,
        meta=meta,
    )
    last_error: Exception | None = None
    attempts = max(1, int(retries or 1))
    raw_response: str | None = None
    model_config = build_model_config_certificate(client)
    firewall_reasons = input_firewall_block_reasons(input_firewall)
    if firewall_reasons:
        return {
            "status": "rejected",
            "error": "; ".join(firewall_reasons),
            "payload": {},
            "probe_body": "",
            "expert_invocation": build_expert_invocation(
                expert_role="probe_synthesis",
                expert_contract=PROBE_EXPERT_CONTRACT,
                system_prompt=PROBE_SYNTHESIS_SYSTEM_PROMPT,
                user_prompt=prompt,
                status="rejected",
                output_kind="probe_body",
                raw_response=None,
                validation_errors=firewall_reasons,
                input_firewall=input_firewall,
                model_config=model_config,
            ),
        }
    for attempt in range(attempts):
        try:
            raw_response = client.complete(system_prompt=PROBE_SYNTHESIS_SYSTEM_PROMPT, user_prompt=prompt)
            payload = extract_json_object(raw_response)
            return normalize_probe_payload(
                payload,
                system_prompt=PROBE_SYNTHESIS_SYSTEM_PROMPT,
                user_prompt=prompt,
                raw_response=raw_response,
                input_firewall=input_firewall,
                model_config=model_config,
            )
        except (LLMError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if isinstance(exc, LLMError) and is_non_retryable_llm_error(exc):
                break
            if attempt + 1 < attempts:
                time.sleep(probe_retry_wait_seconds(exc, attempt))
    assert last_error is not None
    return {
        "status": "failed",
        "error": str(last_error),
        "payload": {},
        "probe_body": "",
        "expert_invocation": build_expert_invocation(
            expert_role="probe_synthesis",
            expert_contract=PROBE_EXPERT_CONTRACT,
            system_prompt=PROBE_SYNTHESIS_SYSTEM_PROMPT,
            user_prompt=prompt,
            status="failed",
            output_kind="probe_body",
            raw_response=raw_response,
            validation_errors=[str(last_error)],
            input_firewall=input_firewall,
            model_config=model_config,
        ),
    }


def build_probe_synthesis_prompt(
    pair: ClonePair,
    *,
    generated_source: str,
    compile_info: dict[str, Any],
    meta: dict[str, Any],
) -> str:
    prompt, _ = build_probe_synthesis_prompt_with_firewall(
        pair,
        generated_source=generated_source,
        compile_info=compile_info,
        meta=meta,
    )
    return prompt


def build_probe_synthesis_prompt_with_firewall(
    pair: ClonePair,
    *,
    generated_source: str,
    compile_info: dict[str, Any],
    meta: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    safe_compile_info, compile_redactions, compile_renames = sanitize_expert_input_fragment(
        compile_info,
        root="compile_info",
    )
    safe_meta, meta_redactions, meta_renames = sanitize_expert_input_fragment(
        meta,
        root="current_harness_meta",
    )
    module_graph_input_binding = build_module_graph_input_binding(meta)
    obj = {
        "task": "synthesize_main_body_only_for_dynamic_clone_probe",
        "expert_input_policy": expert_input_policy("probe_synthesis"),
        "pair": {
            "bcb_functionality": pair.functionality_name,
            "bcb_description": pair.functionality_description,
        },
        "module_graph_input_binding": module_graph_input_binding,
        "current_harness_meta": safe_meta,
        "compile_info": truncate_obj(safe_compile_info, 8000),
        "snippet_a": limit_text(pair.code_a, 22000),
        "snippet_b": limit_text(pair.code_b, 22000),
        "current_generated_EviProbe_java": limit_text(generated_source, 30000),
        "available_helpers": [
            "printResult(boolean same, String outA, String outB)",
            "printStatus(String status)",
            "normalizeValue(Object value)",
            "b64(byte[] bytes)",
            "work Path variable inside main",
            "mockRequest(), mockSession(), mockConnection(), mockResultSet()",
        ],
        "required_json_schema": {
            "status": "completed or not_recoverable",
            "probe_kind": "value_equivalence or file_effect or state_effect or compile_only",
            "semantic_preservation": {
                "level": "high or medium or low",
                "rationale": "why this probe faithfully compares observable behavior",
                "risk_flags": ["explicit probe limitations"],
            },
            "assumptions": ["deterministic shared-input assumptions"],
            "probe_body": "Java statements for EviProbe.main only",
        },
        "forbidden_json_fields": sorted(FORBIDDEN_PROBE_DECISION_KEYS),
        "important": [
            "Return one JSON object only.",
            "probe_body must not include imports, class declarations, SnippetA/SnippetB definitions, or EVICLONE_RESULT text.",
            "probe_body must call both SnippetA and SnippetB.",
            "probe_body must end by calling printResult(...) or printStatus(...).",
            "Use module_graph_input_binding to stay within the standard module execution plan.",
            "Do not infer or use any benchmark gold label.",
        ],
    }
    input_firewall = build_input_firewall_certificate(
        expert_role="probe_synthesis",
        prompt_obj=obj,
        redacted_sensitive_paths=compile_redactions + meta_redactions,
        renamed_nonsemantic_paths=compile_renames + meta_renames,
        module_graph_input_binding=module_graph_input_binding,
    )
    return json.dumps(obj, ensure_ascii=False, indent=2), input_firewall


def normalize_probe_payload(
    payload: dict[str, Any],
    *,
    system_prompt: str = "",
    user_prompt: str = "",
    raw_response: str | None = None,
    input_firewall: dict[str, Any] | None = None,
    model_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    probe_body = str(payload.get("probe_body") or "")
    summary = redact_probe_body(payload)
    status = str(payload.get("status") or "").strip().lower()
    if status != "completed":
        final_status = "not_recoverable" if status == "not_recoverable" else "rejected"
        reason = str(payload.get("reason") or payload.get("rationale") or "model did not return completed")
        validation_errors = [reason]
        token = forbidden_probe_decision_token_in_text(reason)
        if token:
            final_status = "rejected"
            validation_errors = [f"probe synthesis non-completed reason contains forbidden decision token: {token}"]
        return {
            "status": final_status,
            "error": "; ".join(validation_errors),
            "payload": summary,
            "probe_body": "",
            "expert_invocation": build_expert_invocation(
                expert_role="probe_synthesis",
                expert_contract=PROBE_EXPERT_CONTRACT,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                status=final_status,
                output_kind="probe_body",
                output_sha256=summary.get("probe_body_sha256"),
                raw_response=raw_response,
                validation_errors=validation_errors,
                input_firewall=input_firewall,
                model_config=model_config,
            ),
        }
    errors = validate_probe_payload(payload, probe_body)
    if errors:
        summary["validation_errors"] = errors
        return {
            "status": "rejected",
            "error": "; ".join(errors),
            "payload": summary,
            "probe_body": "",
            "expert_invocation": build_expert_invocation(
                expert_role="probe_synthesis",
                expert_contract=PROBE_EXPERT_CONTRACT,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                status="rejected",
                output_kind="probe_body",
                output_sha256=summary.get("probe_body_sha256"),
                raw_response=raw_response,
                validation_errors=errors,
                input_firewall=input_firewall,
                model_config=model_config,
            ),
        }
    return {
        "status": "completed",
        "error": "",
        "payload": summary,
        "probe_body": probe_body,
        "expert_invocation": build_expert_invocation(
            expert_role="probe_synthesis",
            expert_contract=PROBE_EXPERT_CONTRACT,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            status="completed",
            output_kind="probe_body",
            output_sha256=summary.get("probe_body_sha256"),
            raw_response=raw_response,
            input_firewall=input_firewall,
            model_config=model_config,
        ),
    }


def validate_probe_payload(payload: dict[str, Any], probe_body: str) -> list[str]:
    errors: list[str] = []
    for item in find_forbidden_key_paths(payload, FORBIDDEN_PROBE_DECISION_KEYS):
        errors.append(f"probe synthesis expert returned forbidden decision field: {item['path']}")
    schema_payload = dict(payload)
    if probe_body:
        schema_payload.setdefault(
            "probe_body_sha256",
            hashlib.sha256(probe_body.encode("utf-8", "replace")).hexdigest(),
        )
    errors.extend(validate_probe_payload_schema(schema_payload))
    preservation = payload.get("semantic_preservation") or {}
    if isinstance(preservation, dict):
        level = str(preservation.get("level") or "").strip().lower()
        if level == "low":
            errors.append("probe semantic preservation level is low")
    else:
        errors.append("semantic_preservation must be an object")
    if not probe_body.strip():
        errors.append("probe_body is empty")
    if "SnippetA" not in probe_body or "SnippetB" not in probe_body:
        errors.append("probe_body must call both SnippetA and SnippetB")
    if "printResult(" not in probe_body and "printStatus(" not in probe_body:
        errors.append("probe_body must report via printResult or printStatus")
    if re.search(r"\bprintResult\s*\(\s*(?:true|false)\s*,", probe_body):
        errors.append("probe_body must not hard-code printResult same=true/false")
    for token in find_probe_body_forbidden_decision_tokens(probe_body):
        errors.append(f"probe_body contains forbidden decision token: {token}")
    for pattern in FORBIDDEN_PROBE_BODY_PATTERNS:
        if re.search(pattern, probe_body, flags=re.IGNORECASE):
            errors.append(f"probe_body contains forbidden construct: {pattern}")
    return errors


def find_probe_body_forbidden_decision_tokens(probe_body: str) -> list[str]:
    detected: list[str] = []
    for token in sorted(FORBIDDEN_PROBE_DECISION_KEYS):
        pattern = r"(?<![A-Za-z0-9_$])" + re.escape(token) + r"(?![A-Za-z0-9_$])"
        if re.search(pattern, probe_body or "", flags=re.IGNORECASE):
            detected.append(token)
    return detected


def validate_probe_payload_schema(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    probe_kind = str(payload.get("probe_kind") or "").strip()
    if probe_kind not in VALID_PROBE_KINDS:
        errors.append("probe payload probe_kind is invalid")
    assumptions = payload.get("assumptions")
    if not isinstance(assumptions, list) or any(not isinstance(item, str) for item in assumptions):
        errors.append("probe payload assumptions must be a list of strings")
    else:
        for idx, assumption in enumerate(assumptions):
            token = forbidden_probe_decision_token_in_text(assumption)
            if token:
                errors.append(f"probe payload assumptions[{idx}] contains forbidden decision token: {token}")
    body_sha = str(payload.get("probe_body_sha256") or "")
    if len(body_sha) != 64 or any(char not in "0123456789abcdef" for char in body_sha.lower()):
        errors.append("probe payload probe_body_sha256 must be a sha256 digest")
    preservation = payload.get("semantic_preservation")
    if isinstance(preservation, dict):
        level = str(preservation.get("level") or "").strip().lower()
        if level not in {"high", "medium"}:
            errors.append("probe payload semantic_preservation.level must be high or medium")
        rationale = preservation.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append("probe payload semantic_preservation.rationale must be a non-empty string")
        else:
            token = forbidden_probe_decision_token_in_text(rationale)
            if token:
                errors.append(f"probe payload semantic_preservation.rationale contains forbidden decision token: {token}")
        risk_flags = preservation.get("risk_flags")
        if risk_flags is not None and (
            not isinstance(risk_flags, list) or any(not isinstance(item, str) for item in risk_flags)
        ):
            errors.append("probe payload semantic_preservation.risk_flags must be a list of strings")
        elif isinstance(risk_flags, list):
            for idx, risk_flag in enumerate(risk_flags):
                token = forbidden_probe_decision_token_in_text(risk_flag)
                if token:
                    errors.append(
                        f"probe payload semantic_preservation.risk_flags[{idx}] contains forbidden decision token: {token}"
                    )
    else:
        errors.append("probe payload semantic_preservation must be an object")
    return errors


def build_probe_payload_schema_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    schema_payload = canonical_probe_payload_for_schema(payload)
    errors = validate_probe_payload_schema(schema_payload)
    certificate: dict[str, Any] = {
        "schema_version": PROBE_PAYLOAD_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "component_role": PROBE_COMPONENT_ROLE,
        "expert_contract": PROBE_EXPERT_CONTRACT,
        "output_kind": PROBE_OUTPUT_KIND,
        "allowed_output": PROBE_ALLOWED_OUTPUT,
        "clone_label_output_allowed": False,
        "final_decision_allowed": False,
        "probe_kind": schema_payload.get("probe_kind"),
        "probe_body_sha256": schema_payload.get("probe_body_sha256"),
        "validation_errors": errors,
        "payload_sha256": canonical_json_sha256(schema_payload),
    }
    certificate["certificate_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def forbidden_probe_decision_token_in_text(value: str) -> str | None:
    lowered = (value or "").lower()
    for token in sorted(FORBIDDEN_PROBE_DECISION_KEYS):
        if token and re.search(r"(?<![A-Za-z0-9_$])" + re.escape(token.lower()) + r"(?![A-Za-z0-9_$])", lowered):
            return token
    decision_phrases = {
        "clone": r"\b(?:is|are|as|be|likely|definitely|probably)\s+(?:a\s+)?clone\b|\bclone\s+pair\b",
        "non_clone": r"\bnon[-_ ]clone\b|\bnot\s+(?:a\s+)?clone\b",
    }
    for token, pattern in decision_phrases.items():
        if re.search(pattern, lowered):
            return token
    return None


def canonical_probe_payload_for_schema(payload: dict[str, Any]) -> dict[str, Any]:
    ignored = {
        "probe_body",
        "probe_body_chars",
        "expert_contract",
        "probe_payload_schema",
        "validation_errors",
    }
    return {key: value for key, value in (payload or {}).items() if key not in ignored}


def build_probe_source_binding_certificate(
    source: str,
    probe_body: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    body = probe_body or ""
    source_text = source or ""
    body_sha = hashlib.sha256(body.encode("utf-8", "replace")).hexdigest()
    source_sha = hashlib.sha256(source_text.encode("utf-8", "replace")).hexdigest()
    expected_body_sha = str(payload.get("probe_body_sha256") or "")
    normalized_present = bool(body.strip()) and normalize_probe_binding_text(body) in normalize_probe_binding_text(source_text)
    errors = validate_probe_payload(payload, body)
    if expected_body_sha and expected_body_sha != body_sha:
        errors.append("probe_body_sha256 does not match retained probe_body")
    if not normalized_present:
        errors.append("retained EviProbe source does not contain the probe_body")
    certificate: dict[str, Any] = {
        "schema_version": PROBE_SOURCE_BINDING_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "probe_body_sha256": body_sha,
        "payload_probe_body_sha256": expected_body_sha or None,
        "source_sha256": source_sha,
        "probe_body_present_in_source": normalized_present,
        "retained_probe_body": body,
        "validation_errors": errors,
        "certificate_scope": "LLM probe_body embedded into retained EviProbe.java sidecar",
    }
    certificate["certificate_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def normalize_probe_binding_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def redact_probe_body(payload: dict[str, Any]) -> dict[str, Any]:
    result = {k: v for k, v in payload.items() if k != "probe_body"}
    result["expert_contract"] = PROBE_EXPERT_CONTRACT
    probe_body = str(payload.get("probe_body") or "")
    if probe_body:
        result["probe_body_chars"] = len(probe_body)
        result["probe_body_sha256"] = hashlib.sha256(probe_body.encode("utf-8", "replace")).hexdigest()
    result["probe_payload_schema"] = build_probe_payload_schema_certificate(result)
    return result


def probe_retry_wait_seconds(exc: Exception, attempt: int) -> float:
    text = str(exc).lower()
    if "429" in text or "rate limit" in text or "閫熺巼闄愬埗" in text:
        return min(60.0 * (attempt + 1), 180.0)
    return 1.0


def limit_text(text: str, max_chars: int) -> str:
    text = text or ""
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n/* ... truncated ... */\n" + text[-half:]


def truncate_obj(obj: Any, max_chars: int) -> Any:
    text = json.dumps(obj, ensure_ascii=False)
    if len(text) <= max_chars:
        return obj
    return {"truncated_json": limit_text(text, max_chars)}
