from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.config import DEFAULT_API_KEY_ENV, DEFAULT_BASE_URL, DEFAULT_MODEL  # noqa: E402
from scripts.audit_probe_source_retention_outputs import audit_probe_source_retention_outputs  # noqa: E402
from scripts.build_probe_source_retention_rerun_queue import (  # noqa: E402
    DEFAULT_CANDIDATES,
    DEFAULT_DATASET,
    DEFAULT_OUTPUT_DIR as DEFAULT_QUEUE_DIR,
    DEFAULT_SPLIT,
)
from scripts.build_probe_synthesis_plan import DEFAULT_OUTPUT as DEFAULT_PROBE_PLAN  # noqa: E402
from scripts.build_probe_synthesis_plan import DEFAULT_RUN_DIR  # noqa: E402
from scripts.run_probe_synthesis_full_pipeline import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    prepare_output_dir,
    resolve_source_retention_paths,
)
from scripts.verify_probe_source_retention_rerun_queue import verify_probe_source_retention_rerun_queue  # noqa: E402

DEFAULT_OUTPUT = Path("probe_source_retention_experiment_preflight.json")
DEFAULT_REPORT = Path("probe_source_retention_experiment_preflight.md")
DEFAULT_SOURCE_RECOVERABILITY_AUDIT = Path("probe_source_recoverability_audit.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight the 860-case probe source-retention experiment.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--probe-plan", type=Path, default=DEFAULT_PROBE_PLAN)
    parser.add_argument("--queue-dir", type=Path, default=DEFAULT_QUEUE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--source-retention-output-dir", type=Path, default=None)
    parser.add_argument("--source-recoverability-audit", type=Path, default=DEFAULT_SOURCE_RECOVERABILITY_AUDIT)
    parser.add_argument("--split", type=str, default=DEFAULT_SPLIT)
    parser.add_argument("--workers", type=int, default=500)
    parser.add_argument("--dynamic-workers", type=int, default=32)
    parser.add_argument("--dynamic-timeout-sec", type=int, default=8)
    parser.add_argument("--context-completion-retries", type=int, default=3)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key-env", type=str, default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--include-review", action="store_true", default=True)
    parser.add_argument("--with-llm-probe", action="store_true", default=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    result = check_probe_source_retention_experiment(
        run_dir=args.run_dir,
        dataset=args.dataset,
        candidates_jsonl=args.candidates,
        probe_plan_json=args.probe_plan,
        queue_dir=args.queue_dir,
        output_dir=args.output_dir,
        source_retention_output_dir=args.source_retention_output_dir,
        source_recoverability_audit=args.source_recoverability_audit,
        split=args.split,
        workers=args.workers,
        dynamic_workers=args.dynamic_workers,
        dynamic_timeout_sec=args.dynamic_timeout_sec,
        context_completion_retries=args.context_completion_retries,
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        include_review=args.include_review,
        with_llm_probe=args.with_llm_probe,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_report(args.report, result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": str(args.output.resolve()),
                "report": str(args.report.resolve()),
                "source_retention_output_dir": result["paths"]["source_retention_output_dir"],
                "api_key_configured": result["checks"]["api_key_configured"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.strict_exit and result["status"] not in {"ready_to_run_source_retention", "source_retention_done"}:
        return 2
    return 0


def check_probe_source_retention_experiment(
    *,
    run_dir: Path = DEFAULT_RUN_DIR,
    dataset: Path = DEFAULT_DATASET,
    candidates_jsonl: Path = DEFAULT_CANDIDATES,
    probe_plan_json: Path = DEFAULT_PROBE_PLAN,
    queue_dir: Path = DEFAULT_QUEUE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    source_retention_output_dir: Path | None = None,
    source_recoverability_audit: Path = DEFAULT_SOURCE_RECOVERABILITY_AUDIT,
    split: str = DEFAULT_SPLIT,
    workers: int = 500,
    dynamic_workers: int = 32,
    dynamic_timeout_sec: int = 8,
    context_completion_retries: int = 3,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    api_key_env: str = DEFAULT_API_KEY_ENV,
    include_review: bool = True,
    with_llm_probe: bool = True,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    requested_output_dir = output_dir
    actual_output_dir = prepare_output_dir(output_dir)
    source_paths = resolve_source_retention_paths(
        queue_dir=queue_dir,
        output_dir=actual_output_dir,
        requested_output_dir=source_retention_output_dir,
    )
    queue_verification = verify_probe_source_retention_rerun_queue(queue_dir=queue_dir, split=split)
    source_audit = audit_probe_source_retention_outputs(queue_dir=queue_dir, cards_path=source_paths["cards"])
    recoverability = read_json(source_recoverability_audit)
    checks = {
        "queue_verified": queue_verification.get("status") == "verified",
        "queue_dir_writable": path_writable(queue_dir),
        "selected_source_retention_output_dir_writable": path_writable(source_paths["output_dir"]),
        "selected_context_source_dir_writable": path_writable(source_paths["context_sources"]),
        "api_key_env": api_key_env,
        "api_key_configured": bool(os.getenv(api_key_env, "")),
        "api_key_is_not_serialized": True,
        "java_available": bool(shutil.which("java")),
        "javac_available": bool(shutil.which("javac")),
        "existing_source_retention_status": source_audit.get("status"),
        "source_recoverability_status": recoverability.get("status") or "missing",
        "source_recoverable_count": int(((recoverability.get("summary") or {}).get("recoverable_count")) or 0),
        "source_recoverable_rate": float(((recoverability.get("summary") or {}).get("recoverable_rate")) or 0.0),
    }
    command = recommended_pipeline_command(
        run_dir=run_dir,
        dataset=dataset,
        candidates_jsonl=candidates_jsonl,
        probe_plan_json=probe_plan_json,
        queue_dir=queue_dir,
        output_dir=actual_output_dir,
        source_retention_output_dir=source_paths["output_dir"],
        split=split,
        workers=workers,
        dynamic_workers=dynamic_workers,
        dynamic_timeout_sec=dynamic_timeout_sec,
        context_completion_retries=context_completion_retries,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        include_review=include_review,
        with_llm_probe=with_llm_probe,
    )
    return {
        "schema_version": "eviclone-probe-source-retention-experiment-preflight/v1",
        "status": preflight_status(checks),
        "created_at_utc": now.isoformat(),
        "paths": {
            "run_dir": str(run_dir.resolve()),
            "dataset": str(dataset.resolve()),
            "candidates_jsonl": str(candidates_jsonl.resolve()),
            "probe_plan_json": str(probe_plan_json.resolve()),
            "queue_dir": str(queue_dir.resolve()),
            "requested_output_dir": str(requested_output_dir.resolve()),
            "output_dir": str(actual_output_dir.resolve()),
            "source_retention_output_dir": str(source_paths["output_dir"].resolve()),
            "source_cards": str(source_paths["cards"].resolve()),
            "source_report": str(source_paths["report"].resolve()),
            "source_summary": str(source_paths["summary"].resolve()),
            "context_source_dir": str(source_paths["context_sources"].resolve()),
            "source_recoverability_audit": str(source_recoverability_audit.resolve()),
        },
        "configuration": {
            "split": split,
            "workers": workers,
            "dynamic_workers": dynamic_workers,
            "dynamic_timeout_sec": dynamic_timeout_sec,
            "context_completion_retries": context_completion_retries,
            "model": model,
            "base_url": base_url,
            "api_key_env": api_key_env,
            "include_review": include_review,
            "with_llm_probe": with_llm_probe,
        },
        "checks": checks,
        "queue_verification": queue_verification,
        "source_retention_audit": source_audit,
        "source_recoverability_audit_summary": recoverability.get("summary") or {},
        "recommended_command": {
            "description": "Run the full source-retention, readiness, execution, and metric-delta pipeline.",
            "argv": command,
            "powershell": powershell_command(command),
        },
        "next_action": next_action_for_status(preflight_status(checks), api_key_env=api_key_env),
    }


def preflight_status(checks: dict[str, Any]) -> str:
    if not checks.get("queue_verified"):
        return "blocked_queue_not_verified"
    if checks.get("existing_source_retention_status") == "source_artifacts_verified":
        return "source_retention_done"
    if not checks.get("selected_source_retention_output_dir_writable") or not checks.get("selected_context_source_dir_writable"):
        return "blocked_output_not_writable"
    if not checks.get("java_available") or not checks.get("javac_available"):
        return "blocked_missing_java_toolchain"
    if not checks.get("api_key_configured"):
        return "blocked_missing_api_key"
    return "ready_to_run_source_retention"


def recommended_pipeline_command(
    *,
    run_dir: Path,
    dataset: Path,
    candidates_jsonl: Path,
    probe_plan_json: Path,
    queue_dir: Path,
    output_dir: Path,
    source_retention_output_dir: Path,
    split: str,
    workers: int,
    dynamic_workers: int,
    dynamic_timeout_sec: int,
    context_completion_retries: int,
    model: str,
    base_url: str,
    api_key_env: str,
    include_review: bool,
    with_llm_probe: bool,
) -> list[str]:
    command = [
        "python",
        "-B",
        command_path(REPO_ROOT / "scripts" / "run_probe_synthesis_full_pipeline.py"),
        "--run-dir",
        command_path(run_dir),
        "--dataset",
        command_path(dataset),
        "--candidates",
        command_path(candidates_jsonl),
        "--probe-plan",
        command_path(probe_plan_json),
        "--queue-dir",
        command_path(queue_dir),
        "--output-dir",
        command_path(output_dir),
        "--source-retention-output-dir",
        command_path(source_retention_output_dir),
        "--split",
        split,
        "--run-source-retention",
        "--workers",
        str(workers),
        "--dynamic-workers",
        str(dynamic_workers),
        "--dynamic-timeout-sec",
        str(dynamic_timeout_sec),
        "--context-completion-retries",
        str(context_completion_retries),
        "--model",
        model,
        "--base-url",
        base_url,
        "--api-key-env",
        api_key_env,
    ]
    if include_review:
        command.append("--include-review")
    if with_llm_probe:
        command.append("--with-llm-probe")
    return command


def command_path(path: Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        return str(candidate)
    try:
        return str(candidate.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(candidate)


def next_action_for_status(status: str, *, api_key_env: str) -> str:
    if status == "blocked_queue_not_verified":
        return "Rebuild or verify probe_source_retention_rerun_queue before launching the 860-case run."
    if status == "blocked_output_not_writable":
        return "Choose a writable --source-retention-output-dir outside the queue directory."
    if status == "blocked_missing_java_toolchain":
        return "Install or expose java and javac on PATH before probe execution."
    if status == "blocked_missing_api_key":
        return f"Set {api_key_env} in the shell environment, then run recommended_command.powershell."
    if status == "source_retention_done":
        return "Run the full pipeline without --run-source-retention or proceed to readiness/probe execution."
    return "Run recommended_command.powershell to start the full source-retention experiment."


def path_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_probe"
        probe.write_text("ok\n", encoding="utf-8", newline="\n")
        probe.unlink()
        return True
    except OSError:
        return False


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except json.JSONDecodeError:
        return {}
    return obj if isinstance(obj, dict) else {}


def powershell_command(argv: list[str]) -> str:
    return " ".join(ps_quote(part) for part in argv)


def ps_quote(value: str) -> str:
    if value == "":
        return "''"
    if all(ch.isalnum() or ch in "-_./:\\\\" for ch in value):
        return value
    return "'" + value.replace("'", "''") + "'"


def write_report(path: Path, result: dict[str, Any]) -> None:
    checks = result["checks"]
    source_summary = (result.get("source_retention_audit") or {}).get("summary") or {}
    lines = [
        "# Probe Source-Retention Experiment Preflight",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Checks",
        "",
        "| check | value |",
        "| --- | ---: |",
        f"| queue_verified | {checks['queue_verified']} |",
        f"| queue_dir_writable | {checks['queue_dir_writable']} |",
        f"| selected_source_retention_output_dir_writable | {checks['selected_source_retention_output_dir_writable']} |",
        f"| selected_context_source_dir_writable | {checks['selected_context_source_dir_writable']} |",
        f"| api_key_configured | {checks['api_key_configured']} |",
        f"| java_available | {checks['java_available']} |",
        f"| javac_available | {checks['javac_available']} |",
        f"| source_recoverable_count | {checks['source_recoverable_count']} |",
        "",
        "## Source Retention Target",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| existing_status | {checks['existing_source_retention_status']} |",
        f"| expected_cards | {source_summary.get('expected_cards', 0)} |",
        f"| actual_cards | {source_summary.get('actual_cards', 0)} |",
        f"| missing_cards | {source_summary.get('missing_cards', 0)} |",
        "",
        "## Paths",
        "",
        f"- source_retention_output_dir: `{result['paths']['source_retention_output_dir']}`",
        f"- source_cards: `{result['paths']['source_cards']}`",
        f"- context_source_dir: `{result['paths']['context_source_dir']}`",
        "",
        "## Recommended Command",
        "",
        "```powershell",
        result["recommended_command"]["powershell"],
        "```",
        "",
        "## Next Action",
        "",
        result["next_action"],
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
