from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset


REPO_ROOT = Path(__file__).resolve().parents[1]
PRISM_DNN = REPO_ROOT / "external" / "Prism" / "dnn"
if str(PRISM_DNN) not in sys.path:
    sys.path.insert(0, str(PRISM_DNN))

from model_loop import Classifier_Net  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run Prism's DNN classifier on adapter-generated merge.csv files. "
            "This uses Prism's model_loop.Classifier_Net with local surrogate features."
        )
    )
    parser.add_argument("--train-csv", type=Path)
    parser.add_argument("--test-csv", type=Path)
    parser.add_argument("--train-features-npy", type=Path)
    parser.add_argument("--train-labels-npy", type=Path)
    parser.add_argument("--test-features-npy", type=Path)
    parser.add_argument("--test-labels-npy", type=Path)
    parser.add_argument("--val-features-npy", type=Path)
    parser.add_argument("--val-labels-npy", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--eval-batch-size", type=int, default=0)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--max-train-rows", type=int, default=0)
    parser.add_argument("--max-test-rows", type=int, default=0)
    parser.add_argument("--max-val-rows", type=int, default=0)
    parser.add_argument("--balanced-train-rows", type=int, default=0)
    parser.add_argument(
        "--class-weight",
        choices=["none", "balanced"],
        default="none",
        help="Use class-balanced CrossEntropy weights computed from the training labels.",
    )
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--mmap", action="store_true", help="Memory-map .npy arrays instead of loading them into RAM.")
    parser.add_argument("--claim-boundary", default="")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--save-model", action="store_true")
    parser.add_argument("--skip-train-eval", action="store_true")
    parser.add_argument("--select-val-threshold", action="store_true")
    parser.add_argument("--val-threshold-grid-step", type=float, default=0.01)
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def choose_device(requested: str) -> torch.device:
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("--device cuda requested, but CUDA is not available")
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_merge_csv(path: Path, *, max_rows: int = 0) -> tuple[np.ndarray, np.ndarray]:
    rows: list[list[float]] = []
    labels: list[int] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row_no, row in enumerate(reader, start=1):
            if not row:
                continue
            if max_rows and len(rows) >= max_rows:
                break
            if len(row) != 577:
                raise ValueError(f"{path}:{row_no} expected 577 columns, found {len(row)}")
            rows.append([float(value) for value in row[:-1]])
            labels.append(int(float(row[-1])))
    if not rows:
        raise ValueError(f"{path} did not contain any rows")
    return np.asarray(rows, dtype=np.float32), np.asarray(labels, dtype=np.int64)


