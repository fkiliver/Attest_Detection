from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.decomposition import PCA
from transformers import AutoModel, AutoTokenizer


REPO_ROOT = Path(__file__).resolve().parents[1]
PRISM_ASM2VEC = REPO_ROOT / "external" / "Prism" / "asm2vec" / "asm2vec"
if str(PRISM_ASM2VEC) not in sys.path:
    sys.path.insert(0, str(PRISM_ASM2VEC))

import asm2vec.model  # noqa: E402
import asm2vec.parse  # noqa: E402

from build_prism_adapter_dataset import DATASET_DIRS, read_jsonl_functions  # noqa: E402
from build_prism_compile_adapter_arrays import CPP_PRELUDE, JAVA_IMPORTS, JAVA_CLASS_RE  # noqa: E402


ROOT = Path("eviclone_runs/baseline_reproduction/prism_asm2vec_bert_adapter")
ASM_OP_RE = re.compile(r"^[A-Za-z_.][A-Za-z0-9_.$@?]*$")
JAVAP_INSTR_RE = re.compile(r"^\s*\d+:\s+([A-Za-z_][A-Za-z0-9_]*)\s*(.*)$")
MSVC_SKIP_OPS = {
    "include",
    "includelib",
    "public",
    "extrn",
    "segment",
    "ends",
    "proc",
    "endp",
    "org",
    "db",
    "dw",
    "dd",
    "dq",
    "equ",
    "align",
    "assume",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build full-scale Prism-style asm2vec+BERT feature arrays for OJClone/GCJ."
    )
    parser.add_argument("--dataset", required=True, choices=["OJClone", "GCJ"])
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("eviclone_runs/baseline_reproduction/graphcodebert_dsfm_splits"),
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--splits", nargs="+", default=["train", "valid", "test"])
    parser.add_argument("--compile-workers", type=int, default=8)
    parser.add_argument("--compile-timeout-sec", type=int, default=20)
    parser.add_argument("--force-recompile", action="store_true")
    parser.add_argument("--force-asm2vec", action="store_true")
    parser.add_argument("--force-bert", action="store_true")
    parser.add_argument("--force-arrays", action="store_true")
    parser.add_argument("--asm2vec-jobs", type=int, default=4)
    parser.add_argument("--asm2vec-dim", type=int, default=48)
    parser.add_argument("--bert-model", default="bert-base-uncased")
    parser.add_argument("--bert-batch-size", type=int, default=32)
    parser.add_argument("--bert-max-length", type=int, default=256)
    parser.add_argument("--bert-device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--pca-dim", type=int, default=96)
    parser.add_argument("--max-rows-per-split", type=int, default=0)
    parser.add_argument("--max-per-label", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.getLogger("asm2vec").setLevel(logging.WARNING)
    dataset_dir = args.input_root / DATASET_DIRS[args.dataset]
    if not dataset_dir.exists():
        raise FileNotFoundError(dataset_dir)
    output_dir = args.output_dir or ROOT / f"{args.dataset}_full_arrays"
    output_dir.mkdir(parents=True, exist_ok=True)

    functions = read_jsonl_functions(dataset_dir / "data.jsonl")
    split_paths = [dataset_dir / f"{split}.txt" for split in args.splits]
    for split_path in split_paths:
        if not split_path.exists():
            raise FileNotFoundError(split_path)
    needed_ids = needed_function_ids(
        split_paths,
        functions,
        max_rows=args.max_rows_per_split,
        max_per_label=args.max_per_label,
    )
    ordered_ids = sorted(needed_ids, key=lambda value: int(value) if value.isdigit() else value)
    needed_functions = {idx: functions[idx] for idx in ordered_ids}

    channel_specs = channel_specs_for_dataset(args.dataset)
    channel_vectors: dict[str, dict[str, np.ndarray]] = {}
    channel_manifests: dict[str, Any] = {}
    for channel in channel_specs:
        compile_records = compile_channel(
            args.dataset,
            channel,
            needed_functions,
            output_dir=output_dir,
            workers=args.compile_workers,
            timeout=args.compile_timeout_sec,
            force=args.force_recompile,
        )
        vectors, vector_manifest = build_asm2vec_vectors(
            channel,
            compile_records,
            ordered_ids,
            output_dir=output_dir,
            dim=args.asm2vec_dim,
            jobs=args.asm2vec_jobs,
            force=args.force_asm2vec,
        )
        channel_vectors[channel["name"]] = vectors
        channel_manifests[channel["name"]] = {
            "compile": summarize_compile_records(compile_records),
            "asm2vec": vector_manifest,
            "policy": channel["policy"],
        }

    text_vectors, text_manifest = build_bert_vectors(
        needed_functions,
        ordered_ids,
        output_dir=output_dir,
        model_name=args.bert_model,
        batch_size=args.bert_batch_size,
        max_length=args.bert_max_length,
        pca_dim=args.pca_dim,
        device_name=args.bert_device,
        force=args.force_bert,
    )

    split_records = {}
    for split_path in split_paths:
        split_records[split_path.stem] = write_split_arrays(
            split_path,
            output_dir,
            functions,
            channel_vectors[channel_specs[0]["name"]],
            channel_vectors[channel_specs[1]["name"]],
            text_vectors,
            max_rows=args.max_rows_per_split,
            max_per_label=args.max_per_label,
            force=args.force_arrays,
        )

    manifest = {
        "schema_version": "eviclone-prism-asm2vec-bert-arrays/v1",
        "dataset": args.dataset,
        "source_dataset_dir": str(dataset_dir),
        "output_dir": str(output_dir),
        "function_count": len(ordered_ids),
        "row_width": 576,
        "feature_layout": [
            f"left_{channel_specs[0]['name']}_asm2vec96",
            f"left_{channel_specs[1]['name']}_asm2vec96",
            "left_bert_pca96",
            f"right_{channel_specs[0]['name']}_asm2vec96",
            f"right_{channel_specs[1]['name']}_asm2vec96",
            "right_bert_pca96",
        ],
        "claim_boundary": claim_boundary(args.dataset),
        "channels": channel_manifests,
        "text": text_manifest,
        "max_rows_per_split": args.max_rows_per_split,
        "max_per_label": args.max_per_label,
        "splits": split_records,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "splits": split_records}, ensure_ascii=False, indent=2))
    return 0


