"""Offline tests for dataset loading and metrics."""

from __future__ import annotations

from pathlib import Path

import pytest

from attest.datasets.loader import DEFAULT_ROOT, load_pairs, resolve_name
from attest.eval.metrics import score, score_bool
from attest.schemas import PairOutcome, Verdict


def test_resolve_name_aliases():
    assert resolve_name("bcb") == "BigCloneBench"
    assert resolve_name("ojclone") == "OJClone"
    assert resolve_name("gcj") == "GCJ"
    assert resolve_name("GCJ") == "GCJ"


def test_score_bool_perfect():
    preds = [(True, 1), (False, 0), (True, 1), (False, 0)]
    m = score_bool(preds)
    assert m.precision == 1.0 and m.recall == 1.0 and m.f1 == 1.0
    assert m.accuracy == 1.0


def test_score_bool_mixed():
    # 1 tp, 1 fp, 1 fn, 1 tn
    preds = [(True, 1), (True, 0), (False, 1), (False, 0)]
    m = score_bool(preds)
    assert m.tp == 1 and m.fp == 1 and m.fn == 1 and m.tn == 1
    assert m.precision == 0.5 and m.recall == 0.5


def test_score_abstain_excluded_vs_negative():
    def outcome(v):
        return PairOutcome(pair_id="p", verdict=v)

    results = [
        (outcome(Verdict.CLONE), 1),         # tp
        (outcome(Verdict.UNDECIDED_EXEC), 1),  # abstain on a true clone
        (outcome(Verdict.NON_CLONE), 0),     # tn
    ]
    decided = score(results, abstain_as_negative=False)
    assert decided.abstained == 1
    assert decided.tp == 1 and decided.fn == 0  # abstain excluded
    assert abs(decided.abstain_rate - 1 / 3) < 1e-9

    as_neg = score(results, abstain_as_negative=True)
    assert as_neg.fn == 1  # abstain on a true clone now counts as a miss


@pytest.mark.skipif(not DEFAULT_ROOT.exists(), reason="dataset root not present")
def test_load_pairs_bcb_smoke():
    pairs = load_pairs("bcb", limit=6, balanced=True, seed=1, max_code_chars=4000)
    assert len(pairs) == 6
    assert all(p.a.language == "java" and p.b.language == "java" for p in pairs)
    assert {p.label for p in pairs} <= {0, 1}
    # balanced: roughly half clones
    assert sum(1 for p in pairs if p.label == 1) == 3


@pytest.mark.skipif(not DEFAULT_ROOT.exists(), reason="dataset root not present")
def test_load_pairs_ojclone_is_c():
    pairs = load_pairs("ojclone", limit=4, seed=2, max_code_chars=4000)
    assert len(pairs) == 4
    assert all(p.a.language == "c" for p in pairs)
