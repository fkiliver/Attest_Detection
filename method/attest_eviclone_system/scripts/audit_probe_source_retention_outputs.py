from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.selective_gate import card_pair_key, pair_key  # noqa: E402
from scripts.build_probe_source_retention_rerun_queue import DEFAULT_OUTPUT_DIR  # noqa: E402
from scripts.build_probe_synthesis_plan import sorted_counter  # noqa: E402
from scripts.run_selective_gate_pipeline import file_fingerprint  # noqa: E402


DEFAULT_OUTPUT = DEFAULT_OUTPUT_DIR / "source_retention_output_audit.json"
DEFAULT_REPORT = DEFAULT_OUTPUT_DIR / "source_retention_output_audit.md"
DEFAULT_CARDS_NAME = "configured_llm_probe_source_retention_cards.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit retained EviProbe.java sidecars produced by the probe rerun.")
    parser.add_argument("--queue-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--cards", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    result = audit_probe_source_retention_outputs(queue_dir=args.queue_dir, cards_path=args.cards)
    output = args.output or args.queue_dir / "source_retention_output_audit.json"
    report = args.report or args.queue_dir / "source_retention_output_audit.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_report(report, result)
    print(json.dumps({"status": result["status"], "issue_counts": result["issue_counts"]}, ensure_ascii=False))
    if args.strict_exit and result["status"] != "source_artifacts_verified":
        return 2
    return 0


def audit_probe_source_retention_outputs(*, queue_dir: Path, cards_path: Path | None = None) -> dict[str, Any]:
    queue_dir = queue_dir.resolve()
    summary_path = queue_dir / "summary.json"
    manifest_path = queue_dir / "candidate_manifest.jsonl"
    summary = read_json(summary_path)
    cards_path = cards_path.resolve() if cards_path else output_cards_path(queue_dir=queue_dir, summary=summary)
    manifest_rows = read_jsonl(manifest_path)
    expected = expected_manifest_by_pair(manifest_rows)
    issues: list[dict[str, str]] = []
    checks: Counter[str] = Counter()
    checks["expected_cards"] = len(expected)
    checks["manifest_rows"] = len(manifest_rows)

    files = [
        file_state("summary", summary_path),
        file_state("manifest", manifest_path),
        file_state("cards", cards_path),
    ]
    if not summary_path.exists():
        add_issue(issues, "error", "queue_summary_missing", f"Queue summary is missing: {summary_path}")
    if not manifest_path.exists():
        add_issue(issues, "error", "candidate_manifest_missing", f"Candidate manifest is missing: {manifest_path}")
    if duplicate_manifest_pair_count(manifest_rows):
        checks["duplicate_manifest_pairs"] = duplicate_manifest_pair_count(manifest_rows)
        add_issue(
            issues,
            "error",
            "duplicate_manifest_pairs",
            f"Candidate manifest has {checks['duplicate_manifest_pairs']} duplicate function-id pairs.",
        )

    if not cards_path.exists():
        checks["actual_cards"] = 0
        checks["missing_cards"] = len(expected)
        issue_counts = issue_counts_for(issues)
        return {
            "schema_version": "eviclone-probe-source-retention-output-audit/v1",
            "status": "not_run" if issue_counts["error"] == 0 else "failed",
            "queue_dir": str(queue_dir),
            "summary": summary_block(checks),
            "issue_counts": issue_counts,
            "issues": issues,
            "files": files,
            "checks": dict(checks),
            "examples": {
                "missing_cards": [compact_manifest(row) for row in manifest_rows[:5]],
                "source_hash_drift": [],
                "source_artifact_issues": [],
                "unexpected_cards": [],
            },
            "interpretation": interpretation_for("not_run", checks),
        }

    card_rows = read_card_rows(cards_path, issues=issues)
    by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    duplicate_pairs: set[tuple[str, str]] = set()
    unexpected_pairs: set[tuple[str, str]] = set()
    source_artifact_issue_examples: list[dict[str, Any]] = []
    source_hash_drift_examples: list[dict[str, Any]] = []

    for row in card_rows:
        if row.get("invalid"):
            continue
        card = row["card"]
        checks["actual_cards"] += 1
        key = card_pair_key(card)
        if key in by_pair:
            duplicate_pairs.add(key)
        else:
            by_pair[key] = card
        if key not in expected:
            unexpected_pairs.add(key)

    checks["duplicate_card_pairs"] = len(duplicate_pairs)
    checks["unexpected_cards"] = len(unexpected_pairs)
    checks["missing_cards"] = len(set(expected) - set(by_pair))
    if duplicate_pairs:
        add_issue(issues, "error", "duplicate_card_pairs", f"Output has {len(duplicate_pairs)} duplicate function-id pairs.")
    if unexpected_pairs:
        add_issue(issues, "error", "unexpected_card_pairs", f"Output has {len(unexpected_pairs)} pairs not present in manifest.")
    if checks["missing_cards"]:
        add_issue(issues, "warning", "missing_card_pairs", f"Output is missing {checks['missing_cards']} manifest pairs.")

    for key, manifest_row in expected.items():
        card = by_pair.get(key)
        if card is None:
            continue
        result = audit_card_source_artifact(card=card, manifest_row=manifest_row)
        for counter, value in result["counters"].items():
            checks[counter] += int(value)
        for issue in result["issues"]:
            issues.append(issue)
        if result["source_hash_drift"] and len(source_hash_drift_examples) < 10:
            source_hash_drift_examples.append(result["source_hash_drift"])
        if result["issues"] and len(source_artifact_issue_examples) < 10:
            source_artifact_issue_examples.append({"pair": list(key), "issues": result["issues"][:5]})

    for key in [
        "invalid_json_lines",
        "actual_cards",
        "duplicate_card_pairs",
        "unexpected_cards",
        "missing_cards",
        "context_completed",
        "context_not_completed",
        "source_artifact_recorded",
        "source_artifact_file_exists",
        "source_artifact_verified",
        "artifact_source_sha_match",
        "card_source_sha_match",
        "source_hash_replayed",
        "source_hash_drift",
        "source_hash_missing",
        "evi_probe_class_present",
        "snippet_a_present",
        "snippet_b_present",
    ]:
        checks.setdefault(key, 0)
    checks["invalid_json_lines"] += sum(1 for row in card_rows if row.get("invalid"))

    issue_counts = issue_counts_for(issues)
    status = output_audit_status(checks=checks, issue_counts=issue_counts)
    return {
        "schema_version": "eviclone-probe-source-retention-output-audit/v1",
        "status": status,
        "queue_dir": str(queue_dir),
        "summary": summary_block(checks),
        "issue_counts": issue_counts,
        "issues": issues,
        "files": files,
        "checks": dict(checks),
        "examples": {
            "missing_cards": [compact_manifest(expected[key]) for key in sorted(set(expected) - set(by_pair))[:5]],
            "source_hash_drift": source_hash_drift_examples,
            "source_artifact_issues": source_artifact_issue_examples,
            "unexpected_cards": [list(key) for key in sorted(unexpected_pairs)[:10]],
        },
        "interpretation": interpretation_for(status, checks),
    }


def audit_card_source_artifact(*, card: dict[str, Any], manifest_row: dict[str, Any]) -> dict[str, Any]:
    counters: Counter[str] = Counter()
    issues: list[dict[str, str]] = []
    key = card_pair_key(card)
    context = context_completion(card)
    context_status = str(context.get("status") or "") if context else ""
    if context_status == "completed":
        counters["context_completed"] += 1
    else:
        counters["context_not_completed"] += 1
        add_issue(
            issues,
            "warning",
            "context_completion_not_completed",
            f"pair={key} context completion status is {context_status or 'missing'}; resume should retry if the card is not usable.",
        )
        return {"counters": dict(counters), "issues": issues, "source_hash_drift": None}
    artifact = context.get("source_artifact") if isinstance(context.get("source_artifact"), dict) else {}
    if artifact:
        counters["source_artifact_recorded"] += 1
    else:
        add_issue(issues, "error", "source_artifact_missing", f"pair={key} has no source_artifact.")
        return {"counters": dict(counters), "issues": issues, "source_hash_drift": None}

    source_ok = True
    if artifact.get("retained") is not True:
        source_ok = False
        add_issue(issues, "error", "source_artifact_not_retained", f"pair={key} source_artifact.retained is not true.")
    path_text = str(artifact.get("path") or "")
    if not path_text:
        add_issue(issues, "error", "source_artifact_path_missing", f"pair={key} source_artifact.path is missing.")
        return {"counters": dict(counters), "issues": issues, "source_hash_drift": None}
    source_path = resolve_recorded_path(path_text, base=Path.cwd())
    if not source_path.exists():
        add_issue(issues, "error", "source_artifact_file_missing", f"pair={key} sidecar file is missing: {source_path}")
        return {"counters": dict(counters), "issues": issues, "source_hash_drift": None}

    counters["source_artifact_file_exists"] += 1
    bytes_data = source_path.read_bytes()
    text = bytes_data.decode("utf-8", "replace")
    actual_sha = hashlib.sha256(bytes_data).hexdigest()
    actual_bytes = source_path.stat().st_size
    recorded_sha = str(artifact.get("sha256") or "")
    recorded_bytes = int_or_none(artifact.get("bytes"))
    payload_sha = str(nested_get(context, ["payload", "java_source_sha256"]) or context.get("java_source_sha256") or "")
    expected_sha = str(manifest_row.get("expected_source_sha256") or "")

    if recorded_sha and recorded_sha == actual_sha:
        counters["artifact_source_sha_match"] += 1
    else:
        source_ok = False
        add_issue(
            issues,
            "error",
            "source_artifact_sha_mismatch",
            f"pair={key} sidecar sha does not match source file.",
        )
    if payload_sha and payload_sha == actual_sha:
        counters["card_source_sha_match"] += 1
    else:
        source_ok = False
        add_issue(
            issues,
            "error",
            "card_payload_source_sha_mismatch",
            f"pair={key} payload java_source_sha256 does not match source file.",
        )
    if recorded_bytes is not None and recorded_bytes != actual_bytes:
        source_ok = False
        add_issue(
            issues,
            "error",
            "source_artifact_byte_count_mismatch",
            f"pair={key} sidecar bytes={actual_bytes} recorded={recorded_bytes}.",
        )

    if "public class EviProbe" in text:
        counters["evi_probe_class_present"] += 1
    else:
        source_ok = False
        add_issue(issues, "error", "evi_probe_class_missing", f"pair={key} sidecar lacks public class EviProbe.")
    if "SnippetA" in text:
        counters["snippet_a_present"] += 1
    else:
        source_ok = False
        add_issue(issues, "error", "snippet_a_missing", f"pair={key} sidecar lacks SnippetA.")
    if "SnippetB" in text:
        counters["snippet_b_present"] += 1
    else:
        source_ok = False
        add_issue(issues, "error", "snippet_b_missing", f"pair={key} sidecar lacks SnippetB.")

    drift = None
    if not expected_sha:
        counters["source_hash_missing"] += 1
    elif expected_sha == actual_sha:
        counters["source_hash_replayed"] += 1
    else:
        counters["source_hash_drift"] += 1
        drift = {
            "pair": list(key),
            "case_id": manifest_row.get("case_id"),
            "expected_source_sha256": expected_sha,
            "actual_source_sha256": actual_sha,
            "source_path": str(source_path),
        }

    if source_ok:
        counters["source_artifact_verified"] += 1
    return {"counters": dict(counters), "issues": issues, "source_hash_drift": drift}


def context_completion(card: dict[str, Any]) -> dict[str, Any]:
    dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    context = dynamic.get("llm_context_completion") if isinstance(dynamic.get("llm_context_completion"), dict) else {}
    if context:
        return context
    fallback = card.get("context_completion") if isinstance(card.get("context_completion"), dict) else {}
    return fallback


def expected_manifest_by_pair(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = pair_key(str(row.get("function_id_a") or ""), str(row.get("function_id_b") or ""))
        result.setdefault(key, row)
    return result


def duplicate_manifest_pair_count(rows: list[dict[str, Any]]) -> int:
    counts = Counter(
        pair_key(str(row.get("function_id_a") or ""), str(row.get("function_id_b") or ""))
        for row in rows
    )
    return sum(1 for count in counts.values() if count > 1)


def output_audit_status(*, checks: Counter[str], issue_counts: dict[str, int]) -> str:
    expected = int(checks.get("expected_cards") or 0)
    if expected == 0:
        return "no_expected_cards"
    if issue_counts["error"]:
        return "failed"
    if checks.get("missing_cards"):
        return "incomplete"
    if int(checks.get("source_artifact_verified") or 0) == expected:
        return "source_artifacts_verified"
    return "partial"


def summary_block(checks: Counter[str]) -> dict[str, Any]:
    expected = int(checks.get("expected_cards") or 0)
    verified = int(checks.get("source_artifact_verified") or 0)
    return {
        "expected_cards": expected,
        "actual_cards": int(checks.get("actual_cards") or 0),
        "missing_cards": int(checks.get("missing_cards") or 0),
        "source_artifact_verified": verified,
        "source_artifact_verified_rate": (verified / expected) if expected else None,
        "source_hash_replayed": int(checks.get("source_hash_replayed") or 0),
        "source_hash_drift": int(checks.get("source_hash_drift") or 0),
        "invalid_json_lines": int(checks.get("invalid_json_lines") or 0),
        "duplicate_card_pairs": int(checks.get("duplicate_card_pairs") or 0),
        "unexpected_cards": int(checks.get("unexpected_cards") or 0),
    }


def interpretation_for(status: str, checks: Counter[str]) -> dict[str, str]:
    if status == "not_run":
        return {
            "what_this_proves": "The source-retention rerun output cards do not exist yet.",
            "next_step": "Run the verified probe source-retention queue, then rerun this audit before probe execution.",
        }
    if status == "source_artifacts_verified":
        return {
            "what_this_proves": (
                "Every expected card has a retained EviProbe.java sidecar whose file hash matches both "
                "source_artifact.sha256 and payload.java_source_sha256."
            ),
            "next_step": "Use verified sidecars to generate and execute probe templates; manually review hash-drift rows if needed.",
        }
    if status == "incomplete":
        return {
            "what_this_proves": "Some output cards are still missing from the source-retention rerun.",
            "next_step": "Resume the rerun with --resume --resume-usable-only, then rerun this audit.",
        }
    return {
        "what_this_proves": f"The source-retention output audit status is {status}.",
        "next_step": "Fix the reported card/sidecar issues before using these outputs for probe execution.",
    }


def output_cards_path(*, queue_dir: Path, summary: dict[str, Any]) -> Path:
    outputs = summary.get("outputs") if isinstance(summary.get("outputs"), dict) else {}
    recorded = outputs.get("cards")
    if recorded:
        return resolve_recorded_path(str(recorded), base=queue_dir)
    return queue_dir / DEFAULT_CARDS_NAME


def read_card_rows(path: Path, *, issues: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                add_issue(issues, "error", "invalid_json_line", f"{path}:{line_no}: {exc}")
                rows.append({"line_no": line_no, "invalid": True})
                continue
            if not isinstance(obj, dict):
                add_issue(issues, "error", "card_json_not_object", f"{path}:{line_no} is not a JSON object.")
                rows.append({"line_no": line_no, "invalid": True})
                continue
            rows.append({"line_no": line_no, "card": obj})
    return rows


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except json.JSONDecodeError:
        return {"_json_error": True}
    return obj if isinstance(obj, dict) else {"_json_type": type(obj).__name__}


def file_state(name: str, path: Path) -> dict[str, Any]:
    row: dict[str, Any] = {"name": name, "path": str(path), "exists": path.exists(), "fingerprint": None}
    if path.exists():
        row["fingerprint"] = file_fingerprint(path)
    return row


def add_issue(issues: list[dict[str, str]], severity: str, code: str, detail: str) -> None:
    issues.append({"severity": severity, "code": code, "detail": detail})


def issue_counts_for(issues: list[dict[str, str]]) -> dict[str, int]:
    return {
        "error": sum(1 for issue in issues if issue.get("severity") == "error"),
        "warning": sum(1 for issue in issues if issue.get("severity") == "warning"),
    }


def compact_manifest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": row.get("case_id"),
        "pair_id": row.get("pair_id"),
        "function_id_a": row.get("function_id_a"),
        "function_id_b": row.get("function_id_b"),
        "probe_mode": row.get("probe_mode"),
        "generation_route": row.get("generation_route"),
    }


def resolve_recorded_path(path_text: str, *, base: Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    if path.parent == Path("."):
        return (base / path).resolve()
    return (REPO_ROOT / path).resolve()


def nested_get(obj: Any, keys: list[str]) -> Any:
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def write_report(path: Path, audit: dict[str, Any]) -> None:
    summary = audit["summary"]
    checks = Counter(audit.get("checks") or {})
    lines = [
        "# Probe Source-Retention Output Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| expected_cards | {summary['expected_cards']} |",
        f"| actual_cards | {summary['actual_cards']} |",
        f"| missing_cards | {summary['missing_cards']} |",
        f"| source_artifact_verified | {summary['source_artifact_verified']} |",
        f"| source_hash_replayed | {summary['source_hash_replayed']} |",
        f"| source_hash_drift | {summary['source_hash_drift']} |",
        f"| invalid_json_lines | {summary['invalid_json_lines']} |",
        f"| duplicate_card_pairs | {summary['duplicate_card_pairs']} |",
        f"| unexpected_cards | {summary['unexpected_cards']} |",
        "",
        "## Source Checks",
        "",
        "| check | count |",
        "| --- | ---: |",
    ]
    for key, value in sorted_counter(checks).items():
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Issues", "", "| severity | code | detail |", "| --- | --- | --- |"])
    if audit["issues"]:
        for issue in audit["issues"][:50]:
            lines.append(f"| {issue['severity']} | {issue['code']} | {issue['detail']} |")
    else:
        lines.append("| n/a | n/a | No issues recorded. |")
    examples = audit.get("examples") if isinstance(audit.get("examples"), dict) else {}
    drift = examples.get("source_hash_drift") if isinstance(examples.get("source_hash_drift"), list) else []
    if drift:
        lines.extend(["", "## Source Hash Drift Examples", "", "| case_id | pair | expected | actual |", "| ---: | --- | --- | --- |"])
        for item in drift[:10]:
            lines.append(
                f"| {item.get('case_id')} | {item.get('pair')} | "
                f"{item.get('expected_source_sha256')} | {item.get('actual_source_sha256')} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(nested_get(audit, ["interpretation", "what_this_proves"]) or ""),
            "",
            "Next step:",
            "",
            str(nested_get(audit, ["interpretation", "next_step"]) or ""),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
