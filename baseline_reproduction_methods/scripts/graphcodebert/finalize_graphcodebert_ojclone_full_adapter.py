from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path("eviclone_runs") / "baseline_reproduction"
AUDIT_PATH = ROOT / "graphcodebert_ojclone_cpp_dataflow_full_adapter_audit.json"
DEFAULT_OUTPUT = ROOT / "graphcodebert_ojclone_full_adapter_finalize_status.json"
DEFAULT_REPORT = ROOT / "graphcodebert_ojclone_full_adapter_finalize_status.md"
DEFAULT_WRITING_REPORT = (
    Path("paper_writing_workdir") / "67_graphcodebert_ojclone_full_adapter_finalize.md"
)
README_PATH = Path("paper_writing_workdir") / "README.md"

AUDIT_COMMAND = ["scripts/build_graphcodebert_ojclone_cpp_dataflow_full_adapter_audit.py"]
READY_STATUS = "ready_for_variant_table_cell"

REFRESH_COMMANDS = [
    ["scripts/build_external_sota_repro_preflight.py"],
    ["scripts/build_sota_external_method_source_audit.py"],
    ["scripts/build_sota_unsupported_dataset_adapters.py"],
    ["scripts/build_paper_comparison_long_table.py"],
    ["scripts/build_paper_ready_baseline_tables.py"],
    ["scripts/build_baseline_table_cell_audit.py"],
    ["scripts/build_reproduction_table_completion_audit.py"],
    ["scripts/build_remaining_baseline_gap_runbook.py"],
    ["scripts/build_main_dataset_non_llm_completion_queue.py"],
    ["scripts/build_main_dataset_non_llm_sota_table.py"],
    ["scripts/build_main_dataset_non_llm_sota_table_audit.py"],
    ["scripts/build_baseline_reproduction_command_bundle.py"],
    ["scripts/build_baseline_external_artifact_acquisition_checklist.py"],
    ["scripts/build_baseline_manuscript_insert_audit.py"],
    ["scripts/build_baseline_table_deliverable_pack.py"],
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Finalize the GraphCodeBERT/OJClone full adapter result only after "
            "predictions and A/P/R/F1 metrics are present."
        )
    )
    parser.add_argument(
        "--allow-not-ready",
        action="store_true",
        help="Return success when the adapter audit is not ready; useful for polling.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the readiness audit but print the refresh commands instead of executing them.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--writing-report", type=Path, default=DEFAULT_WRITING_REPORT)
    args = parser.parse_args()

    audit_result = run_python(AUDIT_COMMAND)
    audit = read_json(AUDIT_PATH)
    status = str(audit.get("status") or "missing_audit_status")
    failed = int((audit.get("summary") or {}).get("failed") or 0)

    if status != READY_STATUS or failed != 0:
        payload = {
            "status": "not_ready",
            "adapter_audit_status": status,
            "failed_checks": failed,
            "missing_ready_artifacts": audit.get("missing_ready_artifacts") or [],
            "live_progress": (audit.get("summary") or {}).get("live_progress") or {},
            "audit_command": audit_result,
            "audit_path": str(AUDIT_PATH),
            "finalize_commands_after_ready": [format_command(command) for command in REFRESH_COMMANDS],
        }
        payload["readme_progress_sync"] = sync_readme_progress(payload)
        write_outputs(payload, args.output, args.report, args.writing_report)
        print_json(payload)
        return 0 if args.allow_not_ready else 2

    if args.dry_run:
        payload = {
            "status": "ready_dry_run",
            "adapter_audit_status": status,
            "commands": [format_command(command) for command in REFRESH_COMMANDS],
        }
        write_outputs(payload, args.output, args.report, args.writing_report)
        print_json(payload, indent=2)
        return 0

    completed = []
    for command in REFRESH_COMMANDS:
        completed.append(run_python(command))

    payload = {
        "status": "finalized",
        "adapter_audit_status": status,
        "completed_commands": completed,
        "audit_path": str(AUDIT_PATH),
    }
    write_outputs(payload, args.output, args.report, args.writing_report)
    print_json(payload)
    return 0