def load_npy_pair(
    features_path: Path,
    labels_path: Path,
    *,
    max_rows: int = 0,
    mmap: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    mode = "r" if mmap else None
    features = np.load(features_path, mmap_mode=mode)
    labels = np.load(labels_path, mmap_mode=mode)
    if features.ndim != 2 or features.shape[1] != 576:
        raise ValueError(f"{features_path} expected shape (*, 576), found {features.shape}")
    if labels.ndim != 1 or labels.shape[0] != features.shape[0]:
        raise ValueError(f"{labels_path} labels shape {labels.shape} does not match features {features.shape}")
    if max_rows:
        features = features[:max_rows]
        labels = labels[:max_rows]
    if not mmap:
        features = np.asarray(features, dtype=np.float32)
        labels = np.asarray(labels, dtype=np.int64)
    return features, labels


def balanced_subset(features: np.ndarray, labels: np.ndarray, *, rows: int, seed: int) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    if rows <= 0:
        return features, labels, {}
    rng = np.random.default_rng(seed)
    labels_array = np.asarray(labels)
    pos = np.where(labels_array == 1)[0]
    neg = np.where(labels_array == 0)[0]
    pos_target = min(len(pos), rows // 2)
    neg_target = min(len(neg), rows - pos_target)
    if pos_target + neg_target < rows and pos_target < len(pos):
        pos_target = min(len(pos), rows - neg_target)
    pos_sel = rng.choice(pos, size=pos_target, replace=False) if pos_target else np.asarray([], dtype=np.int64)
    neg_sel = rng.choice(neg, size=neg_target, replace=False) if neg_target else np.asarray([], dtype=np.int64)
    selected = np.concatenate([pos_sel, neg_sel])
    rng.shuffle(selected)
    subset_features = np.asarray(features[selected], dtype=np.float32)
    subset_labels = np.asarray(labels_array[selected], dtype=np.int64)
    return subset_features, subset_labels, {"requested": rows, "selected": int(len(selected)), "positive": int(pos_target), "negative": int(neg_target)}


def load_inputs(args: argparse.Namespace) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None, np.ndarray, np.ndarray, dict[str, str]]:
    csv_mode = bool(args.train_csv or args.test_csv)
    npy_mode = bool(args.train_features_npy or args.train_labels_npy or args.test_features_npy or args.test_labels_npy)
    if csv_mode == npy_mode:
        raise ValueError("provide either --train-csv/--test-csv or all four --*-npy paths")
    if csv_mode:
        if not args.train_csv or not args.test_csv:
            raise ValueError("--train-csv and --test-csv must be provided together")
        train_x, train_y = load_merge_csv(args.train_csv, max_rows=args.max_train_rows)
        test_x, test_y = load_merge_csv(args.test_csv, max_rows=args.max_test_rows)
        sources = {"train_csv": str(args.train_csv), "test_csv": str(args.test_csv)}
        return train_x, train_y, None, None, test_x, test_y, sources
    required = [args.train_features_npy, args.train_labels_npy, args.test_features_npy, args.test_labels_npy]
    if any(path is None for path in required):
        raise ValueError("all four --train-features-npy/--train-labels-npy/--test-features-npy/--test-labels-npy paths are required")
    train_x, train_y = load_npy_pair(
        args.train_features_npy,
        args.train_labels_npy,
        max_rows=args.max_train_rows,
        mmap=args.mmap,
    )
    balanced_record: dict[str, int] = {}
    if args.balanced_train_rows:
        train_x, train_y, balanced_record = balanced_subset(train_x, train_y, rows=args.balanced_train_rows, seed=args.seed)
    test_x, test_y = load_npy_pair(
        args.test_features_npy,
        args.test_labels_npy,
        max_rows=args.max_test_rows,
        mmap=args.mmap,
    )
    val_x = val_y = None
    if args.val_features_npy or args.val_labels_npy:
        if not args.val_features_npy or not args.val_labels_npy:
            raise ValueError("--val-features-npy and --val-labels-npy must be provided together")
        val_x, val_y = load_npy_pair(args.val_features_npy, args.val_labels_npy, max_rows=args.max_val_rows, mmap=args.mmap)
    sources = {
        "train_features_npy": str(args.train_features_npy),
        "train_labels_npy": str(args.train_labels_npy),
        "test_features_npy": str(args.test_features_npy),
        "test_labels_npy": str(args.test_labels_npy),
    }
    if args.val_features_npy:
        sources["val_features_npy"] = str(args.val_features_npy)
        sources["val_labels_npy"] = str(args.val_labels_npy)
    if balanced_record:
        sources["balanced_train_rows"] = json.dumps(balanced_record, ensure_ascii=False)
    return train_x, train_y, val_x, val_y, test_x, test_y, sources


def make_loader(features: np.ndarray, labels: np.ndarray, *, batch_size: int, shuffle: bool) -> DataLoader:
    dataset = TensorDataset(torch.from_numpy(features), torch.from_numpy(labels))
    return DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,
        drop_last=shuffle and len(dataset) > batch_size,
    )


def confusion(predictions: np.ndarray, labels: np.ndarray) -> dict[str, int]:
    return {
        "tp": int(((predictions == 1) & (labels == 1)).sum()),
        "tn": int(((predictions == 0) & (labels == 0)).sum()),
        "fp": int(((predictions == 1) & (labels == 0)).sum()),
        "fn": int(((predictions == 0) & (labels == 1)).sum()),
    }


