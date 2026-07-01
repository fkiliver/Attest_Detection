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
DEFAULT_RUN_PLAN = Path("source_retention_run_plan.json")
DEFAULT_MANIFEST = Path("reproducibility_manifest.json")
DEFAULT_OUTPUT = Path("retained_source_manifest_audit.json")
DEFAULT_REPORT = Path("retained_source_manifest_audit.md")

ACCEPTED_STATUSES = {
    "retained_source_manifest_blocked_online",
    "retained_source_manifest_final_ready",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit retained-source sidecar files against the reproducibility manifest.")
    parser.add_argument("--source-progress", type=Path, default=DEFAULT_SOURCE_PROGRESS)
    parser.add_argument("--run-plan", type=Path, default=DEFAULT_RUN_PLAN)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    audit = build_retained_source_manifest_audit(
        source_progress=args.source_progress,
        run_plan=args.run_plan,
        manifest=args.manifest,
    )
    write_json(args.output, audit)
    write_report(args.report, audit)
    print(json.dumps({"status": audit["status"], "output": str(args.output.resolve())}, ensure_ascii=False, indent=2))
    if args.strict_exit and audit["status"] not in ACCEPTED_STATUSES:
        return 2
    return 0


def build_retained_source_manifest_audit(
    *,
    source_progress: Path = DEFAULT_SOURCE_PROGRESS,
    run_plan: Path = DEFAULT_RUN_PLAN,
    manifest: Path = DEFAULT_MANIFEST,
    artifact_overrides: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    overrides = artifact_overrides or {}
    progress = overrides.get("source_progress", read_json(source_progress))
    plan = overrides.get("run_plan", read_json(run_plan))
    manifest_payload = overrides.get("manifest", read_json(manifest))
    expected = int_or_zero(nested(progress, ["progress", "expected_sidecars"]))
    verified = int_or_zero(nested(progress, ["progress", "verified_sidecars"]))
    complete = expected > 0 and verified == expected
    source_artifacts = source_artifact_rows(plan)
    manifest_rows = manifest_artifact_rows(manifest_payload)
    source_artifacts = [attach_file_and_manifest_state(row, manifest_rows) for row in source_artifacts]
    checks = build_checks(expected=expected, verified=verified, complete=complete, source_artifacts=source_artifacts)
    status = status_for(checks=checks, complete=complete)
    return {
        "schema_version": "eviclone-retained-source-manifest-audit/v1",
        "status": status,
        "created_at_utc": now.isoformat(),
        "summary": {
            "expected_sidecars": expected,
            "verified_sidecars": verified,
            "complete": complete,
            "source_artifact_count": len(source_artifacts),
            "existing_source_artifacts": sum(1 for row in source_artifacts if row["exists"]),
            "manifest_backed_source_artifacts": sum(1 for row in source_artifacts if row["manifest_backed"]),
            "missing_source_artifacts": sum(1 for row in source_artifacts if not row["exists"]),
            "missing_manifest_artifacts": sum(1 for row in source_artifacts if not row["manifest_backed"]),
            "failed_checks": sum(1 for row in checks if row["status"] != "passed"),
        },
        "source_artifacts": source_artifacts,
        "checks": checks,
        "interpretation": interpretation_for(status),
    }


def source_artifact_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    paths = plan.get("paths") if isinstance(plan.get("paths"), dict) else {}
    specs = [
        ("source_cards", "retained_source_cards"),
        ("source_summary", "retained_source_summary"),
        ("source_report", "retained_source_report"),
    ]
    return [
        {
            "kind": kind,
            "path": str(paths.get(key) or ""),
        }
        for key, kind in specs
    ]


def attach_file_and_manifest_state(row: dict[str, Any], manifest_rows: list[dict[str, Any]]) -> dict[str, Any]:
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
    complete: bool,
    source_artifacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        check("RSM1_expected_sidecar_target_recorded", expected > 0, {"expected_sidecars": expected}),
        check(
            "RSM2_source_artifact_paths_declared",
            len(source_artifacts) == 3 and all(row["path"] for row in source_artifacts),
            {"source_artifacts": source_artifacts},
        ),
        check(
            "RSM3_incomplete_source_retention_keeps_manifest_gate_deferred",
            complete or (verified < expected and expected > 0),
            {"verified_sidecars": verified, "expected_sidecars": expected, "complete": complete},
        ),
        check(
            "RSM4_complete_source_artifacts_exist",
            (not complete) or all(row["exists"] for row in source_artifacts),
            {"missing": [row for row in source_artifacts if not row["exists"]]},
        ),
        check(
            "RSM5_complete_source_artifacts_manifest_backed",
            (not complete) or all(row["manifest_backed"] and row["manifest_sha256"] for row in source_artifacts),
            {"missing_manifest": [row for row in source_artifacts if not row["manifest_backed"] or not row["manifest_sha256"]]},
        ),
    ]


def check(check_id: str, condition: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"id": check_id, "status": "passed" if condition else "failed", "evidence": evidence}


def status_for(*, checks: list[dict[str, Any]], complete: bool) -> str:
    if any(row["status"] != "passed" for row in checks):
        return "retained_source_manifest_failed"
    return "retained_source_manifest_final_ready" if complete else "retained_source_manifest_blocked_online"


def interpretation_for(status: str) -> str:
    if status == "retained_source_manifest_blocked_online":
        return "Retained-source files are not required in the manifest until the 860-sidecar online stage completes."
    if status == "retained_source_manifest_final_ready":
        return "The retained-source cards, summary, and report are present and manifest-backed."
    return "The retained-source manifest contract is broken and must be repaired before final result promotion."


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
        "# Retained Source Manifest Audit",
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
    lines.extend(["", "## Source Artifacts", "", "| kind | exists | manifest backed | sha256 | path |", "| --- | ---: | ---: | --- | --- |"])
    for row in audit["source_artifacts"]:
        sha = row["manifest_sha256"][:12] if row["manifest_sha256"] else ""
        lines.append(f"| {row['kind']} | {row['exists']} | {row['manifest_backed']} | `{sha}` | `{row['path']}` |")
    lines.extend(["", "## Checks", "", "| check | status |", "| --- | --- |"])
    for row in audit["checks"]:
        lines.append(f"| `{row['id']}` | `{row['status']}` |")
    lines.extend(["", "## Interpretation", "", audit["interpretation"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
