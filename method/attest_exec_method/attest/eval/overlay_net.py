"""Honest net F1: combine the FP-overlay and FN-overlay corrections.

Cherry-picking guard: the overlay must apply the SAME flip rule to both DSFM
error directions. We ran it on the 703 FP (gold=0) and the 612 FN (gold=1)
separately; here we apply BOTH sets of corrections to the single full-test
confusion matrix and recompute F1. This is the only defensible number, because a
gain on FP that is paid back by losses on FN (or vice versa) nets out here.

Corrections are read from the overlay reports' per-pair cards:
  * a card flips DSFM iff it is execution-grounded (or whatever the overlay's
    flip rule decided) and our_pred != base_pred;
  * the flip is correct iff our_pred == gold (a flip to the wrong value is a
    NEW error and is counted against us).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = {"tp": 18134, "fp": 703, "tn": 105301, "fn": 612}


def _f1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def apply_cards(tp, fp, tn, fn, cards):
    """Apply each applied flip to the confusion matrix, honestly.

    For every card with applied=True we move the pair between cells according to
    (gold, base_pred -> our_pred). A flip that lands on the wrong value creates a
    new error (e.g. a TN pair we wrongly flip to clone becomes an FP)."""
    flips = corrected = newly_wrong = 0
    for c in cards:
        if not c.get("applied"):
            continue
        flips += 1
        gold = c["gold"]; base = c["base_pred"]; ours = c["our_pred"]
        # remove pair from its base cell
        if base == 1 and gold == 1: tp -= 1
        elif base == 1 and gold == 0: fp -= 1
        elif base == 0 and gold == 0: tn -= 1
        elif base == 0 and gold == 1: fn -= 1
        # add to its new cell per our prediction
        if ours == 1 and gold == 1: tp += 1; corrected += 1
        elif ours == 1 and gold == 0: fp += 1; newly_wrong += 1
        elif ours == 0 and gold == 0: tn += 1; corrected += 1
        elif ours == 0 and gold == 1: fn += 1; newly_wrong += 1
    return tp, fp, tn, fn, flips, corrected, newly_wrong


def main():
    reports = [Path("runs/overlay_bcb_fp_gated.json"),
               Path("runs/overlay_bcb_fn_gated.json")]
    cards = []
    for rp in reports:
        if not rp.exists():
            print(f"missing {rp}; run that overlay first.", file=sys.stderr)
            return 1
        cards += json.load(open(rp, encoding="utf-8")).get("cards", [])

    tp, fp, tn, fn = BASE["tp"], BASE["fp"], BASE["tn"], BASE["fn"]
    tp, fp, tn, fn, flips, corrected, newly_wrong = apply_cards(tp, fp, tn, fn, cards)

    bp, br, bf = _f1(BASE["tp"], BASE["fp"], BASE["fn"])
    np_, nr, nf = _f1(tp, fp, fn)
    out = {
        "base": {"P": round(bp*100,3), "R": round(br*100,3), "F1": round(bf*100,3)},
        "overlay_net": {"P": round(np_*100,3), "R": round(nr*100,3), "F1": round(nf*100,3)},
        "delta_f1": round((nf-bf)*100, 3),
        "flips_applied": flips, "corrected": corrected, "newly_wrong": newly_wrong,
        "confusion_after": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "note": "FP+FN corrections applied with the SAME rule; net of both directions.",
    }
    Path("runs/overlay_bcb_net.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
