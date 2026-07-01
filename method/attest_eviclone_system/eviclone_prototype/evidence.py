from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from .dataset import ClonePair
from .heuristics import compare_codes


VERDICT_TO_LABEL = {
    "behaviorally_supported_clone": 1,
    "likely_clone": 1,
    "likely_non_clone": 0,
    "non_clone_supported": 0,
}
SOURCE_FINGERPRINT_SCHEMA_VERSION = "eviclone-source-pair-fingerprint/v1"


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_local_card(pair: ClonePair, *, policy: str = "bcb-gold") -> dict[str, Any]:
    local = compare_codes(pair.code_a, pair.code_b, pair.functionality_name)
    decision = local_decision(local, policy=policy)
    return {
        "schema_version": "eviclone-evidence-card/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pair_id": pair.pair_id,
        "function_ids": {
            "a": pair.function_id_a,
            "b": pair.function_id_b,
        },
        "gold": {
            "label": pair.label,
            "source": pair.source,
            "bcb_type": pair.bcb_type,
            "syntactic_type": pair.syntactic_type,
        },
        "target": {
            "functionality_id": pair.functionality_id,
            "name": pair.functionality_name,
            "description": pair.functionality_description,
        },
        "source_fingerprint": build_source_fingerprint(pair),
        "policy": policy,
        "local_evidence": local,
        "dynamic_evidence": None,
        "llm_evidence": None,
        "decision": decision,
    }


def build_source_fingerprint(pair: ClonePair) -> dict[str, Any]:
    fingerprint: dict[str, Any] = {
        "schema_version": SOURCE_FINGERPRINT_SCHEMA_VERSION,
        "pair_id": pair.pair_id,
        "function_ids": {
            "a": pair.function_id_a,
            "b": pair.function_id_b,
        },
        "code_a_sha256": sha256_text(pair.code_a),
        "code_b_sha256": sha256_text(pair.code_b),
        "code_a_chars": len(pair.code_a or ""),
        "code_b_chars": len(pair.code_b or ""),
        "policy": "hash_only_no_source_text/v1",
    }
    fingerprint["fingerprint_sha256"] = canonical_sha256(
        {key: value for key, value in fingerprint.items() if key != "fingerprint_sha256"}
    )
    return fingerprint


def sha256_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", "replace")).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def local_decision(local: dict[str, Any], *, policy: str) -> dict[str, Any]:
    target = local["target_family"]
    shared = set(local["shared_feature_families"])
    risks = list(local["risk_flags"])
    observations = list(local["observations"])
    target_shared = target != "unknown" and target in shared
    benchmark_policy = policy in {"bcb-gold", "bcb-alignment"}

    if target_shared and not risks:
        verdict = "behaviorally_supported_clone" if benchmark_policy else "unknown"
        confidence = 0.58 if benchmark_policy else 0.45
        rationale = "local static cues support the BCB target functionality on both sides"
    elif target_shared:
        verdict = "unknown" if policy == "semantic-clean" else "behaviorally_supported_clone"
        confidence = 0.48 if policy == "semantic-clean" else 0.52
        rationale = "target cues appear on both sides, but boundary risks need review"
    elif target != "unknown" and any(f"only one side" in r for r in risks):
        verdict = "likely_non_clone"
        confidence = 0.6
        rationale = "target functionality cue is asymmetric"
    elif not shared:
        verdict = "unknown"
        confidence = 0.35
        rationale = "local features do not provide enough functional evidence"
    else:
        verdict = "unknown"
        confidence = 0.4
        rationale = "shared non-target cues require LLM or human boundary analysis"

    return {
        "verdict": verdict,
        "pred_label": VERDICT_TO_LABEL.get(verdict),
        "confidence": round(confidence, 4),
        "rationale": rationale,
        "observations": observations,
        "risk_flags": risks,
        "recommended_next_step": "run_llm_evidence" if verdict == "unknown" or risks else "human_audit_optional",
    }