def claim_boundary(dataset: str) -> str:
    if dataset == "OJClone":
        return (
            "Local Prism-style asm2vec+BERT variant. OJClone uses MSVC x64/x86 assembly channels plus "
            "bert-base-uncased PCA-96 source embeddings because the official Prism ARM/x86 asm2vec and "
            "fine-tuned BERT artifacts are not released. Report only as [var]."
        )
    return (
        "Local Prism-style asm2vec+BERT variant. GCJ Java uses javap bytecode channels plus "
        "bert-base-uncased PCA-96 source embeddings because Prism is released for a C/C++ compilation "
        "pipeline and no official GCJ Prism features/checkpoints are released. Report only as [var]."
    )


def channel_specs_for_dataset(dataset: str) -> list[dict[str, str]]:
    if dataset == "OJClone":
        return [
            {"name": "x64", "policy": "MSVC cl.exe x64 /FA assembly normalized for asm2vec."},
            {"name": "x86", "policy": "MSVC cl.exe x86 /FA assembly normalized for asm2vec."},
        ]
    return [
        {"name": "javap", "policy": "javac plus javap -c -p bytecode normalized for asm2vec."},
        {"name": "javap_verbose", "policy": "javac plus javap -c -p -v bytecode normalized for asm2vec."},
    ]


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
                left_id, right_id, label = parse_pair_line(split_path, line_no, line)
                if max_rows and rows >= max_rows:
                    break
                if max_per_label and label_counts[label] >= max_per_label:
                    continue
                if left_id not in functions or right_id not in functions:
                    continue
                needed.add(left_id)
                needed.add(right_id)
                label_counts[label] += 1
                rows += 1
    return needed


def parse_pair_line(path: Path, line_no: int, line: str) -> tuple[str, str, str]:
    parts = line.rstrip("\n").split("\t")
    if len(parts) != 3:
        raise ValueError(f"{path}:{line_no} expected id_a<TAB>id_b<TAB>label")
    return parts[0], parts[1], parts[2]


def command_env(vcvars_arg: str) -> dict[str, str] | None:
    vcvarsall_value = os.environ.get("PRISM_VCVARSALL", "").strip()
    if not vcvarsall_value:
        return None
    vcvarsall = Path(vcvarsall_value)
    if not vcvarsall.exists():
        return None
    with tempfile.TemporaryDirectory(prefix="prism_vcvars_") as tmp:
        script = Path(tmp) / "dump_env.bat"
        script.write_text(f'@echo off\r\ncall "{vcvarsall}" {vcvars_arg} >nul\r\nset\r\n', encoding="utf-8")
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
    if env:
        found = shutil.which("cl.exe", path=env.get("PATH"))
        if found:
            return found
    return shutil.which("cl.exe")


