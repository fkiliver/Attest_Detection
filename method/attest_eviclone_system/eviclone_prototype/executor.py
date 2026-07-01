from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .context_completion import (
    build_context_added_context_certificate,
    build_context_probe_execution_path_certificate,
    build_context_source_safety_certificate,
    complete_context_with_llm,
)
from .dataset import ClonePair
from .expert_invocation import INVOCATION_HASH_FIELD
from .heuristics import target_family
from .probe_synthesis import build_probe_source_binding_certificate, synthesize_probe_with_llm


JAVA_EXECUTION_CERTIFICATE_SCHEMA_VERSION = "eviclone-java-execution-certificate/v1"
JAVA_EXECUTION_SANDBOX_SCHEMA_VERSION = "eviclone-java-execution-sandbox/v1"
JAVA_TOOLCHAIN_CERTIFICATE_SCHEMA_VERSION = "eviclone-java-toolchain-certificate/v1"
JAVA_TOOLCHAIN_HASH_FIELD = "certificate_sha256"
DYNAMIC_OUTCOME_CERTIFICATE_SCHEMA_VERSION = "eviclone-dynamic-outcome-certificate/v1"
DYNAMIC_OUTCOME_HASH_FIELD = "certificate_sha256"
EXECUTION_RESULT_ORACLE_SCHEMA_VERSION = "eviclone-execution-result-oracle/v1"
EXECUTION_RESULT_ALLOWED_STATUSES = {"executed", "compile_only", "inconclusive", "not_recoverable", "invalid_output"}
RUNTIME_SOURCE_SAFETY_SCHEMA_VERSION = "eviclone-runtime-source-safety/v1"
SOURCE_ARTIFACT_SCHEMA_VERSION = "eviclone-retained-source-artifact/v1"
SOURCE_ARTIFACT_HASH_FIELD = "artifact_sha256"
PROBE_CONTRACT_SCHEMA_VERSION = "eviclone-probe-contract/v1"
PROBE_CONTRACT_HASH_FIELD = "contract_sha256"
PROBE_ADEQUACY_SCHEMA_VERSION = "eviclone-probe-adequacy-certificate/v1"
PROBE_ADEQUACY_HASH_FIELD = "certificate_sha256"
PROBE_CASE_PLAN_SCHEMA_VERSION = "eviclone-probe-case-plan/v1"
FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION = "eviclone-framework-mock-contract/v1"
FRAMEWORK_MOCK_CONTRACT_HASH_FIELD = "contract_sha256"
MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION = "eviclone-module-composition-lowering/v1"
MODULE_COMPOSITION_LOWERING_HASH_FIELD = "lowering_sha256"
CLASSPATH_RESOURCE_FIXTURE_SCHEMA_VERSION = "eviclone-classpath-resource-fixture/v1"
CLASSPATH_RESOURCE_FIXTURE_PAYLOAD = "eviclone-classpath-resource-payload\n"
CLASSPATH_RESOURCE_FIXTURE_NAMES = [
    "eviclone-resource.txt",
    "resource.txt",
    "data.txt",
    "test.txt",
    "config.properties",
    "application.properties",
    "META-INF/eviclone-resource.txt",
    "a",
]
SYSTEM_CONTEXT_FIXTURE_SCHEMA_VERSION = "eviclone-system-context-fixture/v1"
LOCALE_TIME_FIXTURE_SCHEMA_VERSION = "eviclone-locale-time-fixture/v1"
RUNTIME_FIXTURE_HASH_FIELD = "fixture_sha256"
SYSTEM_CONTEXT_PROPERTY_FIXTURE = {
    "eviclone.property": "eviclone-property-value",
    "app.env": "eviclone-test",
    "config.value": "eviclone-config-value",
    "user.name": "eviclone-user",
}
LOCALE_TIME_FIXTURE = {
    "language": "en",
    "country": "US",
    "language_tag": "en-US",
    "time_zone_id": "UTC",
}
RUNTIME_FIXTURE_SPECS = {
    "classpath_resource_fixture": {
        "schema_version": CLASSPATH_RESOURCE_FIXTURE_SCHEMA_VERSION,
        "family": "resource_loading",
    },
    "system_context_fixture": {
        "schema_version": SYSTEM_CONTEXT_FIXTURE_SCHEMA_VERSION,
        "family": "runtime_context",
    },
    "locale_time_fixture": {
        "schema_version": LOCALE_TIME_FIXTURE_SCHEMA_VERSION,
        "family": "runtime_context",
    },
}
SYSTEM_CONTEXT_ENV_FIXTURE = {
    "EVICLONE_ENV_VALUE": "eviclone-env-value",
    "APP_ENV": "eviclone-test",
    "CONFIG_ENV": "eviclone-config-value",
    "USER": "eviclone-user",
    "USERNAME": "eviclone-user",
}
RUNTIME_SOURCE_FORBIDDEN_PATTERNS = [
    ("system_exit", r"\bSystem\.exit\s*\("),
    ("runtime_exec", r"\bRuntime\.getRuntime\s*\("),
    ("process_builder", r"\bProcessBuilder\s*\("),
    ("driver_manager_connection", r"\b(?:DriverManager|java\.sql\.DriverManager)\.getConnection\s*\("),
    ("reflection_class_for_name", r"\bClass\.forName\s*\("),
    ("reflection_access_override", r"\.setAccessible\s*\("),
    ("random", r"\bnew\s+(?:java\.util\.)?(?:Random|SecureRandom)\s*\("),
    ("uuid_random", r"\b(?:UUID|java\.util\.UUID)\.randomUUID\s*\("),
    ("math_random", r"\bMath\.random\s*\("),
    ("current_time", r"\bSystem\.(?:currentTimeMillis|nanoTime)\s*\("),
    ("java_time_now", r"\b(?:Instant|LocalDate|LocalDateTime|ZonedDateTime|OffsetDateTime)\.now\s*\("),
    ("date_now", r"\bnew\s+(?:java\.util\.)?Date\s*\(\s*\)"),
    ("calendar_now", r"\b(?:Calendar|java\.util\.Calendar)\.getInstance\s*\("),
    ("thread_sleep", r"\bThread\.sleep\s*\("),
    ("new_thread", r"\bnew\s+Thread\s*\("),
    ("executors", r"\bExecutors\."),
]

_JAVA_TOOLCHAIN_CERTIFICATE_CACHE: dict[str, Any] | None = None

METHOD_RE = re.compile(
    r"(?P<prefix>(?:public|private|protected|static|final|synchronized|native|abstract|\s)+)?"
    r"(?P<return>[A-Za-z_$][\w$<>\[\].?,\s]*?)\s+"
    r"(?P<name>[A-Za-z_$][\w$]*)\s*"
    r"\((?P<params>[^)]*)\)\s*"
    r"(?:throws\s+[^{]+)?\{",
    flags=re.MULTILINE,
)


@dataclass(frozen=True)
class JavaParam:
    type_name: str
    name: str


@dataclass(frozen=True)
class JavaMethod:
    name: str
    return_type: str
    params: list[JavaParam]
    is_static: bool


def parse_method(code: str) -> JavaMethod | None:
    match = METHOD_RE.search(code)
    if not match:
        return None
    prefix = (match.group("prefix") or "").strip()
    params = parse_params(match.group("params") or "")
    return JavaMethod(
        name=match.group("name"),
        return_type=compact_type(match.group("return")),
        params=params,
        is_static="static" in prefix.split(),
    )


def parse_params(params_text: str) -> list[JavaParam]:
    params_text = params_text.strip()
    if not params_text:
        return []
    result: list[JavaParam] = []
    for raw in split_params(params_text):
        cleaned = re.sub(r"\bfinal\b", "", raw).strip()
        cleaned = re.sub(r"@\w+(?:\([^)]*\))?", "", cleaned).strip()
        pieces = cleaned.split()
        if len(pieces) < 2:
            continue
        name = pieces[-1].strip()
        type_name = compact_type(" ".join(pieces[:-1]))
        if name.endswith("[]"):
            name = name[:-2]
            type_name += "[]"
        result.append(JavaParam(type_name=type_name, name=name))
    return result


