from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.config import DEFAULT_API_KEY_ENV, DEFAULT_BASE_URL, DEFAULT_MODEL  # noqa: E402
from scripts.build_probe_source_retention_rerun_queue import (  # noqa: E402
    DEFAULT_CANDIDATES,
    DEFAULT_DATASET,
    DEFAULT_OUTPUT_DIR as DEFAULT_QUEUE_DIR,
    DEFAULT_SPLIT,
)
from scripts.build_probe_synthesis_plan import DEFAULT_OUTPUT as DEFAULT_PROBE_PLAN  # noqa: E402
from scripts.build_probe_synthesis_plan import DEFAULT_RUN_DIR  # noqa: E402
from scripts.check_probe_source_retention_experiment import check_probe_source_retention_experiment  # noqa: E402
from scripts.run_probe_synthesis_full_pipeline import DEFAULT_OUTPUT_DIR  # noqa: E402

DEFAULT_OUTPUT = Path("source_retention_progress_audit.json")
DEFAULT_REPORT = Path("source_retention_progress_audit.md")
DEFAULT_SOURCE_RECOVERABILITY_AUDIT = Path("probe_source_recoverability_audit.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit source-retention launch/progress state for the full probe pipeline.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--probe-plan", type=Path, default=DEFAULT_PROBE_PLAN)
    parser.add_argument("--queue-dir", type=Path, default=DEFAULT_QUEUE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--source-retention-output-dir", type=Path, default=Path("probe_synthesis_closed_loop") / "source_retention")
    parser.add_argument("--source-recoverability-audit", type=Path, default=DEFAULT_SOURCE_RECOVERABILITY_AUDIT)
    parser.add_argument("--split", type=str, default=DEFAULT_SPLIT)
    parser.add_argument("--workers", type=int, default=500)
    parser.add_argument("--dynamic-workers", type=int, default=32)
    parser.add_argument("--dynamic-timeout-sec", type=int, default=8)
    parser.add_argument("--context-completion-retries", type=int, default=3)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key-env", type=str, default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    audit = build_source_retention_progress_audit(
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
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_report(args.report, audit)
    print(
        json.dumps(
            {
                "status": audit["status"],
                "output": str(args.output.resolve()),
                "report": str(args.report.resolve()),
                "verified": audit["progress"]["verified_sidecars"],
                "expected": audit["progress"]["expected_sidecars"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if args.strict_exit and audit["status"] not in {"source_retention_complete_ready_for_probe_execution", "ready_to_start_online_source_retention"}:
        return 2
    return 0


def build_source_retention_progress_audit(
    *,
    run_dir: Path = DEFAULT_RUN_DIR,
    dataset: Path = DEFAULT_DATASET,
    candidates_jsonl: Path = DEFAULT_CANDIDATES,
    probe_plan_json: Path = DEFAULT_PROBE_PLAN,
    queue_dir: Path = DEFAULT_QUEUE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    source_retention_output_dir: Path | None = Path("probe_synthesis_closed_loop") / "source_retention",
    source_recoverability_audit: Path = DEFAULT_SOURCE_RECOVERABILITY_AUDIT,
    split: str = DEFAULT_SPLIT,
    workers: int = 500,
    dynamic_workers: int = 32,
    dynamic_timeout_sec: int = 8,
    context_completion_retries: int = 3,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    api_key_env: str = DEFAULT_API_KEY_ENV,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    preflight = check_probe_source_retention_experiment(
        run_dir=run_dir,
        dataset=dataset,
        candidates_jsonl=candidates_jsonl,
        probe_plan_json=probe_plan_json,
        queue_dir=queue_dir,
        output_dir=output_dir,
        source_retention_output_dir=source_retention_output_dir,
        source_recoverability_audit=source_recoverability_audit,
        split=split,
        workers=workers,
        dynamic_workers=dynamic_workers,
        dynamic_timeout_sec=dynamic_timeout_sec,
        context_completion_retries=context_completion_retries,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        include_review=True,
        with_llm_probe=True,
        now=now,
    )
    source_audit = preflight.get("source_retention_audit") if isinstance(preflight.get("source_retention_audit"), dict) else {}
    checks = source_audit.get("checks") if isinstance(source_audit.get("checks"), dict) else {}
    progress = progress_block(preflight=preflight, checks=checks)
    status = progress_status(preflight=preflight, progress=progress, source_audit=source_audit)
    return {
        "schema_version": "eviclone-source-retention-progress-audit/v1",
        "status": status,
        "created_at_utc": now.isoformat(),
        "preflight_status": preflight.get("status"),
        "source_retention_audit_status": source_audit.get("status"),
        "paths": preflight.get("paths") or {},
        "progress": progress,
        "launch_conditions": {
            "queue_verified": nested_get(preflight, ["checks", "queue_verified"]),
            "output_writable": nested_get(preflight, ["checks", "selected_source_retention_output_dir_writable"]),
            "context_source_dir_writable": nested_get(preflight, ["checks", "selected_context_source_dir_writable"]),
            "java_available": nested_get(preflight, ["checks", "java_available"]),
            "javac_available": nested_get(preflight, ["checks", "javac_available"]),
            "api_key_configured": nested_get(preflight, ["checks", "api_key_configured"]),
            "api_key_is_not_serialized": nested_get(preflight, ["checks", "api_key_is_not_serialized"]),
        },
        "recommended_command": preflight.get("recommended_command") or {},
        "next_action": next_action_for(status),
        "interpretation": interpretation_for(status),
    }


def progress_block(*, preflight: dict[str, Any], checks: dict[str, Any]) -> dict[str, Any]:
    expected = int(checks.get("expected_cards") or nested_get(preflight, ["source_retention_audit", "summary", "expected_cards"]) or 0)
    actual = int(checks.get("actual_cards") or nested_get(preflight, ["source_retention_audit", "summary", "actual_cards"]) or 0)
    missing = int(checks.get("missing_cards") or nested_get(preflight, ["source_retention_audit", "summary", "missing_cards"]) or max(0, expected - actual))
    verified = int(
        checks.get("source_artifact_verified")
        or nested_get(preflight, ["source_retention_audit", "summary", "source_artifact_verified"])
        or 0
    )
    drift = int(checks.get("source_hash_drift") or nested_get(preflight, ["source_retention_audit", "summary", "source_hash_drift"]) or 0)
    unexpected = int(checks.get("unexpected_cards") or nested_get(preflight, ["source_retention_audit", "summary", "unexpected_cards"]) or 0)
    return {
        "expected_sidecars": expected,
        "actual_cards": actual,
        "missing_cards": missing,
        "verified_sidecars": verified,
        "source_hash_drift": drift,
        "unexpected_cards": unexpected,
        "actual_card_rate": actual / expected if expected else 0.0,
        "verified_sidecar_rate": verified / expected if expected else 0.0,
        "remaining_sidecars": max(0, expected - verified),
    }


def progress_status(*, preflight: dict[str, Any], progress: dict[str, Any], source_audit: dict[str, Any]) -> str:
    expected = int(progress["expected_sidecars"])
    actual = int(progress["actual_cards"])
    verified = int(progress["verified_sidecars"])
    if not nested_get(preflight, ["checks", "queue_verified"]):
        return "blocked_queue_not_verified"
    if expected <= 0:
        return "no_source_retention_candidates"
    if progress["unexpected_cards"] or source_audit.get("issue_counts", {}).get("error", 0):
        return "source_retention_outputs_need_repair"
    if verified == expected:
        return "source_retention_complete_ready_for_probe_execution"
    if actual > 0:
        return "source_retention_in_progress_resume_online_run"
    if not nested_get(preflight, ["checks", "selected_source_retention_output_dir_writable"]):
        return "blocked_output_not_writable"
    if not nested_get(preflight, ["checks", "java_available"]) or not nested_get(preflight, ["checks", "javac_available"]):
        return "blocked_missing_java_toolchain"
    if not nested_get(preflight, ["checks", "api_key_configured"]):
        return "not_started_blocked_missing_api_key"
    return "ready_to_start_online_source_retention"


def next_action_for(status: str) -> dict[str, str]:
    if status == "source_retention_complete_ready_for_probe_execution":
        return {"stage": "probe_execution", "action": "Run scripts/run_system_readiness_pipeline.py without --online-source-retention to execute ready probes and refresh metrics."}
    if status == "source_retention_in_progress_resume_online_run":
        return {"stage": "source_retention", "action": "Resume scripts/run_system_readiness_pipeline.py --online-source-retention; the underlying runner uses --resume."}
    if status == "ready_to_start_online_source_retention":
        return {"stage": "source_retention", "action": "Run scripts/run_system_readiness_pipeline.py --online-source-retention."}
    if status == "not_started_blocked_missing_api_key":
        return {"stage": "source_retention", "action": "Set LLM_API_KEY, then run scripts/run_system_readiness_pipeline.py --online-source-retention."}
    if status == "source_retention_outputs_need_repair":
        return {"stage": "source_retention", "action": "Inspect hard source_retention_audit issues, repair/remove bad cards, then resume online run."}
    return {"stage": "preflight", "action": "Fix launch conditions reported by source_retention_progress_audit.json."}


def interpretation_for(status: str) -> str:
    if status == "source_retention_complete_ready_for_probe_execution":
        return "All expected retained source sidecars are verified; probe execution can proceed."
    if status == "source_retention_in_progress_resume_online_run":
        return "Some retained source cards exist; continue the online run with resume semantics."
    if status == "ready_to_start_online_source_retention":
        return "All local launch conditions are satisfied; online source-retention can start."
    if status == "not_started_blocked_missing_api_key":
        return "No retained source sidecars exist yet, and the current shell has no OpenAI-compatible LLM API key configured."
    if status == "source_retention_outputs_need_repair":
        return "Cards or sidecars exist but contain hard audit errors that must be repaired before probe execution."
    return f"Source-retention progress status is {status}."


def write_report(path: Path, audit: dict[str, Any]) -> None:
    progress = audit["progress"]
    lines = [
        "# Source Retention Progress Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Progress",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| expected_sidecars | {progress['expected_sidecars']} |",
        f"| actual_cards | {progress['actual_cards']} |",
        f"| verified_sidecars | {progress['verified_sidecars']} |",
        f"| missing_cards | {progress['missing_cards']} |",
        f"| remaining_sidecars | {progress['remaining_sidecars']} |",
        f"| verified_sidecar_rate | {progress['verified_sidecar_rate']:.6f} |",
        "",
        "## Launch Conditions",
        "",
        "| condition | value |",
        "| --- | --- |",
    ]
    for key, value in audit["launch_conditions"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Next Action",
            "",
            f"- stage: `{audit['next_action']['stage']}`",
            f"- action: {audit['next_action']['action']}",
            "",
            "## Interpretation",
            "",
            audit["interpretation"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def nested_get(obj: Any, path: list[str]) -> Any:
    cur = obj
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


if __name__ == "__main__":
    raise SystemExit(main())