def run_command(
    command: list[str],
    *,
    cwd: Path,
    timeout: int,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
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


def compile_channel(
    dataset: str,
    channel: dict[str, str],
    functions: dict[str, str],
    *,
    output_dir: Path,
    workers: int,
    timeout: int,
    force: bool,
) -> dict[str, dict[str, Any]]:
    name = channel["name"]
    cache_path = output_dir / f"compile_records_{name}.jsonl"
    if cache_path.exists() and not force:
        records = read_jsonl_records(cache_path)
        if len(records) == len(functions):
            return records

    if dataset == "OJClone":
        vc_arg = "x64" if name == "x64" else "x86"
        env = command_env(vc_arg)
        cl_path = find_cl(env)
        if not env or not cl_path:
            raise RuntimeError(f"MSVC environment for {vc_arg} was not found")
    else:
        env = None
        cl_path = None

    compiled_text_dir = output_dir / f"compiled_text_{name}"
    normalized_dir = output_dir / f"normalized_asm_{name}"
    compiled_text_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)

    def one(item: tuple[str, str]) -> dict[str, Any]:
        idx, code = item
        if dataset == "OJClone":
            assert env is not None and cl_path is not None
            record = compile_cpp(idx, code, channel=name, timeout=timeout, env=env, cl_path=cl_path)
        else:
            record = compile_java(idx, code, verbose=name.endswith("verbose"), timeout=timeout)
        compiled_text = record.pop("compiled_text", "")
        normalized = normalize_compiled_text(dataset, idx, compiled_text)
        if compiled_text:
            compiled_path = compiled_text_dir / f"{idx}.txt"
            compiled_path.write_text(compiled_text, encoding="utf-8", errors="ignore")
            record["compiled_text_path"] = str(compiled_path)
        if normalized:
            normalized_path = normalized_dir / f"{idx}.s"
            normalized_path.write_text(normalized, encoding="utf-8", errors="ignore")
            record["normalized_asm_path"] = str(normalized_path)
        record["idx"] = idx
        record["channel"] = name
        record["normalized_sha256"] = hashlib.sha256(normalized.encode("utf-8")).hexdigest() if normalized else ""
        record["normalized_instruction_count"] = max(0, len(normalized.splitlines()) - 1) if normalized else 0
        return record

    records: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(one, item) for item in functions.items()]
        for count, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            record = future.result()
            records[str(record["idx"])] = record
            if count % 250 == 0:
                print(json.dumps({"channel": name, "compiled": count, "total": len(functions)}, ensure_ascii=False), flush=True)

    with cache_path.open("w", encoding="utf-8") as handle:
        for idx in sorted(records, key=lambda value: int(value) if value.isdigit() else value):
            handle.write(json.dumps(records[idx], ensure_ascii=False) + "\n")
    return records


def read_jsonl_records(path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                obj = json.loads(line)
                records[str(obj["idx"])] = obj
    return records


def compile_cpp(
    idx: str,
    code: str,
    *,
    channel: str,
    timeout: int,
    env: dict[str, str],
    cl_path: str,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"prism_asm2vec_cpp_{channel}_{idx}_") as tmp:
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
            source.name,
            "/Fosnippet.obj",
            "/Fasnippet.asm",
        ]
        try:
            result = run_command(command, cwd=work, timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "compiler": f"msvc-{channel}", "compiled_text": "", "stderr": "compile timeout"}
        if result.returncode != 0 or not asm_path.exists():
            return {
                "status": "compile_failed",
                "compiler": f"msvc-{channel}",
                "compiled_text": "",
                "stderr": (result.stderr or result.stdout or "")[-2000:],
            }
        return {
            "status": "compiled",
            "compiler": f"msvc-{channel}",
            "compiled_text": asm_path.read_text(encoding="utf-8", errors="ignore"),
            "stderr": result.stderr[-2000:],
        }


def java_class_name(code: str) -> str | None:
    match = JAVA_CLASS_RE.search(code)
    return match.group(1) if match else None