def split_params(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in text:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return parts


def compact_type(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def call_expr(class_name: str, method: JavaMethod, args: list[str]) -> str:
    target = class_name if method.is_static else f"new {class_name}()"
    return f"{target}.{method.name}({', '.join(args)})"


def simple_type(type_name: str) -> str:
    type_name = (
        type_name.replace("java.io.", "")
        .replace("java.math.", "")
        .replace("java.net.", "")
        .replace("java.nio.file.", "")
        .replace("java.time.", "")
        .replace("java.util.", "")
        .replace("java.lang.", "")
    )
    return re.sub(r"<.*>", "", type_name).strip()


def supported_probe(pair: ClonePair, method_a: JavaMethod, method_b: JavaMethod) -> tuple[str, str]:
    family = target_family(pair.functionality_name)
    if family == "copy_file":
        probe = build_copy_probe(method_a, method_b)
    elif family == "download_web":
        probe = build_download_probe(method_a, method_b)
    elif family == "secure_hash":
        probe = build_hash_probe(method_a, method_b)
    elif family == "bubble_sort":
        probe = build_sort_probe(method_a, method_b)
    else:
        probe = ""
    if not probe:
        generic_probe = build_generic_value_probe(pair, method_a, method_b)
        if generic_probe:
            return "generic_value_equivalence", generic_probe
        return family, ""
    return family, probe


def build_probe_contract(
    pair: ClonePair,
    method_a: JavaMethod,
    method_b: JavaMethod,
    *,
    probe_family: str,
    probe_factory: str,
    probe_body: str,
    mode: str,
) -> dict[str, Any]:
    contract = {
        "schema_version": PROBE_CONTRACT_SCHEMA_VERSION,
        "probe_family": probe_family,
        "probe_factory": probe_factory,
        "mode": mode,
        "target_family": target_family(pair.functionality_name),
        "method_a": method_probe_signature(method_a),
        "method_b": method_probe_signature(method_b),
        "deterministic": True,
        "no_external_services": True,
        "uses_local_loopback_server": probe_family == "download_web",
        "observation_kind": probe_observation_kind(probe_family, method_a, method_b),
        "result_fields": probe_result_fields(probe_family),
        "normalization": "normalizeValue/b64/json",
        "input_profile": probe_input_profile(probe_family, method_a, method_b, pair=pair),
        "probe_body_sha256": hashlib.sha256(probe_body.encode("utf-8", "replace")).hexdigest() if probe_body else None,
        "limitations": probe_limitations(probe_family),
    }
    contract[PROBE_CONTRACT_HASH_FIELD] = build_probe_contract_hash(contract)
    return contract


def build_llm_probe_contract(completion: dict[str, Any], *, reason: str) -> dict[str, Any]:
    payload = completion.get("payload") if isinstance(completion.get("payload"), dict) else {}
    invocation = completion.get("expert_invocation") if isinstance(completion.get("expert_invocation"), dict) else {}
    contract = {
        "schema_version": PROBE_CONTRACT_SCHEMA_VERSION,
        "probe_family": "llm_probe_synthesis",
        "probe_factory": "llm_probe_synthesis",
        "mode": "execute",
        "deterministic": True,
        "no_external_services": True,
        "uses_local_loopback_server": False,
        "observation_kind": str(payload.get("probe_kind") or "llm_synthesized_observation"),
        "result_fields": ["status", "same", "out_a", "out_b"],
        "normalization": "LLM-synthesized body validated to use printResult/printStatus",
        "input_profile": {"source": "llm_probe_body", "reason": reason, "assumptions": payload.get("assumptions") or []},
        "probe_body_sha256": payload.get("probe_body_sha256"),
        "expert_invocation_sha256": invocation.get(INVOCATION_HASH_FIELD) or invocation.get("prompt_pair_sha256"),
        "limitations": list((payload.get("semantic_preservation") or {}).get("risk_flags") or [])
        if isinstance(payload.get("semantic_preservation"), dict)
        else ["llm_probe_contract_risk_flags_missing"],
    }
    contract[PROBE_CONTRACT_HASH_FIELD] = build_probe_contract_hash(contract)
    return contract


def probe_result_fields(probe_family: str) -> list[str]:
    fields = ["status", "same", "out_a", "out_b"]
    if probe_family == "generic_value_equivalence":
        fields.append("case_summary")
    return fields


def build_llm_context_probe_contract(completion: dict[str, Any], *, mode: str, reason: str) -> dict[str, Any]:
    payload = completion.get("payload") if isinstance(completion.get("payload"), dict) else {}
    invocation = completion.get("expert_invocation") if isinstance(completion.get("expert_invocation"), dict) else {}
    contract = {
        "schema_version": PROBE_CONTRACT_SCHEMA_VERSION,
        "probe_family": "llm_context_completion",
        "probe_factory": "llm_context_completion",
        "mode": mode,
        "deterministic": True,
        "no_external_services": True,
        "uses_local_loopback_server": False,
        "observation_kind": str(payload.get("probe_strategy") or "llm_completed_harness"),
        "result_fields": ["status", "same", "out_a", "out_b"],
        "normalization": "LLM-completed EviProbe.java validated before compile/run",
        "input_profile": {
            "source": "llm_completed_java_source",
            "reason": reason,
            "assumptions": payload.get("assumptions") or [],
            "added_context": payload.get("added_context") if isinstance(payload.get("added_context"), dict) else {},
        },
        "probe_body_sha256": payload.get("java_source_sha256"),
        "expert_invocation_sha256": invocation.get(INVOCATION_HASH_FIELD) or invocation.get("prompt_pair_sha256"),
        "limitations": list((payload.get("semantic_preservation") or {}).get("risk_flags") or [])
        if isinstance(payload.get("semantic_preservation"), dict)
        else ["context_completion_risk_flags_missing"],
    }
    contract[PROBE_CONTRACT_HASH_FIELD] = build_probe_contract_hash(contract)
    return contract


def build_probe_contract_hash(contract: dict[str, Any]) -> str:
    return canonical_sha256({key: value for key, value in contract.items() if key != PROBE_CONTRACT_HASH_FIELD})


def build_probe_adequacy_certificate(probe_contract: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(probe_contract, dict) or not probe_contract:
        return None
    input_profile = probe_contract.get("input_profile") if isinstance(probe_contract.get("input_profile"), dict) else {}
    result_fields = [str(item) for item in probe_contract.get("result_fields") or []]
    probe_family = str(probe_contract.get("probe_family") or "")
    probe_factory = str(probe_contract.get("probe_factory") or "")
    observation_kind = str(probe_contract.get("observation_kind") or "")
    case_count = probe_case_count(input_profile)
    observable_indexes = (
        input_profile.get("observable_parameter_indexes")
        if isinstance(input_profile.get("observable_parameter_indexes"), list)
        else []
    )
    observable_type_keys = (
        input_profile.get("observable_parameter_type_keys")
        if isinstance(input_profile.get("observable_parameter_type_keys"), list)
        else []
    )
    case_generation = (
        input_profile.get("case_generation")
        if isinstance(input_profile.get("case_generation"), dict)
        else {}
    )
    boundary_tolerance = (
        input_profile.get("boundary_tolerance")
        if isinstance(input_profile.get("boundary_tolerance"), dict)
        else {}
    )
    case_argument_exprs = (
        input_profile.get("case_argument_exprs")
        if isinstance(input_profile.get("case_argument_exprs"), list)
        else []
    )
    case_tags = [str(item) for item in case_generation.get("case_tags") or [] if str(item)]
    boundary_case_tags = [str(item) for item in boundary_tolerance.get("boundary_case_tags") or [] if str(item)]
    boundary_case_count = count_tagged_probe_cases(case_argument_exprs, boundary_case_tags)
    errors: list[str] = []
    warnings: list[str] = []
    is_llm_declared_probe = probe_family in {"llm_probe_synthesis", "llm_context_completion"}

    if probe_contract.get("schema_version") != PROBE_CONTRACT_SCHEMA_VERSION:
        errors.append("probe_contract_schema_mismatch")
    contract_hash = probe_contract.get(PROBE_CONTRACT_HASH_FIELD)
    if not contract_hash:
        errors.append("probe_contract_self_hash_missing")
    elif contract_hash != build_probe_contract_hash(probe_contract):
        errors.append("probe_contract_self_hash_mismatch")
    if probe_contract.get("deterministic") is not True:
        errors.append("probe_contract_not_deterministic")
    if probe_contract.get("no_external_services") is not True:
        errors.append("probe_contract_allows_external_services")
    for required in ["status", "same", "out_a", "out_b"]:
        if required not in result_fields:
            errors.append(f"result_field_missing:{required}")
    if not observation_kind:
        errors.append("observation_kind_missing")
    if not isinstance(probe_contract.get("input_profile"), dict):
        errors.append("input_profile_missing")
    if case_count is None:
        if is_llm_declared_probe:
            warnings.append("case_count_declared_by_llm_artifact_not_static_profile")
        else:
            errors.append("case_count_missing")
    elif case_count < 1:
        errors.append("case_count_empty")
    probe_body_sha = probe_contract.get("probe_body_sha256")
    if probe_body_sha is not None and not looks_like_sha256(probe_body_sha):
        errors.append("probe_body_sha_invalid")

    certificate: dict[str, Any] = {
        "schema_version": PROBE_ADEQUACY_SCHEMA_VERSION,
        "trust_policy": "bounded_dynamic_probe_not_formal_proof/v1",
        "status": "verified" if not errors else "rejected",
        "probe_contract_sha256": canonical_sha256(probe_contract),
        "probe_contract_self_hash": contract_hash,
        "probe_family": probe_family,
        "probe_factory": probe_factory,
        "observation_kind": observation_kind,
        "adequacy_tier": probe_adequacy_tier(
            probe_family=probe_family,
            observation_kind=observation_kind,
            case_count=case_count,
            observable_parameter_count=len(observable_indexes),
        ),
        "case_count": case_count,
        "case_count_known": case_count is not None,
        "observable_parameter_count": len(observable_indexes),
        "observable_parameter_indexes": [int(item) for item in observable_indexes if isinstance(item, int)],
        "observable_parameter_type_keys": [str(item) for item in observable_type_keys],
        "case_generation_strategy": case_generation.get("strategy"),
        "case_generation_tags": case_tags,
        "case_plan_sha256": case_generation.get("case_plan_sha256"),
        "differential_power_tier": probe_differential_power_tier(
            case_count=case_count,
            case_tags=case_tags,
            boundary_case_count=boundary_case_count,
        ),
        "boundary_case_count": boundary_case_count,
        "partial_boundary_deviation_mode": boundary_tolerance.get("partial_boundary_deviation_mode"),
        "executor_same_policy": boundary_tolerance.get("executor_same_policy"),
        "result_fields": result_fields,
        "deterministic": probe_contract.get("deterministic") is True,
        "no_external_services": probe_contract.get("no_external_services") is True,
        "uses_local_loopback_server": probe_contract.get("uses_local_loopback_server") is True,
        "bounded_evidence_only": True,
        "limitations": list(probe_contract.get("limitations") or []),
        "validation_errors": errors,
        "validation_warnings": warnings,
    }
    certificate[PROBE_ADEQUACY_HASH_FIELD] = build_probe_adequacy_certificate_hash(certificate)
    return certificate


def probe_case_count(input_profile: dict[str, Any]) -> int | None:
    raw = input_profile.get("case_count")
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.strip().isdigit():
        return int(raw.strip())
    return None


def probe_adequacy_tier(
    *,
    probe_family: str,
    observation_kind: str,
    case_count: int | None,
    observable_parameter_count: int,
) -> str:
    if probe_family in {"llm_probe_synthesis", "llm_context_completion"}:
        return "llm_declared_bounded_probe"
    if case_count is not None and case_count >= 2 and observable_parameter_count > 0:
        return "multi_case_return_and_state_observation"
    if case_count is not None and case_count >= 2:
        return "multi_case_return_observation"
    if observation_kind in {
        "file_effect_equivalence",
        "local_loopback_http_value_equivalence",
        "array_value_or_mutation_equivalence",
    }:
        return "single_case_effect_observation"
    return "single_case_bounded_observation"


def count_tagged_probe_cases(case_argument_exprs: list[Any], tags: list[str]) -> int:
    tag_set = set(tags)
    if not tag_set:
        return 0
    count = 0
    for case in case_argument_exprs:
        if not isinstance(case, dict):
            continue
        case_tags = {str(item) for item in case.get("tags") or []}
        if case_tags & tag_set:
            count += 1
    return count


def probe_differential_power_tier(
    *,
    case_count: int | None,
    case_tags: list[str],
    boundary_case_count: int,
) -> str:
    tags = set(case_tags)
    if "branch_boundary" in tags and "boundary_neighbor" in tags and boundary_case_count >= 2:
        return "boundary_discriminative"
    if "code_string_literal" in tags:
        return "literal_sensitive"
    if case_count is not None and case_count >= 4:
        return "multi_shape_type_discriminative"
    if case_count is not None and case_count >= 2:
        return "basic_multi_case"
    return "minimal_bounded"


def build_probe_adequacy_certificate_hash(certificate: dict[str, Any]) -> str:
    return canonical_sha256({key: value for key, value in certificate.items() if key != PROBE_ADEQUACY_HASH_FIELD})


def looks_like_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def method_probe_signature(method: JavaMethod) -> dict[str, Any]:
    return {
        "name": method.name,
        "return_type": method.return_type,
        "return_type_key": generic_type_key(method.return_type),
        "params": [
            {"type": param.type_name, "type_key": generic_type_key(param.type_name), "name": param.name}
            for param in method.params
        ],
    }


def probe_observation_kind(
    probe_family: str,
    method_a: JavaMethod | None = None,
    method_b: JavaMethod | None = None,
) -> str:
    if probe_family == "generic_value_equivalence":
        if method_a is not None and method_b is not None and (
            observable_argument_indexes(method_a.params) or observable_argument_indexes(method_b.params)
        ):
            return "return_value_and_observable_argument_state_equivalence"
        return "return_value_equivalence"
    return {
        "copy_file": "file_effect_equivalence",
        "download_web": "local_loopback_http_value_equivalence",
        "secure_hash": "hash_value_equivalence",
        "bubble_sort": "array_value_or_mutation_equivalence",
    }.get(probe_family, "unknown_probe_observation")


def probe_input_profile(
    probe_family: str,
    method_a: JavaMethod,
    method_b: JavaMethod,
    *,
    pair: ClonePair | None = None,
) -> dict[str, Any]:
    if probe_family == "generic_value_equivalence":
        case_plan = build_generic_probe_case_plan(
            method_a.params,
            method_b.params,
            code_a=pair.code_a if pair else "",
            code_b=pair.code_b if pair else "",
        )
        cases = case_plan["cases"]
        return {
            "case_count": len(cases),
            "parameter_type_keys": [generic_type_key(param.type_name) for param in method_a.params],
            "observable_parameter_indexes": observable_argument_indexes(method_a.params),
            "observable_parameter_type_keys": [
                generic_type_key(method_a.params[index].type_name) for index in observable_argument_indexes(method_a.params)
            ],
            "case_argument_exprs": [
                {
                    "a": list(case["a"]),
                    "b": list(case["b"]),
                    "tags": list(case.get("tags") or []),
                    "origin": case.get("origin"),
                }
                for case in cases
            ],
            "case_generation": case_plan["generation"],
            "boundary_tolerance": case_plan["boundary_tolerance"],
        }
    return {
        "case_count": 1,
        "fixture": {
            "copy_file": "alpha/beta UTF-8 file payload",
            "download_web": "local 127.0.0.1 HTTP server serving deterministic payload",
            "secure_hash": "hash-payload UTF-8 string/bytes",
            "bubble_sort": "int array [5,-1,5,0,2]",
        }.get(probe_family, "target-family fixture"),
    }


def probe_limitations(probe_family: str) -> list[str]:
    common = ["single deterministic probe contract", "not a proof over all possible inputs"]
    by_family = {
        "download_web": ["uses local loopback server only, not external network"],
        "generic_value_equivalence": [
            "covers a bounded generated value set derived from parameter types, source literals, and branch boundary neighborhoods",
            "partial boundary deviations are annotated in the case plan but executor.same remains strict all-case equality",
        ],
        "copy_file": ["covers deterministic file-copy fixture only"],
        "secure_hash": ["covers one deterministic hash payload"],
        "bubble_sort": ["covers one deterministic integer array fixture"],
    }
    return common + by_family.get(probe_family, [])


def build_copy_probe(a: JavaMethod, b: JavaMethod) -> str:
    args_a = copy_args(a, "srcA", "dstA")
    args_b = copy_args(b, "srcB", "dstB")
    if not args_a or not args_b:
        return ""
    return f"""
        Path srcA = work.resolve("srcA.txt");
        Path srcB = work.resolve("srcB.txt");
        Path dstA = work.resolve("dstA.txt");
        Path dstB = work.resolve("dstB.txt");
        byte[] payload = "alpha\\nbeta\\n中文\\n".getBytes(StandardCharsets.UTF_8);
        Files.write(srcA, payload);
        Files.write(srcB, payload);
        {call_expr("SnippetA", a, args_a)};
        {call_expr("SnippetB", b, args_b)};
        byte[] outA = Files.exists(dstA) ? Files.readAllBytes(dstA) : new byte[0];
        byte[] outB = Files.exists(dstB) ? Files.readAllBytes(dstB) : new byte[0];
        printResult(Arrays.equals(outA, outB) && Arrays.equals(outA, payload), b64(outA), b64(outB));
    """


def copy_args(method: JavaMethod, src: str, dst: str) -> list[str] | None:
    if len(method.params) != 2:
        return None
    args: list[str] = []
    for param, value in zip(method.params, [src, dst]):
        t = simple_type(param.type_name)
        if t in {"File"}:
            args.append(f"{value}.toFile()")
        elif t in {"Path"}:
            args.append(value)
        elif t in {"String"}:
            args.append(f"{value}.toString()")
        else:
            return None
    return args


def build_download_probe(a: JavaMethod, b: JavaMethod) -> str:
    args_a = single_url_arg(a)
    args_b = single_url_arg(b)
    if not args_a or not args_b:
        return ""
    call_a = call_expr("SnippetA", a, args_a)
    call_b = call_expr("SnippetB", b, args_b)
    return f"""
        String payload = "download-payload-中文";
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/data", exchange -> {{
            byte[] bytes = payload.getBytes(StandardCharsets.UTF_8);
            exchange.sendResponseHeaders(200, bytes.length);
            try (OutputStream os = exchange.getResponseBody()) {{
                os.write(bytes);
            }}
        }});
        server.start();
        String url = "http://127.0.0.1:" + server.getAddress().getPort() + "/data";
        Object outA;
        Object outB;
        try {{
            outA = {call_a};
            outB = {call_b};
        }} finally {{
            server.stop(0);
        }}
        String normA = normalizeValue(outA);
        String normB = normalizeValue(outB);
        printResult(normA.equals(normB), normA, normB);
    """


def single_url_arg(method: JavaMethod) -> list[str] | None:
    if len(method.params) != 1:
        return None
    t = simple_type(method.params[0].type_name)
    if t == "String":
        return ["url"]
    if t == "URL":
        return ["new URL(url)"]
    return None


def build_hash_probe(a: JavaMethod, b: JavaMethod) -> str:
    args_a = hash_args(a)
    args_b = hash_args(b)
    if not args_a or not args_b:
        return ""
    call_a = call_expr("SnippetA", a, args_a)
    call_b = call_expr("SnippetB", b, args_b)
    return f"""
        String input = "hash-payload-中文";
        byte[] inputBytes = input.getBytes(StandardCharsets.UTF_8);
        Object outA = {call_a};
        Object outB = {call_b};
        String normA = normalizeValue(outA);
        String normB = normalizeValue(outB);
        printResult(normA.equals(normB), normA, normB);
    """


def hash_args(method: JavaMethod) -> list[str] | None:
    if len(method.params) != 1:
        return None
    t = simple_type(method.params[0].type_name)
    if t == "String":
        return ["input"]
    if t in {"byte[]", "Byte[]"}:
        return ["inputBytes"]
    return None


def build_sort_probe(a: JavaMethod, b: JavaMethod) -> str:
    args_a = sort_args(a, "arrA")
    args_b = sort_args(b, "arrB")
    if not args_a or not args_b:
        return ""
    call_a = call_expr("SnippetA", a, args_a)
    call_b = call_expr("SnippetB", b, args_b)
    return f"""
        int[] arrA = new int[]{{5, -1, 5, 0, 2}};
        int[] arrB = new int[]{{5, -1, 5, 0, 2}};
        Object outA = {returns_void(a, call_a, "arrA")};
        Object outB = {returns_void(b, call_b, "arrB")};
        String normA = normalizeValue(outA);
        String normB = normalizeValue(outB);
        printResult(normA.equals(normB), normA, normB);
    """


def sort_args(method: JavaMethod, arr: str) -> list[str] | None:
    if len(method.params) != 1:
        return None
    if simple_type(method.params[0].type_name) == "int[]":
        return [arr]
    return None


def returns_void(method: JavaMethod, expr: str, fallback: str) -> str:
    if simple_type(method.return_type) == "void":
        return f"runVoid(() -> {{ try {{ {expr}; }} catch (Exception e) {{ throw new RuntimeException(e); }} }}, {fallback})"
    return expr


def build_generic_value_probe(pair: ClonePair, a: JavaMethod, b: JavaMethod) -> str:
    if not generic_invocation_supported(a, b):
        return ""
    case_plan = build_generic_probe_case_plan(a.params, b.params, code_a=pair.code_a, code_b=pair.code_b)
    cases = generic_case_pairs(case_plan)
    if not cases:
        return ""
    lines: list[str] = [
        'StringBuilder outA = new StringBuilder();',
        'StringBuilder outB = new StringBuilder();',
        'StringBuilder caseSummary = new StringBuilder();',
        "boolean allSame = true;",
    ]
    for index, (args_a, args_b) in enumerate(cases):
        arg_vars_a: list[str] = []
        arg_vars_b: list[str] = []
        for arg_index, (param, arg_expr) in enumerate(zip(a.params, args_a)):
            arg_var = f"argA{index}_{arg_index}"
            arg_vars_a.append(arg_var)
            lines.append(f"{java_declaration_type(param.type_name)} {arg_var} = {arg_expr};")
        for arg_index, (param, arg_expr) in enumerate(zip(b.params, args_b)):
            arg_var = f"argB{index}_{arg_index}"
            arg_vars_b.append(arg_var)
            lines.append(f"{java_declaration_type(param.type_name)} {arg_var} = {arg_expr};")
        call_a = call_expr("SnippetA", a, arg_vars_a)
        call_b = call_expr("SnippetB", b, arg_vars_b)
        observable_a = observable_argument_vars(a.params, arg_vars_a)
        observable_b = observable_argument_vars(b.params, arg_vars_b)
        if simple_type(a.return_type) == "void":
            lines.extend([f"{call_a};", f"Object outA{index} = null;"])
        else:
            lines.append(f"Object outA{index} = {call_a};")
        if simple_type(b.return_type) == "void":
            lines.extend([f"{call_b};", f"Object outB{index} = null;"])
        else:
            lines.append(f"Object outB{index} = {call_b};")
        lines.extend(
            [
                f"String normA{index} = normalizeInvocation(outA{index}{java_varargs(observable_a)});",
                f"String normB{index} = normalizeInvocation(outB{index}{java_varargs(observable_b)});",
                f"boolean caseSame{index} = normA{index}.equals(normB{index});",
                f"allSame = allSame && caseSame{index};",
                f'outA.append("case{index}=").append(normA{index}).append("\\n");',
                f'outB.append("case{index}=").append(normB{index}).append("\\n");',
                f'caseSummary.append("case{index}|matched=").append(caseSame{index}).append("|tags=").append({case_tags_for_java(case_plan, index)}).append("\\n");',
            ]
        )
    lines.append("printResultWithCaseSummary(allSame, outA.toString(), outB.toString(), caseSummary.toString());")
    return "\n".join(lines)


def build_module_composition_lowering(
    *,
    pair: ClonePair,
    method_a: JavaMethod,
    method_b: JavaMethod,
    executable_module_graph: dict[str, Any],
) -> dict[str, Any] | None:
    return (
        build_system_context_return_module_composition_lowering(
            pair=pair,
            method_a=method_a,
            method_b=method_b,
            executable_module_graph=executable_module_graph,
        )
        or build_locale_time_return_module_composition_lowering(
            pair=pair,
            method_a=method_a,
            method_b=method_b,
            executable_module_graph=executable_module_graph,
        )
        or build_single_return_module_composition_lowering(
            pair=pair,
            method_a=method_a,
            method_b=method_b,
            executable_module_graph=executable_module_graph,
        )
        or build_branch_return_module_composition_lowering(
            pair=pair,
            method_a=method_a,
            method_b=method_b,
            executable_module_graph=executable_module_graph,
        )
        or build_collection_any_match_return_module_composition_lowering(
            pair=pair,
            method_a=method_a,
            method_b=method_b,
            executable_module_graph=executable_module_graph,
        )
        or build_collection_conditional_count_module_composition_lowering(
            pair=pair,
            method_a=method_a,
            method_b=method_b,
            executable_module_graph=executable_module_graph,
        )
    )


def build_single_return_module_composition_lowering(
    *,
    pair: ClonePair,
    method_a: JavaMethod,
    method_b: JavaMethod,
    executable_module_graph: dict[str, Any],
) -> dict[str, Any] | None:
    if not generic_return_supported(method_a.return_type, method_b.return_type):
        return None
    if simple_type(method_a.return_type) == "void" or simple_type(method_b.return_type) == "void":
        return None
    expr_a = extract_single_return_expression(pair.code_a)
    expr_b = extract_single_return_expression(pair.code_b)
    if not expr_a or not expr_b:
        return None
    if not safe_module_lowering_expression(expr_a) or not safe_module_lowering_expression(expr_b):
        return None
    if not module_graph_allows_single_return_lowering(executable_module_graph):
        return None
    case_plan = build_generic_probe_case_plan(method_a.params, method_b.params, code_a=pair.code_a, code_b=pair.code_b)
    cases = generic_case_pairs(case_plan)
    if not cases:
        return None
    probe_body = build_lowered_generic_value_probe(method_a, method_b, cases, case_metadata=case_plan["cases"])
    helper_source = build_lowered_evaluator_source(method_a, method_b, expr_a, expr_b)
    artifact = {
        "schema_version": MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION,
        "status": "applied",
        "backend": "single_return_expression_standard_module_evaluator/v1",
        "eligibility": {
            "kind": "single_return_expression",
            "generic_value_probe": True,
            "non_void_return": True,
            "environment_interaction_allowed": False,
            "state_update_allowed": False,
        },
        "source_module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "source_module_graph_self_hash": executable_module_graph.get("module_graph_sha256")
        if executable_module_graph
        else None,
        "helper_source_sha256": sha256_text(helper_source),
        "probe_body_sha256": sha256_text(probe_body),
        "evaluator_a": {
            "class_name": "ModuleLoweredA",
            "method_name": "eval",
            "return_expression_sha256": sha256_text(expr_a),
            "parameter_names": [param.name for param in method_a.params],
            "parameter_types": [param.type_name for param in method_a.params],
        },
        "evaluator_b": {
            "class_name": "ModuleLoweredB",
            "method_name": "eval",
            "return_expression_sha256": sha256_text(expr_b),
            "parameter_names": [param.name for param in method_b.params],
            "parameter_types": [param.type_name for param in method_b.params],
        },
        "probe_invokes_original_snippet_methods": False,
        "method_fragment_retained_for_compilation_boundary": True,
        "raw_source_patch_allowed": False,
        "llm_used": False,
        "limitations": [
            "first lowering backend only covers methods whose executable logic is a single return expression",
            "complex control flow, mutation, environment effects, and framework state remain on the retained-snippet backend",
        ],
    }
    artifact[MODULE_COMPOSITION_LOWERING_HASH_FIELD] = build_module_composition_lowering_hash(artifact)
    return {"probe_body": probe_body, "helper_source": helper_source, "artifact": artifact}


def build_system_context_return_module_composition_lowering(
    *,
    pair: ClonePair,
    method_a: JavaMethod,
    method_b: JavaMethod,
    executable_module_graph: dict[str, Any],
) -> dict[str, Any] | None:
    if simple_type(method_a.return_type) != "String" or simple_type(method_b.return_type) != "String":
        return None
    if method_a.params or method_b.params:
        return None
    if "system_context_fixture" not in source_context_mock_contracts(pair.code_a, pair.code_b):
        return None
    expr_a = extract_single_return_expression(pair.code_a)
    expr_b = extract_single_return_expression(pair.code_b)
    if not expr_a or not expr_b:
        return None
    reads_a = system_context_expression_reads(expr_a)
    reads_b = system_context_expression_reads(expr_b)
    if reads_a is None or reads_b is None:
        return None
    if not module_graph_allows_single_return_lowering(executable_module_graph):
        return None
    case_plan = build_generic_probe_case_plan(method_a.params, method_b.params, code_a=pair.code_a, code_b=pair.code_b)
    cases = generic_case_pairs(case_plan)
    if not cases:
        return None
    probe_body = build_lowered_generic_value_probe(method_a, method_b, cases, case_metadata=case_plan["cases"])
    helper_source = build_system_context_evaluator_source(method_a, method_b, expr_a, expr_b)
    artifact = {
        "schema_version": MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION,
        "status": "applied",
        "backend": "system_context_return_standard_module_evaluator/v1",
        "eligibility": {
            "kind": "system_context_return_expression",
            "generic_value_probe": True,
            "non_void_return": True,
            "return_type": "String",
            "environment_interaction_allowed": True,
            "required_fixture": "system_context_fixture",
            "state_update_allowed": False,
            "supported_shape": "single_return_expression_over_system_getProperty_getenv_and_string_literals",
        },
        "source_module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "source_module_graph_self_hash": executable_module_graph.get("module_graph_sha256")
        if executable_module_graph
        else None,
        "helper_source_sha256": sha256_text(helper_source),
        "probe_body_sha256": sha256_text(probe_body),
        "evaluator_a": system_context_lowering_evaluator_artifact("ModuleLoweredA", method_a, expr_a, reads_a),
        "evaluator_b": system_context_lowering_evaluator_artifact("ModuleLoweredB", method_b, expr_b, reads_b),
        "fixture_bindings": ["system_context_fixture"],
        "probe_invokes_original_snippet_methods": False,
        "method_fragment_retained_for_compilation_boundary": True,
        "raw_source_patch_allowed": False,
        "llm_used": False,
        "limitations": [
            "system-context lowering allows only System.getProperty/String.getenv reads with deterministic fixture keys",
            "arbitrary System APIs, defaults, path mutation, time, randomness, files, network, and chained method calls remain unsupported",
        ],
    }
    artifact[MODULE_COMPOSITION_LOWERING_HASH_FIELD] = build_module_composition_lowering_hash(artifact)
    return {"probe_body": probe_body, "helper_source": helper_source, "artifact": artifact}


def system_context_lowering_evaluator_artifact(
    class_name: str,
    method: JavaMethod,
    expression: str,
    reads: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "class_name": class_name,
        "method_name": "eval",
        "return_expression_sha256": sha256_text(expression),
        "system_context_reads": reads,
        "parameter_names": [param.name for param in method.params],
        "parameter_types": [param.type_name for param in method.params],
    }


def build_locale_time_return_module_composition_lowering(
    *,
    pair: ClonePair,
    method_a: JavaMethod,
    method_b: JavaMethod,
    executable_module_graph: dict[str, Any],
) -> dict[str, Any] | None:
    if simple_type(method_a.return_type) != "String" or simple_type(method_b.return_type) != "String":
        return None
    if method_a.params or method_b.params:
        return None
    if "locale_time_fixture" not in source_context_mock_contracts(pair.code_a, pair.code_b):
        return None
    expr_a = extract_single_return_expression(pair.code_a)
    expr_b = extract_single_return_expression(pair.code_b)
    if not expr_a or not expr_b:
        return None
    reads_a = locale_time_expression_reads(expr_a)
    reads_b = locale_time_expression_reads(expr_b)
    if reads_a is None or reads_b is None:
        return None
    if not module_graph_allows_single_return_lowering(executable_module_graph):
        return None
    case_plan = build_generic_probe_case_plan(method_a.params, method_b.params, code_a=pair.code_a, code_b=pair.code_b)
    cases = generic_case_pairs(case_plan)
    if not cases:
        return None
    probe_body = build_lowered_generic_value_probe(method_a, method_b, cases, case_metadata=case_plan["cases"])
    helper_source = build_system_context_evaluator_source(method_a, method_b, expr_a, expr_b)
    artifact = {
        "schema_version": MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION,
        "status": "applied",
        "backend": "locale_time_return_standard_module_evaluator/v1",
        "eligibility": {
            "kind": "locale_time_return_expression",
            "generic_value_probe": True,
            "non_void_return": True,
            "return_type": "String",
            "environment_interaction_allowed": True,
            "required_fixture": "locale_time_fixture",
            "state_update_allowed": False,
            "supported_shape": "single_return_expression_over_locale_timezone_zoneid_and_string_literals",
        },
        "source_module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "source_module_graph_self_hash": executable_module_graph.get("module_graph_sha256")
        if executable_module_graph
        else None,
        "helper_source_sha256": sha256_text(helper_source),
        "probe_body_sha256": sha256_text(probe_body),
        "evaluator_a": locale_time_lowering_evaluator_artifact("ModuleLoweredA", method_a, expr_a, reads_a),
        "evaluator_b": locale_time_lowering_evaluator_artifact("ModuleLoweredB", method_b, expr_b, reads_b),
        "fixture_bindings": ["locale_time_fixture"],
        "probe_invokes_original_snippet_methods": False,
        "method_fragment_retained_for_compilation_boundary": True,
        "raw_source_patch_allowed": False,
        "llm_used": False,
        "limitations": [
            "locale/time lowering allows only Locale.getDefault, TimeZone.getDefault, and ZoneId.systemDefault reads under deterministic fixtures",
            "arbitrary locale formatting, calendar/time APIs, host timezone forwarding, mutation, files, and framework state remain unsupported",
        ],
    }
    artifact[MODULE_COMPOSITION_LOWERING_HASH_FIELD] = build_module_composition_lowering_hash(artifact)
    return {"probe_body": probe_body, "helper_source": helper_source, "artifact": artifact}


def locale_time_lowering_evaluator_artifact(
    class_name: str,
    method: JavaMethod,
    expression: str,
    reads: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "class_name": class_name,
        "method_name": "eval",
        "return_expression_sha256": sha256_text(expression),
        "locale_time_reads": reads,
        "parameter_names": [param.name for param in method.params],
        "parameter_types": [param.type_name for param in method.params],
    }


def build_branch_return_module_composition_lowering(
    *,
    pair: ClonePair,
    method_a: JavaMethod,
    method_b: JavaMethod,
    executable_module_graph: dict[str, Any],
) -> dict[str, Any] | None:
    if not generic_return_supported(method_a.return_type, method_b.return_type):
        return None
    if simple_type(method_a.return_type) == "void" or simple_type(method_b.return_type) == "void":
        return None
    branch_a = extract_early_branch_return_expression(pair.code_a)
    branch_b = extract_early_branch_return_expression(pair.code_b)
    if not branch_a or not branch_b:
        return None
    if not all(
        safe_module_lowering_expression(part)
        for branch in (branch_a, branch_b)
        for part in (branch["condition"], branch["then_expression"], branch["fallback_expression"])
    ):
        return None
    if not module_graph_allows_branch_return_lowering(executable_module_graph):
        return None
    case_plan = build_generic_probe_case_plan(method_a.params, method_b.params, code_a=pair.code_a, code_b=pair.code_b)
    cases = generic_case_pairs(case_plan)
    if not cases:
        return None
    probe_body = build_lowered_generic_value_probe(method_a, method_b, cases, case_metadata=case_plan["cases"])
    helper_source = build_branch_return_evaluator_source(method_a, method_b, branch_a, branch_b)
    artifact = {
        "schema_version": MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION,
        "status": "applied",
        "backend": "branch_return_expression_standard_module_evaluator/v1",
        "eligibility": {
            "kind": "early_branch_return_expression",
            "generic_value_probe": True,
            "non_void_return": True,
            "environment_interaction_allowed": False,
            "state_update_allowed": False,
            "supported_shape": "if_condition_then_return_fallback_return",
        },
        "source_module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "source_module_graph_self_hash": executable_module_graph.get("module_graph_sha256")
        if executable_module_graph
        else None,
        "helper_source_sha256": sha256_text(helper_source),
        "probe_body_sha256": sha256_text(probe_body),
        "evaluator_a": branch_lowering_evaluator_artifact("ModuleLoweredA", method_a, branch_a),
        "evaluator_b": branch_lowering_evaluator_artifact("ModuleLoweredB", method_b, branch_b),
        "probe_invokes_original_snippet_methods": False,
        "method_fragment_retained_for_compilation_boundary": True,
        "raw_source_patch_allowed": False,
        "llm_used": False,
        "limitations": [
            "branch lowering covers only early-return if statements followed by a fallback return",
            "explicit else blocks, nested control flow, mutation, environment effects, and framework state remain on the retained-snippet backend",
        ],
    }
    artifact[MODULE_COMPOSITION_LOWERING_HASH_FIELD] = build_module_composition_lowering_hash(artifact)
    return {"probe_body": probe_body, "helper_source": helper_source, "artifact": artifact}


def branch_lowering_evaluator_artifact(
    class_name: str,
    method: JavaMethod,
    branch: dict[str, str],
) -> dict[str, Any]:
    return {
        "class_name": class_name,
        "method_name": "eval",
        "branch_condition_sha256": sha256_text(branch["condition"]),
        "then_return_expression_sha256": sha256_text(branch["then_expression"]),
        "fallback_return_expression_sha256": sha256_text(branch["fallback_expression"]),
        "parameter_names": [param.name for param in method.params],
        "parameter_types": [param.type_name for param in method.params],
    }


def build_collection_any_match_return_module_composition_lowering(
    *,
    pair: ClonePair,
    method_a: JavaMethod,
    method_b: JavaMethod,
    executable_module_graph: dict[str, Any],
) -> dict[str, Any] | None:
    if not generic_return_supported(method_a.return_type, method_b.return_type):
        return None
    if simple_type(method_a.return_type) == "void" or simple_type(method_b.return_type) == "void":
        return None
    loop_a = extract_foreach_any_match_return_expression(pair.code_a)
    loop_b = extract_foreach_any_match_return_expression(pair.code_b)
    if not loop_a or not loop_b:
        return None
    if not all(
        safe_module_lowering_expression(part)
        for loop in (loop_a, loop_b)
        for part in (
            loop["collection_expression"],
            loop["condition"],
            loop["then_expression"],
            loop["fallback_expression"],
        )
    ):
        return None
    if not module_graph_allows_collection_any_match_return_lowering(executable_module_graph):
        return None
    case_plan = build_generic_probe_case_plan(method_a.params, method_b.params, code_a=pair.code_a, code_b=pair.code_b)
    cases = generic_case_pairs(case_plan)
    if not cases:
        return None
    probe_body = build_lowered_generic_value_probe(method_a, method_b, cases, case_metadata=case_plan["cases"])
    helper_source = build_collection_any_match_evaluator_source(method_a, method_b, loop_a, loop_b)
    artifact = {
        "schema_version": MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION,
        "status": "applied",
        "backend": "collection_any_match_return_standard_module_evaluator/v1",
        "eligibility": {
            "kind": "foreach_any_match_return_expression",
            "generic_value_probe": True,
            "non_void_return": True,
            "environment_interaction_allowed": False,
            "state_update_allowed": False,
            "supported_shape": "foreach_item_in_collection_if_condition_return_then_fallback_return",
        },
        "source_module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "source_module_graph_self_hash": executable_module_graph.get("module_graph_sha256")
        if executable_module_graph
        else None,
        "helper_source_sha256": sha256_text(helper_source),
        "probe_body_sha256": sha256_text(probe_body),
        "evaluator_a": collection_lowering_evaluator_artifact("ModuleLoweredA", method_a, loop_a),
        "evaluator_b": collection_lowering_evaluator_artifact("ModuleLoweredB", method_b, loop_b),
        "probe_invokes_original_snippet_methods": False,
        "method_fragment_retained_for_compilation_boundary": True,
        "raw_source_patch_allowed": False,
        "llm_used": False,
        "limitations": [
            "collection lowering covers only for-each loops with an if-return body and a fallback return",
            "accumulators, mutations, nested loops, environment effects, and framework state remain on the retained-snippet backend",
        ],
    }
    artifact[MODULE_COMPOSITION_LOWERING_HASH_FIELD] = build_module_composition_lowering_hash(artifact)
    return {"probe_body": probe_body, "helper_source": helper_source, "artifact": artifact}


def collection_lowering_evaluator_artifact(
    class_name: str,
    method: JavaMethod,
    loop: dict[str, str],
) -> dict[str, Any]:
    return {
        "class_name": class_name,
        "method_name": "eval",
        "loop_kind": "foreach",
        "loop_variable": loop["item_name"],
        "loop_item_type": loop["item_type"],
        "collection_expression_sha256": sha256_text(loop["collection_expression"]),
        "branch_condition_sha256": sha256_text(loop["condition"]),
        "then_return_expression_sha256": sha256_text(loop["then_expression"]),
        "fallback_return_expression_sha256": sha256_text(loop["fallback_expression"]),
        "parameter_names": [param.name for param in method.params],
        "parameter_types": [param.type_name for param in method.params],
    }


def build_collection_conditional_count_module_composition_lowering(
    *,
    pair: ClonePair,
    method_a: JavaMethod,
    method_b: JavaMethod,
    executable_module_graph: dict[str, Any],
) -> dict[str, Any] | None:
    if generic_type_key(method_a.return_type) != "int" or generic_type_key(method_b.return_type) != "int":
        return None
    count_a = extract_foreach_conditional_count_expression(pair.code_a)
    count_b = extract_foreach_conditional_count_expression(pair.code_b)
    if not count_a or not count_b:
        return None
    if not all(
        safe_module_lowering_expression(part)
        for count in (count_a, count_b)
        for part in (count["initial_value"], count["collection_expression"], count["condition"])
    ):
        return None
    if not module_graph_allows_collection_conditional_count_lowering(executable_module_graph):
        return None
    case_plan = build_generic_probe_case_plan(method_a.params, method_b.params, code_a=pair.code_a, code_b=pair.code_b)
    cases = generic_case_pairs(case_plan)
    if not cases:
        return None
    probe_body = build_lowered_generic_value_probe(method_a, method_b, cases, case_metadata=case_plan["cases"])
    helper_source = build_collection_conditional_count_evaluator_source(method_a, method_b, count_a, count_b)
    artifact = {
        "schema_version": MODULE_COMPOSITION_LOWERING_SCHEMA_VERSION,
        "status": "applied",
        "backend": "collection_conditional_count_standard_module_evaluator/v1",
        "eligibility": {
            "kind": "foreach_conditional_count_state_update",
            "generic_value_probe": True,
            "non_void_return": True,
            "return_type": "int",
            "environment_interaction_allowed": False,
            "state_update_allowed": True,
            "supported_shape": "counter_zero_foreach_item_in_collection_if_condition_increment_counter_return_counter",
        },
        "source_module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "source_module_graph_self_hash": executable_module_graph.get("module_graph_sha256")
        if executable_module_graph
        else None,
        "helper_source_sha256": sha256_text(helper_source),
        "probe_body_sha256": sha256_text(probe_body),
        "evaluator_a": count_lowering_evaluator_artifact("ModuleLoweredA", method_a, count_a),
        "evaluator_b": count_lowering_evaluator_artifact("ModuleLoweredB", method_b, count_b),
        "probe_invokes_original_snippet_methods": False,
        "method_fragment_retained_for_compilation_boundary": True,
        "raw_source_patch_allowed": False,
        "llm_used": False,
        "limitations": [
            "conditional-count lowering covers only int counters initialized to zero and incremented by one inside an if body",
            "sum accumulators, multiple state variables, nested loops, environment effects, and framework state remain on the retained-snippet backend",
        ],
    }
    artifact[MODULE_COMPOSITION_LOWERING_HASH_FIELD] = build_module_composition_lowering_hash(artifact)
    return {"probe_body": probe_body, "helper_source": helper_source, "artifact": artifact}


def count_lowering_evaluator_artifact(
    class_name: str,
    method: JavaMethod,
    count: dict[str, str],
) -> dict[str, Any]:
    return {
        "class_name": class_name,
        "method_name": "eval",
        "loop_kind": "foreach",
        "loop_variable": count["item_name"],
        "loop_item_type": count["item_type"],
        "counter_name": count["counter_name"],
        "initial_value_sha256": sha256_text(count["initial_value"]),
        "collection_expression_sha256": sha256_text(count["collection_expression"]),
        "branch_condition_sha256": sha256_text(count["condition"]),
        "state_update_kind": count["update_kind"],
        "parameter_names": [param.name for param in method.params],
        "parameter_types": [param.type_name for param in method.params],
    }


def finalize_module_composition_lowering_artifact(
    artifact: dict[str, Any],
    *,
    executable_composition_spec: dict[str, Any],
    module_probe_plan: dict[str, Any],
    probe_contract: dict[str, Any],
) -> dict[str, Any]:
    finalized = json.loads(json.dumps(artifact, sort_keys=True))
    finalized["source_composition_sha256"] = canonical_sha256(executable_composition_spec)
    finalized["source_composition_self_hash"] = executable_composition_spec.get("composition_sha256")
    finalized["source_probe_plan_sha256"] = canonical_sha256(module_probe_plan)
    finalized["source_probe_plan_self_hash"] = module_probe_plan.get("plan_sha256")
    finalized["probe_contract_sha256"] = canonical_sha256(probe_contract)
    finalized["probe_contract_self_hash"] = probe_contract.get(PROBE_CONTRACT_HASH_FIELD)
    finalized[MODULE_COMPOSITION_LOWERING_HASH_FIELD] = build_module_composition_lowering_hash(finalized)
    return finalized


def build_module_composition_lowering_hash(artifact: dict[str, Any]) -> str:
    return canonical_sha256(
        {key: value for key, value in artifact.items() if key != MODULE_COMPOSITION_LOWERING_HASH_FIELD}
    )


def build_lowered_evaluator_source(
    method_a: JavaMethod,
    method_b: JavaMethod,
    expr_a: str,
    expr_b: str,
) -> str:
    params_a = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_a.params)
    params_b = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_b.params)
    return f"""
    public static class ModuleLoweredA {{
        public static Object eval({params_a}) throws Exception {{
            return {expr_a};
        }}
    }}

    public static class ModuleLoweredB {{
        public static Object eval({params_b}) throws Exception {{
            return {expr_b};
        }}
    }}
"""


def build_system_context_evaluator_source(
    method_a: JavaMethod,
    method_b: JavaMethod,
    expr_a: str,
    expr_b: str,
) -> str:
    params_a = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_a.params)
    params_b = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_b.params)
    return f"""
    public static class ModuleLoweredA {{
        public static Object eval({params_a}) throws Exception {{
            return {expr_a};
        }}
    }}

    public static class ModuleLoweredB {{
        public static Object eval({params_b}) throws Exception {{
            return {expr_b};
        }}
    }}
"""


def build_branch_return_evaluator_source(
    method_a: JavaMethod,
    method_b: JavaMethod,
    branch_a: dict[str, str],
    branch_b: dict[str, str],
) -> str:
    params_a = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_a.params)
    params_b = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_b.params)
    return f"""
    public static class ModuleLoweredA {{
        public static Object eval({params_a}) throws Exception {{
            if ({branch_a["condition"]}) {{
                return {branch_a["then_expression"]};
            }}
            return {branch_a["fallback_expression"]};
        }}
    }}

    public static class ModuleLoweredB {{
        public static Object eval({params_b}) throws Exception {{
            if ({branch_b["condition"]}) {{
                return {branch_b["then_expression"]};
            }}
            return {branch_b["fallback_expression"]};
        }}
    }}
"""


def build_collection_any_match_evaluator_source(
    method_a: JavaMethod,
    method_b: JavaMethod,
    loop_a: dict[str, str],
    loop_b: dict[str, str],
) -> str:
    params_a = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_a.params)
    params_b = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_b.params)
    return f"""
    public static class ModuleLoweredA {{
        public static Object eval({params_a}) throws Exception {{
            for ({loop_a["item_type"]} {loop_a["item_name"]} : {loop_a["collection_expression"]}) {{
                if ({loop_a["condition"]}) {{
                    return {loop_a["then_expression"]};
                }}
            }}
            return {loop_a["fallback_expression"]};
        }}
    }}

    public static class ModuleLoweredB {{
        public static Object eval({params_b}) throws Exception {{
            for ({loop_b["item_type"]} {loop_b["item_name"]} : {loop_b["collection_expression"]}) {{
                if ({loop_b["condition"]}) {{
                    return {loop_b["then_expression"]};
                }}
            }}
            return {loop_b["fallback_expression"]};
        }}
    }}
"""


def build_collection_conditional_count_evaluator_source(
    method_a: JavaMethod,
    method_b: JavaMethod,
    count_a: dict[str, str],
    count_b: dict[str, str],
) -> str:
    params_a = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_a.params)
    params_b = ", ".join(f"{java_declaration_type(param.type_name)} {param.name}" for param in method_b.params)
    return f"""
    public static class ModuleLoweredA {{
        public static Object eval({params_a}) throws Exception {{
            int {count_a["counter_name"]} = {count_a["initial_value"]};
            for ({count_a["item_type"]} {count_a["item_name"]} : {count_a["collection_expression"]}) {{
                if ({count_a["condition"]}) {{
                    {count_a["counter_name"]}++;
                }}
            }}
            return {count_a["counter_name"]};
        }}
    }}

    public static class ModuleLoweredB {{
        public static Object eval({params_b}) throws Exception {{
            int {count_b["counter_name"]} = {count_b["initial_value"]};
            for ({count_b["item_type"]} {count_b["item_name"]} : {count_b["collection_expression"]}) {{
                if ({count_b["condition"]}) {{
                    {count_b["counter_name"]}++;
                }}
            }}
            return {count_b["counter_name"]};
        }}
    }}
"""