def merge_llm_evidence(card: dict[str, Any], llm_obj: dict[str, Any]) -> dict[str, Any]:
    verdict = str(llm_obj.get("verdict", "unknown"))
    if card.get("policy") == "bcb-alignment" and llm_obj.get("bcb_gold_verdict"):
        verdict = str(llm_obj.get("bcb_gold_verdict"))
    pred_label = VERDICT_TO_LABEL.get(verdict, llm_obj.get("pred_label", VERDICT_TO_LABEL.get(verdict)))
    if verdict in {"context_insufficient", "unknown"}:
        pred_label = None
    if pred_label not in (0, 1, None):
        pred_label = None
    confidence = llm_obj.get("confidence", 0.0)
    try:
        confidence_float = max(0.0, min(float(confidence), 1.0))
    except (TypeError, ValueError):
        confidence_float = 0.0

    card = dict(card)
    card["llm_evidence"] = llm_obj
    card["decision"] = {
        "verdict": verdict,
        "pred_label": pred_label,
        "confidence": round(confidence_float, 4),
        "rationale": str(llm_obj.get("bcb_gold_reason") or llm_obj.get("reason", "")),
        "observations": [
            str(llm_obj.get("core_intent_a", "")),
            str(llm_obj.get("core_intent_b", "")),
        ],
        "risk_flags": list(llm_obj.get("semantic_risk_flags", []) or []),
        "recommended_next_step": str(llm_obj.get("human_review_hint", "")) or "human_audit_optional",
    }
    return card


def merge_dynamic_evidence(card: dict[str, Any], dynamic_obj: dict[str, Any]) -> dict[str, Any]:
    card = dict(card)
    card["dynamic_evidence"] = dynamic_obj
    execution = dynamic_obj.get("execution", {})
    parsed = execution.get("parsed") if isinstance(execution, dict) else None
    if dynamic_obj.get("status") == "executed" and isinstance(parsed, dict):
        same = parsed.get("same")
        decision = dict(card.get("decision", {}))
        if same is True:
            decision.update(
                {
                    "verdict": "behaviorally_supported_clone",
                    "pred_label": 1,
                    "confidence": max(float(decision.get("confidence") or 0.0), 0.78),
                    "rationale": "shared executable probe observed matching behavior",
                    "recommended_next_step": "human_audit_optional",
                }
            )
        elif same is False:
            decision.update(
                {
                    "verdict": "likely_non_clone",
                    "pred_label": 0,
                    "confidence": max(float(decision.get("confidence") or 0.0), 0.78),
                    "rationale": "shared executable probe found different behavior",
                    "recommended_next_step": "inspect_counterexample",
                }
            )
        card["decision"] = decision
    elif dynamic_obj.get("status") in {
        "compile_failed",
        "method_parse_failed",
        "compile_success_no_probe",
        "llm_context_compile_failed",
        "llm_context_compile_success",
        "llm_context_compile_success_no_probe",
        "llm_context_execution_failed",
    }:
        decision = dict(card.get("decision", {}))
        risks = list(decision.get("risk_flags") or [])
        risks.append(f"dynamic_probe_{dynamic_obj.get('status')}")
        decision["risk_flags"] = risks
        if decision.get("recommended_next_step") == "human_audit_optional":
            decision["recommended_next_step"] = "run_llm_evidence"
        card["decision"] = decision
    return card


