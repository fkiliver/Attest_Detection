from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dotenv_api_key import load_api_key_from_dotenv
from scripts.export_llm_direct_predictions_from_cards import label_from_card


DEFAULT_ROOT = Path("eviclone_runs") / "baseline_reproduction" / "llm_direct_fulltest"
DEFAULT_OUTPUT = DEFAULT_ROOT / "llm_direct_fulltest_suite_audit.json"
DEFAULT_REPORT = DEFAULT_ROOT / "llm_direct_fulltest_suite_audit.md"
DEFAULT_DATASETS = "BCB,OJClone,GCJ"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run, merge, and evaluate retained LLM-direct full-test shards.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--datasets", default=DEFAULT_DATASETS)
    parser.add_argument("--api-key-env", default="LLM_API_KEY")
    parser.add_argument("--dotenv", type=Path, default=None, help="Optional dotenv file to load only the configured API key variable from.")
    parser.add_argument("--model", default="configured-llm")
    parser.add_argument("--base-url", default="https://llm-provider.example/v1")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=90)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--thinking-type", default="disabled")
    parser.add_argument("--policy", default="bcb-alignment")
    parser.add_argument("--abstain-label", choices=["0", "1", "error"], default="0")
    parser.add_argument(
        "--decision-source",
        choices=["decision", "llm_pred", "llm_bcb_gold", "llm_semantic"],
        default="llm_bcb_gold",
    )
    parser.add_argument("--shard-id", type=int, action="append", default=None)
    parser.add_argument("--max-shards-per-dataset", type=int, default=None)
    parser.add_argument(
        "--next-incomplete-per-dataset",
        type=int,
        default=None,
        help="select the first N incomplete shards per dataset using retained usable card counts",
    )
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--merge-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--require-key", action="store_true")
    parser.add_argument("--skip-io-retention", action="store_true")
    parser.add_argument("--io-output", type=Path, default=DEFAULT_ROOT / "llm_direct_fulltest_io_retention_audit.json")
    parser.add_argument("--io-report", type=Path, default=DEFAULT_ROOT / "llm_direct_fulltest_io_retention_audit.md")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    dotenv_status = load_api_key_from_dotenv(args.dotenv, args.api_key_env)
    audit = build_initial_audit(args, dotenv_status=dotenv_status)
    run_suite(args, audit)
    summarize_outputs(audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_markdown(audit), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": audit["status"],
                "datasets": len(audit["datasets"]),
                "online_shards_run": audit["online_shards_run"],
                "complete_outputs": sum(1 for item in audit["datasets"] if item["output_complete"]),
                "output": str(args.output),
                "report": str(args.report),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    if audit["status"] in {"complete_outputs", "dry_run", "inputs_ready_key_missing"} and not args.require_key:
        return 0
    return 0 if audit["status"] == "complete_outputs" else 2


def build_initial_audit(args: argparse.Namespace, *, dotenv_status: dict[str, Any]) -> dict[str, Any]:
    selected = [item.strip() for item in args.datasets.split(",") if item.strip()]
    return {
        "schema_version": "eviclone-llm-direct-fulltest-suite-runner/v1",
        "status": "pending",
        "created_at_unix": int(time.time()),
        "root": str(args.root),
        "datasets_requested": selected,
        "api_key_env": args.api_key_env,
        "api_key_available": bool(os.environ.get(args.api_key_env)),
        "dotenv": dotenv_status,
        "api_key_handling": (
            f"Only the environment variable name {args.api_key_env} is stored. The key value is never written to "
            "commands, logs, reports, or JSON artifacts."
        ),
        "model": args.model,
        "base_url": args.base_url,
        "policy": args.policy,
        "decision_source": args.decision_source,
        "online_shards_run": 0,
        "commands": [],
        "io_retention": {},
        "datasets": [],
        "claim_boundary": (
            "This runner produces a full-test LLM-direct metric only when every shard for BCB, OJClone, and GCJ "
            "has retained cards and the merged per-dataset prompt/output snapshots, predictions, and metrics are "
            "complete."
        ),
    }


def run_suite(args: argparse.Namespace, audit: dict[str, Any]) -> None:
    if args.dry_run:
        audit["status"] = "dry_run"
    elif not args.merge_only and not audit["api_key_available"]:
        audit["status"] = "inputs_ready_key_missing"
        if args.require_key:
            return

    selected = set(audit["datasets_requested"])
    for dataset_dir in sorted(path for path in args.root.iterdir() if path.is_dir() and path.name in selected):
        item = dataset_item(args=args, dataset_dir=dataset_dir)
        audit["datasets"].append(item)
        if not args.merge_only and not args.dry_run and audit["api_key_available"]:
            run_selected_shards(args=args, audit=audit, item=item)
        merge_dataset_outputs(args=args, item=item, dry_run=args.dry_run)
    if not args.dry_run and not args.skip_io_retention:
        run_io_retention_audit(args=args, audit=audit)
        refresh_dataset_completion(audit)
    if audit["status"] == "pending":
        audit["status"] = "complete_outputs" if all(item["output_complete"] for item in audit["datasets"]) else "outputs_incomplete"


def dataset_item(*, args: argparse.Namespace, dataset_dir: Path) -> dict[str, Any]:
    summary_path = dataset_dir / "summary.json"
    manifest_path = dataset_dir / "shard_manifest.json"
    summary = read_json(summary_path)
    manifest = read_json(manifest_path)
    records = [row for row in manifest.get("records", []) if isinstance(row, dict)]
    selected_records = select_shards(
        records,
        shard_ids=args.shard_id,
        max_shards=args.max_shards_per_dataset,
        next_incomplete=args.next_incomplete_per_dataset,
        decision_source=args.decision_source,
        accept_abstain=args.abstain_label != "error",
    )
    return {
        "dataset": dataset_dir.name,
        "dataset_dir": str(dataset_dir),
        "summary_path": str(summary_path),
        "manifest_path": str(manifest_path),
        "rows": int(summary.get("rows") or 0),
        "label_counts": summary.get("label_counts") or {},
        "total_shards": len(records),
        "selection_mode": selection_mode(args),
        "all_shard_records": records,
        "selected_shards": [int(row.get("shard_id") or 0) for row in selected_records],
        "shard_records": selected_records,
        "command_results": [],
        "merge": {},
        "output_complete": False,
    }


def selection_mode(args: argparse.Namespace) -> str:
    if args.shard_id:
        return "explicit_shard_id"
    if args.next_incomplete_per_dataset is not None:
        return "next_incomplete"
    if args.max_shards_per_dataset is not None:
        return "manifest_prefix"
    return "all_manifest_shards"


def select_shards(
    records: list[dict[str, Any]],
    *,
    shard_ids: list[int] | None,
    max_shards: int | None,
    next_incomplete: int | None,
    decision_source: str,
    accept_abstain: bool,
) -> list[dict[str, Any]]:
    selected = records
    if shard_ids:
        wanted = set(shard_ids)
        selected = [row for row in selected if int(row.get("shard_id") or 0) in wanted]
    elif next_incomplete is not None:
        selected = [
            row
            for row in selected
            if not shard_is_complete(row, decision_source=decision_source, accept_abstain=accept_abstain)
        ][:next_incomplete]
    if max_shards is not None:
        selected = selected[:max_shards]
    return selected


def shard_is_complete(row: dict[str, Any], *, decision_source: str, accept_abstain: bool) -> bool:
    expected_rows = int(row.get("rows") or 0)
    if expected_rows <= 0:
        return False
    output_cards = Path(str(row.get("output_cards") or ""))
    return count_unique_usable_cards(
        output_cards,
        decision_source=decision_source,
        accept_abstain=accept_abstain,
    ) == expected_rows


def run_selected_shards(*, args: argparse.Namespace, audit: dict[str, Any], item: dict[str, Any]) -> None:
    for shard in item["shard_records"]:
        output_cards = Path(str(shard.get("output_cards") or ""))
        expected_rows = int(shard.get("rows") or 0)
        existing_rows = count_nonblank_lines(output_cards)
        existing_usable_rows = count_unique_usable_cards(
            output_cards,
            decision_source=args.decision_source,
            accept_abstain=args.abstain_label != "error",
        )
        if args.skip_existing and expected_rows > 0 and existing_usable_rows == expected_rows:
            item["command_results"].append(
                {
                    "stage": "online_shard",
                    "shard_id": shard.get("shard_id"),
                    "status": "skipped_existing_complete",
                    "returncode": 0,
                    "output_cards": str(output_cards),
                    "existing_rows": existing_rows,
                    "existing_usable_rows": existing_usable_rows,
                    "expected_rows": expected_rows,
                }
            )
            continue
        if args.skip_existing and existing_rows > 0 and existing_usable_rows != expected_rows:
            item["command_results"].append(
                {
                    "stage": "online_shard",
                    "shard_id": shard.get("shard_id"),
                    "status": "rerun_partial_existing",
                    "output_cards": str(output_cards),
                    "existing_rows": existing_rows,
                    "existing_usable_rows": existing_usable_rows,
                    "expected_rows": expected_rows,
                }
            )
        command = shard_command(args=args, dataset_dir=Path(item["dataset_dir"]), shard=shard)
        audit["commands"].append({"dataset": item["dataset"], "shard_id": shard.get("shard_id"), "command": command})
        result = run_command(
            command,
            log_path=Path(item["dataset_dir"]) / "llm_direct_fulltest_suite_run.log",
            stage="online_shard",
        )
        result["shard_id"] = shard.get("shard_id")
        result["output_cards"] = str(output_cards)
        item["command_results"].append(result)
        if result["returncode"] != 0:
            audit["status"] = "failed_online_shard"
            return
        audit["online_shards_run"] += 1


def shard_command(*, args: argparse.Namespace, dataset_dir: Path, shard: dict[str, Any]) -> list[str]:
    return [
        sys.executable,
        "scripts/run_llm_unordered.py",
        "--dataset",
        str(dataset_dir / "pairs.jsonl"),
        "--split-dir",
        str(Path(str(shard["split_dir"]))),
        "--splits",
        "test",
        "--output",
        str(Path(str(shard["output_cards"]))),
        "--report-path",
        str(Path(str(shard["report"]))),
        "--resume-existing",
        "--resume-decision-source",
        args.decision_source,
        *resume_abstain_args(args),
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


def run_command(command: list[str], *, log_path: Path, stage: str) -> dict[str, Any]:
    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as log:
        log.write(f"\n## {stage}\n")
        log.write(" ".join(command) + "\n")
        proc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, text=True)
    return {
        "stage": stage,
        "returncode": proc.returncode,
        "elapsed_sec": round(time.time() - started, 3),
        "log": str(log_path),
        "status": "ok" if proc.returncode == 0 else "failed",
    }


def merge_dataset_outputs(*, args: argparse.Namespace, item: dict[str, Any], dry_run: bool) -> None:
    dataset_dir = Path(item["dataset_dir"])
    cards_out = dataset_dir / "llm_direct_cards.jsonl"
    existing_shards = []
    missing_shards = []
    for shard in item.get("all_shard_records") or item["shard_records"]:
        path = Path(str(shard.get("output_cards") or ""))
        if path.exists():
            existing_shards.append(path)
        else:
            missing_shards.append(path)
    if not dry_run and existing_shards:
        with cards_out.open("w", encoding="utf-8", newline="\n") as sink:
            for path in existing_shards:
                with path.open("r", encoding="utf-8-sig", errors="replace") as source:
                    for line in source:
                        if line.strip():
                            sink.write(line if line.endswith("\n") else line + "\n")
        export_and_evaluate(args=args, dataset_dir=dataset_dir, dataset=item["dataset"])
    item["merge"] = {
        "cards_out": str(cards_out),
        "existing_shards": len(existing_shards),
        "missing_shards": len(missing_shards),
        "merged_card_rows": count_nonblank_lines(cards_out),
        "snapshot_rows": count_nonblank_lines(dataset_dir / "llm_direct_io_snapshot.jsonl"),
        "prediction_rows": count_nonblank_lines(dataset_dir / "llm_direct_predictions.txt"),
        "metrics_exists": (dataset_dir / "llm_direct_metrics.json").exists(),
    }
    item["output_complete"] = (
        item["merge"]["merged_card_rows"] == item["rows"]
        and item["merge"]["snapshot_rows"] == item["rows"]
        and item["merge"]["prediction_rows"] == item["rows"]
        and item["merge"]["metrics_exists"]
    )


def run_io_retention_audit(*, args: argparse.Namespace, audit: dict[str, Any]) -> None:
    command = [
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
        str(args.io_output),
        "--report",
        str(args.io_report),
    ]
    result = run_command(command, log_path=args.root / "llm_direct_fulltest_suite_run.log", stage="io_retention_audit")
    if result["returncode"] == 1:
        result["status"] = "incomplete"
    result["output"] = str(args.io_output)
    result["report"] = str(args.io_report)
    audit["io_retention"] = result
    if result["returncode"] not in {0, 1}:
        audit["status"] = "failed_io_retention_audit"


def refresh_dataset_completion(audit: dict[str, Any]) -> None:
    for item in audit["datasets"]:
        dataset_dir = Path(item["dataset_dir"])
        merge = item.setdefault("merge", {})
        merge["snapshot_rows"] = count_nonblank_lines(dataset_dir / "llm_direct_io_snapshot.jsonl")
        merge["prediction_rows"] = count_nonblank_lines(dataset_dir / "llm_direct_predictions.txt")
        merge["metrics_exists"] = (dataset_dir / "llm_direct_metrics.json").exists()
        item["output_complete"] = (
            merge.get("merged_card_rows", 0) == item["rows"]
            and merge.get("snapshot_rows", 0) == item["rows"]
            and merge.get("prediction_rows", 0) == item["rows"]
            and bool(merge.get("metrics_exists"))
        )


def export_and_evaluate(*, args: argparse.Namespace, dataset_dir: Path, dataset: str) -> None:
    cards_path = dataset_dir / "llm_direct_cards.jsonl"
    predictions_path = dataset_dir / "llm_direct_predictions.txt"
    export_cmd = [
        sys.executable,
        "scripts/export_llm_direct_predictions_from_cards.py",
        "--cards",
        str(cards_path),
        "--gold",
        str(dataset_dir / "test.txt"),
        "--output",
        str(predictions_path),
        "--summary-path",
        str(dataset_dir / "llm_direct_predictions.summary.json"),
        "--abstain-label",
        args.abstain_label,
        "--decision-source",
        args.decision_source,
    ]
    metric_cmd = [
        sys.executable,
        "scripts/evaluate_triplet_predictions.py",
        "--gold",
        str(dataset_dir / "test.txt"),
        "--predictions",
        str(predictions_path),
        "--output",
        str(dataset_dir / "llm_direct_metrics.json"),
        "--report",
        str(dataset_dir / "llm_direct_metrics.md"),
        "--dataset",
        f"{dataset}-fulltest",
        "--method",
        "LLM-direct",
        "--source",
        args.model,
    ]
    log_path = dataset_dir / "llm_direct_fulltest_suite_run.log"
    run_command(export_cmd, log_path=log_path, stage="export_predictions")
    if predictions_path.exists():
        run_command(metric_cmd, log_path=log_path, stage="evaluate_metrics")


def summarize_outputs(audit: dict[str, Any]) -> None:
    if audit["status"] in {"failed_online_shard", "failed_io_retention_audit", "dry_run", "inputs_ready_key_missing"}:
        return
    if all(item["output_complete"] for item in audit["datasets"]):
        audit["status"] = "complete_outputs"
    elif any(item["merge"].get("merged_card_rows", 0) for item in audit["datasets"]):
        audit["status"] = "partial_outputs"
    else:
        audit["status"] = "outputs_missing"


def read_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    if not isinstance(obj, dict):
        raise ValueError(f"expected JSON object: {path}")
    return obj


def count_nonblank_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def resume_abstain_args(args: argparse.Namespace) -> list[str]:
    return ["--resume-accept-abstain"] if args.abstain_label != "error" else []


def count_unique_usable_cards(path: Path, *, decision_source: str, accept_abstain: bool) -> int:
    if not path.exists():
        return 0
    done: set[int] = set()
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            try:
                card = json.loads(text)
            except json.JSONDecodeError:
                continue
            if not isinstance(card, dict) or not card_is_exportable(
                card,
                decision_source=decision_source,
                accept_abstain=accept_abstain,
            ):
                continue
            try:
                pair_id = int(card.get("pair_id", 0))
            except (TypeError, ValueError):
                continue
            if pair_id > 0:
                done.add(pair_id)
    return len(done)


def card_is_exportable(card: dict[str, Any], *, decision_source: str, accept_abstain: bool) -> bool:
    if label_from_card(card, decision_source=decision_source) in (0, 1):
        return True
    if not accept_abstain:
        return False
    llm = card.get("llm_evidence") if isinstance(card.get("llm_evidence"), dict) else {}
    if isinstance(llm, dict) and str(llm.get("status") or "") == "failed":
        return False
    if decision_source == "llm_bcb_gold":
        value = llm.get("bcb_gold_verdict") if isinstance(llm, dict) else None
    elif decision_source == "llm_semantic":
        value = llm.get("semantic_verdict") if isinstance(llm, dict) else None
    elif decision_source == "llm_pred":
        value = llm.get("verdict") if isinstance(llm, dict) else None
    else:
        decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
        value = decision.get("verdict") if isinstance(decision, dict) else None
    return str(value or "").strip() in {"context_insufficient", "unknown"}


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# LLM-Direct Full-Test Suite Runner Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        audit["claim_boundary"],
        "",
        audit["api_key_handling"],
        "",
        "Dotenv support records only the path, variable name, and load status; it never writes the key value.",
        "",
        "## Datasets",
        "",
        "| Dataset | Rows | Total shards | Selected shards | Existing shards | Cards | I/O snapshot | Predictions | Metrics | Complete |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for item in audit["datasets"]:
        merge = item.get("merge") or {}
        lines.append(
            "| {dataset} | {rows} | {total} | {selected} | {existing} | {cards} | {snapshot} | {predictions} | {metrics} | {complete} |".format(
                dataset=item["dataset"],
                rows=item["rows"],
                total=item["total_shards"],
                selected=len(item["selected_shards"]),
                existing=merge.get("existing_shards", 0),
                cards=merge.get("merged_card_rows", 0),
                snapshot=merge.get("snapshot_rows", 0),
                predictions=merge.get("prediction_rows", 0),
                metrics=merge.get("metrics_exists", False),
                complete=item["output_complete"],
            )
        )
    io_retention = audit.get("io_retention") or {}
    if io_retention:
        lines.extend(
            [
                "",
                "## I/O Retention",
                "",
                f"- status: `{io_retention.get('status')}`",
                f"- returncode: `{io_retention.get('returncode')}`",
                f"- output: `{io_retention.get('output', '')}`",
                f"- report: `{io_retention.get('report', '')}`",
            ]
        )
    lines.extend(["", "## Next Action", ""])
    if audit["status"] == "inputs_ready_key_missing":
        lines.append("Set the API key in the configured environment variable and run selected shard commands.")
    elif audit["status"] == "dry_run":
        lines.append("Dry run only; no online calls or merges were executed.")
    elif audit["status"] == "partial_outputs":
        lines.append("Continue running missing shards, then rerun this script with --merge-only.")
    elif audit["status"] == "complete_outputs":
        lines.append("Rebuild LLM I/O retention and paper tables.")
    else:
        lines.append("Run shard commands or inspect failed shard logs.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
