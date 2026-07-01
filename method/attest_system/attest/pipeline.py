"""End-to-end pipeline: comprehend -> make runnable -> synth inputs -> execute.

Orchestrates the four stages for a single :class:`Pair`, writes all artifacts to
``runs/<pair_id>/`` for the paper's evidence trail, and returns a
:class:`PairOutcome`. When the pipeline cannot construct behavioral evidence
(a snippet can't be made runnable, no inputs synthesized, the toolchain is
missing, or execution yields no usable output), it falls back to the LLM-direct
judgment and flags the outcome (``extra['fallback'] == 'llm_direct'``). Set
``decision.llm_fallback_on_exec_fail = False`` to instead abstain with
``UNDECIDED_EXEC`` (useful for measuring the execution pipeline's raw coverage).

CLI:
    python -m attest.pipeline --pair A.java B.java [--label 1] [--docker]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

from .config import DEFAULT, Config
from .executors.base import Executor
from .executors.java_exec import JavaExecutor
from .llm import LLMClient
from .schemas import (
    Contract,
    Pair,
    PairOutcome,
    SideState,
    Snippet,
    Verdict,
)
from .stage1_comprehend import comprehend
from .stage2_make_runnable import make_runnable
from .stage3_synth_inputs import synthesize_inputs
from .stage4_execute_compare import execute_and_compare


def get_executor(language: str, config: Config) -> Executor:
    """Return the executor for a language (C/C++ added in a later task)."""
    if language == "java":
        return JavaExecutor(config)
    if language in ("c", "cpp"):
        from .executors.cpp_exec import CppExecutor  # local import; optional

        return CppExecutor(config)
    raise ValueError(f"no executor for language {language!r}")


def _exec_fail(
    outcome: PairOutcome,
    pair: Pair,
    config: Config,
    client: LLMClient,
    run_dir: Path,
    t0: float,
    reason: str,
    contract: "Contract | None" = None,
) -> PairOutcome:
    """Resolve a no-behavioral-evidence situation.

    By default (config.decision.llm_fallback_on_exec_fail) we do NOT abstain.
    When the pipeline already produced a Stage-1 contract, we use a
    contract-aware fallback judge (functional labels + same-function assessment +
    code) — strictly more information than the blind direct baseline. Only when
    no contract exists (failure before Stage 1) do we fall back to the blind
    direct judge. The outcome is flagged so executed vs fallback verdicts stay
    separable. With the flag off, we return the honest UNDECIDED_EXEC abstention.
    """
    if config.decision.llm_fallback_on_exec_fail:
        if contract is not None:
            from .prompts import fallback_contract_messages

            try:
                data = client.chat_json(
                    fallback_contract_messages(pair, contract),
                    tag=f"fallback-contract-{pair.pair_id}",
                    max_tokens=4096,
                )
                clone = bool(data.get("clone", False))
                conf = float(data.get("confidence", 0.0) or 0.0)
            except Exception:
                clone, conf = False, 0.0
            outcome.verdict = Verdict.CLONE if clone else Verdict.NON_CLONE
            outcome.reason = f"{reason}; contract fallback -> {outcome.verdict.value}"
            outcome.extra["fallback"] = "contract"
            outcome.extra["fallback_reason"] = reason
            outcome.extra["fallback_confidence"] = conf
        else:
            from .eval.baselines import llm_direct_judge

            dv = llm_direct_judge(pair, client)
            outcome.verdict = Verdict.CLONE if dv.clone else Verdict.NON_CLONE
            outcome.reason = f"{reason}; llm_direct fallback -> {outcome.verdict.value}"
            outcome.extra["fallback"] = "llm_direct"
            outcome.extra["fallback_reason"] = reason
            outcome.extra["fallback_confidence"] = dv.confidence
    else:
        outcome.verdict = Verdict.UNDECIDED_EXEC
        outcome.reason = f"{reason} (abstain)"
    _finalize(outcome, run_dir, t0, client)
    return outcome


def run_pair(
    pair: Pair,
    config: Config | None = None,
    client: LLMClient | None = None,
    n_inputs: int = 12,
    keep_dir: bool = True,
) -> PairOutcome:
    """Run the full pipeline for one pair and return its outcome."""
    config = config or DEFAULT
    client = client or LLMClient(config)
    run_dir = config.runs_dir / pair.pair_id
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()

    # Per-stage timing + token accounting (observation only; never affects the
    # verdict). stage_times: wall-clock seconds per stage. _usage0: client usage
    # snapshot at pair start (popped in _finalize to compute the per-pair delta).
    prof: dict[str, float] = {}
    _u0 = client.usage.snapshot()

    outcome = PairOutcome(pair_id=pair.pair_id, verdict=Verdict.ERROR)
    outcome.extra["stage_times"] = prof
    outcome.extra["_usage0"] = {
        "calls": _u0.calls, "prompt": _u0.prompt_tokens,
        "completion": _u0.completion_tokens, "total": _u0.total_tokens,
        "seconds": _u0.seconds,
    }

    # Both snippets must share a language for a single executor; mixed-language
    # pairs can't be executed here, so fall back to the LLM-direct judge.
    if pair.a.language != pair.b.language:
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=f"mixed languages: {pair.a.language} vs {pair.b.language}",
        )

    try:
        executor = get_executor(pair.a.language, config)
    except ValueError as e:
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=str(e),
        )

    status = executor.probe()
    if not status.available:
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=f"toolchain unavailable: {status.detail}",
        )

    # ----- Stage 1: comprehend + contract --------------------------------- #
    # Transient LLM failures (a network blip, a malformed JSON response) should
    # degrade to the fallback judgment, not surface as a bare ERROR verdict.
    _ts = time.monotonic()
    try:
        contract = comprehend(pair, client)
    except Exception as e:
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=f"stage 1 (comprehend) failed: {type(e).__name__}: {e}",
        )
    prof["t1_comprehend"] = round(time.monotonic() - _ts, 3)
    outcome.contract = contract.to_json()
    outcome.stage_reached = 1
    _dump(run_dir / "contract.json", contract.to_json())

    # Ablation: when labels are disabled, do NOT use the same-function judgment
    # to early-exit (the contract's input guidance is still needed to run, but we
    # don't let the label gate the decision).
    if not contract.same_function and not config.ablation.no_label:
        outcome.verdict = Verdict.NON_CLONE
        outcome.reason = "labels differ — different functions (early exit)"
        _finalize(outcome, run_dir, t0, client)
        return outcome

    # ----- Stage 2: make both runnable ------------------------------------ #
    _ts = time.monotonic()
    try:
        build_a = make_runnable(pair.a, contract, executor, client, config, run_dir / "A")
        build_b = make_runnable(pair.b, contract, executor, client, config, run_dir / "B")
    except Exception as e:
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=f"stage 2 (make runnable) failed: {type(e).__name__}: {e}",
            contract=contract,
        )
    prof["t2_make_runnable"] = round(time.monotonic() - _ts, 3)
    # pure compiler time (the rest of t2 is LLM generation/repair)
    prof["t2_compile"] = round(
        sum(c.duration_s for c in (build_a.compiled, build_b.compiled) if c) , 3
    )
    outcome.repair_attempts_a = build_a.attempts
    outcome.repair_attempts_b = build_b.attempts
    outcome.stage_reached = 2
    _save_source(run_dir / "A", build_a.source)
    _save_source(run_dir / "B", build_b.source)

    outcome.side_a_state = SideState.OK if build_a.ok else SideState.EXEC_FAIL
    outcome.side_b_state = SideState.OK if build_b.ok else SideState.EXEC_FAIL
    if not build_a.ok or not build_b.ok:
        bad = []
        if not build_a.ok:
            bad.append("A")
            _dump(run_dir / "A" / "diagnostics.txt", build_a.diagnostics, raw=True)
        if not build_b.ok:
            bad.append("B")
            _dump(run_dir / "B" / "diagnostics.txt", build_b.diagnostics, raw=True)
        # A snippet could not be made runnable: fall back to the LLM-direct judge
        # rather than abstaining (configurable).
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=f"could not make runnable: {', '.join(bad)}",
            contract=contract,
        )

    # Ablation: no_execution — decide from the textual similarity of the two
    # COMPLETED harnesses rather than running them. Isolates the contribution of
    # real execution from the completion step.
    if config.ablation.no_execution:
        from .eval.ablations import text_similarity_verdict

        verdict, sim = text_similarity_verdict(
            build_a.source, build_b.source, config.ablation.text_sim_threshold
        )
        outcome.verdict = verdict
        outcome.pass_rate = sim
        outcome.stage_reached = 2
        outcome.reason = f"no_execution ablation: text_sim={sim:.3f}"
        _finalize(outcome, run_dir, t0, client)
        return outcome

    # ----- Stage 3: synthesize shared inputs ------------------------------ #
    _ts = time.monotonic()
    try:
        batch = synthesize_inputs(contract, client, n=n_inputs)
    except Exception as e:
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=f"stage 3 (synthesize inputs) failed: {type(e).__name__}: {e}",
            contract=contract,
        )
    prof["t3_synth_inputs"] = round(time.monotonic() - _ts, 3)
    outcome.stage_reached = 3
    _dump(run_dir / "inputs.json", batch.to_inputs_json(contract.observe))

    if not batch.cases:
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason="no input cases synthesized",
            contract=contract,
        )

    # ----- Stage 4: execute + compare ------------------------------------- #
    _ts = time.monotonic()
    try:
        cmp = execute_and_compare(
            contract, batch,
            build_a.compiled, build_b.compiled,
            executor, client, config, run_dir,
            pair=pair,
        )
    except Exception as e:
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=f"stage 4 (execute/compare) failed: {type(e).__name__}: {e}",
            contract=contract,
        )
    prof["t4_execute_compare"] = round(time.monotonic() - _ts, 3)
    prof["t4_run"] = cmp.run_seconds  # pure harness execution within stage 4
    outcome.stage_reached = 4

    # Stage 4 could not produce usable behavioral evidence (a side ran but wrote
    # nothing usable). Fall back to the LLM-direct judge rather than abstaining.
    if cmp.verdict == Verdict.UNDECIDED_EXEC:
        outcome.pass_rate = cmp.pass_rate
        outcome.n_cases = cmp.n_cases
        outcome.comparisons = cmp.comparisons
        return _exec_fail(
            outcome, pair, config, client, run_dir, t0,
            reason=f"no usable execution output: {cmp.reason}",
            contract=contract,
        )

    outcome.verdict = cmp.verdict
    outcome.pass_rate = cmp.pass_rate
    outcome.n_cases = cmp.n_cases
    outcome.n_match = cmp.n_match
    outcome.comparisons = cmp.comparisons
    outcome.reason = cmp.reason

    _finalize(outcome, run_dir, t0, client)
    return outcome


# --------------------------------------------------------------------------- #
# artifact helpers
# --------------------------------------------------------------------------- #


def _finalize(
    outcome: PairOutcome, run_dir: Path, t0: float,
    client: "LLMClient | None" = None,
) -> None:
    outcome.extra["elapsed_s"] = round(time.monotonic() - t0, 2)
    u0 = outcome.extra.pop("_usage0", None)
    if client is not None and u0 is not None:
        cur = client.usage.snapshot()
        outcome.extra["tokens"] = {
            "calls": cur.calls - u0["calls"],
            "prompt": cur.prompt_tokens - u0["prompt"],
            "completion": cur.completion_tokens - u0["completion"],
            "total": cur.total_tokens - u0["total"],
            "llm_seconds": round(cur.seconds - u0["seconds"], 3),
        }
    _dump(run_dir / "outcome.json", outcome.to_json())


def _dump(path: Path, obj, raw: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if raw:
            path.write_text(str(obj), encoding="utf-8")
        else:
            path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def _save_source(side_dir: Path, source: str) -> None:
    side_dir.mkdir(parents=True, exist_ok=True)
    try:
        (side_dir / "Harness.generated.java").write_text(source, encoding="utf-8")
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _read_snippet(path: str, sid: str) -> Snippet:
    p = Path(path)
    code = p.read_text(encoding="utf-8")
    ext = p.suffix.lower()
    lang = {".java": "java", ".c": "c", ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp"}.get(ext, "java")
    return Snippet(id=sid, code=code, language=lang)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run Attest on one pair.")
    ap.add_argument("--pair", nargs=2, metavar=("A", "B"), required=True,
                    help="paths to the two snippet files")
    ap.add_argument("--pair-id", default="cli_pair")
    ap.add_argument("--label", type=int, default=None, help="ground-truth label (0/1)")
    ap.add_argument("--inputs", type=int, default=12, help="number of synthesized cases")
    ap.add_argument("--docker", action="store_true", help="run executions in Docker")
    args = ap.parse_args(argv)

    config = DEFAULT.with_docker(True) if args.docker else DEFAULT
    a = _read_snippet(args.pair[0], "A")
    b = _read_snippet(args.pair[1], "B")
    pair = Pair(pair_id=args.pair_id, a=a, b=b, label=args.label)

    client = LLMClient(config)
    outcome = run_pair(pair, config, client, n_inputs=args.inputs)

    print(json.dumps({
        "pair_id": outcome.pair_id,
        "verdict": outcome.verdict.value,
        "pass_rate": outcome.pass_rate,
        "n_match": outcome.n_match,
        "n_cases": outcome.n_cases,
        "side_a": outcome.side_a_state.value,
        "side_b": outcome.side_b_state.value,
        "reason": outcome.reason,
        "elapsed_s": outcome.extra.get("elapsed_s"),
    }, ensure_ascii=False, indent=2))
    print(client.cost_summary(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