def compile_java(idx: str, code: str, *, verbose: bool, timeout: int) -> dict[str, Any]:
    name = java_class_name(code)
    if not name:
        return {"status": "no_class_name", "compiler": "javac-javap", "compiled_text": "", "stderr": "no Java class name found"}
    with tempfile.TemporaryDirectory(prefix=f"prism_asm2vec_java_{idx}_") as tmp:
        work = Path(tmp)
        source = work / f"{name}.java"
        source.write_text(JAVA_IMPORTS + "\n" + code, encoding="utf-8", errors="ignore")
        try:
            compile_result = run_command(["javac", "-encoding", "UTF-8", source.name], cwd=work, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "compiler": "javac-javap", "compiled_text": "", "stderr": "javac timeout"}
        if compile_result.returncode != 0:
            return {
                "status": "compile_failed",
                "compiler": "javac-javap",
                "compiled_text": "",
                "stderr": (compile_result.stderr or compile_result.stdout or "")[-2000:],
            }
        command = ["javap", "-classpath", str(work), "-c", "-p"]
        if verbose:
            command.append("-v")
        command.append(name)
        try:
            javap_result = run_command(command, cwd=work, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "disassemble_timeout", "compiler": "javac-javap", "compiled_text": "", "stderr": "javap timeout"}
        if javap_result.returncode != 0:
            return {
                "status": "disassemble_failed",
                "compiler": "javac-javap",
                "compiled_text": "",
                "stderr": (javap_result.stderr or javap_result.stdout or "")[-2000:],
            }
        return {
            "status": "compiled",
            "compiler": "javac-javap-verbose" if verbose else "javac-javap",
            "compiled_text": javap_result.stdout,
            "stderr": compile_result.stderr[-2000:],
        }


def normalize_compiled_text(dataset: str, idx: str, text: str) -> str:
    if not text:
        return fallback_asm(idx)
    if dataset == "OJClone":
        return normalize_msvc_asm(idx, text)
    return normalize_javap(idx, text)


def fallback_asm(idx: str) -> str:
    return f"fn_{sanitize_label(idx)}:\n nop\n ret\n"


def sanitize_label(label: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]", "_", label)
    if not safe or safe[0].isdigit():
        safe = "id_" + safe
    return safe


def normalize_msvc_asm(idx: str, text: str) -> str:
    lines = [f"fn_{sanitize_label(idx)}:"]
    in_text = False
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].replace("\t", " ").rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if lower == "_text segment":
            in_text = True
            continue
        if lower == "_text ends":
            in_text = False
            continue
        if not in_text:
            continue
        if "=" in stripped and not raw[:1].isspace():
            continue
        if stripped.lower().endswith(" proc") or stripped.lower().endswith(" endp"):
            continue
        if stripped.endswith(":"):
            continue
        parts = stripped.split()
        if not parts:
            continue
        op = parts[0].lower()
        if op in MSVC_SKIP_OPS or not ASM_OP_RE.match(op):
            continue
        args = " ".join(parts[1:])
        args = normalize_args(args)
        lines.append(f" {op}{(' ' + args) if args else ''}")
    if len(lines) <= 2:
        return fallback_asm(idx)
    if not lines[-1].strip().startswith("ret"):
        lines.append(" ret")
    return "\n".join(lines) + "\n"


def normalize_javap(idx: str, text: str) -> str:
    lines = [f"fn_{sanitize_label(idx)}:"]
    for raw in text.splitlines():
        match = JAVAP_INSTR_RE.match(raw)
        if not match:
            continue
        op = match.group(1).lower()
        args = match.group(2).split("//", 1)[0].strip()
        args = normalize_args(args)
        lines.append(f" {op}{(' ' + args) if args else ''}")
    if len(lines) <= 2:
        return fallback_asm(idx)
    if not lines[-1].strip().startswith("return"):
        lines.append(" return")
    return "\n".join(lines) + "\n"


def normalize_args(args: str) -> str:
    if not args:
        return ""
    args = args.replace("SHORT ", "")
    args = args.replace("OFFSET FLAT:", "")
    args = args.replace("QWORD PTR ", "")
    args = args.replace("DWORD PTR ", "")
    args = args.replace("WORD PTR ", "")
    args = args.replace("BYTE PTR ", "")
    args = re.sub(r"\s+", " ", args)
    args = args.replace(" ,", ",").replace(", ", ",")
    return args.strip()


