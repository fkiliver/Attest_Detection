from __future__ import annotations

import argparse
import json
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
                raise ValueError(f"expected object at {path}:{line_no}")
            rows.append(value)
    return rows


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


def prepare_dataset(*, hardset_dir: Path, output_dir: Path, dataset_name: str) -> dict[str, Any]:
    code_rows = read_jsonl(hardset_dir / "data.jsonl")
    pair_meta_rows = read_jsonl(hardset_dir / "pairs.jsonl")
    triplets = read_triplets(hardset_dir / "test.txt")

    code_by_id = {str(row.get("idx")): str(row.get("func") or "") for row in code_rows}
    meta_by_pair = {
        (str(row.get("function_id_a")), str(row.get("function_id_b"))): row for row in pair_meta_rows
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    split_dir = output_dir / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = output_dir / "pairs.jsonl"
    split_path = split_dir / "test.jsonl"
    with dataset_path.open("w", encoding="utf-8", newline="\n") as pair_sink, split_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as split_sink:
        for pair_id, (function_id_a, function_id_b, label) in enumerate(triplets, start=1):
            if function_id_a not in code_by_id:
                raise ValueError(f"missing code for function_id_a={function_id_a}")
            if function_id_b not in code_by_id:
                raise ValueError(f"missing code for function_id_b={function_id_b}")
            meta = meta_by_pair.get((function_id_a, function_id_b)) or meta_by_pair.get((function_id_b, function_id_a)) or {}
            row = {
                "pair_id": pair_id,
                "function_id_a": function_id_a,
                "function_id_b": function_id_b,
                "functionality_id": "",
                "functionality_name": "CodeXGLUE BigCloneBench",
                "functionality_description": "Original CodeXGLUE BigCloneBench pair without target-function metadata.",
                "source": dataset_name,
                "label": label,
                "code_a": code_by_id[function_id_a],
                "code_b": code_by_id[function_id_b],
                "bcb_type": "",
                "syntactic_type": "",
                "search_heuristic": "eviclone_hardset_gcb_corrected",
                "original_hardset": {
                    "hardset_row": meta.get("hardset_row", pair_id),
                    "source_case_id": meta.get("source_case_id"),
                    "source_pair_id": meta.get("source_pair_id"),
                    "selection_basis": meta.get("selection_basis"),
                    "probe_mode": meta.get("probe_mode"),
                    "risk_tier": meta.get("risk_tier"),
                },
            }
            pair_sink.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            split_sink.write(json.dumps({"pair_id": pair_id}, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "schema_version": "eviclone-llm-direct-hardset-input/v1",
        "status": "prepared",
        "dataset_name": dataset_name,
        "hardset_dir": str(hardset_dir),
        "output_dir": str(output_dir),
        "dataset": str(dataset_path),
        "split_dir": str(split_dir),
        "split": "test",
        "rows": len(triplets),
        "function_rows": len(code_rows),
        "runner": "scripts/run_llm_unordered.py",
        "llm_direct_protocol": "configured LLM LLM-as-judge, no dynamic execution, policy=bcb-alignment",
        "run_command": (
            "python scripts\\run_llm_unordered.py "
            f"--dataset {dataset_path} "
            f"--split-dir {split_dir} "
            "--splits test "
            f"--output {output_dir / 'llm_direct_cards.jsonl'} "
            f"--report-path {output_dir / 'llm_direct_cards.report.md'} "
            "--workers 4 --policy bcb-alignment --llm-retries 1 --timeout-sec 90 "
            "--model configured-llm --base-url https://llm-provider.example/v1 --api-key-env LLM_API_KEY "
            "--temperature 0 --max-tokens 2048 --thinking-type disabled"
        ),
        "postprocess_commands": [
            (
                "python scripts\\export_llm_direct_predictions_from_cards.py "
                f"--cards {output_dir / 'llm_direct_cards.jsonl'} "
                f"--gold {hardset_dir / 'test.txt'} "
                f"--output {hardset_dir / 'llm_direct_predictions.txt'} "
                f"--summary-path {hardset_dir / 'llm_direct_predictions.summary.json'} "
                "--abstain-label 0"
            ),
            (
                "python scripts\\evaluate_triplet_predictions.py "
                f"--gold {hardset_dir / 'test.txt'} "
                f"--predictions {hardset_dir / 'llm_direct_predictions.txt'} "
                f"--output {hardset_dir / 'llm_direct_metrics.json'} "
                f"--report {hardset_dir / 'llm_direct_metrics.md'} "
                "--dataset EviClone-HardSet-GCB-Corrected --method LLM-direct "
                "--source configured-llm"
            ),
        ],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(render_readme(summary), encoding="utf-8")
    return summary


def render_readme(summary: dict[str, Any]) -> str:
    commands = "\n\n".join(f"```powershell\n{cmd}\n```" for cmd in [summary["run_command"], *summary["postprocess_commands"]])
    return "\n".join(
        [
            f"# {summary['dataset_name']} LLM-Direct Input",
            "",
            "Prepared input for the existing configured LLM LLM-direct runner.",
            "",
            f"- Dataset: `{summary['dataset']}`",
            f"- Split dir: `{summary['split_dir']}`",
            f"- Rows: {summary['rows']}",
            f"- Protocol: {summary['llm_direct_protocol']}",
            "",
            "## Commands",
            "",
            commands,
            "",
            "No online model call is performed by this preparation step.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare EviClone HardSet input for LLM-direct evaluation.")
    parser.add_argument("--hardset-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-name", default="EviClone-HardSet-GCB-Corrected")
    args = parser.parse_args()

    summary = prepare_dataset(
        hardset_dir=args.hardset_dir,
        output_dir=args.output_dir,
        dataset_name=args.dataset_name,
    )
    print(json.dumps({"status": summary["status"], "rows": summary["rows"], "dataset": summary["dataset"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