def metrics_from_confusion(items: dict[str, int]) -> dict[str, float]:
    tp = items["tp"]
    tn = items["tn"]
    fp = items["fp"]
    fn = items["fn"]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if tp + tn + fp + fn else 0.0
    return {
        "accuracy": round(accuracy, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }


def choose_threshold(gold: np.ndarray, scores: np.ndarray, *, step: float) -> dict[str, object]:
    thresholds = np.arange(0.0, 1.0 + step / 2, step)
    best: dict[str, object] | None = None
    for threshold in thresholds:
        pred = (scores >= threshold).astype(np.int64)
        conf = confusion(pred, gold.astype(np.int64))
        metrics = metrics_from_confusion(conf)
        record = {"threshold": round(float(threshold), 6), "confusion": conf, "metrics": metrics}
        if best is None or float(metrics["f1"]) > float(best["metrics"]["f1"]):
            best = record
    assert best is not None
    return best


@torch.no_grad()
def evaluate(model: torch.nn.Module, loader: DataLoader, *, device: torch.device) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    all_predictions: list[np.ndarray] = []
    all_labels: list[np.ndarray] = []
    for batch_features, batch_labels in loader:
        logits = model(batch_features.to(device))
        predictions = torch.argmax(logits, dim=1).cpu().numpy()
        all_predictions.append(predictions)
        all_labels.append(batch_labels.numpy())
    return np.concatenate(all_predictions), np.concatenate(all_labels)


@torch.no_grad()
def score_model(model: torch.nn.Module, loader: DataLoader, *, device: torch.device) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    all_scores: list[np.ndarray] = []
    all_labels: list[np.ndarray] = []
    for batch_features, batch_labels in loader:
        logits = model(batch_features.to(device))
        scores = torch.softmax(logits, dim=1)[:, 1].detach().cpu().numpy()
        all_scores.append(scores)
        all_labels.append(batch_labels.numpy())
    return np.concatenate(all_scores), np.concatenate(all_labels)


def main() -> int:
    args = parse_args()
    set_seed(args.seed)
    device = choose_device(args.device)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_x, train_y, val_x, val_y, test_x, test_y, sources = load_inputs(args)

    model = Classifier_Net(feature_len=96, kernel_size=3, n_output=2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    class_weight_record: dict[str, object] = {"mode": args.class_weight}
    if args.class_weight == "balanced":
        counts = np.bincount(np.asarray(train_y, dtype=np.int64), minlength=2).astype(np.float64)
        if (counts == 0).any():
            raise ValueError(f"cannot use balanced class weights with empty class counts: {counts.tolist()}")
        weights = counts.sum() / (len(counts) * counts)
        class_weight_record["counts"] = [int(value) for value in counts.tolist()]
        class_weight_record["weights"] = [float(value) for value in weights.tolist()]
        loss_fn = torch.nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32, device=device))
    else:
        loss_fn = torch.nn.CrossEntropyLoss()
    eval_batch_size = args.eval_batch_size or args.batch_size
    train_loader = make_loader(train_x, train_y, batch_size=args.batch_size, shuffle=True)
    eval_train_loader = make_loader(train_x, train_y, batch_size=eval_batch_size, shuffle=False)
    val_loader = make_loader(val_x, val_y, batch_size=eval_batch_size, shuffle=False) if val_x is not None and val_y is not None else None
    test_loader = make_loader(test_x, test_y, batch_size=eval_batch_size, shuffle=False)

    epoch_records = []
    best_val: dict[str, object] | None = None
    best_state: dict[str, torch.Tensor] | None = None
    for epoch in range(args.epochs):
        model.train()
        losses = []
        for batch_features, batch_labels in train_loader:
            logits = model(batch_features.to(device))
            loss = loss_fn(logits, batch_labels.to(device))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            losses.append(float(loss.detach().cpu().item()))
        epoch_record = {
            "epoch": epoch + 1,
            "loss": round(sum(losses) / len(losses), 6) if losses else 0.0,
        }
        if not args.skip_train_eval:
            train_pred, train_gold = evaluate(model, eval_train_loader, device=device)
            train_conf = confusion(train_pred, train_gold)
            train_metrics = metrics_from_confusion(train_conf)
            epoch_record["train_confusion"] = train_conf
            epoch_record["train_metrics"] = train_metrics
        if val_loader is not None:
            if args.select_val_threshold:
                val_scores, val_gold = score_model(model, val_loader, device=device)
                threshold_record = choose_threshold(val_gold, val_scores, step=args.val_threshold_grid_step)
                val_conf = threshold_record["confusion"]
                val_metrics = threshold_record["metrics"]
                epoch_record["val_threshold"] = threshold_record["threshold"]
            else:
                val_pred, val_gold = evaluate(model, val_loader, device=device)
                val_conf = confusion(val_pred, val_gold)
                val_metrics = metrics_from_confusion(val_conf)
            epoch_record["val_confusion"] = val_conf
            epoch_record["val_metrics"] = val_metrics
            if best_val is None or float(val_metrics["f1"]) > float(best_val["metrics"]["f1"]):
                best_val = {"epoch": epoch + 1, "confusion": val_conf, "metrics": val_metrics}
                if args.select_val_threshold:
                    best_val["threshold"] = epoch_record["val_threshold"]
                best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        epoch_records.append(epoch_record)
        print(json.dumps(epoch_record, ensure_ascii=False), flush=True)

    if best_state is not None:
        model.load_state_dict(best_state)
    test_pred, test_gold = evaluate(model, test_loader, device=device)
    test_conf = confusion(test_pred, test_gold)
    test_metrics = metrics_from_confusion(test_conf)

    predictions_path = args.output_dir / "prism_adapter_predictions.txt"
    predictions_path.write_text("\n".join(str(int(value)) for value in test_pred) + "\n", encoding="utf-8")
    metrics = {
        "schema_version": "eviclone-prism-adapter-run/v1",
        "claim_boundary": args.claim_boundary or (
            "Prism DNN architecture run using deterministic source-derived surrogate features. "
            "This does not compile source code, does not run Prism's asm2vec/BERT feature pipeline, "
            "and must be reported only as a no-compile surrogate diagnostic variant."
        ),
        **sources,
        "device": str(device),
        "mmap": bool(args.mmap),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "eval_batch_size": eval_batch_size,
        "class_weight": class_weight_record,
        "weight_decay": args.weight_decay,
        "skip_train_eval": bool(args.skip_train_eval),
        "max_val_rows": args.max_val_rows,
        "select_val_threshold": bool(args.select_val_threshold),
        "val_threshold_grid_step": args.val_threshold_grid_step,
        "train_rows": int(len(train_y)),
        "test_rows": int(len(test_y)),
        "test_confusion": test_conf,
        "test_metrics": test_metrics,
        "best_val": best_val,
        "predictions": str(predictions_path),
        "epoch_records": epoch_records,
    }
    metrics_path = args.output_dir / "prism_adapter_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.save_model:
        torch.save(model.state_dict(), args.output_dir / "prism_adapter_model.pt")
    print(json.dumps({"metrics": str(metrics_path), "test_metrics": test_metrics}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
