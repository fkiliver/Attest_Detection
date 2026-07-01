from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.alignment import load_alignment_model
from eviclone_prototype.cli import analyze_pair, make_llm_client, resolve_context_source_dir
from eviclone_prototype.config import (
    DEFAULT_API_KEY_ENV,
    DEFAULT_BASE_MODEL,
    DEFAULT_BASE_PREDICTION_FORMAT,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
)
from eviclone_prototype.dataset import ClonePair, iter_jsonl, load_pairs
from eviclone_prototype.dynamic_router import load_base_predictions
from eviclone_prototype.llm import ChatClient, LLMError, extract_json_object
from eviclone_prototype.report import write_report
from eviclone_prototype.selective_gate import coerce_label

TERMINAL_LLM_ERROR_BUCKETS = {
    "HTTP 402: Insufficient Balance",
    "HTTP 401: unauthorized or invalid API key",
    "missing API key",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EviClone on error cases with unordered checkpointed writes.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--split-dir", type=Path, default=None)
    parser.add_argument("--splits", type=str, default="")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report-path", type=Path, default=None)
    parser.add_argument("--summary-path", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--resume-usable-only",
        action="store_true",
        help="with --resume, retry existing cards whose decision.pred_label or retained LLM context source is not usable",
    )
    parser.add_argument("--policy", type=str, default="bcb-gold")
    parser.add_argument("--with-dynamic", action="store_true")
    parser.add_argument("--dynamic-mode", choices=["compile", "execute"], default="execute")
    parser.add_argument("--dynamic-timeout-sec", type=int, default=8)
    parser.add_argument("--dynamic-routing", choices=["always", "router"], default="always")
    parser.add_argument("--dynamic-route-threshold", type=float, default=0.5)
    parser.add_argument(
        "--baseline-predictions",
        type=Path,
        default=None,
        help=f"optional DSFM/base-detector prediction file for dynamic-routing pass-through: {DEFAULT_BASE_PREDICTION_FORMAT}",
    )
    parser.add_argument("--baseline-name", type=str, default=DEFAULT_BASE_MODEL)
    parser.add_argument(
        "--dynamic-workers",
        type=int,
        default=0,
        help="optional local Java dynamic-execution concurrency limit; 0 means no separate limit",
    )
    parser.add_argument("--with-llm-context-completion", action="store_true")
    parser.add_argument("--context-completion-retries", type=int, default=3)
    parser.add_argument(
        "--context-source-dir",
        type=Path,
        default=None,
        help="optional directory for sidecar EviProbe.java sources produced by LLM context completion",
    )
    parser.add_argument("--with-llm", action="store_true")
    parser.add_argument("--llm-retries", type=int, default=2)
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key-env", type=str, default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--api-key", type=str, default="")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--alignment-model", type=Path, default=None)
    parser.add_argument("--llm-preflight", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--stop-on-terminal-llm-error",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="stop submitting new pairs after non-retryable account/API errors such as HTTP 402",
    )
    args = parser.parse_args()

    pairs = select_pairs(args)
    if args.offset:
        pairs = pairs[args.offset :]
    if args.limit:
        pairs = pairs[: args.limit]
    if not pairs:
        raise SystemExit("no pairs selected")

    existing_cards = load_existing_cards(args.output) if args.resume else []
    if args.resume and args.resume_usable_only:
        existing_cards = compact_resume_cards(existing_cards, pairs, usable_only=True)
    done_ids = existing_done_ids(existing_cards, usable_only=args.resume_usable_only)
    todo = [pair for pair in pairs if pair.pair_id not in done_ids]

    context_source_dir = resolve_context_source_dir(args, output_path=args.output)
    run_args = SimpleNamespace(
        with_llm=args.with_llm,
        llm_retries=args.llm_retries,
        policy=args.policy,
        with_dynamic=args.with_dynamic,
        dynamic_mode=args.dynamic_mode,
        dynamic_timeout_sec=args.dynamic_timeout_sec,
        dynamic_routing=args.dynamic_routing,
        dynamic_route_threshold=args.dynamic_route_threshold,
        baseline_predictions=args.baseline_predictions,
        baseline_name=args.baseline_name,
        with_llm_context_completion=args.with_llm_context_completion,
        context_completion_retries=args.context_completion_retries,
        context_source_dir=context_source_dir,
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key,
        api_key_env=args.api_key_env,
        timeout_sec=args.timeout_sec,
        temperature=args.temperature,
        alignment_model=args.alignment_model,
        _alignment_model=load_alignment_model(args.alignment_model),
        _base_predictions=(
            load_base_predictions(args.baseline_predictions, source=args.baseline_name)
            if args.baseline_predictions
            else None
        ),
        _dynamic_semaphore=threading.BoundedSemaphore(max(1, args.dynamic_workers)) if args.dynamic_workers > 0 else None,
    )
    client = make_llm_client(run_args) if args.with_llm or args.with_llm_context_completion else None
    if client and args.llm_preflight and todo:
        preflight = preflight_llm(client)
        if preflight["status"] != "ok":
            print(json.dumps({"event": "llm_preflight_failed", **preflight}, ensure_ascii=False), file=sys.stderr)
            raise SystemExit(3)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    report_path = args.report_path or args.output.with_suffix(".report.md")
    summary_path = args.summary_path or args.output.with_suffix(".summary.json")
    if args.resume and args.resume_usable_only:
        rewrite_output_cards_atomic(args.output, existing_cards)

    cards = list(existing_cards)
    started = time.time()
    completed_now = 0
    mode = "a" if args.resume and args.output.exists() else "w"
    print(
        json.dumps(
            {
                "event": "start",
                "selected": len(pairs),
                "already_done": len(done_ids),
                "todo": len(todo),
                "workers": args.workers,
                "dynamic_workers": int(args.dynamic_workers),
                "dynamic_routing": args.dynamic_routing,
                "dynamic_route_threshold": args.dynamic_route_threshold,
                "baseline_predictions": str(args.baseline_predictions) if args.baseline_predictions else "",
                "context_source_dir": str(context_source_dir) if context_source_dir else "",
                "resume_usable_only": bool(args.resume_usable_only),
                "stop_on_terminal_llm_error": bool(args.stop_on_terminal_llm_error),
                "retained_existing_cards": len(existing_cards),
                "write_mode": mode,
                "output": str(args.output),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    run_control = run_unordered_analysis(
        todo=todo,
        run_args=run_args,
        llm_client=client,
        output_path=args.output,
        mode=mode,
        cards=cards,
        done_count=len(done_ids),
        total_count=len(pairs),
        workers=args.workers,
        policy=args.policy,
        started=started,
        stop_on_terminal_llm_error=args.stop_on_terminal_llm_error,
        event_writer=lambda event: print(json.dumps(event, ensure_ascii=False), flush=True),
    )

    summary = write_report(cards, report_path, title="Configured LLM Context Completion Full Error Cases")
    attach_run_control(summary, report_path=report_path, run_control=run_control)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "event": "done",
                "output": str(args.output.resolve()),
                "report_path": str(report_path.resolve()),
                "summary_path": str(summary_path.resolve()),
                "run_control": run_control,
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )
    return 0


def select_pairs(args: argparse.Namespace) -> list[ClonePair]:
    pairs = load_pairs(args.dataset, limit=0)
    if not args.split_dir or not args.splits.strip():
        return pairs
    wanted = set()
    for split in [x.strip() for x in args.splits.split(",") if x.strip()]:
        for obj in iter_jsonl(args.split_dir / f"{split}.jsonl"):
            wanted.add(int(obj["pair_id"]))
    return [pair for pair in pairs if pair.pair_id in wanted]


def run_unordered_analysis(
    *,
    todo: list[ClonePair],
    run_args: SimpleNamespace,
    llm_client: ChatClient | None,
    output_path: Path,
    mode: str,
    cards: list[dict[str, Any]],
    done_count: int,
    total_count: int,
    workers: int,
    policy: str,
    started: float,
    stop_on_terminal_llm_error: bool = True,
    analyzer: Callable[..., dict[str, Any]] = analyze_pair,
    event_writer: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    max_workers = max(1, int(workers or 1))
    completed_now = 0
    submitted_now = 0
    cancelled_pending = 0
    terminal_stop: dict[str, Any] | None = None
    terminal_stop_emitted = False
    pair_iter = iter(todo)
    future_to_pair: dict[concurrent.futures.Future[dict[str, Any]], ClonePair] = {}

    def submit_next(pool: concurrent.futures.ThreadPoolExecutor) -> bool:
        nonlocal submitted_now
        try:
            pair = next(pair_iter)
        except StopIteration:
            return False
        future_to_pair[pool.submit(analyzer, pair, run_args, llm_client=llm_client)] = pair
        submitted_now += 1
        return True

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open(mode, encoding="utf-8", newline="\n") as f:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="error-cases") as pool:
            while len(future_to_pair) < max_workers and submit_next(pool):
                pass
            while future_to_pair:
                done, _pending = concurrent.futures.wait(
                    future_to_pair,
                    return_when=concurrent.futures.FIRST_COMPLETED,
                )
                for future in done:
                    pair = future_to_pair.pop(future)
                    if future.cancelled():
                        cancelled_pending += 1
                        continue
                    try:
                        card = future.result()
                    except Exception as exc:  # noqa: BLE001 - preserve per-pair failure card for auditability.
                        card = failure_card(pair, policy, str(exc))
                    cards.append(card)
                    f.write(json.dumps(card, ensure_ascii=False) + "\n")
                    f.flush()
                    completed_now += 1
                    maybe_emit_progress(
                        completed_now=completed_now,
                        done_count=done_count,
                        total_count=total_count,
                        started=started,
                        event_writer=event_writer,
                    )
                    if stop_on_terminal_llm_error and terminal_stop is None:
                        bucket = terminal_llm_error_bucket(card)
                        if bucket:
                            terminal_stop = {
                                "event": "terminal_llm_error_stop",
                                "error_bucket": bucket,
                                "trigger_pair_id": pair.pair_id,
                                "completed_now": completed_now,
                                "submitted_now": submitted_now,
                                "cancelled_pending": 0,
                            }
                if terminal_stop is not None:
                    for future in list(future_to_pair):
                        if future.cancel():
                            future_to_pair.pop(future)
                            cancelled_pending += 1
                    if not terminal_stop_emitted:
                        terminal_stop["cancelled_pending"] = cancelled_pending
                        emit_event(event_writer, terminal_stop)
                        terminal_stop_emitted = True
                    continue
                while len(future_to_pair) < max_workers and submit_next(pool):
                    pass

    return {
        "completed_now": completed_now,
        "submitted_now": submitted_now,
        "cancelled_pending": cancelled_pending,
        "terminal_llm_stop": terminal_stop,
        "stop_on_terminal_llm_error": stop_on_terminal_llm_error,
        "max_in_flight": max_workers,
    }


def maybe_emit_progress(
    *,
    completed_now: int,
    done_count: int,
    total_count: int,
    started: float,
    event_writer: Callable[[dict[str, Any]], None] | None,
) -> None:
    total_done = done_count + completed_now
    if completed_now % 10 != 0 and total_done != total_count:
        return
    elapsed = max(time.time() - started, 0.001)
    emit_event(
        event_writer,
        {
            "event": "progress",
            "completed_now": completed_now,
            "total_done": total_done,
            "total": total_count,
            "rate_per_min": round(completed_now / elapsed * 60, 2),
        },
    )


def emit_event(event_writer: Callable[[dict[str, Any]], None] | None, event: dict[str, Any]) -> None:
    if event_writer is not None:
        event_writer(event)


def attach_run_control(summary: dict[str, Any], *, report_path: Path, run_control: dict[str, Any]) -> None:
    summary["run_control"] = run_control
    lines = [
        "",
        "## Run Control",
        "",
        "```json",
        json.dumps(run_control, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    with report_path.open("a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def terminal_llm_error_bucket(card: dict[str, Any]) -> str:
    for error in card_llm_error_strings(card):
        bucket = bucket_preflight_error(error)
        if bucket in TERMINAL_LLM_ERROR_BUCKETS:
            return bucket
    return ""


def card_llm_error_strings(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    llm = card.get("llm_evidence") if isinstance(card.get("llm_evidence"), dict) else {}
    if isinstance(llm, dict) and llm.get("error"):
        errors.append(str(llm.get("error")))
    dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    if isinstance(dynamic, dict):
        completion = dynamic.get("llm_context_completion")
        if isinstance(completion, dict) and completion.get("error"):
            errors.append(str(completion.get("error")))
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    if isinstance(decision, dict) and decision.get("rationale"):
        errors.append(str(decision.get("rationale")))
    return errors


def load_existing_cards(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    cards: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                cards.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return cards


def rewrite_output_cards_atomic(path: Path, cards: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.name}.compact.tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as f:
        for card in cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
    temp.replace(path)


def existing_done_ids(cards: list[dict[str, Any]], *, usable_only: bool) -> set[int]:
    done: set[int] = set()
    for card in cards:
        try:
            pair_id = int(card.get("pair_id", 0))
        except (TypeError, ValueError):
            continue
        if pair_id <= 0:
            continue
        if usable_only and not card_is_usable(card):
            continue
        done.add(pair_id)
    return done


def compact_resume_cards(cards: list[dict[str, Any]], selected_pairs: list[Any], *, usable_only: bool) -> list[dict[str, Any]]:
    selected_order: list[int] = []
    expected_keys: dict[int, tuple[str, str]] = {}
    for item in selected_pairs:
        if isinstance(item, ClonePair):
            pair_id = int(item.pair_id)
            expected_keys[pair_id] = (str(item.function_id_a), str(item.function_id_b))
        else:
            pair_id = int(item)
        selected_order.append(pair_id)
    selected = set(selected_order)
    last_by_pair: dict[int, dict[str, Any]] = {}
    for card in cards:
        try:
            pair_id = int(card.get("pair_id", 0))
        except (TypeError, ValueError):
            continue
        if pair_id not in selected:
            continue
        if pair_id in expected_keys and not card_matches_pair_key(card, expected_keys[pair_id]):
            continue
        if usable_only and not card_is_usable(card):
            continue
        last_by_pair[pair_id] = card
    return [last_by_pair[pair_id] for pair_id in selected_order if pair_id in last_by_pair]


def card_matches_pair_key(card: dict[str, Any], expected: tuple[str, str]) -> bool:
    ids = card.get("function_ids") if isinstance(card.get("function_ids"), dict) else {}
    return (str(ids.get("a", "")), str(ids.get("b", ""))) == expected


def card_is_usable(card: dict[str, Any]) -> bool:
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    if coerce_label(decision.get("pred_label")) not in (0, 1):
        return False
    dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    if not isinstance(dynamic, dict) or "llm_context_completion" not in dynamic:
        return True
    completion = dynamic.get("llm_context_completion")
    if not isinstance(completion, dict) or str(completion.get("status") or "") != "completed":
        return False
    artifact = completion.get("source_artifact") if isinstance(completion.get("source_artifact"), dict) else {}
    if not artifact or artifact.get("retained") is not True:
        return False
    path_text = str(artifact.get("path") or "")
    if not path_text:
        return False
    path = Path(path_text)
    if not path.exists() or not path.is_file():
        return False
    data = path.read_bytes()
    actual_sha = hashlib.sha256(data).hexdigest()
    if str(artifact.get("sha256") or "") != actual_sha:
        return False
    payload = completion.get("payload") if isinstance(completion.get("payload"), dict) else {}
    payload_sha = str(payload.get("java_source_sha256") or "")
    if payload_sha and payload_sha != actual_sha:
        return False
    try:
        recorded_bytes = int(artifact.get("bytes"))
    except (TypeError, ValueError):
        recorded_bytes = None
    if recorded_bytes is not None and recorded_bytes != len(data):
        return False
    return True


def preflight_llm(client: ChatClient) -> dict[str, Any]:
    contract = "strict-json-ok-v1"
    try:
        raw = client.complete(
            system_prompt="You are a health-check endpoint for an LLM client.",
            user_prompt='Return exactly this JSON object and nothing else: {"ok": true}',
        )
    except LLMError as exc:
        return {
            "status": "failed",
            "error": str(exc),
            "error_bucket": bucket_preflight_error(str(exc)),
            "api_called": True,
            "preflight_contract": contract,
            "strict_json_ok": False,
        }
    try:
        parsed = extract_json_object(raw)
    except Exception as exc:  # noqa: BLE001 - invalid preflight replies must stop shard execution.
        error = f"invalid preflight response: {type(exc).__name__}: {exc}"
        return {
            "status": "failed",
            "error": error,
            "error_bucket": "invalid LLM preflight response",
            "response_preview": raw[:120],
            "api_called": True,
            "preflight_contract": contract,
            "strict_json_ok": False,
        }
    if parsed.get("ok") is not True:
        return {
            "status": "failed",
            "error": "invalid preflight response: expected JSON field ok=true",
            "error_bucket": "invalid LLM preflight response",
            "response_preview": raw[:120],
            "api_called": True,
            "preflight_contract": contract,
            "strict_json_ok": False,
        }
    return {
        "status": "ok",
        "response_preview": raw[:120],
        "api_called": True,
        "preflight_contract": contract,
        "strict_json_ok": True,
    }


def bucket_preflight_error(error: str) -> str:
    if "HTTP 402" in error or "Insufficient Balance" in error:
        return "HTTP 402: Insufficient Balance"
    if "HTTP 401" in error or "unauthorized" in error.lower() or "invalid api key" in error.lower():
        return "HTTP 401: unauthorized or invalid API key"
    if "HTTP 403" in error or "forbidden" in error.lower():
        return "HTTP 403: forbidden"
    if "HTTP 429" in error or "rate limit" in error.lower():
        return "HTTP 429: rate limit"
    if "missing API key" in error:
        return "missing API key"
    return error[:160]


def failure_card(pair: ClonePair, policy: str, error: str) -> dict[str, Any]:
    return {
        "schema_version": "eviclone-evidence-card/v1",
        "pair_id": pair.pair_id,
        "function_ids": {"a": pair.function_id_a, "b": pair.function_id_b},
        "gold": {
            "label": pair.label,
            "source": pair.source,
            "bcb_type": pair.bcb_type,
            "syntactic_type": pair.syntactic_type,
        },
        "target": {
            "functionality_id": pair.functionality_id,
            "name": pair.functionality_name,
            "description": pair.functionality_description,
        },
        "policy": policy,
        "local_evidence": {},
        "dynamic_evidence": None,
        "llm_evidence": {"status": "failed", "error": error},
        "decision": {
            "verdict": "context_insufficient",
            "pred_label": None,
            "confidence": 0.0,
            "rationale": error,
            "observations": [],
            "risk_flags": ["runner_failure"],
            "recommended_next_step": "retry_llm_or_human_audit",
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
