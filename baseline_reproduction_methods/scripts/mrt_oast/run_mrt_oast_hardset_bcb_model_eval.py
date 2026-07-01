from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F


DEFAULT_REPO_ROOT = Path("external") / "MRT-OAST"
DEFAULT_HARDSET_DIR = Path("eviclone_runs") / "baseline_reproduction" / "hardset_eviclone_corrected_gcb"
DEFAULT_MODEL_DIR = (
    Path("eviclone_runs")
    / "baseline_reproduction"
    / "mrt_oast_bcb_cuda_fullsplit_10epoch_default"
    / "model"
)
DEFAULT_OUTPUT_DIR = (
    Path("eviclone_runs")
    / "baseline_reproduction"
    / "mrt_oast_hardset_bcb_model_eval"
)


class OovDictionary(dict[str, int]):
    def __init__(self, values: dict[str, int]) -> None:
        super().__init__(values)
        self.oov_counter: Counter[str] = Counter()

    def __missing__(self, key: str) -> int:
        self.oov_counter[key] += 1
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate MRT-OAST BCB-model transfer on EviClone HardSet with retained AST/OAST inputs."
    )
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--hardset-dir", type=Path, default=DEFAULT_HARDSET_DIR)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--sen-max-len", type=int, default=256)
    parser.add_argument("--threshold", type=float, default=0.9)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    hardset_dir = args.hardset_dir.resolve()
    model_path = (args.model_dir / "model.pt").resolve()
    output_dir = args.output_dir.resolve()
    input_dir = output_dir / "input"
    output_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()
    status = "completed"
    error = None
    try:
        add_mrt_import_path(repo_root)
        generated = materialize_hardset_mrt_inputs(
            repo_root=repo_root,
            hardset_dir=hardset_dir,
            input_dir=input_dir,
        )
        eval_result = evaluate_hardset(
            repo_root=repo_root,
            model_path=model_path,
            data_csv=generated["data_csv"],
            test_csv=generated["test_csv"],
            dictionary_path=repo_root / "origindata" / "BCB_XXX_dictionary.txt",
            sen_max_len=args.sen_max_len,
            batch_size=args.batch_size,
            threshold=args.threshold,
            predictions_csv=output_dir / "mrt_oast_hardset_predictions.csv",
            predictions_txt=output_dir / "mrt_oast_hardset_predictions.txt",
        )
    except Exception as exc:  # pragma: no cover - retained diagnostic artifact path
        status = "failed"
        error = repr(exc)
        generated = {}
        eval_result = {}

    summary = {
        "schema_version": "eviclone-mrt-oast-hardset-bcb-model-eval/v1",
        "status": status,
        "error": error,
        "dataset": "HardSet",
        "method": "MRT-OAST",
        "source_hardset_dir": str(hardset_dir),
        "repo_root": str(repo_root),
        "model_path": str(model_path),
        "output_dir": str(output_dir),
        "elapsed_seconds": round(time.time() - start, 3),
        "rows": eval_result.get("rows"),
        "metrics": eval_result.get("metrics"),
        "confusion": eval_result.get("confusion"),
        "parse": generated.get("parse"),
        "oov": eval_result.get("oov"),
        "protocol": {
            "base_model": "MRT-OAST BCB CUDA full-split 10-epoch code-default variant",
            "ast_generator": "MRT-OAST repository oast_builder.py and ast_builder.py on function-level Java snippets",
            "dictionary": "BCB_OAST_dictionary.txt",
            "oov_policy": "map unseen HardSet OAST tokens to 0 because the retained BCB model embedding cannot be resized",
            "threshold": args.threshold,
            "sen_max_len": args.sen_max_len,
            "batch_size": args.batch_size,
            "device": "cpu",
        },
        "retained_outputs": {
            "data_csv": str(generated.get("data_csv", "")),
            "test_csv": str(generated.get("test_csv", "")),
            "predictions_csv": str(output_dir / "mrt_oast_hardset_predictions.csv"),
            "predictions_txt": str(output_dir / "mrt_oast_hardset_predictions.txt"),
            "parse_failures": str(input_dir / "parse_failures.json"),
        },
        "table_policy": (
            "HardSet transfer evaluation using a locally trained MRT-OAST BCB variant model. This is useful hard-set "
            "evidence, but it is not an original paper-protocol benchmark cell; keep a [var] status label."
        ),
    }

    json_path = output_dir / "mrt_oast_hardset_bcb_model_eval.json"
    md_path = output_dir / "mrt_oast_hardset_bcb_model_eval.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps({"status": status, "output": str(json_path), "report": str(md_path)}, sort_keys=True))
    return 0 if status == "completed" else 2


