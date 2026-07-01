"""Offline tests for the LLM-direct fallback on execution failure.

Uses a stub client so no real API calls are made: we only need to verify the
pipeline's ``_exec_fail`` routing (fall back vs abstain) and the marking.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from attest.config import DEFAULT
from attest.pipeline import _exec_fail
from attest.schemas import Pair, PairOutcome, Snippet, Verdict


class _StubClient:
    """Minimal stand-in for LLMClient.chat_json used by llm_direct_judge."""

    def __init__(self, clone: bool):
        self._clone = clone
        self.calls = 0

    def chat_json(self, messages, **kw):
        self.calls += 1
        return {"clone": self._clone, "confidence": 0.9, "reason": "stub"}


def _pair() -> Pair:
    return Pair(
        pair_id="t",
        a=Snippet(id="a", code="x", language="java"),
        b=Snippet(id="b", code="y", language="java"),
        label=1,
    )


def test_fallback_on_calls_llm_direct(tmp_path: Path):
    client = _StubClient(clone=True)
    outcome = PairOutcome(pair_id="t", verdict=Verdict.ERROR)
    r = _exec_fail(outcome, _pair(), DEFAULT, client, tmp_path, 0.0, "unrunnable")
    assert r.verdict == Verdict.CLONE
    assert r.extra["fallback"] == "llm_direct"
    assert r.extra["fallback_reason"] == "unrunnable"
    assert client.calls == 1


def test_fallback_on_respects_non_clone(tmp_path: Path):
    client = _StubClient(clone=False)
    outcome = PairOutcome(pair_id="t", verdict=Verdict.ERROR)
    r = _exec_fail(outcome, _pair(), DEFAULT, client, tmp_path, 0.0, "unrunnable")
    assert r.verdict == Verdict.NON_CLONE
    assert r.extra["fallback"] == "llm_direct"


def test_fallback_off_abstains(tmp_path: Path):
    client = _StubClient(clone=True)  # must NOT be consulted
    cfg = replace(DEFAULT, decision=replace(DEFAULT.decision, llm_fallback_on_exec_fail=False))
    outcome = PairOutcome(pair_id="t", verdict=Verdict.ERROR)
    r = _exec_fail(outcome, _pair(), cfg, client, tmp_path, 0.0, "unrunnable")
    assert r.verdict == Verdict.UNDECIDED_EXEC
    assert "fallback" not in r.extra
    assert client.calls == 0


def test_fallback_contract_aware_when_contract_present(tmp_path: Path):
    # When a Stage-1 contract exists, the post-Stage-1 fallback uses the
    # contract-aware judge (flagged "contract"), not the blind direct baseline.
    from attest.schemas import Contract, ObserveSpec

    contract = Contract(
        label_a="sum a list", label_b="sum a list", same_function=True,
        unified_signature="int[] -> int", observe=ObserveSpec(),
    )
    client = _StubClient(clone=True)
    outcome = PairOutcome(pair_id="t", verdict=Verdict.ERROR)
    r = _exec_fail(outcome, _pair(), DEFAULT, client, tmp_path, 0.0,
                   "could not make runnable: B", contract=contract)
    assert r.verdict == Verdict.CLONE
    assert r.extra["fallback"] == "contract"
    assert client.calls == 1
