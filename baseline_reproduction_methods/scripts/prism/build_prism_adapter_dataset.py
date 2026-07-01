from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
from collections import Counter
from pathlib import Path
from typing import Iterable


DATASET_DIRS = {
    "BCB": "BigCloneBench",
    "BigCloneBench": "BigCloneBench",
    "OJClone": "OJClone",
    "GCJ": "GCJ",
}

TOKEN_RE = re.compile(
    r"[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d+)?|==|!=|<=|>=|&&|\|\||[-+*/%<>=!&|^~?:;,.{}()\[\]]"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build Prism-compatible merge.csv files from the local clone-detection splits. "
            "The generated features are deterministic source-derived surrogate features, "
            "not the original Prism asm2vec/BERT artifacts."
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
        help="Default: eviclone_runs/baseline_reproduction/prism_adapter/<dataset>",
    )
    parser.add_argument("--splits", nargs="+", default=["train", "valid", "test"])
    parser.add_argument("--dim", type=int, default=96)
    parser.add_argument("--max-rows-per-split", type=int, default=0)
    parser.add_argument("--max-per-label", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def read_jsonl_functions(path: Path) -> dict[str, str]:
    functions: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            obj = json.loads(line)
            idx = str(obj.get("idx"))
            func = obj.get("func")
            if func is None:
                raise ValueError(f"{path}:{line_no} has no func field")
            functions[idx] = str(func)
    return functions


def tokens(code: str) -> list[str]:
    return TOKEN_RE.findall(code)


def char_ngrams(code: str, sizes: Iterable[int]) -> Iterable[str]:
    compact = re.sub(r"\s+", " ", code)
    for size in sizes:
        if len(compact) < size:
            continue
        for i in range(len(compact) - size + 1):
            yield compact[i : i + size]


def token_ngrams(items: list[str], size: int) -> Iterable[str]:
    if len(items) < size:
        return
    for i in range(len(items) - size + 1):
        yield " ".join(items[i : i + size])


def hash_bucket(feature: str, *, namespace: str, dim: int) -> tuple[int, float]:
    digest = hashlib.blake2b(f"{namespace}\0{feature}".encode("utf-8"), digest_size=8).digest()
    value = int.from_bytes(digest, "little", signed=False)
    sign = 1.0 if (value >> 63) == 0 else -1.0
    return value % dim, sign


def hashed_vector(features: Iterable[str], *, namespace: str, dim: int) -> list[float]:
    vector = [0.0] * dim
    for feature in features:
        bucket, sign = hash_bucket(feature, namespace=namespace, dim=dim)
        vector[bucket] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    return vector


def channel_vectors(code: str, *, dim: int) -> tuple[list[float], list[float], list[float]]:
    toks = tokens(code)
    token_features = [f"tok:{tok.lower()}" for tok in toks]
    token_features.extend(f"kw:{tok}" for tok in toks if tok in {"for", "while", "if", "else", "return", "switch"})

    arm_features = [f"tri:{gram}" for gram in char_ngrams(code, [3])]
    arm_features.extend(f"tok2:{gram.lower()}" for gram in token_ngrams(toks, 2) or [])

    x86_features = [f"quad:{gram}" for gram in char_ngrams(code, [4])]
    x86_features.extend(f"tok3:{gram.lower()}" for gram in token_ngrams(toks, 3) or [])

    text_vec = hashed_vector(token_features, namespace="prism-text-surrogate", dim=dim)
    arm_vec = hashed_vector(arm_features, namespace="prism-arm-surrogate", dim=dim)
    x86_vec = hashed_vector(x86_features, namespace="prism-x86-surrogate", dim=dim)
    return arm_vec, x86_vec, text_vec


def format_row(values: Iterable[float], label: int) -> list[str]:
    row = [f"{value:.7f}" for value in values]
    row.append(str(label))
    return row


def write_split(
    *,
    split_path: Path,
    output_csv: Path,
    functions: dict[str, str],
    dim: int,
    max_rows: int,
    max_per_label: int,
    rng: random.Random,
) -> dict[str, object]:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    cache: dict[str, tuple[list[float], list[float], list[float]]] = {}
    label_counts: Counter[str] = Counter()
    rows = 0
    scanned = 0
    skipped_missing = 0

    with split_path.open("r", encoding="utf-8") as source, output_csv.open("w", newline="", encoding="utf-8") as sink:
        writer = csv.writer(sink)
        for line_no, line in enumerate(source, start=1):
            if not line.strip():
                continue
            scanned += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                raise ValueError(f"{split_path}:{line_no} expected id_a<TAB>id_b<TAB>label")
            left_id, right_id, label_text = parts
            label = int(label_text)
            if max_rows and rows >= max_rows:
                break
            if max_per_label and label_counts[label_text] >= max_per_label:
                continue
            left = functions.get(left_id)
            right = functions.get(right_id)
            if left is None or right is None:
                skipped_missing += 1
                continue
            if left_id not in cache:
                cache[left_id] = channel_vectors(left, dim=dim)
            if right_id not in cache:
                cache[right_id] = channel_vectors(right, dim=dim)
            # The jitter-free shuffle key avoids always taking one class/topic first when a cap is used.
            if max_rows or max_per_label:
                _ = rng.random()
            left_arm, left_x86, left_text = cache[left_id]
            right_arm, right_x86, right_text = cache[right_id]
            writer.writerow(
                format_row(
                    [*left_arm, *left_x86, *left_text, *right_arm, *right_x86, *right_text],
                    label,
                )
            )
            rows += 1
            label_counts[label_text] += 1

    return {
        "path": str(output_csv),
        "rows": rows,
        "scanned_rows": scanned,
        "skipped_missing_functions": skipped_missing,
        "label_counts": dict(sorted(label_counts.items())),
    }


def main() -> int:
    args = parse_args()
    dataset_dir_name = DATASET_DIRS[args.dataset]
    dataset_dir = args.input_root / dataset_dir_name
    if not dataset_dir.exists():
        raise FileNotFoundError(dataset_dir)
    output_dir = args.output_dir or Path("eviclone_runs/baseline_reproduction/prism_adapter") / args.dataset
    rng = random.Random(args.seed)

    functions = read_jsonl_functions(dataset_dir / "data.jsonl")
    split_records = {}
    for split in args.splits:
        split_path = dataset_dir / f"{split}.txt"
        if not split_path.exists():
            raise FileNotFoundError(split_path)
        split_records[split] = write_split(
            split_path=split_path,
            output_csv=output_dir / f"{split}.merge.csv",
            functions=functions,
            dim=args.dim,
            max_rows=args.max_rows_per_split,
            max_per_label=args.max_per_label,
            rng=rng,
        )

    manifest = {
        "schema_version": "eviclone-prism-adapter-dataset/v1",
        "dataset": args.dataset,
        "source_dataset_dir": str(dataset_dir),
        "output_dir": str(output_dir),
        "feature_dim_per_channel": args.dim,
        "row_width": args.dim * 6 + 1,
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