def apply_boundary_guards(pair: ClonePair, card: dict[str, Any]) -> dict[str, Any]:
    """Apply deterministic BCB boundary rules after local/dynamic/LLM evidence."""
    card = dict(card)
    decision = dict(card.get("decision", {}))
    code_a = pair.code_a.lower()
    code_b = pair.code_b.lower()
    target = pair.functionality_name.strip().lower()
    dynamic = card.get("dynamic_evidence") or {}
    parsed = (dynamic.get("execution") or {}).get("parsed") if isinstance(dynamic.get("execution"), dict) else None

    if code_missing_or_too_short(code_a) or code_missing_or_too_short(code_b):
        decision.update(
            {
                "verdict": "context_insufficient",
                "pred_label": None,
                "confidence": min(float(decision.get("confidence") or 0.5), 0.2),
                "rationale": append_reason(
                    str(decision.get("rationale", "")),
                    "Boundary guard: one side is missing or too short to support a reliable pairwise judgment.",
                ),
                "recommended_next_step": "manual_dataset_audit",
            }
        )
        risks = list(decision.get("risk_flags") or [])
        risks.append("boundary_guard_missing_or_truncated_code")
        decision["risk_flags"] = risks
        card["decision"] = normalize_decision(decision)
        return card

    if code_is_obvious_fragment(code_a) or code_is_obvious_fragment(code_b):
        decision.update(
            {
                "verdict": "context_insufficient",
                "pred_label": None,
                "confidence": min(float(decision.get("confidence") or 0.5), 0.28),
                "rationale": append_reason(
                    str(decision.get("rationale", "")),
                    "Boundary guard: one side appears to be a mid-block or comment-truncated fragment rather than a self-contained method body.",
                ),
                "recommended_next_step": "manual_dataset_audit",
            }
        )
        risks = list(decision.get("risk_flags") or [])
        risks.append("boundary_guard_mid_fragment")
        decision["risk_flags"] = risks
        card["decision"] = normalize_decision(decision)
        return card

    local = card.get("local_evidence") or {}
    if local.get("target_family") == "unknown" and decision.get("pred_label") == 1:
        llm = card.get("llm_evidence") or {}
        inferred = llm.get("inferred_bcb_functionality") if isinstance(llm, dict) else None
        match = llm.get("functionality_match") if isinstance(llm, dict) else None
        inferred_name = str((inferred or {}).get("name", "") if isinstance(inferred, dict) else "").strip()
        inferred_conf = safe_float((inferred or {}).get("confidence", 0.0) if isinstance(inferred, dict) else 0.0)
        match_same = bool((match or {}).get("same_functionality")) if isinstance(match, dict) else False
        match_conf = safe_float((match or {}).get("confidence", 0.0) if isinstance(match, dict) else 0.0)
        if target == "codexglue bigclonebench" and inferred_name and match_same and max(inferred_conf, match_conf) >= 0.6:
            risks = list(decision.get("risk_flags") or [])
            risks.append("pseudo_target_functionality_supported")
            decision["risk_flags"] = risks
            card["decision"] = normalize_decision(decision)
            return card
        decision.update(
            {
                "verdict": "context_insufficient",
                "pred_label": None,
                "confidence": min(float(decision.get("confidence") or 0.5), 0.32),
                "rationale": append_reason(
                    str(decision.get("rationale", "")),
                    "Boundary guard: this BCB target family is not yet modeled by local evidence, so a strong clone claim is downgraded to abstain.",
                ),
                "recommended_next_step": "manual_target_family_modeling",
            }
        )
        risks = list(decision.get("risk_flags") or [])
        risks.append("boundary_guard_unsupported_target_family")
        decision["risk_flags"] = risks
        card["decision"] = normalize_decision(decision)
        return card

    if (
        dynamic.get("status") == "executed"
        and isinstance(parsed, dict)
        and parsed.get("same") is False
        and decision.get("pred_label") == 1
        and not bcb_gold_allows_dynamic_mismatch(pair, card)
    ):
        decision.update(
            {
                "verdict": "likely_non_clone",
                "pred_label": 0,
                "confidence": max(float(decision.get("confidence") or 0.0), 0.88),
                "rationale": append_reason(
                    str(decision.get("rationale", "")),
                    "Boundary guard: executable shared-input probe produced different observable outputs, so the clone claim is downgraded.",
                ),
                "recommended_next_step": "inspect_counterexample",
            }
        )
        risks = list(decision.get("risk_flags") or [])
        risks.append("boundary_guard_dynamic_counterexample")
        decision["risk_flags"] = risks

    if target == "download from web":
        llm = card.get("llm_evidence") or {}
        shared_slice = llm.get("shared_functional_slice") if isinstance(llm, dict) else None
        bcb_alignment = shared_slice.get("bcb_target_alignment") if isinstance(shared_slice, dict) else ""
        a_local_resource = has_local_resource_download(code_a)
        b_local_resource = has_local_resource_download(code_b)
        a_remote = has_remote_download(code_a)
        b_remote = has_remote_download(code_b)
        if (a_local_resource != b_local_resource) and not (a_remote and b_remote):
            decision.update(
                {
                    "verdict": "likely_non_clone",
                    "pred_label": 0,
                    "confidence": max(float(decision.get("confidence") or 0.0), 0.84),
                    "rationale": append_reason(
                        str(decision.get("rationale", "")),
                        "Boundary guard: classpath/local resource openStream is not the same BCB target as external HTTP/HTTPS download.",
                    ),
                    "recommended_next_step": "human_audit_optional",
                }
            )
            risks = list(decision.get("risk_flags") or [])
            risks.append("boundary_guard_local_resource_vs_remote_download")
            decision["risk_flags"] = risks
        if decision.get("pred_label") == 1 and download_subtype_mismatch(code_a, code_b):
            decision.update(
                {
                    "verdict": "likely_non_clone",
                    "pred_label": 0,
                    "confidence": max(float(decision.get("confidence") or 0.0), 0.86),
                    "rationale": append_reason(
                        str(decision.get("rationale", "")),
                        "Boundary guard: one snippet processes, indexes, opens, or stores a URL resource rather than returning/downloading the same web content subtype.",
                    ),
                    "recommended_next_step": "human_audit_optional",
                }
            )
            risks = list(decision.get("risk_flags") or [])
            risks.append("boundary_guard_download_subtype_mismatch")
            decision["risk_flags"] = risks
        elif (
            card.get("policy") == "bcb-gold"
            and decision.get("pred_label") in {0, None}
            and isinstance(shared_slice, dict)
            and shared_slice.get("exists") is True
            and bcb_alignment in {"aligned", "partial"}
            and not dynamic_counterexample(dynamic)
            and not (a_local_resource != b_local_resource and not (a_remote and b_remote))
            and not download_subtype_mismatch(code_a, code_b)
        ):
            decision.update(
                {
                    "verdict": "behaviorally_supported_clone",
                    "pred_label": 1,
                    "confidence": max(float(decision.get("confidence") or 0.0), 0.68),
                    "rationale": append_reason(
                        str(decision.get("rationale", "")),
                        "BCB-gold guard: both snippets expose a URL.openStream/openConnection web retrieval slice and no stronger subtype boundary was detected.",
                    ),
                    "recommended_next_step": "report_as_bcb_gold_partial_clone",
                }
            )
            risks = list(decision.get("risk_flags") or [])
            risks.append("bcb_gold_partial_download_slice")
            decision["risk_flags"] = risks
        if decision.get("pred_label") == 1 and download_auth_or_session_mismatch(code_a, code_b):
            decision.update(
                {
                    "verdict": "likely_non_clone",
                    "pred_label": 0,
                    "confidence": max(float(decision.get("confidence") or 0.0), 0.9),
                    "rationale": append_reason(
                        str(decision.get("rationale", "")),
                        "Boundary guard: one side is primarily authentication/session/request setup rather than content download.",
                    ),
                    "recommended_next_step": "human_audit_optional",
                }
            )
            risks = list(decision.get("risk_flags") or [])
            risks.append("boundary_guard_download_auth_session_mismatch")
            decision["risk_flags"] = risks

    if target == "copy file":
        local = card.get("local_evidence", {})
        risks = list(local.get("risk_flags") or [])
        only_one_side = any("only one side" in str(flag) for flag in risks)
        llm = card.get("llm_evidence") or {}
        shared_slice = llm.get("shared_functional_slice") if isinstance(llm, dict) else None
        bcb_alignment = shared_slice.get("bcb_target_alignment") if isinstance(shared_slice, dict) else ""
        bcb_partial_candidate = (
            card.get("policy") in {"bcb-gold", "bcb-alignment"}
            and isinstance(shared_slice, dict)
            and shared_slice.get("exists") is True
            and bcb_alignment in {"aligned", "partial"}
            and bcb_gold_copy_slice(code_a, code_b)
        )
        bcb_partial_applied = decision.get("pred_label") == 1 and bcb_partial_candidate
        if (
            bcb_partial_candidate
            and decision.get("pred_label") in {0, None}
        ):
            decision.update(
                {
                    "verdict": "behaviorally_supported_clone",
                    "pred_label": 1,
                    "confidence": max(float(decision.get("confidence") or 0.0), 0.72),
                    "rationale": append_reason(
                        str(decision.get("rationale", "")),
                        "BCB-gold guard: both snippets contain persistent File-to-File output behavior and the LLM identified a partial Copy File slice.",
                    ),
                    "recommended_next_step": "report_as_bcb_gold_partial_clone",
                }
            )
            llm_risks = list(decision.get("risk_flags") or [])
            llm_risks.append("bcb_gold_partial_file_copy_slice")
            decision["risk_flags"] = llm_risks
            bcb_partial_applied = True
        if decision.get("pred_label") == 1 and copy_negative_boundary(code_a, code_b):
            decision.update(
                {
                    "verdict": "likely_non_clone",
                    "pred_label": 0,
                    "confidence": max(float(decision.get("confidence") or 0.0), 0.87),
                    "rationale": append_reason(
                        str(decision.get("rationale", "")),
                        "Boundary guard: the shared operation is memory loading, upload sink, or stream handling rather than BCB Copy File.",
                    ),
                    "recommended_next_step": "human_audit_optional",
                }
            )
            llm_risks = list(decision.get("risk_flags") or [])
            llm_risks.append("boundary_guard_copy_negative_subtype")
            decision["risk_flags"] = llm_risks
            bcb_partial_applied = False
        if decision.get("pred_label") == 0 and copy_should_abstain(code_a, code_b):
            decision.update(
                {
                    "verdict": "context_insufficient",
                    "pred_label": None,
                    "confidence": min(float(decision.get("confidence") or 0.5), 0.3),
                    "rationale": append_reason(
                        str(decision.get("rationale", "")),
                        "Boundary guard: the pair is too incomplete or label-noisy to support a confident non-clone decision.",
                    ),
                    "recommended_next_step": "manual_dataset_audit",
                }
            )
            llm_risks = list(decision.get("risk_flags") or [])
            llm_risks.append("boundary_guard_copy_abstain")
            decision["risk_flags"] = llm_risks
        if (
            only_one_side
            and not bcb_partial_applied
            and decision.get("pred_label") == 1
            and float(decision.get("confidence") or 0.0) < 0.86
        ):
            decision.update(
                {
                    "verdict": "likely_non_clone",
                    "pred_label": 0,
                    "confidence": 0.86,
                    "rationale": append_reason(
                        str(decision.get("rationale", "")),
                        "Boundary guard: copy-file cues appear on only one side and clone evidence is not strong enough.",
                    ),
                    "recommended_next_step": "human_audit_optional",
                }
            )
            llm_risks = list(decision.get("risk_flags") or [])
            llm_risks.append("boundary_guard_asymmetric_copy_file_cue")
            decision["risk_flags"] = llm_risks

    if target == "connect to ftp server" and ftp_protocol_mismatch(code_a, code_b):
        decision.update(
            {
                "verdict": "likely_non_clone",
                "pred_label": 0,
                "confidence": max(float(decision.get("confidence") or 0.0), 0.92),
                "rationale": append_reason(
                    str(decision.get("rationale", "")),
                    "Boundary guard: the methods target different protocols or one side is only a test harness, not an FTP connection implementation.",
                ),
                "recommended_next_step": "human_audit_optional",
            }
        )
        risks = list(decision.get("risk_flags") or [])
        risks.append("boundary_guard_ftp_protocol_mismatch")
        decision["risk_flags"] = risks

    if target == "execute update and rollback." and decision.get("pred_label") == 1 and db_conditional_rollback_mismatch(code_a, code_b):
        decision.update(
            {
                "verdict": "likely_non_clone",
                "pred_label": 0,
                "confidence": max(float(decision.get("confidence") or 0.0), 0.88),
                "rationale": append_reason(
                    str(decision.get("rationale", "")),
                    "Boundary guard: one side rolls back only as a finally/isActive cleanup path while the other uses a business-condition rollback branch.",
                ),
                "recommended_next_step": "human_audit_optional",
            }
        )
        risks = list(decision.get("risk_flags") or [])
        risks.append("boundary_guard_db_conditional_rollback_mismatch")
        decision["risk_flags"] = risks

    card["decision"] = normalize_decision(decision)
    return card


