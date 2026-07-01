from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("eviclone_runs") / "baseline_reproduction" / "llm_direct_stratified_100"
DEFAULT_OUTPUT = DEFAULT_ROOT / "llm_direct_100_retained_suite.json"
DEFAULT_REPORT = DEFAULT_ROOT / "llm_direct_100_retained_suite.md"
DEFAULT_DATASETS = "BCB,OJClone,GCJ"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the retained LLM-direct 100-row suite and rebuild all I/O retention audits."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--datasets", default=DEFAULT_DATASETS)
    parser.add_argument("--api-key-env", default="LLM_API_KEY")
    parser.add_argument("--model", default="configured-llm")
    parser.add_argument("--base-url", default="https://llm-provider.example/v1")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=90)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--thinking-type", default="disabled")
    parser.add_argument("--policy", default="bcb-alignment")
    parser.add_argument("--abstain-label", choices=["0", "1"], default="0")
    parser.add_argument(
        "--decision-source",
        choices=["decision", "llm_pred", "llm_bcb_gold", "llm_semantic"],
        default="llm_bcb_gold",
    )
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--offline-export-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--render-existing", action="store_true", help="Render the report from the existing JSON without running commands.")
    parser.add_argument("--require-key", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    if args.render_existing:
        audit = read_json(args.output)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_markdown(audit), encoding="utf-8")
        print(
            json.dumps(
                {
                    "status": audit.get("status"),
                    "output": str(args.output),
                    "report": str(args.report),
                    "rendered_existing": True,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0 if audit.get("status") == "complete_outputs" else 2

    audit = build_audit(args)
    run_all(args, audit)
    summarize_state(args, audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_markdown(audit), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": audit["status"],
                "api_key_available": audit["api_key_available"],
                "online_calls_run": audit["online_calls_run"],
                "retention_status": nested_get(audit, ["retention_audit", "status"]),
                "output": str(args.output),
                "report": str(args.report),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    if audit["status"] == "complete_outputs":
        return 0
    if audit["status"] == "inputs_ready_key_missing" and not args.require_key:
        return 0
    if audit["status"] == "dry_run":
        return 0
    return 2


def build_audit(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema_version": "eviclone-llm-direct-100-retained-suite/v1",
        "status": "pending",
        "created_at_unix": int(time.time()),
        "root": str(args.root),
        "datasets": [item.strip() for item in args.datasets.split(",") if item.strip()],
        "api_key_env": args.api_key_env,
        "api_key_available": bool(os.environ.get(args.api_key_env)),
        "api_key_handling": (
            f"Only the environment variable name `{args.api_key_env}` is stored. The API key value is never written "
            "to commands, logs, reports, or JSON artifacts."
        ),
        "model": args.model,
        "base_url": args.base_url,
        "online_calls_run": False,
        "commands": [],
        "command_results": [],
        "claim_boundary": (
            "The 100-row LLM-direct package is not a table metric until all online cards, reconstructed "
            "prompt/output snapshots, exported predictions, metrics, and audits are complete."
        ),
    }


def run_all(args: argparse.Namespace, audit: dict[str, Any]) -> None:
    suite_audit = args.root / "llm_direct_suite_audit.json"
    suite_report = args.root / "llm_direct_suite_audit.md"
    io_audit = args.root / "llm_direct_io_retention_audit.json"
    io_report = args.root / "llm_direct_io_retention_audit.md"
    readiness_audit = args.root / "llm_direct_scaleup_readiness_audit.json"
    readiness_report = args.root / "llm_direct_scaleup_readiness_audit.md"

    suite_command = [
        sys.executable,
        "scripts/run_llm_direct_pilot_suite.py",
        "--root",
        str(args.root),
        "--datasets",
        args.datasets,
        "--audit",
        str(suite_audit),
        "--report",
        str(suite_report),
        "--workers",
        str(args.workers),
        "--llm-retries",
        str(args.llm_retries),
        "--timeout-sec",
        str(args.timeout_sec),
        "--model",
        args.model,
        "--base-url",
        args.base_url,
        "--api-key-env",
        args.api_key_env,
        "--temperature",
        str(args.temperature),
        "--max-tokens",
        str(args.max_tokens),
        "--thinking-type",
        args.thinking_type,
        "--policy",
        args.policy,
        "--abstain-label",
        args.abstain_label,
        "--decision-source",
        args.decision_source,
    ]
    if args.skip_existing:
        suite_command.append("--skip-existing")
    if args.offline_export_existing:
        suite_command.append("--offline-export-existing")
    if args.dry_run:
        suite_command.append("--dry-run")
    if args.require_key:
        suite_command.append("--require-key")

    io_command = [
        sys.executable,
        "scripts/build_llm_direct_io_retention_audit.py",
        "--stratified-root",
        str(args.root),
        "--datasets",
        args.datasets,
        "--force-snapshot",
        "--api-key-env",
        args.api_key_env,
        "--output",
        str(io_audit),
        "--report",
        str(io_report),
    ]
    readiness_command = [
        sys.executable,
        "scripts/build_llm_direct_scaleup_readiness_audit.py",
        "--root",
        str(args.root),
        "--datasets",
        args.datasets,
        "--api-key-env",
        args.api_key_env,
        "--output",
        str(readiness_audit),
        "--report",
        str(readiness_report),
    ]

    for stage, command, allow_incomplete in [
        ("suite", suite_command, False),
        ("io_retention_audit", io_command, True),
        ("scaleup_readiness_audit", readiness_command, True),
    ]:
        audit["commands"].append({"stage": stage, "command": sanitize_command(command)})
        result = run_command(stage=stage, command=command, allow_incomplete=allow_incomplete)
        audit["command_results"].append(result)
        if result["status"] == "failed":
            audit["status"] = "failed"
            return

    audit["online_calls_run"] = read_json(suite_audit).get("online_calls_run") if suite_audit.exists() else False
    audit["suite_audit_path"] = str(suite_audit)
    audit["retention_audit_path"] = str(io_audit)
    audit["readiness_audit_path"] = str(readiness_audit)
    audit["suite_audit"] = read_json(suite_audit) if suite_audit.exists() else {}
    audit["retention_audit"] = read_json(io_audit) if io_audit.exists() else {}
    audit["readiness_audit"] = read_json(readiness_audit) if readiness_audit.exists() else {}


def run_command(*, stage: str, command: list[str], allow_incomplete: bool) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output = proc.stdout[-8000:] if proc.stdout else ""
    expected_incomplete = allow_incomplete and proc.returncode in {0, 1, 2}
    return {
        "stage": stage,
        "returncode": proc.returncode,
        "elapsed_sec": round(time.time() - started, 3),
        "status": "ok" if proc.returncode == 0 or expected_incomplete else "failed",
        "stdout_tail": output,
    }


def summarize_state(args: argparse.Namespace, audit: dict[str, Any]) -> None:
    if audit.get("status") == "failed":
        return
    retention_status = nested_get(audit, ["retention_audit", "status"])
    retention_state = nested_get(audit, ["retention_audit", "online_execution_state"])
    readiness_status = nested_get(audit, ["readiness_audit", "status"])
    if args.dry_run:
        audit["status"] = "dry_run"
    elif retention_status == "complete":
        audit["status"] = "complete_outputs"
    elif not audit["api_key_available"] and retention_state == "inputs_ready_key_missing":
        audit["status"] = "inputs_ready_key_missing"
    elif readiness_status == "inputs_ready_key_present":
        audit["status"] = "inputs_ready_key_present_outputs_missing"
    else:
        audit["status"] = "incomplete_outputs"


def read_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj


def nested_get(obj: dict[str, Any], keys: list[str]) -> Any:
    current: Any = obj
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def sanitize_command(command: list[str]) -> list[str]:
    return [part for part in command]


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# LLM-Direct 100-Row Retained Suite",
        "",
        f"Status: `{audit['status']}`",
        "",
        audit["claim_boundary"],
        "",
        audit["api_key_handling"],
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| root | `{audit['root']}` |",
        f"| datasets | `{', '.join(audit['datasets'])}` |",
        f"| api_key_env | `{audit['api_key_env']}` |",
        f"| api_key_available | `{audit['api_key_available']}` |",
        f"| online_calls_run | `{audit['online_calls_run']}` |",
        f"| suite_audit | `{audit.get('suite_audit_path', '')}` |",
        f"| retention_audit | `{audit.get('retention_audit_path', '')}` |",
        f"| readiness_audit | `{audit.get('readiness_audit_path', '')}` |",
        "",
        "## Command Results",
        "",
        "| Stage | Status | Return code | Seconds |",
        "| --- | --- | ---: | ---: |",
    ]
    for item in audit["command_results"]:
        lines.append(
            "| {stage} | {status} | {returncode} | {elapsed_sec} |".format(
                stage=item["stage"],
                status=item["status"],
                returncode=item["returncode"],
                elapsed_sec=item["elapsed_sec"],
            )
        )
    lines.extend(["", "## Next Action", ""])
    if audit["status"] == "inputs_ready_key_missing":
        lines.append(
            f"Set `{audit['api_key_env']}` in the shell environment and rerun this script. Do not put the key value in commands or files."
        )
    elif audit["status"] == "complete_outputs":
        lines.append("Use the regenerated I/O retention audit and metrics for table review.")
    else:
        lines.append("Inspect the command results and regenerated audits before using any metric cell.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
