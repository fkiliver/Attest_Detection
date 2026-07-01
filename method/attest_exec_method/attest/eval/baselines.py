"""Baselines for comparison and ablation fallback.

The key baseline for the paper is **(c) LLM-direct**: ask the SAME backbone LLM
to judge clone/non-clone directly, with no execution. Because the backbone is
identical, any F1 gap between this and the full pipeline is attributable to the
pipeline design (execution + evidence), not to a stronger model.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..llm import LLMClient
from ..prompts import baseline_direct_messages
from ..schemas import Pair


@dataclass
class DirectVerdict:
    pair_id: str
    clone: bool
    confidence: float
    reason: str


def llm_direct_judge(pair: Pair, client: LLMClient) -> DirectVerdict:
    """Direct LLM clone judgment (no execution)."""
    try:
        data = client.chat_json(
            baseline_direct_messages(pair),
            tag=f"baseline-direct-{pair.pair_id}",
            max_tokens=2048,
        )
    except Exception as e:
        return DirectVerdict(pair.pair_id, False, 0.0, f"error: {e}")
    return DirectVerdict(
        pair_id=pair.pair_id,
        clone=bool(data.get("clone", False)),
        confidence=float(data.get("confidence", 0.0) or 0.0),
        reason=str(data.get("reason", ""))[:300],
    )
