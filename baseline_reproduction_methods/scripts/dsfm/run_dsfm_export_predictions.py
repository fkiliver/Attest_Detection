from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.config import DEFAULT_BASE_MODEL, DEFAULT_DSFM_REPO_DIR


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export per-pair DSFM predictions in the EviClone base prediction format. "
            "Run inside an environment that satisfies DSFM requirements."
        )
    )
    parser.add_argument("--dsfm-repo", type=Path, default=REPO_ROOT / DEFAULT_DSFM_REPO_DIR)
    parser.add_argument("--data-dir", type=Path, required=True, help="processed DSFM dataset directory")
    parser.add_argument("--checkpoint", type=Path, required=True, help="DSFM .pt checkpoint, for example pretrained_models/BigCloneBench.pt")
    parser.add_argument("--output", type=Path, required=True, help="EviClone prediction triplet output")
    parser.add_argument("--summary-path", type=Path, default=None)
    parser.add_argument("--pair-map", type=Path, default=None, help="optional rows aligned with the DSFM split: function_id_a function_id_b [gold]")
    parser.add_argument("--split", choices=["val", "test"], default="test")
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = parser.parse_args()

    summary = export_dsfm_predictions(
        dsfm_repo=args.dsfm_repo,
        data_dir=args.data_dir,
        checkpoint=args.checkpoint,
        output=args.output,
        pair_map=args.pair_map,
        split=args.split,
        batch_size=args.batch_size,
        threshold=args.threshold,
        device_arg=args.device,
    )
    summary_path = args.summary_path or args.output.with_suffix(".summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "output": str(args.output), "rows": summary["rows"]}, ensure_ascii=False))
    return 0 if summary["status"] == "exported" else 1


def export_dsfm_predictions(
    *,
    dsfm_repo: Path,
    data_dir: Path,
    checkpoint: Path,
    output: Path,
    pair_map: Path | None = None,
    split: str = "test",
    batch_size: int = 128,
    threshold: float = 0.5,
    device_arg: str = "auto",
) -> dict[str, Any]:
    dsfm_src = dsfm_repo.resolve() / "src"
    if not dsfm_src.exists():
        raise FileNotFoundError(f"DSFM src directory not found: {dsfm_src}")
    if not data_dir.exists():
        raise FileNotFoundError(f"DSFM data directory not found: {data_dir}")
    if not checkpoint.exists():
        raise FileNotFoundError(f"DSFM checkpoint not found: {checkpoint}")
    sys.path.insert(0, str(dsfm_src))

    import torch  # type: ignore
    from torch.utils.data import DataLoader  # type: ignore
    from model.data import Data  # type: ignore

    if device_arg == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = device_arg

    data = Data(data_dir, batch_size=batch_size, num_workers=0)
    dataset = data.val_dataset if split == "val" else data.test_dataset
    loader = DataLoader(dataset, collate_fn=data.collator, batch_size=batch_size, num_workers=0, shuffle=False)
    pair_ids = read_pair_map(pair_map) if pair_map else None
    if pair_ids is not None and len(pair_ids) != len(dataset):
        raise ValueError(f"pair map row count does not match DSFM {split} split: {len(pair_ids)} != {len(dataset)}")

    import model as model_pkg  # type: ignore
    from model.model import Model  # type: ignore

    setattr(model_pkg, "Model", Model)
    try:
        model = torch.load(checkpoint, map_location=device, weights_only=False)
    except TypeError:
        model = torch.load(checkpoint, map_location=device)
    model.use_gpu = device == "cuda"
    model.device = device
    model.eval()

    output.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    positives = 0
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        offset = 0
        with torch.no_grad():
            for (features1, features2), _labels in loader:
                logits = model(features1, features2)
                probabilities = torch.sigmoid(logits).detach().cpu().numpy().tolist()
                for probability in probabilities:
                    prob = float(probability)
                    label = 1 if prob >= threshold else 0
                    confidence = prob if label == 1 else 1.0 - prob
                    margin = abs(prob - 0.5) * 2.0
                    if pair_ids is not None:
                        function_id_a, function_id_b = pair_ids[offset]
                    else:
                        internal_a, internal_b = dataset.pairs[offset]
                        function_id_a, function_id_b = str(internal_a), str(internal_b)
                    handle.write(f"{function_id_a} {function_id_b} {label} {confidence:.8f} {margin:.8f}\n")
                    rows += 1
                    positives += int(label == 1)
                    offset += 1

    return {
        "schema_version": "eviclone-dsfm-prediction-export/v1",
        "status": "exported",
        "base_model": DEFAULT_BASE_MODEL,
        "dsfm_repo": str(dsfm_repo.resolve()),
        "data_dir": str(data_dir.resolve()),
        "checkpoint": str(checkpoint.resolve()),
        "split": split,
        "threshold": threshold,
        "device": device,
        "output": str(output.resolve()),
        "rows": rows,
        "positive_predictions": positives,
        "negative_predictions": rows - positives,
        "pair_map": str(pair_map.resolve()) if pair_map else "",
        "output_format": "function_id_a function_id_b label confidence margin",
    }


def read_pair_map(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            parts = text.replace(",", " ").split()
            if len(parts) < 2:
                raise ValueError(f"expected at least two columns in pair map at {path}:{line_no}")
            rows.append((parts[0], parts[1]))
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