def build_lowered_generic_value_probe(
    method_a: JavaMethod,
    method_b: JavaMethod,
    cases: list[tuple[list[str], list[str]]],
    *,
    case_metadata: list[dict[str, Any]] | None = None,
) -> str:
    lines: list[str] = [
        'StringBuilder outA = new StringBuilder();',
        'StringBuilder outB = new StringBuilder();',
        'StringBuilder caseSummary = new StringBuilder();',
        "boolean allSame = true;",
    ]
    for index, (args_a, args_b) in enumerate(cases):
        arg_vars_a: list[str] = []
        arg_vars_b: list[str] = []
        for arg_index, (param, arg_expr) in enumerate(zip(method_a.params, args_a)):
            arg_var = f"argA{index}_{arg_index}"
            arg_vars_a.append(arg_var)
            lines.append(f"{java_declaration_type(param.type_name)} {arg_var} = {arg_expr};")
        for arg_index, (param, arg_expr) in enumerate(zip(method_b.params, args_b)):
            arg_var = f"argB{index}_{arg_index}"
            arg_vars_b.append(arg_var)
            lines.append(f"{java_declaration_type(param.type_name)} {arg_var} = {arg_expr};")
        call_a = f"ModuleLoweredA.eval({', '.join(arg_vars_a)})"
        call_b = f"ModuleLoweredB.eval({', '.join(arg_vars_b)})"
        observable_a = observable_argument_vars(method_a.params, arg_vars_a)
        observable_b = observable_argument_vars(method_b.params, arg_vars_b)
        lines.append(f"Object outA{index} = {call_a};")
        lines.append(f"Object outB{index} = {call_b};")
        lines.extend(
            [
                f"String normA{index} = normalizeInvocation(outA{index}{java_varargs(observable_a)});",
                f"String normB{index} = normalizeInvocation(outB{index}{java_varargs(observable_b)});",
                f"boolean caseSame{index} = normA{index}.equals(normB{index});",
                f"allSame = allSame && caseSame{index};",
                f'outA.append("case{index}=").append(normA{index}).append("\\n");',
                f'outB.append("case{index}=").append(normB{index}).append("\\n");',
                f'caseSummary.append("case{index}|matched=").append(caseSame{index}).append("|tags=").append({case_tags_for_java(case_metadata, index)}).append("\\n");',
            ]
        )
    lines.append("printResultWithCaseSummary(allSame, outA.toString(), outB.toString(), caseSummary.toString());")
    return "\n".join(lines)


def extract_single_return_expression(code: str) -> str | None:
    from .functional_blocks import extract_method_body, split_body_into_blocks

    blocks = split_body_into_blocks(extract_method_body(code))
    if len(blocks) != 1:
        return None
    match = re.fullmatch(r"return\s+(.+);", blocks[0].strip(), flags=re.DOTALL)
    if not match:
        return None
    return match.group(1).strip()


def extract_early_branch_return_expression(code: str) -> dict[str, str] | None:
    from .functional_blocks import extract_method_body

    body = extract_method_body(code).strip()
    if not re.match(r"^if\b", body):
        return None
    pos = 2
    while pos < len(body) and body[pos].isspace():
        pos += 1
    if pos >= len(body) or body[pos] != "(":
        return None
    condition, pos = parse_balanced_segment(body, pos, "(", ")")
    if condition is None:
        return None
    then_expression, rest = parse_return_clause(body[pos:].strip())
    if then_expression is None:
        return None
    rest = rest.strip()
    if re.match(r"^else\b", rest):
        return None
    fallback_expression, rest = parse_return_statement(rest)
    if fallback_expression is None or rest.strip():
        return None
    return {
        "condition": condition.strip(),
        "then_expression": then_expression.strip(),
        "fallback_expression": fallback_expression.strip(),
    }


def system_context_expression_reads(expr: str) -> list[dict[str, str]] | None:
    allowed_properties = set(SYSTEM_CONTEXT_PROPERTY_FIXTURE) | {"user.home", "java.io.tmpdir"}
    allowed_env = set(SYSTEM_CONTEXT_ENV_FIXTURE) | {"HOME", "TMPDIR", "TEMP", "TMP"}
    reads: list[dict[str, str]] = []

    def replace_call(match: re.Match[str]) -> str:
        kind = match.group("kind")
        key = match.group("key")
        if kind == "getProperty":
            if key not in allowed_properties:
                raise ValueError("property_key_not_allowed")
            reads.append({"kind": "system_property", "key": key})
        else:
            if key not in allowed_env:
                raise ValueError("environment_variable_not_allowed")
            reads.append({"kind": "environment_variable", "key": key})
        return "VALUE"

    call_pattern = re.compile(
        r"System\s*\.\s*(?P<kind>getProperty|getenv)\s*\(\s*\"(?P<key>[^\"\\]+)\"\s*\)"
    )
    try:
        reduced = call_pattern.sub(replace_call, expr)
    except ValueError:
        return None
    if not reads:
        return None
    reduced = re.sub(r'"(?:[^"\\]|\\.)*"', "VALUE", reduced)
    reduced = re.sub(r"\bVALUE\b", "", reduced)
    reduced = re.sub(r"[\s+()]+", "", reduced)
    if reduced:
        return None
    return reads


def locale_time_expression_reads(expr: str) -> list[dict[str, str]] | None:
    reads: list[dict[str, str]] = []
    allowed_calls: list[tuple[re.Pattern[str], dict[str, str]]] = [
        (
            re.compile(
                r"\b(?:java\.util\.)?Locale\s*\.\s*getDefault\s*\(\s*\)\s*\.\s*toLanguageTag\s*\(\s*\)"
            ),
            {"kind": "locale", "field": "language_tag"},
        ),
        (
            re.compile(
                r"\b(?:java\.util\.)?Locale\s*\.\s*getDefault\s*\(\s*\)\s*\.\s*getLanguage\s*\(\s*\)"
            ),
            {"kind": "locale", "field": "language"},
        ),
        (
            re.compile(
                r"\b(?:java\.util\.)?Locale\s*\.\s*getDefault\s*\(\s*\)\s*\.\s*getCountry\s*\(\s*\)"
            ),
            {"kind": "locale", "field": "country"},
        ),
        (
            re.compile(
                r"\b(?:java\.util\.)?TimeZone\s*\.\s*getDefault\s*\(\s*\)\s*\.\s*getID\s*\(\s*\)"
            ),
            {"kind": "time_zone", "field": "id"},
        ),
        (
            re.compile(
                r"\b(?:java\.time\.)?ZoneId\s*\.\s*systemDefault\s*\(\s*\)\s*\.\s*getId\s*\(\s*\)"
            ),
            {"kind": "zone_id", "field": "id"},
        ),
    ]

    reduced = expr
    for pattern, read in allowed_calls:
        def replace_call(match: re.Match[str], read: dict[str, str] = read) -> str:
            reads.append(dict(read))
            return "VALUE"

        reduced = pattern.sub(replace_call, reduced)

    if not reads:
        return None
    reduced = re.sub(r'"(?:[^"\\]|\\.)*"', "VALUE", reduced)
    reduced = re.sub(r"\bVALUE\b", "", reduced)
    reduced = re.sub(r"[\s+()]+", "", reduced)
    if reduced:
        return None
    return reads


def extract_foreach_any_match_return_expression(code: str) -> dict[str, str] | None:
    from .functional_blocks import extract_method_body

    body = extract_method_body(code).strip()
    if not re.match(r"^for\b", body):
        return None
    pos = len("for")
    while pos < len(body) and body[pos].isspace():
        pos += 1
    if pos >= len(body) or body[pos] != "(":
        return None
    header, pos = parse_balanced_segment(body, pos, "(", ")")
    if header is None:
        return None
    loop_header = parse_foreach_header(header)
    if not loop_header:
        return None
    loop_body, rest = parse_loop_body_clause(body[pos:].strip())
    if loop_body is None:
        return None
    branch = extract_if_return_from_loop_body(loop_body)
    if not branch:
        return None
    fallback_expression, rest = parse_return_statement(rest.strip())
    if fallback_expression is None or rest.strip():
        return None
    return {
        **loop_header,
        "condition": branch["condition"],
        "then_expression": branch["then_expression"],
        "fallback_expression": fallback_expression.strip(),
    }


def extract_foreach_conditional_count_expression(code: str) -> dict[str, str] | None:
    from .functional_blocks import extract_method_body

    body = extract_method_body(code).strip()
    init = parse_counter_initialization(body)
    if not init:
        return None
    rest = init["rest"].strip()
    if not re.match(r"^for\b", rest):
        return None
    pos = len("for")
    while pos < len(rest) and rest[pos].isspace():
        pos += 1
    if pos >= len(rest) or rest[pos] != "(":
        return None
    header, pos = parse_balanced_segment(rest, pos, "(", ")")
    if header is None:
        return None
    loop_header = parse_foreach_header(header)
    if not loop_header:
        return None
    loop_body, after_loop = parse_loop_body_clause(rest[pos:].strip())
    if loop_body is None:
        return None
    update = extract_if_counter_update_from_loop_body(loop_body, init["counter_name"])
    if not update:
        return None
    return_expr, remaining = parse_return_statement(after_loop.strip())
    if return_expr is None or remaining.strip() or return_expr.strip() != init["counter_name"]:
        return None
    return {
        **loop_header,
        "counter_name": init["counter_name"],
        "counter_type": init["counter_type"],
        "initial_value": init["initial_value"],
        "condition": update["condition"],
        "update_kind": update["update_kind"],
    }


def parse_counter_initialization(body: str) -> dict[str, str] | None:
    semicolon = find_top_level_semicolon(body)
    if semicolon < 0:
        return None
    statement = body[:semicolon].strip()
    rest = body[semicolon + 1 :].strip()
    match = re.fullmatch(
        r"(?P<type>int|Integer)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?P<value>0)",
        statement,
    )
    if not match:
        return None
    return {
        "counter_type": match.group("type"),
        "counter_name": match.group("name"),
        "initial_value": match.group("value"),
        "rest": rest,
    }


def extract_if_counter_update_from_loop_body(loop_body: str, counter_name: str) -> dict[str, str] | None:
    branch = parse_if_update_clause(loop_body.strip(), counter_name)
    if branch is None or branch["rest"].strip():
        return None
    return {"condition": branch["condition"], "update_kind": branch["update_kind"]}


def parse_if_update_clause(text: str, counter_name: str) -> dict[str, str] | None:
    text = text.strip()
    if not re.match(r"^if\b", text):
        return None
    pos = len("if")
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != "(":
        return None
    condition, pos = parse_balanced_segment(text, pos, "(", ")")
    if condition is None:
        return None
    update_source, rest = parse_update_clause(text[pos:].strip())
    if update_source is None:
        return None
    update_kind = classify_counter_update(update_source, counter_name)
    if update_kind is None:
        return None
    return {
        "condition": condition.strip(),
        "update_kind": update_kind,
        "rest": rest.strip(),
    }


def parse_update_clause(text: str) -> tuple[str | None, str]:
    text = text.strip()
    if text.startswith("{"):
        block, pos = parse_balanced_segment(text, 0, "{", "}")
        if block is None:
            return None, text
        update, remaining = parse_single_update_statement(block.strip())
        if update is None or remaining.strip():
            return None, text
        return update, text[pos:].strip()
    return parse_single_update_statement(text)


def parse_single_update_statement(text: str) -> tuple[str | None, str]:
    semicolon = find_top_level_semicolon(text)
    if semicolon < 0:
        return None, text
    update = text[:semicolon].strip()
    if not update:
        return None, text
    return update, text[semicolon + 1 :].strip()


def classify_counter_update(update: str, counter_name: str) -> str | None:
    escaped = re.escape(counter_name)
    if re.fullmatch(rf"{escaped}\s*\+\+", update) or re.fullmatch(rf"\+\+\s*{escaped}", update):
        return "increment_by_one"
    if re.fullmatch(rf"{escaped}\s*=\s*{escaped}\s*\+\s*1", update):
        return "assign_plus_one"
    if re.fullmatch(rf"{escaped}\s*=\s*1\s*\+\s*{escaped}", update):
        return "assign_one_plus"
    return None


def parse_foreach_header(header: str) -> dict[str, str] | None:
    parts = split_top_level_once(header, ":")
    if not parts:
        return None
    left, right = parts
    pieces = left.strip().split()
    if len(pieces) < 2:
        return None
    item_name = pieces[-1].strip()
    item_type = " ".join(pieces[:-1]).replace("final ", "").strip()
    collection_expression = right.strip()
    if not item_name or not item_type or not collection_expression:
        return None
    if not re.fullmatch(r"[A-Za-z_$][\w$]*", item_name):
        return None
    return {
        "item_type": item_type,
        "item_name": item_name,
        "collection_expression": collection_expression,
    }


def parse_loop_body_clause(text: str) -> tuple[str | None, str]:
    text = text.strip()
    if text.startswith("{"):
        block, pos = parse_balanced_segment(text, 0, "{", "}")
        if block is None:
            return None, text
        return block.strip(), text[pos:].strip()
    if not re.match(r"^if\b", text):
        return None, text
    branch = parse_if_return_clause(text)
    if branch is None:
        return None, text
    return branch["source"], branch["rest"]


def extract_if_return_from_loop_body(loop_body: str) -> dict[str, str] | None:
    branch = parse_if_return_clause(loop_body.strip())
    if branch is None:
        return None
    if branch["rest"].strip():
        return None
    return {
        "condition": branch["condition"],
        "then_expression": branch["then_expression"],
    }


def parse_if_return_clause(text: str) -> dict[str, str] | None:
    text = text.strip()
    if not re.match(r"^if\b", text):
        return None
    pos = len("if")
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != "(":
        return None
    condition, pos = parse_balanced_segment(text, pos, "(", ")")
    if condition is None:
        return None
    then_expression, rest = parse_return_clause(text[pos:].strip())
    if then_expression is None:
        return None
    source_len = len(text) - len(rest)
    return {
        "condition": condition.strip(),
        "then_expression": then_expression.strip(),
        "source": text[:source_len].strip(),
        "rest": rest.strip(),
    }


def parse_return_clause(text: str) -> tuple[str | None, str]:
    text = text.strip()
    if text.startswith("{"):
        block, pos = parse_balanced_segment(text, 0, "{", "}")
        if block is None:
            return None, text
        expression, remaining = parse_return_statement(block.strip())
        if expression is None or remaining.strip():
            return None, text
        return expression, text[pos:].strip()
    return parse_return_statement(text)


def parse_return_statement(text: str) -> tuple[str | None, str]:
    text = text.strip()
    if not re.match(r"^return\b", text):
        return None, text
    expr_text = text[len("return") :].strip()
    semicolon = find_top_level_semicolon(expr_text)
    if semicolon < 0:
        return None, text
    expression = expr_text[:semicolon].strip()
    if not expression:
        return None, text
    return expression, expr_text[semicolon + 1 :].strip()


def parse_balanced_segment(
    text: str,
    start: int,
    open_char: str,
    close_char: str,
) -> tuple[str | None, int]:
    if start >= len(text) or text[start] != open_char:
        return None, start
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    return None, start


def find_top_level_semicolon(text: str) -> int:
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth = max(0, depth - 1)
        elif char == ";" and depth == 0:
            return index
    return -1


def split_top_level_once(text: str, delimiter: str) -> tuple[str, str] | None:
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char in "([{<":
            depth += 1
        elif char in ")]}>":
            depth = max(0, depth - 1)
        elif char == delimiter and depth == 0:
            return text[:index], text[index + 1 :]
    return None


def safe_module_lowering_expression(expr: str) -> bool:
    if not expr or any(token in expr for token in [";", "{", "}"]):
        return False
    if re.search(r"(?<![=!<>])=(?!=)", expr):
        return False
    forbidden = [
        r"\bSystem\.",
        r"\bRuntime\b",
        r"\bProcessBuilder\b",
        r"\bThread\b",
        r"\bFiles\b",
        r"\bFile\b",
        r"\bPath\b",
        r"\bInputStream\b",
        r"\bOutputStream\b",
        r"\bReader\b",
        r"\bWriter\b",
        r"\bURL\b",
        r"\bURI\b",
        r"\bSocket\b",
        r"\bConnection\b",
        r"\bResultSet\b",
        r"\bStatement\b",
        r"\bHttpServlet",
        r"\bJFrame\b",
        r"\bLocale\b",
        r"\bTimeZone\b",
        r"\bZoneId\b",
        r"\bDate\b",
        r"\bCalendar\b",
        r"\bInstant\b",
        r"\bLocalDate",
        r"\bMath\.random\s*\(",
        r"\bnew\s+Random\s*\(",
    ]
    return not any(re.search(pattern, expr) for pattern in forbidden)


def module_graph_allows_single_return_lowering(executable_module_graph: dict[str, Any]) -> bool:
    side_graphs = (
        executable_module_graph.get("side_graphs")
        if isinstance(executable_module_graph.get("side_graphs"), dict)
        else {}
    )
    for side in ("a", "b"):
        side_graph = side_graphs.get(side) if isinstance(side_graphs.get(side), dict) else {}
        module_types = [str(node.get("module_type")) for node in side_graph.get("nodes") or [] if isinstance(node, dict)]
        if module_types != ["return_mapping"]:
            return False
    return True


def module_graph_allows_branch_return_lowering(executable_module_graph: dict[str, Any]) -> bool:
    side_graphs = (
        executable_module_graph.get("side_graphs")
        if isinstance(executable_module_graph.get("side_graphs"), dict)
        else {}
    )
    for side in ("a", "b"):
        side_graph = side_graphs.get(side) if isinstance(side_graphs.get(side), dict) else {}
        module_types = [str(node.get("module_type")) for node in side_graph.get("nodes") or [] if isinstance(node, dict)]
        if len(module_types) not in {2, 3}:
            return False
        if module_types[0] != "branch_guard":
            return False
        if any(module_type != "return_mapping" for module_type in module_types[1:]):
            return False
    return True


def module_graph_allows_collection_any_match_return_lowering(executable_module_graph: dict[str, Any]) -> bool:
    side_graphs = (
        executable_module_graph.get("side_graphs")
        if isinstance(executable_module_graph.get("side_graphs"), dict)
        else {}
    )
    for side in ("a", "b"):
        side_graph = side_graphs.get(side) if isinstance(side_graphs.get(side), dict) else {}
        module_types = [str(node.get("module_type")) for node in side_graph.get("nodes") or [] if isinstance(node, dict)]
        if module_types != ["collection_iteration", "branch_guard", "return_mapping"]:
            return False
    return True


def module_graph_allows_collection_conditional_count_lowering(executable_module_graph: dict[str, Any]) -> bool:
    side_graphs = (
        executable_module_graph.get("side_graphs")
        if isinstance(executable_module_graph.get("side_graphs"), dict)
        else {}
    )
    for side in ("a", "b"):
        side_graph = side_graphs.get(side) if isinstance(side_graphs.get(side), dict) else {}
        module_types = [str(node.get("module_type")) for node in side_graph.get("nodes") or [] if isinstance(node, dict)]
        if module_types != ["state_update", "collection_iteration", "branch_guard", "return_mapping"]:
            return False
    return True


def generic_invocation_supported(a: JavaMethod, b: JavaMethod) -> bool:
    if generic_return_supported(a.return_type, b.return_type):
        return True
    return (
        simple_type(a.return_type) == "void"
        and simple_type(b.return_type) == "void"
        and bool(observable_argument_indexes(a.params))
        and [generic_type_key(param.type_name) for param in a.params]
        == [generic_type_key(param.type_name) for param in b.params]
    )


def generic_return_supported(return_a: str, return_b: str) -> bool:
    norm_a = generic_type_key(return_a)
    norm_b = generic_type_key(return_b)
    comparable_return_keys = {
        "string",
        "mutable_string",
        "int",
        "long",
        "double",
        "float",
        "big_decimal",
        "big_integer",
        "boolean",
        "bytes",
        "string_array",
        "int_array",
        "integer_array",
        "long_array",
        "long_object_array",
        "double_array",
        "double_object_array",
        "boolean_array",
        "boolean_object_array",
        "collection_list",
        "collection_set",
        "collection_map",
        "properties",
        "optional",
        "optional_int",
        "optional_long",
        "optional_double",
        "date",
        "calendar",
        "instant",
        "local_date",
        "local_datetime",
        "url",
        "uri",
        "url_connection",
        "swing_button",
        "swing_text_field",
        "swing_label",
        "swing_panel",
        "swing_frame",
        "swing_popup_menu",
        "swing_button_jdk",
        "swing_text_field_jdk",
        "swing_label_jdk",
        "swing_panel_jdk",
        "swing_popup_menu_jdk",
        "io_input_stream",
        "io_output_stream",
        "io_reader",
        "io_writer",
    }
    if norm_a == "void" or norm_b == "void":
        return False
    if norm_a.startswith("local_enum:") and norm_a == norm_b:
        return True
    return norm_a in comparable_return_keys and norm_a == norm_b


GENERIC_OBSERVABLE_PARAMETER_KEYS = {
    "io_input_stream",
    "io_output_stream",
    "io_reader",
    "io_writer",
    "servlet_request",
    "servlet_response",
    "servlet_session",
    "servlet_cookie",
    "jdbc_data_source",
    "jdbc_data_source_jdk",
    "collection_list",
    "collection_set",
    "collection_map",
    "properties",
    "date",
    "calendar",
    "mutable_string",
    "string_array",
    "int_array",
    "integer_array",
    "long_array",
    "long_object_array",
    "double_array",
    "double_object_array",
    "boolean_array",
    "boolean_object_array",
}


def observable_argument_indexes(params: list[JavaParam]) -> list[int]:
    return [
        index
        for index, param in enumerate(params)
        if generic_type_key(param.type_name) in GENERIC_OBSERVABLE_PARAMETER_KEYS
    ]


def observable_argument_vars(params: list[JavaParam], variables: list[str]) -> list[str]:
    return [variables[index] for index in observable_argument_indexes(params)]


def java_varargs(variables: list[str]) -> str:
    return "".join(f", {variable}" for variable in variables)


def java_declaration_type(type_name: str) -> str:
    return compact_type(type_name.replace("final ", ""))


def is_potential_local_enum_type(type_name: str) -> bool:
    t = simple_type(type_name).replace("final ", "").strip()
    return bool(re.fullmatch(r"[A-Z][A-Za-z0-9_$]*", t)) and t not in {
        "String",
        "CharSequence",
        "StringBuilder",
        "StringBuffer",
        "File",
        "Path",
        "URI",
        "URL",
        "URLConnection",
        "HttpURLConnection",
        "InputStream",
        "OutputStream",
        "Reader",
        "Writer",
        "PrintWriter",
        "Date",
        "Calendar",
        "GregorianCalendar",
        "Locale",
        "TimeZone",
        "Instant",
        "LocalDate",
        "LocalDateTime",
        "BigDecimal",
        "BigInteger",
        "List",
        "ArrayList",
        "LinkedList",
        "Collection",
        "Iterable",
        "Set",
        "HashSet",
        "LinkedHashSet",
        "Map",
        "HashMap",
        "LinkedHashMap",
        "Properties",
        "Optional",
        "OptionalInt",
        "OptionalLong",
        "OptionalDouble",
        "Integer",
        "Long",
        "Double",
        "Float",
        "Boolean",
        "Byte",
        "Short",
        "Object",
        "Class",
        "Exception",
        "Throwable",
    }


def local_enum_type_name(type_name: str) -> str:
    return simple_type(type_name).replace("final ", "").strip()


def build_generic_probe_case_plan(
    params_a: list[JavaParam],
    params_b: list[JavaParam],
    *,
    code_a: str = "",
    code_b: str = "",
) -> dict[str, Any]:
    code_text = f"{code_a}\n{code_b}"
    empty_plan = {
        "cases": [],
        "case_count": 0,
        "generation": {
            "schema_version": PROBE_CASE_PLAN_SCHEMA_VERSION,
            "strategy": "code_aware_boundary_differential_sampling/v1",
            "status": "unsupported",
            "max_case_count": 8,
            "case_tags": [],
            "boundary_sources": {},
            "discrimination_goals": [],
        },
        "boundary_tolerance": boundary_tolerance_policy(),
    }
    if len(params_a) != len(params_b):
        return empty_plan
    if not params_a:
        plan = json.loads(json.dumps(empty_plan, sort_keys=True))
        plan["cases"] = [{"a": [], "b": [], "tags": ["no_argument"], "origin": "no_argument"}]
        plan["case_count"] = 1
        plan["generation"].update(
            {
                "status": "generated",
                "case_tags": ["no_argument"],
                "discrimination_goals": ["zero_arity_return_observation"],
            }
        )
        plan["generation"]["case_plan_sha256"] = canonical_sha256(
            {key: value for key, value in plan.items() if key != "generation"}
        )
        return plan

    value_sets: list[dict[str, Any]] = []
    all_tags: set[str] = set()
    boundary_sources = generic_probe_boundary_sources(code_text, params_a, params_b)
    for param_a, param_b in zip(params_a, params_b):
        type_a = generic_type_key(param_a.type_name)
        type_b = generic_type_key(param_b.type_name)
        if type_a != type_b:
            return empty_plan
        candidates = generic_value_candidates_for_param(
            type_a,
            param_a=param_a,
            param_b=param_b,
            code_text=code_text,
        )
        if not candidates:
            return empty_plan
        value_sets.append({"type_key": type_a, "candidates": candidates})
        for candidate in candidates:
            all_tags.update(str(tag) for tag in candidate.get("tags") or [])

    case_count = min(8, max(len(item["candidates"]) for item in value_sets))
    cases: list[dict[str, Any]] = []
    for index in range(case_count):
        args_a: list[str] = []
        args_b: list[str] = []
        case_tags: set[str] = set()
        origins: set[str] = set()
        for value_set in value_sets:
            candidates = value_set["candidates"]
            candidate = candidates[index % len(candidates)]
            args_a.append(str(candidate["a"]))
            args_b.append(str(candidate["b"]))
            case_tags.update(str(tag) for tag in candidate.get("tags") or [])
            origins.add(str(candidate.get("origin") or "generated"))
        if not case_tags:
            case_tags.add("type_default")
        cases.append(
            {
                "a": args_a,
                "b": args_b,
                "tags": sorted(case_tags),
                "origin": "code_aware" if any(origin != "type_default" for origin in origins) else "type_default",
            }
        )

    generation = {
        "schema_version": PROBE_CASE_PLAN_SCHEMA_VERSION,
        "strategy": "code_aware_boundary_differential_sampling/v1",
        "status": "generated",
        "max_case_count": 8,
        "case_tags": sorted(all_tags),
        "boundary_sources": boundary_sources,
        "discrimination_goals": generic_probe_discrimination_goals(sorted(all_tags), boundary_sources),
    }
    plan = {
        "cases": cases,
        "case_count": len(cases),
        "generation": generation,
        "boundary_tolerance": boundary_tolerance_policy(),
    }
    generation["case_plan_sha256"] = canonical_sha256(
        {
            "case_count": plan["case_count"],
            "cases": plan["cases"],
            "boundary_tolerance": plan["boundary_tolerance"],
            "generation": {key: value for key, value in generation.items() if key != "case_plan_sha256"},
        }
    )
    return plan


def generic_argument_cases(
    params_a: list[JavaParam],
    params_b: list[JavaParam],
    *,
    code_a: str = "",
    code_b: str = "",
) -> list[tuple[list[str], list[str]]]:
    plan = build_generic_probe_case_plan(params_a, params_b, code_a=code_a, code_b=code_b)
    return [(list(case["a"]), list(case["b"])) for case in plan["cases"]]


def generic_case_pairs(case_plan: dict[str, Any]) -> list[tuple[list[str], list[str]]]:
    return [
        (list(case.get("a") or []), list(case.get("b") or []))
        for case in case_plan.get("cases") or []
        if isinstance(case, dict)
    ]


def case_tags_for_java(case_plan_or_cases: dict[str, Any] | list[dict[str, Any]] | None, index: int) -> str:
    if isinstance(case_plan_or_cases, dict):
        cases = case_plan_or_cases.get("cases") if isinstance(case_plan_or_cases.get("cases"), list) else []
    elif isinstance(case_plan_or_cases, list):
        cases = case_plan_or_cases
    else:
        cases = []
    case = cases[index] if 0 <= index < len(cases) and isinstance(cases[index], dict) else {}
    tags = ",".join(str(tag) for tag in case.get("tags") or [])
    return java_string_literal(tags)


def generic_value_candidates_for_param(
    type_key: str,
    *,
    param_a: JavaParam,
    param_b: JavaParam,
    code_text: str,
) -> list[dict[str, Any]]:
    base_a = generic_values_for_type(type_key, declared_type=param_a.type_name)
    base_b = generic_values_for_type(type_key, declared_type=param_b.type_name)
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add_candidate(expr_a: str, expr_b: str, *, tags: list[str], origin: str) -> None:
        key = (expr_a, expr_b)
        if key in seen:
            return
        seen.add(key)
        candidates.append({"a": expr_a, "b": expr_b, "tags": tags, "origin": origin})

    for index in range(max(len(base_a), len(base_b))):
        add_candidate(
            base_a[index % len(base_a)],
            base_b[index % len(base_b)],
            tags=["type_default", f"type_default_{index}"],
            origin="type_default",
        )

    for concept in code_aware_value_concepts(
        type_key,
        code_text=code_text,
        param_names=[param_a.name, param_b.name],
    ):
        expr_a = probe_value_expr_for_concept(type_key, concept["value"], declared_type=param_a.type_name)
        expr_b = probe_value_expr_for_concept(type_key, concept["value"], declared_type=param_b.type_name)
        if expr_a and expr_b:
            add_candidate(expr_a, expr_b, tags=list(concept["tags"]), origin=str(concept["origin"]))

    return candidates[:8]


