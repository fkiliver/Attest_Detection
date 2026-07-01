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


CONTEXT_EXPERT_CONTRACT = "context_completion_only_no_clone_judgment/v1"
CONTEXT_PAYLOAD_SCHEMA_VERSION = "eviclone-context-payload-schema/v1"
CONTEXT_PROBE_EXECUTION_PATH_SCHEMA_VERSION = "eviclone-context-probe-execution-path/v1"
CONTEXT_SOURCE_SAFETY_SCHEMA_VERSION = "eviclone-context-source-safety/v1"
CONTEXT_ADDED_CONTEXT_SCHEMA_VERSION = "eviclone-context-added-context/v1"
CONTEXT_ADDED_CONTEXT_HASH_FIELD = "certificate_sha256"
CONTEXT_COMPONENT_ROLE = "llm_context_completion_expert"
CONTEXT_OUTPUT_KIND = "java_source"
CONTEXT_ALLOWED_OUTPUT = "context_completed_java_harness_only"
CONTEXT_PROMPT_META_CHARS = 12000
CONTEXT_PROMPT_COMPILE_INFO_CHARS = 2500
CONTEXT_PROMPT_SNIPPET_CHARS = 7000
CONTEXT_PROMPT_GENERATED_SOURCE_CHARS = 9000

CONTEXT_COMPLETION_SYSTEM_PROMPT = """You repair Java dynamic-analysis harnesses for BigCloneBench method snippets.

Your task is conservative context completion, not semantic rewriting. The input snippets may lack imports,
class fields, surrounding classes, framework classes, Servlet/GUI/DB objects, or small helper utilities.

Rules:
- Preserve each original snippet's observable logic. Do not simplify, optimize, reorder, or replace the snippet body.
- You may add imports, class fields, constants, constructors, adapters, minimal helper methods, and inert mocks/stubs.
- Treat the functional block IR and executable module graph as the semantic boundary. Complete only missing context
  needed to execute those modules; do not invent new module behavior.
- For Servlet, GUI, DB, network, filesystem, and framework dependencies, add the smallest deterministic fake context that
  allows compilation or a faithful shared-input probe. Do not use real external services.
- For URL/download/web code, never use real external network. Prefer deterministic in-memory fixtures, byte arrays,
  strings, temp files, loopback-only fake adapters, or in-memory URLStreamHandler fixtures.
  URL.openStream()/openConnection() is allowed only when the URL is a local file URL, a loopback URL, a custom
  in-memory URLStreamHandler URL, or a variable explicitly bound to such a deterministic fixture. Socket, DriverManager,
  Runtime.exec, ProcessBuilder, threads, random, and wall-clock time remain forbidden in the harness support layer.
- If a missing context would require guessing behavior that changes the clone decision, return not_recoverable.
- If you can build a faithful executable probe, main must print exactly one line beginning with EVICLONE_RESULT followed
  by JSON with status, same, out_a, and out_b fields; same must be computed from SnippetA/SnippetB outputs, never a
  hard-coded true/false literal.
- If you can only make the snippets compile, use probe_strategy "compile_only" and main must not claim status "executed".
- You are not the clone classifier. Do not return verdict, pred_label, clone label, benchmark label, or final decision fields.
- Return JSON only.
"""