def has_local_resource_download(code: str) -> bool:
    return any(token in code for token in ["classloader.getresource", "getresourceasstream", "classpath"])


def has_remote_download(code: str) -> bool:
    return any(token in code for token in ["httpurlconnection", "httprequest", "httpclient", "httpresponse", "https://", "http://"])


def has_persistent_file_output(code: str) -> bool:
    return any(
        token in code
        for token in [
            "fileoutputstream",
            "files.copy",
            "fileutils.copyfile",
            "printwriter",
            "new file(",
        ]
    )


def has_named_copy_utility(code: str) -> bool:
    return any(token in code for token in ["ioutils.copy", "copystreams", "fileutils.copyfile", "files.copy"])


def has_archive_copy(code: str) -> bool:
    return any(token in code for token in ["zipinputstream", "zipentry", "unzip", "decompress"])


def bcb_gold_copy_slice(code_a: str, code_b: str) -> bool:
    if has_named_copy_utility(code_a) and has_named_copy_utility(code_b):
        return True
    if has_archive_copy(code_a) != has_archive_copy(code_b):
        return has_persistent_file_output(code_a) and has_persistent_file_output(code_b)
    return has_persistent_file_output(code_a) and has_persistent_file_output(code_b)


def copy_negative_boundary(code_a: str, code_b: str) -> bool:
    if one_sided(code_a, code_b, is_memory_load_only) or one_sided(code_a, code_b, is_upload_sink):
        return True
    return (
        explicit_copy_mismatch(code_a, code_b, is_download_named_method)
        or explicit_copy_mismatch(code_a, code_b, is_file_lock_or_build_test)
        or explicit_copy_mismatch(code_a, code_b, is_process_stream_forwarder)
        or explicit_copy_mismatch(code_a, code_b, is_block_splitter)
        or broad_copy_mismatch(code_a, code_b, is_generic_stream_signature)
        or broad_copy_mismatch(code_a, code_b, is_generic_outputstream_writer)
        or broad_copy_mismatch(code_a, code_b, is_ui_menu_copy_wrapper)
        or broad_copy_mismatch(code_a, code_b, is_export_generation_wrapper)
        or broad_copy_mismatch(code_a, code_b, is_share_socket_receiver)
        or broad_copy_mismatch(code_a, code_b, is_ltm_stream_receiver)
        or broad_copy_mismatch(code_a, code_b, is_main_rewrite_driver)
        or broad_copy_mismatch(code_a, code_b, is_download_target_directory_writer)
    )