def add_mrt_import_path(repo_root: Path) -> None:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def materialize_hardset_mrt_inputs(*, repo_root: Path, hardset_dir: Path, input_dir: Path) -> dict[str, Any]:
    import javalang
    from ast_builder import get_sequence_ast
    from oast_builder import build_sequence_oast

    data_jsonl = hardset_dir / "data.jsonl"
    test_txt = hardset_dir / "test.txt"
    if not data_jsonl.exists():
        raise FileNotFoundError(data_jsonl)
    if not test_txt.exists():
        raise FileNotFoundError(test_txt)

    common_type = ast.literal_eval((repo_root / "origindata" / "BCB_OAST_type_list.txt").read_text(encoding="utf-8"))
    common_func = ast.literal_eval((repo_root / "origindata" / "BCB_OAST_func_list.txt").read_text(encoding="utf-8"))

    functions = [json.loads(line) for line in data_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    failures = []
    for item in functions:
        idx = str(item["idx"])
        code = str(item["func"])
        file_name = f"{idx}.txt"
        try:
            tokens = javalang.tokenizer.tokenize(code)
            parser = javalang.parse.Parser(tokens)
            java_ast = parser.parse_member_declaration()
            ast_seq = get_sequence_ast(java_ast, {"in_BOP": False})
            oast_seq = build_sequence_oast(
                java_ast,
                {"in_BOP": False, "symbol_table": {}, "common_func": common_func, "common_type": common_type},
            )
            rows.append(
                {
                    "index": idx,
                    "file": file_name,
                    "code": code.replace("\0", ""),
                    "AST": " ".join(ast_seq),
                    "OAST": " ".join(oast_seq),
                }
            )
        except Exception as exc:  # pragma: no cover - depends on input corpus
            failures.append({"idx": idx, "file": file_name, "error": repr(exc)})

    data_csv = input_dir / "HardSet_with_AST+OAST.csv"
    with data_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["index", "file", "code", "AST", "OAST"])
        writer.writeheader()
        writer.writerows(rows)

    available = {row["index"] for row in rows}
    pair_rows = []
    dropped_pairs = []
    for row_index, line in enumerate(test_txt.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) < 3:
            dropped_pairs.append({"row": row_index, "line": line, "reason": "malformed"})
            continue
        left, right, label = parts[0], parts[1], parts[2]
        if left not in available or right not in available:
            dropped_pairs.append({"row": row_index, "line": line, "reason": "function_parse_missing"})
            continue
        pair_rows.append(
            {
                "index1": left,
                "file1": f"{left}.txt",
                "index2": right,
                "file2": f"{right}.txt",
                "label": label,
                "ctype": "HardSet",
            }
        )

    test_csv = input_dir / "HardSet_test.csv"
    with test_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["index1", "file1", "index2", "file2", "label", "ctype"])
        writer.writeheader()
        writer.writerows(pair_rows)

    parse_report = {
        "function_rows": len(functions),
        "parsed_functions": len(rows),
        "parse_failures": failures,
        "test_rows": len([line for line in test_txt.read_text(encoding="utf-8").splitlines() if line.strip()]),
        "retained_pairs": len(pair_rows),
        "dropped_pairs": dropped_pairs,
    }
    (input_dir / "parse_failures.json").write_text(
        json.dumps(parse_report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {"data_csv": data_csv, "test_csv": test_csv, "parse": parse_report}


def evaluate_hardset(
    *,
    repo_root: Path,
    model_path: Path,
    data_csv: Path,
    test_csv: Path,
    dictionary_path: Path,
    sen_max_len: int,
    batch_size: int,
    threshold: float,
    predictions_csv: Path,
    predictions_txt: Path,
) -> dict[str, Any]:
    from dataset import YDataset
    from preprocess_data import preprocess_tree, process_pair

    if not model_path.exists():
        raise FileNotFoundError(model_path)

    dictionary = OovDictionary(load_dictionary(dictionary_path.with_name("BCB_OAST_dictionary.txt")))
    with data_csv.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        processed_data = preprocess_tree(handle, "OAST", str(data_csv), dictionary, sen_max_len)
    with test_csv.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        pair_data = process_pair(handle)
    dataset = YDataset(processed_data, pair_data, True, sen_max_len)

    model = load_torch_model(model_path)
    features = generate_features(model, dataset, batch_size)
    prediction_rows = score_pairs(features, pair_data, threshold)
    write_predictions(prediction_rows, predictions_csv, predictions_txt)
    confusion = confusion_from_predictions(prediction_rows)
    metrics = metrics_from_confusion(confusion)
    return {
        "rows": {
            "functions": sum(len(files) for files in processed_data.values()),
            "pairs": len(pair_data),
            "predictions": len(prediction_rows),
        },
        "metrics": metrics,
        "confusion": confusion,
        "oov": {
            "token_occurrences": int(sum(dictionary.oov_counter.values())),
            "unique_tokens": len(dictionary.oov_counter),
            "top_tokens": dictionary.oov_counter.most_common(25),
        },
    }


def load_dictionary(path: Path) -> dict[str, int]:
    values = {}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle, start=1):
            token = line.strip()
            if token:
                values[token] = index
    return values


def load_torch_model(model_path: Path) -> torch.nn.Module:
    try:
        model = torch.load(model_path, map_location="cpu", weights_only=False)
    except TypeError:
        model = torch.load(model_path, map_location="cpu")
    model.eval()
    return model


def generate_features(model: torch.nn.Module, dataset: Any, batch_size: int) -> dict[tuple[str, str], torch.Tensor]:
    index, file, pre, post, seq_len, mask_matrix, max_len = dataset.all_file_data()
    features: dict[tuple[str, str], torch.Tensor] = {}
    with torch.no_grad():
        for start in range(0, len(file), batch_size):
            end = min(start + batch_size, len(file))
            current_batch_size = end - start
            pre_tensor = torch.LongTensor(pre[start:end]).view(current_batch_size, max_len)
            post_tensor = torch.LongTensor(post[start:end]).view(current_batch_size, max_len)
            seq_tensor = torch.LongTensor(seq_len[start:end]).view(current_batch_size)
            mask_tensor = torch.LongTensor(mask_matrix[start:end]).view(current_batch_size, max_len)
            batch_features = model.feature_gen(pre_tensor, post_tensor, seq_tensor, mask_tensor)
            for offset in range(current_batch_size):
                features[(str(index[start + offset]), str(file[start + offset]))] = batch_features[offset].detach().cpu()
    return features


def score_pairs(features: dict[tuple[str, str], torch.Tensor], pair_data: list[dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    rows = []
    for pair_index, pair in enumerate(pair_data, start=1):
        left_key = (str(pair["index1"]), str(pair["file1"]))
        right_key = (str(pair["index2"]), str(pair["file2"]))
        left = features[left_key].unsqueeze(0)
        right = features[right_key].unsqueeze(0)
        score = float(torch.clamp(F.cosine_similarity(left, right), min=0, max=1).item())
        label = int(pair["label"])
        prediction = 1 if score > threshold else 0
        rows.append(
            {
                "pair_index": pair_index,
                "function_id_a": pair["index1"],
                "function_id_b": pair["index2"],
                "file_a": pair["file1"],
                "file_b": pair["file2"],
                "label": label,
                "score": score,
                "prediction": prediction,
                "correct": prediction == label,
            }
        )
    return rows


def write_predictions(rows: list[dict[str, Any]], csv_path: Path, txt_path: Path) -> None:
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "pair_index",
                "function_id_a",
                "function_id_b",
                "file_a",
                "file_b",
                "label",
                "score",
                "prediction",
                "correct",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    txt_path.write_text("\n".join(str(row["prediction"]) for row in rows) + "\n", encoding="utf-8")


def confusion_from_predictions(rows: list[dict[str, Any]]) -> dict[str, int]:
    tp = sum(1 for row in rows if row["label"] == 1 and row["prediction"] == 1)
    tn = sum(1 for row in rows if row["label"] == 0 and row["prediction"] == 0)
    fp = sum(1 for row in rows if row["label"] == 0 and row["prediction"] == 1)
    fn = sum(1 for row in rows if row["label"] == 1 and row["prediction"] == 0)
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}


def metrics_from_confusion(confusion: dict[str, int]) -> dict[str, float]:
    tp = confusion["tp"]
    tn = confusion["tn"]
    fp = confusion["fp"]
    fn = confusion["fn"]
    total = tp + tn + fp + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / total if total else 0.0
    return {
        "accuracy": round(accuracy, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }


def render_markdown(summary: dict[str, Any]) -> str:
    metrics = summary.get("metrics") or {}
    confusion = summary.get("confusion") or {}
    rows = summary.get("rows") or {}
    oov = summary.get("oov") or {}
    parse = summary.get("parse") or {}
    return "\n".join(
        [
            "# MRT-OAST HardSet BCB-Model Evaluation",
            "",
            f"Status: `{summary.get('status')}`",
            "",
            str(summary.get("table_policy") or ""),
            "",
            "| Item | Value |",
            "| --- | ---: |",
            f"| functions | {rows.get('functions', '')} |",
            f"| pairs | {rows.get('pairs', '')} |",
            f"| predictions | {rows.get('predictions', '')} |",
            f"| parsed functions | {parse.get('parsed_functions', '')} |",
            f"| parse failures | {len(parse.get('parse_failures') or [])} |",
            f"| dropped pairs | {len(parse.get('dropped_pairs') or [])} |",
            f"| OOV token occurrences | {oov.get('token_occurrences', '')} |",
            f"| unique OOV tokens | {oov.get('unique_tokens', '')} |",
            f"| TP | {confusion.get('tp', '')} |",
            f"| TN | {confusion.get('tn', '')} |",
            f"| FP | {confusion.get('fp', '')} |",
            f"| FN | {confusion.get('fn', '')} |",
            f"| accuracy | {metrics.get('accuracy', '')} |",
            f"| precision | {metrics.get('precision', '')} |",
            f"| recall | {metrics.get('recall', '')} |",
            f"| f1 | {metrics.get('f1', '')} |",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
