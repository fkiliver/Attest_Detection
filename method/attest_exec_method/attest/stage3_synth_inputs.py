"""Stage 3 — synthesize one shared, intent-covering input batch.

The same batch is fed to both snippets so their observations are directly
comparable. The LLM is asked to cover normal inputs plus edges (empty, large,
non-ASCII, boundary), since those edges are where hidden behavioral divergences
hide (e.g. an ASCII-only implementation crashing on a non-ASCII char).
"""

from __future__ import annotations

from .config import Config
from .llm import LLMClient
from .prompts import stage3_messages
from .schemas import Contract, InputBatch, InputCase


def synthesize_inputs(
    contract: Contract,
    client: LLMClient,
    n: int = 12,
) -> InputBatch:
    # The reasoning model can occasionally exhaust the token budget and truncate
    # the JSON batch. Rather than lose the whole batch (which would force a
    # fallback), retry once asking for fewer, more compact cases.
    from .llm import LLMError

    try:
        data = client.chat_json(
            stage3_messages(contract, n=n),
            tag="stage3-inputs",
            max_tokens=16384,
        )
    except LLMError:
        data = client.chat_json(
            stage3_messages(contract, n=max(5, n // 2)),
            tag="stage3-inputs-retry",
            max_tokens=16384,
        )
    raw_cases = data.get("cases", [])
    cases: list[InputCase] = []
    seen_ids: set[str] = set()
    for i, c in enumerate(raw_cases):
        if not isinstance(c, dict):
            continue
        cid = str(c.get("id") or f"c{i}")
        # guarantee unique, stable ids (Stage 4 aligns A vs B by id)
        if cid in seen_ids:
            cid = f"{cid}_{i}"
        seen_ids.add(cid)
        args = c.get("args")
        if not isinstance(args, dict):
            args = {}
        cases.append(InputCase(id=cid, kind=str(c.get("kind", "normal")), args=args))
    return InputBatch(cases=cases)