FORBIDDEN_CONTEXT_DECISION_KEYS = {
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

VALID_CONTEXT_PROBE_STRATEGIES = {"reuse_existing_probe", "custom_probe", "compile_only"}
ADDED_CONTEXT_CATEGORIES = ("imports", "fields", "stubs", "framework_mocks")

FORBIDDEN_CONTEXT_SOURCE_PATTERNS = [
    ("system_exit", r"\bSystem\.exit\s*\("),
    ("runtime_exec", r"\bRuntime\.getRuntime\s*\("),
    ("process_builder", r"\bProcessBuilder\s*\("),
    ("socket", r"\bnew\s+(?:java\.net\.)?(?:Socket|ServerSocket|DatagramSocket)\s*\("),
    ("driver_manager_connection", r"\b(?:DriverManager|java\.sql\.DriverManager)\.getConnection\s*\("),
    ("reflection_class_for_name", r"\bClass\.forName\s*\("),
    ("reflection_access_override", r"\.setAccessible\s*\("),
    ("random", r"\bnew\s+(?:java\.util\.)?(?:Random|SecureRandom)\s*\("),
    ("math_random", r"\bMath\.random\s*\("),
    ("current_time", r"\bSystem\.(?:currentTimeMillis|nanoTime)\s*\("),
    ("java_time_now", r"\b(?:Instant|LocalDate|LocalDateTime|ZonedDateTime)\.now\s*\("),
    ("thread_sleep", r"\bThread\.sleep\s*\("),
    ("new_thread", r"\bnew\s+Thread\s*\("),
    ("executors", r"\bExecutors\."),
]
NETWORK_OPEN_CALL_RE = re.compile(r"\.open(?:Stream|Connection)\s*\(")
LOOPBACK_URL_LITERAL_RE = re.compile(r"https?://(?:127\.0\.0\.1|localhost)(?::\d+)?(?:/[^\"'\s)]*)?", re.IGNORECASE)
LOCAL_FILE_URL_LITERAL_RE = re.compile(r"file:/", re.IGNORECASE)
LOCAL_MOCK_URL_LITERAL_RE = re.compile(
    r"(?:eviclone://(?:localhost|127\.0\.0\.1|eviclone\.local)|https?://eviclone\.local)"
    r"(?::\d+)?(?:/[^\"'\s)]*)?",
    re.IGNORECASE,
)
LOCAL_MOCK_URL_CONSTRUCTOR_RE = re.compile(
    r"\bnew\s+(?:java\.net\.)?URL\s*\(\s*['\"](?:eviclone|https?)['\"]\s*,\s*"
    r"['\"](?:localhost|127\.0\.0\.1|eviclone\.local)['\"]",
    re.IGNORECASE,
)
CUSTOM_URL_HANDLER_RE = re.compile(
    r"\bnew\s+(?:java\.net\.)?URL\s*\([^;]+?new\s+[A-Za-z_$][\w$.]*StreamHandler\s*\(",
    re.IGNORECASE | re.DOTALL,
)
LOOPBACK_URL_ASSIGN_RE = re.compile(
    r"\b(?:String|URL|java\.net\.URL)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:new\s+(?:java\.net\.)?URL\s*\()?"
    r"[^;]*(?:https?://(?:127\.0\.0\.1|localhost)|file:/)",
    re.IGNORECASE,
)
METHOD_BODY_RE = re.compile(
    r"(?:public|private|protected|static|final|synchronized|\s)+"
    r"[A-Za-z_$][\w$<>\[\].?,\s]*?\s+"
    r"(?P<name>[A-Za-z_$][\w$]*)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\{",
    flags=re.MULTILINE,
)


JAVA_KEYWORDS = {
    "abstract",
    "assert",
    "boolean",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extends",
    "false",
    "final",
    "finally",
    "float",
    "for",
    "goto",
    "if",
    "implements",
    "import",
    "instanceof",
    "int",
    "interface",
    "long",
    "native",
    "new",
    "null",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "static",
    "strictfp",
    "super",
    "switch",
    "synchronized",
    "this",
    "throw",
    "throws",
    "transient",
    "true",
    "try",
    "void",
    "volatile",
    "while",
}

IDENT_RE = re.compile(r"[A-Za-z_$][\w$]*")
MAIN_METHOD_RE = re.compile(
    r"public\s+static\s+void\s+main\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\{",
    flags=re.MULTILINE,
)
METHOD_NAME_RE = re.compile(
    r"(?:public|private|protected|static|final|synchronized|native|abstract|\s)+"
    r"[A-Za-z_$][\w$<>\[\].?,\s]*?\s+"
    r"(?P<name>[A-Za-z_$][\w$]*)\s*\(",
    flags=re.MULTILINE,
)


def complete_context_with_llm(
    pair: ClonePair,
    *,
    generated_source: str,
    compile_info: dict[str, Any],
    meta: dict[str, Any],
    mode: str,
    client: Any,
    retries: int = 1,
) -> dict[str, Any]:
    """Ask an LLM to complete a compilable Java harness and validate its conservative claims."""
    prompt, input_firewall = build_context_completion_prompt_with_firewall(
        pair,
        generated_source=generated_source,
        compile_info=compile_info,
        meta=meta,
        mode=mode,
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
            "java_source": "",
            "expert_invocation": build_expert_invocation(
                expert_role="context_completion",
                expert_contract=CONTEXT_EXPERT_CONTRACT,
                system_prompt=CONTEXT_COMPLETION_SYSTEM_PROMPT,
                user_prompt=prompt,
                status="rejected",
                output_kind="java_source",
                raw_response=None,
                validation_errors=firewall_reasons,
                input_firewall=input_firewall,
                model_config=model_config,
            ),
        }
    for attempt in range(attempts):
        try:
            raw_response = client.complete(system_prompt=CONTEXT_COMPLETION_SYSTEM_PROMPT, user_prompt=prompt)
            payload = extract_json_object(raw_response)
            return normalize_completion_payload(
                pair,
                payload,
                system_prompt=CONTEXT_COMPLETION_SYSTEM_PROMPT,
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
                time.sleep(context_retry_wait_seconds(exc, attempt))
    assert last_error is not None
    return {
        "status": "failed",
        "error": str(last_error),
        "payload": {},
        "java_source": "",
        "expert_invocation": build_expert_invocation(
            expert_role="context_completion",
            expert_contract=CONTEXT_EXPERT_CONTRACT,
            system_prompt=CONTEXT_COMPLETION_SYSTEM_PROMPT,
            user_prompt=prompt,
            status="failed",
            output_kind="java_source",
            raw_response=raw_response,
            validation_errors=[str(last_error)],
            input_firewall=input_firewall,
            model_config=model_config,
        ),
    }


def context_retry_wait_seconds(exc: Exception, attempt: int) -> float:
    text = str(exc).lower()
    if "429" in text or "rate limit" in text or "速率限制" in text:
        return min(60.0 * (attempt + 1), 180.0)
    return 1.0


def build_context_completion_prompt(
    pair: ClonePair,
    *,
    generated_source: str,
    compile_info: dict[str, Any],
    meta: dict[str, Any],
    mode: str,
) -> str:
    prompt, _ = build_context_completion_prompt_with_firewall(
        pair,
        generated_source=generated_source,
        compile_info=compile_info,
        meta=meta,
        mode=mode,
    )
    return prompt


def build_context_completion_prompt_with_firewall(
    pair: ClonePair,
    *,
    generated_source: str,
    compile_info: dict[str, Any],
    meta: dict[str, Any],
    mode: str,
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
        "task": "complete_missing_java_context_for_dynamic_clone_probe",
        "expert_input_policy": expert_input_policy("context_completion"),
        "pair": {
            "bcb_functionality": pair.functionality_name,
            "bcb_description": pair.functionality_description,
        },
        "mode": mode,
        "module_graph_input_binding": module_graph_input_binding,
        "current_harness_meta": truncate_obj(safe_meta, CONTEXT_PROMPT_META_CHARS),
        "compile_info": truncate_obj(safe_compile_info, CONTEXT_PROMPT_COMPILE_INFO_CHARS),
        "snippet_a": limit_text(pair.code_a, CONTEXT_PROMPT_SNIPPET_CHARS),
        "snippet_b": limit_text(pair.code_b, CONTEXT_PROMPT_SNIPPET_CHARS),
        "current_generated_EviProbe_java": limit_text(generated_source, CONTEXT_PROMPT_GENERATED_SOURCE_CHARS),
        "required_json_schema": {
            "status": "completed or not_recoverable",
            "can_compile": True,
            "semantic_preservation": {
                "level": "high or medium",
                "changed_original_logic": False,
                "rationale": "why the generated context preserves the original snippets",
                "risk_flags": ["missing_context_assumptions"],
            },
            "probe_strategy": "reuse_existing_probe or custom_probe or compile_only",
            "assumptions": ["explicit assumptions used for imports, fields, mocks, framework context"],
            "added_context": {
                "imports": ["java imports added"],
                "fields": ["class fields/constants added"],
                "stubs": ["helper classes/methods added"],
                "framework_mocks": ["Servlet/GUI/DB/etc mocks added"],
            },
            "java_source": "complete Java source for public class EviProbe",
        },
        "forbidden_json_fields": sorted(FORBIDDEN_CONTEXT_DECISION_KEYS),
        "important": [
            "Return one JSON object only.",
            "java_source must be a complete compilable EviProbe.java source string.",
            "The original snippets should appear inside SnippetA and SnippetB unless a wrapper is strictly required.",
            "Do not infer or use any benchmark gold label; complete only the missing execution context.",
            "Do not output clone/non-clone verdicts; the program will derive decisions from validated evidence only.",
            "Use module_graph_input_binding as the immutable semantic boundary for any context assumptions.",
            "If probe_strategy is custom_probe or reuse_existing_probe, main must call/reference both SnippetA and SnippetB and compute same from their outputs.",
            "If probe_strategy is compile_only, do not print status executed and do not hard-code same=true.",
            "For web/download logic, replace external resources with deterministic in-memory, temp-file, file-URL, loopback-only, or custom in-memory URLStreamHandler fixtures; openStream/openConnection is allowed only on those local fixture URLs.",
            "If the context cannot be completed without changing logic, set status to not_recoverable.",
        ],
    }
    input_firewall = build_input_firewall_certificate(
        expert_role="context_completion",
        prompt_obj=obj,
        redacted_sensitive_paths=compile_redactions + meta_redactions,
        renamed_nonsemantic_paths=compile_renames + meta_renames,
        module_graph_input_binding=module_graph_input_binding,
    )
    return json.dumps(obj, ensure_ascii=False, indent=2), input_firewall


def normalize_completion_payload(
    pair: ClonePair,
    payload: dict[str, Any],
    *,
    system_prompt: str = "",
    user_prompt: str = "",
    raw_response: str | None = None,
    input_firewall: dict[str, Any] | None = None,
    model_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = normalize_context_payload_metadata(payload)
    java_source = str(payload.get("java_source") or "")
    java_source, deterministic_normalizations = normalize_harness_determinism(java_source)
    if deterministic_normalizations:
        payload = dict(payload)
        payload["java_source"] = java_source
        payload = append_context_normalizations(payload, deterministic_normalizations)
    payload = normalize_context_probe_strategy_for_source_retention(java_source, payload)
    summary = redact_java_source(payload)
    status = str(payload.get("status") or "").strip().lower()
    if status != "completed":
        final_status = "not_recoverable" if status == "not_recoverable" else "rejected"
        reason = str(payload.get("reason") or payload.get("rationale") or "model did not return completed")
        validation_errors = [reason]
        token = forbidden_decision_token_in_text(reason)
        if token:
            final_status = "rejected"
            validation_errors = [f"context completion non-completed reason contains forbidden decision token: {token}"]
        result = {
            "status": final_status,
            "error": "; ".join(validation_errors),
            "payload": summary,
            "java_source": "",
            "expert_invocation": build_expert_invocation(
                expert_role="context_completion",
                expert_contract=CONTEXT_EXPERT_CONTRACT,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                status=final_status,
                output_kind="java_source",
                output_sha256=summary.get("java_source_sha256"),
                raw_response=raw_response,
                validation_errors=validation_errors,
                input_firewall=input_firewall,
                model_config=model_config,
            ),
        }
        if java_source:
            result["diagnostic_java_source"] = java_source
        return result

    errors = validate_completed_source(pair, java_source, payload)
    if errors:
        summary["validation_errors"] = errors
        return {
            "status": "rejected",
            "error": "; ".join(errors),
            "payload": summary,
            "java_source": "",
            "diagnostic_java_source": java_source,
            "expert_invocation": build_expert_invocation(
                expert_role="context_completion",
                expert_contract=CONTEXT_EXPERT_CONTRACT,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                status="rejected",
                output_kind="java_source",
                output_sha256=summary.get("java_source_sha256"),
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
        "java_source": java_source,
        "expert_invocation": build_expert_invocation(
            expert_role="context_completion",
            expert_contract=CONTEXT_EXPERT_CONTRACT,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            status="completed",
            output_kind="java_source",
            output_sha256=summary.get("java_source_sha256"),
            raw_response=raw_response,
            input_firewall=input_firewall,
            model_config=model_config,
        ),
    }


def normalize_context_payload_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload or {})
    normalizations: list[dict[str, str]] = []

    probe_strategy = str(normalized.get("probe_strategy") or "").strip()
    if probe_strategy == "executable_probe":
        normalized["probe_strategy"] = "custom_probe"
        normalizations.append(
            {
                "kind": "probe_strategy_alias_normalized",
                "from": probe_strategy,
                "to": "custom_probe",
            }
        )

    added_context = normalized.get("added_context")
    if isinstance(added_context, dict):
        added_context = dict(added_context)
        framework_mocks = added_context.get("framework_mocks")
        if isinstance(framework_mocks, list) and any(isinstance(item, dict) for item in framework_mocks):
            added_context["framework_mocks"] = [framework_mock_metadata_to_text(item) for item in framework_mocks]
            normalized["added_context"] = added_context
            normalizations.append(
                {
                    "kind": "framework_mock_metadata_stringified",
                    "count": str(len(framework_mocks)),
                }
            )

    preservation = normalized.get("semantic_preservation")
    if isinstance(preservation, dict):
        preservation = dict(preservation)
        risk_flags = preservation.get("risk_flags")
        if isinstance(risk_flags, list):
            sanitized: list[str] = []
            changed = 0
            for flag in risk_flags:
                if not isinstance(flag, str):
                    sanitized.append(str(flag))
                    changed += 1
                    continue
                if forbidden_decision_token_in_text(flag):
                    sanitized.append("context_assumption_recorded")
                    changed += 1
                else:
                    sanitized.append(flag)
            if changed:
                preservation["risk_flags"] = sanitized
                normalized["semantic_preservation"] = preservation
                normalizations.append(
                    {
                        "kind": "risk_flag_decision_language_sanitized",
                        "count": str(changed),
                    }
                )

    if normalizations:
        normalized = append_context_normalizations(normalized, normalizations)
    return normalized


def framework_mock_metadata_to_text(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)
    name = str(item.get("name") or "unknown_framework_mock").strip()
    kind = str(item.get("kind") or "mock").strip()
    methods = item.get("methods")
    if isinstance(methods, list):
        method_text = ",".join(str(method).strip() for method in methods if str(method).strip())
    else:
        method_text = ""
    return f"framework_mock {name} kind={kind} methods={method_text}".strip()


def normalize_harness_determinism(java_source: str) -> tuple[str, list[dict[str, str]]]:
    """Replace nondeterministic harness support calls outside SnippetA/SnippetB."""
    source = java_source or ""
    normalizations: list[dict[str, str]] = []
    replacements = [
        (re.compile(r"\bSystem\.currentTimeMillis\s*\(\s*\)"), "0L", "system_current_time_millis_replaced"),
        (re.compile(r"\bSystem\.nanoTime\s*\(\s*\)"), "0L", "system_nano_time_replaced"),
    ]
    updated = source
    for pattern, replacement, kind in replacements:
        snippet_spans = named_class_spans(updated, {"SnippetA", "SnippetB"})
        updated, count = replace_matches_outside_spans(updated, pattern, replacement, snippet_spans)
        if count:
            normalizations.append(
                {
                    "kind": kind,
                    "scope": "harness_support_outside_snippet_classes",
                    "replacement": replacement,
                    "count": str(count),
                }
            )
    return updated, normalizations


def append_context_normalizations(payload: dict[str, Any], entries: list[dict[str, str]]) -> dict[str, Any]:
    normalized = dict(payload)
    normalizations = normalized.get("normalizations")
    if isinstance(normalizations, list):
        normalizations = list(normalizations)
    else:
        normalizations = []
    normalizations.extend(entries)
    normalized["normalizations"] = normalizations
    preservation = normalized.get("semantic_preservation")
    if isinstance(preservation, dict):
        preservation = dict(preservation)
        risk_flags = preservation.get("risk_flags")
        if isinstance(risk_flags, list):
            risk_flags = list(risk_flags)
        else:
            risk_flags = []
        if any(entry.get("kind") in {"system_current_time_millis_replaced", "system_nano_time_replaced"} for entry in entries):
            risk_flags.append("harness_determinism_normalized")
        preservation["risk_flags"] = risk_flags
        normalized["semantic_preservation"] = preservation
    return normalized


def named_class_spans(source: str, class_names: set[str]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for class_name in class_names:
        pattern = re.compile(rf"\bclass\s+{re.escape(class_name)}\b[^\{{]*\{{")
        search_start = 0
        while True:
            match = pattern.search(source or "", search_start)
            if not match:
                break
            brace_index = match.end() - 1
            depth = 0
            for index in range(brace_index, len(source)):
                char = source[index]
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        spans.append((match.start(), index + 1))
                        search_start = index + 1
                        break
            else:
                break
    return sorted(spans)


def replace_matches_outside_spans(
    source: str,
    pattern: re.Pattern[str],
    replacement: str,
    spans: list[tuple[int, int]],
) -> tuple[str, int]:
    pieces: list[str] = []
    cursor = 0
    count = 0
    for match in pattern.finditer(source or ""):
        if any(start <= match.start() < end for start, end in spans):
            continue
        pieces.append(source[cursor : match.start()])
        pieces.append(replacement)
        cursor = match.end()
        count += 1
    if not count:
        return source, 0
    pieces.append(source[cursor:])
    return "".join(pieces), count


def normalize_context_probe_strategy_for_source_retention(java_source: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Keep compilable source sidecars when the LLM overclaims probe adequacy.

    Source retention and probe adequacy are separate stages. If a completed context
    answer keeps the snippets but its main method is only a compile harness, retain
    the source as compile_only instead of rejecting the sidecar.
    """
    probe_strategy = str(payload.get("probe_strategy") or "").strip().lower()
    if probe_strategy not in {"custom_probe", "reuse_existing_probe"}:
        return payload
    probe_errors = validate_context_probe_execution_path(java_source, payload)
    snippet_reference_errors = {
        "context completion probe must execute or reference SnippetA",
        "context completion probe must execute or reference SnippetB",
    }
    if not probe_errors or any(error not in snippet_reference_errors for error in probe_errors):
        return payload
    normalized = dict(payload)
    normalized["probe_strategy"] = "compile_only"
    normalizations = normalized.get("normalizations")
    if not isinstance(normalizations, list):
        normalizations = []
    normalizations.append(
        {
            "kind": "probe_strategy_downgraded_to_compile_only",
            "from": probe_strategy,
            "reason": "main did not execute or reference both snippets; source is retained for later probe synthesis only",
        }
    )
    normalized["normalizations"] = normalizations
    assumptions = normalized.get("assumptions")
    if isinstance(assumptions, list):
        assumptions = list(assumptions)
    else:
        assumptions = []
    assumptions.append("context completion retained a compile-only source sidecar; discriminating probe synthesis is deferred")
    normalized["assumptions"] = assumptions
    preservation = normalized.get("semantic_preservation")
    if isinstance(preservation, dict):
        preservation = dict(preservation)
        risk_flags = preservation.get("risk_flags")
        if isinstance(risk_flags, list):
            risk_flags = list(risk_flags)
        else:
            risk_flags = []
        risk_flags.append("probe_synthesis_deferred")
        preservation["risk_flags"] = risk_flags
        normalized["semantic_preservation"] = preservation
    return normalized


def validate_completed_source(pair: ClonePair, java_source: str, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_context_expert_scope(payload))
    errors.extend(validate_context_payload_schema(payload))
    if "public class EviProbe" not in java_source:
        errors.append("java_source must define public class EviProbe")
    if "SnippetA" not in java_source or "SnippetB" not in java_source:
        errors.append("java_source must keep SnippetA and SnippetB containers")
    errors.extend(validate_context_probe_execution_path(java_source, payload))
    errors.extend(validate_context_source_safety(java_source))
    added_context_certificate = build_context_added_context_certificate(java_source, payload)
    if added_context_certificate.get("status") != "verified":
        for error in added_context_certificate.get("validation_errors") or []:
            errors.append(f"added_context certificate rejected: {error}")

    preservation = payload.get("semantic_preservation") or {}
    if isinstance(preservation, dict):
        changed = preservation.get("changed_original_logic")
        if changed is True or str(changed).strip().lower() in {"true", "yes", "1"}:
            errors.append("model reported changed_original_logic=true")
        level = str(preservation.get("level") or "").strip().lower()
        if level == "low":
            errors.append("semantic preservation level is low")
    else:
        errors.append("semantic_preservation must be an object")

    for side_name, code in (("A", pair.code_a), ("B", pair.code_b)):
        method_names = declared_method_names(code)
        for method_name in method_names[:3]:
            if method_name not in java_source:
                errors.append(f"snippet {side_name} method name not preserved: {method_name}")
        markers = significant_identifiers(code)
        if markers:
            required = min(3, len(markers))
            matched = sum(1 for marker in markers[:20] if marker in java_source)
            if matched < required:
                errors.append(
                    f"snippet {side_name} retained too few source identifiers: matched {matched}/{required}"
                )
    return errors


def validate_context_payload_schema(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("can_compile") is not True:
        errors.append("context payload can_compile must be true")
    probe_strategy = str(payload.get("probe_strategy") or "").strip()
    if probe_strategy not in VALID_CONTEXT_PROBE_STRATEGIES:
        errors.append("context payload probe_strategy is invalid")
    assumptions = payload.get("assumptions")
    if not isinstance(assumptions, list) or any(not isinstance(item, str) for item in assumptions):
        errors.append("context payload assumptions must be a list of strings")
    else:
        for idx, assumption in enumerate(assumptions):
            token = forbidden_decision_token_in_text(assumption)
            if token:
                errors.append(f"context payload assumptions[{idx}] contains forbidden decision token: {token}")
    added_context = payload.get("added_context")
    if not isinstance(added_context, dict):
        errors.append("context payload added_context must be an object")
    else:
        for key in ["imports", "fields", "stubs"]:
            values = added_context.get(key)
            if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
                errors.append(f"context payload added_context.{key} must be a list of strings")
        framework_mocks = added_context.get("framework_mocks")
        if framework_mocks is not None and (
            not isinstance(framework_mocks, list) or any(not isinstance(item, str) for item in framework_mocks)
        ):
            errors.append("context payload added_context.framework_mocks must be a list of strings")
    preservation = payload.get("semantic_preservation")
    if isinstance(preservation, dict):
        level = str(preservation.get("level") or "").strip().lower()
        if level not in {"high", "medium"}:
            errors.append("context payload semantic_preservation.level must be high or medium")
        if preservation.get("changed_original_logic") is not False:
            errors.append("context payload semantic_preservation.changed_original_logic must be false")
        rationale = preservation.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append("context payload semantic_preservation.rationale must be a non-empty string")
        else:
            token = forbidden_decision_token_in_text(rationale)
            if token:
                errors.append(f"context payload semantic_preservation.rationale contains forbidden decision token: {token}")
        risk_flags = preservation.get("risk_flags")
        if risk_flags is not None and (
            not isinstance(risk_flags, list) or any(not isinstance(item, str) for item in risk_flags)
        ):
            errors.append("context payload semantic_preservation.risk_flags must be a list of strings")
        elif isinstance(risk_flags, list):
            for idx, risk_flag in enumerate(risk_flags):
                token = forbidden_decision_token_in_text(risk_flag)
                if token:
                    errors.append(
                        f"context payload semantic_preservation.risk_flags[{idx}] contains forbidden decision token: {token}"
                    )
    else:
        errors.append("context payload semantic_preservation must be an object")
    return errors


def build_context_payload_schema_certificate(payload: dict[str, Any]) -> dict[str, Any]:
    schema_payload = canonical_context_payload_for_schema(payload)
    errors = validate_context_payload_schema(schema_payload)
    certificate: dict[str, Any] = {
        "schema_version": CONTEXT_PAYLOAD_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "component_role": CONTEXT_COMPONENT_ROLE,
        "expert_contract": CONTEXT_EXPERT_CONTRACT,
        "output_kind": CONTEXT_OUTPUT_KIND,
        "allowed_output": CONTEXT_ALLOWED_OUTPUT,
        "clone_label_output_allowed": False,
        "final_decision_allowed": False,
        "probe_strategy": schema_payload.get("probe_strategy"),
        "can_compile": schema_payload.get("can_compile"),
        "validation_errors": errors,
        "payload_sha256": canonical_json_sha256(schema_payload),
    }
    certificate["certificate_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def canonical_context_payload_for_schema(payload: dict[str, Any]) -> dict[str, Any]:
    ignored = {
        "java_source",
        "java_source_chars",
        "java_source_sha256",
        "expert_contract",
        "context_payload_schema",
        "validation_errors",
    }
    return {key: value for key, value in (payload or {}).items() if key not in ignored}


def validate_context_source_safety(java_source: str) -> list[str]:
    errors: list[str] = []
    harness_source = strip_snippet_class_bodies(java_source)
    for code, pattern in FORBIDDEN_CONTEXT_SOURCE_PATTERNS:
        if re.search(pattern, harness_source):
            errors.append(f"context source contains forbidden harness construct: {code}")
    for _call in unsafe_network_open_calls(harness_source):
        errors.append("context source contains forbidden harness construct: network_open_stream")
    for token in find_context_source_forbidden_decision_tokens(harness_source):
        errors.append(f"context source contains forbidden decision token: {token}")
    return errors


def find_context_source_forbidden_decision_tokens(harness_source: str) -> list[str]:
    detected: list[str] = []
    for token in sorted(FORBIDDEN_CONTEXT_DECISION_KEYS):
        pattern = r"(?<![A-Za-z0-9_$])" + re.escape(token) + r"(?![A-Za-z0-9_$])"
        if re.search(pattern, harness_source or "", flags=re.IGNORECASE):
            detected.append(token)
    return detected


def build_context_source_safety_certificate(java_source: str) -> dict[str, Any]:
    harness_source = strip_snippet_class_bodies(java_source)
    errors = validate_context_source_safety(java_source)
    detected_constructs = [
        code for code, pattern in FORBIDDEN_CONTEXT_SOURCE_PATTERNS if re.search(pattern, harness_source)
    ]
    if unsafe_network_open_calls(harness_source):
        detected_constructs.append("network_open_stream")
    detected_decision_tokens = find_context_source_forbidden_decision_tokens(harness_source)
    non_loopback_urls = [url for url in re.findall(r"https?://[^\"'\s)]+", harness_source) if not is_loopback_url(url)]
    certificate: dict[str, Any] = {
        "schema_version": CONTEXT_SOURCE_SAFETY_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "scan_scope": "EviProbe.java with SnippetA/SnippetB class bodies removed",
        "detected_forbidden_constructs": detected_constructs,
        "detected_forbidden_decision_tokens": detected_decision_tokens,
        "non_loopback_url_literals": non_loopback_urls[:8],
        "validation_warnings": ["non_loopback_url_literal_declared"] if non_loopback_urls else [],
        "validation_errors": errors,
        "java_source_sha256": hashlib.sha256((java_source or "").encode("utf-8", "replace")).hexdigest(),
    }
    certificate["certificate_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def build_context_added_context_certificate(java_source: str, payload: dict[str, Any]) -> dict[str, Any]:
    added_context = payload.get("added_context") if isinstance(payload.get("added_context"), dict) else {}
    items, errors, warnings = context_added_context_items(java_source, added_context)
    declared_counts = {
        category: sum(1 for item in items if item.get("category") == category)
        for category in ADDED_CONTEXT_CATEGORIES
    }
    certificate: dict[str, Any] = {
        "schema_version": CONTEXT_ADDED_CONTEXT_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "certificate_scope": "LLM context completion added_context declarations retained as grounded or synthetic support context in EviProbe.java",
        "allowed_categories": list(ADDED_CONTEXT_CATEGORIES),
        "source_sha256": hashlib.sha256((java_source or "").encode("utf-8", "replace")).hexdigest(),
        "payload_added_context_sha256": canonical_json_sha256(added_context),
        "declared_counts": declared_counts,
        "declared_item_count": len(items),
        "grounded_item_count": sum(1 for item in items if item.get("grounded") is True),
        "synthetic_item_count": sum(1 for item in items if item.get("synthetic_context") is True),
        "items": items,
        "llm_final_decision_allowed": False,
        "method_body_rewrite_allowed": False,
        "validation_errors": errors,
        "validation_warnings": warnings,
    }
    certificate[CONTEXT_ADDED_CONTEXT_HASH_FIELD] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != CONTEXT_ADDED_CONTEXT_HASH_FIELD}
    )
    return certificate


def context_added_context_items(
    java_source: str,
    added_context: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    items: list[dict[str, Any]] = []
    if not isinstance(added_context, dict):
        return items, ["added_context_missing"], warnings
    for key, value in added_context.items():
        if key not in ADDED_CONTEXT_CATEGORIES and value not in (None, [], ""):
            errors.append(f"added_context_unknown_category:{key}")
    for category in ADDED_CONTEXT_CATEGORIES:
        raw_values = added_context.get(category, [])
        if raw_values is None:
            raw_values = []
        if not isinstance(raw_values, list):
            errors.append(f"added_context_{category}_not_list")
            continue
        for index, value in enumerate(raw_values):
            if not isinstance(value, str) or not value.strip():
                errors.append(f"added_context_{category}_item_invalid:{index}")
                continue
            item = context_added_context_item(java_source, category, value)
            items.append(item)
            if len(value) > 2000:
                errors.append(f"added_context_{category}_item_too_long:{index}")
            if item["contains_forbidden_decision_token"]:
                errors.append(f"added_context_{category}_contains_decision_token:{index}")
            if category == "imports" and item["grounded"] is not True:
                warnings.append(f"added_context_import_declared_synthetic:{index}")
            elif category in {"fields", "stubs"} and item["grounded"] is not True:
                warnings.append(f"added_context_{category}_declared_synthetic:{index}")
            elif category == "framework_mocks" and item["grounded"] is not True:
                warnings.append(f"added_context_framework_mock_declared_not_textually_grounded:{index}")
    return items, errors, warnings


def context_added_context_item(java_source: str, category: str, value: str) -> dict[str, Any]:
    normalized = normalize_context_added_item(value)
    tokens = significant_identifiers(value)
    grounding = context_added_context_grounding(java_source, category, value, tokens)
    return {
        "category": category,
        "item_sha256": hashlib.sha256(value.encode("utf-8", "replace")).hexdigest(),
        "normalized": normalized,
        "token_count": len(tokens),
        "tokens": tokens[:12],
        "grounding": grounding,
        "grounded": grounding in {
            "exact_text_present",
            "normalized_text_present",
            "import_declaration_present",
            "identifier_supported",
            "framework_mock_declared",
        },
        "synthetic_context": grounding == "not_grounded",
        "contains_forbidden_decision_token": contains_forbidden_decision_token(value),
    }


def normalize_context_added_item(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def context_added_context_grounding(
    java_source: str,
    category: str,
    value: str,
    tokens: list[str],
) -> str:
    stripped = (value or "").strip()
    if not stripped:
        return "empty"
    if category == "framework_mocks":
        return "framework_mock_declared"
    if stripped in (java_source or ""):
        return "exact_text_present"
    if normalize_context_added_item(stripped) in normalize_context_added_item(java_source or ""):
        return "normalized_text_present"
    if category == "imports":
        import_text = stripped if stripped.startswith("import ") else f"import {stripped}"
        import_text = import_text.rstrip(";") + ";"
        return "import_declaration_present" if import_text in (java_source or "") else "not_grounded"
    meaningful = [token for token in tokens if token not in {"SnippetA", "SnippetB"}]
    if meaningful and all(re.search(rf"\b{re.escape(token)}\b", java_source or "") for token in meaningful[:8]):
        return "identifier_supported"
    return "not_grounded"


def contains_forbidden_decision_token(value: str) -> bool:
    return forbidden_decision_token_in_text(value) is not None


def forbidden_decision_token_in_text(value: str) -> str | None:
    lowered = (value or "").lower()
    for token in sorted(FORBIDDEN_CONTEXT_DECISION_KEYS):
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


def strip_snippet_class_bodies(java_source: str) -> str:
    result = java_source or ""
    for class_name in ("SnippetA", "SnippetB"):
        result = strip_named_class_body(result, class_name)
    return result


def strip_named_class_body(source: str, class_name: str) -> str:
    pattern = re.compile(rf"\bclass\s+{re.escape(class_name)}\b[^\{{]*\{{")
    search_start = 0
    while True:
        match = pattern.search(source, search_start)
        if not match:
            return source
        brace_index = match.end() - 1
        depth = 0
        for index in range(brace_index, len(source)):
            char = source[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    replacement = source[match.start() : match.end()] + " /* original snippet body omitted from safety scan */ }"
                    source = source[: match.start()] + replacement + source[index + 1 :]
                    search_start = match.start() + len(replacement)
                    break
        else:
            return source


def is_loopback_url(url: str) -> bool:
    lowered = (url or "").lower()
    return (
        lowered.startswith("http://127.0.0.1")
        or lowered.startswith("https://127.0.0.1")
        or lowered.startswith("http://localhost")
        or lowered.startswith("https://localhost")
    )


def unsafe_network_open_calls(harness_source: str) -> list[dict[str, Any]]:
    loopback_vars = loopback_url_variable_names(harness_source)
    resource_vars = classpath_resource_url_variable_names(harness_source)
    local_factories = local_fixture_url_factory_names(harness_source)
    local_url_handlers = local_url_stream_handler_class_names(harness_source)
    unsafe: list[dict[str, Any]] = []
    for match in NETWORK_OPEN_CALL_RE.finditer(harness_source or ""):
        statement = java_statement_around(harness_source, match.start())
        context = harness_source[max(0, match.start() - 700) : min(len(harness_source), match.end() + 180)]
        if network_open_call_is_local_fixture(
            statement,
            context,
            loopback_vars,
            local_factories,
            local_url_handlers,
            resource_vars,
        ):
            continue
        unsafe.append(
            {
                "offset": match.start(),
                "call": match.group(0),
                "statement_sha256": hashlib.sha256(statement.encode("utf-8", "replace")).hexdigest(),
            }
        )
    return unsafe


def loopback_url_variable_names(harness_source: str) -> set[str]:
    return {match.group(1) for match in LOOPBACK_URL_ASSIGN_RE.finditer(harness_source or "")}


def classpath_resource_url_variable_names(harness_source: str) -> set[str]:
    source = harness_source or ""
    variables = {
        match.group(1)
        for match in re.finditer(
            r"\b(?:URL|java\.net\.URL)\s+([A-Za-z_$][\w$]*)\s*=\s*[^;]*(?:\.class\s*)?\.getResource\s*\(",
            source,
        )
    }
    resource_enumerations = {
        match.group(1)
        for match in re.finditer(
            r"\b(?:Enumeration\s*<\s*(?:URL|java\.net\.URL)\s*>|java\.util\.Enumeration\s*<\s*(?:URL|java\.net\.URL)\s*>)\s+"
            r"([A-Za-z_$][\w$]*)\s*=\s*[^;]*\.getResources\s*\(",
            source,
        )
    }
    for enum_var in resource_enumerations:
        escaped = re.escape(enum_var)
        variables.update(
            match.group(1)
            for match in re.finditer(
                rf"\b(?:URL|java\.net\.URL)\s+([A-Za-z_$][\w$]*)\s*=\s*{escaped}\s*\.nextElement\s*\(",
                source,
            )
        )
    return variables


def local_fixture_url_factory_names(harness_source: str) -> set[str]:
    factories: set[str] = set()
    source = harness_source or ""
    has_local_handler_factory = bool(local_url_stream_handler_class_names(source)) and bool(
        re.search(r"\bURL\.setURLStreamHandlerFactory\s*\(|\bURLStreamHandlerFactory\b", source)
    )
    for method in extract_method_bodies(harness_source):
        name = str(method.get("name") or "")
        body = str(method.get("body") or "")
        if not name:
            continue
        if (
            "toURI().toURL()" in body
            or "toUri().toURL()" in body
            or LOCAL_FILE_URL_LITERAL_RE.search(body)
            or LOOPBACK_URL_LITERAL_RE.search(body)
            or CUSTOM_URL_HANDLER_RE.search(body)
            or (
                has_local_handler_factory
                and (LOCAL_MOCK_URL_LITERAL_RE.search(body) or LOCAL_MOCK_URL_CONSTRUCTOR_RE.search(body))
            )
            or (re.search(r"\breturn\s+null\s*;", body) and re.search(r"(?:url|resource)", name, re.IGNORECASE))
        ):
            factories.add(name)
    return factories


def local_url_stream_handler_class_names(harness_source: str) -> set[str]:
    return {
        match.group(1)
        for match in re.finditer(
            r"\bclass\s+([A-Za-z_$][\w$]*)\s+extends\s+(?:java\.net\.)?URLStreamHandler\b",
            harness_source or "",
        )
    }


def network_open_call_is_local_fixture(
    statement: str,
    context: str,
    loopback_vars: set[str],
    local_factories: set[str] | None = None,
    local_url_handlers: set[str] | None = None,
    resource_vars: set[str] | None = None,
) -> bool:
    local_factories = local_factories or set()
    local_url_handlers = local_url_handlers or set()
    resource_vars = resource_vars or set()
    combined = f"{context}\n{statement}"
    if (
        LOOPBACK_URL_LITERAL_RE.search(combined)
        or LOCAL_FILE_URL_LITERAL_RE.search(combined)
        or CUSTOM_URL_HANDLER_RE.search(combined)
    ):
        return True
    if ".toURI().toURL().open" in combined or ".toUri().toURL().open" in combined:
        return True
    for variable in loopback_vars:
        escaped = re.escape(variable)
        if re.search(rf"\b{escaped}\s*\.\s*open(?:Stream|Connection)\s*\(", statement):
            return True
        if re.search(rf"\bnew\s+(?:java\.net\.)?URL\s*\(\s*{escaped}\s*\)\s*\.open(?:Stream|Connection)\s*\(", statement):
            return True
        if re.search(rf"\b{escaped}\s*\)\s*\.open(?:Stream|Connection)\s*\(", statement):
            return True
    for factory in local_factories:
        escaped = re.escape(factory)
        if re.search(rf"\b{escaped}\s*\([^;]*\)\s*\.open(?:Stream|Connection)\s*\(", statement):
            return True
        assigned = re.search(
            rf"\b(?:URL|java\.net\.URL)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:this\.)?{escaped}\s*\(",
            combined,
        )
        if assigned:
            variable = re.escape(assigned.group(1))
            if re.search(rf"\b{variable}\s*\.\s*open(?:Stream|Connection)\s*\(", statement):
                return True
    for variable_name in resource_vars:
        variable = re.escape(variable_name)
        if re.search(rf"\b{variable}\s*\.\s*open(?:Stream|Connection)\s*\(", statement):
            return True
    for handler in local_url_handlers:
        escaped = re.escape(handler)
        if re.search(rf"\bnew\s+{escaped}\s*\([^;]*\)\s*\.openConnection\s*\(", statement):
            return True
    return False


def java_statement_around(source: str, offset: int) -> str:
    text = source or ""
    start = max(text.rfind(";", 0, offset), text.rfind("{", 0, offset), text.rfind("}", 0, offset)) + 1
    end_candidates = [idx for idx in [text.find(";", offset), text.find("\n", offset)] if idx >= 0]
    end = min(end_candidates) + 1 if end_candidates else min(len(text), offset + 240)
    return text[start:end]


def validate_context_probe_execution_path(java_source: str, payload: dict[str, Any]) -> list[str]:
    """Reject context-completion harnesses that report results without executing both snippets."""
    errors: list[str] = []
    probe_strategy = str(payload.get("probe_strategy") or "").strip().lower()
    main_region = extract_main_execution_region(java_source)
    if not main_region:
        errors.append("java_source must define public static void main")
        return errors

    if probe_strategy == "compile_only":
        if '"status":"executed"' in compact_java_text(main_region) or '"same":true' in compact_java_text(main_region):
            errors.append("compile_only context must not hard-code an executed/same=true result")
        return errors

    for snippet_name in ("SnippetA", "SnippetB"):
        if not execution_path_references_snippet(java_source, main_region, snippet_name):
            errors.append(f"context completion probe must execute or reference {snippet_name}")
    if hardcodes_executed_same_result(main_region):
        errors.append("context completion probe must not hard-code EVICLONE_RESULT same=true/false")
    return errors


def build_context_probe_execution_path_certificate(java_source: str, payload: dict[str, Any]) -> dict[str, Any]:
    probe_strategy = str(payload.get("probe_strategy") or "").strip().lower()
    main_region = extract_main_execution_region(java_source)
    snippet_a_referenced = execution_region_references_snippet(main_region, "SnippetA") if main_region else False
    snippet_b_referenced = execution_region_references_snippet(main_region, "SnippetB") if main_region else False
    snippet_a_reachable = execution_path_references_snippet(java_source, main_region, "SnippetA") if main_region else False
    snippet_b_reachable = execution_path_references_snippet(java_source, main_region, "SnippetB") if main_region else False
    hardcoded_same = hardcodes_executed_same_result(main_region) if main_region else False
    errors = validate_context_probe_execution_path(java_source, payload)
    certificate: dict[str, Any] = {
        "schema_version": CONTEXT_PROBE_EXECUTION_PATH_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "probe_strategy": probe_strategy or None,
        "main_present": bool(main_region),
        "snippet_a_referenced_in_main": snippet_a_referenced,
        "snippet_b_referenced_in_main": snippet_b_referenced,
        "snippet_a_reachable_from_main": snippet_a_reachable,
        "snippet_b_reachable_from_main": snippet_b_reachable,
        "hardcoded_executed_same_result": hardcoded_same,
        "validation_errors": errors,
        "java_source_sha256": hashlib.sha256((java_source or "").encode("utf-8", "replace")).hexdigest(),
        "certificate_scope": "LLM context-completion EviProbe.java main execution path",
    }
    certificate["certificate_sha256"] = canonical_json_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def extract_main_execution_region(java_source: str) -> str:
    match = MAIN_METHOD_RE.search(java_source or "")
    if not match:
        return ""
    start = match.start()
    brace_index = match.end() - 1
    depth = 0
    for index in range(brace_index, len(java_source)):
        char = java_source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return java_source[start : index + 1]
    return java_source[start:]


def execution_region_references_snippet(region: str, snippet_name: str) -> bool:
    patterns = [
        rf"\bnew\s+{re.escape(snippet_name)}\s*\(",
        rf"\b{re.escape(snippet_name)}\s*\.",
        rf"\b{re.escape(snippet_name)}\s+[A-Za-z_$][\w$]*\s*=",
    ]
    return any(re.search(pattern, region) for pattern in patterns)


def execution_path_references_snippet(java_source: str, main_region: str, snippet_name: str) -> bool:
    if execution_region_references_snippet(main_region, snippet_name):
        return True
    helper_names = helper_methods_referencing_snippet(java_source, snippet_name)
    return any(re.search(rf"\b{re.escape(name)}\s*\(", main_region or "") for name in helper_names)


def helper_methods_referencing_snippet(java_source: str, snippet_name: str) -> set[str]:
    harness_source = strip_snippet_class_bodies(java_source)
    helpers: set[str] = set()
    for method in extract_method_bodies(harness_source):
        name = str(method.get("name") or "")
        body = str(method.get("body") or "")
        if name == "main":
            continue
        if execution_region_references_snippet(body, snippet_name):
            helpers.add(name)
    return helpers


def extract_method_bodies(source: str) -> list[dict[str, str]]:
    methods: list[dict[str, str]] = []
    for match in METHOD_BODY_RE.finditer(source or ""):
        brace_index = match.end() - 1
        depth = 0
        for index in range(brace_index, len(source)):
            char = source[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    methods.append({"name": match.group("name"), "body": source[brace_index : index + 1]})
                    break
    return methods


def hardcodes_executed_same_result(region: str) -> bool:
    compact = compact_java_text(region)
    if re.search(r"\bprintResult\s*\(\s*(?:true|false)\s*,", region):
        has_dynamic_same_output = (
            re.search(r"\bboolean\s+same\s*=", region) is not None
            and re.search(r"\bprintResult\s*\(\s*same\s*,", region) is not None
        )
        if not has_dynamic_same_output:
            return True
    if "EVICLONE_RESULT" not in compact or '"status":"executed"' not in compact:
        return False
    return bool(re.search(r'"same"\s*:\s*(?:true|false)', compact))


def compact_java_text(text: str) -> str:
    return re.sub(r"\s+", "", text or "").replace('\\"', '"')


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def validate_context_expert_scope(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for item in find_forbidden_key_paths(payload, FORBIDDEN_CONTEXT_DECISION_KEYS):
        errors.append(f"context completion expert returned forbidden decision field: {item['path']}")
    return errors


def redact_java_source(payload: dict[str, Any]) -> dict[str, Any]:
    result = {k: v for k, v in payload.items() if k != "java_source"}
    result["expert_contract"] = CONTEXT_EXPERT_CONTRACT
    java_source = str(payload.get("java_source") or "")
    if java_source:
        result["java_source_chars"] = len(java_source)
        result["java_source_sha256"] = hashlib.sha256(java_source.encode("utf-8", "replace")).hexdigest()
    result["context_payload_schema"] = build_context_payload_schema_certificate(result)
    return result


def declared_method_names(code: str) -> list[str]:
    return list(dict.fromkeys(match.group("name") for match in METHOD_NAME_RE.finditer(code or "")))


def significant_identifiers(code: str) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for token in IDENT_RE.findall(code or ""):
        if token in JAVA_KEYWORDS or len(token) < 3:
            continue
        if token and token[0].isupper() and token in {"String", "Integer", "Boolean", "Exception"}:
            continue
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result


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
