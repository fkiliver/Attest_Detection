from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.config import DEFAULT_API_KEY_ENV, DEFAULT_BASE_URL, DEFAULT_MODEL  # noqa: E402
from scripts.audit_probe_source_retention_outputs import (  # noqa: E402
    DEFAULT_CARDS_NAME,
    audit_probe_source_retention_outputs,
)
from scripts.build_probe_execution_readiness_audit import (  # noqa: E402
    DEFAULT_OUTPUT as DEFAULT_READINESS_JSON,
    DEFAULT_REPORT as DEFAULT_READINESS_REPORT,
    build_probe_execution_readiness_audit,
    write_report as write_readiness_report,
)
from scripts.build_probe_source_retention_rerun_queue import (  # noqa: E402
    DEFAULT_CANDIDATES,
    DEFAULT_DATASET,
    DEFAULT_OUTPUT_DIR as DEFAULT_QUEUE_DIR,
    DEFAULT_SPLIT,
    build_probe_source_retention_rerun_queue,
)
from scripts.build_probe_synthesis_plan import DEFAULT_OUTPUT as DEFAULT_PROBE_PLAN  # noqa: E402
from scripts.build_probe_synthesis_plan import DEFAULT_RUN_DIR  # noqa: E402
from scripts.run_probe_synthesis_execution import run_probe_synthesis_execution  # noqa: E402
from scripts.verify_probe_source_retention_rerun_queue import verify_probe_source_retention_rerun_queue  # noqa: E402

