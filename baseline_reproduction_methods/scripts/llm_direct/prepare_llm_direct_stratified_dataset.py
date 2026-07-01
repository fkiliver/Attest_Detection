from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_no}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"expected JSON object at {path}:{line_no}")
            rows.append(value)
    return rows


def read_triplets(path: Path) -> list[tuple[str, str, int, int]]:
    rows: list[tuple[str, str, int, int]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            parts = text.replace(",", " ").split()
            if len(parts) < 3:
                raise ValueError(f"expected id_a id_b label at {path}:{line_no}")
            label = parse_label(parts[2], path=path, line_no=line_no)
            rows.append((parts[0], parts[1], label, line_no))
    return rows


def parse_label(value: str, *, path: Path, line_no: int) -> int:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "clone", "positive"}:
        return 1
    if normalized in {"0", "-1", "false", "nonclone", "non-clone", "negative"}:
        return 0
    raise ValueError(f"invalid binary label at {path}:{line_no}: {value!r}")


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_stratified(
    rows: list[tuple[str, str, int, int]],
    *,
    per_label: int,
    seed: int,
) -> list[tuple[str, str, int, int]]:
    if per_label <= 0:
        raise ValueError("per_label must be positive")
    by_label: dict[int, list[tuple[str, str, int, int]]] = {0: [], 1: []}
    for row in rows:
        by_label[row[2]].append(row)
    rng = random.Random(seed)
    selected: list[tuple[str, str, int, int]] = []
    for label in (0, 1):
        candidates = list(by_label[label])
        if len(candidates) < per_label:
            raise ValueError(
                f"not enough rows for label {label}: requested {per_label}, found {len(candidates)}"
            )
        selected.extend(rng.sample(candidates, per_label))
    selected.sort(key=lambda row: (row[2], row[3], row[0], row[1]))
    return selected


