"""Stage 4 — execute both harnesses on the shared inputs and compare.

Runs A and B against the same ``inputs.json``, aligns their results by case id,
erases harmless differences with rule-based normalization, asks the LLM diff
explainer to adjudicate any residual difference as real-vs-cosmetic, then
computes a pass rate and a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import Config
from .executors.base import CompileResult, Executor
from .llm import LLMClient
from .normalize import (
    CaseDiff,
    compare_result,
    diff_payload,
    results_by_id,
)
from .prompts import stage4_adjudicate_messages, stage4_diff_messages
from .schemas import (
    CaseComparison,
    Contract,
    InputBatch,
    ObserveMode,
    Pair,
    Verdict,
)


@dataclass
class CompareOutcome:
    verdict: Verdict
    pass_rate: float
    n_cases: int
    n_match: int
    comparisons: list[CaseComparison]
    reason: str = ""
    run_seconds: float = 0.0  # wall-clock spent actually running both harnesses


def _write_inputs(path: Path, batch: InputBatch, contract: Contract) -> None:
    import json

    path.write_text(
        json.dumps(batch.to_inputs_json(contract.observe), ensure_ascii=False),
        encoding="utf-8",
    )


def execute_and_compare(
    contract: Contract,
    batch: InputBatch,
    compiled_a: CompileResult,
    compiled_b: CompileResult,
    executor: Executor,
    client: LLMClient,
    config: Config,
    run_dir: Path,
    pair: "Pair | None" = None,
) -> CompareOutcome:
    run_dir.mkdir(parents=True, exist_ok=True)
    inputs_path = run_dir / "inputs.json"
    _write_inputs(inputs_path, batch, contract)

    res_a = executor.run(compiled_a, inputs_path)
    res_b = executor.run(compiled_b, inputs_path)
    run_secs = round((res_a.duration_s or 0.0) + (res_b.duration_s or 0.0), 3)

    # Persist raw outputs for the evidence trail.
    _dump(run_dir / "outputs_a.json", res_a.outputs)
    _dump(run_dir / "outputs_b.json", res_b.outputs)

    if not res_a.produced_output or not res_b.produced_output:
        # One side ran but produced nothing usable — treat as an execution
        # failure of that side (the pipeline maps this to UNDECIDED_EXEC).
        why = []
        if not res_a.produced_output:
            why.append(f"A: {res_a.error or 'no output'}")
        if not res_b.produced_output:
            why.append(f"B: {res_b.error or 'no output'}")
        return CompareOutcome(
            verdict=Verdict.UNDECIDED_EXEC,
            pass_rate=0.0,
            n_cases=len(batch.cases),
            n_match=0,
            comparisons=[],
            reason="; ".join(why),
            run_seconds=run_secs,
        )

    a_by_id = results_by_id(res_a.outputs)
    b_by_id = results_by_id(res_b.outputs)

    unordered = _wants_unordered(contract)
    text_mode = _is_text_observation(contract)

    comparisons: list[CaseComparison] = []
    residual: list[CaseDiff] = []
    ood_ids: set[str] = set()
    for case in batch.cases:
        cid = case.id
        is_ood = str(case.kind).startswith("ood_")
        if is_ood:
            ood_ids.add(cid)
        ra, rb = a_by_id.get(cid), b_by_id.get(cid)
        match, reason = compare_result(
            ra, rb, config.decision, unordered=unordered, text_mode=text_mode
        )
        if is_ood:
            reason = "[out-of-domain probe] " + reason
        comp = CaseComparison(
            id=cid, match=match, reason=reason,
            a_repr=_brief(ra), b_repr=_brief(rb),
        )
        comparisons.append(comp)
        # Only in-domain mismatches are sent to the explainer / count toward the
        # verdict; out-of-domain probes are recorded as evidence but don't decide.
        if not match and not is_ood:
            residual.append(CaseDiff(id=cid, a=ra, b=rb))

    # Hand residual differences to the LLM explainer; it may reclassify some as
    # cosmetic (representation-only), recovering precision the fixed rules missed.
    # Ablation: when no_diff_explainer is set, any residual difference stands as
    # a mismatch (no LLM adjudication).
    if residual and not config.ablation.no_diff_explainer:
        _explain_residual(residual, comparisons, contract, client)

    # The verdict is computed over IN-DOMAIN cases only: inputs the code was meant
    # to handle. Out-of-domain probes are kept in `comparisons` for the evidence
    # trail but excluded from the pass-rate (they would otherwise manufacture
    # spurious non-clone verdicts on inputs outside the contract's stated domain).
    in_domain = [c for c in comparisons if c.id not in ood_ids]
    scored = in_domain if in_domain else comparisons  # fall back if all were ood
    n = len(scored)
    n_match = sum(1 for c in scored if c.match)
    pass_rate = (n_match / n) if n else 0.0

    theta = config.decision.pass_rate_theta
    floor = config.decision.adjudicate_floor
    adjudicated = False
    if n > 0 and pass_rate >= theta:
        verdict = Verdict.CLONE
    elif (
        pair is not None
        and n > 0
        and floor <= pass_rate < theta
        and not config.ablation.no_diff_explainer
    ):
        # Partial agreement: the snippets match on a substantial fraction but
        # diverge on some in-domain inputs. Hand the code + concrete divergences
        # to the LLM adjudicator for a holistic call, instead of auto-non-clone.
        # This recovers same-task clones whose divergence is an incidental bug or
        # a narrower input-domain check.
        verdict = _adjudicate(
            pair, contract, pass_rate, n, scored, client
        )
        adjudicated = True
    else:
        verdict = Verdict.NON_CLONE
    n_ood = len(ood_ids)
    reason = f"pass_rate={pass_rate:.3f} vs theta={theta}"
    if adjudicated:
        reason += f"; LLM adjudicated -> {verdict.value}"
    if n_ood:
        reason += f" (scored {n} in-domain; {n_ood} out-of-domain probes excluded)"
    return CompareOutcome(
        verdict=verdict,
        pass_rate=pass_rate,
        n_cases=n,
        n_match=n_match,
        comparisons=comparisons,
        reason=reason,
        run_seconds=run_secs,
    )


def _adjudicate(
    pair: Pair,
    contract: Contract,
    pass_rate: float,
    n_cases: int,
    scored: list[CaseComparison],
    client: LLMClient,
) -> Verdict:
    """LLM holistic clone judgment from code + concrete divergent behaviors."""
    divergences = [
        {"id": c.id, "a": c.a_repr, "b": c.b_repr, "note": c.reason[:120]}
        for c in scored if not c.match
    ][:20]
    try:
        data = client.chat_json(
            stage4_adjudicate_messages(pair, contract, pass_rate, n_cases, divergences),
            tag=f"stage4-adjudicate-{pair.pair_id}",
            max_tokens=4096,
        )
    except Exception:
        # On adjudicator failure, fall back to the conservative pass-rate verdict.
        return Verdict.NON_CLONE
    return Verdict.CLONE if bool(data.get("clone", False)) else Verdict.NON_CLONE


def _explain_residual(
    residual: list[CaseDiff],
    comparisons: list[CaseComparison],
    contract: Contract,
    client: LLMClient,
) -> None:
    payload = [
        {"id": d.id, **diff_payload(d.a, d.b)} for d in residual
    ]
    try:
        data = client.chat_json(
            stage4_diff_messages(contract, payload),
            tag="stage4-diff",
            max_tokens=8192,
        )
    except Exception:
        return  # keep the conservative rule-based verdict on explainer failure
    verdicts = {
        str(v.get("id")): v
        for v in data.get("verdicts", [])
        if isinstance(v, dict)
    }
    comp_by_id = {c.id: c for c in comparisons}
    for cid, v in verdicts.items():
        comp = comp_by_id.get(cid)
        if comp is None:
            continue
        real = bool(v.get("real_difference", True))
        if not real:
            # explainer says cosmetic -> count as a match
            comp.match = True
            comp.reason = "LLM: cosmetic difference — " + str(v.get("explanation", ""))[:300]
        else:
            comp.reason = "LLM: real difference — " + str(v.get("explanation", ""))[:300]


def _wants_unordered(contract: Contract) -> bool:
    # Heuristic: only relax ordering when the observation is a collection whose
    # order is plausibly irrelevant. We default to ordered (strict) and let the
    # LLM explainer catch ordering-only differences otherwise.
    return False


def _is_text_observation(contract: Contract) -> bool:
    """True if the observation is program text (stdout / a text file).

    For text observations, trailing whitespace / final-newline differences are
    representation-only and are normalized away during comparison.
    """
    obs = contract.observe
    if obs.mode == ObserveMode.ARTIFACT:
        return obs.artifact_kind in ("stdout", "file_text")
    return False


def _dump(path: Path, obj: Any) -> None:
    import json

    if obj is None:
        return
    try:
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def _brief(r: dict[str, Any] | None) -> Any:
    """A compact, size-bounded representation for the comparison log."""
    if r is None:
        return None
    if "error" in r:
        return {"error": (r["error"] or {}).get("type")}
    if r.get("void"):
        return {"void": True}
    ok = r.get("ok")
    if isinstance(ok, dict):
        if "__bytes__" in ok:
            return {"bytes_sha256": ok.get("sha256"), "len": ok.get("len")}
        if "__bytes_ref__" in ok:
            return {"bytes_sha256": ok["__bytes_ref__"].get("sha256")}
    return {"ok": ok}
