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

DEFAULT_SOURCE_PROGRESS = Path("source_retention_progress_audit.json")
DEFAULT_PROBE_SUMMARY = (
    Path("eviclone_runs")
    / "codebert_error_cases_full"
    / "probe_synthesis_closed_loop"
    / "probe_synthesis_full_pipeline.summary.json"
)
DEFAULT_MANIFEST = Path("reproducibility_manifest.json")
DEFAULT_OUTPUT = Path("probe_execution_manifest_audit.json")
DEFAULT_REPORT = Path("probe_execution_manifest_audit.md")

FINAL_PROBE_STATUSES = {"paper_results_ready", "completed", "completed_with_warnings"}
ACCEPTED_STATUSES = {
    "probe_execution_manifest_blocked_on_source_retention",
    "probe_execution_manifest_final_ready",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit full probe execution evidence against manifest-backed result files.")
    parser.add_argument("--source-progress", type=Path, default=DEFAULT_SOURCE_PROGRESS)
    parser.add_argument("--probe-summary", type=Path, default=DEFAULT_PROBE_SUMMARY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    audit = build_probe_execution_manifest_audit(
        source_progress=args.source_progress,
        probe_summary=args.probe_summary,
        manifest=args.manifest,
    )
    write_json(args.output, audit)
    write_report(args.report, audit)
    print(json.dumps({"status": audit["status"], "output": str(args.output.resolve())}, ensure_ascii=False, indent=2))
    if args.strict_exit and audit["status"] not in ACCEPTED_STATUSES:
        return 2
    return 0


def build_probe_execution_manifest_audit(
    *,
    source_progress: Path = DEFAULT_SOURCE_PROGRESS,
    probe_summary: Path = DEFAULT_PROBE_SUMMARY,
    manifest: Path = DEFAULT_MANIFEST,
    artifact_overrides: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    overrides = artifact_overrides or {}
    progress = overrides.get("source_progress", read_json(source_progress))
    probe = overrides.get("probe_summary", read_json(probe_summary))
    manifest_payload = overrides.get("manifest", read_json(manifest))

    expected = int_or_zero(nested(progress, ["progress", "expected_sidecars"]))
    verified = int_or_zero(nested(progress, ["progress", "verified_sidecars"]))
    source_complete = expected > 0 and verified == expected
    metric = metric_delta(probe)
    manifest_rows = manifest_artifact_rows(manifest_payload)
    artifacts = [attach_file_and_manifest_state(row, manifest_rows) for row in probe_artifact_rows(probe)]
    checks = build_checks(
        expected=expected,
        verified=verified,
        source_complete=source_complete,
        probe=probe,
        metric=metric,
        artifacts=artifacts,
    )
    status = status_for(checks=checks, source_complete=source_complete)
    return {
        "schema_version": "eviclone-probe-execution-manifest-audit/v1",
        "status": status,
        "created_at_utc": now.isoformat(),
        "summary": {
            "source_expected_sidecars": expected,
            "source_verified_sidecars": verified,
            "source_complete": source_complete,
            "probe_status": str(probe.get("status") or ""),
            "executed": metric.get("executed", 0),
            "benefit": metric.get("benefit", 0),
            "harm": metric.get("harm", 0),
            "net_gain": metric.get("net_gain", 0),
            "probe_artifact_count": len(artifacts),
            "existing_probe_artifacts": sum(1 for row in artifacts if row["exists"]),
            "manifest_declared_probe_artifacts": sum(1 for row in artifacts if row["manifest_backed"]),
            "fingerprinted_probe_artifacts": sum(1 for row in artifacts if row["manifest_sha256"]),
            "missing_execution_artifacts": sum(1 for row in final_execution_artifacts(artifacts) if not row["exists"]),
            "missing_execution_manifest_artifacts": sum(
                1 for row in final_execution_artifacts(artifacts) if not row["manifest_backed"]
            ),
            "failed_checks": sum(1 for row in checks if row["status"] != "passed"),
        },
        "metric_delta": metric,
        "probe_artifacts": artifacts,
        "checks": checks,
        "interpretation": interpretation_for(status),
    }


def probe_artifact_rows(probe: dict[str, Any]) -> list[dict[str, str]]:
    outputs = probe.get("outputs") if isinstance(probe.get("outputs"), dict) else {}
    return [
        {
            "kind": "pipeline_summary",
            "required_stage": "always",
            "path": str(outputs.get("summary") or DEFAULT_PROBE_SUMMARY),
        },
        {
            "kind": "pipeline_report",
            "required_stage": "always",
            "path": str(outputs.get("report") or DEFAULT_PROBE_SUMMARY.with_suffix(".md")),
        },
        {
            "kind": "execution_summary",
            "required_stage": "final",
            "path": str(outputs.get("execution_summary") or ""),
        },
        {
            "kind": "execution_results",
            "required_stage": "final",
            "path": str(outputs.get("execution_results") or ""),
        },
        {
            "kind": "execution_report",
            "required_stage": "final",
            "path": str(outputs.get("execution_report") or ""),
        },
    ]


def final_execution_artifacts(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in artifacts if row.get("required_stage") == "final"]


def attach_file_and_manifest_state(row: dict[str, str], manifest_rows: list[dict[str, Any]]) -> dict[str, Any]:
    path = str(row.get("path") or "")
    resolved = resolve_path(path) if path else Path("")
    manifest_row = find_manifest_row(path, manifest_rows)
    return {
        **row,
        "resolved_path": str(resolved) if path else "",
        "exists": bool(path and resolved.exists() and resolved.is_file()),
        "manifest_backed": manifest_row is not None,
        "manifest_label": str((manifest_row or {}).get("label") or ""),
        "manifest_sha256": str((manifest_row or {}).get("sha256") or ""),
    }


def manifest_artifact_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = manifest.get("artifacts")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def find_manifest_row(path: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    normalized = normalize_path(path)
    for row in rows:
        if normalize_path(str(row.get("path") or "")) == normalized:
            return row
    return None


def build_checks(
    *,
    expected: int,
    verified: int,
    source_complete: bool,
    probe: dict[str, Any],
    metric: dict[str, int],
    artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    always_artifacts = [row for row in artifacts if row.get("required_stage") == "always"]
    final_artifacts = final_execution_artifacts(artifacts)
    return [
        check("PEM1_source_retention_target_recorded", expected > 0, {"expected_sidecars": expected}),
        check(
            "PEM2_metric_delta_shape_valid",
            metric_delta_is_valid(probe),
            {"metric_delta": probe.get("metric_delta")},
        ),
        check(
            "PEM3_pipeline_summary_report_manifest_backed",
            all(row["exists"] and row["manifest_backed"] and row["manifest_sha256"] for row in always_artifacts),
            {"artifacts": always_artifacts},
        ),
        check(
            "PEM4_incomplete_source_retention_defers_execution_gate",
            source_complete or (expected > 0 and verified < expected),
            {"verified_sidecars": verified, "expected_sidecars": expected, "source_complete": source_complete},
        ),
        check(
            "PEM5_complete_probe_status_final",
            (not source_complete) or str(probe.get("status") or "") in FINAL_PROBE_STATUSES,
            {"probe_status": probe.get("status"), "accepted": sorted(FINAL_PROBE_STATUSES)},
        ),
        check(
            "PEM6_complete_probe_execution_measured",
            (not source_complete) or metric_measured(metric),
            {"metric_delta": metric},
        ),
        check(
            "PEM7_complete_execution_artifacts_exist",
            (not source_complete) or all(row["path"] and row["exists"] for row in final_artifacts),
            {"missing": [row for row in final_artifacts if not row["path"] or not row["exists"]]},
        ),
        check(
            "PEM8_complete_execution_artifacts_manifest_backed",
            (not source_complete)
            or all(row["manifest_backed"] and row["manifest_sha256"] for row in final_artifacts),
            {"missing_manifest": [row for row in final_artifacts if not row["manifest_backed"] or not row["manifest_sha256"]]},
        ),
    ]


def metric_delta(probe: dict[str, Any]) -> dict[str, int]:
    raw = probe.get("metric_delta") if isinstance(probe.get("metric_delta"), dict) else {}
    return {key: int_or_zero(raw.get(key)) for key in ("candidate_count", "executed", "benefit", "harm", "net_gain")}


def metric_delta_is_valid(probe: dict[str, Any]) -> bool:
    raw = probe.get("metric_delta")
    if not isinstance(raw, dict):
        return False
    required = {"candidate_count", "executed", "benefit", "harm", "net_gain"}
    if not required <= set(raw):
        return False
    try:
        values = {key: int(raw[key]) for key in required}
    except (TypeError, ValueError):
        return False
    return (
        min(values.values()) >= 0
        and values["candidate_count"] >= values["executed"]
        and values["executed"] >= values["benefit"]
        and values["executed"] >= values["harm"]
        and values["net_gain"] == values["benefit"] - values["harm"]
    )


def metric_measured(metric: dict[str, int]) -> bool:
    return (
        metric.get("executed", 0) > 0
        and metric.get("candidate_count", 0) >= metric.get("executed", 0)
        and metric.get("executed", 0) >= metric.get("benefit", 0)
        and metric.get("executed", 0) >= metric.get("harm", 0)
        and metric.get("net_gain", 0) == metric.get("benefit", 0) - metric.get("harm", 0)
    )


def check(check_id: str, condition: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"id": check_id, "status": "passed" if condition else "failed", "evidence": evidence}


def status_for(*, checks: list[dict[str, Any]], source_complete: bool) -> str:
    if any(row["status"] != "passed" for row in checks):
        return "probe_execution_manifest_failed"
    return "probe_execution_manifest_final_ready" if source_complete else "probe_execution_manifest_blocked_on_source_retention"


def interpretation_for(status: str) -> str:
    if status == "probe_execution_manifest_blocked_on_source_retention":
        return "Full probe execution result files are deferred until the 860 retained-source sidecars are complete."
    if status == "probe_execution_manifest_final_ready":
        return "Full probe execution metrics and execution result files are present, measured, and manifest-backed."
    return "The probe execution evidence contract is broken and must be repaired before final result promotion."


def resolve_path(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def normalize_path(path: str) -> str:
    if not path:
        return ""
    try:
        resolved = resolve_path(path).resolve(strict=False)
    except OSError:
        resolved = resolve_path(path)
    return str(resolved).replace("/", "\\").casefold()


def read_json(path: Path) -> dict[str, Any]:
    resolved = path if path.is_absolute() else REPO_ROOT / path
    try:
        obj = json.loads(resolved.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return obj if isinstance(obj, dict) else {}


def nested(obj: Any, path: list[str]) -> Any:
    cur = obj
    for part in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Probe Execution Manifest Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
    ]
    for key, value in audit["summary"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Probe Artifacts", "", "| kind | stage | exists | manifest backed | sha256 | path |", "| --- | --- | ---: | ---: | --- | --- |"])
    for row in audit["probe_artifacts"]:
        sha = row["manifest_sha256"][:12] if row["manifest_sha256"] else ""
        lines.append(
            f"| {row['kind']} | {row['required_stage']} | {row['exists']} | {row['manifest_backed']} | `{sha}` | `{row['path']}` |"
        )
    lines.extend(["", "## Checks", "", "| check | status |", "| --- | --- |"])
    for row in audit["checks"]:
        lines.append(f"| `{row['id']}` | `{row['status']}` |")
    lines.extend(["", "## Interpretation", "", audit["interpretation"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
