"""End-to-end correctness gate on the two real case-study pairs (LIVE).

These tests make real OpenAI-compatible LLM API calls and run the JDK, so they are marked
``live`` and skipped by default. Run explicitly with:

    pytest -m live tests/test_gate_e2e.py

They are the primary correctness gate (see the plan):
  1. Case 2284 (copyResource vs copyFromTo) -> CLONE, via destination-file bytes.
     GraphCodeBERT misclassifies this real BCB clone; execution gets it right.
  2. Anagram (full-Unicode vs ASCII-128) -> the pipeline must DETECT the hidden
     behavioral divergence on the non-ASCII case (one side returns a value, the
     other throws), confirmed real by the LLM diff explainer. We assert on the
     divergence detection, not the final pass-rate verdict (which is threshold-
     dependent and, under pass-rate-only semantics, remains CLONE).
"""

from __future__ import annotations

import pytest

from attest.config import DEFAULT
from attest.executors.java_exec import JAVA, JAVAC
from attest.llm import LLMClient
from attest.pipeline import run_pair
from attest.schemas import SideState, Verdict

from .case_fixtures import ANAGRAM, CASE_2284

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        JAVAC is None or JAVA is None,
        reason="host JDK (javac/java) not available via PATH or JAVA_HOME",
    ),
]


def test_case_2284_is_clone_via_execution():
    client = LLMClient(DEFAULT)
    outcome = run_pair(CASE_2284, DEFAULT, client, n_inputs=8)

    # Both sides must have been made runnable (the whole point vs jcoffee).
    assert outcome.side_a_state == SideState.OK, outcome.reason
    assert outcome.side_b_state == SideState.OK, outcome.reason
    assert outcome.stage_reached == 4

    # The behavioral evidence (matching dest bytes) should yield a clone verdict.
    assert outcome.verdict == Verdict.CLONE, (
        f"expected CLONE, got {outcome.verdict.value} "
        f"({outcome.n_match}/{outcome.n_cases}, {outcome.reason})"
    )
    assert outcome.pass_rate >= DEFAULT.decision.pass_rate_theta
    # The contract should have chosen an artifact (file bytes) observation.
    assert outcome.contract["observe"]["mode"] == "artifact"


def test_anagram_divergence_is_detected():
    client = LLMClient(DEFAULT)
    outcome = run_pair(ANAGRAM, DEFAULT, client, n_inputs=10)

    assert outcome.side_a_state == SideState.OK, outcome.reason
    assert outcome.side_b_state == SideState.OK, outcome.reason
    assert outcome.stage_reached == 4

    # The key assertion: at least one case must be a *real* divergence where one
    # side errored and the other returned a value — the hidden ASCII-only crash.
    diverged = [c for c in outcome.comparisons if not c.match]
    assert diverged, "expected at least one behavioral divergence, found none"

    def is_crash_vs_value(c) -> bool:
        a, b = c.a_repr or {}, c.b_repr or {}
        a_err = isinstance(a, dict) and "error" in a
        b_err = isinstance(b, dict) and "error" in b
        return a_err != b_err  # exactly one side threw

    assert any(is_crash_vs_value(c) for c in diverged), (
        "expected a crash-vs-value divergence (ASCII-only crash on non-ASCII), "
        f"got: {[(c.id, c.a_repr, c.b_repr) for c in diverged]}"
    )
