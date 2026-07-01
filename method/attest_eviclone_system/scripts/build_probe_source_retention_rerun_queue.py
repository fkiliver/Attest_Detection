from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eviclone_prototype.dataset import iter_jsonl  # noqa: E402
from scripts.build_probe_synthesis_plan import DEFAULT_RUN_DIR, sorted_counter  # noqa: E402

DEFAULT_DATASET = DEFAULT_RUN_DIR / "graphcodebert_full_test_errors_eviclone.jsonl"
DEFAULT_CANDIDATES = DEFAULT_RUN_DIR / "probe_synthesis_candidates.jsonl"
DEFAULT_OUTPUT_DIR = DEFAULT_RUN_DIR / "probe_source_retention_rerun_queue"
DEFAULT_SPLIT = "probe_source_retention"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a rerun queue that retains completed EviProbe.java sources.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--split", type=str, default=DEFAULT_SPLIT)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=500)
    parser.add_argument("--dynamic-workers", type=int, default=32)
    parser.add_argument("--model", type=str, default="configured-llm")
    parser.add_argument("--base-url", type=str, default="https://llm-provider.example/v1")
    parser.add_argument("--api-key-env", type=str, default="LLM_API_KEY")
    args = parser.parse_args()

    summary = build_probe_source_retention_rerun_queue(
        dataset=args.dataset,
        candidates_jsonl=args.candidates,
        output_dir=args.output_dir,
        split=args.split,
        limit=args.limit,
        workers=args.workers,
        dynamic_workers=args.dynamic_workers,
        model=args.model,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
    )
    print(json.dumps({"status": summary["status"], "output_dir": str(args.output_dir.resolve())}, ensure_ascii=False))
    return 0 if summary["status"] == "queue_ready" else 2


def build_probe_source_retention_rerun_queue(
    *,
    dataset: Path,
    candidates_jsonl: Path,
    output_dir: Path,
    split: str = DEFAULT_SPLIT,
    limit: int = 0,
    workers: int = 500,
    dynamic_workers: int = 32,
    model: str = "configured-llm",
    base_url: str = "https://llm-provider.example/v1",
    api_key_env: str = "LLM_API_KEY",
) -> dict[str, Any]:
    dataset_rows = load_dataset_rows(dataset)
    candidates = load_candidates(candidates_jsonl)
    if limit:
        candidates = candidates[:limit]

    selected: list[dict[str, Any]] = []
    missing_cases: list[int] = []
    pair_mismatches: list[dict[str, Any]] = []
    duplicate_case_ids = duplicate_values([int_or_none(item.get("case_id")) for item in candidates])
    for candidate in candidates:
        case_id = int_or_none(candidate.get("case_id"))
        if case_id is None or case_id not in dataset_rows:
            if case_id is not None:
                missing_cases.append(case_id)
            continue
        source_row = dataset_rows[case_id]
        expected_pair = tuple(str(x) for x in (candidate.get("pair") or [])[:2])
        actual_pair = (str(source_row.get("function_id_a") or ""), str(source_row.get("function_id_b") or ""))
        if expected_pair and expected_pair != actual_pair:
            pair_mismatches.append({"case_id": case_id, "candidate_pair": list(expected_pair), "dataset_pair": list(actual_pair)})
        selected.append({"candidate": candidate, "dataset": source_row})

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = queue_paths(output_dir, split)
    write_queue_files(paths, selected, split=split)
    summary = summarize_queue(
        dataset=dataset,
        candidates_jsonl=candidates_jsonl,
        output_dir=output_dir,
        split=split,
        selected=selected,
        missing_cases=missing_cases,
        pair_mismatches=pair_mismatches,
        duplicate_case_ids=duplicate_case_ids,
        workers=workers,
        dynamic_workers=dynamic_workers,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        paths=paths,
    )
    paths["summary"].write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    write_report(paths["report"], summary)
    return summary


def load_dataset_rows(path: Path) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for obj in iter_jsonl(path):
        case_id = int_or_none(obj.get("case_id")) or int_or_none(obj.get("pair_id"))
        if case_id is not None:
            rows[case_id] = obj
    return rows