def code_aware_value_concepts(
    type_key: str,
    *,
    code_text: str,
    param_names: list[str],
) -> list[dict[str, Any]]:
    concepts: list[dict[str, Any]] = []
    if type_key in {"int", "long"}:
        boundaries = extract_param_numeric_boundaries(code_text, param_names, integer_only=True)
        numeric_literals = extract_numeric_literals(code_text, integer_only=True)
        for value in boundaries:
            concepts.append({"value": value, "tags": ["branch_boundary", "code_numeric_constant"], "origin": "branch_boundary"})
            concepts.append(
                {
                    "value": value - 1,
                    "tags": ["boundary_neighbor", "below_branch_boundary"],
                    "origin": "branch_boundary_neighbor",
                }
            )
            concepts.append(
                {
                    "value": value + 1,
                    "tags": ["boundary_neighbor", "above_branch_boundary"],
                    "origin": "branch_boundary_neighbor",
                }
            )
        for value in numeric_literals:
            concepts.append({"value": value, "tags": ["code_numeric_constant"], "origin": "code_numeric_constant"})
    elif type_key in {"double", "float"}:
        boundaries = extract_param_numeric_boundaries(code_text, param_names, integer_only=False)
        numeric_literals = extract_numeric_literals(code_text, integer_only=False)
        for value in boundaries:
            concepts.append({"value": value, "tags": ["branch_boundary", "code_numeric_constant"], "origin": "branch_boundary"})
            concepts.append(
                {
                    "value": value - 0.5,
                    "tags": ["boundary_neighbor", "below_branch_boundary"],
                    "origin": "branch_boundary_neighbor",
                }
            )
            concepts.append(
                {
                    "value": value + 0.5,
                    "tags": ["boundary_neighbor", "above_branch_boundary"],
                    "origin": "branch_boundary_neighbor",
                }
            )
        for value in numeric_literals:
            concepts.append({"value": value, "tags": ["code_numeric_constant"], "origin": "code_numeric_constant"})
    elif type_key in {"string", "mutable_string", "bytes"}:
        for literal in extract_string_literals(code_text):
            concepts.append({"value": literal, "tags": ["code_string_literal"], "origin": "code_string_literal"})
            if literal:
                concepts.append(
                    {
                        "value": f" {literal} ",
                        "tags": ["boundary_neighbor", "padded_string_literal"],
                        "origin": "string_boundary_neighbor",
                    }
                )
    return dedupe_probe_concepts(concepts)


def dedupe_probe_concepts(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for concept in concepts:
        value = concept.get("value")
        key = (str(value), ",".join(str(tag) for tag in concept.get("tags") or []))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(concept)
        if len(deduped) >= 12:
            break
    return deduped


def probe_value_expr_for_concept(type_key: str, value: Any, *, declared_type: str) -> str:
    declared = simple_type(declared_type)
    if type_key == "int":
        if not isinstance(value, int):
            return ""
        return str(value)
    if type_key == "long":
        if not isinstance(value, int):
            return ""
        return f"{value}L"
    if type_key == "double":
        if not isinstance(value, (int, float)):
            return ""
        return f"{float(value):.6g}d"
    if type_key == "float":
        if not isinstance(value, (int, float)):
            return ""
        return f"{float(value):.6g}f"
    if type_key == "string":
        return java_string_literal(str(value))
    if type_key == "mutable_string":
        constructor = "StringBuffer" if declared == "StringBuffer" else "StringBuilder"
        return f"new {constructor}({java_string_literal(str(value))})"
    if type_key == "bytes":
        return f"{java_string_literal(str(value))}.getBytes(StandardCharsets.UTF_8)"
    return ""


def generic_probe_boundary_sources(
    code_text: str,
    params_a: list[JavaParam],
    params_b: list[JavaParam],
) -> dict[str, Any]:
    param_names = [param.name for param in params_a + params_b]
    numeric_boundaries = extract_param_numeric_boundaries(code_text, param_names, integer_only=False)
    string_literals = extract_string_literals(code_text)
    numeric_literals = extract_numeric_literals(code_text, integer_only=False)
    return {
        "numeric_literal_count": len(numeric_literals),
        "numeric_literals": [str(value) for value in numeric_literals[:8]],
        "branch_numeric_boundaries": [str(value) for value in numeric_boundaries[:8]],
        "string_literal_count": len(string_literals),
        "string_literals": string_literals[:8],
    }


def generic_probe_discrimination_goals(tags: list[str], boundary_sources: dict[str, Any]) -> list[str]:
    goals = ["type_representative_values", "return_value_differentiation"]
    if "branch_boundary" in tags:
        goals.extend(["branch_boundary_separation", "off_by_one_boundary_detection"])
    if boundary_sources.get("string_literal_count"):
        goals.append("literal_sensitive_string_behavior")
    if any(tag.startswith("type_default_") for tag in tags):
        goals.append("multi_case_regression_guard")
    return sorted(set(goals))


def boundary_tolerance_policy() -> dict[str, Any]:
    return {
        "policy": "strict_result_with_boundary_neighbor_annotation/v1",
        "executor_same_policy": "all_cases_must_match",
        "partial_boundary_deviation_mode": "annotate_only",
        "boundary_case_tags": ["branch_boundary", "boundary_neighbor"],
        "fusion_policy_note": "future fusion may report boundary-only divergence separately, but executor does not override strict equality",
    }


def strip_java_string_literals(text: str) -> str:
    return re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)


def extract_numeric_literals(code_text: str, *, integer_only: bool) -> list[int | float]:
    stripped = strip_java_string_literals(code_text)
    values: list[int | float] = []
    for match in re.finditer(r"(?<![\w.])-?\d+(?:\.\d+)?(?:[lLfFdD])?(?![\w.])", stripped):
        parsed = parse_probe_numeric_literal(match.group(0), integer_only=integer_only)
        if parsed is None:
            continue
        values.append(parsed)
    return dedupe_probe_values(values)


def extract_param_numeric_boundaries(
    code_text: str,
    param_names: list[str],
    *,
    integer_only: bool,
) -> list[int | float]:
    stripped = strip_java_string_literals(code_text)
    values: list[int | float] = []
    number = r"(?P<num>-?\d+(?:\.\d+)?(?:[lLfFdD])?)"
    unique_param_names = list(dict.fromkeys(item for item in param_names if item))
    for name in sorted(unique_param_names, key=lambda item: (-len(item), unique_param_names.index(item))):
        param = re.escape(name)
        patterns = [
            re.compile(rf"\b{param}\b\s*(?:<=|>=|<|>|==|!=)\s*{number}"),
            re.compile(rf"{number}\s*(?:<=|>=|<|>|==|!=)\s*\b{param}\b"),
        ]
        for pattern in patterns:
            for match in pattern.finditer(stripped):
                parsed = parse_probe_numeric_literal(match.group("num"), integer_only=integer_only)
                if parsed is not None:
                    values.append(parsed)
    return dedupe_probe_values(values)


def parse_probe_numeric_literal(raw: str, *, integer_only: bool) -> int | float | None:
    text = raw.strip().rstrip("lLfFdD")
    try:
        if "." in text:
            value: int | float = float(text)
            if integer_only:
                return None
        else:
            value = int(text)
    except ValueError:
        return None
    if abs(float(value)) > 1_000_000:
        return None
    return value


def dedupe_probe_values(values: list[int | float]) -> list[int | float]:
    deduped: list[int | float] = []
    seen: set[str] = set()
    for value in values:
        key = f"{float(value):.8g}" if isinstance(value, float) else str(value)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
        if len(deduped) >= 12:
            break
    return deduped


def extract_string_literals(code_text: str) -> list[str]:
    literals: list[str] = []
    for match in re.finditer(r'"((?:[^"\\]|\\.)*)"', code_text):
        value = decode_java_string_literal(match.group(1))
        if len(value) > 80:
            continue
        literals.append(value)
    return [str(value) for value in dedupe_probe_string_values(literals)[:12]]


def decode_java_string_literal(raw: str) -> str:
    replacements = {
        r"\\": "\\",
        r"\"": '"',
        r"\n": "\n",
        r"\r": "\r",
        r"\t": "\t",
    }
    value = raw
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    return value


def dedupe_probe_string_values(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def java_string_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return f'"{escaped}"'



def local_enum_context_types(method_a: JavaMethod, method_b: JavaMethod) -> list[str]:
    names: set[str] = set()
    for type_name in [method_a.return_type, method_b.return_type] + [param.type_name for param in method_a.params + method_b.params]:
        key = generic_type_key(type_name)
        if key.startswith("local_enum:"):
            names.add(key.split(":", 1)[1])
    return sorted(names)


def local_enum_context_source(enum_names: list[str]) -> str:
    return "\n".join(f"    public enum {name} {{ ALPHA, BETA, GAMMA }}" for name in enum_names)


def generic_type_key(type_name: str) -> str:
    t = simple_type(type_name)
    t = t.replace("final ", "").strip()
    mapping = {
        "String": "string",
        "CharSequence": "string",
        "StringBuilder": "mutable_string",
        "StringBuffer": "mutable_string",
        "int": "int",
        "Integer": "int",
        "long": "long",
        "Long": "long",
        "double": "double",
        "Double": "double",
        "float": "float",
        "Float": "float",
        "BigDecimal": "big_decimal",
        "BigInteger": "big_integer",
        "boolean": "boolean",
        "Boolean": "boolean",
        "byte[]": "bytes",
        "Byte[]": "bytes",
        "String[]": "string_array",
        "int[]": "int_array",
        "Integer[]": "integer_array",
        "long[]": "long_array",
        "Long[]": "long_object_array",
        "double[]": "double_array",
        "Double[]": "double_object_array",
        "boolean[]": "boolean_array",
        "Boolean[]": "boolean_object_array",
        "List": "collection_list",
        "ArrayList": "collection_list",
        "LinkedList": "collection_list",
        "Collection": "collection_list",
        "Iterable": "collection_list",
        "Set": "collection_set",
        "HashSet": "collection_set",
        "LinkedHashSet": "collection_set",
        "Map": "collection_map",
        "HashMap": "collection_map",
        "LinkedHashMap": "collection_map",
        "Properties": "properties",
        "Optional": "optional",
        "OptionalInt": "optional_int",
        "OptionalLong": "optional_long",
        "OptionalDouble": "optional_double",
        "Date": "date",
        "Calendar": "calendar",
        "GregorianCalendar": "calendar",
        "Instant": "instant",
        "LocalDate": "local_date",
        "LocalDateTime": "local_datetime",
        "URL": "url",
        "URI": "uri",
        "URLConnection": "url_connection",
        "HttpURLConnection": "url_connection",
        "InputStream": "io_input_stream",
        "ByteArrayInputStream": "io_input_stream",
        "OutputStream": "io_output_stream",
        "ByteArrayOutputStream": "io_output_stream",
        "Reader": "io_reader",
        "StringReader": "io_reader",
        "BufferedReader": "io_reader",
        "Writer": "io_writer",
        "StringWriter": "io_writer",
        "PrintWriter": "io_writer",
        "ActionEvent": "gui_action_event",
        "ActionListener": "gui_action_listener",
        "java.awt.event.ActionEvent": "gui_action_event_jdk",
        "java.awt.event.ActionListener": "gui_action_listener_jdk",
        "JButton": "swing_button",
        "JMenuItem": "swing_button",
        "javax.swing.JButton": "swing_button_jdk",
        "javax.swing.JMenuItem": "swing_button_jdk",
        "JTextField": "swing_text_field",
        "JTextArea": "swing_text_field",
        "javax.swing.JTextField": "swing_text_field_jdk",
        "javax.swing.JTextArea": "swing_text_field_jdk",
        "JLabel": "swing_label",
        "javax.swing.JLabel": "swing_label_jdk",
        "JPanel": "swing_panel",
        "javax.swing.JPanel": "swing_panel_jdk",
        "JFrame": "swing_frame",
        "JPopupMenu": "swing_popup_menu",
        "javax.swing.JPopupMenu": "swing_popup_menu_jdk",
        "HttpServletRequest": "servlet_request",
        "HttpServletResponse": "servlet_response",
        "HttpSession": "servlet_session",
        "Cookie": "servlet_cookie",
        "Connection": "jdbc_connection",
        "DataSource": "jdbc_data_source",
        "PreparedStatement": "jdbc_prepared_statement",
        "Statement": "jdbc_statement",
        "ResultSet": "jdbc_result_set",
        "java.sql.Connection": "jdbc_connection_jdk",
        "javax.sql.DataSource": "jdbc_data_source_jdk",
        "java.sql.PreparedStatement": "jdbc_prepared_statement_jdk",
        "java.sql.Statement": "jdbc_statement_jdk",
        "java.sql.ResultSet": "jdbc_result_set_jdk",
        "void": "void",
    }
    mapped = mapping.get(t, "")
    if mapped:
        return mapped
    if is_potential_local_enum_type(t):
        return f"local_enum:{t}"
    return ""


def generic_values_for_type(type_key: str, *, declared_type: str = "") -> list[str]:
    declared = simple_type(declared_type)
    if type_key.startswith("local_enum:"):
        enum_name = type_key.split(":", 1)[1]
        return [f"{enum_name}.ALPHA", f"{enum_name}.BETA", f"{enum_name}.GAMMA"]
    if type_key == "collection_list":
        return generic_list_values(declared_type, declared)
    if type_key == "collection_set":
        return generic_set_values(declared_type, declared)
    if type_key == "collection_map":
        return generic_map_values(declared_type, declared)
    if type_key == "properties":
        return ["mockProperties()"]
    if type_key == "optional":
        return ['Optional.of("alpha")', "Optional.empty()"]
    if type_key == "optional_int":
        return ["OptionalInt.of(7)", "OptionalInt.empty()"]
    if type_key == "optional_long":
        return ["OptionalLong.of(7L)", "OptionalLong.empty()"]
    if type_key == "optional_double":
        return ["OptionalDouble.of(7.25d)", "OptionalDouble.empty()"]
    if type_key == "date":
        return ["new Date(0L)", "new Date(86400000L)"]
    if type_key == "calendar":
        return ["mockCalendar()"]
    if type_key == "instant":
        return ["Instant.ofEpochMilli(0L)", "Instant.ofEpochMilli(86400000L)"]
    if type_key == "local_date":
        return ["LocalDate.of(2020, 1, 2)", "LocalDate.of(1970, 1, 1)"]
    if type_key == "local_datetime":
        return ["LocalDateTime.of(2020, 1, 2, 3, 4, 5)", "LocalDateTime.of(1970, 1, 1, 0, 0, 0)"]
    if type_key == "big_decimal":
        return ['new BigDecimal("123.45")', 'new BigDecimal("0")', 'new BigDecimal("-7.50")']
    if type_key == "big_integer":
        return ['new BigInteger("12345")', 'BigInteger.ZERO', 'new BigInteger("-7")']
    if type_key == "mutable_string":
        if declared == "StringBuffer":
            return ['new StringBuffer(" alpha ")', 'new StringBuffer("")', 'new StringBuffer("A b")']
        return ['new StringBuilder(" alpha ")', 'new StringBuilder("")', 'new StringBuilder("A b")']
    if type_key == "swing_button":
        if declared == "JButton":
            return ['new JButton("alpha-command")']
        if declared == "JMenuItem":
            return ['new JMenuItem("alpha-command")']
        return ['new JMenuItem("alpha-command")']
    if type_key == "swing_button_jdk":
        if declared == "javax.swing.JButton":
            return ['new javax.swing.JButton("alpha-command")']
        if declared == "javax.swing.JMenuItem":
            return ['new javax.swing.JMenuItem("alpha-command")']
        return ['new javax.swing.JMenuItem("alpha-command")']
    if type_key == "swing_text_field":
        if declared == "JTextArea":
            return ['new JTextArea("alpha")']
        return ['new JTextField("alpha")']
    if type_key == "swing_text_field_jdk":
        if declared == "javax.swing.JTextArea":
            return ['new javax.swing.JTextArea("alpha")']
        return ['new javax.swing.JTextField("alpha")']
    if type_key == "io_reader":
        if declared == "BufferedReader":
            return [
                'new BufferedReader(mockReader("alpha\\nbeta\\n"))',
                'new BufferedReader(mockReader(""))',
                'new BufferedReader(mockReader("A b"))',
            ]
        return [
            'mockReader("alpha\\nbeta\\n")',
            'mockReader("")',
            'mockReader("A b")',
        ]
    return {
        "string": ['"alpha"', '""', '"A b"', '"unicode"'],
        "int": ["-3", "0", "7", "42"],
        "long": ["-3L", "0L", "7L", "42L"],
        "double": ["-3.5d", "0.0d", "7.25d", "42.0d"],
        "float": ["-3.5f", "0.0f", "7.25f", "42.0f"],
        "boolean": ["false", "true"],
        "bytes": [
            '"alpha".getBytes(StandardCharsets.UTF_8)',
            'new byte[0]',
            '"A b".getBytes(StandardCharsets.UTF_8)',
        ],
        "string_array": ['new String[]{"alpha", "beta", "gamma"}', "new String[]{}", 'new String[]{"A b"}'],
        "int_array": ["new int[]{5, -1, 0}", "new int[]{}", "new int[]{7, 7, 2}"],
        "integer_array": ["new Integer[]{5, -1, 0}", "new Integer[]{}", "new Integer[]{7, 7, 2}"],
        "long_array": ["new long[]{5L, -1L, 0L}", "new long[]{}", "new long[]{7L, 7L, 2L}"],
        "long_object_array": ["new Long[]{5L, -1L, 0L}", "new Long[]{}", "new Long[]{7L, 7L, 2L}"],
        "double_array": ["new double[]{1.5d, -2.0d, 0.0d}", "new double[]{}", "new double[]{7.25d}"],
        "double_object_array": [
            "new Double[]{1.5d, -2.0d, 0.0d}",
            "new Double[]{}",
            "new Double[]{7.25d}",
        ],
        "boolean_array": ["new boolean[]{true, false, true}", "new boolean[]{}", "new boolean[]{false}"],
        "boolean_object_array": [
            "new Boolean[]{true, false, true}",
            "new Boolean[]{}",
            "new Boolean[]{false}",
        ],
        "url": ["mockUrl()"],
        "uri": ["mockUri(work)"],
        "url_connection": ["mockUrlConnection()"],
        "io_input_stream": [
            'mockInputStream("alpha\\nbeta\\n")',
            'mockInputStream("")',
            'mockInputStream("A b")',
        ],
        "io_output_stream": ["mockOutputStream()"],
        "io_writer": ["mockPrintWriter()" if declared == "PrintWriter" else "mockWriter()"],
        "gui_action_event": ["mockActionEvent()"],
        "gui_action_listener": ["mockActionListener()"],
        "gui_action_event_jdk": [
            'new java.awt.event.ActionEvent(new javax.swing.JMenuItem("alpha-command"), java.awt.event.ActionEvent.ACTION_PERFORMED, "alpha-command")'
        ],
        "gui_action_listener_jdk": [
            "new java.awt.event.ActionListener() { public void actionPerformed(java.awt.event.ActionEvent event) {} }"
        ],
        "swing_label": ['new JLabel("alpha")'],
        "swing_label_jdk": ['new javax.swing.JLabel("alpha")'],
        "swing_panel": ["new JPanel()"],
        "swing_panel_jdk": ["new javax.swing.JPanel()"],
        "swing_frame": ['new JFrame("eviclone")'],
        "swing_popup_menu": ["new JPopupMenu()"],
        "swing_popup_menu_jdk": ["new javax.swing.JPopupMenu()"],
        "servlet_request": ["mockRequest()"],
        "servlet_response": ["new HttpServletResponse()"],
        "servlet_session": ["mockSession()"],
        "servlet_cookie": ['new Cookie("user", "alice")'],
        "jdbc_connection": ["mockConnection()"],
        "jdbc_data_source": ["mockDataSource()"],
        "jdbc_prepared_statement": ['mockConnection().prepareStatement("select name from users where id=?")'],
        "jdbc_statement": ["mockConnection().createStatement()"],
        "jdbc_result_set": ["mockResultSet()"],
        "jdbc_connection_jdk": ["mockSqlConnection()"],
        "jdbc_data_source_jdk": ["mockSqlDataSource()"],
        "jdbc_prepared_statement_jdk": ['mockSqlPreparedStatement("select name from users where id=?")'],
        "jdbc_statement_jdk": ["mockSqlStatement()"],
        "jdbc_result_set_jdk": ["mockSqlResultSet()"],
    }.get(type_key, [])


def generic_collection_value_kind(declared_type: str) -> str:
    text = declared_type.lower()
    if any(token in text for token in ["integer", "<int", "long", "short", "byte"]):
        return "integer"
    if any(token in text for token in ["double", "float", "number"]):
        return "double"
    if "boolean" in text:
        return "boolean"
    return "string"


def generic_collection_values(kind: str) -> list[str]:
    if kind == "integer":
        return ["Integer.valueOf(1)", "Integer.valueOf(2)", "Integer.valueOf(3)"]
    if kind == "double":
        return ["Double.valueOf(1.5d)", "Double.valueOf(2.5d)", "Double.valueOf(3.5d)"]
    if kind == "boolean":
        return ["Boolean.TRUE", "Boolean.FALSE", "Boolean.TRUE"]
    return ['"alpha"', '"beta"', '"gamma"']


def generic_collection_type(kind: str) -> str:
    return {
        "integer": "Integer",
        "double": "Double",
        "boolean": "Boolean",
        "string": "String",
    }.get(kind, "Object")


def generic_list_values(declared_type: str, declared: str) -> list[str]:
    kind = generic_collection_value_kind(declared_type)
    value_type = generic_collection_type(kind)
    values = generic_collection_values(kind)
    constructor = "LinkedList" if declared == "LinkedList" else "ArrayList"
    if declared in {"List", "Collection", "Iterable", "ArrayList", "LinkedList"}:
        return [
            f"new {constructor}<{value_type}>()",
            f"new {constructor}<{value_type}>(Arrays.asList({values[0]}))",
            f"new {constructor}<{value_type}>(Arrays.asList({', '.join(values)}))",
            f"new {constructor}<{value_type}>(Arrays.asList({values[1]}, {values[1]}, {values[0]}))",
        ]
    return []


def generic_set_values(declared_type: str, declared: str) -> list[str]:
    kind = generic_collection_value_kind(declared_type)
    value_type = generic_collection_type(kind)
    values = generic_collection_values(kind)
    constructor = "HashSet" if declared == "HashSet" else "LinkedHashSet"
    if declared in {"Set", "HashSet", "LinkedHashSet"}:
        return [
            f"new {constructor}<{value_type}>()",
            f"new {constructor}<{value_type}>(Arrays.asList({values[0]}))",
            f"new {constructor}<{value_type}>(Arrays.asList({', '.join(values)}))",
            f"new {constructor}<{value_type}>(Arrays.asList({values[1]}, {values[1]}, {values[0]}))",
        ]
    return []


def generic_map_values(declared_type: str, declared: str) -> list[str]:
    if declared in {"Map", "LinkedHashMap"}:
        return ["mockStringMap()"]
    if declared == "HashMap":
        return ["mockStringHashMap()"]
    return []


def framework_mock_contracts(method_a: JavaMethod, method_b: JavaMethod) -> list[str]:
    framework_keys = {
        "servlet_request",
        "servlet_response",
        "servlet_session",
        "servlet_cookie",
        "jdbc_connection",
        "jdbc_data_source",
        "jdbc_prepared_statement",
        "jdbc_statement",
        "jdbc_result_set",
        "jdbc_connection_jdk",
        "jdbc_data_source_jdk",
        "jdbc_prepared_statement_jdk",
        "jdbc_statement_jdk",
        "jdbc_result_set_jdk",
        "url",
        "uri",
        "url_connection",
        "io_input_stream",
        "io_output_stream",
        "io_reader",
        "io_writer",
        "gui_action_event",
        "gui_action_listener",
        "gui_action_event_jdk",
        "gui_action_listener_jdk",
        "swing_button",
        "swing_text_field",
        "swing_label",
        "swing_panel",
        "swing_frame",
        "swing_popup_menu",
        "swing_button_jdk",
        "swing_text_field_jdk",
        "swing_label_jdk",
        "swing_panel_jdk",
        "swing_popup_menu_jdk",
    }
    keys: set[str] = set()
    for method in (method_a, method_b):
        for param in method.params:
            key = generic_type_key(param.type_name)
            if key in framework_keys:
                keys.add(framework_mock_id_for_type_key(key))
    return sorted(keys)


def source_context_mock_contracts(code_a: str, code_b: str) -> list[str]:
    text = f"{code_a}\n{code_b}"
    mocks: list[str] = []
    if re.search(r"\b(?:getResource|getResourceAsStream|getSystemResource|getSystemResourceAsStream|ClassLoader)\b", text):
        mocks.append("classpath_resource_fixture")
    if re.search(r"\bSystem\s*\.\s*(?:getProperty|getenv)\s*\(", text):
        mocks.append("system_context_fixture")
    if re.search(
        r"\b(?:Locale\s*\.\s*getDefault|TimeZone\s*\.\s*getDefault|ZoneId\s*\.\s*systemDefault|java\.time\.ZoneId\s*\.\s*systemDefault)\s*\(",
        text,
    ):
        mocks.append("locale_time_fixture")
    return mocks


def framework_mock_id_for_type_key(type_key: str) -> str:
    if type_key in {"io_input_stream", "io_output_stream", "io_reader", "io_writer"}:
        return "io_stream_fixture"
    if type_key in {"url", "uri", "url_connection"}:
        return "network_url_fixture"
    if type_key in {
        "jdbc_connection_jdk",
        "jdbc_data_source_jdk",
        "jdbc_prepared_statement_jdk",
        "jdbc_statement_jdk",
        "jdbc_result_set_jdk",
    }:
        return "jdbc_jdk_proxy"
    if type_key in {"gui_action_event_jdk", "gui_action_listener_jdk"}:
        return "gui_jdk_event"
    if type_key in {"gui_action_event", "gui_action_listener"}:
        return "gui_event"
    if type_key in {
        "swing_button_jdk",
        "swing_text_field_jdk",
        "swing_label_jdk",
        "swing_panel_jdk",
        "swing_popup_menu_jdk",
    }:
        return "swing_jdk_component"
    if type_key in {
        "swing_button",
        "swing_text_field",
        "swing_label",
        "swing_panel",
        "swing_frame",
        "swing_popup_menu",
    }:
        return "swing_component"
    return type_key


def framework_mock_contract_certificates(mock_ids: list[str]) -> list[dict[str, Any]]:
    catalog = framework_mock_contract_catalog()
    return [json.loads(json.dumps(catalog[mock_id], sort_keys=True)) for mock_id in mock_ids if mock_id in catalog]


def build_framework_mock_contract_hash(contract: dict[str, Any]) -> str:
    return canonical_sha256(
        {key: value for key, value in contract.items() if key != FRAMEWORK_MOCK_CONTRACT_HASH_FIELD}
    )


def attach_framework_mock_contract_hash(contract: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(contract, sort_keys=True))
    payload[FRAMEWORK_MOCK_CONTRACT_HASH_FIELD] = build_framework_mock_contract_hash(payload)
    return payload


def framework_mock_contract_canonical_hashes(contracts: list[dict[str, Any]]) -> list[str]:
    return [canonical_sha256(contract) for contract in contracts if isinstance(contract, dict)]


def framework_mock_contract_catalog() -> dict[str, dict[str, Any]]:
    catalog = {
        "classpath_resource_fixture": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "classpath_resource_fixture",
            "family": "resource_loading",
            "version": "deterministic-classpath-resource-fixture/v1",
            "provided_helpers": [
                "classpath file: eviclone-resource.txt",
                "classpath file: resource.txt",
                "classpath file: data.txt",
                "classpath file: test.txt",
                "classpath file: config.properties",
                "classpath file: application.properties",
                "classpath file: META-INF/eviclone-resource.txt",
                "classpath file: a",
            ],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "payload": CLASSPATH_RESOURCE_FIXTURE_PAYLOAD,
                "payload_sha256": sha256_text(CLASSPATH_RESOURCE_FIXTURE_PAYLOAD),
                "classpath_policy": "current_workdir_only",
            },
            "limitations": [
                "not a real application resource tree",
                "only a bounded set of common resource names is materialized",
                "resources are immutable UTF-8 text files written under the Java harness classpath root",
                "does not model classloader hierarchy, module path, shaded jars, or container resources",
            ],
        },
        "system_context_fixture": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "system_context_fixture",
            "family": "runtime_context",
            "version": "deterministic-system-property-env-fixture/v1",
            "provided_helpers": [
                "installSystemContextFixture(work)",
                "process env: EVICLONE_ENV_VALUE",
                "process env: APP_ENV",
                "process env: CONFIG_ENV",
                "process env: USER/USERNAME",
            ],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "system_properties": sorted(SYSTEM_CONTEXT_PROPERTY_FIXTURE.keys()),
                "environment_variables": sorted(SYSTEM_CONTEXT_ENV_FIXTURE.keys()),
                "secret_environment_forwarding": False,
            },
            "limitations": [
                "not the host operating system environment",
                "only a bounded set of properties and environment variables is modeled",
                "does not model SecurityManager, process inheritance beyond preserved Java launch essentials, or locale/timezone APIs",
                "path-valued properties are rooted under the Java harness work directory",
            ],
        },
        "locale_time_fixture": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "locale_time_fixture",
            "family": "runtime_context",
            "version": "deterministic-locale-timezone-fixture/v1",
            "provided_helpers": [
                "installLocaleTimeFixture()",
                "Locale.setDefault(Locale.US)",
                "TimeZone.setDefault(TimeZone.getTimeZone(\"UTC\"))",
            ],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": dict(LOCALE_TIME_FIXTURE),
            "limitations": [
                "not the host locale or timezone",
                "models only JVM default Locale and TimeZone APIs",
                "does not freeze current time, calendars, clocks, random values, or external schedulers",
            ],
        },
        "io_stream_fixture": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "io_stream_fixture",
            "family": "io",
            "version": "deterministic-java-io-stream-reader-writer-fixture/v1",
            "provided_helpers": [
                "mockInputStream(text)",
                "mockOutputStream()",
                "mockReader(text)",
                "mockWriter()",
                "mockPrintWriter()",
            ],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "payloads": ["alpha\\nbeta\\n", "", "A b"],
                "encoding": "UTF-8",
                "output_stream": "ByteArrayOutputStream",
                "writer": "StringWriter-backed Writer/PrintWriter",
            },
            "limitations": [
                "not a filesystem or socket stream",
                "models in-memory byte and character streams only",
                "input stream and reader fixtures are single-use consumable objects",
                "output stream and writer observations are local buffer snapshots",
            ],
        },
        "network_url_fixture": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "network_url_fixture",
            "family": "network",
            "version": "deterministic-url-uri-connection-fixture/v1",
            "provided_helpers": ["mockUrl()", "mockUri(work)", "mockUrlConnection()"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "payload": "eviclone-network-payload",
                "url": "http://eviclone.local/resource",
                "uri": "file://<work>/eviclone-uri-resource.txt",
                "content_type": "text/plain",
            },
            "limitations": [
                "not a real network stack",
                "URL uses an in-memory URLStreamHandler and never resolves DNS or opens sockets",
                "URI fixture points to a local temporary file under the Java harness work directory",
                "only common openStream/openConnection/getInputStream/toString behavior is modeled",
            ],
        },
        "gui_event": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "gui_event",
            "family": "gui",
            "version": "deterministic-gui-event/v1",
            "provided_helpers": ["mockActionEvent()", "mockActionListener()"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "action_command": "alpha-command",
                "event_id": 1001,
                "source": 'new JMenuItem("alpha-command")',
            },
            "limitations": [
                "not a real AWT event dispatch thread",
                "no native windows, focus, keyboard, mouse, timing, or listener ordering",
                "only deterministic action command/source state used by shared-input probes",
            ],
        },
        "swing_component": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "swing_component",
            "family": "gui",
            "version": "deterministic-swing-component/v1",
            "provided_helpers": [
                'new JMenuItem("alpha-command")',
                'new JTextField("alpha")',
                'new JLabel("alpha")',
                "new JPanel()",
                'new JFrame("eviclone")',
                "new JPopupMenu()",
            ],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "button_text": "alpha-command",
                "text_field": "alpha",
                "label_text": "alpha",
                "frame_title": "eviclone",
            },
            "limitations": [
                "not a real Swing runtime or native UI",
                "no painting, layout manager semantics, event dispatch thread, focus, or user interaction",
                "component state is local deterministic data only",
            ],
        },
        "gui_jdk_event": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "gui_jdk_event",
            "family": "gui",
            "version": "deterministic-jdk-awt-event/v1",
            "provided_helpers": [
                'new java.awt.event.ActionEvent(new javax.swing.JMenuItem("alpha-command"), ACTION_PERFORMED, "alpha-command")',
                "new java.awt.event.ActionListener(){...}",
            ],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "action_command": "alpha-command",
                "event_id": 1001,
                "source": 'new javax.swing.JMenuItem("alpha-command")',
            },
            "limitations": [
                "uses JDK ActionEvent object but not a real AWT event dispatch thread",
                "no native windows, focus, keyboard, mouse, timing, or listener ordering",
                "only deterministic action command/source state used by shared-input probes",
            ],
        },
        "swing_jdk_component": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "swing_jdk_component",
            "family": "gui",
            "version": "deterministic-jdk-swing-component/v1",
            "provided_helpers": [
                'new javax.swing.JMenuItem("alpha-command")',
                'new javax.swing.JTextField("alpha")',
                'new javax.swing.JLabel("alpha")',
                "new javax.swing.JPanel()",
                "new javax.swing.JPopupMenu()",
            ],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "button_text": "alpha-command",
                "text_field": "alpha",
                "label_text": "alpha",
                "popup_component_count": 0,
            },
            "limitations": [
                "uses JDK Swing components but not a real native UI",
                "no painting, layout manager semantics beyond local component list, event dispatch thread, focus, or user interaction",
                "JFrame construction is intentionally not modeled because headless environments can throw HeadlessException",
            ],
        },
        "servlet_request": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "servlet_request",
            "family": "servlet",
            "version": "deterministic-servlet-request/v1",
            "provided_helpers": ["mockRequest()", "mockSession()", "new HttpServletResponse()", "new Cookie(name,value)"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "parameter_user": "alice",
                "parameter_id": "42",
                "attribute_user": "alice",
                "header_X-EviClone": "true",
                "method": "GET",
                "context_path": "/app",
                "servlet_path": "/eviclone",
                "request_uri": "/app/eviclone",
                "query_string": "user=alice&id=42&q=alpha",
                "session_id": "eviclone-session",
            },
            "limitations": [
                "not a servlet container",
                "no filters, dispatching, security principal, async lifecycle, or real cookies",
                "only deterministic request/session state used by shared-input probes",
            ],
        },
        "servlet_response": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "servlet_response",
            "family": "servlet",
            "version": "deterministic-servlet-response/v1",
            "provided_helpers": ["new HttpServletResponse()"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {"writer_buffer": "", "status": 200, "redirect_status": 302, "location_header": "local only"},
            "limitations": ["not a servlet container", "captures local status/content/headers/cookies only"],
        },
        "servlet_session": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "servlet_session",
            "family": "servlet",
            "version": "deterministic-servlet-session/v1",
            "provided_helpers": ["mockSession()"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {"attribute_user": "alice", "session_id": "eviclone-session"},
            "limitations": ["no expiry, principal, distributed state, or servlet container lifecycle"],
        },
        "servlet_cookie": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "servlet_cookie",
            "family": "servlet",
            "version": "deterministic-servlet-cookie/v1",
            "provided_helpers": ['new Cookie("user", "alice")'],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {"cookie_user": "alice"},
            "limitations": ["plain local cookie object only"],
        },
        "jdbc_connection": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "jdbc_connection",
            "family": "jdbc",
            "version": "deterministic-jdbc-connection/v1",
            "provided_helpers": ["mockConnection()", "mockResultSet()"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "row.name": "alice",
                "row.user": "alice",
                "row.id": 42,
                "row.count": 1,
                "update_count": 1,
            },
            "limitations": [
                "not a real database",
                "no SQL parsing, constraints, transactions, isolation, network, driver behavior, or persistence",
                "commit, rollback, close, and parameters are local observable state only",
            ],
        },
        "jdbc_data_source": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "jdbc_data_source",
            "family": "jdbc",
            "version": "deterministic-jdbc-data-source/v1",
            "provided_helpers": ["mockDataSource()"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "get_connection_returns": "mockConnection()",
                "row.name": "alice",
                "row.user": "alice",
                "row.id": 42,
                "row.count": 1,
                "update_count": 1,
            },
            "limitations": [
                "not a real database, connection pool, JNDI resource, or application server DataSource",
                "getConnection returns deterministic local Connection fixtures only",
                "no SQL parsing, constraints, transactions, isolation, network, driver behavior, or persistence",
            ],
        },
        "jdbc_jdk_proxy": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "jdbc_jdk_proxy",
            "family": "jdbc",
            "version": "deterministic-java-sql-dynamic-proxy/v1",
            "provided_helpers": [
                "mockSqlDataSource()",
                "mockSqlConnection()",
                "mockSqlPreparedStatement(sql)",
                "mockSqlStatement()",
                "mockSqlResultSet()",
            ],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {
                "row.name": "alice",
                "row.user": "alice",
                "row.id": 42,
                "row.count": 1,
                "update_count": 1,
            },
            "limitations": [
                "javax.sql/java.sql interfaces are dynamic proxies, not a real database, DataSource, or JDBC driver",
                "no SQL parsing, constraints, transactions, isolation, network, driver behavior, or persistence",
                "only common DataSource/Connection/Statement/PreparedStatement/ResultSet methods used by shared-input probes are modeled",
            ],
        },
        "jdbc_prepared_statement": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "jdbc_prepared_statement",
            "family": "jdbc",
            "version": "deterministic-jdbc-prepared-statement/v1",
            "provided_helpers": ['mockConnection().prepareStatement("select name from users where id=?")'],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {"result_set": "mockResultSet()", "update_count": 1},
            "limitations": ["no SQL parsing or database side effects", "records parameters locally"],
        },
        "jdbc_statement": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "jdbc_statement",
            "family": "jdbc",
            "version": "deterministic-jdbc-statement/v1",
            "provided_helpers": ["mockConnection().createStatement()"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {"result_set": "mockResultSet()", "update_count": 1},
            "limitations": ["no SQL parsing or database side effects"],
        },
        "jdbc_result_set": {
            "schema_version": FRAMEWORK_MOCK_CONTRACT_SCHEMA_VERSION,
            "mock_id": "jdbc_result_set",
            "family": "jdbc",
            "version": "deterministic-jdbc-result-set/v1",
            "provided_helpers": ["mockResultSet()"],
            "deterministic": True,
            "no_external_services": True,
            "fixtures": {"row.name": "alice", "row.user": "alice", "row.id": 42, "row.count": 1},
            "limitations": ["single deterministic in-memory row set"],
        },
    }
    return {mock_id: attach_framework_mock_contract_hash(contract) for mock_id, contract in catalog.items()}


