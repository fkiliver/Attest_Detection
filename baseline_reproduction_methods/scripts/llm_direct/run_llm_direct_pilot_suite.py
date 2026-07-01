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
DEFAULT_AUDIT = DEFAULT_ROOT / "llm_direct_suite_audit.json"
DEFAULT_REPORT = DEFAULT_ROOT / "llm_direct_suite_audit.md"
DATASET_NAMES = ["BCB", "OJClone", "GCJ"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run or audit the retained LLM-direct pilot suite with input/output retention."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--datasets", default=",".join(DATASET_NAMES))
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
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
        help="Card field used to export LLM-direct predictions. llm_bcb_gold excludes post-LLM EviClone guards.",
    )
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--offline-export-existing",
        action="store_true",
        help="Do not call the LLM; re-export predictions and metrics from retained cards.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--require-key",
        action="store_true",
        help="Return non-zero when the API key environment variable is missing.",
    )
    args = parser.parse_args()

    selected = [item.strip() for item in args.datasets.split(",") if item.strip()]
    audit = build_initial_audit(args=args, selected=selected)
    if args.dry_run:
        audit["status"] = "dry_run"
        audit["online_calls_run"] = False
    elif args.offline_export_existing:
        audit["online_calls_run"] = False
        audit["retained_online_cards_used"] = True
        run_offline_export_suite(args=args, audit=audit)
    elif not os.environ.get(args.api_key_env):
        audit["status"] = "skipped_missing_api_key"
        audit["online_calls_run"] = False
        audit["next_action"] = (
            f"Set {args.api_key_env} in the environment and rerun this script. Do not put the key in commands or files."
        )
    else:
        audit["online_calls_run"] = True
        run_suite(args=args, audit=audit)

    refresh_artifact_state(audit)
    write_outputs(audit, args.audit, args.report)
    print(
        json.dumps(
            {
                "status": audit["status"],
                "online_calls_run": audit["online_calls_run"],
                "datasets": len(audit["datasets"]),
                "complete_outputs": sum(1 for item in audit["datasets"] if item["output_complete"]),
                "audit": str(args.audit),
                "report": str(args.report),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    if audit["status"] == "complete":
        return 0
    if audit["status"] == "skipped_missing_api_key" and not args.require_key:
        return 0
    return 2 if audit["status"].startswith("failed") or args.require_key else 0


def build_initial_audit(*, args: argparse.Namespace, selected: list[str]) -> dict[str, Any]:
    datasets = []
    for name in selected:
        dataset_dir = args.root / name
        summary_path = dataset_dir / "summary.json"
        summary = read_json(summary_path) if summary_path.exists() else {}
        paths = dataset_paths(dataset_dir=dataset_dir, summary=summary)
        datasets.append(
            {
                "dataset": name,
                "dataset_dir": str(dataset_dir),
                "summary_path": str(summary_path),
                "source_rows": (summary.get("sampling") or {}).get("source_rows"),
                "rows": summary.get("rows"),
                "label_counts": summary.get("label_counts"),
                "input_paths": paths["inputs"],
                "output_paths": paths["outputs"],
                "commands": [],
                "command_results": [],
                "output_complete": False,
            }
        )
    return {
        "schema_version": "eviclone-llm-direct-pilot-suite-audit/v1",
        "status": "pending",
        "created_at_unix": int(time.time()),
        "root": str(args.root),
        "api_key_handling": (
            f"{args.api_key_env} environment variable only; the key is never written into commands, logs, or artifacts."
        ),
        "model": args.model,
        "base_url": args.base_url,
        "policy": args.policy,
        "abstain_label": int(args.abstain_label),
        "decision_source": args.decision_source,
        "online_calls_run": False,
        "claim_boundary": (
            "This suite is a balanced LLM-direct pilot with retained input and output artifacts. It is not a "
            "natural-distribution full-test leaderboard result."
        ),
        "datasets": datasets,
    }


def dataset_paths(*, dataset_dir: Path, summary: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "inputs": [
            str(Path(summary.get("dataset") or dataset_dir / "pairs.jsonl")),
            str(Path(summary.get("split_dir") or dataset_dir / "splits")),
            str(Path(summary.get("sampled_gold") or dataset_dir / "test.txt")),
            str(Path(summary.get("selected_rows") or dataset_dir / "selected_rows.jsonl")),
            str(dataset_dir / "summary.json"),
            str(dataset_dir / "README.md"),
        ],
        "outputs": [
            str(dataset_dir / "llm_direct_cards.jsonl"),
            str(dataset_dir / "llm_direct_cards.report.md"),
            str(dataset_dir / "llm_direct_predictions.txt"),
            str(dataset_dir / "llm_direct_predictions.summary.json"),
            str(dataset_dir / "llm_direct_metrics.json"),
            str(dataset_dir / "llm_direct_metrics.md"),
            str(dataset_dir / "llm_direct_suite_run.log"),
        ],
    }


def run_suite(*, args: argparse.Namespace, audit: dict[str, Any]) -> None:
    failed = False
    for item in audit["datasets"]:
        dataset_dir = Path(item["dataset_dir"])
        log_path = dataset_dir / "llm_direct_suite_run.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if args.skip_existing and all(Path(path).exists() for path in item["output_paths"][:6]):
            item["command_results"].append({"stage": "all", "status": "skipped_existing", "returncode": 0})
            continue

        run_command = [
            sys.executable,
            "scripts/run_llm_unordered.py",
            "--dataset",
            str(dataset_dir / "pairs.jsonl"),
            "--split-dir",
            str(dataset_dir / "splits"),
            "--splits",
            "test",
            "--output",
            str(dataset_dir / "llm_direct_cards.jsonl"),
            "--report-path",
            str(dataset_dir / "llm_direct_cards.report.md"),
            "--workers",
            str(args.workers),
            "--policy",
            args.policy,
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
        ]
        export_command = [
            sys.executable,
            "scripts/export_llm_direct_predictions_from_cards.py",
            "--cards",
            str(dataset_dir / "llm_direct_cards.jsonl"),
            "--gold",
            str(dataset_dir / "test.txt"),
            "--output",
            str(dataset_dir / "llm_direct_predictions.txt"),
            "--summary-path",
            str(dataset_dir / "llm_direct_predictions.summary.json"),
            "--abstain-label",
            args.abstain_label,
            "--decision-source",
            args.decision_source,
        ]
        metric_command = [
            sys.executable,
            "scripts/evaluate_triplet_predictions.py",
            "--gold",
            str(dataset_dir / "test.txt"),
            "--predictions",
            str(dataset_dir / "llm_direct_predictions.txt"),
            "--output",
            str(dataset_dir / "llm_direct_metrics.json"),
            "--report",
            str(dataset_dir / "llm_direct_metrics.md"),
            "--dataset",
            f"{item['dataset']}-stratified-pilot",
            "--method",
            "LLM-direct",
            "--source",
            args.model,
        ]
        item["commands"] = [sanitize_command(run_command), sanitize_command(export_command), sanitize_command(metric_command)]
        for stage, command in [
            ("online_cards", run_command),
            ("export_predictions", export_command),
            ("evaluate_metrics", metric_command),
        ]:
            result = run_command_with_log(command, log_path=log_path, stage=stage)
            item["command_results"].append(result)
            if result["returncode"] != 0:
                failed = True
                break
    audit["status"] = "failed_llm_direct_pilot_suite" if failed else "complete"


def run_offline_export_suite(*, args: argparse.Namespace, audit: dict[str, Any]) -> None:
    failed = False
    for item in audit["datasets"]:
        dataset_dir = Path(item["dataset_dir"])
        log_path = dataset_dir / "llm_direct_suite_run.log"
        cards_path = dataset_dir / "llm_direct_cards.jsonl"
        if not cards_path.exists():
            item["command_results"].append(
                {
                    "stage": "offline_cards_check",
                    "status": "missing_retained_cards",
                    "returncode": 2,
                    "log": str(log_path),
                }
            )
            failed = True
            continue
        export_command = export_predictions_command(args=args, dataset_dir=dataset_dir)
        metric_command = metric_command_for(args=args, item=item, dataset_dir=dataset_dir)
        item["commands"] = [sanitize_command(export_command), sanitize_command(metric_command)]
        for stage, command in [
            ("export_predictions_from_retained_cards", export_command),
            ("evaluate_metrics", metric_command),
        ]:
            result = run_command_with_log(command, log_path=log_path, stage=stage)
            item["command_results"].append(result)
            if result["returncode"] != 0:
                failed = True
                break
    audit["status"] = "failed_llm_direct_offline_export" if failed else "complete"


def export_predictions_command(*, args: argparse.Namespace, dataset_dir: Path) -> list[str]:
    return [
        sys.executable,
        "scripts/export_llm_direct_predictions_from_cards.py",
        "--cards",
        str(dataset_dir / "llm_direct_cards.jsonl"),
        "--gold",
        str(dataset_dir / "test.txt"),
        "--output",
        str(dataset_dir / "llm_direct_predictions.txt"),
        "--summary-path",
        str(dataset_dir / "llm_direct_predictions.summary.json"),
        "--abstain-label",
        args.abstain_label,
        "--decision-source",
        args.decision_source,
    ]


def metric_command_for(*, args: argparse.Namespace, item: dict[str, Any], dataset_dir: Path) -> list[str]:
    return [
        sys.executable,
        "scripts/evaluate_triplet_predictions.py",
        "--gold",
        str(dataset_dir / "test.txt"),
        "--predictions",
        str(dataset_dir / "llm_direct_predictions.txt"),
        "--output",
        str(dataset_dir / "llm_direct_metrics.json"),
        "--report",
        str(dataset_dir / "llm_direct_metrics.md"),
        "--dataset",
        f"{item['dataset']}-stratified-pilot",
        "--method",
        "LLM-direct",
        "--source",
        args.model,
    ]


def run_command_with_log(command: list[str], *, log_path: Path, stage: str) -> dict[str, Any]:
    started = time.time()
    with log_path.open("a", encoding="utf-8", newline="\n") as log:
        log.write(f"\n## {stage}\n")
        log.write(" ".join(sanitize_command(command)) + "\n")
        proc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, text=True)
    return {
        "stage": stage,
        "returncode": proc.returncode,
        "elapsed_sec": round(time.time() - started, 3),
        "log": str(log_path),
    }


def refresh_artifact_state(audit: dict[str, Any]) -> None:
    for item in audit["datasets"]:
        input_state = path_state(item["input_paths"])
        output_state = path_state(item["output_paths"])
        item["input_state"] = input_state
        item["output_state"] = output_state
        item["input_complete"] = input_state["missing_count"] == 0
        item["output_complete"] = output_state["missing_count"] == 0
        metrics_path = Path(item["dataset_dir"]) / "llm_direct_metrics.json"
        if metrics_path.exists():
            metrics_obj = read_json(metrics_path)
            item["metrics"] = metrics_obj.get("metrics")
            item["confusion"] = metrics_obj.get("confusion")
    if audit["status"] == "complete" and not all(item["output_complete"] for item in audit["datasets"]):
        audit["status"] = "failed_missing_output_artifacts"
    if audit["status"] == "skipped_missing_api_key":
        audit["claim_boundary"] = (
            "This suite has retained balanced LLM-direct input artifacts, but no online output cards, predictions, "
            "or metrics were generated because the API key environment variable was missing. It must not be used as "
            "a table F1 cell."
        )
    elif not all(item["output_complete"] for item in audit["datasets"]):
        audit["claim_boundary"] = (
            "This suite is incomplete: retained input artifacts exist, but at least one dataset lacks output cards, "
            "predictions, metrics, or logs. It must not be used as a table F1 cell."
        )


def path_state(paths: list[str]) -> dict[str, Any]:
    rows = []
    missing = 0
    for value in paths:
        path = Path(value)
        exists = path.exists()
        if not exists:
            missing += 1
        rows.append(
            {
                "path": value,
                "exists": exists,
                "size_bytes": path.stat().st_size if exists and path.is_file() else None,
            }
        )
    return {"total": len(rows), "missing_count": missing, "paths": rows}


def sanitize_command(command: list[str]) -> list[str]:
    sanitized = []
    skip_next = False
    for part in command:
        if skip_next:
            sanitized.append(part)
            skip_next = False
            continue
        sanitized.append(part)
        if part in {"--api-key-env"}:
            skip_next = True
    return sanitized


def read_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj


def write_outputs(audit: dict[str, Any], audit_path: Path, report_path: Path) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_markdown(audit), encoding="utf-8")


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# LLM-Direct Pilot Suite Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        audit["claim_boundary"],
        "",
        audit["api_key_handling"],
        "",
        "## Datasets",
        "",
        "| Dataset | Rows | Input | Output | F1 | Cards | Metrics |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for item in audit["datasets"]:
        metrics = item.get("metrics") or {}
        output_paths = {Path(path).name: path for path in item["output_paths"]}
        lines.append(
            "| {dataset} | {rows} | {input_ok} | {output_ok} | {f1} | `{cards}` | `{metrics_path}` |".format(
                dataset=item["dataset"],
                rows=item.get("rows") or "",
                input_ok="yes" if item.get("input_complete") else "no",
                output_ok="yes" if item.get("output_complete") else "no",
                f1=format_metric(metrics.get("f1")),
                cards=output_paths.get("llm_direct_cards.jsonl", ""),
                metrics_path=output_paths.get("llm_direct_metrics.json", ""),
            )
        )
    lines.extend(["", "## Next Action", "", audit.get("next_action", "No action required."), ""])
    return "\n".join(lines)


def format_metric(value: Any) -> str:
    if value is None or value == "":
        return ""
    return f"{float(value):.6f}"


if __name__ == "__main__":
    raise SystemExit(main())