DEFAULT_OUTPUT_DIR = DEFAULT_RUN_DIR / "probe_synthesis_closed_loop"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the closed-loop probe-synthesis pipeline: source retention, readiness, execution, and metric delta."
    )
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--probe-plan", type=Path, default=DEFAULT_PROBE_PLAN)
    parser.add_argument("--queue-dir", type=Path, default=DEFAULT_QUEUE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--source-retention-output-dir", type=Path, default=None)
    parser.add_argument("--split", type=str, default=DEFAULT_SPLIT)
    parser.add_argument("--rebuild-queue", action="store_true")
    parser.add_argument("--run-source-retention", action="store_true")
    parser.add_argument("--source-retention-limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=500)
    parser.add_argument("--dynamic-workers", type=int, default=32)
    parser.add_argument("--dynamic-timeout-sec", type=int, default=8)
    parser.add_argument("--context-completion-retries", type=int, default=3)
    parser.add_argument("--execution-limit", type=int, default=0)
    parser.add_argument("--execution-offset", type=int, default=0)
    parser.add_argument("--execution-workers", type=int, default=1)
    parser.add_argument("--probe-timeout-sec", type=int, default=8)
    parser.add_argument("--include-review", action="store_true")
    parser.add_argument("--with-llm-probe", action="store_true")
    parser.add_argument("--llm-probe-retries", type=int, default=1)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key-env", type=str, default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--keep-work", action="store_true")
    parser.add_argument("--skip-execution", action="store_true")
    parser.add_argument("--reuse-existing-execution", action="store_true")
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    result = run_probe_synthesis_full_pipeline(
        run_dir=args.run_dir,
        dataset=args.dataset,
        candidates_jsonl=args.candidates,
        probe_plan_json=args.probe_plan,
        queue_dir=args.queue_dir,
        output_dir=args.output_dir,
        source_retention_output_dir=args.source_retention_output_dir,
        split=args.split,
        rebuild_queue=args.rebuild_queue,
        run_source_retention=args.run_source_retention,
        source_retention_limit=args.source_retention_limit,
        workers=args.workers,
        dynamic_workers=args.dynamic_workers,
        dynamic_timeout_sec=args.dynamic_timeout_sec,
        context_completion_retries=args.context_completion_retries,
        execution_limit=args.execution_limit,
        execution_offset=args.execution_offset,
        execution_workers=args.execution_workers,
        probe_timeout_sec=args.probe_timeout_sec,
        include_review=args.include_review,
        with_llm_probe=args.with_llm_probe,
        llm_probe_retries=args.llm_probe_retries,
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        temperature=args.temperature,
        keep_work=args.keep_work,
        skip_execution=args.skip_execution,
        reuse_existing_execution=args.reuse_existing_execution,
    )
    printable = {
        "status": result["status"],
        "summary": result["outputs"]["summary"],
        "report": result["outputs"]["report"],
        "readiness_status": result["readiness"]["status"],
        "source_retention_run_status": result["source_retention"]["run"]["status"],
        "source_retention_status": result["source_retention"]["audit"]["status"],
        "execution_status": result["execution"]["status"],
    }
    print(json.dumps(printable, ensure_ascii=False, indent=2))
    if args.strict_exit and result["status"] not in {"completed", "completed_with_warnings"}:
        return 2
    return 0


def run_probe_synthesis_full_pipeline(
    *,
    run_dir: Path,
    dataset: Path,
    candidates_jsonl: Path,
    probe_plan_json: Path,
    queue_dir: Path,
    output_dir: Path,
    source_retention_output_dir: Path | None = None,
    split: str = DEFAULT_SPLIT,
    rebuild_queue: bool = False,
    run_source_retention: bool = False,
    source_retention_limit: int = 0,
    workers: int = 500,
    dynamic_workers: int = 32,
    dynamic_timeout_sec: int = 8,
    context_completion_retries: int = 3,
    execution_limit: int = 0,
    execution_offset: int = 0,
    execution_workers: int = 1,
    probe_timeout_sec: int = 8,
    include_review: bool = False,
    with_llm_probe: bool = False,
    llm_probe_retries: int = 1,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    api_key_env: str = DEFAULT_API_KEY_ENV,
    temperature: float = 0.0,
    keep_work: bool = False,
    skip_execution: bool = False,
    reuse_existing_execution: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    requested_output_dir = output_dir
    output_dir = prepare_output_dir(output_dir)
    paths = pipeline_paths(output_dir)
    source_paths = resolve_source_retention_paths(
        queue_dir=queue_dir,
        output_dir=output_dir,
        requested_output_dir=source_retention_output_dir,
    )
    source_cards = source_paths["cards"]
    context_source_dir = source_paths["context_sources"]

    queue = ensure_queue(
        dataset=dataset,
        candidates_jsonl=candidates_jsonl,
        queue_dir=queue_dir,
        split=split,
        rebuild_queue=rebuild_queue,
        workers=workers,
        dynamic_workers=dynamic_workers,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
    )
    queue_verification = verify_probe_source_retention_rerun_queue(queue_dir=queue_dir, split=split)
    source_audit_before = audit_probe_source_retention_outputs(queue_dir=queue_dir, cards_path=source_cards)
    source_run = maybe_run_source_retention(
        run_requested=run_source_retention,
        queue_dir=queue_dir,
        split=split,
        source_cards=source_cards,
        source_report=source_paths["report"],
        source_summary=source_paths["summary"],
        context_source_dir=context_source_dir,
        source_retention_limit=source_retention_limit,
        workers=workers,
        dynamic_workers=dynamic_workers,
        dynamic_timeout_sec=dynamic_timeout_sec,
        context_completion_retries=context_completion_retries,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        temperature=temperature,
        stdout_log=paths["source_retention_stdout"],
        stderr_log=paths["source_retention_stderr"],
        already_verified=source_audit_before.get("status") == "source_artifacts_verified",
    )
    source_audit_after = audit_probe_source_retention_outputs(queue_dir=queue_dir, cards_path=source_cards)

    readiness = build_probe_execution_readiness_audit(
        run_dir=run_dir,
        probe_plan_json=probe_plan_json,
        candidates_jsonl=candidates_jsonl,
        source_cards_jsonl=source_cards,
        now=now,
    )
    paths["readiness"].write_text(
        json.dumps(readiness, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_readiness_report(paths["readiness_report"], readiness)

    execution = run_execution_stage(
        dataset=queue_dir / "pairs.jsonl",
        candidates_jsonl=candidates_jsonl,
        source_cards=source_cards,
        output_jsonl=paths["execution_results"],
        summary_path=paths["execution_summary"],
        report_path=paths["execution_report"],
        source_dir=output_dir / "probe_sources",
        readiness=readiness,
        skip_execution=skip_execution,
        execution_limit=execution_limit,
        execution_offset=execution_offset,
        execution_workers=execution_workers,
        probe_timeout_sec=probe_timeout_sec,
        include_review=include_review,
        with_llm_probe=with_llm_probe,
        llm_probe_retries=llm_probe_retries,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        temperature=temperature,
        keep_work=keep_work,
        reuse_existing_execution=reuse_existing_execution,
    )
    result = {
        "schema_version": "eviclone-probe-synthesis-full-pipeline/v1",
        "status": overall_status(queue_verification, source_audit_after, readiness, execution),
        "created_at_utc": now.isoformat(),
        "configuration": {
            "run_source_retention": run_source_retention,
            "source_retention_limit": source_retention_limit,
            "workers": workers,
            "dynamic_workers": dynamic_workers,
            "execution_limit": execution_limit,
            "execution_offset": execution_offset,
            "execution_workers": execution_workers,
            "reuse_existing_execution": reuse_existing_execution,
            "include_review": include_review,
            "with_llm_probe": with_llm_probe,
            "api_key_env": api_key_env,
            "api_key_configured": bool(os.getenv(api_key_env, "")),
            "model": model,
            "base_url": base_url,
        },
        "inputs": {
            "run_dir": str(run_dir.resolve()),
            "dataset": str(dataset.resolve()),
            "candidates_jsonl": str(candidates_jsonl.resolve()),
            "probe_plan_json": str(probe_plan_json.resolve()),
            "queue_dir": str(queue_dir.resolve()),
            "source_cards": str(source_cards.resolve()),
            "source_retention_output_dir": str(source_paths["output_dir"].resolve()),
            "source_retention_report": str(source_paths["report"].resolve()),
            "source_retention_summary": str(source_paths["summary"].resolve()),
            "context_source_dir": str(context_source_dir.resolve()),
            "requested_output_dir": str(requested_output_dir.resolve()),
            "actual_output_dir": str(output_dir.resolve()),
        },
        "outputs": {
            **{key: str(value.resolve()) for key, value in paths.items() if key not in {"source_retention_stdout", "source_retention_stderr"}},
            "source_retention_cards": str(source_cards.resolve()),
            "source_retention_report": str(source_paths["report"].resolve()),
            "source_retention_summary": str(source_paths["summary"].resolve()),
            "context_source_dir": str(context_source_dir.resolve()),
        },
        "queue": {
            "status": queue.get("status"),
            "summary": queue,
            "verification": queue_verification,
        },
        "source_retention": {
            "run": source_run,
            "audit_before": source_audit_before,
            "audit": source_audit_after,
        },
        "readiness": readiness,
        "execution": execution,
        "metric_delta": metric_delta(execution),
        "next_action": next_action(
            source_audit_after,
            readiness,
            execution,
            source_run=source_run,
            run_source_retention=run_source_retention,
        ),
    }
    paths["summary"].write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_pipeline_report(paths["report"], result)
    return result


def ensure_queue(
    *,
    dataset: Path,
    candidates_jsonl: Path,
    queue_dir: Path,
    split: str,
    rebuild_queue: bool,
    workers: int,
    dynamic_workers: int,
    model: str,
    base_url: str,
    api_key_env: str,
) -> dict[str, Any]:
    summary_path = queue_dir / "summary.json"
    if rebuild_queue or not summary_path.exists():
        return build_probe_source_retention_rerun_queue(
            dataset=dataset,
            candidates_jsonl=candidates_jsonl,
            output_dir=queue_dir,
            split=split,
            workers=workers,
            dynamic_workers=dynamic_workers,
            model=model,
            base_url=base_url,
            api_key_env=api_key_env,
        )
    return read_json(summary_path)


def maybe_run_source_retention(
    *,
    run_requested: bool,
    queue_dir: Path,
    split: str,
    source_cards: Path,
    source_report: Path,
    source_summary: Path,
    context_source_dir: Path,
    source_retention_limit: int,
    workers: int,
    dynamic_workers: int,
    dynamic_timeout_sec: int,
    context_completion_retries: int,
    model: str,
    base_url: str,
    api_key_env: str,
    temperature: float,
    stdout_log: Path,
    stderr_log: Path,
    already_verified: bool,
) -> dict[str, Any]:
    command = source_retention_command(
        queue_dir=queue_dir,
        split=split,
        source_cards=source_cards,
        source_report=source_report,
        source_summary=source_summary,
        context_source_dir=context_source_dir,
        source_retention_limit=source_retention_limit,
        workers=workers,
        dynamic_workers=dynamic_workers,
        dynamic_timeout_sec=dynamic_timeout_sec,
        context_completion_retries=context_completion_retries,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        temperature=temperature,
    )
    base = {
        "requested": run_requested,
        "already_verified": already_verified,
        "api_key_env": api_key_env,
        "api_key_configured": bool(os.getenv(api_key_env, "")),
        "command": printable_command(command),
        "stdout_log": str(stdout_log.resolve()),
        "stderr_log": str(stderr_log.resolve()),
    }
    if already_verified:
        return {**base, "status": "skipped_already_verified"}
    if not run_requested:
        return {**base, "status": "skipped_not_requested"}
    if not os.getenv(api_key_env, ""):
        return {**base, "status": "blocked_missing_api_key"}

    source_cards.parent.mkdir(parents=True, exist_ok=True)
    source_report.parent.mkdir(parents=True, exist_ok=True)
    source_summary.parent.mkdir(parents=True, exist_ok=True)
    context_source_dir.mkdir(parents=True, exist_ok=True)
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    stderr_log.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with stdout_log.open("w", encoding="utf-8", newline="\n") as stdout, stderr_log.open(
        "w", encoding="utf-8", newline="\n"
    ) as stderr:
        proc = subprocess.run(command, cwd=str(REPO_ROOT), stdout=stdout, stderr=stderr, text=True, env=env, check=False)
    return {**base, "status": "completed" if proc.returncode == 0 else "failed", "returncode": proc.returncode}


def source_retention_command(
    *,
    queue_dir: Path,
    split: str,
    source_cards: Path,
    source_report: Path,
    source_summary: Path,
    context_source_dir: Path,
    source_retention_limit: int,
    workers: int,
    dynamic_workers: int,
    dynamic_timeout_sec: int,
    context_completion_retries: int,
    model: str,
    base_url: str,
    api_key_env: str,
    temperature: float,
) -> list[str]:
    command = [
        sys.executable,
        "-B",
        str(REPO_ROOT / "scripts" / "run_error_cases_unordered.py"),
        "--dataset",
        str(queue_dir / "pairs.jsonl"),
        "--split-dir",
        str(queue_dir),
        "--splits",
        split,
        "--output",
        str(source_cards),
        "--report-path",
        str(source_report),
        "--summary-path",
        str(source_summary),
        "--workers",
        str(workers),
        "--dynamic-workers",
        str(dynamic_workers),
        "--with-dynamic",
        "--dynamic-mode",
        "execute",
        "--dynamic-timeout-sec",
        str(dynamic_timeout_sec),
        "--with-llm-context-completion",
        "--context-completion-retries",
        str(context_completion_retries),
        "--context-source-dir",
        str(context_source_dir),
        "--model",
        model,
        "--base-url",
        base_url,
        "--api-key-env",
        api_key_env,
        "--temperature",
        str(temperature),
        "--resume",
        "--resume-usable-only",
    ]
    if source_retention_limit:
        command.extend(["--limit", str(source_retention_limit)])
    return command


def run_execution_stage(
    *,
    dataset: Path,
    candidates_jsonl: Path,
    source_cards: Path,
    output_jsonl: Path,
    summary_path: Path,
    report_path: Path,
    source_dir: Path,
    readiness: dict[str, Any],
    skip_execution: bool,
    execution_limit: int,
    execution_offset: int,
    execution_workers: int,
    probe_timeout_sec: int,
    include_review: bool,
    with_llm_probe: bool,
    llm_probe_retries: int,
    model: str,
    base_url: str,
    api_key_env: str,
    temperature: float,
    keep_work: bool,
    reuse_existing_execution: bool,
) -> dict[str, Any]:
    ready = int((readiness.get("summary") or {}).get("execution_ready") or 0)
    if skip_execution:
        return {"status": "skipped_by_request", "ready_candidates": ready}
    if ready <= 0:
        return {"status": "skipped_no_ready_candidates", "ready_candidates": ready}
    reusable = reusable_execution_summary(
        summary_path=summary_path,
        output_jsonl=output_jsonl,
        execution_limit=execution_limit,
        execution_offset=execution_offset,
        include_review=include_review,
        with_llm_probe=with_llm_probe,
    )
    if reuse_existing_execution and reusable:
        return reusable
    return run_probe_synthesis_execution(
        dataset=dataset,
        candidates_jsonl=candidates_jsonl,
        source_cards_jsonl=source_cards,
        output_jsonl=output_jsonl,
        summary_path=summary_path,
        report_path=report_path,
        source_dir=source_dir,
        limit=execution_limit,
        offset=execution_offset,
        workers=execution_workers,
        timeout_sec=probe_timeout_sec,
        include_review=include_review,
        with_llm_probe=with_llm_probe,
        llm_retries=llm_probe_retries,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        api_key="",
        temperature=temperature,
        keep_work=keep_work,
        resume=reuse_existing_execution and not (execution_limit or execution_offset),
    )


def reusable_execution_summary(
    *,
    summary_path: Path,
    output_jsonl: Path,
    execution_limit: int,
    execution_offset: int,
    include_review: bool,
    with_llm_probe: bool,
) -> dict[str, Any]:
    if execution_limit or execution_offset:
        return {}
    if not summary_path.exists() or not output_jsonl.exists():
        return {}
    summary = read_json(summary_path)
    if summary.get("schema_version") != "eviclone-probe-synthesis-execution-summary/v1":
        return {}
    if summary.get("status") not in {"completed", "completed_with_warnings"}:
        return {}
    config = summary.get("configuration") if isinstance(summary.get("configuration"), dict) else {}
    if bool(config.get("include_review")) != bool(include_review):
        return {}
    if bool(config.get("with_llm_probe")) != bool(with_llm_probe):
        return {}
    outputs = summary.get("outputs") if isinstance(summary.get("outputs"), dict) else {}
    if outputs.get("results") and Path(str(outputs["results"])).name != output_jsonl.name:
        return {}
    result_state = jsonl_result_state(output_jsonl)
    summary_block = summary.get("summary") if isinstance(summary.get("summary"), dict) else {}
    candidate_count = int_or_none(summary_block.get("candidate_count"))
    executed = int_or_none(summary_block.get("executed"))
    benefit = int_or_none(summary_block.get("benefit"))
    harm = int_or_none(summary_block.get("harm"))
    if candidate_count is None or candidate_count <= 0:
        return {}
    if result_state["bad_lines"] or result_state["records"] != candidate_count:
        return {}
    if any(value is None for value in (executed, benefit, harm)):
        return {}
    if not (0 <= benefit <= executed <= candidate_count and 0 <= harm <= executed):
        return {}
    return {
        **summary,
        "reuse": {
            "status": "reused_existing_execution",
            "summary_path": str(summary_path.resolve()),
            "results_path": str(output_jsonl.resolve()),
        },
    }


def overall_status(
    queue_verification: dict[str, Any],
    source_audit: dict[str, Any],
    readiness: dict[str, Any],
    execution: dict[str, Any],
) -> str:
    if queue_verification.get("status") != "verified":
        return "queue_not_verified"
    ready_count = int((readiness.get("summary") or {}).get("execution_ready") or 0)
    if source_audit.get("status") != "source_artifacts_verified" and ready_count <= 0:
        return "source_retention_required"
    if readiness.get("status") not in {"execution_ready", "partial"}:
        return "no_execution_ready"
    execution_status = execution.get("status")
    if execution_status in {"completed", "completed_with_warnings"}:
        if source_audit.get("status") != "source_artifacts_verified":
            return "partial_probe_execution_completed"
        return str(execution_status)
    if source_audit.get("status") != "source_artifacts_verified" and ready_count > 0:
        return "partial_probe_execution_pending"
    return str(execution_status or "execution_not_completed")


def jsonl_result_state(path: Path) -> dict[str, int]:
    records = 0
    bad_lines = 0
    if not path.exists():
        return {"records": 0, "bad_lines": 1}
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError:
                bad_lines += 1
                continue
            records += 1
    return {"records": records, "bad_lines": bad_lines}


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def metric_delta(execution: dict[str, Any]) -> dict[str, int]:
    summary = execution.get("summary") if isinstance(execution.get("summary"), dict) else {}
    return {
        "candidate_count": int(summary.get("candidate_count") or 0),
        "executed": int(summary.get("executed") or 0),
        "benefit": int(summary.get("benefit") or 0),
        "harm": int(summary.get("harm") or 0),
        "net_gain": int(summary.get("net_gain") or 0),
    }


def next_action(
    source_audit: dict[str, Any],
    readiness: dict[str, Any],
    execution: dict[str, Any],
    *,
    source_run: dict[str, Any],
    run_source_retention: bool,
) -> dict[str, str]:
    ready_count = int((readiness.get("summary") or {}).get("execution_ready") or 0)
    if source_audit.get("status") != "source_artifacts_verified" and ready_count <= 0:
        if source_run.get("status") == "blocked_missing_api_key":
            return {"stage": "source_retention", "action": "configure LLM_API_KEY and rerun with --run-source-retention"}
        if source_run.get("status") == "failed":
            return {"stage": "source_retention", "action": "inspect source-retention stdout/stderr logs and rerun with --resume"}
        if run_source_retention:
            return {"stage": "source_retention", "action": "inspect source-retention logs and rerun with --resume"}
        return {"stage": "source_retention", "action": "rerun with --run-source-retention after configuring LLM_API_KEY"}
    if ready_count <= 0:
        return {"stage": "readiness", "action": "inspect readiness blockers and source artifact hashes"}
    if execution.get("status") not in {"completed", "completed_with_warnings"}:
        return {"stage": "probe_execution", "action": "run without --skip-execution or inspect probe execution blockers"}
    if source_audit.get("status") != "source_artifacts_verified":
        return {
            "stage": "module_lowering",
            "action": "use partial metric_delta now, then improve retained-source completion and probe helper synthesis for blocked candidates.",
        }
    return {"stage": "done", "action": "use metric_delta and execution results in the final evaluation"}


def resolve_source_retention_paths(
    *,
    queue_dir: Path,
    output_dir: Path,
    requested_output_dir: Path | None = None,
) -> dict[str, Path]:
    if requested_output_dir is not None:
        if requested_output_dir.is_absolute():
            root = requested_output_dir
        else:
            parts = requested_output_dir.parts
            if parts and parts[0] == output_dir.name:
                root = output_dir.joinpath(*parts[1:]) if len(parts) > 1 else output_dir
            elif path_is_relative_to(requested_output_dir, output_dir) or requested_output_dir.exists():
                root = requested_output_dir
            else:
                root = output_dir / requested_output_dir
    elif (queue_dir / DEFAULT_CARDS_NAME).exists():
        root = queue_dir
    else:
        root = output_dir / "source_retention"
    return {
        "output_dir": root,
        "cards": root / DEFAULT_CARDS_NAME,
        "report": root / "configured_llm_probe_source_retention_cards.report.md",
        "summary": root / "configured_llm_probe_source_retention_cards.summary.json",
        "context_sources": root / "context_sources",
    }


def path_is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def pipeline_paths(output_dir: Path) -> dict[str, Path]:
    return {
        "summary": output_dir / "probe_synthesis_full_pipeline.summary.json",
        "report": output_dir / "probe_synthesis_full_pipeline.md",
        "readiness": output_dir / DEFAULT_READINESS_JSON.name,
        "readiness_report": output_dir / DEFAULT_READINESS_REPORT.name,
        "execution_results": output_dir / "probe_synthesis_execution_results.jsonl",
        "execution_summary": output_dir / "probe_synthesis_execution.summary.json",
        "execution_report": output_dir / "probe_synthesis_execution.md",
        "source_retention_stdout": output_dir / "source_retention.stdout.log",
        "source_retention_stderr": output_dir / "source_retention.stderr.log",
    }


def prepare_output_dir(requested: Path) -> Path:
    candidates = [requested, Path("probe_synthesis_closed_loop")]
    last_error: PermissionError | None = None
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write_probe"
            probe.write_text("ok\n", encoding="utf-8", newline="\n")
            probe.unlink()
            return candidate
        except PermissionError as exc:
            last_error = exc
            continue
    if last_error is not None:
        raise last_error
    raise PermissionError(f"no writable output directory found for {requested}")


def write_pipeline_report(path: Path, result: dict[str, Any]) -> None:
    readiness_summary = result["readiness"].get("summary") or {}
    execution_delta = result.get("metric_delta") or {}
    source_audit = result["source_retention"]["audit"]
    source_checks = source_audit.get("checks") or {}
    lines = [
        "# Probe Synthesis Full Pipeline",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Stage Status",
        "",
        "| stage | status |",
        "| --- | --- |",
        f"| queue verification | {result['queue']['verification'].get('status')} |",
        f"| source retention run | {result['source_retention']['run'].get('status')} |",
        f"| source retention audit | {source_audit.get('status')} |",
        f"| readiness | {result['readiness'].get('status')} |",
        f"| probe execution | {result['execution'].get('status')} |",
        "",
        "## Source Retention",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| expected_cards | {source_checks.get('expected_cards', 0)} |",
        f"| actual_cards | {source_checks.get('actual_cards', 0)} |",
        f"| source_artifact_verified | {source_checks.get('source_artifact_verified', 0)} |",
        f"| missing_cards | {source_checks.get('missing_cards', 0)} |",
        "",
        "## Readiness",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| candidate_count | {readiness_summary.get('candidate_count', 0)} |",
        f"| execution_ready | {readiness_summary.get('execution_ready', 0)} |",
        f"| blocked | {readiness_summary.get('blocked', 0)} |",
        f"| source_retention_missing | {readiness_summary.get('source_retention_missing', 0)} |",
        "",
        "## Metric Delta",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| candidate_count | {execution_delta.get('candidate_count', 0)} |",
        f"| executed | {execution_delta.get('executed', 0)} |",
        f"| benefit | {execution_delta.get('benefit', 0)} |",
        f"| harm | {execution_delta.get('harm', 0)} |",
        f"| net_gain | {execution_delta.get('net_gain', 0)} |",
        "",
        "## Next Action",
        "",
        f"- stage: `{result['next_action']['stage']}`",
        f"- action: {result['next_action']['action']}",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def printable_command(command: list[str]) -> list[str]:
    return ["python" if part == sys.executable else part for part in command]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    raise SystemExit(main())