def code_stats(values: list[str]) -> dict[str, Any]:
    lengths = sorted(len(value) for value in values)
    if not lengths:
        return {"count": 0}
    return {
        "count": len(lengths),
        "min_chars": lengths[0],
        "median_chars": lengths[len(lengths) // 2],
        "max_chars": lengths[-1],
    }


def prepare_dataset(
    *,
    input_dir: Path,
    output_dir: Path,
    dataset_name: str,
    split_name: str,
    per_label: int,
    seed: int,
    policy: str,
) -> dict[str, Any]:
    data_path = input_dir / "data.jsonl"
    split_path = input_dir / f"{split_name}.txt"
    code_rows = read_jsonl(data_path)
    triplets = read_triplets(split_path)
    selected = select_stratified(triplets, per_label=per_label, seed=seed)
    code_by_id = {str(row.get("idx")): str(row.get("func") or "") for row in code_rows}

    output_dir.mkdir(parents=True, exist_ok=True)
    split_dir = output_dir / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = output_dir / "pairs.jsonl"
    sampled_gold_path = output_dir / f"{split_name}.txt"
    selected_rows_path = output_dir / "selected_rows.jsonl"
    split_jsonl_path = split_dir / f"{split_name}.jsonl"

    labels: Counter[int] = Counter()
    code_values: list[str] = []
    with dataset_path.open("w", encoding="utf-8", newline="\n") as pair_sink, split_jsonl_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as split_sink, sampled_gold_path.open("w", encoding="utf-8", newline="\n") as gold_sink, selected_rows_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as selected_sink:
        for pair_id, (id_a, id_b, label, source_row) in enumerate(selected, start=1):
            if id_a not in code_by_id:
                raise ValueError(f"missing code for id_a={id_a}")
            if id_b not in code_by_id:
                raise ValueError(f"missing code for id_b={id_b}")
            code_a = code_by_id[id_a]
            code_b = code_by_id[id_b]
            labels[label] += 1
            code_values.extend([code_a, code_b])
            row = {
                "pair_id": pair_id,
                "function_id_a": id_a,
                "function_id_b": id_b,
                "functionality_id": "",
                "functionality_name": dataset_name,
                "functionality_description": (
                    f"{dataset_name} {split_name} split pair sampled for an LLM-direct "
                    "clone/non-clone judgment pilot."
                ),
                "source": f"{dataset_name}-{split_name}-stratified-per-label-{per_label}",
                "label": label,
                "code_a": code_a,
                "code_b": code_b,
                "bcb_type": "",
                "syntactic_type": "",
                "search_heuristic": "stratified_random_by_gold_label",
                "sample_metadata": {
                    "input_dir": str(input_dir),
                    "split_name": split_name,
                    "source_row": source_row,
                    "seed": seed,
                    "per_label": per_label,
                },
            }
            pair_sink.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            split_sink.write(json.dumps({"pair_id": pair_id}, ensure_ascii=False, sort_keys=True) + "\n")
            gold_sink.write(f"{id_a}\t{id_b}\t{label}\n")
            selected_sink.write(
                json.dumps(
                    {
                        "pair_id": pair_id,
                        "function_id_a": id_a,
                        "function_id_b": id_b,
                        "label": label,
                        "source_row": source_row,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    summary = {
        "schema_version": "eviclone-llm-direct-stratified-input/v1",
        "status": "prepared",
        "dataset_name": dataset_name,
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "source_data_jsonl": str(data_path),
        "source_split": str(split_path),
        "source_data_jsonl_sha256": file_sha256(data_path),
        "source_split_sha256": file_sha256(split_path),
        "dataset": str(dataset_path),
        "split_dir": str(split_dir),
        "split": split_name,
        "sampled_gold": str(sampled_gold_path),
        "selected_rows": str(selected_rows_path),
        "rows": len(selected),
        "label_counts": {"0": int(labels[0]), "1": int(labels[1])},
        "sampling": {
            "type": "stratified_random_by_gold_label",
            "per_label": per_label,
            "seed": seed,
            "source_rows": len(triplets),
            "source_label_counts": {str(k): int(v) for k, v in sorted(Counter(row[2] for row in triplets).items())},
        },
        "code_stats": code_stats(code_values),
        "runner": "scripts/run_llm_unordered.py",
        "llm_direct_protocol": f"configured LLM LLM-as-judge, no dynamic execution, policy={policy}",
        "run_command": (
            "python scripts\\run_llm_unordered.py "
            f"--dataset {dataset_path} "
            f"--split-dir {split_dir} "
            f"--splits {split_name} "
            f"--output {output_dir / 'llm_direct_cards.jsonl'} "
            f"--report-path {output_dir / 'llm_direct_cards.report.md'} "
            "--workers 4 "
            f"--policy {policy} "
            "--llm-retries 1 --timeout-sec 90 "
            "--model configured-llm --base-url https://llm-provider.example/v1 "
            "--api-key-env LLM_API_KEY --temperature 0 --max-tokens 2048 "
            "--thinking-type disabled"
        ),
        "postprocess_commands": [
            (
                "python scripts\\export_llm_direct_predictions_from_cards.py "
                f"--cards {output_dir / 'llm_direct_cards.jsonl'} "
                f"--gold {sampled_gold_path} "
                f"--output {output_dir / 'llm_direct_predictions.txt'} "
                f"--summary-path {output_dir / 'llm_direct_predictions.summary.json'} "
                "--abstain-label 0"
            ),
            (
                "python scripts\\evaluate_triplet_predictions.py "
                f"--gold {sampled_gold_path} "
                f"--predictions {output_dir / 'llm_direct_predictions.txt'} "
                f"--output {output_dir / 'llm_direct_metrics.json'} "
                f"--report {output_dir / 'llm_direct_metrics.md'} "
                f"--dataset {dataset_name}-stratified-pilot "
                "--method LLM-direct --source configured-llm"
            ),
        ],
        "table_use_note": (
            "This is a balanced stratified pilot input package for LLM-direct evaluation. "
            "Do not use it as a natural-distribution full-test F1 cell."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(render_readme(summary), encoding="utf-8")
    return summary


def render_readme(summary: dict[str, Any]) -> str:
    commands = "\n\n".join(
        f"```powershell\n{cmd}\n```" for cmd in [summary["run_command"], *summary["postprocess_commands"]]
    )
    return "\n".join(
        [
            f"# {summary['dataset_name']} LLM-Direct Stratified Pilot Input",
            "",
            "Prepared input for the existing configured LLM LLM-direct runner.",
            "",
            f"- Dataset: `{summary['dataset']}`",
            f"- Split dir: `{summary['split_dir']}`",
            f"- Sampled gold: `{summary['sampled_gold']}`",
            f"- Rows: {summary['rows']}",
            f"- Label counts: {summary['label_counts']}",
            f"- Sampling: {summary['sampling']}",
            "",
            "## Commands",
            "",
            commands,
            "",
            "No online model call is performed by this preparation step. Provide the API key through `LLM_API_KEY` only.",
            "",
            f"Table-use note: {summary['table_use_note']}",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a balanced stratified input package for LLM-direct clone judgment."
    )
    parser.add_argument("--input-dir", type=Path, required=True, help="Directory with data.jsonl and <split>.txt")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--split", default="test")
    parser.add_argument("--per-label", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--policy", default="bcb-alignment")
    args = parser.parse_args()

    summary = prepare_dataset(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        dataset_name=args.dataset_name,
        split_name=args.split,
        per_label=args.per_label,
        seed=args.seed,
        policy=args.policy,
    )
    print(
        json.dumps(
            {
                "status": summary["status"],
                "dataset": summary["dataset"],
                "rows": summary["rows"],
                "label_counts": summary["label_counts"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