def load_candidates(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [obj for obj in iter_jsonl(path) if isinstance(obj, dict)]


def queue_paths(output_dir: Path, split: str) -> dict[str, Path]:
    return {
        "pairs": output_dir / "pairs.jsonl",
        "split": output_dir / f"{split}.jsonl",
        "txt": output_dir / f"{split}.txt",
        "data": output_dir / "data.jsonl",
        "manifest": output_dir / "candidate_manifest.jsonl",
        "summary": output_dir / "summary.json",
        "report": output_dir / "report.md",
        "context_sources": output_dir / "context_sources",
        "cards": output_dir / "configured_llm_probe_source_retention_cards.jsonl",
        "cards_report": output_dir / "configured_llm_probe_source_retention_cards.report.md",
        "cards_summary": output_dir / "configured_llm_probe_source_retention_cards.summary.json",
    }


def write_queue_files(paths: dict[str, Path], selected: list[dict[str, Any]], *, split: str) -> None:
    used_functions: dict[str, dict[str, str]] = {}
    with paths["pairs"].open("w", encoding="utf-8", newline="\n") as pairs_file, paths["split"].open(
        "w", encoding="utf-8", newline="\n"
    ) as split_file, paths["txt"].open("w", encoding="utf-8", newline="\n") as txt_file, paths["manifest"].open(
        "w", encoding="utf-8", newline="\n"
    ) as manifest_file:
        for item in selected:
            row = item["dataset"]
            candidate = item["candidate"]
            pair_id = int_or_none(row.get("pair_id")) or int_or_none(row.get("case_id")) or int(candidate["case_id"])
            function_id_a = str(row.get("function_id_a") or "")
            function_id_b = str(row.get("function_id_b") or "")
            queue_row = dict(row)
            queue_row.update(
                {
                    "pair_id": pair_id,
                    "case_id": int(candidate["case_id"]),
                    "source": "probe_source_retention_rerun",
                    "split": split,
                    "probe_source_retention": {
                        "generation_route": candidate.get("generation_route"),
                        "probe_mode": candidate.get("probe_mode"),
                        "risk_tier": candidate.get("risk_tier"),
                        "pain_point": candidate.get("pain_point"),
                        "candidate_correct": bool(candidate.get("candidate_correct")),
                        "expected_source_sha256": (candidate.get("context_completion") or {}).get("java_source_sha256"),
                    },
                }
            )
            pairs_file.write(json.dumps(queue_row, ensure_ascii=False) + "\n")
            split_file.write(json.dumps({"pair_id": pair_id}, ensure_ascii=False) + "\n")
            txt_file.write(f"{function_id_a}\t{function_id_b}\t{int(row.get('label', 0))}\n")
            manifest_file.write(json.dumps(compact_manifest_row(candidate, row, pair_id=pair_id), ensure_ascii=False) + "\n")
            used_functions[function_id_a] = {"idx": function_id_a, "func": str(row.get("code_a") or "")}
            used_functions[function_id_b] = {"idx": function_id_b, "func": str(row.get("code_b") or "")}

    with paths["data"].open("w", encoding="utf-8", newline="\n") as data_file:
        for idx in sorted(used_functions):
            data_file.write(json.dumps(used_functions[idx], ensure_ascii=False) + "\n")


def compact_manifest_row(candidate: dict[str, Any], row: dict[str, Any], *, pair_id: int) -> dict[str, Any]:
    context = candidate.get("context_completion") if isinstance(candidate.get("context_completion"), dict) else {}
    return {
        "case_id": candidate.get("case_id"),
        "pair_id": pair_id,
        "function_id_a": row.get("function_id_a"),
        "function_id_b": row.get("function_id_b"),
        "gold": row.get("label"),
        "graphcodebert_prediction": row.get("graphcodebert_prediction"),
        "pain_point": candidate.get("pain_point"),
        "family": candidate.get("family"),
        "probe_mode": candidate.get("probe_mode"),
        "generation_route": candidate.get("generation_route"),
        "risk_tier": candidate.get("risk_tier"),
        "candidate_correct": bool(candidate.get("candidate_correct")),
        "expected_source_sha256": context.get("java_source_sha256"),
        "context_completion_status": context.get("status"),
        "next_action": candidate.get("next_action"),
    }


def summarize_queue(
    *,
    dataset: Path,
    candidates_jsonl: Path,
    output_dir: Path,
    split: str,
    selected: list[dict[str, Any]],
    missing_cases: list[int],
    pair_mismatches: list[dict[str, Any]],
    duplicate_case_ids: list[int],
    workers: int,
    dynamic_workers: int,
    model: str,
    base_url: str,
    api_key_env: str,
    paths: dict[str, Path],
) -> dict[str, Any]:
    route_counts = Counter(str(item["candidate"].get("generation_route") or "unknown") for item in selected)
    probe_counts = Counter(str(item["candidate"].get("probe_mode") or "unknown") for item in selected)
    pain_counts = Counter(str(item["candidate"].get("pain_point") or "unknown") for item in selected)
    risk_counts = Counter(str(item["candidate"].get("risk_tier") or "unknown") for item in selected)
    label_counts = Counter(str(item["dataset"].get("label")) for item in selected)
    candidate_correct = sum(1 for item in selected if item["candidate"].get("candidate_correct"))
    missing_code = sum(1 for item in selected if not item["dataset"].get("code_a") or not item["dataset"].get("code_b"))
    source_hashes = Counter(
        "present" if (item["candidate"].get("context_completion") or {}).get("java_source_sha256") else "missing"
        for item in selected
    )
    run_command = build_run_command(
        paths=paths,
        split=split,
        workers=workers,
        dynamic_workers=dynamic_workers,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
    )
    status = "queue_ready"
    if missing_cases or pair_mismatches or duplicate_case_ids or missing_code:
        status = "queue_ready_with_warnings"
    return {
        "schema_version": "eviclone-probe-source-retention-rerun-queue/v1",
        "status": status,
        "dataset": str(dataset.resolve()),
        "candidates_jsonl": str(candidates_jsonl.resolve()),
        "output_dir": str(output_dir.resolve()),
        "split": split,
        "candidate_count": len(selected) + len(missing_cases),
        "written_pairs": len(selected),
        "missing_dataset_cases": sorted(missing_cases),
        "missing_dataset_case_count": len(missing_cases),
        "pair_mismatch_count": len(pair_mismatches),
        "pair_mismatch_examples": pair_mismatches[:10],
        "duplicate_case_ids": duplicate_case_ids,
        "duplicate_case_id_count": len(duplicate_case_ids),
        "missing_code_pairs": missing_code,
        "candidate_correct": candidate_correct,
        "source_hash_counts": sorted_counter(source_hashes),
        "generation_route_counts": sorted_counter(route_counts),
        "probe_mode_counts": sorted_counter(probe_counts),
        "pain_point_counts": sorted_counter(pain_counts),
        "risk_tier_counts": sorted_counter(risk_counts),
        "label_counts": sorted_counter(label_counts),
        "outputs": {name: str(path.resolve()) for name, path in paths.items() if name not in {"context_sources"}},
        "context_source_dir": str(paths["context_sources"].resolve()),
        "recommended_run": {
            "purpose": "Regenerate LLM context-completed EviProbe.java sidecars for the 860 compile-success/no-probe cases.",
            "api_key_env": api_key_env,
            "api_key_is_not_serialized": True,
            "workers": workers,
            "dynamic_workers": dynamic_workers,
            "command": run_command,
        },
    }


def build_run_command(
    *,
    paths: dict[str, Path],
    split: str,
    workers: int,
    dynamic_workers: int,
    model: str,
    base_url: str,
    api_key_env: str,
) -> list[str]:
    return [
        "python",
        "scripts/run_error_cases_unordered.py",
        "--dataset",
        rel(paths["pairs"]),
        "--split-dir",
        rel(paths["pairs"].parent),
        "--splits",
        split,
        "--output",
        rel(paths["cards"]),
        "--report-path",
        rel(paths["cards_report"]),
        "--summary-path",
        rel(paths["cards_summary"]),
        "--workers",
        str(workers),
        "--dynamic-workers",
        str(dynamic_workers),
        "--with-dynamic",
        "--dynamic-mode",
        "execute",
        "--with-llm-context-completion",
        "--context-source-dir",
        rel(paths["context_sources"]),
        "--model",
        model,
        "--base-url",
        base_url,
        "--api-key-env",
        api_key_env,
        "--resume",
        "--resume-usable-only",
    ]


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Probe Source-Retention Rerun Queue",
        "",
        f"Status: `{summary['status']}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "| --- | ---: |",
        f"| candidate_count | {summary['candidate_count']} |",
        f"| written_pairs | {summary['written_pairs']} |",
        f"| candidate_correct | {summary['candidate_correct']} |",
        f"| missing_dataset_case_count | {summary['missing_dataset_case_count']} |",
        f"| pair_mismatch_count | {summary['pair_mismatch_count']} |",
        f"| duplicate_case_id_count | {summary['duplicate_case_id_count']} |",
        f"| missing_code_pairs | {summary['missing_code_pairs']} |",
        "",
        "## Generation Routes",
        "",
        "| route | cases |",
        "| --- | ---: |",
    ]
    for route, count in summary["generation_route_counts"].items():
        lines.append(f"| {route} | {count} |")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- pairs_jsonl: `{summary['outputs']['pairs']}`",
            f"- split_jsonl: `{summary['outputs']['split']}`",
            f"- split_txt: `{summary['outputs']['txt']}`",
            f"- data_jsonl: `{summary['outputs']['data']}`",
            f"- candidate_manifest: `{summary['outputs']['manifest']}`",
            f"- context_source_dir: `{summary['context_source_dir']}`",
            "",
            "## Recommended Run",
            "",
            "The command intentionally stores only the API-key environment variable name, not a secret value.",
            "",
            "```powershell",
            powershell_command(summary["recommended_run"]["command"]),
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def duplicate_values(values: list[int | None]) -> list[int]:
    counts = Counter(value for value in values if value is not None)
    return sorted(value for value, count in counts.items() if count > 1)


def int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def powershell_command(parts: list[str]) -> str:
    return " ".join(ps_quote(part) for part in parts)


def ps_quote(value: str) -> str:
    if value.replace("_", "").replace("-", "").replace(".", "").replace("/", "").replace(":", "").isalnum():
        return value
    return "'" + value.replace("'", "''") + "'"


if __name__ == "__main__":
    raise SystemExit(main())
