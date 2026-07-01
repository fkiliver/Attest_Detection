from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .adjudication import (
    ADJUDICATION_SYSTEM_PROMPT,
    apply_adjudication,
    build_adjudication_prompt,
    should_adjudicate,
)
from .alignment import (
    apply_bcb_alignment,
    evaluate_alignment_model,
    load_alignment_model,
    mine_hard_cases,
    save_alignment_model,
    train_alignment_model,
    tune_alignment_thresholds,
    tune_target_thresholds,
)
from .config import (
    DEFAULT_API_KEY_ENV,
    DEFAULT_BASE_MODEL,
    DEFAULT_BASE_PREDICTION_FORMAT,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_OUTPUT_DIR,
    LLMConfig,
    find_default_dataset,
)
from .dataset import ClonePair, load_pairs, summarize_pairs
from .dynamic_router import (
    apply_base_model_passthrough,
    attach_dynamic_route,
    base_prediction_for_pair,
    load_base_predictions,
    load_learned_dynamic_route_model,
    route_dynamic_execution,
)
from .evidence import apply_boundary_guards, build_local_card, merge_dynamic_evidence, merge_llm_evidence, metrics
from .executable_fusion import apply_executable_fusion
from .executor import evaluate_java_pair
from .llm import ChatClient, LLMError, extract_json_object, is_non_retryable_llm_error
from .pipeline_trace import attach_pipeline_trace
from .preference import (
    apply_preference_model,
    evaluate_preference_model,
    load_preference_model,
    save_preference_model,
    train_preference_model,
    tune_preference_model,
    tune_preference_target_thresholds,
)
from .prompts import SYSTEM_PROMPT, build_evidence_prompt
from .report import write_report
from .splits import load_split_pair_ids, parse_split_names, resolve_reference_sources, split_pairs_to_codexglue
from .storage import connect, get_or_create_run, upsert_card


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eviclone",
        description="EviClone prototype for BCB-oriented semantic clone evidence cards.",
    )
    parser.add_argument("--config", type=Path, default=None, help="reserved JSON config path")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_p = sub.add_parser("inspect", help="summarize a BCB JSONL dataset")
    add_dataset_args(inspect_p)
    add_subset_args(inspect_p)
    inspect_p.add_argument("--limit", type=int, default=0)

    run_p = sub.add_parser("run", help="generate evidence cards for one or more pairs")
    add_dataset_args(run_p)
    add_subset_args(run_p)
    run_p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR / "evidence_cards.jsonl")
    run_p.add_argument("--db-path", type=Path, default=DEFAULT_OUTPUT_DIR / "evidence.db")
    run_p.add_argument("--run-name", type=str, default="")
    run_p.add_argument("--limit", type=int, default=20)
    run_p.add_argument("--offset", type=int, default=0)
    run_p.add_argument("--pair-id", type=int, default=0)
    run_p.add_argument("--policy", choices=["bcb-gold", "semantic-clean", "bcb-alignment"], default="bcb-gold")
    run_p.add_argument("--with-dynamic", action="store_true", help="compile/run synthetic Java probes when possible")
    run_p.add_argument("--dynamic-mode", choices=["compile", "execute"], default="execute")
    run_p.add_argument("--dynamic-timeout-sec", type=int, default=8)
    add_dynamic_router_args(run_p)
    run_p.add_argument(
        "--with-llm-context-completion",
        action="store_true",
        help="use the LLM to complete missing Java snippet context before giving up on dynamic probes",
    )
    run_p.add_argument("--context-completion-retries", type=int, default=1)
    run_p.add_argument(
        "--context-source-dir",
        type=Path,
        default=None,
        help="optional directory for sidecar EviProbe.java sources produced by LLM context completion",
    )
    run_p.add_argument("--with-llm", action="store_true")
    run_p.add_argument("--llm-retries", type=int, default=2)
    run_p.add_argument("--report-path", type=Path, default=None)
    run_p.add_argument("--workers", type=int, default=0, help="parallel worker count; 0 means auto")
    run_p.add_argument("--commit-every", type=int, default=10, help="SQLite commit batch size")
    run_p.add_argument("--alignment-model", type=Path, default=None, help="BCB-alignment model JSON")
    add_llm_args(run_p)
    run_p.add_argument("--sleep-ms", type=int, default=0)

    show_p = sub.add_parser("show", help="print one evidence card as Markdown")
    add_dataset_args(show_p)
    add_subset_args(show_p)
    show_p.add_argument("--pair-id", type=int, required=True)
    show_p.add_argument("--policy", choices=["bcb-gold", "semantic-clean", "bcb-alignment"], default="bcb-gold")
    show_p.add_argument("--with-dynamic", action="store_true")
    show_p.add_argument("--dynamic-mode", choices=["compile", "execute"], default="execute")
    show_p.add_argument("--dynamic-timeout-sec", type=int, default=8)
    add_dynamic_router_args(show_p)
    show_p.add_argument("--with-llm-context-completion", action="store_true")
    show_p.add_argument("--context-completion-retries", type=int, default=1)
    show_p.add_argument("--context-source-dir", type=Path, default=None)
    show_p.add_argument("--with-llm", action="store_true")
    show_p.add_argument("--llm-retries", type=int, default=2)
    show_p.add_argument("--alignment-model", type=Path, default=None)
    add_llm_args(show_p)

    report_p = sub.add_parser("report", help="summarize an evidence-card JSONL file")
    report_p.add_argument("--input", type=Path, required=True)
    report_p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR / "report.md")

    rejudge_p = sub.add_parser("rejudge", help="rebuild decisions from saved cards without calling the LLM")
    add_dataset_args(rejudge_p)
    add_subset_args(rejudge_p)
    rejudge_p.add_argument("--input", type=Path, required=True)
    rejudge_p.add_argument("--output", type=Path, required=True)
    rejudge_p.add_argument("--report-path", type=Path, default=None)
    rejudge_p.add_argument("--policy", choices=["", "bcb-gold", "semantic-clean", "bcb-alignment"], default="")
    rejudge_p.add_argument("--alignment-model", type=Path, default=None)

    adjudicate_p = sub.add_parser("adjudicate", help="apply a focused LLM adjudicator to saved aligned cards")
    add_dataset_args(adjudicate_p)
    add_subset_args(adjudicate_p)
    adjudicate_p.add_argument("--input", type=Path, required=True)
    adjudicate_p.add_argument("--output", type=Path, required=True)
    adjudicate_p.add_argument("--report-path", type=Path, default=None)
    adjudicate_p.add_argument("--trigger-mode", choices=["strict", "focused", "all", "none"], default="strict")
    adjudicate_p.add_argument("--margin-low", type=float, default=0.3)
    adjudicate_p.add_argument("--margin-high", type=float, default=0.7)
    adjudicate_p.add_argument("--accept-confidence", type=float, default=0.75)
    adjudicate_p.add_argument("--llm-retries", type=int, default=2)
    adjudicate_p.add_argument("--workers", type=int, default=4)
    add_llm_args(adjudicate_p)

    fit_p = sub.add_parser("fit-align", help="train a lightweight BCB-alignment model from evidence cards")
    add_dataset_args(fit_p)
    add_subset_args(fit_p)
    fit_p.add_argument("--input", type=Path, action="append", required=True)
    fit_p.add_argument("--output", type=Path, required=True)
    fit_p.add_argument("--k", type=int, default=11)
    fit_p.add_argument("--threshold", type=float, default=0.5)
    fit_p.add_argument("--positive-threshold", type=float, default=None)
    fit_p.add_argument("--negative-threshold", type=float, default=None)
    fit_p.add_argument("--nb-weight", type=float, default=0.35)
    fit_p.add_argument("--linear-weight", type=float, default=0.5)
    fit_p.add_argument("--linear-epochs", type=int, default=40)
    fit_p.add_argument("--memory-k", type=int, default=7)
    fit_p.add_argument("--memory-weight", type=float, default=0.0)
    fit_p.add_argument("--memory-min-similarity", type=float, default=0.2)
    fit_p.add_argument("--decision-mode", choices=["replace", "selective", "fill-abstain"], default="replace")

    tune_p = sub.add_parser("tune-align", help="tune BCB-alignment thresholds on a validation evidence set")
    add_dataset_args(tune_p)
    add_subset_args(tune_p)
    tune_p.add_argument("--input", type=Path, action="append", required=True)
    tune_p.add_argument("--model", type=Path, required=True)
    tune_p.add_argument("--output", type=Path, required=True)
    tune_p.add_argument("--positive-grid", type=str, default="0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1")
    tune_p.add_argument("--negative-grid", type=str, default="0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1")
    tune_p.add_argument("--nb-weight-grid", type=str, default="0,0.1,0.2,0.35,0.5,0.65,0.8,1")
    tune_p.add_argument("--linear-weight-grid", type=str, default="0,0.25,0.5,0.75,1")
    tune_p.add_argument("--memory-weight-grid", type=str, default="0,0.1,0.25,0.5,0.75,1")
    tune_p.add_argument("--decision-modes", type=str, default="selective,fill-abstain")
    tune_p.add_argument("--target-calibration", action="store_true")
    tune_p.add_argument("--target-grid", type=str, default="0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1")
    tune_p.add_argument("--metric", choices=["f1", "accuracy", "precision", "recall"], default="f1")

    fit_pref_p = sub.add_parser("fit-pref", help="train a target-conditioned annotation preference model")
    add_dataset_args(fit_pref_p)
    add_subset_args(fit_pref_p)
    fit_pref_p.add_argument("--input", type=Path, action="append", required=True)
    fit_pref_p.add_argument("--output", type=Path, required=True)
    fit_pref_p.add_argument("--epochs", type=int, default=80)
    fit_pref_p.add_argument("--learning-rate", type=float, default=0.18)
    fit_pref_p.add_argument("--l2", type=float, default=0.0008)
    fit_pref_p.add_argument("--target-l2", type=float, default=0.004)
    fit_pref_p.add_argument("--target-min-examples", type=int, default=5)
    fit_pref_p.add_argument("--adapter-strength", type=float, default=1.0)
    fit_pref_p.add_argument("--preference-gate", type=float, default=1.0)
    fit_pref_p.add_argument("--prototype-weight", type=float, default=0.0)
    fit_pref_p.add_argument("--prototype-k", type=int, default=9)
    fit_pref_p.add_argument("--prototype-min-similarity", type=float, default=0.02)
    fit_pref_p.add_argument("--profile-prior-weight", type=float, default=0.0)
    fit_pref_p.add_argument("--reference-mode", choices=["decision", "score", "semantic"], default="decision")
    fit_pref_p.add_argument("--threshold", type=float, default=0.5)

    tune_pref_p = sub.add_parser("tune-pref", help="tune an annotation preference model on validation cards")
    add_dataset_args(tune_pref_p)
    add_subset_args(tune_pref_p)
    tune_pref_p.add_argument("--input", type=Path, action="append", required=True)
    tune_pref_p.add_argument("--model", type=Path, required=True)
    tune_pref_p.add_argument("--output", type=Path, required=True)
    tune_pref_p.add_argument("--threshold-grid", type=str, default="0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1")
    tune_pref_p.add_argument("--adapter-grid", type=str, default="0,0.25,0.5,0.75,1,1.25,1.5,2")
    tune_pref_p.add_argument("--gate-grid", type=str, default="0,0.25,0.5,0.75,1")
    tune_pref_p.add_argument("--prototype-grid", type=str, default="0,0.25,0.5,0.75,1")
    tune_pref_p.add_argument("--profile-prior-grid", type=str, default="0,0.25,0.5,0.75,1")
    tune_pref_p.add_argument("--target-calibration", action="store_true")
    tune_pref_p.add_argument("--target-grid", type=str, default="0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1")
    tune_pref_p.add_argument("--metric", choices=["f1", "accuracy", "precision", "recall"], default="f1")

    apply_pref_p = sub.add_parser("apply-pref", help="apply an annotation preference model to saved cards")
    add_dataset_args(apply_pref_p)
    add_subset_args(apply_pref_p)
    apply_pref_p.add_argument("--input", type=Path, required=True)
    apply_pref_p.add_argument("--model", type=Path, required=True)
    apply_pref_p.add_argument("--output", type=Path, required=True)
    apply_pref_p.add_argument("--report-path", type=Path, default=None)

    mine_p = sub.add_parser("mine-hard", help="export hard positives, hard negatives, and abstentions from evidence cards")
    mine_p.add_argument("--input", type=Path, action="append", required=True)
    mine_p.add_argument("--output", type=Path, required=True)

    split_p = sub.add_parser("split", help="export local pair JSONL into CodeXGLUE-style data/train/valid/test files")
    add_dataset_args(split_p)
    split_p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR / "codexglue_split")
    split_p.add_argument("--unmatched-policy", choices=["ratio", "drop"], default="ratio")
    split_p.add_argument("--reference-train", type=str, default="")
    split_p.add_argument("--reference-valid", type=str, default="")
    split_p.add_argument("--reference-test", type=str, default="")

    return parser


