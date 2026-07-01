from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create train-z-scored Prism .npy feature arrays.")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--splits", nargs="+", default=["train", "valid", "test"])
    parser.add_argument("--chunk-rows", type=int, default=100_000)
    parser.add_argument("--std-floor", type=float, default=1e-6)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def load_features(path: Path) -> np.ndarray:
    features = np.load(path, mmap_mode="r")
    if features.ndim != 2 or features.shape[1] != 576:
        raise ValueError(f"{path} expected shape (*, 576), found {features.shape}")
    return features


def iter_chunks(features: np.ndarray, chunk_rows: int):
    for start in range(0, features.shape[0], chunk_rows):
        end = min(start + chunk_rows, features.shape[0])
        yield start, end, np.asarray(features[start:end], dtype=np.float64)


def compute_train_stats(train_features: np.ndarray, chunk_rows: int, std_floor: float) -> tuple[np.ndarray, np.ndarray]:
    rows = train_features.shape[0]
    total = np.zeros(train_features.shape[1], dtype=np.float64)
    total_sq = np.zeros(train_features.shape[1], dtype=np.float64)
    for _, _, chunk in iter_chunks(train_features, chunk_rows):
        total += chunk.sum(axis=0)
        total_sq += np.square(chunk).sum(axis=0)
    mean = total / rows
    variance = np.maximum(total_sq / rows - np.square(mean), 0.0)
    std = np.sqrt(variance)
    std = np.where(std < std_floor, 1.0, std)
    return mean.astype(np.float32), std.astype(np.float32)


def write_standardized_split(
    source_features_path: Path,
    source_labels_path: Path,
    output_features_path: Path,
    output_labels_path: Path,
    mean: np.ndarray,
    std: np.ndarray,
    chunk_rows: int,
) -> dict[str, object]:
    source_features = load_features(source_features_path)
    source_labels = np.load(source_labels_path, mmap_mode="r")
    if source_labels.ndim != 1 or source_labels.shape[0] != source_features.shape[0]:
        raise ValueError(f"{source_labels_path} labels do not match {source_features_path}")

    output_features = np.lib.format.open_memmap(
        output_features_path,
        mode="w+",
        dtype=np.float32,
        shape=source_features.shape,
    )
    for start, end, chunk in iter_chunks(source_features, chunk_rows):
        output_features[start:end] = ((chunk.astype(np.float32) - mean) / std).astype(np.float32)
        if end % (chunk_rows * 5) == 0 or end == source_features.shape[0]:
            print(json.dumps({"split": output_features_path.stem, "rows_written": int(end), "total": int(source_features.shape[0])}), flush=True)
    del output_features

    np.save(output_labels_path, np.asarray(source_labels, dtype=np.int64))
    labels = np.asarray(source_labels, dtype=np.int64)
    values, counts = np.unique(labels, return_counts=True)
    return {
        "rows": int(source_features.shape[0]),
        "row_width": int(source_features.shape[1]),
        "features": str(output_features_path),
        "labels": str(output_labels_path),
        "label_counts": {str(int(value)): int(count) for value, count in zip(values, counts)},
    }


def main() -> int:
    args = parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()) and not args.force:
        raise FileExistsError(f"{args.output_dir} already exists and is not empty; pass --force to reuse it")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_features_path = args.input_dir / "train.features.npy"
    train_features = load_features(train_features_path)
    mean, std = compute_train_stats(train_features, args.chunk_rows, args.std_floor)
    mean_path = args.output_dir / "feature_mean.npy"
    std_path = args.output_dir / "feature_std.npy"
    np.save(mean_path, mean)
    np.save(std_path, std)

    split_records: dict[str, object] = {}
    for split in args.splits:
        split_records[split] = write_standardized_split(
            args.input_dir / f"{split}.features.npy",
            args.input_dir / f"{split}.labels.npy",
            args.output_dir / f"{split}.features.npy",
            args.output_dir / f"{split}.labels.npy",
            mean,
            std,
            args.chunk_rows,
        )

    source_manifest = args.input_dir / "manifest.json"
    copied_source_manifest = None
    if source_manifest.exists():
        copied_source_manifest = args.output_dir / "source_manifest.json"
        shutil.copyfile(source_manifest, copied_source_manifest)

    manifest = {
        "schema_version": "eviclone-prism-standardized-arrays/v1",
        "source_dir": str(args.input_dir),
        "output_dir": str(args.output_dir),
        "source_manifest": str(copied_source_manifest) if copied_source_manifest else "",
        "standardization": {
            "fit_split": "train",
            "feature_width": int(mean.shape[0]),
            "mean": str(mean_path),
            "std": str(std_path),
            "std_floor": args.std_floor,
            "policy": "Per-column z-score using only train split statistics.",
        },
        "splits": split_records,
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "splits": split_records}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