def build_java_source(pair: ClonePair, mode: str) -> tuple[str, dict[str, Any]]:
    method_a = parse_method(pair.code_a)
    method_b = parse_method(pair.code_b)
    functional_block_pair_ir = build_functional_block_pair_ir(pair)
    executable_module_graph = build_executable_module_graph(functional_block_pair_ir)
    meta: dict[str, Any] = {
        "method_a": method_to_dict(method_a),
        "method_b": method_to_dict(method_b),
        "target_family": target_family(pair.functionality_name),
        "probe_supported": False,
        "probe_family": target_family(pair.functionality_name),
        "functional_block_pair_ir": functional_block_pair_ir,
        "executable_module_graph": executable_module_graph,
    }
    if not method_a or not method_b:
        return "", meta

    probe_family, probe = supported_probe(pair, method_a, method_b)
    local_enums = local_enum_context_types(method_a, method_b) if probe else []
    meta["probe_supported"] = bool(probe)
    meta["probe_family"] = probe_family
    if local_enums:
        meta["programmatic_context_completion"] = {
            "schema_version": "eviclone-programmatic-context-completion/v1",
            "status": "applied",
            "kind": "local_enum_fallback",
            "local_enums": local_enums,
            "constants": ["ALPHA", "BETA", "GAMMA"],
            "llm_used": False,
            "limitations": [
                "only fills missing local enum declarations for same-name enum-shaped method signatures",
                "does not model external enum methods, fields, annotations, or application-specific constants",
            ],
        }
    if probe:
        meta["probe_factory"] = (
            "generic_value_equivalence" if probe_family == "generic_value_equivalence" else "builtin_target_family"
        )
    else:
        meta["probe_factory"] = "none"
    meta["framework_mocks"] = (
        sorted(set(framework_mock_contracts(method_a, method_b) + source_context_mock_contracts(pair.code_a, pair.code_b)))
        if probe
        else []
    )
    meta["framework_mock_contracts"] = framework_mock_contract_certificates(meta["framework_mocks"])
    module_lowering_source = ""
    module_lowering_artifact: dict[str, Any] | None = None
    if mode == "execute" and probe_family == "generic_value_equivalence" and probe:
        lowered = build_module_composition_lowering(
            pair=pair,
            method_a=method_a,
            method_b=method_b,
            executable_module_graph=executable_module_graph,
        )
        if lowered:
            probe = str(lowered["probe_body"])
            module_lowering_source = str(lowered["helper_source"])
            module_lowering_artifact = lowered["artifact"] if isinstance(lowered.get("artifact"), dict) else None
    meta["probe_contract"] = (
        build_probe_contract(
            pair,
            method_a,
            method_b,
            probe_family=probe_family,
            probe_factory=meta["probe_factory"],
            probe_body=probe,
            mode=mode,
        )
        if probe
        else None
    )
    meta["module_probe_plan"] = build_module_probe_plan(executable_module_graph, meta["probe_contract"])
    meta["executable_composition_spec"] = build_executable_composition_spec(
        executable_module_graph,
        meta["module_probe_plan"],
    )
    if module_lowering_artifact:
        meta["module_composition_lowering"] = finalize_module_composition_lowering_artifact(
            module_lowering_artifact,
            executable_composition_spec=meta["executable_composition_spec"],
            module_probe_plan=meta["module_probe_plan"],
            probe_contract=meta["probe_contract"],
        )
    meta["probe_adequacy_certificate"] = build_probe_adequacy_certificate(meta["probe_contract"])
    setup_lines: list[str] = []
    if "system_context_fixture" in list(meta.get("framework_mocks") or []):
        setup_lines.append("installSystemContextFixture(work);")
    if "locale_time_fixture" in list(meta.get("framework_mocks") or []):
        setup_lines.append("installLocaleTimeFixture();")
    body_lines = setup_lines + [probe if mode == "execute" and probe else 'printStatus("compile_only");']
    main_body = "\n".join(body_lines)
    local_enum_source = local_enum_context_source(local_enums)

    source = f"""
import java.io.*;
import java.math.*;
import java.net.*;
import java.nio.channels.*;
import java.nio.charset.*;
import java.nio.file.*;
import java.security.*;
import java.time.*;
import java.util.*;
import java.util.zip.*;
import com.sun.net.httpserver.HttpServer;

public class EviProbe {{
{local_enum_source}
    public static class SnippetA {{
{indent(pair.code_a, 8)}
    }}

    public static class SnippetB {{
{indent(pair.code_b, 8)}
    }}

{module_lowering_source}

    public static class FileUtils {{
        public static void copyFile(File src, File dst) throws IOException {{
            Files.copy(src.toPath(), dst.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }}
    }}

    public static class IOUtils {{
        public static int copy(InputStream in, OutputStream out) throws IOException {{
            return copyLarge(in, out) > Integer.MAX_VALUE ? -1 : 0;
        }}
        public static long copyLarge(InputStream in, OutputStream out) throws IOException {{
            byte[] buf = new byte[8192];
            long total = 0;
            int n;
            while ((n = in.read(buf)) != -1) {{
                out.write(buf, 0, n);
                total += n;
            }}
            return total;
        }}
    }}

    private static final String EVICLONE_NETWORK_PAYLOAD = "eviclone-network-payload";

    public static ByteArrayInputStream mockInputStream(String text) {{
        return new ByteArrayInputStream(text.getBytes(StandardCharsets.UTF_8));
    }}

    public static ByteArrayOutputStream mockOutputStream() {{
        return new ByteArrayOutputStream();
    }}

    public static StringReader mockReader(String text) {{
        return new StringReader(text);
    }}

    public static StringWriter mockWriter() {{
        return new StringWriter();
    }}

    public static PrintWriter mockPrintWriter() {{
        return new ObservablePrintWriter();
    }}

    public static class ObservablePrintWriter extends PrintWriter {{
        private final StringWriter sink;

        public ObservablePrintWriter() {{
            this(new StringWriter());
        }}

        private ObservablePrintWriter(StringWriter sink) {{
            super(sink, true);
            this.sink = sink;
        }}

        public String snapshot() {{
            flush();
            return sink.toString();
        }}
    }}

    public static void installSystemContextFixture(Path work) throws IOException {{
        Path home = work.resolve("system-home");
        Path tmp = work.resolve("system-tmp");
        Files.createDirectories(home);
        Files.createDirectories(tmp);
        System.setProperty("eviclone.property", "eviclone-property-value");
        System.setProperty("app.env", "eviclone-test");
        System.setProperty("config.value", "eviclone-config-value");
        System.setProperty("user.name", "eviclone-user");
        System.setProperty("user.home", home.toString());
        System.setProperty("java.io.tmpdir", tmp.toString());
    }}

    public static void installLocaleTimeFixture() {{
        Locale.setDefault(Locale.US);
        TimeZone.setDefault(TimeZone.getTimeZone("UTC"));
        System.setProperty("user.language", "en");
        System.setProperty("user.country", "US");
        System.setProperty("user.timezone", "UTC");
    }}

    public static URL mockUrl() throws MalformedURLException {{
        return new URL(null, "http://eviclone.local/resource", new InMemoryUrlStreamHandler());
    }}

    public static URI mockUri(Path work) throws IOException {{
        Path path = work.resolve("eviclone-uri-resource.txt");
        Files.write(path, EVICLONE_NETWORK_PAYLOAD.getBytes(StandardCharsets.UTF_8));
        return path.toUri();
    }}

    public static URLConnection mockUrlConnection() throws IOException {{
        return mockUrl().openConnection();
    }}

    public static class InMemoryUrlStreamHandler extends URLStreamHandler {{
        protected URLConnection openConnection(URL url) {{
            return new InMemoryURLConnection(url);
        }}
    }}

    public static class InMemoryURLConnection extends URLConnection {{
        private boolean connected = false;

        public InMemoryURLConnection(URL url) {{
            super(url);
        }}

        public void connect() {{
            connected = true;
        }}

        public boolean connected() {{
            return connected;
        }}

        public InputStream getInputStream() throws IOException {{
            connect();
            return new ByteArrayInputStream(EVICLONE_NETWORK_PAYLOAD.getBytes(StandardCharsets.UTF_8));
        }}

        public Object getContent() throws IOException {{
            return EVICLONE_NETWORK_PAYLOAD;
        }}

        public int getContentLength() {{
            return EVICLONE_NETWORK_PAYLOAD.getBytes(StandardCharsets.UTF_8).length;
        }}

        public long getContentLengthLong() {{
            return EVICLONE_NETWORK_PAYLOAD.getBytes(StandardCharsets.UTF_8).length;
        }}

        public String getContentType() {{
            return "text/plain";
        }}

        public String getHeaderField(String name) {{
            if ("Content-Type".equalsIgnoreCase(name)) return getContentType();
            if ("Content-Length".equalsIgnoreCase(name)) return String.valueOf(getContentLength());
            return null;
        }}
    }}

    public interface ActionListener {{
        void actionPerformed(ActionEvent event);
    }}

    public static class ActionEvent {{
        public static final int ACTION_PERFORMED = 1001;
        private final Object source;
        private final int id;
        private final String command;
        private final long when;
        private final int modifiers;

        public ActionEvent(Object source, int id, String command) {{
            this(source, id, command, 0L, 0);
        }}

        public ActionEvent(Object source, int id, String command, long when, int modifiers) {{
            this.source = source;
            this.id = id;
            this.command = command;
            this.when = when;
            this.modifiers = modifiers;
        }}

        public Object getSource() {{
            return source;
        }}

        public int getID() {{
            return id;
        }}

        public String getActionCommand() {{
            return command;
        }}

        public long getWhen() {{
            return when;
        }}

        public int getModifiers() {{
            return modifiers;
        }}

        public String paramString() {{
            return "ACTION_PERFORMED,cmd=" + command;
        }}

        public String toString() {{
            return "ActionEvent[id=" + id + ",command=" + command + "]";
        }}
    }}

    public static class JButton {{
        private String text;
        private String actionCommand;
        private boolean enabled = true;
        private String name = "";
        private final List<ActionListener> listeners = new ArrayList<>();

        public JButton() {{
            this("");
        }}

        public JButton(String text) {{
            this.text = text;
            this.actionCommand = text;
        }}

        public String getText() {{
            return text;
        }}

        public void setText(String text) {{
            this.text = text;
        }}

        public String getActionCommand() {{
            return actionCommand;
        }}

        public void setActionCommand(String command) {{
            this.actionCommand = command;
        }}

        public void addActionListener(ActionListener listener) {{
            if (listener != null) listeners.add(listener);
        }}

        public ActionListener[] getActionListeners() {{
            return listeners.toArray(new ActionListener[0]);
        }}

        public void doClick() {{
            ActionEvent event = new ActionEvent(this, ActionEvent.ACTION_PERFORMED, actionCommand);
            for (ActionListener listener : listeners) {{
                listener.actionPerformed(event);
            }}
        }}

        public void setEnabled(boolean enabled) {{
            this.enabled = enabled;
        }}

        public boolean isEnabled() {{
            return enabled;
        }}

        public void setName(String name) {{
            this.name = name;
        }}

        public String getName() {{
            return name;
        }}

        public String toString() {{
            return "JButton[text=" + text + ",command=" + actionCommand + ",enabled=" + enabled + "]";
        }}
    }}

    public static class JMenuItem extends JButton {{
        public JMenuItem() {{
            super("");
        }}

        public JMenuItem(String text) {{
            super(text);
        }}

        public String toString() {{
            return "JMenuItem[text=" + getText() + ",command=" + getActionCommand() + ",enabled=" + isEnabled() + "]";
        }}
    }}

    public static class JTextField {{
        private String text;
        private boolean editable = true;
        private boolean enabled = true;

        public JTextField() {{
            this("");
        }}

        public JTextField(String text) {{
            this.text = text;
        }}

        public String getText() {{
            return text;
        }}

        public void setText(String text) {{
            this.text = text;
        }}

        public void setEditable(boolean editable) {{
            this.editable = editable;
        }}

        public boolean isEditable() {{
            return editable;
        }}

        public void setEnabled(boolean enabled) {{
            this.enabled = enabled;
        }}

        public boolean isEnabled() {{
            return enabled;
        }}

        public String toString() {{
            return "JTextField[text=" + text + ",editable=" + editable + ",enabled=" + enabled + "]";
        }}
    }}

    public static class JTextArea extends JTextField {{
        public JTextArea() {{
            super("");
        }}

        public JTextArea(String text) {{
            super(text);
        }}

        public String toString() {{
            return "JTextArea[text=" + getText() + "]";
        }}
    }}

    public static class JLabel {{
        private String text;

        public JLabel() {{
            this("");
        }}

        public JLabel(String text) {{
            this.text = text;
        }}

        public String getText() {{
            return text;
        }}

        public void setText(String text) {{
            this.text = text;
        }}

        public String toString() {{
            return "JLabel[text=" + text + "]";
        }}
    }}

    public static class JPanel {{
        private final List<Object> children = new ArrayList<>();

        public void add(Object component) {{
            children.add(component);
        }}

        public int getComponentCount() {{
            return children.size();
        }}

        public Object getComponent(int index) {{
            return children.get(index);
        }}

        public String toString() {{
            return "JPanel[count=" + children.size() + "]";
        }}
    }}

    public static class JFrame {{
        private String title;
        private boolean visible = false;
        private final JPanel contentPane = new JPanel();

        public JFrame() {{
            this("");
        }}

        public JFrame(String title) {{
            this.title = title;
        }}

        public void setTitle(String title) {{
            this.title = title;
        }}

        public String getTitle() {{
            return title;
        }}

        public void setVisible(boolean visible) {{
            this.visible = visible;
        }}

        public boolean isVisible() {{
            return visible;
        }}

        public JPanel getContentPane() {{
            return contentPane;
        }}

        public void add(Object component) {{
            contentPane.add(component);
        }}

        public String toString() {{
            return "JFrame[title=" + title + ",visible=" + visible + ",components=" + contentPane.getComponentCount() + "]";
        }}
    }}

    public static class JPopupMenu {{
        private final List<Object> items = new ArrayList<>();

        public JMenuItem add(String text) {{
            JMenuItem item = new JMenuItem(text);
            items.add(item);
            return item;
        }}

        public JMenuItem add(JMenuItem item) {{
            items.add(item);
            return item;
        }}

        public int getComponentCount() {{
            return items.size();
        }}

        public Object getComponent(int index) {{
            return items.get(index);
        }}

        public String toString() {{
            return "JPopupMenu[count=" + items.size() + "]";
        }}
    }}

    public static ActionEvent mockActionEvent() {{
        return new ActionEvent(new JMenuItem("alpha-command"), ActionEvent.ACTION_PERFORMED, "alpha-command");
    }}

    public static ActionListener mockActionListener() {{
        return new ActionListener() {{
            public void actionPerformed(ActionEvent event) {{
            }}
        }};
    }}

    public static class Cookie {{
        private final String name;
        private String value;

        public Cookie(String name, String value) {{
            this.name = name;
            this.value = value;
        }}

        public String getName() {{
            return name;
        }}

        public String getValue() {{
            return value;
        }}

        public void setValue(String value) {{
            this.value = value;
        }}

        public String toString() {{
            return "Cookie[" + name + "=" + value + "]";
        }}
    }}

    public static class HttpSession {{
        private final Map<String, Object> attributes = new LinkedHashMap<>();
        private final String id = "eviclone-session";

        public Object getAttribute(String name) {{
            return attributes.get(name);
        }}

        public void setAttribute(String name, Object value) {{
            attributes.put(name, value);
        }}

        public void removeAttribute(String name) {{
            attributes.remove(name);
        }}

        public Enumeration<String> getAttributeNames() {{
            return Collections.enumeration(attributes.keySet());
        }}

        public String getId() {{
            return id;
        }}
    }}

    public static class HttpServletRequest {{
        private final Map<String, String[]> parameters = new LinkedHashMap<>();
        private final Map<String, Object> attributes = new LinkedHashMap<>();
        private final Map<String, String> headers = new LinkedHashMap<>();
        private final HttpSession session = new HttpSession();
        private Cookie[] cookies = new Cookie[0];
        private String method = "GET";
        private String contextPath = "/app";
        private String servletPath = "/eviclone";
        private String requestURI = "/app/eviclone";
        private String queryString = "user=alice&id=42&q=alpha";

        public String getParameter(String name) {{
            String[] values = parameters.get(name);
            return values == null || values.length == 0 ? null : values[0];
        }}

        public String[] getParameterValues(String name) {{
            String[] values = parameters.get(name);
            return values == null ? null : values.clone();
        }}

        public Map<String, String[]> getParameterMap() {{
            return parameters;
        }}

        public void setParameter(String name, String value) {{
            parameters.put(name, new String[]{{value}});
        }}

        public Object getAttribute(String name) {{
            return attributes.get(name);
        }}

        public void setAttribute(String name, Object value) {{
            attributes.put(name, value);
        }}

        public HttpSession getSession() {{
            return session;
        }}

        public HttpSession getSession(boolean create) {{
            return session;
        }}

        public String getHeader(String name) {{
            return headers.get(name);
        }}

        public void setHeader(String name, String value) {{
            headers.put(name, value);
        }}

        public Cookie[] getCookies() {{
            return cookies.clone();
        }}

        public void setCookies(Cookie[] cookies) {{
            this.cookies = cookies == null ? new Cookie[0] : cookies.clone();
        }}

        public String getMethod() {{
            return method;
        }}

        public void setMethod(String method) {{
            this.method = method == null ? "" : method;
        }}

        public String getRequestURI() {{
            return requestURI;
        }}

        public void setRequestURI(String requestURI) {{
            this.requestURI = requestURI == null ? "" : requestURI;
        }}

        public String getContextPath() {{
            return contextPath;
        }}

        public void setContextPath(String contextPath) {{
            this.contextPath = contextPath == null ? "" : contextPath;
        }}

        public String getServletPath() {{
            return servletPath;
        }}

        public void setServletPath(String servletPath) {{
            this.servletPath = servletPath == null ? "" : servletPath;
        }}

        public String getQueryString() {{
            return queryString;
        }}

        public void setQueryString(String queryString) {{
            this.queryString = queryString;
        }}

        private String formattedParameters() {{
            Map<String, String> rendered = new LinkedHashMap<>();
            for (Map.Entry<String, String[]> entry : parameters.entrySet()) {{
                rendered.put(entry.getKey(), Arrays.toString(entry.getValue()));
            }}
            return rendered.toString();
        }}

        public String toString() {{
            return "HttpServletRequest[method=" + method + ",uri=" + requestURI + ",query=" + queryString
                + ",contextPath=" + contextPath + ",servletPath=" + servletPath + ",parameters=" + formattedParameters()
                + ",headers=" + headers + ",cookies=" + Arrays.toString(cookies) + "]";
        }}
    }}

    public static class HttpServletResponse {{
        private int status = 200;
        private final Map<String, String> headers = new LinkedHashMap<>();
        private final List<Cookie> cookies = new ArrayList<>();
        private final StringWriter body = new StringWriter();
        private final PrintWriter writer = new PrintWriter(body);

        public void setStatus(int status) {{
            this.status = status;
        }}

        public int getStatus() {{
            return status;
        }}

        public void setHeader(String name, String value) {{
            headers.put(name, value);
        }}

        public void addHeader(String name, String value) {{
            headers.put(name, value);
        }}

        public String getHeader(String name) {{
            return headers.get(name);
        }}

        public void addCookie(Cookie cookie) {{
            if (cookie != null) {{
                cookies.add(cookie);
            }}
        }}

        public Cookie[] getCookies() {{
            return cookies.toArray(new Cookie[0]);
        }}

        public void sendRedirect(String location) {{
            status = 302;
            setHeader("Location", location);
        }}

        public PrintWriter getWriter() {{
            return writer;
        }}

        public String bodyText() {{
            writer.flush();
            return body.toString();
        }}

        public String toString() {{
            return "HttpServletResponse[status=" + status + ",headers=" + headers + ",cookies=" + cookies
                + ",body=" + bodyText() + "]";
        }}
    }}

    public static HttpServletRequest mockRequest() {{
        HttpServletRequest request = new HttpServletRequest();
        request.setParameter("user", "alice");
        request.setParameter("id", "42");
        request.setParameter("q", "alpha");
        request.setAttribute("role", "admin");
        request.setHeader("X-EviClone", "true");
        request.setCookies(new Cookie[]{{new Cookie("user", "alice"), new Cookie("id", "42")}});
        request.getSession().setAttribute("user", "alice");
        request.getSession().setAttribute("id", "42");
        return request;
    }}

    public static HttpSession mockSession() {{
        HttpSession session = new HttpSession();
        session.setAttribute("user", "alice");
        session.setAttribute("id", "42");
        return session;
    }}

    public static class SQLException extends Exception {{
        public SQLException() {{
            super();
        }}

        public SQLException(String message) {{
            super(message);
        }}
    }}

    public static class ResultSet {{
        private final List<Map<String, Object>> rows;
        private int index = -1;
        private boolean lastWasNull = false;

        public ResultSet(List<Map<String, Object>> rows) {{
            this.rows = rows == null ? Collections.emptyList() : rows;
        }}

        public boolean next() throws SQLException {{
            if (index + 1 < rows.size()) {{
                index += 1;
                return true;
            }}
            return false;
        }}

        public String getString(String column) throws SQLException {{
            Object value = getObject(column);
            return value == null ? null : String.valueOf(value);
        }}

        public String getString(int column) throws SQLException {{
            Object value = getObject(column);
            return value == null ? null : String.valueOf(value);
        }}

        public int getInt(String column) throws SQLException {{
            Object value = getObject(column);
            if (value instanceof Number) return ((Number) value).intValue();
            return value == null ? 0 : Integer.parseInt(String.valueOf(value));
        }}

        public int getInt(int column) throws SQLException {{
            Object value = getObject(column);
            if (value instanceof Number) return ((Number) value).intValue();
            return value == null ? 0 : Integer.parseInt(String.valueOf(value));
        }}

        public long getLong(String column) throws SQLException {{
            Object value = getObject(column);
            if (value instanceof Number) return ((Number) value).longValue();
            return value == null ? 0L : Long.parseLong(String.valueOf(value));
        }}

        public boolean getBoolean(String column) throws SQLException {{
            Object value = getObject(column);
            if (value instanceof Boolean) return ((Boolean) value).booleanValue();
            return value != null && Boolean.parseBoolean(String.valueOf(value));
        }}

        public Object getObject(String column) throws SQLException {{
            Map<String, Object> row = currentRow();
            Object value = row.get(column);
            lastWasNull = value == null;
            return value;
        }}

        public Object getObject(int column) throws SQLException {{
            Map<String, Object> row = currentRow();
            if (column < 1 || column > row.size()) {{
                throw new SQLException("column index out of range: " + column);
            }}
            Object value = new ArrayList<Object>(row.values()).get(column - 1);
            lastWasNull = value == null;
            return value;
        }}

        public boolean wasNull() {{
            return lastWasNull;
        }}

        public void close() {{
        }}

        private Map<String, Object> currentRow() throws SQLException {{
            if (index < 0 && !rows.isEmpty()) {{
                index = 0;
            }}
            if (index < 0 || index >= rows.size()) {{
                throw new SQLException("cursor is not positioned on a row");
            }}
            return rows.get(index);
        }}
    }}

    public static class Statement {{
        public static final int RETURN_GENERATED_KEYS = 1;
        protected int updateCount = 1;
        protected ResultSet resultSet = mockResultSet();

        public ResultSet executeQuery(String sql) throws SQLException {{
            resultSet = mockResultSet();
            return resultSet;
        }}

        public int executeUpdate(String sql) throws SQLException {{
            updateCount = 1;
            return updateCount;
        }}

        public boolean execute(String sql) throws SQLException {{
            resultSet = mockResultSet();
            updateCount = 1;
            return true;
        }}

        public ResultSet getResultSet() {{
            return resultSet;
        }}

        public int getUpdateCount() {{
            return updateCount;
        }}

        public void close() {{
        }}
    }}

    public static class PreparedStatement extends Statement {{
        private final String sql;
        private final List<Object> parameters = new ArrayList<>();

        public PreparedStatement(String sql) {{
            this.sql = sql;
        }}

        public void setString(int parameterIndex, String value) {{
            setObject(parameterIndex, value);
        }}

        public void setInt(int parameterIndex, int value) {{
            setObject(parameterIndex, Integer.valueOf(value));
        }}

        public void setLong(int parameterIndex, long value) {{
            setObject(parameterIndex, Long.valueOf(value));
        }}

        public void setBoolean(int parameterIndex, boolean value) {{
            setObject(parameterIndex, Boolean.valueOf(value));
        }}

        public void setDouble(int parameterIndex, double value) {{
            setObject(parameterIndex, Double.valueOf(value));
        }}

        public void setObject(int parameterIndex, Object value) {{
            while (parameters.size() < parameterIndex) {{
                parameters.add(null);
            }}
            parameters.set(parameterIndex - 1, value);
        }}

        public void clearParameters() {{
            parameters.clear();
        }}

        public ResultSet executeQuery() throws SQLException {{
            resultSet = mockResultSet();
            return resultSet;
        }}

        public int executeUpdate() throws SQLException {{
            updateCount = 1;
            return updateCount;
        }}

        public boolean execute() throws SQLException {{
            resultSet = mockResultSet();
            updateCount = 1;
            return true;
        }}

        public String sql() {{
            return sql;
        }}

        public List<Object> parameters() {{
            return parameters;
        }}
    }}

    public static class Connection {{
        private boolean autoCommit = true;
        private boolean closed = false;
        private boolean committed = false;
        private boolean rolledBack = false;

        public PreparedStatement prepareStatement(String sql) throws SQLException {{
            return new PreparedStatement(sql);
        }}

        public PreparedStatement prepareStatement(String sql, int autoGeneratedKeys) throws SQLException {{
            return new PreparedStatement(sql);
        }}

        public Statement createStatement() throws SQLException {{
            return new Statement();
        }}

        public void setAutoCommit(boolean autoCommit) throws SQLException {{
            this.autoCommit = autoCommit;
        }}

        public boolean getAutoCommit() throws SQLException {{
            return autoCommit;
        }}

        public void commit() throws SQLException {{
            committed = true;
        }}

        public void rollback() throws SQLException {{
            rolledBack = true;
        }}

        public void close() throws SQLException {{
            closed = true;
        }}

        public boolean isClosed() throws SQLException {{
            return closed;
        }}

        public boolean committed() {{
            return committed;
        }}

        public boolean rolledBack() {{
            return rolledBack;
        }}

        public String toString() {{
            return "Connection[autoCommit=" + autoCommit + ",closed=" + closed
                + ",committed=" + committed + ",rolledBack=" + rolledBack + "]";
        }}
    }}

    public static class DataSource {{
        private int connectionCount = 0;

        public Connection getConnection() throws SQLException {{
            connectionCount++;
            return mockConnection();
        }}

        public Connection getConnection(String username, String password) throws SQLException {{
            connectionCount++;
            return mockConnection();
        }}

        public int connectionCount() {{
            return connectionCount;
        }}

        public String toString() {{
            return "DataSource[connectionCount=" + connectionCount + "]";
        }}
    }}

    public static Connection mockConnection() {{
        return new Connection();
    }}

    public static DataSource mockDataSource() {{
        return new DataSource();
    }}

    public static ResultSet mockResultSet() {{
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("name", "alice");
        row.put("user", "alice");
        row.put("id", Integer.valueOf(42));
        row.put("count", Integer.valueOf(1));
        row.put("ok", Boolean.TRUE);
        return new ResultSet(Arrays.asList(row));
    }}

    public static LinkedHashMap<String, String> mockStringMap() {{
        LinkedHashMap<String, String> values = new LinkedHashMap<>();
        values.put("name", "alice");
        values.put("user", "alice");
        values.put("city", "paris");
        return values;
    }}

    public static HashMap<String, String> mockStringHashMap() {{
        return new HashMap<String, String>(mockStringMap());
    }}

    public static Properties mockProperties() {{
        Properties properties = new Properties();
        properties.setProperty("name", "alice");
        properties.setProperty("user", "alice");
        properties.setProperty("city", "paris");
        return properties;
    }}

    public static Calendar mockCalendar() {{
        GregorianCalendar calendar = new GregorianCalendar(TimeZone.getTimeZone("UTC"), Locale.US);
        calendar.clear();
        calendar.set(2020, Calendar.JANUARY, 2, 3, 4, 5);
        calendar.set(Calendar.MILLISECOND, 0);
        return calendar;
    }}

    public static javax.sql.DataSource mockSqlDataSource() {{
        return (javax.sql.DataSource) java.lang.reflect.Proxy.newProxyInstance(
            EviProbe.class.getClassLoader(),
            new Class<?>[]{{javax.sql.DataSource.class}},
            new SqlProxyHandler("data_source", "")
        );
    }}

    public static java.sql.Connection mockSqlConnection() {{
        return (java.sql.Connection) java.lang.reflect.Proxy.newProxyInstance(
            EviProbe.class.getClassLoader(),
            new Class<?>[]{{java.sql.Connection.class}},
            new SqlProxyHandler("connection", "")
        );
    }}

    public static java.sql.Statement mockSqlStatement() {{
        return (java.sql.Statement) java.lang.reflect.Proxy.newProxyInstance(
            EviProbe.class.getClassLoader(),
            new Class<?>[]{{java.sql.Statement.class}},
            new SqlProxyHandler("statement", "")
        );
    }}

    public static java.sql.PreparedStatement mockSqlPreparedStatement(String sql) {{
        return (java.sql.PreparedStatement) java.lang.reflect.Proxy.newProxyInstance(
            EviProbe.class.getClassLoader(),
            new Class<?>[]{{java.sql.PreparedStatement.class}},
            new SqlProxyHandler("prepared_statement", sql)
        );
    }}

    public static java.sql.ResultSet mockSqlResultSet() {{
        return (java.sql.ResultSet) java.lang.reflect.Proxy.newProxyInstance(
            EviProbe.class.getClassLoader(),
            new Class<?>[]{{java.sql.ResultSet.class}},
            new SqlProxyHandler("result_set", "")
        );
    }}

    public static class SqlProxyHandler implements java.lang.reflect.InvocationHandler {{
        private final String kind;
        private final String sql;
        private final List<Object> parameters = new ArrayList<>();
        private int cursor = -1;
        private boolean lastWasNull = false;
        private boolean closed = false;
        private boolean autoCommit = true;
        private int connectionCount = 0;
        private int loginTimeout = 0;
        private PrintWriter logWriter = null;

        public SqlProxyHandler(String kind, String sql) {{
            this.kind = kind;
            this.sql = sql == null ? "" : sql;
        }}

        public Object invoke(Object proxy, java.lang.reflect.Method method, Object[] args) throws Throwable {{
            String name = method.getName();
            if ("toString".equals(name)) {{
                if ("data_source".equals(kind)) {{
                    return "SqlProxy[data_source:connectionCount=" + connectionCount
                        + ",loginTimeout=" + loginTimeout + "]";
                }}
                return "SqlProxy[" + kind + ":" + sql + "]";
            }}
            if ("hashCode".equals(name)) {{
                return Integer.valueOf(System.identityHashCode(proxy));
            }}
            if ("equals".equals(name)) {{
                return Boolean.valueOf(args != null && args.length == 1 && proxy == args[0]);
            }}
            if ("unwrap".equals(name) && args != null && args.length == 1 && args[0] instanceof Class) {{
                Class<?> iface = (Class<?>) args[0];
                if (iface.isInstance(proxy)) return proxy;
                throw new java.sql.SQLException("not a wrapper for " + iface.getName());
            }}
            if ("isWrapperFor".equals(name) && args != null && args.length == 1 && args[0] instanceof Class) {{
                return Boolean.valueOf(((Class<?>) args[0]).isInstance(proxy));
            }}
            if ("data_source".equals(kind)) {{
                if ("getConnection".equals(name)) {{
                    connectionCount++;
                    return mockSqlConnection();
                }}
                if ("getLoginTimeout".equals(name)) return Integer.valueOf(loginTimeout);
                if ("setLoginTimeout".equals(name)) {{
                    loginTimeout = args != null && args.length > 0 && args[0] instanceof Integer
                        ? ((Integer) args[0]).intValue()
                        : 0;
                    return null;
                }}
                if ("getLogWriter".equals(name)) return logWriter;
                if ("setLogWriter".equals(name)) {{
                    logWriter = args != null && args.length > 0 && args[0] instanceof PrintWriter ? (PrintWriter) args[0] : null;
                    return null;
                }}
                if ("getParentLogger".equals(name)) return java.util.logging.Logger.getGlobal();
            }}
            if ("connection".equals(kind)) {{
                if ("prepareStatement".equals(name)) {{
                    return mockSqlPreparedStatement(args != null && args.length > 0 ? String.valueOf(args[0]) : "");
                }}
                if ("createStatement".equals(name)) return mockSqlStatement();
                if ("setAutoCommit".equals(name)) {{
                    autoCommit = args != null && args.length > 0 && Boolean.TRUE.equals(args[0]);
                    return null;
                }}
                if ("getAutoCommit".equals(name)) return Boolean.valueOf(autoCommit);
                if ("commit".equals(name) || "rollback".equals(name)) return null;
                if ("close".equals(name)) {{
                    closed = true;
                    return null;
                }}
                if ("isClosed".equals(name)) return Boolean.valueOf(closed);
                if ("isValid".equals(name)) return Boolean.TRUE;
                if ("nativeSQL".equals(name)) return args != null && args.length > 0 ? args[0] : "";
            }}
            if ("statement".equals(kind) || "prepared_statement".equals(kind)) {{
                if ("executeQuery".equals(name)) return mockSqlResultSet();
                if ("executeUpdate".equals(name)) return Integer.valueOf(1);
                if ("execute".equals(name)) return Boolean.TRUE;
                if ("getResultSet".equals(name) || "getGeneratedKeys".equals(name)) return mockSqlResultSet();
                if ("getUpdateCount".equals(name)) return Integer.valueOf(1);
                if ("getConnection".equals(name)) return mockSqlConnection();
                if ("close".equals(name)) {{
                    closed = true;
                    return null;
                }}
                if ("isClosed".equals(name)) return Boolean.valueOf(closed);
                if ("clearParameters".equals(name)) {{
                    parameters.clear();
                    return null;
                }}
                if (name.startsWith("set") && args != null && args.length >= 2 && args[0] instanceof Integer) {{
                    int index = ((Integer) args[0]).intValue();
                    while (parameters.size() < index) parameters.add(null);
                    parameters.set(index - 1, args[1]);
                    return null;
                }}
            }}
            if ("result_set".equals(kind)) {{
                if ("next".equals(name)) {{
                    if (cursor < 0) {{
                        cursor = 0;
                        return Boolean.TRUE;
                    }}
                    return Boolean.FALSE;
                }}
                if ("beforeFirst".equals(name)) {{
                    cursor = -1;
                    return null;
                }}
                if ("getString".equals(name)) {{
                    Object value = sqlValue(args == null || args.length == 0 ? "name" : args[0]);
                    return value == null ? null : String.valueOf(value);
                }}
                if ("getInt".equals(name)) {{
                    Object value = sqlValue(args == null || args.length == 0 ? "id" : args[0]);
                    if (value instanceof Number) return Integer.valueOf(((Number) value).intValue());
                    return value == null ? Integer.valueOf(0) : Integer.valueOf(Integer.parseInt(String.valueOf(value)));
                }}
                if ("getLong".equals(name)) {{
                    Object value = sqlValue(args == null || args.length == 0 ? "id" : args[0]);
                    if (value instanceof Number) return Long.valueOf(((Number) value).longValue());
                    return value == null ? Long.valueOf(0L) : Long.valueOf(Long.parseLong(String.valueOf(value)));
                }}
                if ("getBoolean".equals(name)) {{
                    Object value = sqlValue(args == null || args.length == 0 ? "ok" : args[0]);
                    if (value instanceof Boolean) return value;
                    return Boolean.valueOf(value != null && Boolean.parseBoolean(String.valueOf(value)));
                }}
                if ("getObject".equals(name)) {{
                    return sqlValue(args == null || args.length == 0 ? "name" : args[0]);
                }}
                if ("findColumn".equals(name)) return Integer.valueOf(1);
                if ("wasNull".equals(name)) return Boolean.valueOf(lastWasNull);
                if ("close".equals(name)) {{
                    closed = true;
                    return null;
                }}
                if ("isClosed".equals(name)) return Boolean.valueOf(closed);
            }}
            return defaultSqlValue(method.getReturnType());
        }}

        private Object sqlValue(Object key) {{
            Map<String, Object> row = sqlRow();
            Object value;
            if (key instanceof Integer) {{
                int index = ((Integer) key).intValue();
                if (index < 1 || index > row.size()) value = null;
                else value = new ArrayList<Object>(row.values()).get(index - 1);
            }} else {{
                value = row.get(String.valueOf(key));
            }}
            lastWasNull = value == null;
            return value;
        }}

        private Map<String, Object> sqlRow() {{
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("name", "alice");
            row.put("user", "alice");
            row.put("id", Integer.valueOf(42));
            row.put("count", Integer.valueOf(1));
            row.put("ok", Boolean.TRUE);
            if (cursor < 0) cursor = 0;
            return row;
        }}
    }}

    public static Object defaultSqlValue(Class<?> type) {{
        if (type == Void.TYPE) return null;
        if (type == Boolean.TYPE) return Boolean.FALSE;
        if (type == Byte.TYPE) return Byte.valueOf((byte) 0);
        if (type == Short.TYPE) return Short.valueOf((short) 0);
        if (type == Integer.TYPE) return Integer.valueOf(0);
        if (type == Long.TYPE) return Long.valueOf(0L);
        if (type == Float.TYPE) return Float.valueOf(0.0f);
        if (type == Double.TYPE) return Double.valueOf(0.0d);
        if (type == Character.TYPE) return Character.valueOf((char) 0);
        return null;
    }}

    public interface ThrowingRunnable {{
        void run() throws Exception;
    }}

    public static Object runVoid(ThrowingRunnable r, Object fallback) throws Exception {{
        r.run();
        return fallback;
    }}

    public static void main(String[] args) throws Exception {{
        Path work = Paths.get(args.length > 0 ? args[0] : ".").toAbsolutePath();
        Files.createDirectories(work);
{indent(main_body, 8)}
    }}

    public static String normalizeValue(Object value) throws Exception {{
        if (value == null) return "null";
        if (value instanceof byte[]) return b64((byte[]) value);
        if (value instanceof int[]) return Arrays.toString((int[]) value);
        if (value instanceof long[]) return Arrays.toString((long[]) value);
        if (value instanceof double[]) return Arrays.toString((double[]) value);
        if (value instanceof boolean[]) return Arrays.toString((boolean[]) value);
        if (value instanceof Object[]) return Arrays.deepToString((Object[]) value);
        if (value instanceof StringBuilder) {{
            return "StringBuilder[" + value.toString() + "]";
        }}
        if (value instanceof StringBuffer) {{
            return "StringBuffer[" + value.toString() + "]";
        }}
        if (value instanceof Date) {{
            return "Date[" + ((Date) value).getTime() + "]";
        }}
        if (value instanceof Calendar) {{
            Calendar calendar = (Calendar) value;
            return "Calendar[time=" + calendar.getTimeInMillis() + ",zone=" + calendar.getTimeZone().getID() + "]";
        }}
        if (value instanceof Instant) return "Instant[" + value.toString() + "]";
        if (value instanceof LocalDate) return "LocalDate[" + value.toString() + "]";
        if (value instanceof LocalDateTime) return "LocalDateTime[" + value.toString() + "]";
        if (value instanceof BigDecimal) return "BigDecimal[" + ((BigDecimal) value).toPlainString() + "]";
        if (value instanceof BigInteger) return "BigInteger[" + value.toString() + "]";
        if (value instanceof Enum) {{
            Enum<?> enumValue = (Enum<?>) value;
            return "Enum[" + enumValue.getDeclaringClass().getSimpleName() + "." + enumValue.name() + "]";
        }}
        if (value instanceof Optional) {{
            Optional<?> optional = (Optional<?>) value;
            return optional.isPresent() ? "Optional[" + normalizeValue(optional.get()) + "]" : "Optional.empty";
        }}
        if (value instanceof OptionalInt) {{
            OptionalInt optional = (OptionalInt) value;
            return optional.isPresent() ? "OptionalInt[" + optional.getAsInt() + "]" : "OptionalInt.empty";
        }}
        if (value instanceof OptionalLong) {{
            OptionalLong optional = (OptionalLong) value;
            return optional.isPresent() ? "OptionalLong[" + optional.getAsLong() + "]" : "OptionalLong.empty";
        }}
        if (value instanceof OptionalDouble) {{
            OptionalDouble optional = (OptionalDouble) value;
            return optional.isPresent() ? "OptionalDouble[" + optional.getAsDouble() + "]" : "OptionalDouble.empty";
        }}
        if (value instanceof Map) {{
            Map<?, ?> map = (Map<?, ?>) value;
            List<String> entries = new ArrayList<>();
            for (Map.Entry<?, ?> entry : map.entrySet()) {{
                entries.add(String.valueOf(entry.getKey()) + "=" + String.valueOf(entry.getValue()));
            }}
            Collections.sort(entries);
            return value.getClass().getName() + entries.toString();
        }}
        if (value instanceof Iterable) {{
            List<String> items = new ArrayList<>();
            for (Object item : (Iterable<?>) value) {{
                items.add(normalizeValue(item));
            }}
            if (value instanceof Set) Collections.sort(items);
            return value.getClass().getName() + items.toString();
        }}
        if (value instanceof ByteArrayOutputStream) {{
            return "ByteArrayOutputStream[" + b64(((ByteArrayOutputStream) value).toByteArray()) + "]";
        }}
        if (value instanceof InputStream) {{
            try {{
                return "InputStream[remaining=" + b64(readRemaining((InputStream) value)) + "]";
            }} catch (IOException error) {{
                return "InputStream[unreadable=" + error.getClass().getSimpleName() + "]";
            }}
        }}
        if (value instanceof ObservablePrintWriter) {{
            return "Writer[text=" + ((ObservablePrintWriter) value).snapshot() + "]";
        }}
        if (value instanceof StringWriter) {{
            return "Writer[text=" + value.toString() + "]";
        }}
        if (value instanceof Reader) {{
            try {{
                return "Reader[remaining=" + readRemaining((Reader) value) + "]";
            }} catch (IOException error) {{
                return "Reader[unreadable=" + error.getClass().getSimpleName() + "]";
            }}
        }}
        if (value instanceof URL) return ((URL) value).toExternalForm();
        if (value instanceof URI) return ((URI) value).toString();
        if (value instanceof URLConnection) {{
            URLConnection connection = (URLConnection) value;
            return "URLConnection[url=" + connection.getURL().toExternalForm() + ",contentType="
                + connection.getContentType() + ",contentLength=" + connection.getContentLengthLong() + "]";
        }}
        if (value instanceof java.awt.event.ActionEvent) {{
            java.awt.event.ActionEvent event = (java.awt.event.ActionEvent) value;
            return "ActionEvent[id=" + event.getID() + ",command=" + event.getActionCommand() + "]";
        }}
        if (value instanceof javax.swing.AbstractButton) {{
            javax.swing.AbstractButton button = (javax.swing.AbstractButton) value;
            return button.getClass().getName() + "[text=" + button.getText() + ",command=" + button.getActionCommand()
                + ",enabled=" + button.isEnabled() + "]";
        }}
        if (value instanceof javax.swing.text.JTextComponent) {{
            javax.swing.text.JTextComponent text = (javax.swing.text.JTextComponent) value;
            return value.getClass().getName() + "[text=" + text.getText() + ",editable=" + text.isEditable()
                + ",enabled=" + text.isEnabled() + "]";
        }}
        if (value instanceof javax.swing.JLabel) {{
            javax.swing.JLabel label = (javax.swing.JLabel) value;
            return "javax.swing.JLabel[text=" + label.getText() + ",enabled=" + label.isEnabled() + "]";
        }}
        if (value instanceof javax.swing.JPopupMenu) {{
            javax.swing.JPopupMenu menu = (javax.swing.JPopupMenu) value;
            List<String> children = new ArrayList<>();
            for (int i = 0; i < menu.getComponentCount(); i++) {{
                children.add(normalizeValue(menu.getComponent(i)));
            }}
            return "javax.swing.JPopupMenu[count=" + menu.getComponentCount() + ",children=" + children + "]";
        }}
        if (value instanceof javax.swing.JPanel) {{
            javax.swing.JPanel panel = (javax.swing.JPanel) value;
            return "javax.swing.JPanel[count=" + panel.getComponentCount() + "]";
        }}
        if (value instanceof Path) return Files.exists((Path) value) ? b64(Files.readAllBytes((Path) value)) : value.toString();
        if (value instanceof File) {{
            File f = (File) value;
            return f.exists() ? b64(Files.readAllBytes(f.toPath())) : f.toString();
        }}
        return String.valueOf(value);
    }}

    public static String normalizeInvocation(Object result, Object... observed) throws Exception {{
        StringBuilder normalized = new StringBuilder();
        normalized.append("return=").append(normalizeValue(result));
        for (int i = 0; i < observed.length; i++) {{
            normalized.append("|arg").append(i).append("=").append(normalizeValue(observed[i]));
        }}
        return normalized.toString();
    }}

    public static byte[] readRemaining(InputStream in) throws IOException {{
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        IOUtils.copy(in, out);
        return out.toByteArray();
    }}

    public static String readRemaining(Reader reader) throws IOException {{
        StringBuilder out = new StringBuilder();
        char[] buf = new char[4096];
        int n;
        while ((n = reader.read(buf)) != -1) {{
            out.append(buf, 0, n);
        }}
        return out.toString();
    }}

    public static String b64(byte[] bytes) {{
        return Base64.getEncoder().encodeToString(bytes);
    }}

    public static void printResult(boolean same, String outA, String outB) {{
        System.out.println("EVICLONE_RESULT " + json("executed", same, outA, outB));
    }}

    public static void printResultWithCaseSummary(boolean same, String outA, String outB, String caseSummary) {{
        System.out.println("EVICLONE_RESULT " + jsonWithCaseSummary("executed", same, outA, outB, caseSummary));
    }}

    public static void printStatus(String status) {{
        System.out.println("EVICLONE_RESULT " + json(status, false, "", ""));
    }}

    public static String json(String status, boolean same, String outA, String outB) {{
        return "{{\\\"status\\\":\\\"" + esc(status) + "\\\",\\\"same\\\":" + same
            + ",\\\"out_a\\\":\\\"" + esc(outA) + "\\\",\\\"out_b\\\":\\\"" + esc(outB) + "\\\"}}";
    }}

    public static String jsonWithCaseSummary(String status, boolean same, String outA, String outB, String caseSummary) {{
        return "{{\\\"status\\\":\\\"" + esc(status) + "\\\",\\\"same\\\":" + same
            + ",\\\"out_a\\\":\\\"" + esc(outA) + "\\\",\\\"out_b\\\":\\\"" + esc(outB)
            + "\\\",\\\"case_summary\\\":\\\"" + esc(caseSummary) + "\\\"}}";
    }}

    public static String esc(String value) {{
        return value.replace("\\\\", "\\\\\\\\").replace("\\\"", "\\\\\\\"").replace("\\n", "\\\\n").replace("\\r", "\\\\r");
    }}
}}
"""
    return source, meta


