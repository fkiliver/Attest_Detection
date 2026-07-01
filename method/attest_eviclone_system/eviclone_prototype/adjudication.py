from __future__ import annotations

import json
from typing import Any

from .dataset import ClonePair
from .evidence import VERDICT_TO_LABEL, append_reason


ADJUDICATION_SYSTEM_PROMPT = """
You are a BigCloneBench-oriented adjudicator for Java code clone detection.
Your job is not to reward strict behavioral equivalence only. Estimate the BCB-gold label convention while also catching obvious benchmark-negative subtype mismatches.
Return only JSON. Do not use markdown.
""".strip()


def should_adjudicate(
    card: dict[str, Any],
    *,
    mode: str = "focused",
    margin_low: float = 0.3,
    margin_high: float = 0.7,
) -> bool:
    if mode == "all":
        return True
    if mode == "none":
        return False

    decision = card.get("decision") or {}
    semantic = card.get("semantic_decision") or {}
    alignment = card.get("bcb_alignment") or {}
    llm = card.get("llm_evidence") or {}
    shared = llm.get("shared_functional_slice") if isinstance(llm, dict) else None
    slice_alignment = shared.get("bcb_target_alignment") if isinstance(shared, dict) else ""
    score = alignment.get("score")
    target = str((card.get("target") or {}).get("name") or "").lower()
    flags = " ".join(str(flag) for flag in (decision.get("risk_flags") or []))
    flags_lower = flags.lower()

    disagreement = decision.get("pred_label") != semantic.get("pred_label")
    margin_hit = isinstance(score, (float, int)) and margin_low <= float(score) <= margin_high
    secure_hash = "secure hash" in target
    boundary_guard = "boundary_guard" in flags_lower
    algorithm_risk = any(piece in flags_lower for piece in ["algorithm", "md5", "sha"])
    algorithm_risk = algorithm_risk or any(piece in flags for piece in ["算法", "哈希", "摘要"])

    if mode == "strict":
        return disagreement or margin_hit or secure_hash or boundary_guard or algorithm_risk

    if disagreement or margin_hit or secure_hash or boundary_guard:
        return True
    if any(piece in flags_lower for piece in ["mismatch", "different", "filter", "transform", "algorithm", "md5", "sha"]):
        return True
    if any(piece in flags for piece in ["算法", "不同", "转换", "过滤"]):
        return True
    if slice_alignment in {"partial", "unclear"} and decision.get("confidence", 0) < 0.9:
        return True
    return False


def build_adjudication_prompt(pair: ClonePair, card: dict[str, Any]) -> str:
    compact_card = {
        "pair_id": card.get("pair_id"),
        "target": card.get("target"),
        "gold_hidden": "do_not_assume",
        "current_decision": card.get("decision"),
        "semantic_decision": card.get("semantic_decision"),
        "bcb_alignment": summarize_alignment(card.get("bcb_alignment") or {}),
        "local_evidence": card.get("local_evidence"),
        "dynamic_evidence": card.get("dynamic_evidence") or {"status": "not_run"},
        "llm_evidence": summarize_llm(card.get("llm_evidence") or {}),
    }
    schema = {
        "pred_label": 1,
        "bcb_gold_verdict": "benchmark_supported_clone|benchmark_supported_non_clone|context_insufficient",
        "confidence": 0.0,
        "matched_bcb_pattern": "...",
        "counterevidence": ["..."],
        "reason": "...",
    }
    return (
        "Adjudicate this BCB pair. Use the target functionality as the benchmark task.\n"
        "BCB often marks pairs positive when both snippets contain the target functional slice, even if wrappers differ.\n"
        "But mark negative for clear subtype/algorithm/source-output mismatches, one-sided missing target behavior, or transformations that break the target semantics.\n"
        "For Copy File, distinguish persistent file/content-preserving copy from upload/download, parsing, filtering, encoding, archive construction, logging, tests, or memory-only copy.\n"
        "For Download From Web, distinguish remote HTTP/HTTPS retrieval from local classpath/file/jar resources, UI login/session wrappers, parsers, or incidental URL usage.\n"
        "For Secure Hash, different digest algorithms such as MD5 vs SHA-1/SHA-512 should be treated as benchmark-negative unless the BCB evidence strongly says algorithm-agnostic hashing.\n\n"
        "Evidence:\n"
        f"{json.dumps(compact_card, ensure_ascii=False, indent=2)}\n\n"
        "Return exactly this JSON schema:\n"
        f"{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        f"Code A:\n{pair.code_a}\n\n"
        f"Code B:\n{pair.code_b}\n"
    )


def summarize_alignment(alignment: dict[str, Any]) -> dict[str, Any]:
    return {
        "score": alignment.get("score"),
        "semantic_pred_label": alignment.get("semantic_pred_label"),
        "linear_score": alignment.get("linear_score"),
        "hard_memory_score": alignment.get("hard_memory_score"),
        "hard_memory_coverage": alignment.get("hard_memory_coverage"),
        "hard_memory_neighbors": alignment.get("hard_memory_neighbors", [])[:5],
        "top_neighbors": alignment.get("top_neighbors", [])[:5],
    }


def summarize_llm(llm: dict[str, Any]) -> dict[str, Any]:
    shared = llm.get("shared_functional_slice") if isinstance(llm, dict) else None
    return {
        "status": llm.get("status", "success") if llm else "not_run",
        "semantic_verdict": llm.get("semantic_verdict"),
        "bcb_gold_verdict": llm.get("bcb_gold_verdict"),
        "shared_functional_slice": shared,
        "wrapper_differences": llm.get("wrapper_differences", [])[:5],
        "semantic_risk_flags": llm.get("semantic_risk_flags", [])[:8],
    }


def apply_adjudication(
    card: dict[str, Any],
    adjudication: dict[str, Any],
    *,
    accept_confidence: float = 0.75,
) -> dict[str, Any]:
    updated = dict(card)
    normalized = normalize_adjudication(adjudication)
    updated["llm_adjudication"] = normalized
    pred = normalized.get("pred_label")
    confidence = float(normalized.get("confidence", 0.0) or 0.0)
    if pred not in (0, 1) or confidence < accept_confidence:
        return updated

    decision = dict(card.get("decision") or {})
    verdict = "benchmark_supported_clone" if pred == 1 else "benchmark_supported_non_clone"
    decision.update(
        {
            "verdict": verdict,
            "pred_label": pred,
            "confidence": round(confidence, 4),
            "rationale": append_reason(
                str(decision.get("rationale", "")),
                "LLM adjudication: " + str(normalized.get("reason", "")),
            ),
            "risk_flags": list(decision.get("risk_flags") or []) + ["llm_adjudication_override"],
            "recommended_next_step": "human_audit_optional",
        }
    )
    updated["decision"] = decision
    return updated


def normalize_adjudication(obj: dict[str, Any]) -> dict[str, Any]:
    result = dict(obj)
    verdict = str(result.get("bcb_gold_verdict") or result.get("verdict") or "")
    pred = result.get("pred_label", VERDICT_TO_LABEL.get(verdict))
    if verdict == "benchmark_supported_clone":
        pred = 1
    elif verdict == "benchmark_supported_non_clone":
        pred = 0
    if pred not in (0, 1):
        pred = None
    try:
        confidence = max(0.0, min(float(result.get("confidence", 0.0)), 1.0))
    except (TypeError, ValueError):
        confidence = 0.0
    result["pred_label"] = pred
    result["confidence"] = round(confidence, 4)
    return result