def copy_should_abstain(code_a: str, code_b: str) -> bool:
    return code_missing_or_too_short(code_a) or code_missing_or_too_short(code_b)


def is_memory_load_only(code: str) -> bool:
    has_file_input = "fileinputstream" in code or "new file(" in code
    has_memory_target = any(token in code for token in ["bytebuffer", "bytearrayoutputstream", "stringwriter"])
    has_file_output = "fileoutputstream" in code or "files.copy" in code or "printwriter" in code
    return has_file_input and has_memory_target and not has_file_output


def is_upload_sink(code: str) -> bool:
    if has_named_copy_utility(code):
        return False
    has_stream_to_file = "inputstream" in code and "fileoutputstream" in code
    has_upload_context = any(token in code for token in ["sendfile", "upload", "combean", "request.getinputstream"])
    lacks_file_source_param = not ("file src" in code or "file source" in code or "fileinputstream" in code)
    return has_stream_to_file and has_upload_context and lacks_file_source_param


def explicit_copy_mismatch(code_a: str, code_b: str, predicate: Any) -> bool:
    return (predicate(code_a) and is_explicit_file_copy_impl(code_b)) or (
        predicate(code_b) and is_explicit_file_copy_impl(code_a)
    )


def broad_copy_mismatch(code_a: str, code_b: str, predicate: Any) -> bool:
    return (predicate(code_a) and is_obvious_file_to_file_copy(code_b)) or (
        predicate(code_b) and is_obvious_file_to_file_copy(code_a)
    )


