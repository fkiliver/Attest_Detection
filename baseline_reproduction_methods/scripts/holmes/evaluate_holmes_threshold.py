from __future__ import annotations

import argparse
import importlib
import json
import sys
import __main__
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch_geometric.loader import DataLoader

from run_holmes_artifact import LegacyHolmesDataset, PairData, forward_batch, metric_dict, normalized_y


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune a probability threshold for a saved HOLMES artifact model.")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, default=Path("external/HOLMES_drive/Model"))
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--dataset", choices=["bcb", "gcj", "ojclone"], required=True)
    parser.add_argument("--variant", choices=["EA", "EU"], default="EA")
    parser.add_argument("--val-limit", type=int, default=0)
    parser.add_argument("--test-limit", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--grid-step", type=float, default=0.001)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--claim-boundary", default="")
    return parser.parse_args()


def choose_device(requested: str) -> torch.device:
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("--device cuda requested, but CUDA is not available")
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@torch.no_grad()
def score_model(model: torch.nn.Module, loader: DataLoader, *, device: torch.device, variant: str) -> dict[str, list[Any]]:
    model.eval()
    scores: list[float] = []
    gold: list[int] = []
    sample_indices: list[int] = []
    for batch in loader:
        y = normalized_y(batch.y.to(device))
        pred, _ = forward_batch(model, batch, y=y, device=device, variant=variant)
        scores.extend(np.asarray(pred).reshape(-1).astype(float).tolist())
        gold.extend(y.detach().cpu().numpy().reshape(-1).astype(int).tolist())
        if hasattr(batch, "sample_id"):
            sample_indices.extend(batch.sample_id.detach().cpu().numpy().reshape(-1).astype(int).tolist())
        else:
            sample_indices.extend(range(len(sample_indices), len(sample_indices) + int(y.numel())))
    return {"score": scores, "gold": gold, "sample_index": sample_indices}


def choose_threshold(gold: list[int], scores: list[float], step: float) -> dict[str, Any]:
    score_array = np.asarray(scores)
    thresholds = np.arange(0.0, 1.0 + step / 2, step)
    best: dict[str, Any] | None = None
    sampled: list[dict[str, Any]] = []
    for threshold in thresholds:
        pred = (score_array >= threshold).astype(int)
        metrics = metric_dict(gold, pred)
        record = {"threshold": round(float(threshold), 6), **metrics}
        if best is None or metrics["f1"] > best["f1"]:
            best = record
        if abs((threshold * 100) - round(threshold * 100)) < 1e-9:
            sampled.append(record)
    assert best is not None
    return {"best": best, "sampled_candidates": sampled}


def write_predictions(path: Path, scores: dict[str, list[Any]], pred: np.ndarray) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for sample_index, gold, score, label in zip(scores["sample_index"], scores["gold"], scores["score"], pred.tolist()):
            handle.write(
                json.dumps(
                    {"sample_index": int(sample_index), "gold": int(gold), "score": float(score), "prediction": int(label)},
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(args.model_dir.resolve()))
    __main__.PairData = PairData
    model_module = importlib.import_module(f"holmes{args.variant}")
    device = choose_device(args.device)
    model = model_module.BCE(100).to(device)
    checkpoint = torch.load(args.model, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["state_dict"] if isinstance(checkpoint, dict) and "state_dict" in checkpoint else checkpoint)
    prefix = f"{args.dataset}{args.variant}"
    val_ds = LegacyHolmesDataset(args.data_root / prefix / "val" / "processed", limit=args.val_limit)
    test_ds = LegacyHolmesDataset(args.data_root / prefix / "test" / "processed", limit=args.test_limit)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, follow_batch=["x1", "x2"], num_workers=0, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, follow_batch=["x1", "x2"], num_workers=0, shuffle=False)
    val_scores = score_model(model, val_loader, device=device, variant=args.variant)
    threshold_record = choose_threshold(val_scores["gold"], val_scores["score"], args.grid_step)
    test_scores = score_model(model, test_loader, device=device, variant=args.variant)
    threshold = float(threshold_record["best"]["threshold"])
    test_pred = (np.asarray(test_scores["score"]) >= threshold).astype(int)
    test_metrics = metric_dict(test_scores["gold"], test_pred)
    predictions_path = args.output_dir / "holmes_threshold_predictions.jsonl"
    write_predictions(predictions_path, test_scores, test_pred)
    metrics = {
        "schema_version": "eviclone-holmes-threshold-eval/v1",
        "claim_boundary": args.claim_boundary
        or "Probability-threshold evaluation of a saved HOLMES local artifact model; does not retrain or change labels.",
        "model": str(args.model),
        "model_dir": str(args.model_dir),
        "data_root": str(args.data_root),
        "dataset": args.dataset,
        "variant": args.variant,
        "device": str(device),
        "grid_step": args.grid_step,
        "rows": {"val": len(val_ds), "test": len(test_ds)},
        "threshold": threshold_record,
        "test_metrics": test_metrics,
        "predictions": str(predictions_path),
    }
    metrics_path = args.output_dir / "holmes_threshold_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": str(metrics_path), "test_metrics": test_metrics, "threshold": threshold}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