def add_dataset_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="BCB JSONL path; defaults to the local bcb_exported_balanced_1000.jsonl if found",
    )


def add_subset_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--split-dir",
        type=Path,
        default=None,
        help="directory produced by `eviclone split`; enables train/valid/test filtering via JSONL split files",
    )
    parser.add_argument(
        "--splits",
        type=str,
        default="",
        help="comma-separated split names from --split-dir, for example train,valid or test",
    )


def add_llm_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--api-key", type=str, default="")
    parser.add_argument("--api-key-env", type=str, default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--thinking-type", type=str, default="disabled")


def add_dynamic_router_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dynamic-routing",
        choices=["always", "router"],
        default="always",
        help="with --with-dynamic, either always run dynamic evidence or use the dynamic evidence router",
    )
    parser.add_argument(
        "--dynamic-route-threshold",
        type=float,
        default=0.5,
        help="minimum expected-utility score required to run dynamic evidence in router mode",
    )
    parser.add_argument(
        "--baseline-predictions",
        type=Path,
        default=None,
        help=f"optional DSFM/base-detector prediction file: {DEFAULT_BASE_PREDICTION_FORMAT}",
    )
    parser.add_argument("--baseline-name", type=str, default=DEFAULT_BASE_MODEL)
    parser.add_argument(
        "--dynamic-route-model",
        type=Path,
        default=None,
        help="optional learned execution-routing model; it decides only whether to acquire dynamic evidence",
    )


