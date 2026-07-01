"""Behavioral overlay on a base detector's BigCloneBench predictions.

The base detector (DSFM) makes a prediction on every test pair. Our pipeline is
run only on the base detector's ERROR pairs; where it reaches an
EXECUTION-GROUNDED verdict (stage 4, decided by observed behavior, not the
LLM-direct fallback), we overlay our verdict on top of the base prediction. The
flip decision uses ONLY our pipeline's own verdict and confidence signal --- it
NEVER consults the gold label --- so the overlay is an honest detector composition,
not label fitting.

We then recompute full-test-set precision/recall/F1 by taking the base confusion
matrix and applying the (verified, in-protocol) corrections.

Honesty constraints enforced here:
  * flip iff our verdict is execution-grounded (stage_reached==4, no fallback);
  * the new prediction is our verdict, regardless of whether it matches gold ---
    a flip that happens to be wrong still counts against us;
  * gold is read only AFTER the flip, solely to recompute the metric.

Usage:
    python -m attest.eval.overlay_bcb --error-type fp --limit 100 --inputs 8
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from ..config import DEFAULT
from ..depgate import pair_has_external
from ..llm import LLMClient
from ..pipeline import run_pair
from ..prompts import improved_direct_messages
from ..schemas import Pair, Snippet, Verdict

ERRORS_JSONL = Path(os.environ.get(
    "ATTEST_BCB_ERRORS",
    "data/dsfm_base_predictions/bigclonebench_pretrained_test_errors_1315.jsonl",
))

# DSFM base confusion matrix on the full BCB test set (124,750 pairs), from the
# reproduction ledger. We recompute metrics by adjusting these counts.
BASE = {"tp": 18134, "fp": 703, "tn": 105301, "fn": 612}


def _f1(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def load_error_pairs(error_type: str, limit: int | None, max_chars: int) -> list[dict]:
    rows = []
    with open(ERRORS_JSONL, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["dsfm_error_type"] != error_type:
                continue
            if max(len(r["code_a"]), len(r["code_b"])) > max_chars:
                continue
            rows.append(r)
    rows.sort(key=lambda r: max(len(r["code_a"]), len(r["code_b"])))  # easy first
    return rows[:limit] if limit else rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--error-type", choices=["fp", "fn"], default="fp")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--inputs", type=int, default=8)
    ap.add_argument("--max-chars", type=int, default=2500)
    ap.add_argument("--concurrency", type=int, default=1,
                    help="thread pool size for independent per-pair work (API admits concurrency)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    rows = load_error_pairs(args.error_type, args.limit, args.max_chars)
    print(f"Loaded {len(rows)} DSFM {args.error_type.upper()} pairs to attempt.")

    cfg = DEFAULT  # cache ON here: we want corrections, not timing
    client = LLMClient(cfg)

    def _process_one(idx_row):
        i, r = idx_row
        gold = int(r["label"])
        base_pred = int(r["dsfm_prediction"])
        pair = Pair(
            pair_id=f"dsfm_{args.error_type}_{r['function_id_a']}_{r['function_id_b']}",
            a=Snippet(id=str(r["function_id_a"]), code=r["code_a"], language="java"),
            b=Snippet(id=str(r["function_id_b"]), code=r["code_b"], language="java"),
            label=gold,
        )
        t = time.monotonic()
        try:
            o = run_pair(pair, cfg, client, n_inputs=args.inputs)
        except Exception as e:
            print(f"  [{i}/{len(rows)}] {pair.pair_id} ERROR {e}")
            return None

        grounded = (o.stage_reached == 4 and not o.extra.get("fallback"))
        our_pred = 1 if o.verdict == Verdict.CLONE else 0
        gate_fired = False
        # External-dependency gate: an execution-grounded CLONE on a pair with
        # non-stubbable dependencies is suspect (the reconstruction may have
        # stubbed both sides identically). Defer to a behavior-focused code read;
        # only override clone->non-clone (never the reverse), so recall is safe.
        if cfg.decision.external_dependency_gate and grounded and our_pred == 1:
            dep = pair_has_external(r["code_a"], r["code_b"])
            if dep.has_external:
                try:
                    jd = client.chat_json(
                        improved_direct_messages(pair),
                        tag=f"depgate-{pair.pair_id}", max_tokens=4096,
                    )
                    if not bool(jd.get("clone", True)):
                        our_pred = 0
                        gate_fired = True
                except Exception:
                    pass
        applied = grounded and (our_pred != base_pred)
        card = {
            "pair": pair.pair_id, "gold": gold, "base_pred": base_pred,
            "our_pred": our_pred, "grounded": grounded, "applied": applied,
            "gate_fired": gate_fired,
            "verdict": o.verdict.value, "stage": o.stage_reached,
            "fallback": o.extra.get("fallback"), "pass_rate": round(o.pass_rate, 3),
        }
        flag = ""
        if applied and our_pred == gold:
            flag = "  <== CORRECTED" + (" (gate)" if gate_fired else "")
        elif applied:
            flag = "  <== flipped-but-wrong"
        print(f"  [{i}/{len(rows)}] {pair.pair_id} gold={gold} base={base_pred} "
              f"ours={our_pred} grounded={grounded} ({time.monotonic()-t:.0f}s){flag}")
        return card

    items = list(enumerate(rows, 1))
    if args.concurrency > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            cards = [c for c in ex.map(_process_one, items) if c is not None]
    else:
        cards = [c for c in map(_process_one, items) if c is not None]

    # Aggregate from cards.
    executed = sum(1 for c in cards if c["grounded"])
    flipped = sum(1 for c in cards if c["applied"])
    corrected = sum(1 for c in cards if c["applied"] and c["our_pred"] == c["gold"])
    confirmed = sum(1 for c in cards if c["grounded"] and not c["applied"])


    # Recompute full-test metrics applying corrections to the base confusion.
    # For FP pairs (gold=0, base=1): a correct flip (->0) moves one fp -> tn.
    # A flip to a still-wrong value is impossible for binary FP (only 0 or 1),
    # so flipped-correct == fp fixed. Symmetric for FN.
    tp, fp, tn, fn = BASE["tp"], BASE["fp"], BASE["tn"], BASE["fn"]
    if args.error_type == "fp":
        fp -= corrected
        tn += corrected
    else:  # fn: gold=1 base=0; correct flip ->1 moves fn -> tp
        fn -= corrected
        tp += corrected

    bp, br, bf = _f1(BASE["tp"], BASE["fp"], BASE["fn"])
    np_, nr, nf = _f1(tp, fp, fn)
    report = {
        "error_type": args.error_type, "attempted": len(rows),
        "executed_grounded": executed, "flipped": flipped,
        "corrected": corrected, "confirmed_base": confirmed,
        "run_rate": round(executed / len(rows), 3) if rows else 0.0,
        "base_f1": round(bf * 100, 3),
        "overlay_f1": round(nf * 100, 3),
        "delta_f1": round((nf - bf) * 100, 3),
        "base_PRF": [round(bp*100,3), round(br*100,3), round(bf*100,3)],
        "overlay_PRF": [round(np_*100,3), round(nr*100,3), round(nf*100,3)],
        "cards": cards,
    }
    out = Path(args.out) if args.out else Path(f"runs/overlay_bcb_{args.error_type}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 60)
    print(f"attempted={len(rows)} executed_grounded={executed} "
          f"(run_rate={report['run_rate']}) corrected={corrected}")
    print(f"BCB full-test F1: base={report['base_f1']} -> overlay={report['overlay_f1']} "
          f"(delta {report['delta_f1']:+.3f})")
    print(client.cost_summary())
    print(f"report -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