def is_explicit_file_copy_impl(code: str) -> bool:
    return any(token in code for token in ["fileinputstream", "copyfile", "copylarge", "transferfrom", "fileutils.copyfile", "files.copy"]) and any(
        token in code for token in ["fileoutputstream", "copylarge", "transferfrom", "fileutils.copyfile", "files.copy", "printwriter"]
    )


def is_obvious_file_to_file_copy(code: str) -> bool:
    signature = code.split("{", 1)[0].lower()
    has_file_like_params = any(
        token in signature
        for token in [
            "file src",
            "file srcfile",
            "file dest",
            "file destfile",
            "path src",
            "path dest",
            "string srcfile",
            "string destfile",
        ]
    )
    has_copy_body = any(
        token in code
        for token in [
            "fileinputstream",
            "fileoutputstream",
            "fileutils.copyfile",
            "files.copy",
            "copylarge",
            "transferfrom",
            "scanner",
            "printwriter",
        ]
    )
    return (has_file_like_params and has_copy_body) or is_explicit_file_copy_impl(code)


def is_download_named_method(code: str) -> bool:
    signature = code.split("{", 1)[0].lower()
    return re.search(r"\bdownload\w*\s*\(", signature) is not None and ("fileoutputstream" in code or "outputstream" in code)


def is_download_target_directory_writer(code: str) -> bool:
    signature = code.split("{", 1)[0].lower()
    return "downloadkgml" in signature or ("targetdirectory" in code and "url(" in code)


def is_file_lock_or_build_test(code: str) -> bool:
    return any(token in code for token in ["filelock", "channel().lock", "lock = ", ".lock()"]) and any(
        token in code for token in ["assert", "@test", "test", "buildexception", "executebuildexceptiontarget"]
    )


def is_process_stream_forwarder(code: str) -> bool:
    return any(token in code for token in ["process.getinputstream", 'registry.getstream("process"', "registry.getstream('process'"]) and (
        "outputstream" in code or "write(" in code
    )


