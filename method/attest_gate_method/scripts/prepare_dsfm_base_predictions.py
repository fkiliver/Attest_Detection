from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from attest_gate.config import DEFAULT_BASE_MODEL
from attest_gate.dynamic_router import coerce_label, coerce_optional_float


ID_A_KEYS = (
    "function_id_a",
    "id_a",
    "code_id_a",
    "method_id_a",
    "func_id_a",
    "function1",
    "id1",
    "code1",
    "func1",
    "f1",
)
ID_B_KEYS = (
    "function_id_b",
    "id_b",
    "code_id_b",
    "method_id_b",
    "func_id_b",
    "function2",
    "id2",
    "code2",
    "func2",
    "f2",
)
LABEL_KEYS = (
    "dsfm_prediction",
    "dsfm_label",
    "prediction",
    "predicted_label",
    "label",
    "pred",
    "y_pred",
    "is_clone",
    "clone",
)
CONFIDENCE_KEYS = (
    "dsfm_confidence",
    "confidence",
    "base_confidence",
    "score",
    "probability",
    "prob",
    "positive_probability",
    "p_clone",
)
MARGIN_KEYS = ("dsfm_margin", "margin", "base_margin")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize DSFM prediction exports into the Attest base prediction format."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-path", type=Path, default=None)
    parser.add_argument("--format", choices=["auto", "jsonl", "csv", "tsv", "triplet"], default="auto")
    parser.add_argument("--source", type=str, default=DEFAULT_BASE_MODEL)
    parser.add_argument("--threshold", type=float, default=0.5, help="threshold used when only a probability is available")
    args = parser.parse_args()

    summary = prepare_dsfm_base_predictions(
        input_path=args.input,
        output_path=args.output,
        input_format=args.format,
        source=args.source,
        threshold=args.threshold,
    )
    summary_path = args.summary_path or args.output.with_suffix(".summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "rows": summary["rows"], "output": str(args.output)}, ensure_ascii=False))
    return 0 if summary["status"] == "prepared" else 1


def prepare_dsfm_base_predictions(
    *,
    input_path: Path,
    output_path: Path,
    input_format: str = "auto",
    source: str = DEFAULT_BASE_MODEL,
    threshold: float = 0.5,
) -> dict[str, Any]:
    if not input_path.exists():
        raise FileNotFoundError(f"DSFM prediction input not found: {input_path}")
    rows = list(read_rows(input_path, input_format=input_format, threshold=threshold))
    if not rows:
        raise ValueError(f"no usable prediction rows found in {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    positives = 0
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            positives += int(row["label"] == 1)
            values = [row["function_id_a"], row["function_id_b"], str(row["label"])]
            confidence = row.get("confidence")
            margin = row.get("margin")
            if confidence is not None or margin is not None:
                values.append(format_float(confidence) if confidence is not None else "NA")
            if margin is not None:
                values.append(format_float(margin))
            handle.write(" ".join(values) + "\n")

    return {
        "schema_version": "attest-dsfm-base-prediction-adapter/v1",
        "status": "prepared",
        "base_model": source,
        "input": str(input_path.resolve()),
        "output": str(output_path.resolve()),
        "rows": len(rows),
        "positive_predictions": positives,
        "negative_predictions": len(rows) - positives,
        "output_format": "function_id_a function_id_b label [confidence] [margin]",
        "compatible_loader": "attest_gate.dynamic_router.load_base_predictions",
    }


def read_rows(input_path: Path, *, input_format: str, threshold: float) -> Iterable[dict[str, Any]]:
    fmt = detect_format(input_path, input_format)
    if fmt == "jsonl":
        yield from read_jsonl_rows(input_path, threshold=threshold)
    elif fmt in {"csv", "tsv"}:
        delimiter = "," if fmt == "csv" else "\t"
        yield from read_delimited_rows(input_path, delimiter=delimiter, threshold=threshold)
    else:
        yield from read_triplet_rows(input_path, threshold=threshold)


def detect_format(input_path: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    suffix = input_path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    if suffix == ".tsv":
        return "tsv"
    return "triplet"


def read_jsonl_rows(path: Path, *, threshold: float) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_no}: {exc}") from exc
            yield normalize_mapping_row(obj, threshold=threshold, context=f"{path}:{line_no}")


def read_delimited_rows(path: Path, *, delimiter: str, threshold: float) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        has_header = csv.Sniffer().has_header(sample) if sample.strip() else False
        if has_header:
            reader = csv.DictReader(handle, delimiter=delimiter)
            for line_no, obj in enumerate(reader, start=2):
                yield normalize_mapping_row(obj, threshold=threshold, context=f"{path}:{line_no}")
        else:
            reader = csv.reader(handle, delimiter=delimiter)
            for line_no, parts in enumerate(reader, start=1):
                if not parts or not any(part.strip() for part in parts):
                    continue
                yield normalize_triplet_parts(parts, threshold=threshold, context=f"{path}:{line_no}")


def read_triplet_rows(path: Path, *, threshold: float) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            parts = re.split(r"[\s,]+", text)
            yield normalize_triplet_parts(parts, threshold=threshold, context=f"{path}:{line_no}")


def normalize_mapping_row(obj: dict[str, Any], *, threshold: float, context: str) -> dict[str, Any]:
    lowered = {str(key).strip().lower(): value for key, value in obj.items()}
    function_id_a = first_value(lowered, ID_A_KEYS)
    function_id_b = first_value(lowered, ID_B_KEYS)
    if function_id_a is None or function_id_b is None:
        raise ValueError(f"missing pair identifiers in {context}")

    raw_label = first_value(lowered, LABEL_KEYS)
    probability = coerce_optional_float(first_value(lowered, CONFIDENCE_KEYS))
    label = coerce_label(raw_label)
    if label not in (0, 1) and probability is not None:
        label = 1 if probability >= threshold else 0
    if label not in (0, 1):
        raise ValueError(f"missing binary prediction label in {context}")

    confidence = probability
    if confidence is not None and confidence < 0.5:
        confidence = 1.0 - confidence
    margin = coerce_optional_float(first_value(lowered, MARGIN_KEYS))
    if margin is None and probability is not None:
        margin = abs(probability - 0.5) * 2.0
    return {
        "function_id_a": str(function_id_a),
        "function_id_b": str(function_id_b),
        "label": int(label),
        "confidence": confidence,
        "margin": margin,
    }


def normalize_triplet_parts(parts: list[str], *, threshold: float, context: str) -> dict[str, Any]:
    if len(parts) < 3:
        raise ValueError(f"expected at least three columns in {context}")
    if coerce_label(parts[2]) is None and parts[2].strip().lower() in {"label", "prediction", "pred"}:
        raise ValueError(f"header row detected without delimiter/header metadata in {context}")
    label = coerce_label(parts[2])
    confidence = coerce_optional_float(parts[3]) if len(parts) >= 4 else None
    if label not in (0, 1) and confidence is not None:
        label = 1 if confidence >= threshold else 0
    if label not in (0, 1):
        raise ValueError(f"missing binary prediction label in {context}")
    margin = coerce_optional_float(parts[4]) if len(parts) >= 5 else None
    if margin is None and confidence is not None:
        raw_probability = confidence if int(label) == 1 else 1.0 - confidence
        margin = abs(raw_probability - 0.5) * 2.0
    return {
        "function_id_a": parts[0],
        "function_id_b": parts[1],
        "label": int(label),
        "confidence": confidence,
        "margin": margin,
    }


def first_value(mapping: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        normalized = key.lower()
        if normalized in mapping and mapping[normalized] not in (None, ""):
            return mapping[normalized]
    return None


def format_float(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.8f}"


if __name__ == "__main__":
    raise SystemExit(main())
