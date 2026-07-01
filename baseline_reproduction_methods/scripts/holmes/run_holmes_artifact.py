from __future__ import annotations

import argparse
import importlib
import json
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch_geometric.data import Data, Dataset
from torch_geometric.loader import DataLoader


DATA_RE = re.compile(r"data_(\d+)\.pt$")


class PairData(Data):
    def __inc__(self, key: str, value: Any, *args: Any, **kwargs: Any) -> int:
        if key in {"edgedata_index1", "edgecontrol_index1", "edge_index1"}:
            return int(self.x1.size(0))
        if key in {"edgedata_index2", "edgecontrol_index2", "edge_index2"}:
            return int(self.x2.size(0))
        return super().__inc__(key, value, *args, **kwargs)

    def __cat_dim__(self, key: str, value: Any, *args: Any, **kwargs: Any) -> int:
        if "index" in key or "face" in key:
            return 1
        return 0


class LegacyHolmesDataset(Dataset):
    def __init__(self, processed_dir: Path, *, limit: int = 0) -> None:
        super().__init__(root=str(processed_dir.parent))
        self._legacy_processed_dir = processed_dir
        paths = sorted(
            processed_dir.glob("data_*.pt"),
            key=lambda path: int(DATA_RE.match(path.name).group(1)) if DATA_RE.match(path.name) else 10**18,
        )
        self.paths = paths[:limit] if limit and limit > 0 else paths

    def len(self) -> int:
        return len(self.paths)

    def get(self, idx: int) -> PairData:
        legacy = torch.load(self.paths[idx], weights_only=False)
        get_field = lambda key: read_data_field(legacy, key, required=True)
        kwargs = {
            "x1": get_field("x1").float(),
            "x2": get_field("x2").float(),
            "y": get_field("y").float(),
            "sample_id": torch.tensor([int(DATA_RE.match(self.paths[idx].name).group(1))], dtype=torch.long),
        }
        for key in ["edgedata_index1", "edgedata_index2", "edgecontrol_index1", "edgecontrol_index2", "edge_index1", "edge_index2"]:
            value = read_data_field(legacy, key)
            if value is not None:
                kwargs[key] = value.long()
        return PairData(**kwargs)


