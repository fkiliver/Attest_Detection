from __future__ import annotations

import json
from typing import Any

from .dataset import ClonePair


SYSTEM_PROMPT = """
You are an evidence builder for BigCloneBench / CodeXGLUE Java clone detection.
Your job is to produce a compact, auditable JSON evidence card for two Java methods.

Judging policy:
1. Distinguish strict semantic equivalence from the benchmark label convention.
2. BigCloneBench often accepts Type-1/2/3 clones: copied or near-copied code with renamed identifiers, reordered wrappers, added/deleted statements, or embedded common functional slices.
3. CodeXGLUE BigCloneBench pairs may not provide a target functionality name. In that case, estimate the benchmark clone label from code overlap, control/data-flow similarity, API sequence similarity, and shared algorithmic structure.
4. Do not overuse unknown/context_insufficient. If there is enough code to compare, give the most likely BCB label.
5. Use likely_non_clone when overlap is superficial: common Java boilerplate, unrelated APIs, unrelated control flow, different algorithms, or only generic names/types match.
6. For target-tagged BCB tasks, BCB-gold may accept a target functionality embedded inside a larger method; semantic-clean remains stricter.
7. Output JSON only.
""".strip()


def build_evidence_prompt(
    pair: ClonePair,
    local_evidence: dict[str, Any],
    *,
    policy: str,
    dynamic_evidence: dict[str, Any] | None = None,
) -> str:
    schema = {
        "inferred_bcb_functionality": {
            "name": "short benchmark-style functionality label, e.g. Copy File, Download From Web, Parse XML, Database Update, UI Event Handler",
            "confidence": 0.0,
            "evidence": "...",
        },
        "functionality_match": {
            "same_functionality": True,
            "confidence": 0.0,
            "reason": "...",
        },
        "core_intent_a": "...",
        "core_intent_b": "...",
        "shared_functional_slice": {
            "exists": True,
            "description": "...",
            "bcb_target_alignment": "aligned|partial|not_aligned|unclear",
        },
        "wrapper_differences": ["..."],
        "semantic_risk_flags": ["..."],
        "shared_test_intentions": [
            {
                "intent": "...",
                "input_shape": "...",
                "expected_observation": "return_value|exception|file_effect|state_change|trace",
                "why_discriminative": "...",
            }
        ],
        "counterexample_ideas": ["..."],
        "adapter_plan": {
            "can_align_interfaces": True,
            "strategy": "...",
            "missing_context": ["..."],
        },
        "dynamic_evidence_assessment": {
            "status": "supports_clone|supports_non_clone|inconclusive|not_available",
            "reason": "...",
        },
        "semantic_verdict": "behaviorally_supported_clone|likely_non_clone|context_insufficient|unknown",
        "semantic_confidence": 0.0,
        "semantic_reason": "...",
        "bcb_gold_verdict": "behaviorally_supported_clone|likely_non_clone|context_insufficient|unknown",
        "bcb_gold_confidence": 0.0,
        "bcb_gold_reason": "Estimate the BigCloneBench label convention, even when strict semantic equivalence is weak.",
        "verdict": "behaviorally_supported_clone|likely_non_clone|context_insufficient|unknown",
        "pred_label": 1,
        "confidence": 0.0,
        "reason": "...",
        "human_review_hint": "...",
    }
    if pair.functionality_name.strip().lower() == "codexglue bigclonebench":
        task_note = (
            "This is an original CodeXGLUE BigCloneBench pair. No target functionality metadata is available. "
            "First infer a benchmark-style shared functionality label from the two methods, then estimate whether the pair is a clone under the benchmark convention. "
            "The inferred label should be short and functional, such as Copy File, Download From Web, Secure Hash, Parse Config, Build XML Request, Database Query, or UI Event Handler. "
            "If both methods share the inferred functionality, the BCB-gold label may be clone even when their full business contexts differ. "
            "Treat substantial copied structure, API-call sequence similarity, renamed variables, and Type-3 edited clones as positive evidence. "
            "Also treat a shared meaningful feature family from Local static evidence, such as copy_file, download_web, secure_hash, ftp, or db_update_rollback, as strong BCB-positive evidence even when the surrounding business logic is different. "
            "BigCloneBench often labels such pairs as clones because they share the tagged functional slice, not because the whole methods are interchangeable. "
            "When the shared slice is meaningful and non-trivial, set bcb_gold_verdict to behaviorally_supported_clone unless there is clear evidence that the apparent functionality is only generic boilerplate. "
            "Treat unrelated control flow, unrelated APIs, different algorithms, and generic boilerplate-only overlap as negative evidence. "
            "If Local static evidence reports shared_feature_families, explain whether that shared slice is meaningful enough for BCB-gold. "
            "Avoid context_insufficient unless one snippet is unusable or truncated beyond comparison."
        )
    else:
        task_note = (
            "For bcb-alignment, output both semantic_verdict and bcb_gold_verdict. "
            "semantic_verdict means strict behavioral evidence; bcb_gold_verdict means the likely benchmark label convention."
        )
    return (
        f"Policy: {policy}\n"
        f"{task_note}\n\n"
        f"{pair.target_context()}\n\n"
        "Local static evidence:\n"
        f"{json.dumps(local_evidence, ensure_ascii=False, indent=2)}\n\n"
        "Dynamic execution evidence:\n"
        f"{json.dumps(dynamic_evidence or {'status': 'not_run'}, ensure_ascii=False, indent=2)}\n\n"
        "Output only the following JSON structure, with no Markdown:\n"
        f"{json.dumps(schema, ensure_ascii=False, indent=2)}\n\n"
        f"Code A:\n{pair.code_a}\n\n"
        f"Code B:\n{pair.code_b}\n"
    )
