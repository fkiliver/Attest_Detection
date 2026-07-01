from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.build_probe_synthesis_plan import DEFAULT_OUTPUT as DEFAULT_PROBE_PLAN  # noqa: E402
from scripts.build_probe_synthesis_plan import DEFAULT_RUN_DIR, input_state, sorted_counter  # noqa: E402

DEFAULT_OUTPUT = DEFAULT_RUN_DIR / "probe_execution_readiness_audit.json"
DEFAULT_REPORT = DEFAULT_RUN_DIR / "probe_execution_readiness_audit.md"
DEFAULT_CANDIDATES = DEFAULT_RUN_DIR / "probe_synthesis_candidates.jsonl"
DEFAULT_SOURCE_CARDS = (
    DEFAULT_RUN_DIR
    / "probe_source_retention_rerun_queue"
    / "configured_llm_probe_source_retention_cards.jsonl"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit whether probe-synthesis candidates have executable source artifacts.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--probe-plan", type=Path, default=DEFAULT_PROBE_PLAN)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument(
        "--source-cards",
        type=Path,
        default=DEFAULT_SOURCE_CARDS,
        help="optional rerun cards containing retained llm_context_completion.source_artifact sidecars",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    audit = build_probe_execution_readiness_audit(
        run_dir=args.run_dir,
        probe_plan_json=args.probe_plan,
        candidates_jsonl=args.candidates,
        source_cards_jsonl=args.source_cards,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_report(args.report, audit)
    print(json.dumps({"status": audit["status"], "output": str(args.output.resolve())}, ensure_ascii=False))
    return 0 if audit["status"] in {"execution_ready", "source_retention_required", "no_candidates"} else 2


def build_probe_execution_readiness_audit(
    *,
    run_dir: Path,
    probe_plan_json: Path,
    candidates_jsonl: Path,
    source_cards_jsonl: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    plan = read_json(probe_plan_json)
    candidates = load_candidates(candidates_jsonl)
    source_cards = load_source_cards_by_pair(source_cards_jsonl) if source_cards_jsonl else {}
    materialized = [materialize_candidate_source_artifact(item, source_cards) for item in candidates]
    rows = [classify_candidate(item) for item in materialized]
    summary = summarize(rows)
    return {
        "schema_version": "eviclone-probe-execution-readiness/v1",
        "status": readiness_status(summary),
        "created_at_utc": now.isoformat(),
        "run_dir": str(run_dir.resolve()),
        "inputs": {
            "probe_plan_json": input_state(probe_plan_json),
            "candidates_jsonl": input_state(candidates_jsonl),
            "source_cards_jsonl": input_state(source_cards_jsonl) if source_cards_jsonl else {"exists": False},
        },
        "probe_plan_status": plan.get("status") or "missing",
        "summary": summary,
        "readiness_by_route": summarize_group(rows, "generation_route"),
        "readiness_by_probe_mode": summarize_group(rows, "probe_mode"),
        "readiness_by_pain_point": summarize_group(rows, "pain_point"),
        "examples": {
            "ready": [compact(row) for row in rows if row["readiness"] == "execution_ready"][:5],
            "blocked": [compact(row) for row in rows if row["readiness"] != "execution_ready"][:5],
        },
        "required_system_change": {
            "id": "retain_llm_completed_source_sidecars",
            "status": "implemented_and_materialized" if summary.get("source_artifacts_from_cards") else "implemented_for_future_runs",
            "detail": (
                "evaluate_java_pair now accepts context_source_dir and records sidecar EviProbe.java path, sha256, and "
                "byte count in dynamic_evidence.llm_context_completion.source_artifact. This audit also materializes "
                "verified sidecars from source-retention rerun cards back into the probe candidates."
            ),
        },
        "interpretation": {
            "what_this_proves": (
                "The probe work queue is executable only for rows whose completed Java source sidecar is retained and "
                "hash-verified. Source-retention rerun cards are now treated as the authoritative sidecar index."
            ),
            "next_step": (
                "Rerun the selected probe-synthesis candidates with --context-source-dir, then execute deterministic "
                "templates only for rows whose source_artifact fingerprint is present and matches the plan."
            ),
        },
    }


def classify_candidate(item: dict[str, Any]) -> dict[str, Any]:
    artifact = source_artifact(item)
    has_sha = bool((item.get("context_completion") or {}).get("java_source_sha256"))
    route = str(item.get("generation_route") or "unknown")
    file_check = source_file_check(
        artifact,
        expected_sha=(item.get("context_completion") or {}).get("java_source_sha256"),
        allow_expected_drift=item.get("source_artifact_origin") == "source_retention_cards",
    )
    if file_check["status"] == "verified":
        readiness = "execution_ready"
    elif not artifact:
        readiness = "source_retention_missing"
    elif file_check["status"] == "missing":
        readiness = "source_artifact_missing"
    elif file_check["status"] == "sha_mismatch":
        readiness = "source_artifact_sha_mismatch"
    else:
        readiness = "source_artifact_unverified"
    return {
        "case_id": item.get("case_id"),
        "pain_point": item.get("pain_point"),
        "pair": item.get("pair"),
        "probe_mode": item.get("probe_mode"),
        "generation_route": route,
        "risk_tier": item.get("risk_tier"),
        "candidate_correct": item.get("candidate_correct"),
        "expected_source_sha256": (item.get("context_completion") or {}).get("java_source_sha256"),
        "has_source_sha256": has_sha,
        "source_artifact": artifact,
        "source_artifact_origin": item.get("source_artifact_origin"),
        "source_file_check": file_check,
        "readiness": readiness,
    }


def materialize_candidate_source_artifact(
    item: dict[str, Any],
    source_cards: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    context = item.get("context_completion") if isinstance(item.get("context_completion"), dict) else {}
    if isinstance(context.get("source_artifact"), dict) and context.get("source_artifact"):
        return item
    card = source_cards.get(candidate_pair_key(item))
    if not card:
        return item
    artifact = card_context_source_artifact(card)
    if not artifact:
        return item
    copied = json.loads(json.dumps(item, ensure_ascii=False))
    copied_context = copied.get("context_completion") if isinstance(copied.get("context_completion"), dict) else {}
    copied_context["source_artifact"] = artifact
    if not copied_context.get("java_source_sha256"):
        payload_sha = card_context_source_sha(card)
        if payload_sha:
            copied_context["java_source_sha256"] = payload_sha
    copied["context_completion"] = copied_context
    copied["source_artifact_origin"] = "source_retention_cards"
    return copied


def load_source_cards_by_pair(path: Path | None) -> dict[tuple[str, str], dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    rows = {}
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            key = card_pair_key(obj)
            if key != ("", ""):
                rows[key] = obj
    return rows


def candidate_pair_key(item: dict[str, Any]) -> tuple[str, str]:
    pair = item.get("pair")
    if isinstance(pair, list) and len(pair) >= 2:
        return normalized_pair_key(str(pair[0]), str(pair[1]))
    if isinstance(pair, dict):
        left = pair.get("function_id_a") or pair.get("a") or pair.get("left")
        right = pair.get("function_id_b") or pair.get("b") or pair.get("right")
        return normalized_pair_key(str(left or ""), str(right or ""))
    return ("", "")


def card_pair_key(card: dict[str, Any]) -> tuple[str, str]:
    ids = card.get("function_ids") if isinstance(card.get("function_ids"), dict) else {}
    return normalized_pair_key(str(ids.get("a") or ""), str(ids.get("b") or ""))


def normalized_pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b))) if a and b else ("", "")


def card_context_source_artifact(card: dict[str, Any]) -> dict[str, Any]:
    context = card_context_completion(card)
    artifact = context.get("source_artifact") if isinstance(context.get("source_artifact"), dict) else {}
    return artifact


def card_context_source_sha(card: dict[str, Any]) -> str:
    context = card_context_completion(card)
    payload = context.get("payload") if isinstance(context.get("payload"), dict) else {}
    return str(payload.get("java_source_sha256") or context.get("java_source_sha256") or "")


def card_context_completion(card: dict[str, Any]) -> dict[str, Any]:
    dynamic = card.get("dynamic_evidence") if isinstance(card.get("dynamic_evidence"), dict) else {}
    return dynamic.get("llm_context_completion") if isinstance(dynamic.get("llm_context_completion"), dict) else {}


def source_artifact(item: dict[str, Any]) -> dict[str, Any]:
    context = item.get("context_completion") if isinstance(item.get("context_completion"), dict) else {}
    artifact = context.get("source_artifact") if isinstance(context.get("source_artifact"), dict) else {}
    return artifact


def source_file_check(artifact: dict[str, Any], *, expected_sha: Any, allow_expected_drift: bool = False) -> dict[str, Any]:
    if not artifact:
        return {"status": "not_recorded"}
    path_text = str(artifact.get("path") or "")
    if not path_text:
        return {"status": "path_missing"}
    path = Path(path_text)
    if not path.exists():
        return {"status": "missing", "path": path_text}
    text = path.read_text(encoding="utf-8", errors="replace")
    actual_sha = sha256_text(text)
    recorded_sha = artifact.get("sha256")
    if recorded_sha and str(recorded_sha) != actual_sha:
        return {"status": "sha_mismatch", "path": path_text, "actual_sha256": actual_sha, "recorded_sha256": recorded_sha}
    if expected_sha and str(expected_sha) != actual_sha:
        if allow_expected_drift:
            return {
                "status": "verified",
                "path": path_text,
                "sha256": actual_sha,
                "bytes": path.stat().st_size,
                "expected_sha256": str(expected_sha),
                "source_hash_drift_accepted": True,
            }
        return {"status": "sha_mismatch", "path": path_text, "actual_sha256": actual_sha, "expected_sha256": expected_sha}
    return {"status": "verified", "path": path_text, "sha256": actual_sha, "bytes": path.stat().st_size}


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    readiness = Counter(str(row["readiness"]) for row in rows)
    routes = Counter(str(row["generation_route"]) for row in rows)
    origins = Counter(str(row.get("source_artifact_origin") or "candidate") for row in rows if row["readiness"] == "execution_ready")
    return {
        "candidate_count": len(rows),
        "execution_ready": readiness.get("execution_ready", 0),
        "blocked": len(rows) - readiness.get("execution_ready", 0),
        "source_retention_missing": readiness.get("source_retention_missing", 0),
        "source_artifact_missing": readiness.get("source_artifact_missing", 0),
        "source_artifact_sha_mismatch": readiness.get("source_artifact_sha_mismatch", 0),
        "source_hash_drift_accepted": sum(1 for row in rows if row["source_file_check"].get("source_hash_drift_accepted") is True),
        "readiness_counts": sorted_counter(readiness),
        "source_artifact_origin_counts": sorted_counter(origins),
        "source_artifacts_from_cards": origins.get("source_retention_cards", 0),
        "generation_route_counts": sorted_counter(routes),
        "deterministic_blocked": sum(
            1
            for row in rows
            if row["generation_route"] in {"deterministic_template", "deterministic_template_with_review"}
            and row["readiness"] != "execution_ready"
        ),
        "llm_probe_completion_blocked": sum(
            1 for row in rows if row["generation_route"] == "llm_probe_completion" and row["readiness"] != "execution_ready"
        ),
        "candidate_correct_blocked": sum(1 for row in rows if row.get("candidate_correct") and row["readiness"] != "execution_ready"),
    }


def summarize_group(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    result = []
    for value in sorted({str(row.get(key) or "unknown") for row in rows}):
        items = [row for row in rows if str(row.get(key) or "unknown") == value]
        result.append(
            {
                key: value,
                "candidate_count": len(items),
                "readiness_counts": sorted_counter(Counter(str(row["readiness"]) for row in items)),
                "execution_ready": sum(1 for row in items if row["readiness"] == "execution_ready"),
            }
        )
    return result


def readiness_status(summary: dict[str, Any]) -> str:
    if summary["candidate_count"] == 0:
        return "no_candidates"
    if summary["execution_ready"] == summary["candidate_count"]:
        return "execution_ready"
    if summary["source_retention_missing"] == summary["candidate_count"]:
        return "source_retention_required"
    return "partial"


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": row["case_id"],
        "pair": row["pair"],
        "probe_mode": row["probe_mode"],
        "generation_route": row["generation_route"],
        "readiness": row["readiness"],
    }


def load_candidates(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line in handle:
            if line.strip():
                obj = json.loads(line)
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


def sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# Probe Execution Readiness Audit",
        "",
        f"Status: `{audit['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| candidate_count | {audit['summary']['candidate_count']} |",
        f"| execution_ready | {audit['summary']['execution_ready']} |",
        f"| blocked | {audit['summary']['blocked']} |",
        f"| source_retention_missing | {audit['summary']['source_retention_missing']} |",
        f"| source_hash_drift_accepted | {audit['summary'].get('source_hash_drift_accepted', 0)} |",
        f"| deterministic_blocked | {audit['summary']['deterministic_blocked']} |",
        f"| llm_probe_completion_blocked | {audit['summary']['llm_probe_completion_blocked']} |",
        f"| candidate_correct_blocked | {audit['summary']['candidate_correct_blocked']} |",
        "",
        "## Readiness Counts",
        "",
        "| readiness | count |",
        "| --- | ---: |",
    ]
    for key, count in audit["summary"]["readiness_counts"].items():
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Source Artifact Origins", "", "| origin | count |", "| --- | ---: |"])
    for key, count in audit["summary"].get("source_artifact_origin_counts", {}).items():
        lines.append(f"| {key} | {count} |")
    lines.extend(
        [
            "",
            "## Required System Change",
            "",
            f"{audit['required_system_change']['detail']}",
            "",
            "## Interpretation",
            "",
            audit["interpretation"]["what_this_proves"],
            "",
            audit["interpretation"]["next_step"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