def read_data_field(data: Data, key: str, *, required: bool = False) -> Any:
    fields = object.__getattribute__(data, "__dict__")
    if key in fields:
        return fields[key]

    store = fields.get("_store")
    if store is not None:
        store_fields = object.__getattribute__(store, "__dict__")
        mapping = store_fields.get("_mapping")
        if mapping is not None and key in mapping:
            return mapping[key]
        try:
            if key in store:
                return store[key]
        except Exception:
            pass

    try:
        return data[key]
    except Exception:
        pass

    if required:
        raise KeyError(f"Missing required HOLMES data field {key!r}")
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run downloaded HOLMES artifacts while preserving metrics/predictions.")
    parser.add_argument("--model-dir", type=Path, default=Path("external/HOLMES_drive/Model"))
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--variant", choices=["EA", "EU"], default="EA")
    parser.add_argument("--dataset", choices=["bcb", "gcj", "ojclone"], required=True)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--train-limit", type=int, default=0)
    parser.add_argument("--val-limit", type=int, default=0)
    parser.add_argument("--test-limit", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=30)
    parser.add_argument("--eval-batch-size", type=int, default=500)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--progress-every-batches", type=int, default=0)
    parser.add_argument("--learning-rate", type=float, default=0.0002)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--lr-decay-epoch", type=int, default=0, help="Set lr to --lr-decay-value at the start of this 1-based epoch.")
    parser.add_argument("--lr-decay-value", type=float, default=0.0)
    parser.add_argument("--threshold-grid-step", type=float, default=0.1)
    parser.add_argument("--select-best-val", action="store_true")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seed_everything(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(args.model_dir.resolve()))
    model_module = importlib.import_module(f"holmes{args.variant}")
    device = choose_device(args.device)
    model = model_module.BCE(100).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)

    prefix = f"{args.dataset}{args.variant}"
    train_ds = LegacyHolmesDataset(args.data_root / prefix / "train" / "processed", limit=args.train_limit)
    val_ds = LegacyHolmesDataset(args.data_root / prefix / "val" / "processed", limit=args.val_limit)
    test_ds = LegacyHolmesDataset(args.data_root / prefix / "test" / "processed", limit=args.test_limit)
    loaders = {
        "train": DataLoader(train_ds, batch_size=args.batch_size, follow_batch=["x1", "x2"], num_workers=args.num_workers, shuffle=True),
        "val": DataLoader(val_ds, batch_size=args.eval_batch_size, follow_batch=["x1", "x2"], num_workers=args.num_workers, shuffle=False),
        "test": DataLoader(test_ds, batch_size=args.eval_batch_size, follow_batch=["x1", "x2"], num_workers=args.num_workers, shuffle=False),
    }

    epoch_records = []
    best_val: dict[str, Any] | None = None
    best_state: dict[str, torch.Tensor] | None = None
    for epoch in range(1, args.epochs + 1):
        if args.lr_decay_epoch and epoch == args.lr_decay_epoch:
            for group in optimizer.param_groups:
                group["lr"] = args.lr_decay_value
        start = time.time()
        train_record = train_epoch(
            model,
            optimizer,
            loaders["train"],
            device=device,
            variant=args.variant,
            epoch=epoch,
            progress_every_batches=args.progress_every_batches,
        )
        train_record["epoch"] = epoch
        train_record["learning_rate"] = float(optimizer.param_groups[0]["lr"])
        train_record["seconds"] = round(time.time() - start, 3)
        if args.select_best_val:
            val_scores_epoch = predict(model, loaders["val"], device=device, variant=args.variant)
            val_threshold_epoch = choose_threshold(val_scores_epoch["gold"], val_scores_epoch["score"], step=args.threshold_grid_step)
            train_record["val_threshold"] = {
                "threshold": val_threshold_epoch["threshold"],
                "best_f1": val_threshold_epoch["best_f1"],
            }
            if best_val is None or float(val_threshold_epoch["best_f1"]) > float(best_val["best_f1"]):
                best_val = {
                    "epoch": epoch,
                    "threshold": val_threshold_epoch["threshold"],
                    "best_f1": val_threshold_epoch["best_f1"],
                }
                best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        epoch_records.append(train_record)
        print(json.dumps(train_record, ensure_ascii=False), flush=True)

    if best_state is not None:
        model.load_state_dict(best_state)
    val_scores = predict(model, loaders["val"], device=device, variant=args.variant)
    threshold_record = choose_threshold(val_scores["gold"], val_scores["score"], step=args.threshold_grid_step)
    test_scores = predict(model, loaders["test"], device=device, variant=args.variant)
    test_pred = (np.asarray(test_scores["score"]) > threshold_record["threshold"]).astype(int)
    metrics = metric_dict(test_scores["gold"], test_pred)
    predictions_path = args.output_dir / "holmes_predictions.jsonl"
    write_predictions(predictions_path, test_scores, test_pred)

    model_path = args.output_dir / f"{args.dataset}_holmes_{args.variant}.pth"
    torch.save({"state_dict": model.state_dict(), "optimizer": optimizer.state_dict()}, model_path)
    if args.dataset == "ojclone":
        claim_boundary = (
            "HOLMES model code run on a local OJClone HOLMES-compatible graph adapter. "
            "The supplied HOLMES artifact has no OJClone processed graph package, so this is an adapter variant "
            "rather than the original HOLMES PDG extraction pipeline."
        )
    else:
        claim_boundary = (
            "Downloaded HOLMES artifact run using the released model code and released processed graph data. "
            "Rows may be capped by --*-limit and must be labelled as smoke/variant unless full official rows are used."
        )
    manifest = {
        "schema_version": "eviclone-holmes-artifact-run/v1",
        "dataset": args.dataset,
        "variant": args.variant,
        "data_root": str(args.data_root),
        "model_dir": str(args.model_dir),
        "device": str(device),
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "eval_batch_size": args.eval_batch_size,
        "limits": {"train": args.train_limit, "val": args.val_limit, "test": args.test_limit},
        "rows": {"train": len(train_ds), "val": len(val_ds), "test": len(test_ds)},
        "epoch_records": epoch_records,
        "best_val": best_val,
        "threshold": threshold_record,
        "test_metrics": metrics,
        "predictions": str(predictions_path),
        "model": str(model_path),
        "claim_boundary": claim_boundary,
    }
    metrics_path = args.output_dir / "holmes_metrics.json"
    metrics_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": str(metrics_path), "test_metrics": metrics, "rows": manifest["rows"]}, ensure_ascii=False), flush=True)
    return 0


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def choose_device(requested: str) -> torch.device:
    if requested == "cuda":
        return torch.device("cuda")
    if requested == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def train_epoch(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    loader: DataLoader,
    *,
    device: torch.device,
    variant: str,
    epoch: int,
    progress_every_batches: int = 0,
) -> dict[str, Any]:
    model.train()
    total_loss = 0.0
    total_rows = 0
    start = time.time()
    for batch_no, batch in enumerate(loader, start=1):
        y = normalized_y(batch.y.to(device))
        optimizer.zero_grad()
        _, loss = forward_batch(model, batch, y=y, device=device, variant=variant)
        loss.backward()
        optimizer.step()
        rows = int(y.numel())
        total_loss += float(loss.item()) * rows
        total_rows += rows
        if progress_every_batches and batch_no % progress_every_batches == 0:
            print(
                json.dumps(
                    {
                        "progress": "train",
                        "epoch": epoch,
                        "batches": batch_no,
                        "rows": total_rows,
                        "loss_so_far": round(total_loss / total_rows, 6) if total_rows else None,
                        "seconds": round(time.time() - start, 3),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
    return {"train_rows": total_rows, "loss": round(total_loss / total_rows, 6) if total_rows else None}


def predict(model: torch.nn.Module, loader: DataLoader, *, device: torch.device, variant: str) -> dict[str, list[Any]]:
    model.eval()
    scores: list[float] = []
    gold: list[int] = []
    sample_indices: list[int] = []
    with torch.no_grad():
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


def forward_batch(model: torch.nn.Module, batch: PairData, *, y: torch.Tensor, device: torch.device, variant: str) -> tuple[np.ndarray, torch.Tensor]:
    x1 = batch.x1.to(device)
    x2 = batch.x2.to(device)
    x1_batch = batch.x1_batch.to(device)
    x2_batch = batch.x2_batch.to(device)
    if variant == "EA":
        return model(
            x1,
            x2,
            batch.edgedata_index1.to(device).long(),
            batch.edgecontrol_index1.to(device).long(),
            batch.edgedata_index2.to(device).long(),
            batch.edgecontrol_index2.to(device).long(),
            y,
            x1_batch,
            x2_batch,
        )
    return model(
        x1,
        x2,
        batch.edge_index1.to(device).long(),
        batch.edge_index2.to(device).long(),
        y.view(-1),
        x1_batch,
        x2_batch,
    )


def normalized_y(y: torch.Tensor) -> torch.Tensor:
    y = y.float().view(-1, 1)
    return torch.where(y < 0, torch.zeros_like(y), y)


def choose_threshold(gold: list[int], score: list[float], *, step: float = 0.1) -> dict[str, Any]:
    thresholds = [round(float(value), 10) for value in np.arange(0.0, 1.0 + step / 2, step)]
    rows = []
    best = {"threshold": thresholds[0], "f1": -1.0}
    for threshold in thresholds:
        pred = (np.asarray(score) > threshold).astype(int)
        metrics = metric_dict(gold, pred)
        rows.append({"threshold": threshold, **metrics})
        if metrics["f1"] > best["f1"]:
            best = {"threshold": threshold, "f1": metrics["f1"]}
    return {"threshold": best["threshold"], "best_f1": best["f1"], "candidates": rows}


def metric_dict(gold: list[int], pred: Any) -> dict[str, Any]:
    pred_array = np.asarray(pred).astype(int)
    gold_array = np.asarray(gold).astype(int)
    tp = int(((pred_array == 1) & (gold_array == 1)).sum())
    tn = int(((pred_array == 0) & (gold_array == 0)).sum())
    fp = int(((pred_array == 1) & (gold_array == 0)).sum())
    fn = int(((pred_array == 0) & (gold_array == 1)).sum())
    return {
        "accuracy": round(float(accuracy_score(gold_array, pred_array)), 6) if len(gold_array) else None,
        "precision": round(float(precision_score(gold_array, pred_array, zero_division=0)), 6) if len(gold_array) else None,
        "recall": round(float(recall_score(gold_array, pred_array, zero_division=0)), 6) if len(gold_array) else None,
        "f1": round(float(f1_score(gold_array, pred_array, zero_division=0)), 6) if len(gold_array) else None,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


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


if __name__ == "__main__":
    raise SystemExit(main())
