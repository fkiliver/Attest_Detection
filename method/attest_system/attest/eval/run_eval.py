"""Batch evaluation runner.

Loads a dataset split, runs the chosen method(s) over a (sub)sample of pairs,
and prints a metrics table plus a JSON results file. Methods:
  * ``full``     — the full Attest pipeline (execution-based).
  * ``direct``   — the LLM-direct baseline (same backbone, no execution).
  * ``no-label`` / ``no-diff`` / ``no-exec`` — ablations of the full pipeline.

Usage:
    python -m attest.eval.run_eval --dataset bcb --limit 20
    python -m attest.eval.run_eval --dataset ojclone --limit 10 --methods full direct
    python -m attest.eval.run_eval --dataset bcb --limit 20 --methods full no-exec
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from ..config import DEFAULT, Config
from ..datasets.loader import load_pairs, resolve_name
from ..llm import LLMClient
from ..pipeline import run_pair
from ..schemas import Pair, PairOutcome, Verdict
from .baselines import llm_direct_judge
from .metrics import Metrics, score, score_bool

# method name -> (is_pipeline, config-mutator or None)
ABLATION_FLAGS = {
    "no-label": {"no_label": True},
    "no-diff": {"no_diff_explainer": True},
    "no-exec": {"no_execution": True},
}


def _run_pipeline_method(
    method: str, pairs: list[Pair], base: Config, client: LLMClient, n_inputs: int,
    concurrency: int = 1,
) -> list[tuple[PairOutcome, int]]:
    cfg = base
    if method in ABLATION_FLAGS:
        cfg = base.with_ablation(**ABLATION_FLAGS[method])

    def one(item):
        i, pair = item
        t0 = time.monotonic()
        try:
            outcome = run_pair(pair, cfg, client, n_inputs=n_inputs)
        except Exception as e:  # never let one pair kill the whole run
            outcome = PairOutcome(pair_id=pair.pair_id, verdict=Verdict.ERROR, reason=str(e))
        print(
            f"  [{method}] {i}/{len(pairs)} {pair.pair_id} -> "
            f"{outcome.verdict.value} (label={pair.label}, {time.monotonic()-t0:.1f}s)"
        )
        return (outcome, pair.label if pair.label is not None else -1)

    items = list(enumerate(pairs, 1))
    if concurrency > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            return list(ex.map(one, items))
    return [one(it) for it in items]


def _run_direct(
    pairs: list[Pair], client: LLMClient
) -> list[tuple[bool, int]]:
    preds: list[tuple[bool, int]] = []
    for i, pair in enumerate(pairs, 1):
        v = llm_direct_judge(pair, client)
        preds.append((v.clone, pair.label if pair.label is not None else -1))
        print(f"  [direct] {i}/{len(pairs)} {pair.pair_id} -> clone={v.clone} (label={pair.label})")
    return preds


def _print_table(rows: list[tuple[str, Metrics]]) -> None:
    hdr = f"{'method':<14}{'n':>5}{'P':>9}{'R':>9}{'F1':>9}{'Acc':>9}{'abst%':>8}"
    print("\n" + hdr)
    print("-" * len(hdr))
    for name, m in rows:
        print(
            f"{name:<14}{m.n:>5}{m.precision:>9.3f}{m.recall:>9.3f}"
            f"{m.f1:>9.3f}{m.accuracy:>9.3f}{m.abstain_rate*100:>8.1f}"
        )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evaluate Attest on a dataset.")
    ap.add_argument("--dataset", required=True, help="bcb | ojclone | gcj (or full name)")
    ap.add_argument("--split", default="test")
    ap.add_argument("--limit", type=int, default=20, help="number of pairs (balanced)")
    ap.add_argument("--inputs", type=int, default=10, help="synthesized cases per pair")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-code-chars", type=int, default=4000,
                    help="skip pairs with a snippet longer than this")
    ap.add_argument("--methods", nargs="+", default=["full"],
                    choices=["full", "direct", "no-label", "no-diff", "no-exec"])
    ap.add_argument("--docker", action="store_true")
    ap.add_argument("--concurrency", type=int, default=1,
                    help="thread pool size for per-pair pipeline runs")
    ap.add_argument("--clone-types", default=None,
                    help="restrict clone positives to these raw types, comma-sep "
                         "(BCB: 1,2,3,4 = Type-1/2/3 reliable; 5 = noisy WT). "
                         "e.g. --clone-types 1,2,3,4")
    ap.add_argument("--out", default=None, help="path to write JSON results")
    args = ap.parse_args(argv)

    base = DEFAULT.with_docker(True) if args.docker else DEFAULT
    client = LLMClient(base)

    clone_types = None
    if args.clone_types:
        clone_types = {int(x) for x in args.clone_types.split(",") if x.strip()}

    pairs = load_pairs(
        args.dataset, split=args.split, limit=args.limit, balanced=True,
        seed=args.seed, max_code_chars=args.max_code_chars, clone_types=clone_types,
    )
    ds = resolve_name(args.dataset)
    ct_note = f", clone_types={sorted(clone_types)}" if clone_types else ""
    print(f"Loaded {len(pairs)} pairs from {ds}/{args.split}{ct_note} "
          f"({sum(1 for p in pairs if p.label==1)} clone / "
          f"{sum(1 for p in pairs if p.label==0)} non-clone)")

    table: list[tuple[str, Metrics]] = []
    all_results: dict = {"dataset": ds, "split": args.split, "n_pairs": len(pairs), "methods": {}}

    for method in args.methods:
        print(f"\n=== method: {method} ===")
        if method == "direct":
            preds = _run_direct(pairs, client)
            m = score_bool(preds)
            table.append(("direct", m))
            all_results["methods"]["direct"] = {
                "metrics": m.as_dict(),
                "preds": [{"clone": p, "label": l} for p, l in preds],
            }
        else:
            results = _run_pipeline_method(method, pairs, base, client, args.inputs,
                                           concurrency=args.concurrency)
            m = score(results, abstain_as_negative=False)
            m_neg = score(results, abstain_as_negative=True)
            table.append((method, m))
            if m.abstained:
                table.append((f"{method}+abs-", m_neg))
            n_fallback = sum(
                1 for o, _ in results if o.extra.get("fallback") in ("llm_direct", "contract")
            )
            n_executed = sum(1 for o, _ in results if o.stage_reached == 4
                             and o.extra.get("fallback") is None)
            fb_rate = n_fallback / len(results) if results else 0.0
            print(f"  [{method}] executed={n_executed} fell_back={n_fallback} "
                  f"({fb_rate*100:.0f}%) abstained={m.abstained}")
            all_results["methods"][method] = {
                "metrics_decided": m.as_dict(),
                "metrics_abstain_as_negative": m_neg.as_dict(),
                "fallback_rate": round(fb_rate, 4),
                "n_fallback": n_fallback,
                "n_executed": n_executed,
                "per_pair": [
                    {"pair_id": o.pair_id, "verdict": o.verdict.value,
                     "label": l, "pass_rate": o.pass_rate,
                     "side_a": o.side_a_state.value, "side_b": o.side_b_state.value,
                     "fallback": o.extra.get("fallback")}
                    for o, l in results
                ],
            }

    _print_table(table)
    print("\n" + client.cost_summary())

    out_path = Path(args.out) if args.out else base.runs_dir / f"eval_{ds}_{args.split}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"results -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
