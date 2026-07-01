from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_INPUTS = {
    "BCB": Path("eviclone_runs") / "codexglue_original",
    "OJClone": Path("eviclone_runs") / "baseline_reproduction" / "graphcodebert_dsfm_splits" / "OJClone",
    "GCJ": Path("eviclone_runs") / "baseline_reproduction" / "graphcodebert_dsfm_splits" / "GCJ",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare natural-distribution full-test inputs for LLM-direct.")
    parser.add_argument("--output-root", type=Path, default=Path("eviclone_runs") / "baseline_reproduction" / "llm_direct_fulltest")
    parser.add_argument("--datasets", default="BCB,OJClone,GCJ")
    parser.add_argument("--split", default="test")
    parser.add_argument("--policy", default="bcb-alignment")
    parser.add_argument("--shard-size", type=int, default=5000)
    parser.add_argument("--model", default="configured-llm")
    parser.add_argument("--base-url", default="https://llm-provider.example/v1")
    parser.add_argument("--api-key-env", default="LLM_API_KEY")
    args = parser.parse_args()

    selected = [item.strip() for item in args.datasets.split(",") if item.strip()]
    summaries = []
    for dataset in selected:
        if dataset not in DEFAULT_INPUTS:
            raise ValueError(f"unknown dataset {dataset!r}; expected one of {sorted(DEFAULT_INPUTS)}")
        summaries.append(
            prepare_dataset(
                input_dir=DEFAULT_INPUTS[dataset],
                output_dir=args.output_root / dataset,
                dataset_name=dataset,
                split_name=args.split,
                policy=args.policy,
                shard_size=args.shard_size,
                model=args.model,
                base_url=args.base_url,
                api_key_env=args.api_key_env,
            )
        )
    suite = {
        "schema_version": "eviclone-llm-direct-fulltest-suite-input/v1",
        "status": "prepared",
        "output_root": str(args.output_root),
        "datasets": summaries,
        "total_rows": sum(int(item["rows"]) for item in summaries),
        "total_shards": sum(int(item["shards"]["count"]) for item in summaries),
        "api_key_env": args.api_key_env,
        "api_key_handling": (
            f"Only the environment variable name {args.api_key_env} is stored. The secret value must never be "
            "written into commands, logs, reports, JSON, or shell history."
        ),
        "table_use_note": (
            "This is a natural-distribution full-test input package for future online LLM-direct execution. It is "
            "not a completed LLM result until every shard has retained cards, prompt/output snapshots, exported "
            "predictions, and A/P/R/F1 metrics."
        ),
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "suite_summary.json").write_text(
        json.dumps(suite, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_root / "README.md").write_text(render_suite_readme(suite), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": suite["status"],
                "datasets": len(summaries),
                "total_rows": suite["total_rows"],
                "total_shards": suite["total_shards"],
                "output_root": str(args.output_root),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


def prepare_dataset(
    *,
    input_dir: Path,
    output_dir: Path,
    dataset_name: str,
    split_name: str,
    policy: str,
    shard_size: int,
    model: str,
    base_url: str,
    api_key_env: str,
) -> dict[str, Any]:
    if shard_size <= 0:
        raise ValueError("shard_size must be positive")
    data_path = input_dir / "data.jsonl"
    split_path = input_dir / f"{split_name}.txt"
    code_by_id = read_code_map(data_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    split_dir = output_dir / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    shard_root = output_dir / "shards"
    shard_root.mkdir(parents=True, exist_ok=True)

    dataset_path = output_dir / "pairs.jsonl"
    full_split_jsonl = split_dir / f"{split_name}.jsonl"
    gold_path = output_dir / f"{split_name}.txt"
    selected_rows_path = output_dir / "selected_rows.jsonl"

    labels: Counter[int] = Counter()
    pair_count = 0
    code_lengths: list[int] = []
    shard_handles: dict[int, Any] = {}
    shard_rows: Counter[int] = Counter()
    try:
        with dataset_path.open("w", encoding="utf-8", newline="\n") as pair_sink, full_split_jsonl.open(
            "w", encoding="utf-8", newline="\n"
        ) as split_sink, gold_path.open("w", encoding="utf-8", newline="\n") as gold_sink, selected_rows_path.open(
            "w", encoding="utf-8", newline="\n"
        ) as selected_sink:
            for source_row, (id_a, id_b, label) in enumerate(read_triplets(split_path), start=1):
                code_a = require_code(code_by_id, id_a, data_path=data_path, source_row=source_row)
                code_b = require_code(code_by_id, id_b, data_path=data_path, source_row=source_row)
                pair_count += 1
                labels[label] += 1
                code_lengths.extend([len(code_a), len(code_b)])
                row = {
                    "pair_id": pair_count,
                    "function_id_a": id_a,
                    "function_id_b": id_b,
                    "functionality_id": "",
                    "functionality_name": dataset_name,
                    "functionality_description": (
                        f"{dataset_name} {split_name} full-test pair for an LLM-direct clone/non-clone judgment."
                    ),
                    "source": f"{dataset_name}-{split_name}-fulltest",
                    "label": label,
                    "code_a": code_a,
                    "code_b": code_b,
                    "bcb_type": "",
                    "syntactic_type": "",
                    "search_heuristic": "full_natural_distribution",
                    "sample_metadata": {
                        "input_dir": str(input_dir),
                        "split_name": split_name,
                        "source_row": source_row,
                    },
                }
                pair_sink.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                split_record = {"pair_id": pair_count}
                split_sink.write(json.dumps(split_record, ensure_ascii=False, sort_keys=True) + "\n")
                shard_id = (pair_count - 1) // shard_size + 1
                shard_handle = shard_handles.get(shard_id)
                if shard_handle is None:
                    shard_dir = shard_root / f"shard_{shard_id:04d}"
                    shard_dir.mkdir(parents=True, exist_ok=True)
                    shard_handle = (shard_dir / f"{split_name}.jsonl").open("w", encoding="utf-8", newline="\n")
                    shard_handles[shard_id] = shard_handle
                shard_handle.write(json.dumps(split_record, ensure_ascii=False, sort_keys=True) + "\n")
                shard_rows[shard_id] += 1
                gold_sink.write(f"{id_a}\t{id_b}\t{label}\n")
                selected_sink.write(
                    json.dumps(
                        {
                            "pair_id": pair_count,
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
    finally:
        for handle in shard_handles.values():
            handle.close()

    shard_manifest = write_shard_manifest(
        output_dir=output_dir,
        shard_root=shard_root,
        split_name=split_name,
        shard_rows=shard_rows,
        dataset_path=dataset_path,
        policy=policy,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
    )
    summary = {
        "schema_version": "eviclone-llm-direct-fulltest-input/v1",
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
        "gold": str(gold_path),
        "selected_rows": str(selected_rows_path),
        "rows": pair_count,
        "label_counts": {"0": int(labels[0]), "1": int(labels[1])},
        "code_stats": code_stats(code_lengths),
        "shards": shard_manifest,
        "runner": "scripts/run_llm_unordered.py",
        "llm_direct_protocol": f"configured LLM LLM-as-judge, no dynamic execution, policy={policy}",
        "full_run_command": run_command(
            dataset_path=dataset_path,
            split_dir=split_dir,
            split_name=split_name,
            output_path=output_dir / "llm_direct_cards.jsonl",
            report_path=output_dir / "llm_direct_cards.report.md",
            policy=policy,
            model=model,
            base_url=base_url,
            api_key_env=api_key_env,
        ),
        "postprocess_commands": postprocess_commands(
            output_dir=output_dir,
            gold_path=gold_path,
            dataset_name=dataset_name,
            model=model,
        ),
        "table_use_note": (
            "This is a full-test input package. Do not use it as an LLM-direct metric cell until retained online "
            "cards, prompt/output snapshots, exported predictions, and metrics are complete."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(render_dataset_readme(summary), encoding="utf-8")
    return summary


def read_code_map(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                continue
            row = json.loads(text)
            if not isinstance(row, dict):
                raise ValueError(f"expected JSON object at {path}:{line_no}")
            idx = str(row.get("idx"))
            result[idx] = str(row.get("func") or "")
    return result


def read_triplets(path: Path) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as source:
        for line_no, line in enumerate(source, start=1):
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            parts = text.replace(",", " ").split()
            if len(parts) < 3:
                raise ValueError(f"expected id_a id_b label at {path}:{line_no}")
            rows.append((parts[0], parts[1], parse_label(parts[2], path=path, line_no=line_no)))
    return rows


def parse_label(value: str, *, path: Path, line_no: int) -> int:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "clone", "positive"}:
        return 1
    if normalized in {"0", "-1", "false", "nonclone", "non-clone", "negative"}:
        return 0
    raise ValueError(f"invalid binary label at {path}:{line_no}: {value!r}")


def require_code(code_by_id: dict[str, str], key: str, *, data_path: Path, source_row: int) -> str:
    if key not in code_by_id:
        raise ValueError(f"missing code id={key} referenced from split row {source_row}; data={data_path}")
    return code_by_id[key]


def write_shard_manifest(
    *,
    output_dir: Path,
    shard_root: Path,
    split_name: str,
    shard_rows: Counter[int],
    dataset_path: Path,
    policy: str,
    model: str,
    base_url: str,
    api_key_env: str,
) -> dict[str, Any]:
    records = []
    for shard_id in sorted(shard_rows):
        shard_dir = shard_root / f"shard_{shard_id:04d}"
        split_dir = shard_dir
        output_path = shard_dir / "llm_direct_cards.jsonl"
        report_path = shard_dir / "llm_direct_cards.report.md"
        records.append(
            {
                "shard_id": shard_id,
                "rows": int(shard_rows[shard_id]),
                "split_dir": str(split_dir),
                "split_jsonl": str(split_dir / f"{split_name}.jsonl"),
                "output_cards": str(output_path),
                "report": str(report_path),
                "run_command": run_command(
                    dataset_path=dataset_path,
                    split_dir=split_dir,
                    split_name=split_name,
                    output_path=output_path,
                    report_path=report_path,
                    policy=policy,
                    model=model,
                    base_url=base_url,
                    api_key_env=api_key_env,
                ),
            }
        )
    manifest = {
        "root": str(shard_root),
        "count": len(records),
        "shard_size": max(shard_rows.values()) if records else 0,
        "records": records,
    }
    (output_dir / "shard_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def run_command(
    *,
    dataset_path: Path,
    split_dir: Path,
    split_name: str,
    output_path: Path,
    report_path: Path,
    policy: str,
    model: str,
    base_url: str,
    api_key_env: str,
) -> str:
    return (
        "python scripts\\run_llm_unordered.py "
        f"--dataset {dataset_path} "
        f"--split-dir {split_dir} "
        f"--splits {split_name} "
        f"--output {output_path} "
        f"--report-path {report_path} "
        "--workers 4 "
        f"--policy {policy} "
        "--llm-retries 1 --timeout-sec 90 "
        f"--model {model} --base-url {base_url} "
        f"--api-key-env {api_key_env} --temperature 0 --max-tokens 2048 "
        "--thinking-type disabled"
    )


def postprocess_commands(*, output_dir: Path, gold_path: Path, dataset_name: str, model: str) -> list[str]:
    return [
        (
            "python scripts\\export_llm_direct_predictions_from_cards.py "
            f"--cards {output_dir / 'llm_direct_cards.jsonl'} "
            f"--gold {gold_path} "
            f"--output {output_dir / 'llm_direct_predictions.txt'} "
            f"--summary-path {output_dir / 'llm_direct_predictions.summary.json'} "
            "--abstain-label 0 --decision-source llm_bcb_gold"
        ),
        (
            "python scripts\\evaluate_triplet_predictions.py "
            f"--gold {gold_path} "
            f"--predictions {output_dir / 'llm_direct_predictions.txt'} "
            f"--output {output_dir / 'llm_direct_metrics.json'} "
            f"--report {output_dir / 'llm_direct_metrics.md'} "
            f"--dataset {dataset_name}-fulltest "
            f"--method LLM-direct --source {model}"
        ),
    ]


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def code_stats(lengths: list[int]) -> dict[str, Any]:
    ordered = sorted(lengths)
    if not ordered:
        return {"count": 0}
    return {
        "count": len(ordered),
        "min_chars": ordered[0],
        "median_chars": ordered[len(ordered) // 2],
        "max_chars": ordered[-1],
    }


def render_dataset_readme(summary: dict[str, Any]) -> str:
    shard_preview = "\n".join(
        f"- shard_{row['shard_id']:04d}: {row['rows']} rows"
        for row in summary["shards"]["records"][:10]
    )
    if summary["shards"]["count"] > 10:
        shard_preview += f"\n- ... {summary['shards']['count'] - 10} more shards"
    commands = "\n\n".join(
        f"```powershell\n{cmd}\n```" for cmd in [summary["full_run_command"], *summary["postprocess_commands"]]
    )
    return "\n".join(
        [
            f"# {summary['dataset_name']} LLM-Direct Full-Test Input",
            "",
            "Prepared input for the existing configured LLM LLM-direct runner.",
            "",
            f"- Dataset: `{summary['dataset']}`",
            f"- Split dir: `{summary['split_dir']}`",
            f"- Gold: `{summary['gold']}`",
            f"- Rows: {summary['rows']}",
            f"- Label counts: {summary['label_counts']}",
            f"- Shards: {summary['shards']['count']}",
            "",
            "## Shard Preview",
            "",
            shard_preview,
            "",
            "## Commands",
            "",
            commands,
            "",
            "No online model call is performed by this preparation step. Provide the API key through the configured environment variable only.",
            "",
            f"Table-use note: {summary['table_use_note']}",
            "",
        ]
    )


def render_suite_readme(suite: dict[str, Any]) -> str:
    lines = [
        "# LLM-Direct Full-Test Input Suite",
        "",
        suite["table_use_note"],
        "",
        suite["api_key_handling"],
        "",
        "| Dataset | Rows | Positives | Negatives | Shards |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in suite["datasets"]:
        labels = item["label_counts"]
        lines.append(
            f"| {item['dataset_name']} | {item['rows']} | {labels.get('1', 0)} | {labels.get('0', 0)} | {item['shards']['count']} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