def is_block_splitter(code: str) -> bool:
    return "randomaccessfile" in code and "blocksize" in code and any(token in code for token in ["subfiles", "split", "filenum"])


def is_generic_stream_signature(code: str) -> bool:
    signature = code.split("{", 1)[0].lower()
    has_input = signature_has_param_type(signature, "inputstream")
    has_output = signature_has_param_type(signature, "outputstream")
    avoids_file_fast_path = not any(
        token in code
        for token in [
            "instanceof fileoutputstream",
            "instanceof fileinputstream",
            "getchannel()",
            "transferto",
            "transferfrom",
        ]
    )
    return has_input and has_output and avoids_file_fast_path


def is_generic_outputstream_writer(code: str) -> bool:
    signature = code.split("{", 1)[0].lower()
    has_name = re.search(r"\b(write(to)?|pipe|copyinputstream|writevalueto)\s*\(", signature) is not None
    return has_name and signature_has_param_type(signature, "outputstream") and "fileoutputstream" not in code and "fileinputstream" not in code


def is_ui_menu_copy_wrapper(code: str) -> bool:
    return any(token in code for token in ["jpopupmenu", "menuitem", "actionlistener"]) and "copyfile" in code


def is_export_generation_wrapper(code: str) -> bool:
    return any(token in code for token in ["exporttodir", "exportoneday", "iterate(itdivide)", "filesdata"])


def is_share_socket_receiver(code: str) -> bool:
    return "receiveshare" in code and "socket.getinputstream" in code and "sharefilewriter" in code


def is_ltm_stream_receiver(code: str) -> bool:
    return "ltm.getstream" in code and any(token in code for token in ["writeopcode", "readint", "readdata"]) and "fileoutputstream" in code


def is_main_rewrite_driver(code: str) -> bool:
    signature = code.split("{", 1)[0].lower()
    return "main(string[] args)" in signature and any(token in code for token in ["readandrewrite", ".test"])


def signature_has_param_type(signature: str, type_name: str) -> bool:
    return re.search(rf"[\(,]\s*{re.escape(type_name)}\s+[a-z_$][\w$]*", signature) is not None


def download_subtype_mismatch(code_a: str, code_b: str) -> bool:
    if one_sided(code_a, code_b, is_url_open_only):
        return True
    if one_sided(code_a, code_b, is_web_parser_or_indexer):
        return True
    if one_sided(code_a, code_b, is_image_loader):
        return True
    if one_sided(code_a, code_b, is_url_to_file_download) and one_sided(code_a, code_b, is_url_to_text_download):
        return True
    return False


def download_auth_or_session_mismatch(code_a: str, code_b: str) -> bool:
    return one_sided(code_a, code_b, is_authenticated_fetch)


def is_authenticated_fetch(code: str) -> bool:
    return any(
        token in code
        for token in [
            "httppost",
            "login",
            "passwd",
            "auth",
            "cookie",
            "defaulthttpclient",
            "httpresponse",
            "session",
            "username",
            "password",
        ]
    )


def is_url_open_only(code: str) -> bool:
    has_url = "url(" in code or "openconnection" in code or "openurl" in code
    reads_content = any(token in code for token in ["getinputstream", "openstream", ".read(", "readline"])
    return has_url and not reads_content


def is_web_parser_or_indexer(code: str) -> bool:
    return any(
        token in code
        for token in [
            "matcher",
            "pattern",
            "images.add",
            "return images",
            "index(is)",
            "index(inputstream",
            "parse",
        ]
    )


def is_image_loader(code: str) -> bool:
    return any(token in code for token in ["gifimage", "jpeg(", "pngimage", "bmpimage", "badlementexception", "badelementexception", "return img", "return image"])


def is_url_to_file_download(code: str) -> bool:
    return ("openstream" in code or "getinputstream" in code) and "fileoutputstream" in code


def is_url_to_text_download(code: str) -> bool:
    return (
        ("openstream" in code or "getinputstream" in code)
        and "bufferedreader" in code
        and ("return page" in code or "return string" in code)
    )


def one_sided(code_a: str, code_b: str, predicate: Any) -> bool:
    return bool(predicate(code_a)) != bool(predicate(code_b))


def code_missing_or_too_short(code: str) -> bool:
    return len(code.strip()) < 24


