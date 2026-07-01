"""Efficiency profiling for the paper's RQ4 (Cost and coverage).

Runs a small balanced sample per dataset SEQUENTIALLY with the LLM cache
DISABLED, so per-stage wall-clock and token counts reflect real cost without
cache hits or cross-run API contention. Aggregates, per dataset:
  * per-stage wall-clock T1..T4 (+ pure compile / pure run sub-times),
  * share of time spent in LLM requests vs compile+execute,
  * LLM calls and tokens per pair,
  * coverage: fraction of pairs decided by execution (reached stage 4 without
    falling back), reconstruction success, and repair-iteration distribution.

Optionally (--concurrency K) re-runs the SAME sample with a thread pool to
measure the wall-clock speedup from concurrency (the API admits parallel calls),
supporting the paper's claim that wall-clock scales sub-linearly in #pairs.

Usage:
    python -m attest.eval.profile_efficiency --per-dataset 15 --inputs 8
    python -m attest.eval.profile_efficiency --per-dataset 12 --concurrency 4
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

from ..config import DEFAULT
from ..datasets.loader import load_pairs, resolve_name
from ..llm import LLMClient
from ..pipeline import run_pair
from ..schemas import Verdict

DATASETS = [
    ("bcb", {1, 2, 3, 4}),   # use reliable Type-1/2/3 positives
    ("ojclone", None),
    ("gcj", None),
]


def _mean(xs):
    return round(statistics.mean(xs), 2) if xs else 0.0


def _median(xs):
    return round(statistics.median(xs), 2) if xs else 0.0


def _aggregate(outcomes: list) -> dict:
    """Aggregate per-stage timing / tokens / coverage over a list of outcomes."""
    n = len(outcomes)
    # collect per-stage times (only present when the stage ran)
    keys = ["t1_comprehend", "t2_make_runnable", "t2_compile",
            "t3_synth_inputs", "t4_execute_compare", "t4_run"]
    stage_vals = {k: [] for k in keys}
    elapsed, calls, toks, llm_secs = [], [], [], []
    reached = {}
    executed = 0
    fallback = 0
    repairs = []
    for o in outcomes:
        st = o.extra.get("stage_times", {})
        for k in keys:
            if k in st:
                stage_vals[k].append(st[k])
        elapsed.append(o.extra.get("elapsed_s", 0.0))
        tk = o.extra.get("tokens", {})
        calls.append(tk.get("calls", 0))
        toks.append(tk.get("total", 0))
        llm_secs.append(tk.get("llm_seconds", 0.0))
        reached[o.stage_reached] = reached.get(o.stage_reached, 0) + 1
        if o.extra.get("fallback"):
            fallback += 1
        elif o.stage_reached == 4:
            executed += 1
        repairs.append(max(o.repair_attempts_a, o.repair_attempts_b))

    total_llm = sum(llm_secs)
    total_compile = sum(stage_vals["t2_compile"])
    total_run = sum(stage_vals["t4_run"])
    total_elapsed = sum(elapsed)
    return {
        "n": n,
        "coverage_executed": round(executed / n, 3) if n else 0.0,
        "n_executed": executed,
        "n_fallback": fallback,
        "stage_reached": dict(sorted(reached.items())),
        "elapsed_s": {"mean": _mean(elapsed), "median": _median(elapsed)},
        "per_stage_mean_s": {k: _mean(v) for k, v in stage_vals.items()},
        "llm_calls_per_pair": {"mean": _mean(calls), "median": _median(calls)},
        "tokens_per_pair": {"mean": _mean(toks), "median": _median(toks)},
        "time_share": {
            "llm": round(total_llm / total_elapsed, 3) if total_elapsed else 0.0,
            "compile": round(total_compile / total_elapsed, 3) if total_elapsed else 0.0,
            "run": round(total_run / total_elapsed, 3) if total_elapsed else 0.0,
        },
        "repair_iters": {
            "mean": _mean(repairs), "max": max(repairs) if repairs else 0,
            "distribution": {str(k): repairs.count(k) for k in sorted(set(repairs))},
        },
    }


def _run_sequential(pairs, cfg, client, n_inputs):
    outs = []
    for i, p in enumerate(pairs, 1):
        t = time.monotonic()
        try:
            o = run_pair(p, cfg, client, n_inputs=n_inputs)
        except Exception as e:
            print(f"    [{i}/{len(pairs)}] {p.pair_id} ERROR {e}")
            continue
        outs.append(o)
        print(f"    [{i}/{len(pairs)}] {p.pair_id} -> {o.verdict.value} "
              f"({time.monotonic()-t:.1f}s, stage{o.stage_reached})")
    return outs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Profile Attest efficiency.")
    ap.add_argument("--per-dataset", type=int, default=15)
    ap.add_argument("--inputs", type=int, default=8)
    ap.add_argument("--seed", type=int, default=99)
    ap.add_argument("--max-code-chars", type=int, default=2500)
    ap.add_argument("--concurrency", type=int, default=0,
                    help="if >0, also measure wall-clock speedup at this thread count")
    ap.add_argument("--out", default="runs/efficiency_profile.json")
    args = ap.parse_args(argv)

    # Cache OFF so timing is real; Docker for C/C++.
    cfg = replace(DEFAULT, llm=replace(DEFAULT.llm, cache_enabled=False))
    client = LLMClient(cfg)

    report = {"config": {"per_dataset": args.per_dataset, "inputs": args.inputs,
                          "seed": args.seed, "cache": False}, "datasets": {}}

    for name, ctypes in DATASETS:
        ds = resolve_name(name)
        pairs = load_pairs(name, split="test", limit=args.per_dataset, balanced=True,
                           seed=args.seed, max_code_chars=args.max_code_chars,
                           clone_types=ctypes)
        print(f"\n=== {ds}: {len(pairs)} pairs (sequential, cache off) ===")
        t_wall = time.monotonic()
        outs = _run_sequential(pairs, cfg, client, args.inputs)
        seq_wall = time.monotonic() - t_wall
        agg = _aggregate(outs)
        agg["sequential_wall_s"] = round(seq_wall, 1)
        agg["sequential_wall_per_pair_s"] = round(seq_wall / len(outs), 1) if outs else 0.0
        report["datasets"][ds] = agg

    # optional concurrency speedup on a fresh sample of the first dataset
    if args.concurrency > 0:
        name, ctypes = DATASETS[0]
        pairs = load_pairs(name, split="test", limit=args.per_dataset, balanced=True,
                           seed=args.seed + 1, max_code_chars=args.max_code_chars,
                           clone_types=ctypes)
        print(f"\n=== concurrency speedup on {resolve_name(name)} "
              f"({len(pairs)} pairs, K={args.concurrency}) ===")
        # sequential baseline
        t = time.monotonic()
        _run_sequential(pairs, cfg, client, args.inputs)
        seq = time.monotonic() - t
        # concurrent
        t = time.monotonic()
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            list(ex.map(lambda p: run_pair(p, cfg, client, n_inputs=args.inputs), pairs))
        conc = time.monotonic() - t
        report["concurrency"] = {
            "dataset": resolve_name(name), "n": len(pairs), "K": args.concurrency,
            "sequential_wall_s": round(seq, 1), "concurrent_wall_s": round(conc, 1),
            "speedup": round(seq / conc, 2) if conc else 0.0,
            "eff_per_pair_s": round(conc / len(pairs), 1) if pairs else 0.0,
        }
        print(f"  sequential={seq:.0f}s  concurrent={conc:.0f}s  "
              f"speedup={report['concurrency']['speedup']}x")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 60)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("=" * 60)
    print(client.cost_summary())
    print(f"profile -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