def resolve_dataset(path: Path | None) -> Path:
    dataset = path or find_default_dataset(Path.cwd())
    if not dataset.exists():
        raise FileNotFoundError(
            "dataset not found. Pass --dataset, or place bcb_exported_balanced_1000.jsonl in data_work/."
        )
    return dataset.resolve()


def make_llm_client(args: argparse.Namespace) -> ChatClient:
    cfg = LLMConfig(
        base_url=args.base_url,
        model=args.model,
        timeout_sec=args.timeout_sec,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        thinking_type=args.thinking_type,
        api_key_env=args.api_key_env,
    )
    api_key = cfg.resolve_api_key(args.api_key)
    return ChatClient(config=cfg, api_key=api_key)


def llm_enrich_pair(
    pair: ClonePair,
    card: dict[str, Any],
    args: argparse.Namespace,
    *,
    client: ChatClient | None = None,
) -> dict[str, Any]:
    client = client or make_llm_client(args)
    prompt = build_evidence_prompt(
        pair,
        card["local_evidence"],
        policy=args.policy,
        dynamic_evidence=card.get("dynamic_evidence"),
    )
    last_error: Exception | None = None
    for attempt in range(max(1, args.llm_retries)):
        try:
            raw = client.complete(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)
            obj = extract_json_object(raw)
            return merge_llm_evidence(card, obj)
        except (LLMError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if isinstance(exc, LLMError) and is_non_retryable_llm_error(exc):
                break
            wait_sec = llm_retry_wait_seconds(exc, attempt)
            if wait_sec > 0:
                time.sleep(wait_sec)
    assert last_error is not None
    raise last_error


def llm_retry_wait_seconds(exc: Exception, attempt: int) -> float:
    text = str(exc).lower()
    if "429" in text or "rate limit" in text or "速率限制" in text:
        return min(90.0 * (attempt + 1), 300.0)
    return 1.0


def command_inspect(args: argparse.Namespace) -> int:
    dataset, pairs = resolve_selected_pairs(args, inspect_limit=args.limit)
    summary = summarize_pairs(pairs)
    summary["dataset"] = str(dataset)
    if getattr(args, "splits", ""):
        summary["splits"] = list(parse_split_names(args.splits))
        summary["split_dir"] = str(args.split_dir.resolve()) if args.split_dir else ""
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def command_run(args: argparse.Namespace) -> int:
    dataset, pairs = resolve_selected_pairs(args)
    if not pairs:
        print("No pairs matched the requested range.", file=sys.stderr)
        return 2

    run_name = args.run_name or default_run_name(args)
    worker_count = resolve_worker_count(getattr(args, "workers", 0), len(pairs))
    commit_every = max(1, int(getattr(args, "commit_every", 10) or 10))
    args._alignment_model = load_alignment_model(getattr(args, "alignment_model", None))
    args._base_predictions = resolve_base_predictions(args)
    args._dynamic_route_model = resolve_dynamic_route_model(args)
    args.context_source_dir = resolve_context_source_dir(args, output_path=args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(args.db_path)
    run_id = get_or_create_run(
        conn,
        name=run_name,
        dataset_path=dataset,
        policy=args.policy,
        model=args.model if (args.with_llm or args.with_llm_context_completion) else "local",
        with_llm=args.with_llm or args.with_llm_context_completion,
    )

    cards: list[dict[str, Any]] = []
    dirty_writes = 0
    with args.output.open("w", encoding="utf-8", newline="\n") as f:
        for index, pair, card in iter_analyzed_pairs(pairs, args, worker_count=worker_count):
            cards.append(card)
            upsert_card(conn, run_id, card)
            dirty_writes += 1
            if dirty_writes >= commit_every:
                conn.commit()
                dirty_writes = 0
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
            print(
                f"[{index}/{len(pairs)}] pair={pair.pair_id} "
                f"gold={pair.label} verdict={card['decision']['verdict']} "
                f"pred={card['decision'].get('pred_label')}",
                flush=True,
            )
        if dirty_writes:
            conn.commit()

    result = {
        "run_name": run_name,
        "dataset": str(dataset),
        "output": str(args.output.resolve()),
        "db_path": str(args.db_path.resolve()),
        "workers": worker_count,
        "commit_every": commit_every,
        "metrics_against_bcb_gold": metrics(cards),
    }
    report_path = args.report_path or args.output.with_suffix(".report.md")
    result["report_path"] = str(report_path.resolve())
    result["summary"] = write_report(cards, report_path, title=f"EviClone Run Report: {run_name}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    conn.close()
    return 0


def analyze_pair(
    pair: ClonePair,
    args: argparse.Namespace,
    *,
    llm_client: ChatClient | None = None,
) -> dict[str, Any]:
    card = build_local_card(pair, policy=args.policy)
    should_run_dynamic = bool(getattr(args, "with_dynamic", False))
    route_decision = None
    routed_mode = should_run_dynamic and getattr(args, "dynamic_routing", "always") == "router"
    if routed_mode:
        route_threshold = getattr(args, "dynamic_route_threshold", None)
        route_decision = route_dynamic_execution(
            pair,
            card,
            base_prediction=base_prediction_for_pair(pair, getattr(args, "_base_predictions", None)),
            threshold=0.5 if route_threshold is None else float(route_threshold),
            mode=getattr(args, "dynamic_mode", "execute"),
            model=getattr(args, "_dynamic_route_model", None),
        )
        card = attach_dynamic_route(card, route_decision)
        should_run_dynamic = route_decision.run_dynamic
        if not should_run_dynamic:
            return attach_pipeline_trace(apply_base_model_passthrough(card, route_decision))

    if should_run_dynamic:
        context_completion_client = None
        if getattr(args, "with_llm_context_completion", False):
            context_completion_client = llm_client or make_llm_client(args)
        semaphore = getattr(args, "_dynamic_semaphore", None)
        dynamic = evaluate_java_pair(
            pair,
            mode=args.dynamic_mode,
            timeout_sec=args.dynamic_timeout_sec,
            context_completion_client=context_completion_client,
            context_completion_retries=getattr(args, "context_completion_retries", 1),
            context_source_dir=resolve_context_source_dir(args),
            local_execution_semaphore=semaphore,
        )
        if route_decision is not None:
            card = dict(card)
            card["dynamic_evidence"] = dynamic
            card = apply_executable_fusion(card, base_prediction=route_decision.base_prediction)
        else:
            card = merge_dynamic_evidence(card, dynamic)
    elif route_decision is not None:
        card = attach_dynamic_route(card, route_decision)
    if route_decision is not None:
        return attach_pipeline_trace(card)
    if not getattr(args, "with_llm", False):
        card = apply_boundary_guards(pair, card)
        return maybe_apply_alignment(pair, card, args)
    try:
        card = llm_enrich_pair(pair, card, args, client=llm_client)
    except (LLMError, ValueError, json.JSONDecodeError) as exc:
        card["llm_evidence"] = {
            "status": "failed",
            "error": str(exc),
        }
        card["decision"]["recommended_next_step"] = "retry_llm_or_human_audit"
    card = apply_boundary_guards(pair, card)
    return maybe_apply_alignment(pair, card, args)


def maybe_apply_alignment(pair: ClonePair, card: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    model = getattr(args, "_alignment_model", None)
    if model is None:
        model = load_alignment_model(getattr(args, "alignment_model", None))
        args._alignment_model = model
    if model and (getattr(args, "policy", "") == "bcb-alignment" or getattr(args, "alignment_model", None)):
        return apply_bcb_alignment(card, model, pair=pair)
    return card


def resolve_base_predictions(args: argparse.Namespace) -> dict[tuple[str, str], Any] | None:
    path = getattr(args, "baseline_predictions", None)
    if not path:
        return None
    return load_base_predictions(path, source=str(getattr(args, "baseline_name", DEFAULT_BASE_MODEL) or DEFAULT_BASE_MODEL))


def resolve_dynamic_route_model(args: argparse.Namespace) -> Any | None:
    path = getattr(args, "dynamic_route_model", None)
    if not path:
        return None
    return load_learned_dynamic_route_model(path)


def resolve_context_source_dir(args: argparse.Namespace, *, output_path: Path | None = None) -> Path | None:
    explicit = getattr(args, "context_source_dir", None)
    if explicit:
        return Path(explicit)
    if not (getattr(args, "with_dynamic", False) and getattr(args, "with_llm_context_completion", False)):
        return None
    output = output_path or getattr(args, "output", None)
    if output:
        output = Path(output)
        return output.with_name(f"{output.stem}.context_sources")
    return DEFAULT_OUTPUT_DIR / "context_sources" / "routed_dynamic"


def resolve_worker_count(requested: int, pair_count: int) -> int:
    if pair_count <= 1:
        return 1
    if requested and requested > 0:
        return max(1, min(int(requested), pair_count))
    cpu_count = os.cpu_count() or 4
    return max(1, min(pair_count, min(cpu_count, 8)))


def iter_analyzed_pairs(
    pairs: list[ClonePair],
    args: argparse.Namespace,
    *,
    worker_count: int | None = None,
    analyze_fn: Callable[..., dict[str, Any]] = analyze_pair,
):
    if not pairs:
        return
    resolved_workers = resolve_worker_count(worker_count or 0, len(pairs))
    llm_client = (
        make_llm_client(args)
        if getattr(args, "with_llm", False) or getattr(args, "with_llm_context_completion", False)
        else None
    )
    if resolved_workers <= 1:
        for index, pair in enumerate(pairs, start=1):
            yield index, pair, analyze_fn(pair, args, llm_client=llm_client)
            if getattr(args, "sleep_ms", 0) > 0 and index < len(pairs):
                time.sleep(args.sleep_ms / 1000.0)
        return

    pending: dict[int, tuple[ClonePair, dict[str, Any]]] = {}
    next_index = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=resolved_workers, thread_name_prefix="eviclone") as pool:
        future_to_meta: dict[concurrent.futures.Future[dict[str, Any]], tuple[int, ClonePair]] = {}
        for index, pair in enumerate(pairs, start=1):
            future = pool.submit(analyze_fn, pair, args, llm_client=llm_client)
            future_to_meta[future] = (index, pair)
            if getattr(args, "sleep_ms", 0) > 0 and index < len(pairs):
                time.sleep(args.sleep_ms / 1000.0)
        for future in concurrent.futures.as_completed(future_to_meta):
            index, pair = future_to_meta[future]
            pending[index] = (pair, future.result())
            while next_index in pending:
                ready_pair, ready_card = pending.pop(next_index)
                yield next_index, ready_pair, ready_card
                next_index += 1


def command_show(args: argparse.Namespace) -> int:
    dataset, pairs = resolve_selected_pairs(args)
    if not pairs:
        print(f"pair_id not found: {args.pair_id}", file=sys.stderr)
        return 2
    args._alignment_model = load_alignment_model(getattr(args, "alignment_model", None))
    args._base_predictions = resolve_base_predictions(args)
    args._dynamic_route_model = resolve_dynamic_route_model(args)
    args.context_source_dir = resolve_context_source_dir(args)
    card = analyze_pair(pairs[0], args)
    print(render_markdown_card(card))
    return 0


def command_split(args: argparse.Namespace) -> int:
    dataset = resolve_dataset(args.dataset)
    reference_sources = resolve_reference_sources(
        train_source=args.reference_train,
        valid_source=args.reference_valid,
        test_source=args.reference_test,
    )
    summary = split_pairs_to_codexglue(
        dataset,
        args.output_dir,
        reference_sources=reference_sources,
        unmatched_policy=args.unmatched_policy,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def command_fit_align(args: argparse.Namespace) -> int:
    from .report import load_cards

    cards: list[dict[str, Any]] = []
    for path in args.input:
        cards.extend(load_cards(path))
    pair_map: dict[int, ClonePair] = {}
    try:
        _, pairs = resolve_selected_pairs(args)
        pair_map = {pair.pair_id: pair for pair in pairs}
    except FileNotFoundError:
        pair_map = {}
    model = train_alignment_model(
        cards,
        pair_map=pair_map,
        k=args.k,
        threshold=args.threshold,
        positive_threshold=args.positive_threshold,
        negative_threshold=args.negative_threshold,
        nb_weight=args.nb_weight,
        linear_weight=args.linear_weight,
        linear_epochs=args.linear_epochs,
        memory_k=args.memory_k,
        memory_weight=args.memory_weight,
        memory_min_similarity=args.memory_min_similarity,
        decision_mode=args.decision_mode,
    )
    save_alignment_model(model, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "inputs": [str(path.resolve()) for path in args.input],
                "summary": model.get("summary", {}),
                "label_counts": model.get("label_counts", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_tune_align(args: argparse.Namespace) -> int:
    from .report import load_cards

    cards: list[dict[str, Any]] = []
    for path in args.input:
        cards.extend(load_cards(path))
    pair_map: dict[int, ClonePair] = {}
    try:
        _, pairs = resolve_selected_pairs(args)
        pair_map = {pair.pair_id: pair for pair in pairs}
    except FileNotFoundError:
        pair_map = {}
    model = load_alignment_model(args.model)
    if model is None:
        raise FileNotFoundError(f"alignment model not found: {args.model}")
    baseline = evaluate_alignment_model(cards, model, pair_map=pair_map)
    tuned = tune_alignment_thresholds(
        cards,
        model,
        pair_map=pair_map,
        positive_thresholds=parse_float_grid(args.positive_grid),
        negative_thresholds=parse_float_grid(args.negative_grid),
        nb_weights=parse_float_grid(args.nb_weight_grid),
        linear_weights=parse_float_grid(args.linear_weight_grid),
        memory_weights=parse_float_grid(args.memory_weight_grid),
        decision_modes=parse_decision_modes(args.decision_modes),
        metric=args.metric,
    )
    if args.target_calibration:
        tuned = tune_target_thresholds(
            cards,
            tuned,
            pair_map=pair_map,
            threshold_grid=parse_float_grid(args.target_grid),
            metric=args.metric,
        )
    tuned_summary = evaluate_alignment_model(cards, tuned, pair_map=pair_map)
    save_alignment_model(tuned, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "model": str(args.model.resolve()),
                "inputs": [str(path.resolve()) for path in args.input],
                "baseline_metrics": baseline,
                "tuned_metrics": tuned_summary,
                "tuning": tuned.get("tuning", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_fit_pref(args: argparse.Namespace) -> int:
    from .report import load_cards

    cards: list[dict[str, Any]] = []
    for path in args.input:
        cards.extend(load_cards(path))
    pair_map: dict[int, ClonePair] = {}
    try:
        _, pairs = resolve_selected_pairs(args)
        pair_map = {pair.pair_id: pair for pair in pairs}
    except FileNotFoundError:
        pair_map = {}
    model = train_preference_model(
        cards,
        pair_map=pair_map,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        l2=args.l2,
        target_l2=args.target_l2,
        target_min_examples=args.target_min_examples,
        adapter_strength=args.adapter_strength,
        preference_gate=args.preference_gate,
        prototype_weight=args.prototype_weight,
        prototype_k=args.prototype_k,
        prototype_min_similarity=args.prototype_min_similarity,
        profile_prior_weight=args.profile_prior_weight,
        reference_mode=args.reference_mode,
        threshold=args.threshold,
    )
    save_preference_model(model, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "inputs": [str(path.resolve()) for path in args.input],
                "summary": model.get("summary", {}),
                "label_counts": model.get("label_counts", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_tune_pref(args: argparse.Namespace) -> int:
    from .report import load_cards

    cards: list[dict[str, Any]] = []
    for path in args.input:
        cards.extend(load_cards(path))
    pair_map: dict[int, ClonePair] = {}
    try:
        _, pairs = resolve_selected_pairs(args)
        pair_map = {pair.pair_id: pair for pair in pairs}
    except FileNotFoundError:
        pair_map = {}
    model = load_preference_model(args.model)
    if model is None:
        raise FileNotFoundError(f"preference model not found: {args.model}")
    baseline = evaluate_preference_model(cards, model, pair_map=pair_map)
    tuned = tune_preference_model(
        cards,
        model,
        pair_map=pair_map,
        threshold_grid=parse_float_grid(args.threshold_grid),
        adapter_grid=parse_float_grid(args.adapter_grid, max_value=None),
        gate_grid=parse_float_grid(args.gate_grid),
        prototype_grid=parse_float_grid(args.prototype_grid),
        profile_prior_grid=parse_float_grid(args.profile_prior_grid),
        metric=args.metric,
    )
    if args.target_calibration:
        tuned = tune_preference_target_thresholds(
            cards,
            tuned,
            pair_map=pair_map,
            threshold_grid=parse_float_grid(args.target_grid),
            metric=args.metric,
        )
    tuned_summary = evaluate_preference_model(cards, tuned, pair_map=pair_map)
    save_preference_model(tuned, args.output)
    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "model": str(args.model.resolve()),
                "inputs": [str(path.resolve()) for path in args.input],
                "baseline_metrics": baseline,
                "tuned_metrics": tuned_summary,
                "tuning": tuned.get("tuning", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_apply_pref(args: argparse.Namespace) -> int:
    from .report import load_cards

    dataset, selected_pairs = resolve_selected_pairs(args)
    pairs = {pair.pair_id: pair for pair in selected_pairs}
    model = load_preference_model(args.model)
    if model is None:
        raise FileNotFoundError(f"preference model not found: {args.model}")
    cards = []
    for card in load_cards(args.input):
        pair = pairs.get(int(card.get("pair_id", 0) or 0))
        if not pair:
            continue
        cards.append(apply_preference_model(card, model, pair=pair))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(card, ensure_ascii=False) for card in cards) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report_path = args.report_path or args.output.with_suffix(".report.md")
    summary = write_report(cards, report_path)
    print(
        json.dumps(
            {
                "dataset": str(dataset),
                "model": str(args.model.resolve()),
                "output": str(args.output.resolve()),
                "report_path": str(report_path.resolve()),
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def command_mine_hard(args: argparse.Namespace) -> int:
    from .report import load_cards

    cards: list[dict[str, Any]] = []
    for path in args.input:
        cards.extend(load_cards(path))
    cases = mine_hard_cases(cards)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + ("\n" if cases else ""),
        encoding="utf-8",
        newline="\n",
    )
    summary: dict[str, int] = {}
    for case in cases:
        key = str(case.get("case_type", "unknown"))
        summary[key] = summary.get(key, 0) + 1
    print(json.dumps({"output": str(args.output.resolve()), "summary": summary}, ensure_ascii=False, indent=2))
    return 0


def command_adjudicate(args: argparse.Namespace) -> int:
    from .report import load_cards

    dataset, selected_pairs = resolve_selected_pairs(args)
    pairs = {item.pair_id: item for item in selected_pairs}
    cards = load_cards(args.input)
    worker_count = resolve_worker_count(getattr(args, "workers", 4), len(cards))
    client = make_llm_client(args)

    def handle(item: tuple[int, dict[str, Any]]) -> tuple[int, dict[str, Any], bool]:
        index, card = item
        pair = pairs.get(int(card.get("pair_id", 0)))
        if not pair or not should_adjudicate(
            card,
            mode=args.trigger_mode,
            margin_low=args.margin_low,
            margin_high=args.margin_high,
        ):
            return index, card, False
        prompt = build_adjudication_prompt(pair, card)
        last_error: Exception | None = None
        for attempt in range(max(1, int(args.llm_retries))):
            try:
                raw = client.complete(system_prompt=ADJUDICATION_SYSTEM_PROMPT, user_prompt=prompt)
                obj = extract_json_object(raw)
                return index, apply_adjudication(card, obj, accept_confidence=args.accept_confidence), True
            except (LLMError, ValueError, json.JSONDecodeError) as exc:
                last_error = exc
                error_text = str(exc)
                if "HTTP 429" in error_text or "rate" in error_text.lower() or "速率" in error_text:
                    time.sleep(min(60.0, 8.0 * (attempt + 1)))
                else:
                    time.sleep(1.0 + attempt)
        failed = dict(card)
        failed["llm_adjudication"] = {"status": "failed", "error": str(last_error)}
        return index, failed, True

    indexed_cards = list(enumerate(cards))
    results: list[dict[str, Any] | None] = [None] * len(cards)
    adjudicated = 0
    if worker_count <= 1:
        for index_card in indexed_cards:
            index, card, did_adjudicate = handle(index_card)
            results[index] = card
            adjudicated += 1 if did_adjudicate else 0
            print(f"[{index + 1}/{len(cards)}] pair={card.get('pair_id')} adjudicated={did_adjudicate}", flush=True)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="eviclone-adj") as pool:
            futures = [pool.submit(handle, item) for item in indexed_cards]
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                index, card, did_adjudicate = future.result()
                results[index] = card
                adjudicated += 1 if did_adjudicate else 0
                completed += 1
                print(f"[{completed}/{len(cards)}] pair={card.get('pair_id')} adjudicated={did_adjudicate}", flush=True)

    output_cards = [card for card in results if card is not None]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(card, ensure_ascii=False) for card in output_cards) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report_path = args.report_path or args.output.with_suffix(".report.md")
    summary = write_report(output_cards, report_path)
    print(
        json.dumps(
            {
                "dataset": str(dataset),
                "input": str(args.input.resolve()),
                "output": str(args.output.resolve()),
                "report_path": str(report_path.resolve()),
                "trigger_mode": args.trigger_mode,
                "adjudicated": adjudicated,
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def parse_float_grid(text: str, *, min_value: float = 0.0, max_value: float | None = 1.0) -> list[float]:
    values: list[float] = []
    for raw in text.split(","):
        item = raw.strip()
        if not item:
            continue
        value = float(item)
        if value < min_value or (max_value is not None and value > max_value):
            if max_value is None:
                raise ValueError(f"grid value must be >= {min_value:g}: {item}")
            raise ValueError(f"grid value must be in [{min_value:g}, {max_value:g}]: {item}")
        if value not in values:
            values.append(value)
    if not values:
        raise ValueError("grid must contain at least one value")
    return values


def parse_decision_modes(text: str) -> list[str]:
    allowed = {"replace", "selective", "fill-abstain"}
    modes: list[str] = []
    for raw in text.split(","):
        mode = raw.strip()
        if not mode:
            continue
        if mode not in allowed:
            raise ValueError(f"unsupported decision mode: {mode}")
        if mode not in modes:
            modes.append(mode)
    if not modes:
        raise ValueError("decision mode list must not be empty")
    return modes


def resolve_selected_pairs(
    args: argparse.Namespace,
    *,
    inspect_limit: int | None = None,
) -> tuple[Path, list[ClonePair]]:
    dataset = resolve_dataset(args.dataset)
    split_names = parse_split_names(getattr(args, "splits", ""))
    split_pair_ids: set[int] | None = None
    if split_names:
        if not getattr(args, "split_dir", None):
            raise ValueError("--splits requires --split-dir")
        split_pair_ids = load_split_pair_ids(args.split_dir, split_names)

    pair_id = int(getattr(args, "pair_id", 0) or 0)
    if pair_id:
        pairs = load_pairs(dataset, pair_id=pair_id)
        if split_pair_ids is not None:
            pairs = [pair for pair in pairs if pair.pair_id in split_pair_ids]
        return dataset, pairs

    limit = inspect_limit if inspect_limit is not None else int(getattr(args, "limit", 0) or 0)
    offset = int(getattr(args, "offset", 0) or 0)
    if split_pair_ids is None:
        return dataset, load_pairs(dataset, limit=limit, offset=offset)

    pairs = [pair for pair in load_pairs(dataset) if pair.pair_id in split_pair_ids]
    if offset:
        pairs = pairs[offset:]
    if limit:
        pairs = pairs[:limit]
    return dataset, pairs


def render_markdown_card(card: dict[str, Any]) -> str:
    decision = card["decision"]
    target = card["target"]
    local = card["local_evidence"]
    llm = card.get("llm_evidence")
    lines = [
        f"# Evidence Card: pair {card['pair_id']}",
        "",
        f"- Target: {target.get('name') or target.get('functionality_id')}",
        f"- Gold label: {card['gold']['label']} ({card['gold']['source']})",
        f"- Policy: {card['policy']}",
        f"- Verdict: {decision.get('verdict')}",
        f"- Pred label: {decision.get('pred_label')}",
        f"- Confidence: {decision.get('confidence')}",
        "",
        "## Local Evidence",
        "",
        f"- Shared feature families: {', '.join(local.get('shared_feature_families', [])) or 'none'}",
        f"- Identifier similarity: {local.get('identifier_similarity')}",
        f"- Observations: {'; '.join(local.get('observations', [])) or 'none'}",
        f"- Risk flags: {'; '.join(local.get('risk_flags', [])) or 'none'}",
        "",
        "## Rationale",
        "",
        str(decision.get("rationale", "")) or "No rationale.",
    ]
    if llm:
        lines.extend(["", "## LLM Evidence", "", "```json", json.dumps(llm, ensure_ascii=False, indent=2), "```"])
    dynamic = card.get("dynamic_evidence")
    if dynamic:
        lines.extend(["", "## Dynamic Evidence", "", "```json", json.dumps(dynamic, ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines)


def default_run_name(args: argparse.Namespace) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = "llm" if args.with_llm else "local"
    suffix = f"pair{args.pair_id}" if args.pair_id else f"n{args.limit}_o{args.offset}"
    split_names = parse_split_names(getattr(args, "splits", ""))
    if split_names:
        suffix += "_" + "-".join(split_names)
    return f"eviclone_{mode}_{args.policy}_{suffix}_{stamp}"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "inspect":
        return command_inspect(args)
    if args.command == "run":
        return command_run(args)
    if args.command == "show":
        return command_show(args)
    if args.command == "split":
        return command_split(args)
    if args.command == "fit-align":
        return command_fit_align(args)
    if args.command == "tune-align":
        return command_tune_align(args)
    if args.command == "fit-pref":
        return command_fit_pref(args)
    if args.command == "tune-pref":
        return command_tune_pref(args)
    if args.command == "apply-pref":
        return command_apply_pref(args)
    if args.command == "mine-hard":
        return command_mine_hard(args)
    if args.command == "report":
        from .report import load_cards

        cards = load_cards(args.input)
        summary = write_report(cards, args.output)
        print(json.dumps({"output": str(args.output.resolve()), "summary": summary}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "rejudge":
        from .report import load_cards

        dataset, selected_pairs = resolve_selected_pairs(args)
        pairs = {item.pair_id: item for item in selected_pairs}
        args._alignment_model = load_alignment_model(getattr(args, "alignment_model", None))
        cards = []
        for old_card in load_cards(args.input):
            pair = pairs.get(int(old_card["pair_id"]))
            if not pair:
                continue
            policy = args.policy or old_card.get("policy", "bcb-gold")
            rebuilt = build_local_card(pair, policy=policy)
            if old_card.get("dynamic_evidence"):
                rebuilt = merge_dynamic_evidence(rebuilt, old_card["dynamic_evidence"])
            if old_card.get("llm_evidence") and old_card.get("llm_evidence", {}).get("status") != "failed":
                rebuilt = merge_llm_evidence(rebuilt, old_card["llm_evidence"])
            rebuilt = apply_boundary_guards(pair, rebuilt)
            rebuilt = maybe_apply_alignment(pair, rebuilt, args)
            cards.append(rebuilt)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "\n".join(json.dumps(card, ensure_ascii=False) for card in cards) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        report_path = args.report_path or args.output.with_suffix(".report.md")
        summary = write_report(cards, report_path)
        print(
            json.dumps(
                {"output": str(args.output.resolve()), "report_path": str(report_path.resolve()), "summary": summary},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "adjudicate":
        return command_adjudicate(args)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
