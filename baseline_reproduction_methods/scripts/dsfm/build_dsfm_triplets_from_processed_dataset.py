from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Export DSFM processed split labels as EviClone triplet rows.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--split", choices=["train", "val", "test"], default="test")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-path", type=Path, default=None)
    args = parser.parse_args()

    summary = build_dsfm_triplets(
        data_dir=args.data_dir,
        split=args.split,
        output=args.output,
    )
    summary_path = args.summary_path or args.output.with_suffix(".summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "rows": summary["rows"], "output": str(args.output)}, ensure_ascii=False))
    return 0


def build_dsfm_triplets(*, data_dir: Path, split: str, output: Path) -> dict[str, Any]:
    split_path = data_dir / f"{split}.pkl"
    if not split_path.exists():
        raise FileNotFoundError(f"DSFM split file not found: {split_path}")
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    positives = 0
    negative_raw = 0
    positive_raw = 0
    with split_path.open("rb") as source, output.open("w", encoding="utf-8", newline="\n") as sink:
        while True:
            try:
                (idx_a, idx_b), raw_label = pickle.load(source)
            except EOFError:
                break
            label = 1 if int(raw_label) > 0 else 0
            positives += int(label == 1)
            positive_raw += int(int(raw_label) > 0)
            negative_raw += int(int(raw_label) < 0)
            sink.write(f"{idx_a} {idx_b} {label}\n")
            rows += 1
    return {
        "schema_version": "eviclone-dsfm-processed-triplets/v1",
        "status": "exported",
        "data_dir": str(data_dir.resolve()),
        "split": split,
        "output": str(output.resolve()),
        "rows": rows,
        "positive_labels": positives,
        "negative_labels": rows - positives,
        "positive_raw_labels": positive_raw,
        "negative_raw_labels": negative_raw,
        "label_rule": "raw_label > 0 => clone; raw_label <= 0 => non_clone",
    }


if __name__ == "__main__":
    raise SystemExit(main())
