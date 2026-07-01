from __future__ import annotations

import argparse
import json
import pickle
import shutil
import sys
import types
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
            label = parse_label(parts[2], path=path, line_no=line_no)
            rows.append((parts[0], parts[1], label))
    return rows


def parse_label(value: str, *, path: Path, line_no: int) -> int:
    if value in {"1", "true", "clone", "positive"}:
        return 1
    if value in {"0", "-1", "false", "nonclone", "non-clone", "negative"}:
        return 0
    raise ValueError(f"invalid binary label at {path}:{line_no}: {value!r}")


def iter_pickle_stream(path: Path):
    with path.open("rb") as source:
        while True:
            try:
                yield pickle.load(source)
            except EOFError:
                return


def write_pickle_stream(path: Path, values: list[Any]) -> None:
    with path.open("wb") as sink:
        for value in values:
            pickle.dump(value, sink)


def load_pickle_stream(path: Path) -> list[Any]:
    return list(iter_pickle_stream(path))


def load_dsfm_code_index(codes_pkl: Path) -> tuple[dict[str, list[int]], int]:
    by_code: dict[str, list[int]] = {}
    count = 0
    for idx, code in enumerate(iter_pickle_stream(codes_pkl)):
        by_code.setdefault(str(code), []).append(idx)
        count += 1
    return by_code, count


def copy_required_dsfm_files(dsfm_data_dir: Path, output_dir: Path) -> dict[str, str]:
    copied: dict[str, str] = {}
    for name in ["codes.pkl", "subtrees.pkl", "train.pkl", "val.pkl"]:
        source = dsfm_data_dir / name
        if not source.exists():
            raise FileNotFoundError(f"required DSFM file not found: {source}")
        target = output_dir / name
        shutil.copy2(source, target)
        copied[name] = str(target)
    return copied


def copy_or_extend_dsfm_files(
    *,
    dsfm_data_dir: Path,
    output_dir: Path,
    missing_function_ids: list[str],
    code_by_function_id: dict[str, str],
    function_to_dsfm_idx: dict[str, int],
    dsfm_src: Path,
) -> dict[str, str]:
    copied: dict[str, str] = {}
    for name in ["train.pkl", "val.pkl"]:
        source = dsfm_data_dir / name
        if not source.exists():
            raise FileNotFoundError(f"required DSFM file not found: {source}")
        target = output_dir / name
        shutil.copy2(source, target)
        copied[name] = str(target)

    official_codes = load_pickle_stream(dsfm_data_dir / "codes.pkl")
    official_subtrees = load_pickle_stream(dsfm_data_dir / "subtrees.pkl")
    if len(official_codes) != len(official_subtrees):
        raise ValueError(
            f"official DSFM codes/subtrees row mismatch: {len(official_codes)} != {len(official_subtrees)}"
        )

    appended_codes = [code_by_function_id[function_id] for function_id in missing_function_ids]
    appended_subtrees = build_subtrees_from_java_methods(appended_codes, dsfm_src=dsfm_src)
    next_idx = len(official_codes)
    for offset, function_id in enumerate(missing_function_ids):
        function_to_dsfm_idx[function_id] = next_idx + offset

    write_pickle_stream(output_dir / "codes.pkl", official_codes + appended_codes)
    write_pickle_stream(output_dir / "subtrees.pkl", official_subtrees + appended_subtrees)
    copied["codes.pkl"] = str(output_dir / "codes.pkl")
    copied["subtrees.pkl"] = str(output_dir / "subtrees.pkl")
    return copied


def build_subtrees_from_java_methods(codes: list[str], *, dsfm_src: Path) -> list[Any]:
    if not codes:
        return []
    if str(dsfm_src.resolve()) not in sys.path:
        sys.path.insert(0, str(dsfm_src.resolve()))
    # DSFM imports its BCB database loader at module import time. The subtree
    # extraction methods used here do not need a PostgreSQL connection.
    sys.modules.setdefault("psycopg2", types.ModuleType("psycopg2"))
    from preprocess.pipeline import Pipeline  # type: ignore

    pipeline = Pipeline(".", ".", "BigCloneBench")
    asts = pipeline.parse_codes(codes)
    unified = pipeline.unify_asts(asts)
    return pipeline.extract_subtrees(unified)


