from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from build_prism_adapter_dataset import DATASET_DIRS, channel_vectors, hashed_vector, read_jsonl_functions


JAVA_IMPORTS = "import java.io.*;\nimport java.util.*;\nimport java.math.*;\n"
CPP_PRELUDE = r"""
#define _CRT_SECURE_NO_WARNINGS
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <cctype>
#include <climits>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <queue>
#include <stack>
#include <deque>
#include <map>
#include <set>
#include <algorithm>
using namespace std;
extern "C" char *gets(char *);
"""

JAVA_CLASS_RE = re.compile(r"\b(?:public\s+)?class\s+([A-Za-z_][A-Za-z_0-9]*)")
ASM_TOKEN_RE = re.compile(r"[A-Za-z_.$][A-Za-z_0-9.$]*|\d+|[-+*/%<>=!&|^~?:;,.{}()\[\]#@]")
COMPILED_TEXT_FEATURE_LIMIT = 50000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build Prism compile-adapter arrays. OJClone is compiled to MSVC assembly; "
            "GCJ Java is compiled with javac and represented by javap bytecode disassembly."
        )
    )
    parser.add_argument("--dataset", required=True, choices=["OJClone", "GCJ"])
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("eviclone_runs/baseline_reproduction/graphcodebert_dsfm_splits"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Default: eviclone_runs/baseline_reproduction/prism_compile_adapter/<dataset>_full_arrays",
    )
    parser.add_argument("--splits", nargs="+", default=["train", "test"])
    parser.add_argument("--dim", type=int, default=96)
    parser.add_argument("--max-rows-per-split", type=int, default=0)
    parser.add_argument("--max-per-label", type=int, default=0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--compile-timeout-sec", type=int, default=20)
    parser.add_argument("--force-recompile", action="store_true")
    return parser.parse_args()


def run_command(command: list[str], *, cwd: Path, timeout: int, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def msvc_environment() -> dict[str, str] | None:
    vcvars_value = os.environ.get("PRISM_VCVARS64", "").strip()
    if not vcvars_value:
        return None
    vcvars = Path(vcvars_value)
    if not vcvars.exists():
        return None
    with tempfile.TemporaryDirectory(prefix="prism_vcvars_") as tmp:
        script = Path(tmp) / "dump_env.bat"
        script.write_text(f'@echo off\r\ncall "{vcvars}" >nul\r\nset\r\n', encoding="utf-8")
        result = subprocess.run(["cmd.exe", "/c", str(script)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        return None
    env = dict(os.environ)
    for line in result.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            env[key] = value
    return env


def find_cl(env: dict[str, str] | None) -> str | None:
    found = shutil.which("cl.exe", path=env.get("PATH") if env else None)
    if found:
        return found
    return shutil.which("cl.exe")


def needed_function_ids(
    split_paths: list[Path],
    functions: dict[str, str],
    *,
    max_rows: int,
    max_per_label: int,
) -> set[str]:
    needed: set[str] = set()
    for split_path in split_paths:
        rows = 0
        label_counts: Counter[str] = Counter()
        with split_path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) != 3:
                    raise ValueError(f"{split_path}:{line_no} expected id_a<TAB>id_b<TAB>label")
                left_id, right_id, label = parts
                if max_rows and rows >= max_rows:
                    break
                if max_per_label and label_counts[label] >= max_per_label:
                    continue
                if left_id not in functions or right_id not in functions:
                    continue
                needed.add(left_id)
                needed.add(right_id)
                rows += 1
                label_counts[label] += 1
    return needed


def compile_cpp_to_asm(idx: str, code: str, *, timeout: int, env: dict[str, str], cl_path: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"prism_cpp_{idx}_") as tmp:
        work = Path(tmp)
        source = work / "snippet.cpp"
        asm_path = work / "snippet.asm"
        source.write_text(CPP_PRELUDE + "\n" + code, encoding="utf-8", errors="ignore")
        command = [
            cl_path,
            "/nologo",
            "/TP",
            "/std:c++17",
            "/EHsc",
            "/D_CRT_SECURE_NO_WARNINGS",
            "/FA",
            "/c",
            str(source.name),
            "/Fosnippet.obj",
            "/Fasnippet.asm",
        ]
        try:
            result = run_command(command, cwd=work, timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            return {"idx": idx, "status": "timeout", "compiled_text": "", "stderr": "compile timeout"}
        alt_asm_path = work / "snippet.asm"
        if not asm_path.exists() and alt_asm_path.exists():
            asm_path = alt_asm_path
        if result.returncode != 0 or not asm_path.exists():
            stderr = (result.stderr or result.stdout or "")
            return {
                "idx": idx,
                "status": "compile_failed",
                "compiled_text": "",
                "stderr": stderr[-2000:],
            }
        return {
            "idx": idx,
            "status": "compiled",
            "compiled_text": asm_path.read_text(encoding="utf-8", errors="ignore"),
            "stderr": result.stderr[-2000:],
        }


def java_class_name(code: str) -> str | None:
    match = JAVA_CLASS_RE.search(code)
    return match.group(1) if match else None


def compile_java_to_javap(idx: str, code: str, *, timeout: int) -> dict[str, Any]:
    name = java_class_name(code)
    if not name:
        return {"idx": idx, "status": "no_class_name", "compiled_text": "", "stderr": "no Java class name found"}
    with tempfile.TemporaryDirectory(prefix=f"prism_java_{idx}_") as tmp:
        work = Path(tmp)
        source = work / f"{name}.java"
        source.write_text(JAVA_IMPORTS + "\n" + code, encoding="utf-8", errors="ignore")
        try:
            compile_result = run_command(["javac", "-encoding", "UTF-8", source.name], cwd=work, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"idx": idx, "status": "timeout", "compiled_text": "", "stderr": "javac timeout"}
        if compile_result.returncode != 0:
            return {
                "idx": idx,
                "status": "compile_failed",
                "compiled_text": "",
                "stderr": (compile_result.stderr or compile_result.stdout)[-2000:],
            }
        try:
            javap_result = run_command(["javap", "-classpath", str(work), "-c", "-p", name], cwd=work, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"idx": idx, "status": "disassemble_timeout", "compiled_text": "", "stderr": "javap timeout"}
        if javap_result.returncode != 0:
            return {
                "idx": idx,
                "status": "disassemble_failed",
                "compiled_text": "",
                "stderr": (javap_result.stderr or javap_result.stdout)[-2000:],
            }
        return {
            "idx": idx,
            "status": "compiled",
            "compiled_text": javap_result.stdout,
            "stderr": compile_result.stderr[-2000:],
        }


def compile_functions(dataset: str, functions: dict[str, str], *, output_dir: Path, workers: int, timeout: int, force: bool) -> dict[str, dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = output_dir / "compile_records.jsonl"
    if cache_path.exists() and not force:
        records: dict[str, dict[str, Any]] = {}
        with cache_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    obj = json.loads(line)
                    records[str(obj["idx"])] = obj
        if len(records) == len(functions):
            return records

    env = msvc_environment() if dataset == "OJClone" else None
    cl_path = find_cl(env) if dataset == "OJClone" else None
    if dataset == "OJClone" and (not env or not cl_path):
        raise RuntimeError("MSVC cl.exe environment was not found; cannot compile OJClone C/C++ snippets")

    def one(item: tuple[str, str]) -> dict[str, Any]:
        idx, code = item
        if dataset == "OJClone":
            assert env is not None and cl_path is not None
            record = compile_cpp_to_asm(idx, code, timeout=timeout, env=env, cl_path=cl_path)
            record["compiler"] = "msvc-cl-asm"
        else:
            record = compile_java_to_javap(idx, code, timeout=timeout)
            record["compiler"] = "javac-javap"
        record["compiled_sha256"] = hashlib.sha256(record.get("compiled_text", "").encode("utf-8")).hexdigest() if record.get("compiled_text") else ""
        return record

    records = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(one, item) for item in functions.items()]
        for idx, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            record = future.result()
            records[str(record["idx"])] = record
            if idx % 250 == 0:
                print(json.dumps({"compiled_or_attempted": idx, "total": len(functions)}, ensure_ascii=False), flush=True)

    with cache_path.open("w", encoding="utf-8") as handle:
        for idx in sorted(records, key=lambda value: int(value) if value.isdigit() else value):
            compact = dict(records[idx])
            compiled_text = compact.pop("compiled_text", "")
            compact["compiled_text_path"] = ""
            if compiled_text:
                text_path = output_dir / "compiled_text" / f"{idx}.txt"
                text_path.parent.mkdir(parents=True, exist_ok=True)
                text_path.write_text(compiled_text, encoding="utf-8", errors="ignore")
                compact["compiled_text_path"] = str(text_path)
            handle.write(json.dumps(compact, ensure_ascii=False) + "\n")
            records[idx] = {**compact, "compiled_text": compiled_text}
    return records


def compiled_channel_vectors(code: str, record: dict[str, Any], *, dim: int) -> tuple[list[float], list[float], list[float], str]:
    compiled_text = record.get("compiled_text") or ""
    if not compiled_text and record.get("compiled_text_path"):
        path = Path(record["compiled_text_path"])
        if path.exists():
            compiled_text = path.read_text(encoding="utf-8", errors="ignore")
    if compiled_text:
        compiled_text = compiled_text[:COMPILED_TEXT_FEATURE_LIMIT]
        status = str(record.get("status") or "compiled")
        asm_tokens = ASM_TOKEN_RE.findall(compiled_text)
        arm_features = (
            [f"asm_tok:{tok.lower()}" for tok in asm_tokens],
            (f"asm_line:{line.strip().lower()}" for line in compiled_text.splitlines() if line.strip()),
        )
        x86_features = (
            (f"asm_char:{compiled_text[i:i+4]}" for i in range(max(0, len(compiled_text) - 3))),
            (f"asm_tri:{' '.join(asm_tokens[i:i+3]).lower()}" for i in range(max(0, len(asm_tokens) - 2))),
        )
        arm_iter = (feature for group in arm_features for feature in group)
        x86_iter = (feature for group in x86_features for feature in group)
        text_arm = hashed_vector(arm_iter, namespace="prism-compile-arm", dim=dim)
        text_x86 = hashed_vector(x86_iter, namespace="prism-compile-x86", dim=dim)
        _, _, text_vec = channel_vectors(code, dim=dim)
        return text_arm, text_x86, text_vec, status
    arm_vec, x86_vec, text_vec = channel_vectors(code, dim=dim)
    return arm_vec, x86_vec, text_vec, f"fallback_{record.get('status') or 'missing_compile'}"


def count_split_rows(split_path: Path, functions: dict[str, str], *, max_rows: int, max_per_label: int) -> dict[str, Any]:
    rows = 0
    scanned = 0
    label_counts: Counter[str] = Counter()
    skipped_missing = 0
    with split_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            scanned += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                raise ValueError(f"{split_path}:{line_no} expected id_a<TAB>id_b<TAB>label")
            left_id, right_id, label = parts
            if max_rows and rows >= max_rows:
                break
            if max_per_label and label_counts[label] >= max_per_label:
                continue
            if left_id not in functions or right_id not in functions:
                skipped_missing += 1
                continue
            rows += 1
            label_counts[label] += 1
    return {
        "rows": rows,
        "scanned_rows": scanned,
        "skipped_missing_functions": skipped_missing,
        "label_counts": dict(sorted(label_counts.items())),
    }


def write_split_arrays(
    split_path: Path,
    output_dir: Path,
    functions: dict[str, str],
    compile_records: dict[str, dict[str, Any]],
    *,
    dim: int,
    max_rows: int,
    max_per_label: int,
) -> dict[str, Any]:
    count_record = count_split_rows(split_path, functions, max_rows=max_rows, max_per_label=max_per_label)
    rows = int(count_record["rows"])
    output_dir.mkdir(parents=True, exist_ok=True)
    features_path = output_dir / f"{split_path.stem}.features.npy"
    labels_path = output_dir / f"{split_path.stem}.labels.npy"
    features = np.lib.format.open_memmap(features_path, mode="w+", dtype=np.float32, shape=(rows, dim * 6))
    labels = np.lib.format.open_memmap(labels_path, mode="w+", dtype=np.int64, shape=(rows,))
    vector_cache: dict[str, tuple[list[float], list[float], list[float], str]] = {}
    row_compile_status_counts: Counter[str] = Counter()
    label_counts: Counter[str] = Counter()
    row_idx = 0
    with split_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                raise ValueError(f"{split_path}:{line_no} expected id_a<TAB>id_b<TAB>label")
            left_id, right_id, label_text = parts
            if max_rows and row_idx >= max_rows:
                break
            if max_per_label and label_counts[label_text] >= max_per_label:
                continue
            if left_id not in functions or right_id not in functions:
                continue
            if left_id not in vector_cache:
                vector_cache[left_id] = compiled_channel_vectors(functions[left_id], compile_records.get(left_id, {}), dim=dim)
            if right_id not in vector_cache:
                vector_cache[right_id] = compiled_channel_vectors(functions[right_id], compile_records.get(right_id, {}), dim=dim)
            left_arm, left_x86, left_text, left_status = vector_cache[left_id]
            right_arm, right_x86, right_text, right_status = vector_cache[right_id]
            row_status = "both_compiled" if left_status == "compiled" and right_status == "compiled" else "has_compile_fallback"
            row_compile_status_counts[row_status] += 1
            features[row_idx, :] = np.asarray(
                [*left_arm, *left_x86, *left_text, *right_arm, *right_x86, *right_text],
                dtype=np.float32,
            )
            labels[row_idx] = int(label_text)
            label_counts[label_text] += 1
            row_idx += 1
    features.flush()
    labels.flush()
    return {
        **count_record,
        "features": str(features_path),
        "labels": str(labels_path),
        "row_width": dim * 6,
        "vector_cache_entries": len(vector_cache),
        "row_compile_status_counts": dict(sorted(row_compile_status_counts.items())),
    }


def main() -> int:
    args = parse_args()
    dataset_dir = args.input_root / DATASET_DIRS[args.dataset]
    if not dataset_dir.exists():
        raise FileNotFoundError(dataset_dir)
    output_dir = args.output_dir or ROOT / f"{args.dataset}_full_arrays"
    functions = read_jsonl_functions(dataset_dir / "data.jsonl")
    split_paths = []
    for split in args.splits:
        split_path = dataset_dir / f"{split}.txt"
        if not split_path.exists():
            raise FileNotFoundError(split_path)
        split_paths.append(split_path)
    ids = needed_function_ids(
        split_paths,
        functions,
        max_rows=args.max_rows_per_split,
        max_per_label=args.max_per_label,
    )
    compile_input_functions = {idx: functions[idx] for idx in ids}
    compile_records = compile_functions(
        args.dataset,
        compile_input_functions,
        output_dir=output_dir,
        workers=args.workers,
        timeout=args.compile_timeout_sec,
        force=args.force_recompile,
    )
    compile_counts = Counter(str(record.get("status")) for record in compile_records.values())
    split_records = {}
    for split_path in split_paths:
        split = split_path.stem
        split_records[split] = write_split_arrays(
            split_path,
            output_dir,
            functions,
            compile_records,
            dim=args.dim,
            max_rows=args.max_rows_per_split,
            max_per_label=args.max_per_label,
        )

    manifest = {
        "schema_version": "eviclone-prism-compile-adapter-arrays/v1",
        "dataset": args.dataset,
        "source_dataset_dir": str(dataset_dir),
        "output_dir": str(output_dir),
        "feature_dim_per_channel": args.dim,
        "row_width": args.dim * 6,
        "compile_policy": {
            "OJClone": "MSVC cl.exe /FA assembly from C/C++ snippets with common C/C++ includes.",
            "GCJ": "javac compilation followed by javap -c bytecode disassembly for Java classes.",
        }[args.dataset],
        "claim_boundary": (
            "Compile-based Prism adapter. It restores a compilation-derived representation stage, but it is not the "
            "official Prism asm2vec+BERT feature pipeline and must be reported as a variant."
        ),
        "compile_status_counts": dict(sorted(compile_counts.items())),
        "max_rows_per_split": args.max_rows_per_split,
        "max_per_label": args.max_per_label,
        "splits": split_records,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "compile_status_counts": manifest["compile_status_counts"], "splits": split_records}, indent=2, ensure_ascii=False))
    return 0


ROOT = Path("eviclone_runs/baseline_reproduction/prism_compile_adapter")


if __name__ == "__main__":
    raise SystemExit(main())
