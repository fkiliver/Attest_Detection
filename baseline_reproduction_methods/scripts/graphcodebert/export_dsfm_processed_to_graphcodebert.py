from __future__ import annotations

import argparse
import json
import pickle
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


SPLIT_OUTPUT_NAMES = {
    "train": "train.txt",
    "val": "valid.txt",
    "valid": "valid.txt",
    "test": "test.txt",
}


def iter_pickle_stream(path: Path) -> Iterable[Any]:
    with path.open("rb") as source:
        while True:
            try:
                yield pickle.load(source)
            except EOFError:
                return


def load_code_stream(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"DSFM codes file not found: {path}")
    return [str(item) for item in iter_pickle_stream(path)]


def normalize_label(raw_label: Any) -> int:
    return 1 if int(raw_label) > 0 else 0


def split_source_name(split: str) -> str:
    return "val.pkl" if split == "valid" else f"{split}.pkl"


def write_data_jsonl(codes: list[str], output_path: Path) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8", newline="\n") as sink:
        for idx, code in enumerate(codes):
            sink.write(json.dumps({"idx": str(idx), "func": code}, ensure_ascii=False) + "\n")
    temp_path.replace(output_path)
    return {
        "path": str(output_path.resolve()),
        "rows": len(codes),
    }


def export_split(*, data_dir: Path, output_dir: Path, split: str, code_count: int) -> dict[str, Any]:
    source_path = data_dir / split_source_name(split)
    if not source_path.exists():
        raise FileNotFoundError(f"DSFM split file not found: {source_path}")

    output_name = SPLIT_OUTPUT_NAMES[split]
    output_path = output_dir / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    rows = 0
    positives = 0
    raw_label_counts: Counter[str] = Counter()
    max_index = -1
    min_index: int | None = None

    with temp_path.open("w", encoding="utf-8", newline="\n") as sink:
        for item in iter_pickle_stream(source_path):
            (idx_a, idx_b), raw_label = item
            idx_a = int(idx_a)
            idx_b = int(idx_b)
            if idx_a < 0 or idx_b < 0 or idx_a >= code_count or idx_b >= code_count:
                raise ValueError(
                    f"Split {source_path} references code ids outside [0, {code_count}): "
                    f"{idx_a}, {idx_b}"
                )
            label = normalize_label(raw_label)
            sink.write(f"{idx_a}\t{idx_b}\t{label}\n")
            rows += 1
            positives += int(label == 1)
            raw_label_counts[str(int(raw_label))] += 1
            max_index = max(max_index, idx_a, idx_b)
            min_index = min(idx_a, idx_b) if min_index is None else min(min_index, idx_a, idx_b)

    temp_path.replace(output_path)
    return {
        "source": str(source_path.resolve()),
        "output": str(output_path.resolve()),
        "rows": rows,
        "positive_labels": positives,
        "negative_labels": rows - positives,
        "raw_label_counts": dict(sorted(raw_label_counts.items(), key=lambda item: int(item[0]))),
        "min_code_index": min_index,
        "max_code_index": max_index,
        "label_rule": "raw_label > 0 => clone; raw_label <= 0 => non_clone",
        "format": "idx1<TAB>idx2<TAB>label",
    }


def export_dsfm_processed_to_graphcodebert(
    *,
    data_dir: Path,
    output_dir: Path,
    dataset_name: str | None = None,
    splits: list[str] | None = None,
) -> dict[str, Any]:
    selected_splits = splits or ["train", "val", "test"]
    normalized_splits = ["val" if split == "valid" else split for split in selected_splits]
    unknown = [split for split in normalized_splits if split not in {"train", "val", "test"}]
    if unknown:
        raise ValueError(f"Unsupported split names: {unknown}")

    codes = load_code_stream(data_dir / "codes.pkl")
    output_dir.mkdir(parents=True, exist_ok=True)
    data_jsonl = write_data_jsonl(codes, output_dir / "data.jsonl")
    split_summaries = {
        split: export_split(
            data_dir=data_dir,
            output_dir=output_dir,
            split=split,
            code_count=len(codes),
        )
        for split in normalized_splits
    }

    return {
        "schema_version": "eviclone-dsfm-to-graphcodebert/v1",
        "status": "exported",
        "dataset_name": dataset_name or data_dir.name,
        "source_data_dir": str(data_dir.resolve()),
        "output_dir": str(output_dir.resolve()),
        "data_jsonl": data_jsonl,
        "splits": split_summaries,
        "label_rule": "raw_label > 0 => clone; raw_label <= 0 => non_clone",
        "graphcodebert_format": {
            "data_jsonl": "one JSON object per function with string idx and func fields",
            "split_files": "tab-separated idx1, idx2, binary label",
        },
        "notes": [
            "The official Microsoft GraphCodeBERT clone-detection script expects this file layout.",
            "OJClone contains C/C++ programs in DSFM; the official GraphCodeBERT clone script hardcodes Java data-flow extraction, so OJClone needs either a C/C++ parser adaptation or a clearly declared text-only GraphCodeBERT protocol.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export a DSFM processed dataset to GraphCodeBERT/CodeXGLUE clone-detection layout."
    )
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-name", default=None)
    parser.add_argument(
        "--splits",
        nargs="+",
        choices=["train", "val", "valid", "test"],
        default=["train", "val", "test"],
    )
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()

    summary = export_dsfm_processed_to_graphcodebert(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        dataset_name=args.dataset_name,
        splits=args.splits,
    )
    summary_path = args.summary_path or args.output_dir / "export_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": summary["status"],
                "dataset_name": summary["dataset_name"],
                "output_dir": summary["output_dir"],
                "splits": {
                    name: {
                        "rows": split_summary["rows"],
                        "positive_labels": split_summary["positive_labels"],
                        "negative_labels": split_summary["negative_labels"],
                    }
                    for name, split_summary in summary["splits"].items()
                },
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
