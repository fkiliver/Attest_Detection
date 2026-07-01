from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch.utils.data import DataLoader, TensorDataset


REPO_ROOT = Path(__file__).resolve().parents[1]
PRISM_DNN = REPO_ROOT / "external" / "Prism" / "dnn"
if str(PRISM_DNN) not in sys.path:
    sys.path.insert(0, str(PRISM_DNN))

from model_loop import Classifier_Net  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune a probability threshold for a saved Prism adapter model.")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--val-features-npy", type=Path, required=True)
    parser.add_argument("--val-labels-npy", type=Path, required=True)
    parser.add_argument("--test-features-npy", type=Path, required=True)
    parser.add_argument("--test-labels-npy", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--grid-step", type=float, default=0.001)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
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


def load_arrays(features_path: Path, labels_path: Path) -> tuple[np.ndarray, np.ndarray]:
    features = np.load(features_path, mmap_mode="r")
    labels = np.load(labels_path, mmap_mode="r")
    if features.shape[0] != labels.shape[0]:
        raise ValueError(f"{features_path} rows do not match {labels_path}")
    return features, labels


def make_loader(features: np.ndarray, labels: np.ndarray, batch_size: int) -> DataLoader:
    dataset = TensorDataset(torch.from_numpy(np.asarray(features, dtype=np.float32)), torch.from_numpy(np.asarray(labels, dtype=np.int64)))
    return DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)


@torch.no_grad()
def score_model(model: torch.nn.Module, loader: DataLoader, device: torch.device) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    scores: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    for batch_features, batch_labels in loader:
        logits = model(batch_features.to(device))
        prob = torch.softmax(logits, dim=1)[:, 1]
        scores.append(prob.detach().cpu().numpy())
        labels.append(batch_labels.numpy())
    return np.concatenate(scores), np.concatenate(labels)


def metric_dict(gold: np.ndarray, pred: np.ndarray) -> dict[str, Any]:
    gold = gold.astype(int)
    pred = pred.astype(int)
    tp = int(((pred == 1) & (gold == 1)).sum())
    tn = int(((pred == 0) & (gold == 0)).sum())
    fp = int(((pred == 1) & (gold == 0)).sum())
    fn = int(((pred == 0) & (gold == 1)).sum())
    return {
        "accuracy": round(float(accuracy_score(gold, pred)), 6),
        "precision": round(float(precision_score(gold, pred, zero_division=0)), 6),
        "recall": round(float(recall_score(gold, pred, zero_division=0)), 6),
        "f1": round(float(f1_score(gold, pred, zero_division=0)), 6),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def choose_threshold(gold: np.ndarray, scores: np.ndarray, step: float) -> dict[str, Any]:
    thresholds = np.arange(0.0, 1.0 + step / 2, step)
    best: dict[str, Any] | None = None
    sampled: list[dict[str, Any]] = []
    for threshold in thresholds:
        pred = (scores >= threshold).astype(int)
        metrics = metric_dict(gold, pred)
        record = {"threshold": round(float(threshold), 6), **metrics}
        if best is None or metrics["f1"] > best["f1"]:
            best = record
        if abs((threshold * 100) - round(threshold * 100)) < 1e-9:
            sampled.append(record)
    assert best is not None
    return {"best": best, "sampled_candidates": sampled}


def write_predictions(path: Path, gold: np.ndarray, scores: np.ndarray, pred: np.ndarray) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for index, (label, score, prediction) in enumerate(zip(gold.tolist(), scores.tolist(), pred.tolist())):
            handle.write(
                json.dumps(
                    {"sample_index": index, "gold": int(label), "score": float(score), "prediction": int(prediction)},
                    ensure_ascii=False,
                )
                + "\n"
            )


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    device = choose_device(args.device)
    model = Classifier_Net(feature_len=96, kernel_size=3, n_output=2).to(device)
    model.load_state_dict(torch.load(args.model, map_location=device))
    val_x, val_y = load_arrays(args.val_features_npy, args.val_labels_npy)
    test_x, test_y = load_arrays(args.test_features_npy, args.test_labels_npy)
    val_scores, val_gold = score_model(model, make_loader(val_x, val_y, args.batch_size), device)
    threshold_record = choose_threshold(val_gold, val_scores, args.grid_step)
    test_scores, test_gold = score_model(model, make_loader(test_x, test_y, args.batch_size), device)
    threshold = float(threshold_record["best"]["threshold"])
    test_pred = (test_scores >= threshold).astype(int)
    test_metrics = metric_dict(test_gold, test_pred)
    predictions_path = args.output_dir / "prism_threshold_predictions.jsonl"
    write_predictions(predictions_path, test_gold, test_scores, test_pred)
    metrics = {
        "schema_version": "eviclone-prism-threshold-eval/v1",
        "claim_boundary": args.claim_boundary
        or "Probability-threshold evaluation of a saved Prism compile-adapter model; not the official Prism asm2vec+BERT pipeline.",
        "model": str(args.model),
        "val_features_npy": str(args.val_features_npy),
        "val_labels_npy": str(args.val_labels_npy),
        "test_features_npy": str(args.test_features_npy),
        "test_labels_npy": str(args.test_labels_npy),
        "device": str(device),
        "grid_step": args.grid_step,
        "threshold": threshold_record,
        "test_rows": int(len(test_gold)),
        "test_metrics": test_metrics,
        "predictions": str(predictions_path),
    }
    metrics_path = args.output_dir / "prism_threshold_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": str(metrics_path), "test_metrics": test_metrics, "threshold": threshold}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
