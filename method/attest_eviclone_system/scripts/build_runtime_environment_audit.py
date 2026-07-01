from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.config import DEFAULT_API_KEY_ENV  # noqa: E402

DEFAULT_OUTPUT = Path("runtime_environment_audit.json")
DEFAULT_REPORT = Path("runtime_environment_audit.md")

ACCEPTED_STATUSES = {
    "runtime_environment_ready",
    "runtime_environment_ready_online_key_missing",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the local runtime environment used by artifact evaluation.")
    parser.add_argument("--api-key-env", type=str, default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    audit = build_runtime_environment_audit(api_key_env=args.api_key_env)
    write_json(args.output, audit)
    write_report(args.report, audit)
    print(json.dumps({"status": audit["status"], "output": str(args.output.resolve())}, ensure_ascii=False, indent=2))
    if args.strict_exit and audit["status"] not in ACCEPTED_STATUSES:
        return 2
    return 0


def build_runtime_environment_audit(
    *,
    api_key_env: str = DEFAULT_API_KEY_ENV,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    java_path = shutil.which("java")
    javac_path = shutil.which("javac")
    key_present = bool(os.environ.get(api_key_env, ""))
    writable = {
        "repo_root": path_writable(REPO_ROOT),
        "temp_dir": path_writable(Path(tempfile.gettempdir())),
    }
    checks = {
        "python_executable_exists": Path(sys.executable).exists(),
        "python_version_supported": sys.version_info >= (3, 10),
        "repo_root_writable": writable["repo_root"],
        "temp_dir_writable": writable["temp_dir"],
        "java_available": bool(java_path),
        "javac_available": bool(javac_path),
        "api_key_env_name_recorded_only": api_key_env == DEFAULT_API_KEY_ENV or api_key_env.isidentifier(),
        "api_key_configured": key_present,
    }
    hard_check_names = [
        "python_executable_exists",
        "python_version_supported",
        "repo_root_writable",
        "temp_dir_writable",
        "java_available",
        "javac_available",
        "api_key_env_name_recorded_only",
    ]
    hard_failed = [name for name in hard_check_names if not checks[name]]
    status = status_for(hard_failed=hard_failed, api_key_configured=key_present)
    return {
        "schema_version": "eviclone-runtime-environment-audit/v1",
        "status": status,
        "created_at_utc": now.isoformat(),
        "summary": {
            "hard_failed_checks": len(hard_failed),
            "online_key_missing": not key_present,
            "java_available": bool(java_path),
            "javac_available": bool(javac_path),
            "python_version": platform.python_version(),
        },
        "runtime": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "repo_root": str(REPO_ROOT.resolve()),
            "temp_dir": tempfile.gettempdir(),
            "java": java_path or "",
            "javac": javac_path or "",
            "api_key_env": api_key_env,
            "api_key_configured": key_present,
        },
        "checks": checks,
        "hard_failed_checks": hard_failed,
        "interpretation": interpretation_for(status),
    }


def status_for(*, hard_failed: list[str], api_key_configured: bool) -> str:
    if hard_failed:
        return "runtime_environment_failed"
    if not api_key_configured:
        return "runtime_environment_ready_online_key_missing"
    return "runtime_environment_ready"


def path_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / f".eviclone_write_probe_{os.getpid()}"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def interpretation_for(status: str) -> str:
    if status == "runtime_environment_ready":
        return "The local runtime has Python, Java/Javac, writable directories, and an online API key configured."
    if status == "runtime_environment_ready_online_key_missing":
        return "The local runtime can execute offline artifacts; the online 860-case run remains blocked because the API key is not configured."
    return "At least one hard runtime requirement is missing; inspect hard_failed_checks."


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Runtime Environment Audit",
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
    lines.extend(["", "## Checks", "", "| check | value |", "| --- | --- |"])
    for key, value in audit["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Runtime", "", "| field | value |", "| --- | --- |"])
    for key, value in audit["runtime"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Interpretation", "", audit["interpretation"], ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
