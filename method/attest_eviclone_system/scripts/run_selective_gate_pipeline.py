from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.selective_gate import load_cards, read_triplet_file
from scripts.apply_selective_correction_gate import (
    apply_gate_to_predictions,
    load_policy,
    override_rows,
    resolve_threshold,
    write_csv,
)
from scripts.check_selective_gate_deployment import (
    assess_readiness,
    check_triplet_file_health,
    count_csv_rows,
    count_triplet_rows,
    verify_actual_metric_consistency,
    verify_prediction_audit_consistency,
    write_report as write_readiness_report,
)
from scripts.verify_selective_gate_manifest import (
    attach_manifest_certificate,
    verify_manifest,
    write_report as write_manifest_verification_report,
)


@dataclass(frozen=True)
class PipelinePaths:
    output_predictions: Path
    summary: Path
    rows_csv: Path
    override_csv: Path
    readiness_json: Path
    readiness_report: Path
    manifest: Path
    manifest_verification_json: Path
    manifest_verification_report: Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run selective gate application plus deployment readiness checks.")
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--cards", type=Path, action="append", required=True)
    parser.add_argument("--policy-file", type=Path, default=None)
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--actual", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--name", default="selective_gate")
    parser.add_argument("--min-card-coverage", type=float, default=0.95)
    parser.add_argument("--max-damage", type=int, default=0)
    parser.add_argument("--require-actual", action="store_true")
    parser.add_argument("--skip-content-check", action="store_true")
    parser.add_argument("--strict-exit", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(
        predictions=args.predictions,
        card_paths=args.cards,
        policy_file=args.policy_file,
        threshold=args.threshold,
        actual=args.actual,
        output_dir=args.output_dir,
        name=args.name,
        min_card_coverage=args.min_card_coverage,
        max_damage=args.max_damage,
        require_actual=args.require_actual,
        skip_content_check=args.skip_content_check,
    )
    print(
        json.dumps(
            {
                "manifest": str(result["paths"].manifest.resolve()),
                "status": result["readiness"]["status"],
                "manifest_verification": result["manifest_verification"]["status"],
            },
            ensure_ascii=False,
        )
    )
    if args.strict_exit and (
        result["readiness"]["status"] != "ready" or result["manifest_verification"]["status"] != "verified"
    ):
        return 2
    return 0


def run_pipeline(
    *,
    predictions: Path,
    card_paths: list[Path],
    policy_file: Path | None,
    threshold: float | None,
    actual: Path | None,
    output_dir: Path,
    name: str,
    min_card_coverage: float = 0.95,
    max_damage: int = 0,
    require_actual: bool = False,
    skip_content_check: bool = False,
) -> dict[str, Any]:
    paths = pipeline_paths(output_dir, name)
    policy = load_policy(policy_file) if policy_file else None
    applied_threshold = resolve_threshold(threshold, policy)
    prediction_rows = read_triplet_file(predictions)
    cards = []
    for path in card_paths:
        cards.extend(load_cards(path))
    actual_rows = read_triplet_file(actual) if actual else None
    gate_result = apply_gate_to_predictions(
        prediction_rows,
        cards,
        threshold=applied_threshold,
        actual_rows=actual_rows,
    )

    write_predictions(paths.output_predictions, gate_result["prediction_rows"])
    write_csv(paths.rows_csv, gate_result["rows"])
    write_csv(paths.override_csv, override_rows(gate_result["rows"]))
    summary = build_summary(
        predictions=predictions,
        card_paths=card_paths,
        policy_file=policy_file,
        policy=policy,
        threshold=applied_threshold,
        actual=actual,
        paths=paths,
        gate_summary=gate_result["summary"],
    )
    write_json(paths.summary, summary)

    file_consistency = None
    if not skip_content_check:
        file_consistency = verify_prediction_audit_consistency(
            predictions,
            paths.output_predictions,
            paths.rows_csv,
            paths.override_csv,
        )
    actual_consistency = None
    if not skip_content_check and actual is not None:
        actual_consistency = verify_actual_metric_consistency(
            summary,
            actual,
            predictions,
            paths.output_predictions,
            paths.rows_csv,
        )
    triplet_healths = [check_triplet_file_health(predictions, "baseline_predictions")]
    if actual is not None:
        triplet_healths.append(check_triplet_file_health(actual, "actual"))
    triplet_healths.append(check_triplet_file_health(paths.output_predictions, "output_predictions"))
    readiness = assess_readiness(
        summary,
        policy=policy,
        actual_count=count_triplet_rows(actual) if actual else None,
        baseline_prediction_count=count_triplet_rows(predictions),
        output_prediction_count=count_triplet_rows(paths.output_predictions),
        rows_csv_count=count_csv_rows(paths.rows_csv),
        override_csv_count=count_csv_rows(paths.override_csv),
        file_consistency=file_consistency,
        actual_consistency=actual_consistency,
        triplet_healths=triplet_healths,
        min_card_coverage=min_card_coverage,
        max_damage=max_damage,
        require_actual=require_actual,
        content_check_skipped=skip_content_check,
    )
    readiness["inputs"] = {
        "summary": str(paths.summary.resolve()),
        "policy_file": str(policy_file.resolve()) if policy_file else None,
        "actual": str(actual.resolve()) if actual else None,
        "baseline_predictions": str(predictions.resolve()),
        "output_predictions": str(paths.output_predictions.resolve()),
        "rows_csv": str(paths.rows_csv.resolve()),
        "override_csv": str(paths.override_csv.resolve()),
        "min_card_coverage": min_card_coverage,
        "max_damage": max_damage,
        "require_actual": require_actual,
        "content_check": file_consistency is not None,
    }
    write_json(paths.readiness_json, readiness)
    write_readiness_report(paths.readiness_report, readiness)

    manifest = attach_manifest_certificate({
        "schema_version": "eviclone-selective-gate-pipeline-manifest/v1",
        "pipeline": "selective_gate_apply_and_readiness/v1",
        "name": name,
        "threshold": applied_threshold,
        "parameters": {
            "requested_threshold": threshold,
            "min_card_coverage": min_card_coverage,
            "max_damage": max_damage,
            "require_actual": require_actual,
            "skip_content_check": skip_content_check,
        },
        "status": readiness["status"],
        "issue_counts": readiness["issue_counts"],
        "summary_checks": deployment_summary_checks(summary),
        "readiness_checks": readiness.get("checks", {}),
        "inputs": {
            "predictions": file_fingerprint(predictions),
            "cards": [file_fingerprint(path) for path in card_paths],
            "policy_file": file_fingerprint(policy_file),
            "actual": file_fingerprint(actual),
        },
        "outputs": {
            "output_predictions": file_fingerprint(paths.output_predictions),
            "summary": file_fingerprint(paths.summary),
            "rows_csv": file_fingerprint(paths.rows_csv),
            "override_csv": file_fingerprint(paths.override_csv),
            "readiness_json": file_fingerprint(paths.readiness_json),
            "readiness_report": file_fingerprint(paths.readiness_report),
        },
        "paths": {key: str(value.resolve()) for key, value in paths.__dict__.items()},
    })
    write_json(paths.manifest, manifest)
    manifest_verification = verify_manifest(paths.manifest, base_dir=REPO_ROOT)
    write_json(paths.manifest_verification_json, manifest_verification)
    write_manifest_verification_report(paths.manifest_verification_report, manifest_verification)
    return {
        "paths": paths,
        "summary": summary,
        "readiness": readiness,
        "manifest": manifest,
        "manifest_verification": manifest_verification,
    }


def deployment_summary_checks(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "total_predictions": summary.get("total_predictions"),
        "card_count": summary.get("card_count"),
        "matched_cards": summary.get("matched_cards"),
        "missing_cards": summary.get("missing_cards"),
        "duplicate_cards": summary.get("duplicate_cards"),
        "duplicate_cards_ignored_unusable": summary.get("duplicate_cards_ignored_unusable"),
        "card_selection_rule": summary.get("card_selection_rule"),
        "override_count": summary.get("override_count"),
        "corrections": summary.get("corrections"),
        "damage": summary.get("damage"),
        "net_gain": summary.get("net_gain"),
    }


def pipeline_paths(output_dir: Path, name: str) -> PipelinePaths:
    safe_name = name.strip() or "selective_gate"
    return PipelinePaths(
        output_predictions=output_dir / f"{safe_name}.predictions.txt",
        summary=output_dir / f"{safe_name}.summary.json",
        rows_csv=output_dir / f"{safe_name}.rows.csv",
        override_csv=output_dir / f"{safe_name}.overrides.csv",
        readiness_json=output_dir / f"{safe_name}.readiness.json",
        readiness_report=output_dir / f"{safe_name}.readiness.md",
        manifest=output_dir / f"{safe_name}.manifest.json",
        manifest_verification_json=output_dir / f"{safe_name}.manifest_verification.json",
        manifest_verification_report=output_dir / f"{safe_name}.manifest_verification.md",
    )


def write_predictions(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(f"{row['function_id_a']}\t{row['function_id_b']}\t{row['final_pred']}\n")


def build_summary(
    *,
    predictions: Path,
    card_paths: list[Path],
    policy_file: Path | None,
    policy: dict[str, Any] | None,
    threshold: float,
    actual: Path | None,
    paths: PipelinePaths,
    gate_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "predictions": str(predictions.resolve()),
        "cards": [str(path.resolve()) for path in card_paths],
        "threshold": threshold,
        "policy_file": str(policy_file.resolve()) if policy_file else None,
        "policy": policy,
        "actual": str(actual.resolve()) if actual else None,
        "output_predictions": str(paths.output_predictions.resolve()),
        "output_csv": str(paths.rows_csv.resolve()),
        "output_override_csv": str(paths.override_csv.resolve()),
        **gate_summary,
    }


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def file_fingerprint(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    resolved = path.resolve()
    h = hashlib.sha256()
    size = 0
    with resolved.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            size += len(chunk)
            h.update(chunk)
    return {
        "path": str(resolved),
        "relative_path": relative_path(resolved),
        "bytes": size,
        "sha256": h.hexdigest(),
    }


def relative_path(path: Path) -> str | None:
    try:
        return str(path.relative_to(REPO_ROOT.resolve()).as_posix())
    except ValueError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
