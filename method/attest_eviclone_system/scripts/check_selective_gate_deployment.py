from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description="Check selective correction gate deployment readiness.")
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--policy-file", type=Path, default=None)
    parser.add_argument("--actual", type=Path, default=None)
    parser.add_argument("--baseline-predictions", type=Path, default=None)
    parser.add_argument("--output-predictions", type=Path, default=None)
    parser.add_argument("--rows-csv", type=Path, default=None)
    parser.add_argument("--override-csv", type=Path, default=None)
    parser.add_argument("--min-card-coverage", type=float, default=0.95)
    parser.add_argument("--max-damage", type=int, default=0)
    parser.add_argument("--require-actual", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--skip-content-check", action="store_true")
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    summary = load_json(args.summary)
    policy = load_json(args.policy_file) if args.policy_file else summary.get("policy")
    actual_count = count_triplet_rows(args.actual) if args.actual else None
    baseline_prediction_count = count_triplet_rows(args.baseline_predictions) if args.baseline_predictions else None
    output_prediction_count = count_triplet_rows(args.output_predictions) if args.output_predictions else None
    rows_csv_count = count_csv_rows(args.rows_csv) if args.rows_csv else None
    override_csv_count = count_csv_rows(args.override_csv) if args.override_csv else None
    triplet_healths = []
    if args.actual:
        triplet_healths.append(check_triplet_file_health(args.actual, "actual"))
    if args.baseline_predictions:
        triplet_healths.append(check_triplet_file_health(args.baseline_predictions, "baseline_predictions"))
    if args.output_predictions:
        triplet_healths.append(check_triplet_file_health(args.output_predictions, "output_predictions"))
    file_consistency = None
    if not args.skip_content_check and args.baseline_predictions and args.output_predictions and args.rows_csv:
        file_consistency = verify_prediction_audit_consistency(
            args.baseline_predictions,
            args.output_predictions,
            args.rows_csv,
            args.override_csv,
        )
    actual_consistency = None
    if not args.skip_content_check and args.actual and args.baseline_predictions and args.output_predictions:
        actual_consistency = verify_actual_metric_consistency(
            summary,
            args.actual,
            args.baseline_predictions,
            args.output_predictions,
            args.rows_csv,
        )
    result = assess_readiness(
        summary,
        policy=policy,
        actual_count=actual_count,
        baseline_prediction_count=baseline_prediction_count,
        output_prediction_count=output_prediction_count,
        rows_csv_count=rows_csv_count,
        override_csv_count=override_csv_count,
        file_consistency=file_consistency,
        actual_consistency=actual_consistency,
        triplet_healths=triplet_healths,
        min_card_coverage=args.min_card_coverage,
        max_damage=args.max_damage,
        require_actual=args.require_actual,
        content_check_skipped=args.skip_content_check,
    )
    result["inputs"] = {
        "summary": str(args.summary.resolve()),
        "policy_file": str(args.policy_file.resolve()) if args.policy_file else summary.get("policy_file"),
        "actual": str(args.actual.resolve()) if args.actual else None,
        "baseline_predictions": str(args.baseline_predictions.resolve()) if args.baseline_predictions else None,
        "output_predictions": str(args.output_predictions.resolve()) if args.output_predictions else None,
        "rows_csv": str(args.rows_csv.resolve()) if args.rows_csv else None,
        "override_csv": str(args.override_csv.resolve()) if args.override_csv else None,
        "min_card_coverage": args.min_card_coverage,
        "max_damage": args.max_damage,
        "require_actual": args.require_actual,
        "content_check": file_consistency is not None,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    if args.report:
        write_report(args.report, result)
    print(json.dumps({"status": result["status"], "issue_counts": result["issue_counts"]}, ensure_ascii=False))
    if args.strict_exit and result["status"] != "ready":
        return 2
    return 0


def load_json(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def count_csv_rows(path: Path | None) -> int | None:
    if path is None:
        return None
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def count_triplet_rows(path: Path | None) -> int | None:
    if path is None:
        return None
    count = 0
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) < 3:
                raise ValueError(f"expected at least 3 columns at {path}:{line_no}, got {len(parts)}")
            count += 1
    return count


def check_triplet_file_health(path: Path, role: str, *, sample_limit: int = 10) -> dict[str, Any]:
    rows = read_triplet_rows(path)
    pair_counts: dict[tuple[str, str], int] = {}
    for a, b, _label in rows:
        key = (a, b)
        pair_counts[key] = pair_counts.get(key, 0) + 1
    duplicate_pairs = sorted(key for key, count in pair_counts.items() if count > 1)
    issues: list[dict[str, str]] = []
    if duplicate_pairs:
        add_issue(
            issues,
            "error",
            f"{role}_duplicate_pairs",
            f"{role} has {len(duplicate_pairs)} duplicate function-id pairs.",
        )
    return {
        "issues": issues,
        "checks": {
            f"{role}_rows": len(rows),
            f"{role}_unique_pairs": len(pair_counts),
            f"{role}_duplicate_pairs": len(duplicate_pairs),
            f"{role}_sample_duplicate_pairs": sample_pairs(duplicate_pairs, sample_limit),
        },
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
            rows.append((parts[0], parts[1], int(parts[2])))
    return rows


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def verify_prediction_audit_consistency(
    baseline_predictions: Path,
    output_predictions: Path,
    rows_csv: Path,
    override_csv: Path | None = None,
) -> dict[str, Any]:
    baseline_rows = read_triplet_rows(baseline_predictions)
    output_rows = read_triplet_rows(output_predictions)
    audit_rows = read_csv_rows(rows_csv)
    override_rows = read_csv_rows(override_csv) if override_csv else None
    issues: list[dict[str, str]] = []
    prediction_changes = 0
    audit_override_rows = 0
    unexplained_prediction_changes = 0
    missing_prediction_changes = 0
    row_content_mismatches = 0
    checked_rows = min(len(baseline_rows), len(output_rows), len(audit_rows))

    if len(baseline_rows) != len(output_rows):
        add_issue(
            issues,
            "error",
            "baseline_output_row_count_mismatch",
            f"Baseline predictions have {len(baseline_rows)} rows; output predictions have {len(output_rows)} rows.",
        )
    if len(audit_rows) != len(baseline_rows):
        add_issue(
            issues,
            "error",
            "audit_prediction_row_count_mismatch",
            f"Rows CSV has {len(audit_rows)} rows; baseline predictions have {len(baseline_rows)} rows.",
        )

    override_pairs: set[tuple[str, str]] = set()
    for idx in range(checked_rows):
        base_a, base_b, base_pred = baseline_rows[idx]
        out_a, out_b, out_pred = output_rows[idx]
        audit = audit_rows[idx]
        audit_key = (str(audit.get("function_id_a") or ""), str(audit.get("function_id_b") or ""))
        pair_key = (base_a, base_b)
        changed = base_pred != out_pred
        override = parse_bool(audit.get("override"))
        if changed:
            prediction_changes += 1
        if override:
            audit_override_rows += 1
            override_pairs.add(audit_key)

        if (out_a, out_b) != pair_key or audit_key != pair_key:
            row_content_mismatches += 1
            continue
        if int_or_none(audit.get("baseline_pred")) != base_pred or int_or_none(audit.get("final_pred")) != out_pred:
            row_content_mismatches += 1
            continue
        if changed and not override:
            unexplained_prediction_changes += 1
        if override and not changed:
            missing_prediction_changes += 1

    if row_content_mismatches:
        add_issue(
            issues,
            "error",
            "prediction_audit_content_mismatch",
            f"{row_content_mismatches} rows disagree between prediction files and rows CSV.",
        )
    if unexplained_prediction_changes:
        add_issue(
            issues,
            "error",
            "unexplained_prediction_changes",
            f"{unexplained_prediction_changes} output prediction changes are not marked as override=true.",
        )
    if missing_prediction_changes:
        add_issue(
            issues,
            "error",
            "override_without_prediction_change",
            f"{missing_prediction_changes} override=true rows did not change the final prediction.",
        )

    override_csv_rows = None
    override_csv_missing_from_rows = None
    override_csv_extra_from_rows = None
    if override_rows is not None:
        override_csv_pairs = {(str(row.get("function_id_a") or ""), str(row.get("function_id_b") or "")) for row in override_rows}
        override_csv_rows = len(override_rows)
        override_csv_missing_from_rows = len(override_pairs - override_csv_pairs)
        override_csv_extra_from_rows = len(override_csv_pairs - override_pairs)
        if override_csv_missing_from_rows or override_csv_extra_from_rows:
            add_issue(
                issues,
                "error",
                "override_csv_subset_mismatch",
                "Override CSV does not match rows CSV override=true pairs.",
            )

    return {
        "issues": issues,
        "checks": {
            "content_check_rows": checked_rows,
            "prediction_changes": prediction_changes,
            "audit_override_rows": audit_override_rows,
            "unexplained_prediction_changes": unexplained_prediction_changes,
            "missing_prediction_changes": missing_prediction_changes,
            "row_content_mismatches": row_content_mismatches,
            "override_csv_subset_missing": override_csv_missing_from_rows,
            "override_csv_subset_extra": override_csv_extra_from_rows,
            "override_csv_content_rows": override_csv_rows,
        },
    }


def verify_actual_metric_consistency(
    summary: dict[str, Any],
    actual_labels: Path,
    baseline_predictions: Path,
    output_predictions: Path,
    rows_csv: Path | None = None,
) -> dict[str, Any]:
    actual_rows = read_triplet_rows(actual_labels)
    baseline_rows = read_triplet_rows(baseline_predictions)
    output_rows = read_triplet_rows(output_predictions)
    audit_rows = read_csv_rows(rows_csv) if rows_csv else None
    issues: list[dict[str, str]] = []
    checked_rows = min(len(actual_rows), len(baseline_rows), len(output_rows))
    if audit_rows is not None:
        checked_rows = min(checked_rows, len(audit_rows))

    if len(actual_rows) != len(baseline_rows):
        add_issue(
            issues,
            "error",
            "actual_baseline_row_count_mismatch",
            f"Actual labels have {len(actual_rows)} rows; baseline predictions have {len(baseline_rows)} rows.",
        )
    if len(actual_rows) != len(output_rows):
        add_issue(
            issues,
            "error",
            "actual_output_row_count_mismatch",
            f"Actual labels have {len(actual_rows)} rows; output predictions have {len(output_rows)} rows.",
        )

    baseline_confusion = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    final_confusion = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
    corrections = 0
    damage = 0
    actual_pair_mismatches = 0
    audit_actual_mismatches = 0

    for idx in range(checked_rows):
        actual_a, actual_b, gold = actual_rows[idx]
        base_a, base_b, base_pred = baseline_rows[idx]
        out_a, out_b, final_pred = output_rows[idx]
        key = (actual_a, actual_b)
        if (base_a, base_b) != key or (out_a, out_b) != key:
            actual_pair_mismatches += 1
            continue

        baseline_confusion[confusion_key(gold, base_pred)] += 1
        final_confusion[confusion_key(gold, final_pred)] += 1
        baseline_correct = base_pred == gold
        final_correct = final_pred == gold
        if not baseline_correct and final_correct:
            corrections += 1
        if baseline_correct and not final_correct:
            damage += 1

        if audit_rows is not None:
            audit = audit_rows[idx]
            audit_key = (str(audit.get("function_id_a") or ""), str(audit.get("function_id_b") or ""))
            if (
                audit_key != key
                or int_or_none(audit.get("gold")) != gold
                or parse_bool(audit.get("baseline_correct")) != baseline_correct
                or parse_bool(audit.get("final_correct")) != final_correct
            ):
                audit_actual_mismatches += 1

    if actual_pair_mismatches:
        add_issue(
            issues,
            "error",
            "actual_prediction_pair_mismatch",
            f"{actual_pair_mismatches} rows disagree between actual labels and prediction files.",
        )
    if audit_actual_mismatches:
        add_issue(
            issues,
            "error",
            "actual_audit_content_mismatch",
            f"{audit_actual_mismatches} rows disagree between actual labels and rows CSV correctness fields.",
        )

    baseline_metrics = metrics_from_confusion(baseline_confusion)
    final_metrics = metrics_from_confusion(final_confusion)
    net_gain = corrections - damage
    compare_summary_value(issues, summary, "actual_available", len(actual_rows), "summary_actual_available_mismatch")
    compare_summary_value(issues, summary, "corrections", corrections, "summary_corrections_mismatch")
    compare_summary_value(issues, summary, "damage", damage, "summary_damage_mismatch")
    compare_summary_value(issues, summary, "net_gain", net_gain, "summary_net_gain_mismatch")
    compare_summary_metrics(issues, summary, "baseline_metrics", baseline_metrics)
    compare_summary_metrics(issues, summary, "final_metrics", final_metrics)

    return {
        "issues": issues,
        "checks": {
            "actual_label_rows": len(actual_rows),
            "actual_metric_check_rows": checked_rows,
            "actual_pair_mismatches": actual_pair_mismatches,
            "actual_audit_mismatches": audit_actual_mismatches,
            "recomputed_corrections": corrections,
            "recomputed_damage": damage,
            "recomputed_net_gain": net_gain,
            "recomputed_baseline_f1": baseline_metrics["f1"],
            "recomputed_final_f1": final_metrics["f1"],
        },
    }


def assess_readiness(
    summary: dict[str, Any],
    *,
    policy: dict[str, Any] | None,
    actual_count: int | None = None,
    baseline_prediction_count: int | None = None,
    output_prediction_count: int | None = None,
    rows_csv_count: int | None = None,
    override_csv_count: int | None = None,
    file_consistency: dict[str, Any] | None = None,
    actual_consistency: dict[str, Any] | None = None,
    triplet_healths: list[dict[str, Any]] | None = None,
    min_card_coverage: float = 0.95,
    max_damage: int = 0,
    require_actual: bool = False,
    content_check_skipped: bool = False,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    total = int(summary.get("total_predictions") or 0)
    matched = int(summary.get("matched_cards") or 0)
    missing = int(summary.get("missing_cards") or 0)
    override_count = int(summary.get("override_count") or 0)
    coverage = ratio(matched, total)

    if total <= 0:
        add_issue(issues, "error", "empty_predictions", "No baseline predictions were checked.")
    if matched + missing != total and total > 0:
        add_issue(
            issues,
            "warning",
            "card_accounting_mismatch",
            f"matched_cards + missing_cards = {matched + missing}, but total_predictions = {total}.",
        )
    if coverage < min_card_coverage:
        add_issue(
            issues,
            "warning",
            "incomplete_card_coverage",
            f"Card coverage is {coverage:.6f}, below the deployment threshold {min_card_coverage:.6f}.",
        )
    if baseline_prediction_count is not None and baseline_prediction_count != total:
        add_issue(
            issues,
            "error",
            "baseline_prediction_count_mismatch",
            f"Baseline prediction file has {baseline_prediction_count} rows, but summary total_predictions is {total}.",
        )
    if output_prediction_count is not None and output_prediction_count != total:
        add_issue(
            issues,
            "error",
            "output_prediction_count_mismatch",
            f"Output prediction file has {output_prediction_count} rows, but summary total_predictions is {total}.",
        )
    if rows_csv_count is not None and rows_csv_count != total:
        add_issue(
            issues,
            "error",
            "rows_audit_count_mismatch",
            f"Rows CSV has {rows_csv_count} rows, but summary total_predictions is {total}.",
        )
    if actual_count is not None and actual_count != total:
        add_issue(
            issues,
            "error",
            "actual_label_count_mismatch",
            f"Actual label file has {actual_count} rows, but summary total_predictions is {total}.",
        )
    if content_check_skipped:
        add_issue(
            issues,
            "warning",
            "content_check_skipped",
            "Prediction audit and actual metric content consistency checks were skipped; this result is diagnostic-only.",
        )

    threshold = summary.get("threshold")
    if threshold is None:
        add_issue(issues, "error", "missing_threshold", "The applied gate threshold is missing.")
    if policy is None:
        add_issue(issues, "warning", "missing_policy", "No policy file or embedded policy was available.")
    else:
        policy_threshold = policy.get("threshold")
        if policy.get("schema_version") != "eviclone-selective-gate-policy/v1":
            add_issue(issues, "error", "unsupported_policy_schema", "The policy schema is not supported.")
        if policy.get("gate_type") != "heuristic_override_score":
            add_issue(issues, "error", "unsupported_gate_type", "The policy gate type is not supported.")
        if threshold is not None and policy_threshold is not None and abs(float(threshold) - float(policy_threshold)) > 1e-9:
            add_issue(
                issues,
                "error",
                "threshold_policy_mismatch",
                f"Applied threshold {threshold} does not match policy threshold {policy_threshold}.",
            )
        evidence = policy.get("selected_threshold_evidence") or {}
        if int(evidence.get("guard_harm") or 0) > 0:
            add_issue(issues, "warning", "policy_guard_harm", "The selected policy has non-zero sampled guard harm.")

    if override_csv_count is None and override_count:
        add_issue(issues, "warning", "missing_override_audit", "Overrides occurred but no override CSV was checked.")
    if override_csv_count is not None and override_csv_count != override_count:
        add_issue(
            issues,
            "error",
            "override_audit_mismatch",
            f"Override CSV has {override_csv_count} rows, but summary override_count is {override_count}.",
        )

    actual_available = int(summary.get("actual_available") or 0)
    if require_actual and actual_available != total:
        add_issue(issues, "error", "actual_labels_missing", "Post-hoc actual labels are required but incomplete.")
    elif actual_available != total:
        add_issue(issues, "warning", "actual_labels_not_full", "Post-hoc actual labels are unavailable or incomplete.")

    if actual_available:
        damage = int(summary.get("damage") or 0)
        net_gain = int(summary.get("net_gain") or 0)
        baseline_f1 = metric_value(summary, "baseline_metrics", "f1")
        final_f1 = metric_value(summary, "final_metrics", "f1")
        if damage > max_damage:
            add_issue(issues, "error", "damage_budget_exceeded", f"Damage {damage} exceeds budget {max_damage}.")
        if net_gain < 0:
            add_issue(issues, "error", "negative_net_gain", f"Net gain is negative: {net_gain}.")
        if baseline_f1 is not None and final_f1 is not None and final_f1 < baseline_f1:
            add_issue(
                issues,
                "error",
                "f1_regression",
                f"Final F1 {final_f1} is lower than baseline F1 {baseline_f1}.",
            )

    extra_checks: dict[str, Any] = {}
    if file_consistency is not None:
        issues.extend(file_consistency.get("issues") or [])
        extra_checks.update(file_consistency.get("checks") or {})
    if actual_consistency is not None:
        issues.extend(actual_consistency.get("issues") or [])
        extra_checks.update(actual_consistency.get("checks") or {})
    for health in triplet_healths or []:
        issues.extend(health.get("issues") or [])
        extra_checks.update(health.get("checks") or {})

    issue_counts = {
        "error": sum(1 for item in issues if item["severity"] == "error"),
        "warning": sum(1 for item in issues if item["severity"] == "warning"),
    }
    status = "ready"
    if issue_counts["error"]:
        status = "fail"
    elif any(item["code"] in {"incomplete_card_coverage", "content_check_skipped"} for item in issues):
        status = "diagnostic_only"
    elif issue_counts["warning"]:
        status = "warn"

    return {
        "status": status,
        "issue_counts": issue_counts,
        "issues": issues,
        "checks": {
            "total_predictions": total,
            "card_count": int(summary.get("card_count") or 0),
            "matched_cards": matched,
            "missing_cards": missing,
            "duplicate_cards": int(summary.get("duplicate_cards") or 0),
            "duplicate_cards_ignored_unusable": int(summary.get("duplicate_cards_ignored_unusable") or 0),
            "card_selection_rule": summary.get("card_selection_rule"),
            "card_coverage": round(coverage, 6),
            "baseline_prediction_rows": baseline_prediction_count,
            "output_prediction_rows": output_prediction_count,
            "rows_csv_rows": rows_csv_count,
            "override_count": override_count,
            "override_csv_rows": override_csv_count,
            "actual_label_rows": actual_count,
            "content_check_skipped": content_check_skipped,
            "actual_available": actual_available,
            "threshold": threshold,
            "damage": summary.get("damage"),
            "net_gain": summary.get("net_gain"),
            "baseline_f1": metric_value(summary, "baseline_metrics", "f1"),
            "final_f1": metric_value(summary, "final_metrics", "f1"),
            **extra_checks,
        },
        "recommendation": recommendation(status),
    }


def metric_value(summary: dict[str, Any], section: str, key: str) -> float | None:
    metrics = summary.get(section)
    if not isinstance(metrics, dict) or key not in metrics:
        return None
    return float(metrics[key])


def confusion_key(gold: int, pred: int) -> str:
    if gold == 1 and pred == 1:
        return "tp"
    if gold == 0 and pred == 0:
        return "tn"
    if gold == 0 and pred == 1:
        return "fp"
    return "fn"


def metrics_from_confusion(confusion: dict[str, int]) -> dict[str, float | int]:
    tp = int(confusion.get("tp", 0))
    tn = int(confusion.get("tn", 0))
    fp = int(confusion.get("fp", 0))
    fn = int(confusion.get("fn", 0))
    total = tp + tn + fp + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": round((tp + tn) / total, 6) if total else 0.0,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round((2 * precision * recall / (precision + recall)), 6) if precision + recall else 0.0,
    }


def compare_summary_value(
    issues: list[dict[str, str]],
    summary: dict[str, Any],
    key: str,
    expected: int,
    code: str,
) -> None:
    if key not in summary:
        add_issue(issues, "error", code, f"Summary is missing {key}; recomputed value is {expected}.")
        return
    actual = int(summary.get(key) or 0)
    if actual != expected:
        add_issue(issues, "error", code, f"Summary {key}={actual}, but recomputed value is {expected}.")


def compare_summary_metrics(
    issues: list[dict[str, str]],
    summary: dict[str, Any],
    section: str,
    expected: dict[str, float | int],
) -> None:
    actual = summary.get(section)
    if not isinstance(actual, dict):
        add_issue(issues, "error", f"summary_{section}_missing", f"Summary is missing {section}.")
        return
    for key, expected_value in expected.items():
        if key not in actual:
            add_issue(issues, "error", f"summary_{section}_{key}_missing", f"Summary is missing {section}.{key}.")
            continue
        actual_value = float(actual[key])
        if abs(actual_value - float(expected_value)) > 1e-6:
            add_issue(
                issues,
                "error",
                f"summary_{section}_{key}_mismatch",
                f"Summary {section}.{key}={actual_value}, but recomputed value is {expected_value}.",
            )


def add_issue(issues: list[dict[str, str]], severity: str, code: str, message: str) -> None:
    issues.append({"severity": severity, "code": code, "message": message})


def sample_pairs(pairs: list[tuple[str, str]], limit: int) -> list[dict[str, str]]:
    return [{"function_id_a": a, "function_id_b": b} for a, b in pairs[:limit]]


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "1", "yes"}


def int_or_none(value: Any) -> int | None:
    try:
        text = str(value or "").strip()
        return int(text) if text else None
    except ValueError:
        return None


def recommendation(status: str) -> str:
    if status == "ready":
        return "Ready for policy-controlled deployment on the checked prediction/card set."
    if status == "diagnostic_only":
        return "Use as a diagnostic artifact only; generate EviClone cards for the full target prediction set before deployment."
    if status == "warn":
        return "Usable only after manually reviewing warnings and documenting the accepted risk."
    return "Do not deploy; fix error-level readiness issues first."


def ratio(num: int | float, den: int | float) -> float:
    return float(num) / float(den) if den else 0.0


def write_report(path: Path, result: dict[str, Any]) -> None:
    checks = result["checks"]
    lines = [
        "# Selective Gate Deployment Readiness",
        "",
        f"Status: `{result['status']}`",
        "",
        result["recommendation"],
        "",
        "## Checks",
        "",
        "| check | value |",
        "| --- | ---: |",
    ]
    for key in [
        "total_predictions",
        "card_count",
        "matched_cards",
        "missing_cards",
        "duplicate_cards",
        "duplicate_cards_ignored_unusable",
        "card_selection_rule",
        "card_coverage",
        "baseline_prediction_rows",
        "output_prediction_rows",
        "rows_csv_rows",
        "content_check_rows",
        "prediction_changes",
        "audit_override_rows",
        "unexplained_prediction_changes",
        "missing_prediction_changes",
        "row_content_mismatches",
        "override_csv_subset_missing",
        "override_csv_subset_extra",
        "override_csv_content_rows",
        "override_count",
        "override_csv_rows",
        "actual_label_rows",
        "content_check_skipped",
        "actual_rows",
        "actual_unique_pairs",
        "actual_duplicate_pairs",
        "actual_available",
        "baseline_predictions_rows",
        "baseline_predictions_unique_pairs",
        "baseline_predictions_duplicate_pairs",
        "output_predictions_rows",
        "output_predictions_unique_pairs",
        "output_predictions_duplicate_pairs",
        "actual_metric_check_rows",
        "actual_pair_mismatches",
        "actual_audit_mismatches",
        "recomputed_corrections",
        "recomputed_damage",
        "recomputed_net_gain",
        "recomputed_baseline_f1",
        "recomputed_final_f1",
        "threshold",
        "damage",
        "net_gain",
        "baseline_f1",
        "final_f1",
    ]:
        lines.append(f"| {key} | {checks.get(key)} |")
    lines.extend(["", "## Issues", "", "| severity | code | message |", "| --- | --- | --- |"])
    if result["issues"]:
        for issue in result["issues"]:
            lines.append(f"| {issue['severity']} | {issue['code']} | {issue['message']} |")
    else:
        lines.append("| info | none | No readiness issues detected. |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