def run_python(args: list[str]) -> dict[str, Any]:
    command = [sys.executable, *args]
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    return {
        "command": format_command(args),
        "returncode": result.returncode,
    }


def format_command(args: list[str]) -> str:
    return "python " + " ".join(args)


def print_json(payload: dict[str, Any], *, indent: int | None = None) -> None:
    print(json.dumps(payload, ensure_ascii=True, indent=indent, sort_keys=True))


def write_outputs(payload: dict[str, Any], output: Path, report: Path, writing_report: Path | None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_markdown(payload, output)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(markdown, encoding="utf-8")
    if writing_report:
        writing_report.parent.mkdir(parents=True, exist_ok=True)
        writing_report.write_text(markdown, encoding="utf-8")


def render_markdown(payload: dict[str, Any], output: Path) -> str:
    lines = [
        "# GraphCodeBERT OJClone Full Adapter Finalize Status",
        "",
        f"Status: `{payload.get('status')}`",
        "",
        "This file records the post-training finalization gate for the project-defined "
        "GraphCodeBERT/OJClone C++ data-flow adapter. It must not promote a table "
        "cell until the readiness audit reports zero failed checks.",
        "",
        "## Gate",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| adapter_audit_status | `{payload.get('adapter_audit_status')}` |",
        f"| failed_checks | `{payload.get('failed_checks', 0)}` |",
        f"| audit_path | `{payload.get('audit_path')}` |",
        f"| output | `{output.as_posix()}` |",
        "",
    ]
    missing = payload.get("missing_ready_artifacts") or []
    if missing:
        lines.extend(["## Missing Ready Artifacts", "", "| Artifact |", "| --- |"])
        lines.extend(f"| `{artifact}` |" for artifact in missing)
        lines.append("")
    progress = payload.get("live_progress") or {}
    if progress:
        lines.extend(["## Live Progress", "", "| Metric | Value |", "| --- | ---: |"])
        for key in ["epoch", "step", "total_steps", "progress_percent", "loss", "it_per_second"]:
            lines.append(f"| {key} | {progress.get(key)} |")
        lines.extend(
            [
                f"| elapsed | `{progress.get('elapsed')}` |",
                f"| eta | `{progress.get('eta')}` |",
                "",
            ]
        )
    commands = payload.get("finalize_commands_after_ready") or payload.get("commands") or []
    if commands:
        lines.extend(["## Commands After Ready", "", "| Command |", "| --- |"])
        lines.extend(f"| `{command}` |" for command in commands)
        lines.append("")
    completed = payload.get("completed_commands") or []
    if completed:
        lines.extend(["## Completed Commands", "", "| Command | Return code |", "| --- | ---: |"])
        for item in completed:
            lines.append(f"| `{item.get('command')}` | {item.get('returncode')} |")
        lines.append("")
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    return obj if isinstance(obj, dict) else {}


def sync_readme_progress(payload: dict[str, Any]) -> str:
    progress = payload.get("live_progress") or {}
    step = progress.get("step")
    total = progress.get("total_steps")
    percent = progress.get("progress_percent")
    if not README_PATH.exists():
        return "missing_readme"
    if step is None or total is None or percent is None:
        return "missing_live_progress"

    text = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(The refreshed audit also records live progress from the retained train log; "
        r"at the latest rebuild it was at )[\d,]+/[\d,]+ training steps \([0-9.]+%\)"
        r"( with no timing/prediction/metric artifacts yet\.)"
    )

    def replace(match: re.Match[str]) -> str:
        return (
            f"{match.group(1)}{int(step):,}/{int(total):,} training steps "
            f"({float(percent):.3f}%){match.group(2)}"
        )

    updated, count = pattern.subn(replace, text, count=1)
    if count != 1:
        return "marker_not_found"
    if updated == text:
        return "unchanged"
    README_PATH.write_text(updated, encoding="utf-8")
    return "updated"


if __name__ == "__main__":
    raise SystemExit(main())
