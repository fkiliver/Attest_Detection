from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader, SequentialSampler
from transformers import RobertaConfig, RobertaForSequenceClassification, RobertaTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GraphCodeBERT clone inference and sweep clone thresholds.")
    parser.add_argument("--graphcodebert-dir", type=Path, default=Path("source_snapshots/GraphCodeBERT/clonedetection"))
    parser.add_argument("--model-name-or-path", default="microsoft/graphcodebert-base")
    parser.add_argument("--config-name", default="microsoft/graphcodebert-base")
    parser.add_argument("--tokenizer-name", default="microsoft/graphcodebert-base")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--test-data-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--code-length", type=int, default=512)
    parser.add_argument("--data-flow-length", type=int, default=128)
    parser.add_argument("--eval-batch-size", type=int, default=8)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--seed", type=int, default=123456)
    parser.add_argument("--official-threshold", type=float, default=0.97)
    parser.add_argument("--grid-step", type=float, default=0.01)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    set_seed(args.seed)
    device = choose_device(args.device)
    run_module = load_graphcodebert_run(args.graphcodebert_dir)
    infer_args = argparse.Namespace(
        code_length=args.code_length,
        data_flow_length=args.data_flow_length,
        eval_batch_size=args.eval_batch_size,
        num_workers=args.num_workers,
        device=device,
        n_gpu=1 if device.type == "cuda" else 0,
    )

    config = RobertaConfig.from_pretrained(args.config_name)
    config.num_labels = 1
    tokenizer = RobertaTokenizer.from_pretrained(args.tokenizer_name)
    encoder = RobertaForSequenceClassification.from_pretrained(args.model_name_or_path, config=config)
    model = run_module.Model(encoder, config, tokenizer, infer_args)
    state = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model.load_state_dict(state)
    model.to(device)

    dataset = run_module.TextDataset(tokenizer, infer_args, file_path=str(args.test_data_file))
    loader = DataLoader(
        dataset,
        sampler=SequentialSampler(dataset),
        batch_size=args.eval_batch_size,
        num_workers=args.num_workers,
    )
    scores = infer_scores(model, loader, device=device)
    rows = []
    labels = []
    for example, score in zip(dataset.examples, scores):
        label = int(example.label)
        labels.append(label)
        rows.append(
            {
                "function_id_a": str(example.url1),
                "function_id_b": str(example.url2),
                "gold": label,
                "p_non_clone": float(1.0 - score),
                "p_clone": float(score),
            }
        )

    scores_path = args.output_dir / "graphcodebert_scores.jsonl"
    with scores_path.open("w", encoding="utf-8", newline="\n") as sink:
        for row in rows:
            sink.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    thresholds = sorted(
        set(
            [round(float(x), 6) for x in np.arange(0.0, 1.0 + args.grid_step / 2, args.grid_step)]
            + [0.5, round(float(args.official_threshold), 6)]
        )
    )
    sweep = []
    for threshold in thresholds:
        predictions = (np.asarray(scores) > threshold).astype(int)
        record = {
            "threshold": threshold,
            "metrics": metric_dict(labels, predictions),
            "prediction_counts": count_predictions(predictions),
        }
        sweep.append(record)

    best = max(
        sweep,
        key=lambda row: (
            float(row["metrics"]["f1"]),
            float(row["metrics"]["accuracy"]),
            float(row["metrics"]["precision"]),
        ),
    )
    selected_thresholds = {
        "default_0.5": 0.5,
        "official_valid_threshold": round(float(args.official_threshold), 6),
        "best_on_hardset_diagnostic": float(best["threshold"]),
    }
    prediction_artifacts = {}
    for name, threshold in selected_thresholds.items():
        path = args.output_dir / f"graphcodebert_predictions_{name}.txt"
        write_predictions(path, rows=rows, threshold=threshold)
        prediction_artifacts[name] = str(path)

    summary = {
        "schema_version": "eviclone-graphcodebert-threshold-sweep/v1",
        "status": "completed",
        "dataset": "BCB-LLM-Refined-HardCases-balanced",
        "test_data_file": str(args.test_data_file),
        "checkpoint": str(args.checkpoint),
        "model_name_or_path": args.model_name_or_path,
        "device": str(device),
        "rows": len(rows),
        "label_counts": dict(sorted(Counter(str(value) for value in labels).items())),
        "score_summary": score_summary(rows),
        "thresholds": {
            "default_0.5": find_threshold(sweep, 0.5),
            "official_valid_threshold": find_threshold(sweep, args.official_threshold),
            "best_on_hardset_diagnostic": best,
        },
        "sweep": sweep,
        "artifacts": {
            "scores_jsonl": str(scores_path),
            "summary_json": str(args.output_dir / "graphcodebert_threshold_sweep.json"),
            "summary_md": str(args.output_dir / "graphcodebert_threshold_sweep.md"),
            "predictions": prediction_artifacts,
        },
        "claim_boundary": (
            "The best_on_hardset_diagnostic threshold is selected on the hard-case test labels, so it is an "
            "optimistic diagnostic upper bound. Use the official_valid_threshold row for protocol-consistent reporting."
        ),
    }
    (args.output_dir / "graphcodebert_threshold_sweep.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "graphcodebert_threshold_sweep.md").write_text(render_markdown(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "rows": summary["rows"],
                "default_0.5_f1": summary["thresholds"]["default_0.5"]["metrics"]["f1"],
                "official_threshold_f1": summary["thresholds"]["official_valid_threshold"]["metrics"]["f1"],
                "best_threshold": summary["thresholds"]["best_on_hardset_diagnostic"]["threshold"],
                "best_f1": summary["thresholds"]["best_on_hardset_diagnostic"]["metrics"]["f1"],
                "summary": summary["artifacts"]["summary_json"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def choose_device(requested: str) -> torch.device:
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("--device cuda requested, but CUDA is unavailable")
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_graphcodebert_run(graphcodebert_dir: Path) -> Any:
    graphcodebert_dir = graphcodebert_dir.resolve()
    if str(graphcodebert_dir) not in sys.path:
        sys.path.insert(0, str(graphcodebert_dir))
    spec = importlib.util.spec_from_file_location("graphcodebert_clone_run_for_threshold", graphcodebert_dir / "run.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import GraphCodeBERT run.py from {graphcodebert_dir}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@torch.no_grad()
def infer_scores(model: torch.nn.Module, loader: DataLoader, *, device: torch.device) -> list[float]:
    model.eval()
    scores: list[float] = []
    for batch in loader:
        (
            inputs_ids_1,
            position_idx_1,
            attn_mask_1,
            inputs_ids_2,
            position_idx_2,
            attn_mask_2,
            labels,
        ) = [item.to(device) for item in batch]
        _loss, prob = model(
            inputs_ids_1,
            position_idx_1,
            attn_mask_1,
            inputs_ids_2,
            position_idx_2,
            attn_mask_2,
            labels,
        )
        scores.extend(prob[:, 1].detach().cpu().numpy().astype(float).tolist())
    return scores


def metric_dict(gold: list[int], pred: np.ndarray) -> dict[str, Any]:
    gold_array = np.asarray(gold).astype(int)
    pred_array = np.asarray(pred).astype(int)
    tp = int(((pred_array == 1) & (gold_array == 1)).sum())
    tn = int(((pred_array == 0) & (gold_array == 0)).sum())
    fp = int(((pred_array == 1) & (gold_array == 0)).sum())
    fn = int(((pred_array == 0) & (gold_array == 1)).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(gold_array) if len(gold_array) else 0.0
    return {
        "accuracy": round(float(accuracy), 6),
        "precision": round(float(precision), 6),
        "recall": round(float(recall), 6),
        "f1": round(float(f1), 6),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def count_predictions(pred: np.ndarray) -> dict[str, int]:
    counts = Counter(int(value) for value in pred.tolist())
    return {"0": int(counts.get(0, 0)), "1": int(counts.get(1, 0))}


def find_threshold(sweep: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    normalized = round(float(threshold), 6)
    for row in sweep:
        if round(float(row["threshold"]), 6) == normalized:
            return row
    raise ValueError(f"threshold {threshold} missing from sweep")


def write_predictions(path: Path, *, rows: list[dict[str, Any]], threshold: float) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as sink:
        for row in rows:
            pred = 1 if float(row["p_clone"]) > threshold else 0
            sink.write(f"{row['function_id_a']}\t{row['function_id_b']}\t{pred}\t{float(row['p_clone']):.8f}\n")


def score_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for label in [0, 1]:
        scores = np.asarray([row["p_clone"] for row in rows if int(row["gold"]) == label], dtype=float)
        if len(scores) == 0:
            result[str(label)] = {}
            continue
        result[str(label)] = {
            "count": int(len(scores)),
            "min": round(float(np.min(scores)), 6),
            "p25": round(float(np.quantile(scores, 0.25)), 6),
            "median": round(float(np.median(scores)), 6),
            "p75": round(float(np.quantile(scores, 0.75)), 6),
            "max": round(float(np.max(scores)), 6),
            "mean": round(float(np.mean(scores)), 6),
        }
    return result


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# GraphCodeBERT Threshold Sweep",
        "",
        f"Dataset: `{summary['dataset']}`",
        f"Rows: {summary['rows']}; labels: {summary['label_counts']}",
        "",
        "| Threshold setting | Threshold | Accuracy | Precision | Recall | F1 | TP/TN/FP/FN |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in summary["thresholds"].items():
        metrics = row["metrics"]
        lines.append(
            f"| {name} | {row['threshold']:.6f} | {metrics['accuracy']*100:.2f} | "
            f"{metrics['precision']*100:.2f} | {metrics['recall']*100:.2f} | {metrics['f1']*100:.2f} | "
            f"{metrics['tp']}/{metrics['tn']}/{metrics['fp']}/{metrics['fn']} |"
        )
    lines.extend(
        [
            "",
            "## Score Summary",
            "",
            "Clone probability (`p_clone`) by gold label:",
            "",
            "| Gold label | Count | Min | P25 | Median | P75 | Max | Mean |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label, stats in summary["score_summary"].items():
        lines.append(
            f"| {label} | {stats['count']} | {stats['min']:.6f} | {stats['p25']:.6f} | "
            f"{stats['median']:.6f} | {stats['p75']:.6f} | {stats['max']:.6f} | {stats['mean']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            summary["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