def build_functional_block_pair_ir(pair: ClonePair) -> dict[str, Any]:
    from .functional_blocks import extract_pair_functional_block_ir

    return extract_pair_functional_block_ir(pair.code_a, pair.code_b)


def build_executable_module_graph(functional_block_pair_ir: dict[str, Any]) -> dict[str, Any]:
    from .executable_modules import build_executable_module_graph as build_graph

    return build_graph(functional_block_pair_ir)


def build_module_probe_plan(
    executable_module_graph: dict[str, Any],
    probe_contract: dict[str, Any] | None,
) -> dict[str, Any]:
    from .probe_planner import build_module_probe_plan as build_plan

    return build_plan(executable_module_graph, probe_contract)


def build_executable_composition_spec(
    executable_module_graph: dict[str, Any],
    module_probe_plan: dict[str, Any] | None,
) -> dict[str, Any]:
    from .executable_composition import build_executable_composition_spec as build_spec

    return build_spec(executable_module_graph, module_probe_plan)


def method_to_dict(method: JavaMethod | None) -> dict[str, Any] | None:
    if method is None:
        return None
    return {
        "name": method.name,
        "return_type": method.return_type,
        "params": [{"type": p.type_name, "name": p.name} for p in method.params],
        "is_static": method.is_static,
    }


def indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else line for line in text.strip().splitlines())


def evaluate_java_pair(
    pair: ClonePair,
    *,
    mode: str = "execute",
    keep_dir: Path | None = None,
    timeout_sec: int = 8,
    context_completion_client: Any | None = None,
    context_completion_retries: int = 1,
    context_source_dir: Path | None = None,
    local_execution_semaphore: Any | None = None,
) -> dict[str, Any]:
    source, meta = build_java_source(pair, mode)
    result: dict[str, Any] = {
        "engine": "java_synthetic_harness",
        "mode": mode,
        "available": bool(shutil.which("javac") and shutil.which("java")),
        "status": "not_started",
        "meta": meta,
        "compile": {},
        "execution": {},
        "llm_context_completion": None,
        "llm_probe_synthesis": None,
    }
    if not result["available"]:
        result["status"] = "toolchain_missing"
        return result
    if not source:
        result["status"] = "method_parse_failed"
        if context_completion_client is None:
            return result

    should_cleanup = False
    if keep_dir:
        keep_dir.mkdir(parents=True, exist_ok=True)
        work_root = keep_dir
    else:
        tmp_parent = Path(os.environ.get("EVICLONE_TMP_DIR", "")) if os.environ.get("EVICLONE_TMP_DIR") else Path("eviclone_runs") / "tmp"
        try:
            tmp_parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            tmp_parent = Path("tmp") / "eviclone_runs"
            tmp_parent.mkdir(parents=True, exist_ok=True)
        work_root = tmp_parent / f"eviclone_pair_{pair.pair_id}_{uuid.uuid4().hex[:8]}"
        try:
            work_root.mkdir(parents=True, exist_ok=False)
        except PermissionError:
            tmp_parent = Path("tmp") / "eviclone_runs"
            tmp_parent.mkdir(parents=True, exist_ok=True)
            work_root = tmp_parent / f"eviclone_pair_{pair.pair_id}_{uuid.uuid4().hex[:8]}"
            work_root.mkdir(parents=True, exist_ok=False)
        should_cleanup = True
    try:
        source_path = work_root / "EviProbe.java"
        probe_work = work_root / "work"
        classpath_resource_fixture: dict[str, Any] | None = None
        system_context_fixture: dict[str, Any] | None = None
        locale_time_fixture: dict[str, Any] | None = None

        def attach_execution_certificate() -> None:
            result["execution_certificate"] = build_java_execution_certificate(
                source=source,
                mode=mode,
                engine=str(result.get("engine") or ""),
                status=str(result.get("status") or ""),
                compile_info=result.get("compile") if isinstance(result.get("compile"), dict) else {},
                execution_info=result.get("execution") if isinstance(result.get("execution"), dict) else {},
                meta=result.get("meta") if isinstance(result.get("meta"), dict) else {},
                llm_context_completion=result.get("llm_context_completion")
                if isinstance(result.get("llm_context_completion"), dict)
                else None,
                llm_probe_synthesis=result.get("llm_probe_synthesis")
                if isinstance(result.get("llm_probe_synthesis"), dict)
                else None,
                compile_attempts=result.get("compile_attempts")
                if isinstance(result.get("compile_attempts"), list)
                else None,
                timeout_sec=timeout_sec,
                work_root=work_root,
                probe_work=probe_work,
                cleanup_requested=should_cleanup,
                classpath_resource_fixture=classpath_resource_fixture,
                system_context_fixture=system_context_fixture,
                locale_time_fixture=locale_time_fixture,
            )

        def run_local_process(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
            if local_execution_semaphore is None:
                return subprocess.run(
                    command,
                    cwd=str(work_root),
                    text=True,
                    capture_output=True,
                    timeout=timeout_sec,
                    env=env,
                )
            with local_execution_semaphore:
                return subprocess.run(
                    command,
                    cwd=str(work_root),
                    text=True,
                    capture_output=True,
                    timeout=timeout_sec,
                    env=env,
                )

        def compile_current(label: str) -> dict[str, Any]:
            source_path.write_text(source, encoding="utf-8", newline="\n")
            proc = run_local_process(["javac", "-encoding", "UTF-8", source_path.name])
            info = proc_info(proc)
            info["label"] = label
            return info

        def apply_llm_context(reason: str, compile_info: dict[str, Any]) -> bool:
            nonlocal source, meta
            if context_completion_client is None:
                return False
            repair_budget = max(1, int(context_completion_retries or 1))
            last_compile_info = compile_info
            last_completed_context: dict[str, Any] | None = None
            result.setdefault("llm_context_completion_attempts", [])
            for attempt_index in range(repair_budget):
                attempt_reason = reason if attempt_index == 0 else "llm_context_compile_failed"
                completion = complete_context_with_llm(
                    pair,
                    generated_source=source,
                    compile_info={
                        **last_compile_info,
                        "reason": attempt_reason,
                        "context_compile_repair_attempt": attempt_index,
                    },
                    meta=meta,
                    mode=mode,
                    client=context_completion_client,
                    retries=context_completion_retries if attempt_index == 0 else 1,
                )
                completion_record = {
                    k: v
                    for k, v in completion.items()
                    if k not in {"java_source", "diagnostic_java_source", "rejected_java_source"}
                }
                completion_record["compile_repair_attempt"] = attempt_index
                result["llm_context_completion_attempts"].append(completion_record)
                repaired_source = str(completion.get("java_source") or "")
                if not repaired_source:
                    diagnostic_source = str(
                        completion.get("diagnostic_java_source") or completion.get("rejected_java_source") or ""
                    )
                    if diagnostic_source and context_source_dir is not None:
                        completion_record["diagnostic_source_artifact"] = write_context_source_artifact(
                            diagnostic_source,
                            context_source_dir,
                            pair=pair,
                            context_payload=completion.get("payload")
                            if isinstance(completion.get("payload"), dict)
                            else {},
                            retained=False,
                            quarantined=True,
                            artifact_role="diagnostic_rejected_context_source",
                            rejection_reason=str(completion.get("error") or ""),
                        )
                    if last_completed_context is None:
                        result["llm_context_completion"] = completion_record
                    else:
                        last_completed_context["compile_repair_terminal_status"] = str(completion.get("status") or "")
                        last_completed_context["compile_repair_terminal_error"] = str(completion.get("error") or "")
                    return False
                source = repaired_source
                meta = dict(meta)
                meta["probe_family"] = "llm_context_completion"
                meta["probe_factory"] = "llm_context_completion"
                meta["probe_contract"] = build_llm_context_probe_contract(
                    completion,
                    mode=mode,
                    reason=attempt_reason,
                )
                meta["module_probe_plan"] = build_module_probe_plan(
                    meta.get("executable_module_graph") if isinstance(meta.get("executable_module_graph"), dict) else {},
                    meta["probe_contract"],
                )
                meta["executable_composition_spec"] = build_executable_composition_spec(
                    meta.get("executable_module_graph") if isinstance(meta.get("executable_module_graph"), dict) else {},
                    meta["module_probe_plan"],
                )
                meta["probe_adequacy_certificate"] = build_probe_adequacy_certificate(meta["probe_contract"])
                result["meta"] = meta
                if context_source_dir is not None:
                    completion_record["source_artifact"] = write_context_source_artifact(
                        source,
                        context_source_dir,
                        pair=pair,
                        context_payload=completion.get("payload") if isinstance(completion.get("payload"), dict) else {},
                    )
                result["llm_context_completion"] = completion_record
                last_completed_context = completion_record
                result["engine"] = "java_synthetic_harness+llm_context_completion"
                compile_label = "llm_context" if attempt_index == 0 else f"llm_context_repair_{attempt_index}"
                llm_compile_info = compile_current(compile_label)
                result.setdefault("compile_attempts", []).append(llm_compile_info)
                result["compile"] = llm_compile_info
                if llm_compile_info.get("returncode") == 0:
                    return True
                result["status"] = "llm_context_compile_failed"
                completion_record["compile_status"] = "failed"
                completion_record["compile_returncode"] = llm_compile_info.get("returncode")
                completion_record["compile_stderr_sha256"] = sha256_text(str(llm_compile_info.get("stderr") or ""))
                last_compile_info = llm_compile_info
            attach_execution_certificate()
            return False

        def apply_llm_probe_synthesis(reason: str, compile_info: dict[str, Any]) -> bool:
            nonlocal source, meta
            if context_completion_client is None:
                return False
            completion = synthesize_probe_with_llm(
                pair,
                generated_source=source,
                compile_info={**compile_info, "reason": reason},
                meta=meta,
                client=context_completion_client,
                retries=context_completion_retries,
            )
            result["llm_probe_synthesis"] = {k: v for k, v in completion.items() if k != "probe_body"}
            probe_body = str(completion.get("probe_body") or "")
            if not probe_body:
                return False
            source = replace_compile_only_main_body(source, probe_body)
            meta = dict(meta)
            meta["probe_supported"] = True
            meta["probe_family"] = "llm_probe_synthesis"
            meta["probe_factory"] = "llm_probe_synthesis"
            meta["probe_synthesis_reason"] = reason
            meta["probe_contract"] = build_llm_probe_contract(completion, reason=reason)
            meta["module_probe_plan"] = build_module_probe_plan(
                meta.get("executable_module_graph") if isinstance(meta.get("executable_module_graph"), dict) else {},
                meta["probe_contract"],
            )
            meta["executable_composition_spec"] = build_executable_composition_spec(
                meta.get("executable_module_graph") if isinstance(meta.get("executable_module_graph"), dict) else {},
                meta["module_probe_plan"],
            )
            meta["probe_adequacy_certificate"] = build_probe_adequacy_certificate(meta["probe_contract"])
            result["meta"] = meta
            if context_source_dir is not None:
                result["llm_probe_synthesis"]["source_artifact"] = write_context_source_artifact(
                    source,
                    context_source_dir,
                    pair=pair,
                    probe_payload=completion.get("payload") if isinstance(completion.get("payload"), dict) else {},
                    probe_body=probe_body,
                )
            result["engine"] = "java_synthetic_harness+llm_probe_synthesis"
            llm_probe_compile_info = compile_current("llm_probe_synthesis")
            result.setdefault("compile_attempts", []).append(llm_probe_compile_info)
            result["compile"] = llm_probe_compile_info
            if llm_probe_compile_info.get("returncode") != 0:
                result["status"] = "llm_probe_compile_failed"
                attach_execution_certificate()
                return False
            return True

        used_llm_context = False
        used_llm_probe = False
        if source:
            compile_info = compile_current("original")
            result["compile"] = compile_info
            result.setdefault("compile_attempts", []).append(compile_info)
            if compile_info.get("returncode") != 0:
                result["status"] = "compile_failed"
                used_llm_context = apply_llm_context("original_compile_failed", compile_info)
                if not used_llm_context:
                    attach_execution_certificate()
                    return result
        else:
            compile_info = {"returncode": None, "stdout": "", "stderr": "method_parse_failed", "label": "original"}
            result["compile"] = compile_info
            result.setdefault("compile_attempts", []).append(compile_info)
            used_llm_context = apply_llm_context("method_parse_failed", compile_info)
            if not used_llm_context:
                attach_execution_certificate()
                return result

        if mode != "execute":
            result["status"] = "llm_context_compile_success" if used_llm_context else "compile_success"
            attach_execution_certificate()
            return result
        if not meta.get("probe_supported") and not used_llm_context:
            used_llm_probe = apply_llm_probe_synthesis("compile_success_no_builtin_probe", result["compile"])
            if not used_llm_probe:
                used_llm_context = apply_llm_context("compile_success_no_builtin_probe", result["compile"])
            if not used_llm_probe and not used_llm_context:
                if result.get("status") == "llm_probe_compile_failed":
                    attach_execution_certificate()
                    return result
                if result.get("status") == "llm_context_compile_failed":
                    attach_execution_certificate()
                    return result
                result["status"] = "compile_success_no_probe"
                attach_execution_certificate()
                return result

        if "classpath_resource_fixture" in list(meta.get("framework_mocks") or []):
            classpath_resource_fixture = install_classpath_resource_fixture(work_root)
            result["classpath_resource_fixture"] = classpath_resource_fixture
        java_env: dict[str, str] | None = None
        if "system_context_fixture" in list(meta.get("framework_mocks") or []):
            system_context_fixture = install_system_context_fixture(probe_work)
            result["system_context_fixture"] = system_context_fixture
            java_env = system_context_process_env(system_context_fixture)
        if "locale_time_fixture" in list(meta.get("framework_mocks") or []):
            locale_time_fixture = install_locale_time_fixture()
            result["locale_time_fixture"] = locale_time_fixture

        run_proc = run_local_process(["java", "-cp", ".", "EviProbe", str(probe_work.resolve())], env=java_env)
        result["execution"] = proc_info(run_proc)
        parsed = parse_probe_output(run_proc.stdout)
        result["execution"]["parsed"] = parsed
        if run_proc.returncode == 0 and isinstance(parsed, dict):
            parsed_status = str(parsed.get("status") or "").strip().lower()
            if parsed_status == "executed":
                result["status"] = "executed"
            elif parsed_status in {"compile_only", "inconclusive", "not_recoverable"}:
                result["status"] = "llm_context_compile_success_no_probe" if used_llm_context else "compile_success_no_probe"
            else:
                result["status"] = "llm_context_execution_failed" if used_llm_context else "execution_failed"
        else:
            if used_llm_context:
                result["status"] = "llm_context_execution_failed"
            elif used_llm_probe:
                result["status"] = "llm_probe_execution_failed"
            else:
                result["status"] = "execution_failed"
        attach_execution_certificate()
        return result
    except subprocess.TimeoutExpired as exc:
        result["status"] = "timeout"
        result["execution"] = {"timeout": True, "cmd": exc.cmd}
        result["execution_certificate"] = build_java_execution_certificate(
            source=source,
            mode=mode,
            engine=str(result.get("engine") or ""),
            status="timeout",
            compile_info=result.get("compile") if isinstance(result.get("compile"), dict) else {},
            execution_info=result.get("execution") if isinstance(result.get("execution"), dict) else {},
            meta=result.get("meta") if isinstance(result.get("meta"), dict) else {},
            llm_context_completion=result.get("llm_context_completion")
            if isinstance(result.get("llm_context_completion"), dict)
            else None,
            llm_probe_synthesis=result.get("llm_probe_synthesis")
            if isinstance(result.get("llm_probe_synthesis"), dict)
            else None,
            compile_attempts=result.get("compile_attempts")
            if isinstance(result.get("compile_attempts"), list)
            else None,
            timeout_sec=timeout_sec,
            work_root=work_root,
            probe_work=probe_work,
            cleanup_requested=should_cleanup,
            classpath_resource_fixture=classpath_resource_fixture,
            system_context_fixture=system_context_fixture,
            locale_time_fixture=locale_time_fixture,
        )
        return result
    finally:
        if should_cleanup:
            shutil.rmtree(work_root, ignore_errors=True)


def proc_info(proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def build_java_execution_certificate(
    *,
    source: str,
    mode: str,
    engine: str,
    status: str,
    compile_info: dict[str, Any],
    execution_info: dict[str, Any],
    meta: dict[str, Any],
    timeout_sec: int | float,
    llm_context_completion: dict[str, Any] | None = None,
    llm_probe_synthesis: dict[str, Any] | None = None,
    compile_attempts: list[Any] | None = None,
    work_root: Path | str | None = None,
    probe_work: Path | str | None = None,
    cleanup_requested: bool | None = None,
    classpath_resource_fixture: dict[str, Any] | None = None,
    system_context_fixture: dict[str, Any] | None = None,
    locale_time_fixture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    parsed = execution_info.get("parsed") if isinstance(execution_info.get("parsed"), dict) else None
    execution_stdout = str(execution_info.get("stdout") or "")
    framework_mock_contracts = [
        item for item in meta.get("framework_mock_contracts") or [] if isinstance(item, dict)
    ]
    probe_contract = meta.get("probe_contract") if isinstance(meta.get("probe_contract"), dict) else {}
    probe_adequacy_certificate = build_probe_adequacy_certificate(probe_contract)
    module_probe_plan = meta.get("module_probe_plan") if isinstance(meta.get("module_probe_plan"), dict) else {}
    functional_block_pair_ir = (
        meta.get("functional_block_pair_ir") if isinstance(meta.get("functional_block_pair_ir"), dict) else {}
    )
    executable_module_graph = (
        meta.get("executable_module_graph") if isinstance(meta.get("executable_module_graph"), dict) else {}
    )
    executable_composition_spec = (
        meta.get("executable_composition_spec")
        if isinstance(meta.get("executable_composition_spec"), dict)
        else {}
    )
    module_composition_lowering = (
        meta.get("module_composition_lowering")
        if isinstance(meta.get("module_composition_lowering"), dict)
        else {}
    )
    certificate = {
        "schema_version": JAVA_EXECUTION_CERTIFICATE_SCHEMA_VERSION,
        "engine": engine,
        "mode": mode,
        "status": status,
        "timeout_sec": timeout_sec,
        "source_sha256": sha256_text(source),
        "source_chars": len(source or ""),
        "java_toolchain": build_java_toolchain_certificate(),
        "runtime_source_safety": build_runtime_source_safety_certificate(source),
        "dynamic_outcome": build_dynamic_outcome_certificate(
            status=status,
            mode=mode,
            engine=engine,
            compile_info=compile_info,
            execution_info=execution_info,
            meta=meta,
            llm_context_completion=llm_context_completion,
            llm_probe_synthesis=llm_probe_synthesis,
            compile_attempts=compile_attempts,
        ),
        "execution_sandbox": build_java_execution_sandbox_certificate(
            timeout_sec=timeout_sec,
            work_root=work_root,
            probe_work=probe_work,
            cleanup_requested=cleanup_requested,
            classpath_resource_fixture=classpath_resource_fixture,
            system_context_fixture=system_context_fixture,
            locale_time_fixture=locale_time_fixture,
        ),
        "compile": {
            "command": ["javac", "-encoding", "UTF-8", "EviProbe.java"],
            "returncode": compile_info.get("returncode"),
            "stdout_sha256": sha256_text(str(compile_info.get("stdout") or "")),
            "stderr_sha256": sha256_text(str(compile_info.get("stderr") or "")),
            "attempt_name": compile_info.get("label"),
        },
        "execution": {
            "command": ["java", "-cp", ".", "EviProbe", "$EVICLONE_WORK_DIR"],
            "returncode": execution_info.get("returncode"),
            "timeout": execution_info.get("timeout") is True,
            "stdout_sha256": sha256_text(execution_stdout),
            "stderr_sha256": sha256_text(str(execution_info.get("stderr") or "")),
            "result_line_count": count_probe_result_lines(execution_stdout),
            "parsed_sha256": canonical_sha256(parsed) if parsed is not None else None,
            "parsed_same": parsed.get("same") if isinstance(parsed, dict) else None,
            "parsed_status": parsed.get("status") if isinstance(parsed, dict) else None,
        },
        "execution_result_oracle": build_execution_result_oracle_certificate(
            stdout=execution_stdout,
            parsed=parsed,
            meta=meta,
        ),
        "probe": {
            "probe_factory": meta.get("probe_factory"),
            "probe_family": meta.get("probe_family"),
            "probe_contract_present": bool(probe_contract),
            "probe_contract_sha256": canonical_sha256(probe_contract) if probe_contract else None,
            "probe_contract_self_hash": probe_contract.get(PROBE_CONTRACT_HASH_FIELD) if probe_contract else None,
            "probe_adequacy_certificate": probe_adequacy_certificate,
            "probe_adequacy_sha256": (
                probe_adequacy_certificate.get(PROBE_ADEQUACY_HASH_FIELD)
                if isinstance(probe_adequacy_certificate, dict)
                else None
            ),
            "probe_adequacy_status": (
                probe_adequacy_certificate.get("status") if isinstance(probe_adequacy_certificate, dict) else None
            ),
            "probe_adequacy_tier": (
                probe_adequacy_certificate.get("adequacy_tier")
                if isinstance(probe_adequacy_certificate, dict)
                else None
            ),
            "probe_case_count": (
                probe_adequacy_certificate.get("case_count") if isinstance(probe_adequacy_certificate, dict) else None
            ),
            "probe_observation_kind": (
                probe_adequacy_certificate.get("observation_kind")
                if isinstance(probe_adequacy_certificate, dict)
                else None
            ),
            "framework_mocks": list(meta.get("framework_mocks") or []),
            "framework_mock_contract_sha256s": framework_mock_contract_canonical_hashes(framework_mock_contracts),
            "framework_mock_contract_self_hashes": [
                item.get(FRAMEWORK_MOCK_CONTRACT_HASH_FIELD) for item in framework_mock_contracts
            ],
            "module_probe_plan_present": bool(module_probe_plan),
            "module_probe_plan_sha256": canonical_sha256(module_probe_plan) if module_probe_plan else None,
            "module_probe_plan_self_hash": module_probe_plan.get("plan_sha256") if module_probe_plan else None,
            "module_probe_plan_risk": (
                module_probe_plan.get("risk", {}).get("level")
                if isinstance(module_probe_plan.get("risk"), dict)
                else None
            ),
            "module_probe_plan_uncovered_obligations": (
                list(module_probe_plan.get("coverage", {}).get("uncovered_obligations") or [])
                if isinstance(module_probe_plan.get("coverage"), dict)
                else []
            ),
        },
        "functional_blocks": build_functional_block_execution_binding(functional_block_pair_ir, executable_module_graph),
        "executable_composition": build_executable_composition_execution_binding(
            executable_composition_spec,
            executable_module_graph,
            module_probe_plan,
            module_composition_lowering,
        ),
        "runtime_fixtures": {
            "classpath_resource_fixture": classpath_resource_fixture,
            "system_context_fixture": system_context_fixture,
            "locale_time_fixture": locale_time_fixture,
        },
    }
    certificate["certificate_sha256"] = canonical_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def build_executable_composition_execution_binding(
    executable_composition_spec: dict[str, Any],
    executable_module_graph: dict[str, Any] | None = None,
    module_probe_plan: dict[str, Any] | None = None,
    module_composition_lowering: dict[str, Any] | None = None,
) -> dict[str, Any]:
    executable_module_graph = executable_module_graph or {}
    module_probe_plan = module_probe_plan or {}
    module_composition_lowering = module_composition_lowering or {}
    if not executable_composition_spec:
        return {
            "composition_present": False,
            "composition_sha256": None,
            "composition_self_hash": None,
            "module_graph_sha256": None,
            "module_graph_self_hash": None,
            "module_probe_plan_sha256": None,
            "module_probe_plan_self_hash": None,
            "module_composition_lowering_present": False,
            "module_composition_lowering_sha256": None,
            "module_composition_lowering_self_hash": None,
            "llm_clone_decision_allowed": None,
            "raw_source_patch_allowed": None,
        }
    llm_contract = (
        executable_composition_spec.get("llm_contract")
        if isinstance(executable_composition_spec.get("llm_contract"), dict)
        else {}
    )
    lowering_contract = (
        executable_composition_spec.get("lowering_contract")
        if isinstance(executable_composition_spec.get("lowering_contract"), dict)
        else {}
    )
    side_compositions = (
        executable_composition_spec.get("side_compositions")
        if isinstance(executable_composition_spec.get("side_compositions"), dict)
        else {}
    )
    return {
        "composition_present": True,
        "composition_schema_version": executable_composition_spec.get("schema_version"),
        "composition_sha256": canonical_sha256(executable_composition_spec),
        "composition_self_hash": executable_composition_spec.get("composition_sha256"),
        "module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "module_graph_self_hash": executable_module_graph.get("module_graph_sha256") if executable_module_graph else None,
        "module_probe_plan_sha256": canonical_sha256(module_probe_plan) if module_probe_plan else None,
        "module_probe_plan_self_hash": module_probe_plan.get("plan_sha256") if module_probe_plan else None,
        "module_composition_lowering_present": bool(module_composition_lowering),
        "module_composition_lowering_sha256": (
            canonical_sha256(module_composition_lowering) if module_composition_lowering else None
        ),
        "module_composition_lowering_self_hash": (
            module_composition_lowering.get(MODULE_COMPOSITION_LOWERING_HASH_FIELD)
            if module_composition_lowering
            else None
        ),
        "module_composition_lowering_backend": (
            module_composition_lowering.get("backend") if module_composition_lowering else None
        ),
        "module_composition_lowering_calls_original_snippets": (
            module_composition_lowering.get("probe_invokes_original_snippet_methods")
            if module_composition_lowering
            else None
        ),
        "composition_model": executable_composition_spec.get("composition_model"),
        "plan_a": list((executable_composition_spec.get("execution_plan_binding") or {}).get("a") or [])
        if isinstance(executable_composition_spec.get("execution_plan_binding"), dict)
        else [],
        "plan_b": list((executable_composition_spec.get("execution_plan_binding") or {}).get("b") or [])
        if isinstance(executable_composition_spec.get("execution_plan_binding"), dict)
        else [],
        "step_count_a": len((side_compositions.get("a") or {}).get("steps") or [])
        if isinstance(side_compositions.get("a"), dict)
        else 0,
        "step_count_b": len((side_compositions.get("b") or {}).get("steps") or [])
        if isinstance(side_compositions.get("b"), dict)
        else 0,
        "llm_clone_decision_allowed": llm_contract.get("clone_decision_allowed"),
        "raw_source_patch_allowed": lowering_contract.get("raw_source_patch_allowed"),
        "llm_module_rewrite_allowed": lowering_contract.get("llm_module_rewrite_allowed"),
    }


def build_functional_block_execution_binding(
    functional_block_pair_ir: dict[str, Any],
    executable_module_graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    executable_module_graph = executable_module_graph or {}
    if not functional_block_pair_ir:
        return {
            "pair_ir_present": False,
            "pair_ir_sha256": None,
            "pair_ir_self_hash": None,
            "module_graph_present": False,
            "module_graph_sha256": None,
            "module_graph_self_hash": None,
            "module_signature_a": [],
            "module_signature_b": [],
            "llm_clone_decision_allowed": None,
            "raw_source_patch_allowed": None,
        }
    llm_contract = functional_block_pair_ir.get("llm_contract") if isinstance(functional_block_pair_ir.get("llm_contract"), dict) else {}
    ir_a = functional_block_pair_ir.get("a") if isinstance(functional_block_pair_ir.get("a"), dict) else {}
    ir_b = functional_block_pair_ir.get("b") if isinstance(functional_block_pair_ir.get("b"), dict) else {}
    return {
        "pair_ir_present": True,
        "pair_ir_schema_version": functional_block_pair_ir.get("schema_version"),
        "pair_ir_sha256": canonical_sha256(functional_block_pair_ir),
        "pair_ir_self_hash": functional_block_pair_ir.get("pair_ir_sha256"),
        "module_signature_a": list(functional_block_pair_ir.get("module_signature_a") or []),
        "module_signature_b": list(functional_block_pair_ir.get("module_signature_b") or []),
        "module_signature_equal": functional_block_pair_ir.get("module_signature_equal"),
        "block_count_a": len(ir_a.get("blocks") or []),
        "block_count_b": len(ir_b.get("blocks") or []),
        "edge_count_a": len(ir_a.get("edges") or []),
        "edge_count_b": len(ir_b.get("edges") or []),
        "module_graph_present": bool(executable_module_graph),
        "module_graph_schema_version": executable_module_graph.get("schema_version") if executable_module_graph else None,
        "module_graph_sha256": canonical_sha256(executable_module_graph) if executable_module_graph else None,
        "module_graph_self_hash": executable_module_graph.get("module_graph_sha256") if executable_module_graph else None,
        "module_graph_source_pair_ir_sha256": executable_module_graph.get("source_pair_ir_sha256")
        if executable_module_graph
        else None,
        "module_graph_plan_a": list(
            (executable_module_graph.get("execution_plan") or {}).get("a") or []
        )
        if isinstance(executable_module_graph.get("execution_plan"), dict)
        else [],
        "module_graph_plan_b": list(
            (executable_module_graph.get("execution_plan") or {}).get("b") or []
        )
        if isinstance(executable_module_graph.get("execution_plan"), dict)
        else [],
        "llm_clone_decision_allowed": llm_contract.get("clone_decision_allowed"),
        "raw_source_patch_allowed": (
            ir_a.get("llm_contract", {}).get("raw_source_patch_allowed")
            if isinstance(ir_a.get("llm_contract"), dict)
            else None
        ),
    }


def build_execution_result_oracle_certificate(
    *,
    stdout: str,
    parsed: dict[str, Any] | None,
    meta: dict[str, Any],
) -> dict[str, Any]:
    probe_contract = meta.get("probe_contract") if isinstance(meta.get("probe_contract"), dict) else {}
    required_fields = probe_contract.get("result_fields") if isinstance(probe_contract.get("result_fields"), list) else []
    if not required_fields:
        required_fields = ["status", "same", "out_a", "out_b"]
    errors = validate_execution_result_oracle(
        stdout=stdout,
        parsed=parsed,
        required_fields=[str(field) for field in required_fields],
    )
    oracle: dict[str, Any] = {
        "schema_version": EXECUTION_RESULT_ORACLE_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "result_line_count": count_probe_result_lines(stdout),
        "required_result_fields": [str(field) for field in required_fields],
        "parsed_status": parsed.get("status") if isinstance(parsed, dict) else None,
        "parsed_same": parsed.get("same") if isinstance(parsed, dict) else None,
        "parsed_sha256": canonical_sha256(parsed) if parsed is not None else None,
        "stdout_sha256": sha256_text(stdout),
        "final_label_available": (
            isinstance(parsed, dict)
            and parsed.get("status") == "executed"
            and parsed.get("same") in (True, False)
            and not errors
        ),
        "case_summary_present": isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict),
        "case_summary_status": (
            parsed.get("case_summary", {}).get("status")
            if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict)
            else None
        ),
        "case_summary_sha256": (
            canonical_sha256(parsed.get("case_summary"))
            if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict)
            else None
        ),
        "case_summary_case_count": (
            parsed.get("case_summary", {}).get("case_count")
            if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict)
            else None
        ),
        "case_summary_mismatch_count": (
            parsed.get("case_summary", {}).get("mismatch_count")
            if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict)
            else None
        ),
        "case_summary_boundary_mismatch_count": (
            parsed.get("case_summary", {}).get("boundary_mismatch_count")
            if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict)
            else None
        ),
        "case_summary_non_boundary_mismatch_count": (
            parsed.get("case_summary", {}).get("non_boundary_mismatch_count")
            if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict)
            else None
        ),
        "boundary_only_divergence": (
            parsed.get("case_summary", {}).get("boundary_only_divergence")
            if isinstance(parsed, dict) and isinstance(parsed.get("case_summary"), dict)
            else None
        ),
        "probe_contract_sha256": canonical_sha256(probe_contract) if probe_contract else None,
        "validation_errors": errors,
    }
    oracle["oracle_sha256"] = canonical_sha256({key: value for key, value in oracle.items() if key != "oracle_sha256"})
    return oracle