def build_asm2vec_vectors(
    channel: dict[str, str],
    records: dict[str, dict[str, Any]],
    ordered_ids: list[str],
    *,
    output_dir: Path,
    dim: int,
    jobs: int,
    force: bool,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    name = channel["name"]
    vectors_path = output_dir / f"asm2vec_vectors_{name}.npy"
    ids_path = output_dir / f"asm2vec_ids_{name}.json"
    manifest_path = output_dir / f"asm2vec_manifest_{name}.json"
    if vectors_path.exists() and ids_path.exists() and manifest_path.exists() and not force:
        ids = json.loads(ids_path.read_text(encoding="utf-8"))
        matrix = np.load(vectors_path)
        return {str(idx): matrix[pos] for pos, idx in enumerate(ids)}, json.loads(manifest_path.read_text(encoding="utf-8"))

    funcs = []
    parse_counts: Counter[str] = Counter()
    parsed_ids = []
    for idx in ordered_ids:
        record = records.get(idx, {})
        path_text = str(record.get("normalized_asm_path") or "")
        asm_text = Path(path_text).read_text(encoding="utf-8", errors="ignore") if path_text and Path(path_text).exists() else fallback_asm(idx)
        try:
            parsed = asm2vec.parse.parse_text(asm_text, func_names=[f"fn_{sanitize_label(idx)}"])
        except Exception:
            parsed = asm2vec.parse.parse_text(fallback_asm(idx), func_names=[f"fn_{sanitize_label(idx)}"])
            parse_counts["parse_failed_fallback"] += 1
        else:
            parse_counts["parsed"] += 1
        if not parsed:
            parsed = asm2vec.parse.parse_text(fallback_asm(idx), func_names=[f"fn_{sanitize_label(idx)}"])
            parse_counts["empty_fallback"] += 1
        funcs.append(parsed[0])
        parsed_ids.append(idx)

    model = asm2vec.model.Asm2Vec(d=dim, jobs=jobs)
    repo = model.make_function_repo(funcs)
    model.train(repo)
    vector_by_name = {vf.sequential().name(): vf.v.astype(np.float32) for vf in repo.funcs()}
    matrix = np.zeros((len(parsed_ids), dim * 2), dtype=np.float32)
    for pos, idx in enumerate(parsed_ids):
        matrix[pos] = vector_by_name.get(f"fn_{sanitize_label(idx)}", np.zeros(dim * 2, dtype=np.float32))
    np.save(vectors_path, matrix)
    ids_path.write_text(json.dumps(parsed_ids, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = {
        "channel": name,
        "policy": channel["policy"],
        "asm2vec_d": dim,
        "vector_width": dim * 2,
        "function_count": len(parsed_ids),
        "parse_counts": dict(sorted(parse_counts.items())),
        "vectors": str(vectors_path),
        "ids": str(ids_path),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {str(idx): matrix[pos] for pos, idx in enumerate(parsed_ids)}, manifest


def choose_device(name: str) -> torch.device:
    if name == "cpu":
        return torch.device("cpu")
    if name == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but unavailable")
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def build_bert_vectors(
    functions: dict[str, str],
    ordered_ids: list[str],
    *,
    output_dir: Path,
    model_name: str,
    batch_size: int,
    max_length: int,
    pca_dim: int,
    device_name: str,
    force: bool,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    cls_path = output_dir / "bert_cls768.npy"
    pca_path = output_dir / "bert_pca96.npy"
    ids_path = output_dir / "bert_ids.json"
    manifest_path = output_dir / "bert_manifest.json"
    if pca_path.exists() and ids_path.exists() and manifest_path.exists() and not force:
        ids = json.loads(ids_path.read_text(encoding="utf-8"))
        matrix = np.load(pca_path)
        return {str(idx): matrix[pos] for pos, idx in enumerate(ids)}, json.loads(manifest_path.read_text(encoding="utf-8"))

    device = choose_device(device_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
    model = AutoModel.from_pretrained(model_name, local_files_only=True).to(device)
    model.eval()

    cls_matrix = np.zeros((len(ordered_ids), 768), dtype=np.float32)
    with torch.no_grad():
        for start in range(0, len(ordered_ids), batch_size):
            batch_ids = ordered_ids[start : start + batch_size]
            texts = [functions[idx] for idx in batch_ids]
            encoded = tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )
            encoded = {key: value.to(device) for key, value in encoded.items()}
            output = model(**encoded)
            pooled = getattr(output, "pooler_output", None)
            if pooled is None:
                pooled = output.last_hidden_state[:, 0, :]
            cls_matrix[start : start + len(batch_ids)] = pooled.detach().cpu().numpy().astype(np.float32)
            if (start // batch_size + 1) % 25 == 0:
                print(json.dumps({"bert_encoded": start + len(batch_ids), "total": len(ordered_ids)}, ensure_ascii=False), flush=True)

    n_components = min(pca_dim, cls_matrix.shape[0], cls_matrix.shape[1])
    pca = PCA(n_components=n_components, random_state=42)
    reduced = pca.fit_transform(cls_matrix).astype(np.float32)
    if n_components < pca_dim:
        padded = np.zeros((reduced.shape[0], pca_dim), dtype=np.float32)
        padded[:, :n_components] = reduced
        reduced = padded
    np.save(cls_path, cls_matrix)
    np.save(pca_path, reduced)
    ids_path.write_text(json.dumps(ordered_ids, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = {
        "model": model_name,
        "local_files_only": True,
        "device": str(device),
        "max_length": max_length,
        "batch_size": batch_size,
        "function_count": len(ordered_ids),
        "cls_width": int(cls_matrix.shape[1]),
        "pca_width": pca_dim,
        "pca_components": int(n_components),
        "pca_explained_variance_sum": float(np.sum(pca.explained_variance_ratio_)),
        "cls_vectors": str(cls_path),
        "pca_vectors": str(pca_path),
        "ids": str(ids_path),
        "boundary": "Base BERT CLS embeddings reduced to 96 dimensions by PCA; not the unreleased Prism fine-tuned BERT checkpoint.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {str(idx): reduced[pos] for pos, idx in enumerate(ordered_ids)}, manifest


def write_split_arrays(
    split_path: Path,
    output_dir: Path,
    functions: dict[str, str],
    left_channel: dict[str, np.ndarray],
    right_channel: dict[str, np.ndarray],
    text_vectors: dict[str, np.ndarray],
    *,
    max_rows: int,
    max_per_label: int,
    force: bool,
) -> dict[str, Any]:
    split = split_path.stem
    features_path = output_dir / f"{split}.features.npy"
    labels_path = output_dir / f"{split}.labels.npy"
    if features_path.exists() and labels_path.exists() and not force:
        labels = np.load(labels_path, mmap_mode="r")
        return {
            "rows": int(labels.shape[0]),
            "features": str(features_path),
            "labels": str(labels_path),
            "reused": True,
        }

    count_record = count_split_rows(split_path, functions, max_rows=max_rows, max_per_label=max_per_label)
    rows = int(count_record["rows"])
    features = np.lib.format.open_memmap(features_path, mode="w+", dtype=np.float32, shape=(rows, 576))
    labels = np.lib.format.open_memmap(labels_path, mode="w+", dtype=np.int64, shape=(rows,))
    label_counts: Counter[str] = Counter()
    row_idx = 0
    with split_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            left_id, right_id, label_text = parse_pair_line(split_path, line_no, line)
            if max_rows and row_idx >= max_rows:
                break
            if max_per_label and label_counts[label_text] >= max_per_label:
                continue
            if left_id not in functions or right_id not in functions:
                continue
            features[row_idx, :] = np.concatenate(
                [
                    left_channel[left_id],
                    right_channel[left_id],
                    text_vectors[left_id],
                    left_channel[right_id],
                    right_channel[right_id],
                    text_vectors[right_id],
                ]
            )
            labels[row_idx] = int(label_text)
            label_counts[label_text] += 1
            row_idx += 1
            if row_idx % 250000 == 0:
                print(json.dumps({"split": split, "rows_written": row_idx, "total": rows}, ensure_ascii=False), flush=True)
    features.flush()
    labels.flush()
    return {
        **count_record,
        "features": str(features_path),
        "labels": str(labels_path),
        "row_width": 576,
        "label_counts_written": dict(sorted(label_counts.items())),
    }


def count_split_rows(
    split_path: Path,
    functions: dict[str, str],
    *,
    max_rows: int,
    max_per_label: int,
) -> dict[str, Any]:
    rows = 0
    scanned = 0
    skipped_missing = 0
    label_counts: Counter[str] = Counter()
    with split_path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            scanned += 1
            left_id, right_id, label = parse_pair_line(split_path, line_no, line)
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


def summarize_compile_records(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(str(record.get("status") or "") for record in records.values())
    instruction_counts = [int(record.get("normalized_instruction_count") or 0) for record in records.values()]
    return {
        "function_count": len(records),
        "status_counts": dict(sorted(status_counts.items())),
        "normalized_instruction_min": min(instruction_counts) if instruction_counts else 0,
        "normalized_instruction_max": max(instruction_counts) if instruction_counts else 0,
        "normalized_instruction_avg": round(sum(instruction_counts) / len(instruction_counts), 3) if instruction_counts else 0,
    }


if __name__ == "__main__":
    raise SystemExit(main())
