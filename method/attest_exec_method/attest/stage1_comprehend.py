"""Stage 1 — comprehend each snippet and define the unified test contract.

Produces a :class:`Contract`. If the LLM judges the two snippets to attempt
different functions, the pipeline can early-exit as Non-Clone without running
anything (the cheapest possible decision).
"""

from __future__ import annotations

from .llm import LLMClient
from .prompts import stage1_messages
from .schemas import Contract, Pair


def comprehend(pair: Pair, client: LLMClient) -> Contract:
    """Run Stage 1 and return the unified contract."""
    data = client.chat_json(
        stage1_messages(pair),
        tag=f"stage1-{pair.pair_id}",
        max_tokens=8192,
    )
    contract = Contract.from_json(data)
    # Defensive defaults: if the model omitted an observe spec, fall back to
    # return-mode rather than crashing downstream.
    if not contract.unified_signature:
        contract.unified_signature = f"{contract.label_a or 'function'} under test"
    return contract
