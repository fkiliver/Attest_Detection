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

from eviclone_prototype.deployment_policy import (  # noqa: E402
    architecture_contracts_block_deployment,
    dynamic_contract_deployment_decision,
    dynamic_contract_deployment_blockers,
    dynamic_contracts_block_deployment,
    dynamic_route_certificates_block_deployment,
    executable_evidence_integrity_blocks_deployment,
    fusion_decision_contracts_block_deployment,
    llm_expert_contracts_block_deployment,
    runtime_fixture_contracts_block_deployment,
    verify_dynamic_contract_deployment_decision,
)
from scripts.check_selective_gate_deployment import (  # noqa: E402
    assess_readiness as recompute_assess_readiness,
    check_triplet_file_health as recompute_triplet_file_health,
    count_csv_rows as recompute_count_csv_rows,
    count_triplet_rows as recompute_count_triplet_rows,
    verify_actual_metric_consistency as recompute_actual_metric_consistency,
    verify_prediction_audit_consistency as recompute_prediction_audit_consistency,
)

MERGE_SUMMARY_SCHEMA = "eviclone-repair-shard-merge/v1"
MERGE_SUMMARY_READY_PUBLISH_REASON = "complete_healthy_merge"
MANIFEST_CERTIFICATE_SCHEMA_VERSION = "eviclone-selective-gate-manifest-certificate/v1"
MANIFEST_CERTIFICATE_HASH_FIELD = "certificate_sha256"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify selective gate pipeline manifest file fingerprints.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--base-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    result = verify_manifest(args.manifest, base_dir=args.base_dir)
    if args.output:
        write_json(args.output, result)
    if args.report:
        write_report(args.report, result)
    print(json.dumps({"status": result["status"], "issue_counts": result["issue_counts"]}, ensure_ascii=False))
    if args.strict_exit and result["status"] != "verified":
        return 2
    return 0


def verify_manifest(path: Path, *, base_dir: Path | None = None) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    resolved_base_dir = base_dir.resolve() if base_dir else Path.cwd().resolve()
    issues: list[dict[str, str]] = []
    if manifest.get("schema_version") != "eviclone-selective-gate-pipeline-manifest/v1":
        add_issue(issues, "error", "unsupported_manifest_schema", "Manifest schema is not supported.")
    certificate_result = verify_manifest_certificate(manifest)
    issues.extend(certificate_result["issues"])

    checked_files = []
    for section in ["inputs", "outputs"]:
        entries = manifest.get(section)
        if not isinstance(entries, dict):
            add_issue(issues, "error", f"missing_{section}", f"Manifest is missing {section}.")
            continue
        checked_files.extend(iter_fingerprint_entries(section, entries))

    verified = 0
    missing = 0
    mismatch = 0
    files: list[dict[str, Any]] = []
    for item in checked_files:
        expected = item["fingerprint"]
        label = item["label"]
        if expected is None:
            continue
        file_path = resolve_fingerprint_path(expected, base_dir=resolved_base_dir)
        file_result: dict[str, Any] = {
            "label": label,
            "status": "pending",
            "path": str(file_path),
            "relative_path": expected.get("relative_path"),
            "expected_bytes": int(expected.get("bytes") or -1),
            "expected_sha256": str(expected.get("sha256") or ""),
            "actual_bytes": None,
            "actual_sha256": None,
        }
        if not file_path.exists():
            missing += 1
            file_result["status"] = "missing"
            files.append(file_result)
            add_issue(issues, "error", "fingerprinted_file_missing", f"{label} does not exist: {file_path}")
            continue
        actual = file_fingerprint(file_path)
        expected_bytes = int(expected.get("bytes") or -1)
        expected_sha = str(expected.get("sha256") or "")
        file_result["actual_bytes"] = actual["bytes"]
        file_result["actual_sha256"] = actual["sha256"]
        if actual["bytes"] != expected_bytes or actual["sha256"] != expected_sha:
            mismatch += 1
            file_result["status"] = "mismatch"
            files.append(file_result)
            add_issue(
                issues,
                "error",
                "fingerprint_mismatch",
                f"{label} fingerprint mismatch: expected bytes={expected_bytes} sha256={expected_sha}, "
                f"actual bytes={actual['bytes']} sha256={actual['sha256']}.",
            )
            continue
        verified += 1
        file_result["status"] = "verified"
        files.append(file_result)

    semantic_checks = verify_manifest_semantics(manifest, base_dir=resolved_base_dir)
    issues.extend(semantic_checks["issues"])
    issue_counts = {
        "error": sum(1 for item in issues if item["severity"] == "error"),
        "warning": sum(1 for item in issues if item["severity"] == "warning"),
    }
    status = "verified" if issue_counts["error"] == 0 else "failed"
    return {
        "status": status,
        "manifest": str(path.resolve()),
        "manifest_fingerprint": file_fingerprint(path),
        "manifest_certificate": certificate_result,
        "base_dir": str(resolved_base_dir),
        "issue_counts": issue_counts,
        "issues": issues,
        "checked_file_count": len([item for item in checked_files if item["fingerprint"] is not None]),
        "verified_file_count": verified,
        "missing_file_count": missing,
        "mismatched_file_count": mismatch,
        "semantic_check_count": semantic_checks["checked"],
        "semantic_issue_count": len(semantic_checks["issues"]),
        "files": files,
    }


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8", "replace")).hexdigest()


def manifest_payload_without_certificate(manifest: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "manifest_certificate"}


def build_manifest_certificate(manifest: dict[str, Any]) -> dict[str, Any]:
    payload = manifest_payload_without_certificate(manifest)
    certificate = {
        "schema_version": MANIFEST_CERTIFICATE_SCHEMA_VERSION,
        "manifest_schema_version": manifest.get("schema_version"),
        "pipeline": manifest.get("pipeline"),
        "name": manifest.get("name"),
        "status": manifest.get("status"),
        "parameters_sha256": canonical_sha256(manifest.get("parameters") or {}),
        "inputs_sha256": canonical_sha256(manifest.get("inputs") or {}),
        "outputs_sha256": canonical_sha256(manifest.get("outputs") or {}),
        "summary_checks_sha256": canonical_sha256(manifest.get("summary_checks") or {}),
        "readiness_checks_sha256": canonical_sha256(manifest.get("readiness_checks") or {}),
        "dynamic_evidence_contracts_sha256": canonical_sha256(manifest.get("dynamic_evidence_contracts") or {}),
        "inner_pipeline_sha256": canonical_sha256(manifest.get("inner_pipeline") or {}),
        "manifest_payload_sha256": canonical_sha256(payload),
        "decision_owner": "manifest_verifier_recomputes_file_fingerprints_and_semantic_checks",
    }
    certificate[MANIFEST_CERTIFICATE_HASH_FIELD] = canonical_sha256(
        {key: value for key, value in certificate.items() if key != MANIFEST_CERTIFICATE_HASH_FIELD}
    )
    return certificate


def attach_manifest_certificate(manifest: dict[str, Any]) -> dict[str, Any]:
    payload = dict(manifest)
    payload["manifest_certificate"] = build_manifest_certificate(payload)
    return payload


