from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from build_prism_adapter_dataset import DATASET_DIRS, channel_vectors, read_jsonl_functions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build memory-efficient Prism-adapter .npy arrays from local clone-detection splits. "
            "Rows follow Prism's 576-feature DNN layout plus a separate label vector."
        )
    )
    parser.add_argument("--dataset", required=True, choices=sorted(DATASET_DIRS))
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("eviclone_runs/baseline_reproduction/graphcodebert_dsfm_splits"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Default: eviclone_runs/baseline_reproduction/prism_adapter/<dataset>_full_arrays",
    )
    parser.add_argument("--splits", nargs="+", default=["train", "test"])
    parser.add_argument("--dim", type=int, default=96)
    parser.add_argument("--max-rows-per-split", type=int, default=0)
    parser.add_argument("--max-per-label", type=int, default=0)
    return parser.parse_args()


def count_split_rows(
    split_path: Path,
    functions: dict[str, str],
    *,
    max_rows: int,
    max_per_label: int,
) -> dict[str, object]:
    rows = 0
    scanned = 0
    skipped_missing = 0
    label_counts: Counter[str] = Counter()
    with split_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            scanned += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                raise ValueError(f"{split_path}:{line_no} expected id_a<TAB>id_b<TAB>label")
            left_id, right_id, label = parts
            if max_rows and rows >= max_rows:
                break
            if max_per_label and label_counts[label] >= max_per_label:
                continue
            if left_id not in functions or right_id not in functions:
                skipped_missing += 1
                continue
            rows += 1
            label_counts[label] += 1
    return {
        "rows": rows,
        "scanned_rows": scanned,
        "skipped_missing_functions": skipped_missing,
        "label_counts": dict(sorted(label_counts.items())),
    }


def write_split_arrays(
    split_path: Path,
    output_dir: Path,
    functions: dict[str, str],
    *,
    dim: int,
    max_rows: int,
    max_per_label: int,
) -> dict[str, object]:
    count_record = count_split_rows(split_path, functions, max_rows=max_rows, max_per_label=max_per_label)
    rows = int(count_record["rows"])
    output_dir.mkdir(parents=True, exist_ok=True)
    features_path = output_dir / f"{split_path.stem}.features.npy"
    labels_path = output_dir / f"{split_path.stem}.labels.npy"
    features = np.lib.format.open_memmap(features_path, mode="w+", dtype=np.float32, shape=(rows, dim * 6))
    labels = np.lib.format.open_memmap(labels_path, mode="w+", dtype=np.int64, shape=(rows,))

    cache: dict[str, tuple[list[float], list[float], list[float]]] = {}
    label_counts: Counter[str] = Counter()
    row_idx = 0
    with split_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                raise ValueError(f"{split_path}:{line_no} expected id_a<TAB>id_b<TAB>label")
            left_id, right_id, label_text = parts
            if max_rows and row_idx >= max_rows:
                break
            if max_per_label and label_counts[label_text] >= max_per_label:
                continue
            left = functions.get(left_id)
            right = functions.get(right_id)
            if left is None or right is None:
                continue
            if left_id not in cache:
                cache[left_id] = channel_vectors(left, dim=dim)
            if right_id not in cache:
                cache[right_id] = channel_vectors(right, dim=dim)
            left_arm, left_x86, left_text = cache[left_id]
            right_arm, right_x86, right_text = cache[right_id]
            features[row_idx, :] = np.asarray(
                [*left_arm, *left_x86, *left_text, *right_arm, *right_x86, *right_text],
                dtype=np.float32,
            )
            labels[row_idx] = int(label_text)
            label_counts[label_text] += 1
            row_idx += 1

    features.flush()
    labels.flush()
    return {
        **count_record,
        "features": str(features_path),
        "labels": str(labels_path),
        "row_width": dim * 6,
        "vector_cache_entries": len(cache),
    }


def main() -> int:
    args = parse_args()
    dataset_dir_name = DATASET_DIRS[args.dataset]
    dataset_dir = args.input_root / dataset_dir_name
    if not dataset_dir.exists():
        raise FileNotFoundError(dataset_dir)
    output_dir = args.output_dir or Path("eviclone_runs/baseline_reproduction/prism_adapter") / f"{args.dataset}_full_arrays"

    functions = read_jsonl_functions(dataset_dir / "data.jsonl")
    split_records = {}
    for split in args.splits:
        split_path = dataset_dir / f"{split}.txt"
        if not split_path.exists():
            raise FileNotFoundError(split_path)
        split_records[split] = write_split_arrays(
            split_path,
            output_dir,
            functions,
            dim=args.dim,
            max_rows=args.max_rows_per_split,
            max_per_label=args.max_per_label,
        )

    manifest = {
        "schema_version": "eviclone-prism-adapter-arrays/v1",
        "dataset": args.dataset,
        "source_dataset_dir": str(dataset_dir),
        "output_dir": str(output_dir),
        "feature_dim_per_channel": args.dim,
        "row_width": args.dim * 6,
        "feature_policy": (
            "Deterministic source-derived surrogate channels compatible with Prism's DNN input shape. "
            "This does not recreate the official Prism asm2vec/BERT feature pipeline."
        ),
        "max_rows_per_split": args.max_rows_per_split,
        "max_per_label": args.max_per_label,
        "splits": split_records,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "splits": split_records}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
