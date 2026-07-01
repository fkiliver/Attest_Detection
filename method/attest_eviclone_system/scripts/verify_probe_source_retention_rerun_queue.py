from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.dataset import iter_jsonl  # noqa: E402
from scripts.build_probe_source_retention_rerun_queue import DEFAULT_OUTPUT_DIR, DEFAULT_SPLIT  # noqa: E402
from scripts.build_probe_synthesis_plan import sorted_counter  # noqa: E402
from scripts.run_selective_gate_pipeline import file_fingerprint  # noqa: E402

SECRET_MARKERS = ["sk-", "--api-key", "Authorization:", "Bearer ", "LLM_API_KEY=", "OPENAI_API_KEY="]
REQUIRED_FILES = ["summary", "pairs", "split", "txt", "data", "manifest", "report"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the probe source-retention rerun queue artifacts.")
    parser.add_argument("--queue-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--split", type=str, default=DEFAULT_SPLIT)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    result = verify_probe_source_retention_rerun_queue(queue_dir=args.queue_dir, split=args.split)
    output = args.output or args.queue_dir / "queue_verification.json"
    report = args.report or args.queue_dir / "queue_verification.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_report(report, result)
    print(json.dumps({"status": result["status"], "issue_counts": result["issue_counts"]}, ensure_ascii=False))
    if args.strict_exit and result["status"] != "verified":
        return 2
    return 0


def verify_probe_source_retention_rerun_queue(*, queue_dir: Path, split: str = DEFAULT_SPLIT) -> dict[str, Any]:
    queue_dir = queue_dir.resolve()
    paths = queue_paths(queue_dir, split)
    issues: list[dict[str, str]] = []
    files = verify_required_files(paths, issues)
    summary = read_json(paths["summary"])
    pairs = read_jsonl(paths["pairs"])
    split_rows = read_jsonl(paths["split"])
    manifest = read_jsonl(paths["manifest"])
    txt_rows = read_triplet_rows(paths["txt"])
    data_rows = read_data_rows(paths["data"])

    verify_summary(summary, queue_dir=queue_dir, split=split, issues=issues)
    verify_counts(summary, pairs=pairs, split_rows=split_rows, manifest=manifest, txt_rows=txt_rows, data_rows=data_rows, issues=issues)
    verify_pair_alignment(pairs=pairs, split_rows=split_rows, txt_rows=txt_rows, manifest=manifest, data_rows=data_rows, split=split, issues=issues)
    verify_recommended_run(summary, queue_dir=queue_dir, split=split, issues=issues)

    recomputed = recompute_summary(pairs=pairs, manifest=manifest, data_rows=data_rows)
    compare_recomputed_summary(summary, recomputed, issues)
    issue_counts = {
        "error": sum(1 for item in issues if item["severity"] == "error"),
        "warning": sum(1 for item in issues if item["severity"] == "warning"),
    }
    return {
        "schema_version": "eviclone-probe-source-retention-rerun-queue-verification/v1",
        "status": "verified" if issue_counts["error"] == 0 else "failed",
        "queue_dir": str(queue_dir),
        "split": split,
        "issue_counts": issue_counts,
        "issues": issues,
        "files": files,
        "checks": {
            "summary_status": summary.get("status"),
            "written_pairs": len(pairs),
            "split_rows": len(split_rows),
            "txt_rows": len(txt_rows),
            "manifest_rows": len(manifest),
            "data_rows": len(data_rows),
            **recomputed,
        },
    }


def queue_paths(queue_dir: Path, split: str) -> dict[str, Path]:
    return {
        "summary": queue_dir / "summary.json",
        "pairs": queue_dir / "pairs.jsonl",
        "split": queue_dir / f"{split}.jsonl",
        "txt": queue_dir / f"{split}.txt",
        "data": queue_dir / "data.jsonl",
        "manifest": queue_dir / "candidate_manifest.jsonl",
        "report": queue_dir / "report.md",
    }


def verify_required_files(paths: dict[str, Path], issues: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows = []
    for name in REQUIRED_FILES:
        path = paths[name]
        row: dict[str, Any] = {"name": name, "path": str(path), "exists": path.exists(), "fingerprint": None}
        if not path.exists():
            add_issue(issues, "error", "required_file_missing", f"{name} is missing: {path}")
        else:
            row["fingerprint"] = file_fingerprint(path)
        rows.append(row)
    return rows


def verify_summary(summary: dict[str, Any], *, queue_dir: Path, split: str, issues: list[dict[str, str]]) -> None:
    if summary.get("schema_version") != "eviclone-probe-source-retention-rerun-queue/v1":
        add_issue(issues, "error", "unsupported_summary_schema", "Queue summary schema is not supported.")
    if summary.get("status") != "queue_ready":
        add_issue(issues, "warning", "queue_status_not_ready", f"Queue status is {summary.get('status')}.")
    if str(summary.get("split") or "") != split:
        add_issue(issues, "error", "summary_split_mismatch", f"summary.split={summary.get('split')} expected {split}.")
    output_dir = Path(str(summary.get("output_dir") or ""))
    if output_dir and output_dir.resolve() != queue_dir:
        add_issue(issues, "error", "summary_output_dir_mismatch", f"summary.output_dir={output_dir} expected {queue_dir}.")
    recommended = summary.get("recommended_run") if isinstance(summary.get("recommended_run"), dict) else {}
    if recommended.get("api_key_is_not_serialized") is not True:
        add_issue(issues, "error", "api_key_serialization_flag_missing", "recommended_run.api_key_is_not_serialized must be true.")


def verify_counts(
    summary: dict[str, Any],
    *,
    pairs: list[dict[str, Any]],
    split_rows: list[dict[str, Any]],
    manifest: list[dict[str, Any]],
    txt_rows: list[tuple[str, str, int]],
    data_rows: dict[str, str],
    issues: list[dict[str, str]],
) -> None:
    expected = int(summary.get("written_pairs") or -1)
    for name, actual in [
        ("pairs", len(pairs)),
        ("split", len(split_rows)),
        ("manifest", len(manifest)),
        ("txt", len(txt_rows)),
    ]:
        if expected != actual:
            add_issue(issues, "error", "queue_row_count_mismatch", f"{name} rows={actual} expected {expected}.")
    function_ids = {str(row.get("function_id_a") or "") for row in pairs} | {str(row.get("function_id_b") or "") for row in pairs}
    function_ids.discard("")
    missing_data = sorted(fid for fid in function_ids if fid not in data_rows)
    if missing_data:
        add_issue(issues, "error", "data_jsonl_missing_functions", f"data.jsonl is missing {len(missing_data)} functions.")
    if len(data_rows) < len(function_ids):
        add_issue(issues, "error", "data_jsonl_too_small", f"data rows={len(data_rows)} function_ids={len(function_ids)}.")


def verify_pair_alignment(
    *,
    pairs: list[dict[str, Any]],
    split_rows: list[dict[str, Any]],
    txt_rows: list[tuple[str, str, int]],
    manifest: list[dict[str, Any]],
    data_rows: dict[str, str],
    split: str,
    issues: list[dict[str, str]],
) -> None:
    seen_pair_ids: set[int] = set()
    seen_function_pairs: set[tuple[str, str]] = set()
    for idx, row in enumerate(pairs):
        pair_id = int_or_none(row.get("pair_id"))
        case_id = int_or_none(row.get("case_id"))
        if pair_id is None or case_id is None:
            add_issue(issues, "error", "pair_identity_missing", f"pairs row {idx + 1} lacks pair_id/case_id.")
            continue
        if pair_id in seen_pair_ids:
            add_issue(issues, "error", "duplicate_pair_id", f"duplicate pair_id={pair_id}.")
        seen_pair_ids.add(pair_id)
        if row.get("source") != "probe_source_retention_rerun":
            add_issue(issues, "error", "pair_source_mismatch", f"pair_id={pair_id} source={row.get('source')}.")
        if row.get("split") != split:
            add_issue(issues, "error", "pair_split_mismatch", f"pair_id={pair_id} split={row.get('split')}.")
        key = (str(row.get("function_id_a") or ""), str(row.get("function_id_b") or ""))
        if key in seen_function_pairs:
            add_issue(issues, "warning", "duplicate_function_pair", f"duplicate function pair={key}.")
        seen_function_pairs.add(key)
        retention = row.get("probe_source_retention") if isinstance(row.get("probe_source_retention"), dict) else {}
        if not retention.get("expected_source_sha256"):
            add_issue(issues, "error", "expected_source_sha_missing", f"pair_id={pair_id} has no expected source sha.")
        if not row.get("code_a") or not row.get("code_b"):
            add_issue(issues, "error", "pair_code_missing", f"pair_id={pair_id} is missing source code.")
        if key[0] in data_rows and str(row.get("code_a") or "") != data_rows[key[0]]:
            add_issue(issues, "error", "data_code_a_mismatch", f"pair_id={pair_id} code_a does not match data.jsonl.")
        if key[1] in data_rows and str(row.get("code_b") or "") != data_rows[key[1]]:
            add_issue(issues, "error", "data_code_b_mismatch", f"pair_id={pair_id} code_b does not match data.jsonl.")

        if idx < len(split_rows) and int_or_none(split_rows[idx].get("pair_id")) != pair_id:
            add_issue(issues, "error", "split_pair_id_mismatch", f"row {idx + 1} split pair_id does not match pairs.jsonl.")
        if idx < len(txt_rows) and txt_rows[idx] != (key[0], key[1], int(row.get("label", 0))):
            add_issue(issues, "error", "txt_triplet_mismatch", f"row {idx + 1} triplet does not match pairs.jsonl.")
        if idx < len(manifest):
            verify_manifest_row(row, manifest[idx], pair_id=pair_id, key=key, issues=issues)


def verify_manifest_row(
    pair_row: dict[str, Any],
    manifest_row: dict[str, Any],
    *,
    pair_id: int,
    key: tuple[str, str],
    issues: list[dict[str, str]],
) -> None:
    expected = {
        "case_id": pair_row.get("case_id"),
        "pair_id": pair_id,
        "function_id_a": key[0],
        "function_id_b": key[1],
        "gold": pair_row.get("label"),
        "expected_source_sha256": (pair_row.get("probe_source_retention") or {}).get("expected_source_sha256"),
    }
    for field, value in expected.items():
        if manifest_row.get(field) != value:
            add_issue(issues, "error", "candidate_manifest_mismatch", f"pair_id={pair_id} field={field} mismatch.")


def verify_recommended_run(summary: dict[str, Any], *, queue_dir: Path, split: str, issues: list[dict[str, str]]) -> None:
    recommended = summary.get("recommended_run") if isinstance(summary.get("recommended_run"), dict) else {}
    command = recommended.get("command") if isinstance(recommended.get("command"), list) else []
    command_text = " ".join(str(part) for part in command)
    for marker in SECRET_MARKERS:
        if marker in command_text and marker not in {"--api-key", "LLM_API_KEY="}:
            add_issue(issues, "error", "secret_marker_in_recommended_run", f"recommended command contains marker {marker}.")
    if "--api-key" in command:
        add_issue(issues, "error", "explicit_api_key_argument_present", "recommended command must not use --api-key.")
    required_parts = [
        "--with-dynamic",
        "--with-llm-context-completion",
        "--context-source-dir",
        "--api-key-env",
        "LLM_API_KEY",
        "--resume",
        "--resume-usable-only",
    ]
    for part in required_parts:
        if part not in command:
            add_issue(issues, "error", "recommended_run_missing_required_arg", f"recommended command is missing {part}.")
    expected_paths = {
        "--dataset": queue_dir / "pairs.jsonl",
        "--split-dir": queue_dir,
        "--output": queue_dir / "configured_llm_probe_source_retention_cards.jsonl",
        "--context-source-dir": queue_dir / "context_sources",
    }
    for flag, expected in expected_paths.items():
        value = command_value(command, flag)
        if value is None:
            continue
        if resolve_command_path(value).resolve() != expected.resolve():
            add_issue(issues, "error", "recommended_run_path_mismatch", f"{flag}={value} expected {expected}.")
    split_value = command_value(command, "--splits")
    if split_value != split:
        add_issue(issues, "error", "recommended_run_split_mismatch", f"--splits={split_value} expected {split}.")


def recompute_summary(*, pairs: list[dict[str, Any]], manifest: list[dict[str, Any]], data_rows: dict[str, str]) -> dict[str, Any]:
    route_counts = Counter(str((row.get("probe_source_retention") or {}).get("generation_route") or "unknown") for row in pairs)
    probe_counts = Counter(str((row.get("probe_source_retention") or {}).get("probe_mode") or "unknown") for row in pairs)
    risk_counts = Counter(str((row.get("probe_source_retention") or {}).get("risk_tier") or "unknown") for row in pairs)
    pain_counts = Counter(str((row.get("probe_source_retention") or {}).get("pain_point") or "unknown") for row in pairs)
    label_counts = Counter(str(row.get("label")) for row in pairs)
    source_hash_counts = Counter(
        "present" if (row.get("probe_source_retention") or {}).get("expected_source_sha256") else "missing" for row in pairs
    )
    return {
        "candidate_count": len(pairs),
        "written_pairs": len(pairs),
        "candidate_correct": sum(1 for row in pairs if (row.get("probe_source_retention") or {}).get("candidate_correct")),
        "missing_code_pairs": sum(1 for row in pairs if not row.get("code_a") or not row.get("code_b")),
        "data_function_count": len(data_rows),
        "manifest_rows": len(manifest),
        "generation_route_counts": sorted_counter(route_counts),
        "probe_mode_counts": sorted_counter(probe_counts),
        "risk_tier_counts": sorted_counter(risk_counts),
        "pain_point_counts": sorted_counter(pain_counts),
        "label_counts": sorted_counter(label_counts),
        "source_hash_counts": sorted_counter(source_hash_counts),
    }


def compare_recomputed_summary(summary: dict[str, Any], recomputed: dict[str, Any], issues: list[dict[str, str]]) -> None:
    for key in [
        "candidate_count",
        "written_pairs",
        "candidate_correct",
        "missing_code_pairs",
        "generation_route_counts",
        "probe_mode_counts",
        "risk_tier_counts",
        "pain_point_counts",
        "label_counts",
        "source_hash_counts",
    ]:
        if summary.get(key) != recomputed.get(key):
            add_issue(issues, "error", "summary_recomputed_mismatch", f"{key} summary value does not match queue files.")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except json.JSONDecodeError:
        return {}
    return obj if isinstance(obj, dict) else {}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [obj for obj in iter_jsonl(path) if isinstance(obj, dict)]


def read_triplet_rows(path: Path) -> list[tuple[str, str, int]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                rows.append((parts[0], parts[1], int(parts[2])))
    return rows


def read_data_rows(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    if not path.exists():
        return rows
    for obj in iter_jsonl(path):
        idx = str(obj.get("idx") or "")
        if idx:
            rows[idx] = str(obj.get("func") or "")
    return rows


def command_value(command: list[Any], flag: str) -> str | None:
    values = [str(item) for item in command]
    try:
        index = values.index(flag)
    except ValueError:
        return None
    if index + 1 >= len(values):
        return None
    return values[index + 1]


def resolve_command_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def add_issue(issues: list[dict[str, str]], severity: str, code: str, detail: str) -> None:
    issues.append({"severity": severity, "code": code, "detail": detail})


def write_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# Probe Source-Retention Queue Verification",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| errors | {result['issue_counts']['error']} |",
        f"| warnings | {result['issue_counts']['warning']} |",
        f"| written_pairs | {result['checks']['written_pairs']} |",
        f"| manifest_rows | {result['checks']['manifest_rows']} |",
        f"| data_rows | {result['checks']['data_rows']} |",
        f"| candidate_correct | {result['checks']['candidate_correct']} |",
        "",
        "## Issues",
        "",
    ]
    if result["issues"]:
        lines.extend(["| severity | code | detail |", "| --- | --- | --- |"])
        for issue in result["issues"]:
            lines.append(f"| {issue['severity']} | {issue['code']} | {issue['detail']} |")
    else:
        lines.append("No issues.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