def verify_manifest_certificate(manifest: dict[str, Any]) -> dict[str, Any]:
    certificate = manifest.get("manifest_certificate")
    if not isinstance(certificate, dict):
        return {"status": "missing", "issues": []}
    issues: list[dict[str, str]] = []
    expected = build_manifest_certificate(manifest)
    if certificate.get("schema_version") != MANIFEST_CERTIFICATE_SCHEMA_VERSION:
        add_issue(
            issues,
            "error",
            "manifest_certificate_schema_mismatch",
            f"manifest_certificate.schema_version={certificate.get('schema_version')!r} expected {MANIFEST_CERTIFICATE_SCHEMA_VERSION}.",
        )
    for key in [
        "manifest_schema_version",
        "pipeline",
        "name",
        "status",
        "parameters_sha256",
        "inputs_sha256",
        "outputs_sha256",
        "summary_checks_sha256",
        "readiness_checks_sha256",
        "dynamic_evidence_contracts_sha256",
        "inner_pipeline_sha256",
        "manifest_payload_sha256",
        "decision_owner",
    ]:
        if certificate.get(key) != expected.get(key):
            add_issue(
                issues,
                "error",
                f"manifest_certificate_{key}_mismatch",
                f"manifest_certificate.{key}={certificate.get(key)!r} expected {expected.get(key)!r}.",
            )
    if certificate.get(MANIFEST_CERTIFICATE_HASH_FIELD) != expected.get(MANIFEST_CERTIFICATE_HASH_FIELD):
        add_issue(
            issues,
            "error",
            "manifest_certificate_sha_mismatch",
            "manifest_certificate.certificate_sha256 does not match the verifier-recomputed certificate payload.",
        )
    return {
        "status": "verified" if not issues else "failed",
        "schema_version": certificate.get("schema_version"),
        "expected_certificate_sha256": expected.get(MANIFEST_CERTIFICATE_HASH_FIELD),
        "actual_certificate_sha256": certificate.get(MANIFEST_CERTIFICATE_HASH_FIELD),
        "manifest_payload_sha256": certificate.get("manifest_payload_sha256"),
        "issues": issues,
    }


