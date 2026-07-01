from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch_geometric.loader import DataLoader


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from evaluate_triplet_predictions import evaluate as evaluate_triplets  # noqa: E402
from run_holmes_artifact import (  # noqa: E402
    LegacyHolmesDataset,
    choose_device,
    choose_threshold,
    metric_dict,
    predict,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a saved HOLMES checkpoint on a processed test directory.")
    parser.add_argument("--model-dir", type=Path, default=Path("external/HOLMES_drive/Model"))
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--processed-dir", type=Path, required=True)
    parser.add_argument("--raw-test", type=Path, required=True)
    parser.add_argument("--variant", choices=["EA", "EU"], default="EA")
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--threshold-grid-step", type=float, default=0.01)
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset", default="BCB-LLM-Refined-HardCases")
    parser.add_argument("--method", default="HOLMES")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(args.model_dir.resolve()))
    model_module = importlib.import_module(f"holmes{args.variant}")
    device = choose_device(args.device)
    model = model_module.BCE(100).to(device)
    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    state_dict = checkpoint["state_dict"] if isinstance(checkpoint, dict) and "state_dict" in checkpoint else checkpoint
    model.load_state_dict(state_dict)

    dataset = LegacyHolmesDataset(args.processed_dir)
    loader = DataLoader(dataset, batch_size=args.batch_size, follow_batch=["x1", "x2"], num_workers=0, shuffle=False)
    scores = predict(model, loader, device=device, variant=args.variant)
    if args.threshold is None:
        threshold_record = choose_threshold(scores["gold"], scores["score"], step=args.threshold_grid_step)
        threshold = float(threshold_record["threshold"])
        threshold_policy = "selected_on_same_test_scores_for_diagnostic_upper_bound"
    else:
        threshold = float(args.threshold)
        threshold_record = {"threshold": threshold, "best_f1": None, "candidates": []}
        threshold_policy = "fixed_user_supplied_or_prior_threshold"

    predictions = (np.asarray(scores["score"]) > threshold).astype(int)
    metrics = metric_dict(scores["gold"], predictions)
    raw_pairs = read_triplets(args.raw_test)
    if len(raw_pairs) != len(predictions):
        raise ValueError(f"raw-test rows do not match predictions: {len(raw_pairs)} != {len(predictions)}")

    predictions_jsonl = args.output_dir / "holmes_predictions.jsonl"
    predictions_triplet = args.output_dir / "holmes_predictions.txt"
    with (
        predictions_jsonl.open("w", encoding="utf-8", newline="\n") as jsonl_sink,
        predictions_triplet.open("w", encoding="utf-8", newline="\n") as triplet_sink,
    ):
        for index, ((idx1, idx2, gold), score, pred) in enumerate(zip(raw_pairs, scores["score"], predictions), start=1):
            triplet_sink.write(f"{idx1}\t{idx2}\t{int(pred)}\t{float(score):.8f}\n")
            jsonl_sink.write(
                json.dumps(
                    {
                        "row": index,
                        "function_id_a": idx1,
                        "function_id_b": idx2,
                        "gold": gold,
                        "score": float(score),
                        "prediction": int(pred),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    triplet_eval = evaluate_triplets(
        gold_path=args.raw_test,
        prediction_path=predictions_triplet,
        dataset=args.dataset,
        method=args.method,
        source=str(args.checkpoint),
    )
    summary: dict[str, Any] = {
        "schema_version": "eviclone-holmes-checkpoint-test-eval/v1",
        "dataset": args.dataset,
        "method": args.method,
        "variant": args.variant,
        "model_dir": str(args.model_dir),
        "checkpoint": str(args.checkpoint),
        "processed_dir": str(args.processed_dir),
        "raw_test": str(args.raw_test),
        "device": str(device),
        "rows": len(raw_pairs),
        "threshold": threshold_record,
        "threshold_policy": threshold_policy,
        "test_metrics": metrics,
        "triplet_evaluation": triplet_eval,
        "artifacts": {
            "predictions_jsonl": str(predictions_jsonl),
            "predictions_triplet": str(predictions_triplet),
            "summary_json": str(args.output_dir / "holmes_metrics.json"),
        },
        "claim_boundary": (
            "Saved HOLMES BCB checkpoint evaluated on a lightweight source-graph adapter for the hard-case test set. "
            "The test graphs are HOLMES-compatible but are not the original HOLMES PDG extraction pipeline."
        ),
    }
    metrics_path = args.output_dir / "holmes_metrics.json"
    report_path = args.output_dir / "holmes_metrics.md"
    metrics_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(render_report(summary), encoding="utf-8")
    print(json.dumps({"metrics": str(metrics_path), "rows": len(raw_pairs), "test_metrics": metrics}, ensure_ascii=False))
    return 0


def read_triplets(path: Path) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            parts = text.replace(",", " ").split()
            if len(parts) < 3:
                raise ValueError(f"expected triplet at {path}:{line_no}")
            rows.append((parts[0], parts[1], int(parts[2])))
    return rows


def render_report(summary: dict[str, Any]) -> str:
    metrics = summary["test_metrics"]
    return "\n".join(
        [
            f"# {summary['method']} on {summary['dataset']}",
            "",
            f"Rows: {summary['rows']}",
            f"Checkpoint: `{summary['checkpoint']}`",
            f"Threshold: `{summary['threshold']['threshold']}` ({summary['threshold_policy']})",
            "",
            "| metric | value |",
            "| --- | ---: |",
            f"| accuracy | {metrics['accuracy']} |",
            f"| precision | {metrics['precision']} |",
            f"| recall | {metrics['recall']} |",
            f"| f1 | {metrics['f1']} |",
            f"| tp | {metrics['tp']} |",
            f"| tn | {metrics['tn']} |",
            f"| fp | {metrics['fp']} |",
            f"| fn | {metrics['fn']} |",
            "",
            summary["claim_boundary"],
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