def build_dsfm_hardset(
    *,
    hardset_dir: Path,
    dsfm_data_dir: Path,
    output_dir: Path,
    dataset_name: str,
    append_missing_functions: bool,
    dsfm_src: Path,
) -> dict[str, Any]:
    hardset_data = read_jsonl(hardset_dir / "data.jsonl")
    hardset_triplets = read_triplets(hardset_dir / "test.txt")
    code_by_function_id = {str(row.get("idx")): str(row.get("func") or "") for row in hardset_data}
    if len(code_by_function_id) != len(hardset_data):
        raise ValueError("duplicate or missing function ids in HardSet data.jsonl")

    dsfm_code_to_indices, dsfm_code_count = load_dsfm_code_index(dsfm_data_dir / "codes.pkl")
    function_to_dsfm_idx: dict[str, int] = {}
    duplicate_code_matches: dict[str, list[int]] = {}
    missing: list[str] = []
    for function_id, code in code_by_function_id.items():
        indices = dsfm_code_to_indices.get(code)
        if not indices:
            missing.append(function_id)
            continue
        function_to_dsfm_idx[function_id] = int(indices[0])
        if len(indices) > 1:
            duplicate_code_matches[function_id] = [int(value) for value in indices]
    if missing:
        if not append_missing_functions:
            raise ValueError(f"{len(missing)} HardSet functions are missing from DSFM codes.pkl: {missing[:10]}")

    output_dir.mkdir(parents=True, exist_ok=True)
    if missing:
        copied = copy_or_extend_dsfm_files(
            dsfm_data_dir=dsfm_data_dir,
            output_dir=output_dir,
            missing_function_ids=sorted(missing, key=lambda value: int(value) if value.isdigit() else value),
            code_by_function_id=code_by_function_id,
            function_to_dsfm_idx=function_to_dsfm_idx,
            dsfm_src=dsfm_src,
        )
    else:
        copied = copy_required_dsfm_files(dsfm_data_dir, output_dir)

    label_counts: Counter[int] = Counter()
    with (output_dir / "test.pkl").open("wb") as sink, (output_dir / "pair_map.txt").open(
        "w", encoding="utf-8", newline="\n"
    ) as pair_map:
        for function_id_a, function_id_b, label in hardset_triplets:
            if function_id_a not in function_to_dsfm_idx:
                raise ValueError(f"HardSet function id not mapped to DSFM: {function_id_a}")
            if function_id_b not in function_to_dsfm_idx:
                raise ValueError(f"HardSet function id not mapped to DSFM: {function_id_b}")
            idx_a = function_to_dsfm_idx[function_id_a]
            idx_b = function_to_dsfm_idx[function_id_b]
            raw_label = 1 if label == 1 else -1
            pickle.dump(((idx_a, idx_b), raw_label), sink)
            pair_map.write(f"{function_id_a}\t{function_id_b}\t{label}\n")
            label_counts[label] += 1

    summary = {
        "schema_version": "eviclone-dsfm-hardset/v1",
        "status": "materialized",
        "dataset_name": dataset_name,
        "hardset_dir": str(hardset_dir),
        "dsfm_data_dir": str(dsfm_data_dir),
        "output_dir": str(output_dir),
        "source_dsfm_code_count": dsfm_code_count,
        "hardset_rows": len(hardset_triplets),
        "hardset_function_rows": len(hardset_data),
        "mapped_function_rows": len(function_to_dsfm_idx),
        "missing_function_rows": len(missing),
        "appended_missing_functions": bool(missing and append_missing_functions),
        "appended_function_ids": sorted(missing, key=lambda value: int(value) if value.isdigit() else value),
        "duplicate_code_match_count": len(duplicate_code_matches),
        "duplicate_code_matches": duplicate_code_matches,
        "label_counts": {"0": int(label_counts[0]), "1": int(label_counts[1])},
        "copied_dsfm_files": copied,
        "artifacts": {
            "test_pkl": str(output_dir / "test.pkl"),
            "pair_map": str(output_dir / "pair_map.txt"),
            "summary": str(output_dir / "summary.json"),
        },
        "protocol_note": (
            "This directory reuses the official DSFM BigCloneBench train split and subtrees.pkl "
            "so that the checkpoint sees the same vocabulary construction as the reproduced BCB run. "
            "Only test.pkl is replaced with the HardSet pairs mapped back to DSFM internal code indices. "
            "When --append-missing-functions is used, functions absent from official DSFM codes.pkl are appended "
            "after all official rows and are therefore unseen by the training vocabulary except through [OOV]."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Map CodeXGLUE BCB HardSet rows into DSFM processed BCB indices.")
    parser.add_argument("--hardset-dir", type=Path, required=True)
    parser.add_argument("--dsfm-data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-name", default="EviClone-HardSet-GCB-Corrected-DSFM")
    parser.add_argument("--append-missing-functions", action="store_true")
    parser.add_argument("--dsfm-src", type=Path, default=Path("external") / "DSFM" / "src")
    args = parser.parse_args()

    summary = build_dsfm_hardset(
        hardset_dir=args.hardset_dir,
        dsfm_data_dir=args.dsfm_data_dir,
        output_dir=args.output_dir,
        dataset_name=args.dataset_name,
        append_missing_functions=args.append_missing_functions,
        dsfm_src=args.dsfm_src,
    )
    print(
        json.dumps(
            {
                "status": summary["status"],
                "hardset_rows": summary["hardset_rows"],
                "mapped_function_rows": summary["mapped_function_rows"],
                "duplicate_code_match_count": summary["duplicate_code_match_count"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