def iter_fingerprint_entries(section: str, entries: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for key, value in entries.items():
        if value is None:
            continue
        if isinstance(value, list):
            for idx, item in enumerate(value):
                result.append({"label": f"{section}.{key}[{idx}]", "fingerprint": item})
        else:
            result.append({"label": f"{section}.{key}", "fingerprint": value})
    return result


def resolve_fingerprint_path(expected: dict[str, Any], *, base_dir: Path) -> Path:
    absolute = Path(str(expected.get("path") or ""))
    if absolute.exists():
        return absolute
    relative = expected.get("relative_path")
    if relative:
        return base_dir / str(relative)
    return absolute


def verify_manifest_semantics(manifest: dict[str, Any], *, base_dir: Path) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    checked = 0
    pipeline = manifest.get("pipeline")
    if pipeline == "selective_gate_apply_and_readiness/v1":
        checked += verify_apply_pipeline_semantics(manifest, base_dir=base_dir, issues=issues)
    elif pipeline == "selective_gate_full_test_wrapper/v1":
        checked += verify_full_test_wrapper_semantics(manifest, base_dir=base_dir, issues=issues)
    return {"checked": checked, "issues": issues}


def verify_apply_pipeline_semantics(manifest: dict[str, Any], *, base_dir: Path, issues: list[dict[str, str]]) -> int:
    checked = 0
    summary = read_output_json(manifest, "summary", base_dir=base_dir, issues=issues)
    if summary is not None:
        checked += 1
        compare_subset(
            issues,
            expected=manifest.get("summary_checks"),
            actual=summary,
            code="manifest_summary_checks_mismatch",
            label="summary_checks",
        )
    summary_recomputed = recompute_apply_pipeline_summary_checks(manifest, base_dir=base_dir, issues=issues)
    if summary_recomputed is not None:
        checked += 1
        compare_known_keys(
            issues,
            expected=manifest.get("summary_checks"),
            actual=summary_recomputed,
            code="manifest_apply_summary_recomputed_checks_mismatch",
            label="summary_checks recomputed from predictions/cards",
        )
    readiness_recomputed = recompute_apply_pipeline_readiness(manifest, summary, base_dir=base_dir, issues=issues)
    if readiness_recomputed is not None:
        checked += 1
        compare_known_keys(
            issues,
            expected=manifest.get("readiness_checks"),
            actual=readiness_recomputed.get("checks") or {},
            code="manifest_apply_readiness_recomputed_checks_mismatch",
            label="readiness_checks recomputed fields",
        )
        checked += 1
        compare_value(
            issues,
            manifest.get("status"),
            readiness_recomputed.get("status"),
            "manifest_apply_readiness_recomputed_status_mismatch",
            "readiness status recomputed from recorded files",
        )
        compare_value(
            issues,
            manifest.get("issue_counts"),
            readiness_recomputed.get("issue_counts"),
            "manifest_apply_readiness_recomputed_issue_counts_mismatch",
            "readiness issue_counts recomputed from recorded files",
        )
    readiness = read_output_json(manifest, "readiness_json", base_dir=base_dir, issues=issues)
    if readiness is not None:
        checked += 1
        compare_value(issues, manifest.get("status"), readiness.get("status"), "manifest_readiness_status_mismatch", "status")
        compare_value(
            issues,
            manifest.get("issue_counts"),
            readiness.get("issue_counts"),
            "manifest_readiness_issue_counts_mismatch",
            "issue_counts",
        )
        compare_value(
            issues,
            manifest.get("readiness_checks"),
            readiness.get("checks"),
            "manifest_readiness_checks_mismatch",
            "readiness_checks",
        )
    return checked


def recompute_apply_pipeline_summary_checks(
    manifest: dict[str, Any],
    *,
    base_dir: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any] | None:
    predictions = input_fingerprint_path(manifest, "predictions", base_dir=base_dir, issues=issues)
    card_paths = input_fingerprint_paths(manifest, "cards", base_dir=base_dir, issues=issues)
    if predictions is None or not predictions.exists() or card_paths is None:
        return None
    try:
        prediction_rows = read_triplet_rows(predictions)
        prediction_pairs = [(str(a), str(b)) for a, b, _label in prediction_rows]
        seen_prediction_keys = set(prediction_pairs)
        effective_card_by_pair: dict[tuple[str, str], dict[str, Any]] = {}
        card_count = 0
        duplicate_cards = 0
        duplicate_cards_ignored_unusable = 0

        for path in card_paths:
            if not path.exists():
                return None
            for card in iter_card_jsonl(path):
                card_count += 1
                key = manifest_card_pair_key(card)
                if key in effective_card_by_pair:
                    duplicate_cards += 1
                    if not manifest_should_replace_effective_card(effective_card_by_pair[key], card):
                        duplicate_cards_ignored_unusable += 1
                        continue
                effective_card_by_pair[key] = card
    except ValueError as exc:
        add_issue(issues, "error", "manifest_apply_summary_recompute_invalid", str(exc))
        return None

    matched_cards = sum(1 for key in prediction_pairs if key in effective_card_by_pair)
    missing_cards = len(prediction_pairs) - matched_cards
    unmatched_cards = len(set(effective_card_by_pair) - seen_prediction_keys)
    recomputed = {
        "total_predictions": len(prediction_rows),
        "card_count": card_count,
        "duplicate_cards": duplicate_cards,
        "duplicate_cards_ignored_unusable": duplicate_cards_ignored_unusable,
        "card_selection_rule": "usable_card_priority_last_usable_wins",
        "matched_cards": matched_cards,
        "missing_cards": missing_cards,
    }
    summary_checks = manifest.get("summary_checks") if isinstance(manifest.get("summary_checks"), dict) else {}
    if "unmatched_cards" in summary_checks:
        recomputed["unmatched_cards"] = unmatched_cards
    override_csv = output_fingerprint_path(manifest, "override_csv", base_dir=base_dir, issues=issues)
    if override_csv is not None and override_csv.exists():
        recomputed["override_count"] = recompute_count_csv_rows(override_csv)
    return recomputed


def recompute_apply_pipeline_readiness(
    manifest: dict[str, Any],
    summary: dict[str, Any] | None,
    *,
    base_dir: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any] | None:
    if summary is None:
        return None
    predictions = input_fingerprint_path(manifest, "predictions", base_dir=base_dir, issues=issues)
    output_predictions = output_fingerprint_path(manifest, "output_predictions", base_dir=base_dir, issues=issues)
    actual = input_fingerprint_path(manifest, "actual", base_dir=base_dir, issues=issues)
    rows_csv = output_fingerprint_path(manifest, "rows_csv", base_dir=base_dir, issues=issues)
    override_csv = output_fingerprint_path(manifest, "override_csv", base_dir=base_dir, issues=issues)
    if predictions is None or output_predictions is None or not predictions.exists() or not output_predictions.exists():
        return None
    try:
        skip_content_check = bool((manifest.get("parameters") or {}).get("skip_content_check"))
        triplet_healths = [recompute_triplet_file_health(predictions, "baseline_predictions")]
        if actual is not None and actual.exists():
            triplet_healths.append(recompute_triplet_file_health(actual, "actual"))
        triplet_healths.append(recompute_triplet_file_health(output_predictions, "output_predictions"))
        file_consistency = None
        if not skip_content_check and rows_csv is not None and rows_csv.exists():
            prediction_audit = recompute_prediction_audit_consistency(
                predictions,
                output_predictions,
                rows_csv,
                override_csv if override_csv is not None and override_csv.exists() else None,
            )
            file_consistency = prediction_audit
        actual_consistency = None
        if not skip_content_check and actual is not None and actual.exists():
            actual_consistency = recompute_actual_metric_consistency(
                summary,
                actual,
                predictions,
                output_predictions,
                rows_csv if rows_csv is not None and rows_csv.exists() else None,
            )
        policy = summary.get("policy") if isinstance(summary.get("policy"), dict) else None
        parameters = manifest.get("parameters") if isinstance(manifest.get("parameters"), dict) else {}
        recomputed = recompute_assess_readiness(
            summary,
            policy=policy,
            actual_count=recompute_count_triplet_rows(actual) if actual is not None and actual.exists() else None,
            baseline_prediction_count=recompute_count_triplet_rows(predictions),
            output_prediction_count=recompute_count_triplet_rows(output_predictions),
            rows_csv_count=recompute_count_csv_rows(rows_csv) if rows_csv is not None and rows_csv.exists() else None,
            override_csv_count=recompute_count_csv_rows(override_csv) if override_csv is not None and override_csv.exists() else None,
            file_consistency=file_consistency,
            actual_consistency=actual_consistency,
            triplet_healths=triplet_healths,
            min_card_coverage=float(parameters.get("min_card_coverage") if parameters.get("min_card_coverage") is not None else 0.95),
            max_damage=int(parameters.get("max_damage") if parameters.get("max_damage") is not None else 0),
            require_actual=bool(parameters.get("require_actual")),
            content_check_skipped=skip_content_check,
        )
        expected_checks = manifest.get("readiness_checks") if isinstance(manifest.get("readiness_checks"), dict) else {}
        if not skip_content_check and "content_check_skipped" not in expected_checks:
            (recomputed.get("checks") or {}).pop("content_check_skipped", None)
        return recomputed
    except ValueError as exc:
        add_issue(issues, "error", "manifest_apply_triplet_invalid", str(exc))
        return None


def verify_full_test_wrapper_semantics(manifest: dict[str, Any], *, base_dir: Path, issues: list[dict[str, str]]) -> int:
    checked = 0
    input_triplets = recompute_full_test_input_triplets(manifest, base_dir=base_dir, issues=issues)
    if input_triplets is not None:
        checked += 1
        compare_value(
            issues,
            manifest.get("input_triplet_status"),
            input_triplets.get("status"),
            "manifest_input_triplet_status_mismatch",
            "input_triplet_status",
        )
        compare_value(
            issues,
            manifest.get("input_triplet_checks"),
            input_triplets.get("checks"),
            "manifest_input_triplet_checks_mismatch",
            "input_triplet_checks",
        )
    coverage = read_output_json(manifest, "coverage_json", base_dir=base_dir, issues=issues)
    if coverage is not None:
        checked += 1
        compare_value(
            issues,
            manifest.get("coverage_status"),
            coverage.get("status"),
            "manifest_coverage_status_mismatch",
            "coverage_status",
        )
        compare_subset(
            issues,
            expected=manifest.get("coverage_checks"),
            actual=coverage,
            code="manifest_coverage_checks_mismatch",
            label="coverage_checks",
        )
    recomputed_coverage = recompute_full_test_coverage(manifest, base_dir=base_dir, issues=issues)
    if recomputed_coverage is not None:
        checked += 1
        compare_value(
            issues,
            manifest.get("coverage_status"),
            recomputed_coverage.get("status"),
            "manifest_coverage_recomputed_status_mismatch",
            "coverage_status recomputed from predictions/cards",
        )
        compare_subset(
            issues,
            expected=manifest.get("coverage_checks"),
            actual=recomputed_coverage,
            code="manifest_coverage_recomputed_checks_mismatch",
            label="coverage_checks recomputed from predictions/cards",
        )
    merge_summaries = recompute_full_test_merge_summaries(manifest, base_dir=base_dir, issues=issues)
    if merge_summaries is not None:
        checked += 1
        compare_value(
            issues,
            manifest.get("merge_summary_status"),
            merge_summaries.get("status"),
            "manifest_merge_summary_status_mismatch",
            "merge_summary_status",
        )
        compare_known_keys(
            issues,
            expected=manifest.get("merge_summary_checks"),
            actual=merge_summaries.get("checks") or {},
            code="manifest_merge_summary_checks_mismatch",
            label="merge_summary_checks recomputed from merge summaries",
        )
    dynamic_contracts = read_output_json(manifest, "dynamic_contract_json", base_dir=base_dir, issues=issues)
    if dynamic_contracts is not None:
        checked += verify_full_test_dynamic_contract_semantics(manifest, dynamic_contracts, issues=issues)
    inner = manifest.get("inner_pipeline") if isinstance(manifest.get("inner_pipeline"), dict) else {}
    outputs = manifest.get("outputs") if isinstance(manifest.get("outputs"), dict) else {}
    inner_manifest_present = outputs.get("pipeline_manifest") is not None
    inner_verification_present = outputs.get("pipeline_manifest_verification_json") is not None
    checked += 1
    if inner_manifest_present != inner_verification_present:
        add_issue(
            issues,
            "error",
            "manifest_inner_outputs_presence_mismatch",
            "Inner pipeline manifest and inner manifest-verification outputs must either both be present or both be absent.",
        )
    checked += 1
    compare_value(
        issues,
        inner.get("ran"),
        inner_manifest_present and inner_verification_present,
        "manifest_inner_ran_mismatch",
        "inner_pipeline.ran",
    )
    pipeline_manifest = read_output_json(manifest, "pipeline_manifest", base_dir=base_dir, issues=issues)
    if pipeline_manifest is not None:
        checked += 1
        compare_value(issues, inner.get("status"), pipeline_manifest.get("status"), "manifest_inner_status_mismatch", "inner_pipeline.status")
        compare_value(
            issues,
            inner.get("issue_counts"),
            pipeline_manifest.get("issue_counts"),
            "manifest_inner_issue_counts_mismatch",
            "inner_pipeline.issue_counts",
        )
        compare_value(
            issues,
            inner.get("summary_checks"),
            pipeline_manifest.get("summary_checks"),
            "manifest_inner_summary_checks_mismatch",
            "inner_pipeline.summary_checks",
        )
        compare_value(
            issues,
            inner.get("readiness_status"),
            pipeline_manifest.get("status"),
            "manifest_inner_readiness_status_mismatch",
            "inner_pipeline.readiness_status",
        )
        compare_value(
            issues,
            inner.get("readiness_issue_counts"),
            pipeline_manifest.get("issue_counts"),
            "manifest_inner_readiness_issue_counts_mismatch",
            "inner_pipeline.readiness_issue_counts",
        )
        compare_value(
            issues,
            inner.get("readiness_checks"),
            summarize_inner_readiness_checks_from_pipeline_manifest(pipeline_manifest),
            "manifest_inner_readiness_checks_mismatch",
            "inner_pipeline.readiness_checks",
        )
    pipeline_verification = read_output_json(manifest, "pipeline_manifest_verification_json", base_dir=base_dir, issues=issues)
    if pipeline_verification is not None:
        checked += 1
        compare_value(
            issues,
            inner.get("manifest_verification_status"),
            pipeline_verification.get("status"),
            "manifest_inner_verification_status_mismatch",
            "inner_pipeline.manifest_verification_status",
        )
        compare_value(
            issues,
            inner.get("manifest_verification_checks"),
            {
                "checked_file_count": pipeline_verification.get("checked_file_count"),
                "verified_file_count": pipeline_verification.get("verified_file_count"),
                "missing_file_count": pipeline_verification.get("missing_file_count"),
                "mismatched_file_count": pipeline_verification.get("mismatched_file_count"),
            },
            "manifest_inner_verification_checks_mismatch",
            "inner_pipeline.manifest_verification_checks",
        )
    expected_status = recompute_full_test_wrapper_status(
        manifest,
        input_triplets=input_triplets,
        coverage=coverage,
        merge_summaries=merge_summaries,
        dynamic_contracts=dynamic_contracts,
        pipeline_manifest=pipeline_manifest,
        pipeline_verification=pipeline_verification,
    )
    if expected_status is not None:
        checked += 1
        compare_value(
            issues,
            manifest.get("status"),
            expected_status,
            "manifest_full_test_status_mismatch",
            "full-test wrapper status",
        )
    return checked


def summarize_inner_readiness_checks_from_pipeline_manifest(pipeline_manifest: dict[str, Any]) -> dict[str, Any] | None:
    checks = pipeline_manifest.get("readiness_checks")
    if not isinstance(checks, dict):
        return None
    keys = [
        "total_predictions",
        "card_count",
        "matched_cards",
        "missing_cards",
        "duplicate_cards",
        "duplicate_cards_ignored_unusable",
        "card_selection_rule",
        "card_coverage",
        "override_count",
        "actual_available",
        "damage",
        "net_gain",
        "baseline_f1",
        "final_f1",
    ]
    return {key: checks.get(key) for key in keys}


def verify_full_test_dynamic_contract_semantics(
    manifest: dict[str, Any],
    dynamic_contracts: dict[str, Any],
    *,
    issues: list[dict[str, str]],
) -> int:
    checked = 0
    recorded = manifest.get("dynamic_evidence_contracts")
    if not isinstance(recorded, dict):
        add_issue(
            issues,
            "error",
            "manifest_dynamic_contracts_missing",
            "Manifest dynamic_evidence_contracts must be an object.",
        )
        return 1

    for key, code in [
        ("status", "manifest_dynamic_contract_status_mismatch"),
        ("issue_counts", "manifest_dynamic_contract_issue_counts_mismatch"),
        ("summary", "manifest_dynamic_contract_summary_mismatch"),
        ("selection", "manifest_dynamic_contract_selection_mismatch"),
        ("dynamic_route_accounting", "manifest_dynamic_contract_dynamic_route_accounting_mismatch"),
        ("architecture_contract_accounting", "manifest_dynamic_contract_architecture_contract_accounting_mismatch"),
        ("fusion_decision_accounting", "manifest_dynamic_contract_fusion_decision_accounting_mismatch"),
        ("executable_evidence_integrity_accounting", "manifest_dynamic_contract_executable_integrity_accounting_mismatch"),
        ("llm_expert_contract_accounting", "manifest_dynamic_contract_llm_expert_contract_accounting_mismatch"),
        ("runtime_fixture_accounting", "manifest_dynamic_contract_runtime_fixture_accounting_mismatch"),
        ("correction_accounting", "manifest_dynamic_contract_correction_accounting_mismatch"),
    ]:
        checked += 1
        compare_value(
            issues,
            recorded.get(key),
            dynamic_contracts.get(key),
            code,
            f"dynamic_evidence_contracts.{key}",
        )

    checked += verify_architecture_contract_accounting_semantics(
        recorded.get("architecture_contract_accounting") if isinstance(recorded.get("architecture_contract_accounting"), dict) else {},
        dynamic_contracts.get("architecture_contract_accounting")
        if isinstance(dynamic_contracts.get("architecture_contract_accounting"), dict)
        else {},
        issues=issues,
    )

    checked += 1
    compare_value(
        issues,
        recorded.get("blocking"),
        dynamic_contracts_block_deployment(
            dynamic_contracts,
            allow_dynamic_contract_issues=bool((manifest.get("parameters") or {}).get("allow_dynamic_contract_issues")),
        ),
        "manifest_dynamic_contract_blocking_mismatch",
        "dynamic_evidence_contracts.blocking",
    )
    checked += 1
    compare_value(
        issues,
        recorded.get("deployment_blockers"),
        dynamic_contract_deployment_blockers(
            dynamic_contracts,
            allow_dynamic_contract_issues=bool((manifest.get("parameters") or {}).get("allow_dynamic_contract_issues")),
        ),
        "manifest_dynamic_contract_deployment_blockers_mismatch",
        "dynamic_evidence_contracts.deployment_blockers",
    )
    checked += 1
    compare_value(
        issues,
        recorded.get("deployment_policy_decision"),
        dynamic_contract_deployment_decision(
            dynamic_contracts,
            allow_dynamic_contract_issues=bool((manifest.get("parameters") or {}).get("allow_dynamic_contract_issues")),
        ),
        "manifest_dynamic_contract_deployment_policy_decision_mismatch",
        "dynamic_evidence_contracts.deployment_policy_decision",
    )
    decision_ok, decision_reasons = verify_dynamic_contract_deployment_decision(
        recorded.get("deployment_policy_decision") if isinstance(recorded.get("deployment_policy_decision"), dict) else {},
        dynamic_contracts,
        allow_dynamic_contract_issues=bool((manifest.get("parameters") or {}).get("allow_dynamic_contract_issues")),
    )
    if not decision_ok:
        for reason in decision_reasons:
            add_issue(
                issues,
                "error",
                f"manifest_dynamic_contract_{reason}",
                f"dynamic_evidence_contracts.deployment_policy_decision failed verifier check: {reason}.",
            )
    checked += 1
    compare_value(
        issues,
        recorded.get("dynamic_route_certificate_blocking"),
        dynamic_route_certificates_block_deployment(dynamic_contracts),
        "manifest_dynamic_contract_route_certificate_blocking_mismatch",
        "dynamic_evidence_contracts.dynamic_route_certificate_blocking",
    )
    checked += 1
    compare_value(
        issues,
        recorded.get("architecture_contract_blocking"),
        architecture_contracts_block_deployment(dynamic_contracts),
        "manifest_dynamic_contract_architecture_blocking_mismatch",
        "dynamic_evidence_contracts.architecture_contract_blocking",
    )
    checked += 1
    compare_value(
        issues,
        recorded.get("fusion_decision_contract_blocking"),
        fusion_decision_contracts_block_deployment(dynamic_contracts),
        "manifest_dynamic_contract_fusion_decision_blocking_mismatch",
        "dynamic_evidence_contracts.fusion_decision_contract_blocking",
    )
    checked += 1
    compare_value(
        issues,
        recorded.get("executable_evidence_integrity_blocking"),
        executable_evidence_integrity_blocks_deployment(dynamic_contracts),
        "manifest_dynamic_contract_executable_integrity_blocking_mismatch",
        "dynamic_evidence_contracts.executable_evidence_integrity_blocking",
    )
    checked += 1
    compare_value(
        issues,
        recorded.get("llm_expert_contract_blocking"),
        llm_expert_contracts_block_deployment(dynamic_contracts),
        "manifest_dynamic_contract_llm_expert_blocking_mismatch",
        "dynamic_evidence_contracts.llm_expert_contract_blocking",
    )
    checked += 1
    compare_value(
        issues,
        recorded.get("runtime_fixture_contract_blocking"),
        runtime_fixture_contracts_block_deployment(dynamic_contracts),
        "manifest_dynamic_contract_runtime_fixture_blocking_mismatch",
        "dynamic_evidence_contracts.runtime_fixture_contract_blocking",
    )
    return checked


def verify_architecture_contract_accounting_semantics(
    recorded: dict[str, Any],
    recomputed: dict[str, Any],
    *,
    issues: list[dict[str, str]],
) -> int:
    checked = 0
    for field, code in [
        (
            "llm_component_final_decision_permission_violations",
            "manifest_dynamic_contract_llm_final_decision_permission_violation_count_mismatch",
        ),
        (
            "bounded_expert_components_match_route",
            "manifest_dynamic_contract_bounded_expert_components_match_count_mismatch",
        ),
        (
            "bounded_expert_components_mismatch_route",
            "manifest_dynamic_contract_bounded_expert_components_mismatch_count_mismatch",
        ),
        (
            "unauthorized_bounded_expert_artifact_permission_violations",
            "manifest_dynamic_contract_unauthorized_bounded_expert_permission_count_mismatch",
        ),
    ]:
        checked += 1
        compare_value(
            issues,
            recorded.get(field),
            recomputed.get(field),
            code,
            f"dynamic_evidence_contracts.architecture_contract_accounting.{field}",
        )
    return checked


def recompute_full_test_merge_summaries(
    manifest: dict[str, Any],
    *,
    base_dir: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any] | None:
    paths = input_fingerprint_paths(manifest, "merge_summaries", base_dir=base_dir, issues=issues)
    if paths is None:
        return None
    card_paths = input_fingerprint_paths(manifest, "cards", base_dir=base_dir, issues=issues) or []
    card_fingerprints = []
    for card_path in card_paths:
        if card_path.exists():
            fingerprint = file_fingerprint(card_path)
            card_fingerprints.append(
                {
                    "path": str(card_path.resolve()),
                    "bytes": fingerprint["bytes"],
                    "sha256": fingerprint["sha256"],
                }
            )
    counters: Counter[str] = Counter()
    blockers: list[str] = []
    summaries = []
    for path in paths:
        row: dict[str, Any] = {
            "path": str(path.resolve()),
            "exists": path.exists(),
            "valid_json": False,
            "schema_version": None,
            "schema_valid": False,
            "summary_checks_match_output": False,
            "recomputed_output_checks": None,
            "output": None,
            "output_path_matches_card_input": False,
            "matched_output_path_card_input": None,
            "output_fingerprint": None,
            "output_matches_card_input": False,
            "matched_card_input": None,
            "status": None,
            "output_published": None,
            "deployment_eligible": None,
            "diagnostic_only": None,
            "publish_reason": None,
            "deployment_blockers": [],
            "blocking_reasons": [],
            "blocking": True,
            "error": None,
        }
        counters["provided_summaries"] += 1
        if not path.exists():
            row["error"] = "missing"
            counters["missing_summaries"] += 1
            blockers.append("merge_summary_missing")
            summaries.append(row)
            continue
        try:
            obj = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            row["error"] = str(exc)
            counters["invalid_json_summaries"] += 1
            blockers.append("merge_summary_invalid_json")
            summaries.append(row)
            continue
        if not isinstance(obj, dict):
            row["error"] = "root is not an object"
            counters["invalid_json_summaries"] += 1
            blockers.append("merge_summary_invalid_json")
            summaries.append(row)
            continue
        deployment_eligible = obj.get("deployment_eligible") is True
        deployment_blockers = normalize_manifest_merge_summary_blockers(obj.get("deployment_blockers"))
        row.update(
            {
                "valid_json": True,
                "schema_version": obj.get("schema_version"),
                "schema_valid": obj.get("schema_version") == MERGE_SUMMARY_SCHEMA,
                "status": obj.get("status"),
                "output": obj.get("output"),
                "output_fingerprint": obj.get("output_fingerprint"),
                "output_published": obj.get("output_published"),
                "deployment_eligible": obj.get("deployment_eligible"),
                "diagnostic_only": obj.get("diagnostic_only"),
                "publish_reason": obj.get("publish_reason"),
                "deployment_blockers": deployment_blockers,
            }
        )
        output_match = match_manifest_merge_summary_output_to_card_input(obj.get("output_fingerprint"), card_fingerprints)
        output_path_match = match_manifest_merge_summary_output_path_to_card_input(
            obj.get("output"),
            card_fingerprints,
            summary_path=path,
        )
        row["output_matches_card_input"] = output_match is not None
        row["matched_card_input"] = output_match.get("path") if output_match else None
        row["output_path_matches_card_input"] = output_path_match is not None
        row["matched_output_path_card_input"] = output_path_match.get("path") if output_path_match else None
        recomputed_output_checks = None
        summary_checks_match_output = False
        if output_match is not None:
            try:
                recomputed_output_checks = summarize_manifest_card_file_for_merge_summary(Path(str(output_match["path"])))
                summary_checks_match_output = compare_manifest_merge_summary_output_checks(
                    obj.get("checks"),
                    recomputed_output_checks,
                )
            except ValueError as exc:
                row["error"] = str(exc)
        row["recomputed_output_checks"] = recomputed_output_checks
        row["summary_checks_match_output"] = summary_checks_match_output
        row["blocking"] = not deployment_eligible or output_match is None
        counters["deployment_eligible_summaries" if deployment_eligible else "not_deployment_eligible_summaries"] += 1
        if obj.get("diagnostic_only"):
            counters["diagnostic_only_summaries"] += 1
        counters["valid_schema_summaries" if row["schema_valid"] else "invalid_schema_summaries"] += 1
        counters["ready_status_summaries" if obj.get("status") == "ready" else "non_ready_status_summaries"] += 1
        counters["output_published_summaries" if obj.get("output_published") is True else "output_not_published_summaries"] += 1
        counters[
            "ready_publish_reason_summaries"
            if obj.get("publish_reason") == MERGE_SUMMARY_READY_PUBLISH_REASON
            else "unexpected_publish_reason_summaries"
        ] += 1
        if isinstance(obj.get("output_fingerprint"), dict):
            counters["output_fingerprint_present_summaries"] += 1
        else:
            counters["output_fingerprint_missing_summaries"] += 1
        if isinstance(obj.get("output"), str) and obj.get("output").strip():
            counters["output_path_present_summaries"] += 1
            if output_path_match is not None:
                counters["output_path_matched_summaries"] += 1
            else:
                counters["output_path_mismatched_summaries"] += 1
        else:
            counters["output_path_missing_summaries"] += 1
        if output_match is not None:
            counters["output_fingerprint_matched_summaries"] += 1
            if summary_checks_match_output:
                counters["summary_checks_matched_output_summaries"] += 1
            else:
                counters["summary_checks_mismatched_output_summaries"] += 1
        elif isinstance(obj.get("output_fingerprint"), dict):
            counters["output_fingerprint_mismatched_summaries"] += 1
        row_blockers = manifest_merge_summary_semantic_blockers(
            obj,
            deployment_eligible=deployment_eligible,
            deployment_blockers=deployment_blockers,
            schema_valid=bool(row["schema_valid"]),
            output_match=output_match,
            output_path_match=output_path_match,
            summary_checks_match_output=summary_checks_match_output,
        )
        row["blocking_reasons"] = row_blockers
        row["blocking"] = bool(row_blockers)
        blockers.extend(row_blockers)
        if not deployment_eligible:
            blockers.extend(deployment_blockers)
        if output_match is None:
            if isinstance(obj.get("output_fingerprint"), dict):
                blockers.append("merge_summary_output_fingerprint_mismatch")
            else:
                blockers.append("merge_summary_output_fingerprint_missing")
        if output_path_match is None:
            if isinstance(obj.get("output"), str) and obj.get("output").strip():
                blockers.append("merge_summary_output_path_mismatch")
            else:
                blockers.append("merge_summary_output_path_missing")
        if deployment_eligible and output_match is not None and not summary_checks_match_output:
            blockers.append("merge_summary_output_checks_mismatch")
        summaries.append(row)

    for key in [
        "provided_summaries",
        "deployment_eligible_summaries",
        "not_deployment_eligible_summaries",
        "diagnostic_only_summaries",
        "valid_schema_summaries",
        "invalid_schema_summaries",
        "ready_status_summaries",
        "non_ready_status_summaries",
        "output_published_summaries",
        "output_not_published_summaries",
        "ready_publish_reason_summaries",
        "unexpected_publish_reason_summaries",
        "output_path_present_summaries",
        "output_path_missing_summaries",
        "output_path_matched_summaries",
        "output_path_mismatched_summaries",
        "output_fingerprint_present_summaries",
        "output_fingerprint_missing_summaries",
        "output_fingerprint_matched_summaries",
        "output_fingerprint_mismatched_summaries",
        "summary_checks_matched_output_summaries",
        "summary_checks_mismatched_output_summaries",
        "missing_summaries",
        "invalid_json_summaries",
    ]:
        counters.setdefault(key, 0)
    blocking_summary_count = sum(1 for row in summaries if row["blocking"])
    counters["blocking_summary_count"] = blocking_summary_count
    status = "not_provided" if not paths else "blocked" if blocking_summary_count else "ok"
    return {
        "status": status,
        "checks": dict(counters),
        "blocking_summary_count": blocking_summary_count,
        "deployment_blockers": sorted(set(blockers)),
        "summaries": summaries,
    }


def normalize_manifest_merge_summary_blockers(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return ["merge_summary_deployment_blockers_invalid"]
    return [str(item) for item in value]


def manifest_merge_summary_semantic_blockers(
    obj: dict[str, Any],
    *,
    deployment_eligible: bool,
    deployment_blockers: list[str],
    schema_valid: bool,
    output_match: dict[str, Any] | None,
    output_path_match: dict[str, Any] | None,
    summary_checks_match_output: bool,
) -> list[str]:
    blockers: list[str] = []
    if not schema_valid:
        blockers.append("merge_summary_schema_invalid")
    if obj.get("status") != "ready":
        blockers.append(f"merge_summary_status_{obj.get('status') or 'unknown'}")
    if obj.get("output_published") is not True:
        blockers.append("merge_summary_output_not_published")
    if obj.get("diagnostic_only") is True:
        blockers.append("merge_summary_diagnostic_only")
    if obj.get("publish_reason") != MERGE_SUMMARY_READY_PUBLISH_REASON:
        blockers.append("merge_summary_publish_reason_unexpected")
    if not deployment_eligible:
        if deployment_blockers:
            blockers.extend(deployment_blockers)
        else:
            blockers.append("merge_summary_not_deployment_eligible")
    elif deployment_blockers:
        blockers.append("merge_summary_has_deployment_blockers")
        blockers.extend(deployment_blockers)
    if output_match is None:
        if isinstance(obj.get("output_fingerprint"), dict):
            blockers.append("merge_summary_output_fingerprint_mismatch")
        else:
            blockers.append("merge_summary_output_fingerprint_missing")
    elif not summary_checks_match_output:
        blockers.append("merge_summary_output_checks_mismatch")
    if output_path_match is None:
        if isinstance(obj.get("output"), str) and obj.get("output").strip():
            blockers.append("merge_summary_output_path_mismatch")
        else:
            blockers.append("merge_summary_output_path_missing")
    return sorted(set(blockers))


def match_manifest_merge_summary_output_to_card_input(
    output_fingerprint: Any,
    card_fingerprints: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not isinstance(output_fingerprint, dict):
        return None
    expected_bytes = output_fingerprint.get("bytes")
    expected_sha = output_fingerprint.get("sha256")
    if expected_bytes is None or expected_sha is None:
        return None
    for fingerprint in card_fingerprints:
        if fingerprint["bytes"] == expected_bytes and fingerprint["sha256"] == expected_sha:
            return fingerprint
    return None


def match_manifest_merge_summary_output_path_to_card_input(
    output: Any,
    card_fingerprints: list[dict[str, Any]],
    *,
    summary_path: Path,
) -> dict[str, Any] | None:
    normalized = normalize_manifest_merge_summary_output_path(output, summary_path=summary_path)
    if normalized is None:
        return None
    for fingerprint in card_fingerprints:
        if fingerprint["path"] == normalized:
            return fingerprint
    return None


def normalize_manifest_merge_summary_output_path(output: Any, *, summary_path: Path) -> str | None:
    if not isinstance(output, str) or not output.strip():
        return None
    candidate = Path(output)
    if not candidate.is_absolute():
        candidate = summary_path.parent / candidate
    return str(candidate.resolve())


def summarize_manifest_card_file_for_merge_summary(path: Path) -> dict[str, int]:
    merged_cards = 0
    usable_cards = 0
    unusable_cards = 0
    for card in iter_card_jsonl(path):
        merged_cards += 1
        if manifest_card_health_status(card) == "usable":
            usable_cards += 1
        else:
            unusable_cards += 1
    return {
        "merged_cards": merged_cards,
        "usable_cards": usable_cards,
        "unusable_cards": unusable_cards,
    }


def compare_manifest_merge_summary_output_checks(summary_checks: Any, recomputed: dict[str, int] | None) -> bool:
    if recomputed is None or not isinstance(summary_checks, dict):
        return False
    return all(summary_checks.get(key) == value for key, value in recomputed.items())


def recompute_full_test_wrapper_status(
    manifest: dict[str, Any],
    *,
    input_triplets: dict[str, Any] | None,
    coverage: dict[str, Any] | None,
    merge_summaries: dict[str, Any] | None,
    dynamic_contracts: dict[str, Any] | None,
    pipeline_manifest: dict[str, Any] | None,
    pipeline_verification: dict[str, Any] | None,
) -> str | None:
    if coverage is None or input_triplets is None:
        return None
    coverage_checks = coverage
    parameters = manifest.get("parameters") if isinstance(manifest.get("parameters"), dict) else {}
    if int(coverage_checks.get("duplicate_prediction_pairs") or 0):
        return "coverage_duplicate_predictions"
    if input_triplets.get("status") != "ok":
        return "input_triplet_mismatch"
    if (
        merge_summaries is not None
        and int(merge_summaries.get("blocking_summary_count") or 0)
        and not bool(parameters.get("allow_diagnostic_merge_summary"))
    ):
        return "merge_summary_not_deployable"
    if int(coverage_checks.get("missing_prediction_pairs") or 0) and not bool(parameters.get("allow_incomplete_cards")):
        return "coverage_incomplete"
    if int(coverage_checks.get("unusable_matched_prediction_pairs") or 0) and not bool(parameters.get("allow_unusable_cards")):
        return "coverage_unusable"
    if pipeline_manifest is None or pipeline_verification is None:
        return None
    if (
        pipeline_manifest.get("status") != "ready"
        or pipeline_verification.get("status") != "verified"
        or bool(parameters.get("allow_incomplete_cards"))
        or bool(parameters.get("allow_unusable_cards"))
        or dynamic_contracts_block_deployment(
            dynamic_contracts or {},
            allow_dynamic_contract_issues=bool(parameters.get("allow_dynamic_contract_issues")),
        )
        or (
            merge_summaries is not None
            and int(merge_summaries.get("blocking_summary_count") or 0)
            and bool(parameters.get("allow_diagnostic_merge_summary"))
        )
    ):
        return "diagnostic_only"
    return "ready"


def recompute_full_test_coverage(
    manifest: dict[str, Any],
    *,
    base_dir: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any] | None:
    predictions = input_fingerprint_path(manifest, "predictions", base_dir=base_dir, issues=issues)
    card_paths = input_fingerprint_paths(manifest, "cards", base_dir=base_dir, issues=issues)
    if predictions is None or not predictions.exists() or card_paths is None:
        return None
    try:
        prediction_rows = read_triplet_rows(predictions)
        prediction_pairs = [(str(a), str(b)) for a, b, _label in prediction_rows]
        prediction_set = set(prediction_pairs)
        prediction_counter = Counter(prediction_pairs)
        duplicate_prediction_pairs = sorted(key for key, count in prediction_counter.items() if count > 1)
        duplicate_counter: Counter[tuple[str, str]] = Counter()
        seen_cards: set[tuple[str, str]] = set()
        effective_card_by_pair: dict[tuple[str, str], dict[str, Any]] = {}
        card_count = 0
        all_card_health: Counter[str] = Counter()
        duplicate_cards_ignored_unusable = 0

        for path in card_paths:
            if not path.exists():
                return None
            for card in iter_card_jsonl(path):
                card_count += 1
                key = manifest_card_pair_key(card)
                if key in seen_cards:
                    duplicate_counter[key] += 1
                    if not manifest_should_replace_effective_card(effective_card_by_pair[key], card):
                        duplicate_cards_ignored_unusable += 1
                        all_card_health[manifest_card_health_status(card)] += 1
                        continue
                seen_cards.add(key)
                all_card_health[manifest_card_health_status(card)] += 1
                effective_card_by_pair[key] = card
    except ValueError as exc:
        add_issue(issues, "error", "manifest_coverage_recompute_invalid", str(exc))
        return None

    matched_cards: set[tuple[str, str]] = set()
    usable_matched_cards: set[tuple[str, str]] = set()
    unusable_matched_cards: set[tuple[str, str]] = set()
    unmatched_cards: set[tuple[str, str]] = set()
    card_health: Counter[str] = Counter()
    for key, card in effective_card_by_pair.items():
        if key not in prediction_set:
            unmatched_cards.add(key)
            continue
        matched_cards.add(key)
        health = manifest_card_health_status(card)
        card_health[health] += 1
        if health == "usable":
            usable_matched_cards.add(key)
        else:
            unusable_matched_cards.add(key)

    missing_pairs = [key for key in prediction_pairs if key not in matched_cards]
    unusable_pairs = [key for key in prediction_pairs if key in matched_cards and key not in usable_matched_cards]
    missing_or_unusable_pairs = [key for key in prediction_pairs if key not in usable_matched_cards]
    duplicate_pairs = [key for key, count in duplicate_counter.items() if count > 0]
    coverage = len(matched_cards) / len(prediction_pairs) if prediction_pairs else 0.0
    usable_coverage = len(usable_matched_cards) / len(prediction_pairs) if prediction_pairs else 0.0
    if duplicate_prediction_pairs:
        status = "duplicate_predictions"
    elif missing_pairs:
        status = "incomplete"
    elif unusable_pairs:
        status = "unusable_cards"
    else:
        status = "full_coverage"
    return {
        "status": status,
        "prediction_rows": len(prediction_rows),
        "prediction_unique_pairs": len(prediction_set),
        "duplicate_prediction_pairs": len(duplicate_prediction_pairs),
        "card_rows": card_count,
        "card_unique_pairs": len(seen_cards),
        "matched_prediction_pairs": len(matched_cards),
        "usable_matched_prediction_pairs": len(usable_matched_cards),
        "unusable_matched_prediction_pairs": len(unusable_pairs),
        "missing_prediction_pairs": len(missing_pairs),
        "missing_or_unusable_prediction_pairs": len(missing_or_unusable_pairs),
        "unmatched_card_pairs": len(unmatched_cards),
        "duplicate_card_pairs": len(duplicate_pairs),
        "duplicate_cards_ignored_unusable": duplicate_cards_ignored_unusable,
        "card_selection_rule": "usable_card_priority_last_usable_wins",
        "card_health_counts": dict(card_health),
        "all_card_health_counts": dict(all_card_health),
        "card_coverage": round(coverage, 6),
        "usable_card_coverage": round(usable_coverage, 6),
    }


def input_fingerprint_paths(
    manifest: dict[str, Any],
    key: str,
    *,
    base_dir: Path,
    issues: list[dict[str, str]],
) -> list[Path] | None:
    inputs = manifest.get("inputs") if isinstance(manifest.get("inputs"), dict) else {}
    fingerprints = inputs.get(key)
    if fingerprints is None:
        return None
    if not isinstance(fingerprints, list):
        add_issue(issues, "error", "manifest_semantic_input_fingerprint_invalid", f"inputs.{key} is not a fingerprint list.")
        return None
    paths: list[Path] = []
    for idx, fingerprint in enumerate(fingerprints):
        if not isinstance(fingerprint, dict):
            add_issue(
                issues,
                "error",
                "manifest_semantic_input_fingerprint_invalid",
                f"inputs.{key}[{idx}] is not a fingerprint object.",
            )
            return None
        paths.append(resolve_fingerprint_path(fingerprint, base_dir=base_dir))
    return paths


def iter_card_jsonl(path: Path) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                card = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid card JSON at {path}:{line_no}: {exc}") from exc
            if not isinstance(card, dict):
                raise ValueError(f"card JSON root at {path}:{line_no} is not an object")
            cards.append(card)
    return cards


def manifest_card_pair_key(card: dict[str, Any]) -> tuple[str, str]:
    ids = card.get("function_ids") if isinstance(card.get("function_ids"), dict) else {}
    return str(ids.get("a", "")), str(ids.get("b", ""))


def manifest_card_health_status(card: dict[str, Any]) -> str:
    decision = card.get("decision") if isinstance(card.get("decision"), dict) else {}
    pred = coerce_manifest_label(decision.get("pred_label"))
    if pred not in (0, 1):
        llm = card.get("llm_evidence") if isinstance(card.get("llm_evidence"), dict) else {}
        if llm.get("status") == "failed":
            return "unusable_llm_failed_no_prediction"
        verdict = str(decision.get("verdict") or "")
        if verdict in {"unknown", "context_insufficient"}:
            return "unusable_unknown_no_prediction"
        return "unusable_no_prediction"
    return "usable"


def manifest_should_replace_effective_card(existing: dict[str, Any], candidate: dict[str, Any]) -> bool:
    existing_usable = manifest_card_health_status(existing) == "usable"
    candidate_usable = manifest_card_health_status(candidate) == "usable"
    return candidate_usable or not existing_usable


def coerce_manifest_label(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        parsed = int(value)
        return parsed if parsed in (0, 1) else None
    except (TypeError, ValueError):
        return None


def recompute_full_test_input_triplets(
    manifest: dict[str, Any],
    *,
    base_dir: Path,
    issues: list[dict[str, str]],
) -> dict[str, Any] | None:
    predictions = input_fingerprint_path(manifest, "predictions", base_dir=base_dir, issues=issues)
    actual = input_fingerprint_path(manifest, "actual", base_dir=base_dir, issues=issues)
    if predictions is None or actual is None or not predictions.exists() or not actual.exists():
        return None
    try:
        prediction_rows = read_triplet_rows(predictions)
        actual_rows = read_triplet_rows(actual)
    except ValueError as exc:
        add_issue(issues, "error", "manifest_input_triplet_invalid", str(exc))
        return None
    prediction_pairs = [(a, b) for a, b, _label in prediction_rows]
    actual_pairs = [(a, b) for a, b, _label in actual_rows]
    prediction_duplicate_pairs = duplicate_pair_count(prediction_pairs)
    actual_duplicate_pairs = duplicate_pair_count(actual_pairs)
    checked_rows = min(len(prediction_rows), len(actual_rows))
    pair_mismatches = sum(1 for idx in range(checked_rows) if prediction_pairs[idx] != actual_pairs[idx])
    row_count_mismatch = len(prediction_rows) != len(actual_rows)
    if row_count_mismatch or pair_mismatches:
        status = "actual_prediction_mismatch"
    elif actual_duplicate_pairs:
        status = "actual_duplicate_pairs"
    elif prediction_duplicate_pairs:
        status = "prediction_duplicate_pairs"
    else:
        status = "ok"
    return {
        "status": status,
        "checks": {
            "prediction_rows": len(prediction_rows),
            "prediction_unique_pairs": len(set(prediction_pairs)),
            "prediction_duplicate_pairs": prediction_duplicate_pairs,
            "actual_rows": len(actual_rows),
            "actual_unique_pairs": len(set(actual_pairs)),
            "actual_duplicate_pairs": actual_duplicate_pairs,
            "actual_prediction_checked_rows": checked_rows,
            "actual_prediction_row_count_mismatch": row_count_mismatch,
            "actual_prediction_pair_mismatches": pair_mismatches,
        },
    }


def input_fingerprint_path(
    manifest: dict[str, Any],
    key: str,
    *,
    base_dir: Path,
    issues: list[dict[str, str]],
) -> Path | None:
    inputs = manifest.get("inputs") if isinstance(manifest.get("inputs"), dict) else {}
    fingerprint = inputs.get(key)
    if fingerprint is None:
        return None
    if not isinstance(fingerprint, dict):
        add_issue(issues, "error", "manifest_semantic_input_fingerprint_invalid", f"inputs.{key} is not a fingerprint object.")
        return None
    return resolve_fingerprint_path(fingerprint, base_dir=base_dir)


def output_fingerprint_path(
    manifest: dict[str, Any],
    key: str,
    *,
    base_dir: Path,
    issues: list[dict[str, str]],
) -> Path | None:
    outputs = manifest.get("outputs") if isinstance(manifest.get("outputs"), dict) else {}
    fingerprint = outputs.get(key)
    if fingerprint is None:
        return None
    if not isinstance(fingerprint, dict):
        add_issue(issues, "error", "manifest_semantic_output_fingerprint_invalid", f"outputs.{key} is not a fingerprint object.")
        return None
    return resolve_fingerprint_path(fingerprint, base_dir=base_dir)


def triplet_health_checks(path: Path, role: str) -> dict[str, Any]:
    rows = read_triplet_rows(path)
    pairs = [(a, b) for a, b, _label in rows]
    return {
        f"{role}_rows": len(rows),
        f"{role}_unique_pairs": len(set(pairs)),
        f"{role}_duplicate_pairs": duplicate_pair_count(pairs),
    }


def read_triplet_rows(path: Path) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) < 3:
                raise ValueError(f"expected at least 3 columns at {path}:{line_no}, got {len(parts)}")
            try:
                label = int(parts[2])
            except ValueError as exc:
                raise ValueError(f"expected integer label at {path}:{line_no}, got {parts[2]!r}") from exc
            rows.append((parts[0], parts[1], label))
    return rows


def duplicate_pair_count(pairs: list[tuple[str, str]]) -> int:
    counts: dict[tuple[str, str], int] = {}
    for pair in pairs:
        counts[pair] = counts.get(pair, 0) + 1
    return sum(1 for count in counts.values() if count > 1)


def read_output_json(manifest: dict[str, Any], key: str, *, base_dir: Path, issues: list[dict[str, str]]) -> dict[str, Any] | None:
    outputs = manifest.get("outputs") if isinstance(manifest.get("outputs"), dict) else {}
    fingerprint = outputs.get(key)
    if fingerprint is None:
        return None
    if not isinstance(fingerprint, dict):
        add_issue(issues, "error", "manifest_semantic_output_fingerprint_invalid", f"outputs.{key} is not a fingerprint object.")
        return None
    path = resolve_fingerprint_path(fingerprint, base_dir=base_dir)
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        add_issue(issues, "error", "manifest_semantic_json_invalid", f"outputs.{key} is not valid JSON: {exc}")
        return None
    if not isinstance(obj, dict):
        add_issue(issues, "error", "manifest_semantic_json_invalid", f"outputs.{key} JSON root is not an object.")
        return None
    return obj


def compare_subset(
    issues: list[dict[str, str]],
    *,
    expected: Any,
    actual: dict[str, Any],
    code: str,
    label: str,
) -> None:
    if expected is None:
        return
    if not isinstance(expected, dict):
        add_issue(issues, "error", code, f"Manifest {label} is not an object.")
        return
    mismatched = []
    for key, expected_value in expected.items():
        if actual.get(key) != expected_value:
            mismatched.append(key)
    if mismatched:
        add_issue(issues, "error", code, f"Manifest {label} differs from output JSON for keys: {', '.join(mismatched[:20])}.")


def compare_known_keys(
    issues: list[dict[str, str]],
    *,
    expected: Any,
    actual: dict[str, Any],
    code: str,
    label: str,
) -> None:
    if not isinstance(expected, dict):
        add_issue(issues, "error", code, f"Manifest {label} is not an object.")
        return
    mismatched = []
    for key, actual_value in actual.items():
        if expected.get(key) != actual_value:
            mismatched.append(key)
    if mismatched:
        add_issue(issues, "error", code, f"Manifest {label} differs from recomputed triplet checks for keys: {', '.join(mismatched[:20])}.")


def compare_value(issues: list[dict[str, str]], expected: Any, actual: Any, code: str, label: str) -> None:
    if expected != actual:
        add_issue(issues, "error", code, f"Manifest {label}={expected!r}, but output JSON has {actual!r}.")


def file_fingerprint(path: Path) -> dict[str, Any]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            size += len(chunk)
            h.update(chunk)
    return {"path": str(path.resolve()), "bytes": size, "sha256": h.hexdigest()}


def add_issue(issues: list[dict[str, str]], severity: str, code: str, message: str) -> None:
    issues.append({"severity": severity, "code": code, "message": message})


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def write_report(path: Path, result: dict[str, Any]) -> None:
    certificate = result.get("manifest_certificate") if isinstance(result.get("manifest_certificate"), dict) else {}
    lines = [
        "# Selective Gate Manifest Verification",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Checks",
        "",
        "| check | value |",
        "| --- | ---: |",
        f"| checked_file_count | {result['checked_file_count']} |",
        f"| verified_file_count | {result['verified_file_count']} |",
        f"| missing_file_count | {result['missing_file_count']} |",
        f"| mismatched_file_count | {result['mismatched_file_count']} |",
        f"| semantic_check_count | {result.get('semantic_check_count', 0)} |",
        f"| semantic_issue_count | {result.get('semantic_issue_count', 0)} |",
        f"| manifest_certificate_status | {certificate.get('status')} |",
        f"| manifest_certificate_sha256 | {short_sha(str(certificate.get('actual_certificate_sha256') or ''))} |",
        "",
        "## Files",
        "",
        "| label | status | bytes | sha256 |",
        "| --- | --- | ---: | --- |",
    ]
    for item in result["files"]:
        sha = str(item.get("actual_sha256") or item.get("expected_sha256") or "")
        lines.append(
            f"| {item['label']} | {item['status']} | {item.get('actual_bytes')} | {short_sha(sha)} |"
        )
    lines.extend(
        [
            "",
        ]
    )
    lines.extend([
        "## Issues",
        "",
        "| severity | code | message |",
        "| --- | --- | --- |",
    ])
    if result["issues"]:
        for issue in result["issues"]:
            lines.append(f"| {issue['severity']} | {issue['code']} | {issue['message']} |")
    else:
        lines.append("| info | none | All manifest fingerprints match current files. |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def short_sha(value: str) -> str:
    return value[:12] if value else ""


if __name__ == "__main__":
    raise SystemExit(main())
