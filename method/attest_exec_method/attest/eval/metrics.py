"""Classification metrics with explicit abstention handling.

The pipeline can return UNDECIDED_EXEC (it could not construct runnable evidence).
We never silently fold that into a clone/non-clone bucket; instead we report the
abstention rate and compute P/R/F1 under two clearly-labeled policies:
  * ``decided``  — metrics over only the pairs that got a clone/non-clone verdict.
  * ``abstain_as_negative`` — abstentions counted as non-clone predictions
    (a conservative lower bound, comparable to baselines that always decide).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..schemas import PairOutcome, Verdict


@dataclass
class Metrics:
    n: int = 0
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0
    abstained: int = 0
    skipped_no_label: int = 0

    @property
    def precision(self) -> float:
        d = self.tp + self.fp
        return self.tp / d if d else 0.0

    @property
    def recall(self) -> float:
        d = self.tp + self.fn
        return self.tp / d if d else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def accuracy(self) -> float:
        d = self.tp + self.fp + self.tn + self.fn
        return (self.tp + self.tn) / d if d else 0.0

    @property
    def abstain_rate(self) -> float:
        return self.abstained / self.n if self.n else 0.0

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "accuracy": round(self.accuracy, 4),
            "abstain_rate": round(self.abstain_rate, 4),
            "tp": self.tp, "fp": self.fp, "tn": self.tn, "fn": self.fn,
            "abstained": self.abstained,
        }


def _update(m: Metrics, pred_clone: bool, label: int) -> None:
    if label == 1:
        if pred_clone:
            m.tp += 1
        else:
            m.fn += 1
    else:
        if pred_clone:
            m.fp += 1
        else:
            m.tn += 1


def score(
    results: list[tuple[PairOutcome, int]],
    *,
    abstain_as_negative: bool = False,
) -> Metrics:
    """Compute metrics from (outcome, label) pairs.

    Args:
        abstain_as_negative: if True, UNDECIDED_EXEC counts as a non-clone
            prediction; otherwise abstentions are excluded from P/R/F1.
    """
    m = Metrics()
    for outcome, label in results:
        m.n += 1
        v = outcome.verdict
        if v == Verdict.CLONE:
            _update(m, True, label)
        elif v == Verdict.NON_CLONE:
            _update(m, False, label)
        elif v == Verdict.UNDECIDED_EXEC:
            m.abstained += 1
            if abstain_as_negative:
                _update(m, False, label)
        else:  # ERROR — treat like an abstention for accounting
            m.abstained += 1
            if abstain_as_negative:
                _update(m, False, label)
    return m


def score_bool(preds: list[tuple[bool, int]]) -> Metrics:
    """Metrics for a baseline that always decides (bool prediction, label)."""
    m = Metrics()
    for pred, label in preds:
        m.n += 1
        _update(m, pred, label)
    return m