def build_dynamic_outcome_certificate(
    *,
    status: str,
    mode: str,
    engine: str,
    compile_info: dict[str, Any],
    execution_info: dict[str, Any],
    meta: dict[str, Any],
    llm_context_completion: dict[str, Any] | None = None,
    llm_probe_synthesis: dict[str, Any] | None = None,
    compile_attempts: list[Any] | None = None,
) -> dict[str, Any]:
    parsed = execution_info.get("parsed") if isinstance(execution_info.get("parsed"), dict) else None
    compile_attempt_labels = [
        str(item.get("label"))
        for item in (compile_attempts or [])
        if isinstance(item, dict) and item.get("label") is not None
    ]
    final_label_available = (
        status == "executed"
        and isinstance(parsed, dict)
        and parsed.get("status") == "executed"
        and parsed.get("same") in (True, False)
    )
    outcome_class = dynamic_outcome_class(
        status=status,
        parsed=parsed,
        compile_info=compile_info,
        execution_info=execution_info,
    )
    failure_family = dynamic_failure_family(
        status=status,
        parsed=parsed,
        compile_info=compile_info,
        execution_info=execution_info,
    )
    certificate: dict[str, Any] = {
        "schema_version": DYNAMIC_OUTCOME_CERTIFICATE_SCHEMA_VERSION,
        "status": "verified",
        "policy": "classify_dynamic_execution_outcome_without_clone_judgment/v1",
        "dynamic_status": status,
        "mode": mode,
        "engine": engine,
        "outcome_class": outcome_class,
        "failure_family": failure_family,
        "phase": dynamic_outcome_phase(status),
        "final_label_available": final_label_available,
        "trusted_override_eligible": final_label_available,
        "probe_supported": bool(meta.get("probe_supported")),
        "probe_factory": meta.get("probe_factory"),
        "probe_family": meta.get("probe_family"),
        "llm_context_status": llm_context_completion.get("status") if isinstance(llm_context_completion, dict) else None,
        "llm_probe_status": llm_probe_synthesis.get("status") if isinstance(llm_probe_synthesis, dict) else None,
        "compile_returncode": compile_info.get("returncode") if isinstance(compile_info, dict) else None,
        "compile_attempt_count": len(compile_attempts or []),
        "compile_attempt_labels": compile_attempt_labels,
        "execution_returncode": execution_info.get("returncode") if isinstance(execution_info, dict) else None,
        "execution_timeout": execution_info.get("timeout") is True if isinstance(execution_info, dict) else False,
        "parsed_status": parsed.get("status") if isinstance(parsed, dict) else None,
        "parsed_same": parsed.get("same") if isinstance(parsed, dict) else None,
        "parsed_sha256": canonical_sha256(parsed) if isinstance(parsed, dict) else None,
        "compile_stdout_sha256": sha256_text(str(compile_info.get("stdout") or "")) if isinstance(compile_info, dict) else None,
        "compile_stderr_sha256": sha256_text(str(compile_info.get("stderr") or "")) if isinstance(compile_info, dict) else None,
        "execution_stdout_sha256": sha256_text(str(execution_info.get("stdout") or "")) if isinstance(execution_info, dict) else None,
        "execution_stderr_sha256": sha256_text(str(execution_info.get("stderr") or "")) if isinstance(execution_info, dict) else None,
        "llm_final_decision_allowed": False,
    }
    certificate[DYNAMIC_OUTCOME_HASH_FIELD] = build_dynamic_outcome_certificate_hash(certificate)
    return certificate


def dynamic_outcome_class(
    *,
    status: str,
    parsed: dict[str, Any] | None,
    compile_info: dict[str, Any],
    execution_info: dict[str, Any],
) -> str:
    if status == "executed" and isinstance(parsed, dict) and parsed.get("same") in (True, False):
        return "executed_label_available"
    if status in {"compile_success", "llm_context_compile_success"}:
        return "compile_only_success"
    if status in {"compile_success_no_probe", "llm_context_compile_success_no_probe"}:
        return "compiled_but_no_executable_probe"
    if status in {"compile_failed", "llm_context_compile_failed", "llm_probe_compile_failed"}:
        return "compile_failure"
    if status in {"execution_failed", "llm_context_execution_failed", "llm_probe_execution_failed"}:
        return "execution_failure"
    if status == "timeout" or (isinstance(execution_info, dict) and execution_info.get("timeout") is True):
        return "execution_timeout"
    if status in {"method_parse_failed"}:
        return "source_parse_failure"
    if status == "toolchain_missing":
        return "toolchain_unavailable"
    if status == "not_started":
        return "not_started"
    if isinstance(parsed, dict) and parsed.get("status") in {"compile_only", "inconclusive", "not_recoverable"}:
        return "probe_reported_no_label"
    return "unknown_or_incomplete"


def dynamic_failure_family(
    *,
    status: str,
    parsed: dict[str, Any] | None,
    compile_info: dict[str, Any],
    execution_info: dict[str, Any],
) -> str | None:
    if status == "executed" and isinstance(parsed, dict) and parsed.get("same") in (True, False):
        return None
    if status == "toolchain_missing":
        return "toolchain_missing"
    if status == "method_parse_failed":
        return "method_parse_failed"
    if status == "compile_failed":
        return "original_compile_failed"
    if status == "llm_context_compile_failed":
        return "llm_context_compile_failed"
    if status == "llm_probe_compile_failed":
        return "llm_probe_compile_failed"
    if status in {"compile_success_no_probe", "llm_context_compile_success_no_probe"}:
        return "probe_unavailable"
    if status in {"execution_failed", "llm_context_execution_failed", "llm_probe_execution_failed"}:
        return "execution_failed"
    if status == "timeout" or (isinstance(execution_info, dict) and execution_info.get("timeout") is True):
        return "timeout"
    if isinstance(parsed, dict) and parsed.get("status") in {"compile_only", "inconclusive", "not_recoverable"}:
        return f"probe_status_{parsed.get('status')}"
    if isinstance(compile_info, dict) and compile_info.get("returncode") not in (0, "0", None):
        return "compile_returncode_nonzero"
    return "unknown"


def dynamic_outcome_phase(status: str) -> str:
    if status in {"toolchain_missing", "method_parse_failed", "not_started"}:
        return "preflight"
    if status in {"compile_failed", "compile_success", "llm_context_compile_failed", "llm_context_compile_success"}:
        return "compile"
    if status in {"llm_probe_compile_failed"}:
        return "probe_synthesis"
    if status in {"compile_success_no_probe", "llm_context_compile_success_no_probe"}:
        return "probe_selection"
    if status in {"execution_failed", "llm_context_execution_failed", "llm_probe_execution_failed", "timeout"}:
        return "execution"
    if status == "executed":
        return "oracle"
    return "unknown"


def build_dynamic_outcome_certificate_hash(certificate: dict[str, Any]) -> str:
    return canonical_sha256({key: value for key, value in certificate.items() if key != DYNAMIC_OUTCOME_HASH_FIELD})


def validate_execution_result_oracle(
    *,
    stdout: str,
    parsed: dict[str, Any] | None,
    required_fields: list[str],
) -> list[str]:
    errors: list[str] = []
    result_line_count = count_probe_result_lines(stdout)
    if result_line_count != 1:
        errors.append("execution result oracle requires exactly one EVICLONE_RESULT line")
    if not isinstance(parsed, dict):
        errors.append("execution result oracle requires parsed JSON object")
        return errors
    for field in required_fields:
        if field not in parsed:
            errors.append(f"execution result missing required field: {field}")
    status = str(parsed.get("status") or "").strip()
    if status not in EXECUTION_RESULT_ALLOWED_STATUSES:
        errors.append("execution result status is invalid")
    same = parsed.get("same")
    if status == "executed" and same not in (True, False):
        errors.append("executed result requires boolean same")
    if "out_a" in required_fields and "out_a" in parsed and not isinstance(parsed.get("out_a"), str):
        errors.append("execution result out_a must be a string")
    if "out_b" in required_fields and "out_b" in parsed and not isinstance(parsed.get("out_b"), str):
        errors.append("execution result out_b must be a string")
    if "case_summary" in required_fields:
        summary = parsed.get("case_summary")
        if not isinstance(summary, dict):
            errors.append("execution result case_summary must be a parsed object")
        elif summary.get("status") != "verified":
            errors.append("execution result case_summary is invalid")
    return errors


def validate_runtime_source_safety(source: str) -> list[str]:
    errors: list[str] = []
    for name, pattern in RUNTIME_SOURCE_FORBIDDEN_PATTERNS:
        if re.search(pattern, source or ""):
            errors.append(f"runtime source uses non-deterministic or external-effect API: {name}")
    return errors


def build_runtime_source_safety_certificate(source: str) -> dict[str, Any]:
    errors = validate_runtime_source_safety(source)
    certificate: dict[str, Any] = {
        "schema_version": RUNTIME_SOURCE_SAFETY_SCHEMA_VERSION,
        "status": "verified" if not errors else "rejected",
        "source_sha256": sha256_text(source),
        "source_chars": len(source or ""),
        "forbidden_pattern_count": len(errors),
        "validation_errors": errors,
        "policy": "reject_non_deterministic_or_external_effect_runtime_source/v1",
    }
    certificate["certificate_sha256"] = canonical_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def build_java_toolchain_certificate() -> dict[str, Any]:
    global _JAVA_TOOLCHAIN_CERTIFICATE_CACHE
    if _JAVA_TOOLCHAIN_CERTIFICATE_CACHE is not None:
        return json.loads(json.dumps(_JAVA_TOOLCHAIN_CERTIFICATE_CACHE))

    javac = java_tool_version("javac")
    java = java_tool_version("java")
    errors: list[str] = []
    if not javac.get("available"):
        errors.append("javac_unavailable")
    if not java.get("available"):
        errors.append("java_unavailable")
    if javac.get("available") and javac.get("version_returncode") not in (0, "0"):
        errors.append("javac_version_failed")
    if java.get("available") and java.get("version_returncode") not in (0, "0"):
        errors.append("java_version_failed")

    certificate: dict[str, Any] = {
        "schema_version": JAVA_TOOLCHAIN_CERTIFICATE_SCHEMA_VERSION,
        "status": "verified" if not errors else "unavailable",
        "policy": "record_java_and_javac_used_by_synthetic_harness/v1",
        "compile_tool": javac,
        "execution_tool": java,
        "compile_command_prefix": ["javac", "-encoding", "UTF-8"],
        "execution_command_prefix": ["java", "-cp", "."],
        "version_probe_uses_shell": False,
        "validation_errors": errors,
    }
    certificate[JAVA_TOOLCHAIN_HASH_FIELD] = build_java_toolchain_certificate_hash(certificate)
    _JAVA_TOOLCHAIN_CERTIFICATE_CACHE = json.loads(json.dumps(certificate))
    return certificate


def java_tool_version(command_name: str) -> dict[str, Any]:
    path = shutil.which(command_name)
    info: dict[str, Any] = {
        "command_name": command_name,
        "available": bool(path),
        "path_sha256": sha256_text(str(Path(path).resolve())) if path else None,
        "path_basename": Path(path).name if path else None,
        "version_command": [command_name, "-version"],
        "version_returncode": None,
        "version_stdout_sha256": None,
        "version_stderr_sha256": None,
        "version_text": "",
    }
    if not path:
        return info
    try:
        proc = subprocess.run(
            [path, "-version"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        info["version_error"] = type(exc).__name__
        return info
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    version_text = (stdout + "\n" + stderr).strip()
    info.update(
        {
            "version_returncode": proc.returncode,
            "version_stdout_sha256": sha256_text(stdout),
            "version_stderr_sha256": sha256_text(stderr),
            "version_text": version_text[:1000],
        }
    )
    return info


def build_java_toolchain_certificate_hash(certificate: dict[str, Any]) -> str:
    return canonical_sha256({key: value for key, value in certificate.items() if key != JAVA_TOOLCHAIN_HASH_FIELD})


def build_java_execution_sandbox_certificate(
    *,
    timeout_sec: int | float,
    work_root: Path | str | None,
    probe_work: Path | str | None,
    cleanup_requested: bool | None,
    classpath_resource_fixture: dict[str, Any] | None = None,
    system_context_fixture: dict[str, Any] | None = None,
    locale_time_fixture: dict[str, Any] | None = None,
) -> dict[str, Any]:
    work_root_text = str(Path(work_root).resolve()) if work_root is not None else ""
    probe_work_text = str(Path(probe_work).resolve()) if probe_work is not None else ""
    work_dir_within_cwd = False
    if work_root_text and probe_work_text:
        try:
            Path(probe_work_text).relative_to(Path(work_root_text))
            work_dir_within_cwd = True
        except ValueError:
            work_dir_within_cwd = False
    sandbox = {
        "schema_version": JAVA_EXECUTION_SANDBOX_SCHEMA_VERSION,
        "cwd_policy": "dedicated_pair_workdir" if work_root_text else "unrecorded_unit_test_workdir",
        "cwd_sha256": sha256_text(work_root_text) if work_root_text else None,
        "work_dir_argument_policy": "dedicated_child_work_dir",
        "work_dir_argument_sha256": sha256_text(probe_work_text) if probe_work_text else None,
        "work_dir_argument_within_cwd": work_dir_within_cwd if probe_work_text else None,
        "source_filename": "EviProbe.java",
        "compile_uses_shell": False,
        "execution_uses_shell": False,
        "compile_command_policy": "javac_utf8_single_source",
        "execution_command_policy": "java_classpath_current_dir_single_work_arg",
        "classpath_policy": "current_workdir_only",
        "classpath_resource_fixture": classpath_resource_fixture,
        "system_context_fixture": system_context_fixture,
        "locale_time_fixture": locale_time_fixture,
        "timeout_sec": timeout_sec,
        "cleanup_requested": cleanup_requested,
        "real_external_services_allowed": False,
    }
    sandbox["sandbox_sha256"] = canonical_sha256(
        {key: value for key, value in sandbox.items() if key != "sandbox_sha256"}
    )
    return sandbox


def install_classpath_resource_fixture(work_root: Path) -> dict[str, Any]:
    installed: list[dict[str, Any]] = []
    for name in CLASSPATH_RESOURCE_FIXTURE_NAMES:
        target = work_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(CLASSPATH_RESOURCE_FIXTURE_PAYLOAD, encoding="utf-8", newline="\n")
        installed.append(
            {
                "name": name,
                "bytes": target.stat().st_size,
                "sha256": sha256_text(target.read_text(encoding="utf-8")),
            }
        )
    manifest: dict[str, Any] = {
        "schema_version": CLASSPATH_RESOURCE_FIXTURE_SCHEMA_VERSION,
        "status": "installed",
        "classpath_policy": "current_workdir_only",
        "resource_count": len(installed),
        "resource_names": list(CLASSPATH_RESOURCE_FIXTURE_NAMES),
        "payload_sha256": sha256_text(CLASSPATH_RESOURCE_FIXTURE_PAYLOAD),
        "resources": installed,
        "deterministic": True,
        "no_external_services": True,
    }
    manifest["fixture_sha256"] = canonical_sha256(
        {key: value for key, value in manifest.items() if key != "fixture_sha256"}
    )
    return manifest


def install_system_context_fixture(work_dir: Path) -> dict[str, Any]:
    home = work_dir.resolve() / "system-home"
    tmp = work_dir.resolve() / "system-tmp"
    home.mkdir(parents=True, exist_ok=True)
    tmp.mkdir(parents=True, exist_ok=True)
    properties = dict(SYSTEM_CONTEXT_PROPERTY_FIXTURE)
    properties.update(
        {
            "user.home": str(home),
            "java.io.tmpdir": str(tmp),
        }
    )
    environment = dict(SYSTEM_CONTEXT_ENV_FIXTURE)
    environment.update(
        {
            "HOME": str(home),
            "TMPDIR": str(tmp),
            "TEMP": str(tmp),
            "TMP": str(tmp),
        }
    )
    manifest: dict[str, Any] = {
        "schema_version": SYSTEM_CONTEXT_FIXTURE_SCHEMA_VERSION,
        "status": "installed",
        "property_keys": sorted(properties.keys()),
        "environment_keys": sorted(environment.keys()),
        "property_values": properties,
        "environment_values": environment,
        "property_values_sha256": canonical_sha256(properties),
        "environment_values_sha256": canonical_sha256(environment),
        "secret_environment_forwarding": False,
        "deterministic": True,
        "no_external_services": True,
    }
    manifest["fixture_sha256"] = canonical_sha256(
        {key: value for key, value in manifest.items() if key != "fixture_sha256"}
    )
    return manifest


def install_locale_time_fixture() -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema_version": LOCALE_TIME_FIXTURE_SCHEMA_VERSION,
        "status": "installed",
        "locale_language": LOCALE_TIME_FIXTURE["language"],
        "locale_country": LOCALE_TIME_FIXTURE["country"],
        "locale_language_tag": LOCALE_TIME_FIXTURE["language_tag"],
        "time_zone_id": LOCALE_TIME_FIXTURE["time_zone_id"],
        "system_properties": {
            "user.language": LOCALE_TIME_FIXTURE["language"],
            "user.country": LOCALE_TIME_FIXTURE["country"],
            "user.timezone": LOCALE_TIME_FIXTURE["time_zone_id"],
        },
        "deterministic": True,
        "no_external_services": True,
        "host_locale_forwarding": False,
        "host_timezone_forwarding": False,
    }
    manifest["fixture_sha256"] = canonical_sha256(
        {key: value for key, value in manifest.items() if key != "fixture_sha256"}
    )
    return manifest


def build_runtime_fixture_hash(fixture: dict[str, Any]) -> str:
    return canonical_sha256(
        {key: value for key, value in fixture.items() if key != RUNTIME_FIXTURE_HASH_FIELD}
    )


def system_context_process_env(fixture: dict[str, Any]) -> dict[str, str]:
    env = minimal_java_process_env()
    values = fixture.get("environment_values") if isinstance(fixture.get("environment_values"), dict) else {}
    for key, value in values.items():
        env[str(key)] = str(value)
    return env


def minimal_java_process_env() -> dict[str, str]:
    keep = {
        "PATH",
        "Path",
        "PATHEXT",
        "SystemRoot",
        "WINDIR",
        "ComSpec",
        "TEMP",
        "TMP",
        "JAVA_HOME",
        "JDK_HOME",
    }
    env = {key: value for key, value in os.environ.items() if key in keep}
    if not any(key.lower() == "path" for key in env):
        env["PATH"] = os.defpath
    return env


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def write_context_source_artifact(
    source: str,
    output_dir: Path,
    *,
    pair: ClonePair,
    context_payload: dict[str, Any] | None = None,
    probe_payload: dict[str, Any] | None = None,
    probe_body: str | None = None,
    retained: bool = True,
    quarantined: bool = False,
    artifact_role: str | None = None,
    rejection_reason: str | None = None,
) -> dict[str, Any]:
    digest = hashlib.sha256(source.encode("utf-8", "replace")).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"pair_{pair.pair_id}_{digest[:16]}_EviProbe.java"
    path.write_text(source, encoding="utf-8", newline="\n")
    artifact = {
        "schema_version": SOURCE_ARTIFACT_SCHEMA_VERSION,
        "retained": bool(retained),
        "path": str(path.resolve()),
        "sha256": digest,
        "bytes": path.stat().st_size,
        "source_preservation": build_source_preservation_certificate(source, pair),
    }
    if quarantined:
        artifact["quarantined"] = True
    if artifact_role:
        artifact["artifact_role"] = artifact_role
    if rejection_reason:
        artifact["rejection_reason"] = rejection_reason
    if isinstance(context_payload, dict):
        artifact["context_added_context"] = build_context_added_context_certificate(
            source,
            context_payload,
        )
        artifact["context_probe_execution_path"] = build_context_probe_execution_path_certificate(
            source,
            context_payload,
        )
        artifact["context_source_safety"] = build_context_source_safety_certificate(source)
    if isinstance(probe_payload, dict) and probe_body is not None:
        artifact["probe_source_binding"] = build_probe_source_binding_certificate(
            source,
            probe_body,
            probe_payload,
        )
    artifact[SOURCE_ARTIFACT_HASH_FIELD] = build_source_artifact_hash(artifact)
    return artifact


def build_source_artifact_hash(artifact: dict[str, Any]) -> str:
    return canonical_sha256({key: value for key, value in artifact.items() if key != SOURCE_ARTIFACT_HASH_FIELD})


def build_source_preservation_certificate(source: str, pair: ClonePair) -> dict[str, Any]:
    a = source_fragment_preservation(source, pair.code_a)
    b = source_fragment_preservation(source, pair.code_b)
    if a["exact_present"] and b["exact_present"]:
        status = "exact"
    elif a["normalized_present"] and b["normalized_present"]:
        status = "normalized"
    elif a["identifier_retention"]["status"] == "sufficient" and b["identifier_retention"]["status"] == "sufficient":
        status = "identifier_supported"
    else:
        status = "weak"
    certificate: dict[str, Any] = {
        "schema_version": "eviclone-source-preservation/v1",
        "status": status,
        "pair_id": pair.pair_id,
        "function_ids": {
            "a": pair.function_id_a,
            "b": pair.function_id_b,
        },
        "source_sha256": sha256_text(source),
        "source_chars": len(source or ""),
        "snippet_a": a,
        "snippet_b": b,
        "method_body_rewrite_allowed": False,
        "certificate_scope": "original BCB method fragments embedded in retained EviProbe.java sidecar",
    }
    certificate["certificate_sha256"] = canonical_sha256(
        {key: value for key, value in certificate.items() if key != "certificate_sha256"}
    )
    return certificate


def source_fragment_preservation(source: str, fragment: str) -> dict[str, Any]:
    stripped = fragment.strip()
    method = parse_method(fragment)
    identifiers = significant_source_identifiers(fragment)
    return {
        "sha256": hashlib.sha256(fragment.encode("utf-8", "replace")).hexdigest(),
        "nonempty": bool(stripped),
        "exact_present": bool(stripped and stripped in source),
        "normalized_present": bool(stripped and normalize_source_fragment(stripped) in normalize_source_fragment(source)),
        "method_name": method.name if method else None,
        "method_name_present": bool(method and re.search(rf"\b{re.escape(method.name)}\b", source)),
        "identifier_retention": identifier_retention_certificate(identifiers, source),
    }


def normalize_source_fragment(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def significant_source_identifiers(text: str) -> list[str]:
    keywords = {
        "abstract",
        "boolean",
        "break",
        "byte",
        "case",
        "catch",
        "char",
        "class",
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
    seen: set[str] = set()
    result: list[str] = []
    for token in re.findall(r"[A-Za-z_$][\w$]*", text):
        if token in keywords or len(token) <= 1:
            continue
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result[:24]


def identifier_retention_certificate(identifiers: list[str], source: str) -> dict[str, Any]:
    matched = [identifier for identifier in identifiers if re.search(rf"\b{re.escape(identifier)}\b", source)]
    required = min(3, len(identifiers))
    if not identifiers:
        status = "no_identifiers"
    elif len(matched) >= required:
        status = "sufficient"
    elif matched:
        status = "partial"
    else:
        status = "none"
    return {
        "status": status,
        "identifier_count": len(identifiers),
        "matched_count": len(matched),
        "required_count": required,
        "matched": matched[:12],
    }


def replace_compile_only_main_body(source: str, probe_body: str) -> str:
    marker = '        printStatus("compile_only");'
    if marker not in source:
        return source
    return source.replace(marker, indent(probe_body, 8), 1)


def parse_probe_output(stdout: str) -> dict[str, Any] | None:
    result_lines = [line for line in stdout.splitlines() if line.startswith("EVICLONE_RESULT ")]
    if not result_lines:
        return None
    if len(result_lines) != 1:
        return {"status": "invalid_output", "error": "multiple_result_lines", "result_line_count": len(result_lines)}
    payload = result_lines[0][len("EVICLONE_RESULT ") :].strip()
    try:
        parsed = json.loads(payload)
        if isinstance(parsed, dict):
            case_summary = parsed.get("case_summary")
            if isinstance(case_summary, str):
                parsed["case_summary_raw"] = case_summary
                parsed["case_summary"] = parse_probe_case_summary(case_summary)
            parsed["result_line_count"] = 1
        return parsed
    except json.JSONDecodeError:
        return {"status": "invalid_output", "error": "invalid_json", "raw": payload, "result_line_count": 1}
    return None


def count_probe_result_lines(stdout: str) -> int:
    return sum(1 for line in (stdout or "").splitlines() if line.startswith("EVICLONE_RESULT "))


def parse_probe_case_summary(raw: str) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    issues: list[str] = []
    boundary_tags = {"branch_boundary", "boundary_neighbor", "below_branch_boundary", "above_branch_boundary"}
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|")
        if len(parts) < 3 or not parts[0].startswith("case"):
            issues.append(f"malformed_case_summary_line:{line[:40]}")
            continue
        try:
            case_index = int(parts[0][len("case") :])
        except ValueError:
            issues.append(f"malformed_case_index:{parts[0]}")
            continue
        fields: dict[str, str] = {}
        for part in parts[1:]:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            fields[key] = value
        matched_raw = fields.get("matched")
        if matched_raw not in {"true", "false"}:
            issues.append(f"malformed_case_match:{parts[0]}")
            continue
        tags = [tag for tag in fields.get("tags", "").split(",") if tag]
        cases.append(
            {
                "case_index": case_index,
                "matched": matched_raw == "true",
                "tags": tags,
                "is_boundary_case": bool(boundary_tags & set(tags)),
            }
        )
    mismatch_count = sum(1 for case in cases if not case["matched"])
    boundary_case_count = sum(1 for case in cases if case["is_boundary_case"])
    boundary_mismatch_count = sum(1 for case in cases if case["is_boundary_case"] and not case["matched"])
    non_boundary_mismatch_count = sum(1 for case in cases if not case["is_boundary_case"] and not case["matched"])
    summary = {
        "schema_version": "eviclone-probe-case-summary/v1",
        "status": "verified" if not issues else "rejected",
        "case_count": len(cases),
        "mismatch_count": mismatch_count,
        "boundary_case_count": boundary_case_count,
        "boundary_mismatch_count": boundary_mismatch_count,
        "non_boundary_mismatch_count": non_boundary_mismatch_count,
        "boundary_only_divergence": mismatch_count > 0 and boundary_mismatch_count > 0 and non_boundary_mismatch_count == 0,
        "cases": cases,
        "issues": issues,
    }
    summary["case_summary_sha256"] = canonical_sha256(
        {key: value for key, value in summary.items() if key != "case_summary_sha256"}
    )
    return summary