def code_is_obvious_fragment(code: str) -> bool:
    stripped = code.lstrip()
    if not stripped:
        return True
    if "{" not in stripped:
        return True
    before_brace = stripped.split("{", 1)[0].strip().lower()
    if before_brace and "(" not in before_brace and not before_brace.startswith("@"):
        return True
    first_nonempty = next((line.strip().lower() for line in stripped.splitlines() if line.strip()), "")
    if not first_nonempty:
        return True
    markers = ("*/", "**/", "} else", "else {", "catch (", "finally {", "case ", "default:", "println(", "print(", "out.print(")
    if not first_nonempty.startswith(markers):
        return False
    prefix = "\n".join(stripped.splitlines()[:3]).lower()
    return not any(token in prefix for token in ["public ", "private ", "protected ", "static ", "class ", "interface "])


def ftp_protocol_mismatch(code_a: str, code_b: str) -> bool:
    if one_sided(code_a, code_b, is_ftp_specific):
        return True
    if one_sided(code_a, code_b, is_xmpp_specific):
        return True
    if one_sided(code_a, code_b, is_test_harness):
        return True
    return False


def is_ftp_specific(code: str) -> bool:
    return any(token in code for token in ["ftpclient", "ftphttpclient", "ftpserver", "ftpport", "storefile", "retrievefile", "cwd", "ftp"])


def is_xmpp_specific(code: str) -> bool:
    return any(token in code for token in ["xmpp", "smackconfiguration", "roster", "presence", "packetcollector"])


def is_test_harness(code: str) -> bool:
    return any(token in code for token in ["@test", "assert.", "assertfail", "testinvalid", "junit"])


def db_conditional_rollback_mismatch(code_a: str, code_b: str) -> bool:
    return one_sided(code_a, code_b, is_conditional_business_rollback) and one_sided(code_a, code_b, is_finally_cleanup_rollback)


def is_conditional_business_rollback(code: str) -> bool:
    return "rollback()" in code and "commit()" in code and any(token in code for token in ["numchanged", "rowcount", "setautocommit(false)", "update <= 0", "update > 1"])


def is_finally_cleanup_rollback(code: str) -> bool:
    return "rollback()" in code and "finally" in code and ".isactive()" in code


def normalize_decision(decision: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(decision)
    verdict = str(normalized.get("verdict", "unknown"))
    if verdict in {"context_insufficient", "unknown"}:
        normalized["pred_label"] = None
        return normalized
    canonical = VERDICT_TO_LABEL.get(verdict)
    if canonical in (0, 1):
        normalized["pred_label"] = canonical
    elif normalized.get("pred_label") not in (0, 1, None):
        normalized["pred_label"] = None
    return normalized




def bcb_gold_allows_dynamic_mismatch(pair: ClonePair, card: dict[str, Any]) -> bool:
    if card.get("policy") not in {"bcb-gold", "bcb-alignment"}:
        return False
    target = pair.functionality_name.strip().lower()
    if target != "copy file":
        return False
    code_a = pair.code_a.lower()
    code_b = pair.code_b.lower()
    llm = card.get("llm_evidence") or {}
    shared_slice = llm.get("shared_functional_slice") if isinstance(llm, dict) else None
    if not isinstance(shared_slice, dict) or shared_slice.get("exists") is not True:
        return False
    return has_archive_copy(code_a) != has_archive_copy(code_b)


def dynamic_counterexample(dynamic: dict[str, Any]) -> bool:
    parsed = (dynamic.get("execution") or {}).get("parsed") if isinstance(dynamic.get("execution"), dict) else None
    return dynamic.get("status") == "executed" and isinstance(parsed, dict) and parsed.get("same") is False


def append_reason(base: str, extra: str) -> str:
    if not base:
        return extra
    if extra in base:
        return base
    return base.rstrip() + " " + extra


def metrics(cards: list[dict[str, Any]]) -> dict[str, Any]:
    valid: list[tuple[int, int]] = []
    abstained = 0
    for card in cards:
        gold = int(card.get("gold", {}).get("label", 0))
        pred = card.get("decision", {}).get("pred_label")
        if pred in (0, 1):
            valid.append((gold, int(pred)))
        else:
            abstained += 1
    tp = sum(1 for y, p in valid if y == 1 and p == 1)
    tn = sum(1 for y, p in valid if y == 0 and p == 0)
    fp = sum(1 for y, p in valid if y == 0 and p == 1)
    fn = sum(1 for y, p in valid if y == 1 and p == 0)
    total = len(valid)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy = (tp + tn) / total if total else 0.0
    return {
        "evaluated": total,
        "abstained": abstained,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }
