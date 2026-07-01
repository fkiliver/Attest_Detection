from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

import torch
from torch_geometric.data import Data


STATEMENTS = [
    "NULL",
    "AssignStmt",
    "DefinitionStmt",
    "IdentityStmt",
    "IfStmt",
    "ReturnStmt",
    "BreakpointStmt",
    "EnterMonitorStmt",
    "ExitMonitorStmt",
    "GotoStmt",
    "InvokeStmt",
    "LookupSwitchStmt",
    "MonitorStmt",
    "NopStmt",
    "RetStmt",
    "ReturnVoidStmt",
    "TableSwitchStmt",
    "ThrowStmt",
]
STMT_TO_INDEX = {name: i for i, name in enumerate(STATEMENTS)}
IDENT_RE = re.compile(r"\b[_A-Za-z]\w*\b")
KEYWORDS = {
    "alignas", "alignof", "and", "asm", "auto", "bool", "break", "case", "catch", "char", "class",
    "const", "continue", "default", "delete", "do", "double", "else", "enum", "extern", "false",
    "float", "for", "friend", "goto", "if", "inline", "int", "long", "namespace", "new", "operator",
    "or", "private", "protected", "public", "register", "return", "short", "signed", "sizeof", "static",
    "struct", "switch", "template", "this", "throw", "true", "try", "typedef", "typename", "union",
    "unsigned", "using", "virtual", "void", "volatile", "while", "include", "define", "cin", "cout",
    "scanf", "printf", "gets", "strlen", "strcmp", "memset", "sqrt", "sort", "vector", "string",
}
TYPE_WORDS = {
    "char", "double", "float", "int", "long", "short", "signed", "unsigned", "bool", "void", "string",
    "vector", "size_t", "ll",
}


class PairData(Data):
    def __inc__(self, key: str, value: Any, *args: Any, **kwargs: Any) -> int:
        if key in {"edgedata_index1", "edgecontrol_index1", "edge_index1"}:
            return int(self.x1.size(0))
        if key in {"edgedata_index2", "edgecontrol_index2", "edge_index2"}:
            return int(self.x2.size(0))
        return super().__inc__(key, value, *args, **kwargs)

    def __cat_dim__(self, key: str, value: Any, *args: Any, **kwargs: Any) -> int:
        if "index" in key or "face" in key:
            return 1
        return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a HOLMES-compatible OJClone graph adapter dataset.")
    parser.add_argument("--source-dir", type=Path, default=Path("eviclone_runs/baseline_reproduction/graphcodebert_dsfm_splits/OJClone"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--train-rows", type=int, default=3000)
    parser.add_argument("--val-rows", type=int, default=3000)
    parser.add_argument("--test-rows", type=int, default=3000)
    parser.add_argument("--train-sampling", choices=["balanced", "natural"], default="balanced")
    parser.add_argument("--val-sampling", choices=["balanced", "natural"], default="balanced")
    parser.add_argument("--test-sampling", choices=["balanced", "natural"], default="natural")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-nodes", type=int, default=256)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    functions = load_functions(args.source_dir / "data.jsonl")
    graph_cache: dict[str, tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = {}
    split_specs = {
        "train": ("train.txt", args.train_rows, args.train_sampling, "train.txt"),
        "val": ("valid.txt", args.val_rows, args.val_sampling, "dev.txt"),
        "test": ("test.txt", args.test_rows, args.test_sampling, "test.txt"),
    }
    split_records = {}
    for split, (source_name, limit, sampling, raw_name) in split_specs.items():
        pairs = read_pairs(args.source_dir / source_name)
        selected = select_pairs(pairs, limit=limit, sampling=sampling, seed=args.seed + len(split))
        split_dir = args.output_dir / "ojcloneEA" / split
        processed_dir = split_dir / "processed"
        raw_dir = split_dir / "raw"
        processed_dir.mkdir(parents=True, exist_ok=True)
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_lines = []
        label_counts = Counter()
        for out_idx, (idx1, idx2, label) in enumerate(selected):
            graph1 = graph_cache.get(idx1)
            if graph1 is None:
                graph1 = code_to_graph(functions[idx1], max_nodes=args.max_nodes)
                graph_cache[idx1] = graph1
            graph2 = graph_cache.get(idx2)
            if graph2 is None:
                graph2 = code_to_graph(functions[idx2], max_nodes=args.max_nodes)
                graph_cache[idx2] = graph2
            x1, data1, control1 = graph1
            x2, data2, control2 = graph2
            pair = PairData(
                x1=x1,
                x2=x2,
                edgedata_index1=data1,
                edgedata_index2=data2,
                edgecontrol_index1=control1,
                edgecontrol_index2=control2,
                y=torch.tensor([float(label)], dtype=torch.float32),
                sample_id=torch.tensor([out_idx], dtype=torch.long),
            )
            torch.save(pair, processed_dir / f"data_{out_idx}.pt")
            raw_lines.append(f"{idx1}\t{idx2}\t{label}\n")
            label_counts[str(label)] += 1
            if (out_idx + 1) % 1000 == 0:
                print(json.dumps({"split": split, "written": out_idx + 1}, ensure_ascii=False), flush=True)
        (raw_dir / raw_name).write_text("".join(raw_lines), encoding="utf-8")
        split_records[split] = {
            "source": str(args.source_dir / source_name),
            "sampling": sampling,
            "requested_rows": limit,
            "rows": len(selected),
            "label_counts": dict(label_counts),
            "processed_dir": str(processed_dir),
            "raw_file": str(raw_dir / raw_name),
        }
    manifest = {
        "schema_version": "eviclone-holmes-ojclone-adapter/v1",
        "source_dir": str(args.source_dir),
        "output_dir": str(args.output_dir),
        "variant": "EA",
        "max_nodes": args.max_nodes,
        "statement_labels": STATEMENTS,
        "graph_cache_entries": len(graph_cache),
        "splits": split_records,
        "claim_boundary": (
            "OJClone HOLMES adapter generated from C/C++ source by a lightweight statement/control/data graph builder. "
            "It is HOLMES-compatible but not the original HOLMES PDG extraction pipeline."
        ),
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(args.output_dir / "manifest.json"), "splits": split_records}, ensure_ascii=False), flush=True)
    return 0


def load_functions(path: Path) -> dict[str, str]:
    functions: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            functions[str(row["idx"])] = str(row["func"])
    return functions


def read_pairs(path: Path) -> list[tuple[str, str, int]]:
    pairs: list[tuple[str, str, int]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            pairs.append((parts[0], parts[1], int(parts[2])))
    return pairs


def select_pairs(
    pairs: list[tuple[str, str, int]],
    *,
    limit: int,
    sampling: str,
    seed: int,
) -> list[tuple[str, str, int]]:
    if limit <= 0 or limit >= len(pairs):
        return pairs
    rng = random.Random(seed)
    if sampling == "natural":
        selected = list(pairs)
        rng.shuffle(selected)
        return selected[:limit]
    positives = [pair for pair in pairs if pair[2] == 1]
    negatives = [pair for pair in pairs if pair[2] == 0]
    rng.shuffle(positives)
    rng.shuffle(negatives)
    pos_target = min(len(positives), limit // 2)
    neg_target = min(len(negatives), limit - pos_target)
    if pos_target + neg_target < limit and pos_target < len(positives):
        pos_target = min(len(positives), limit - neg_target)
    selected = positives[:pos_target] + negatives[:neg_target]
    rng.shuffle(selected)
    return selected


def code_to_graph(code: str, *, max_nodes: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    statements = split_statements(code)[:max_nodes]
    if not statements:
        statements = [""]
    labels = [classify_statement(stmt) for stmt in statements]
    x = torch.zeros((len(labels), len(STATEMENTS)), dtype=torch.float32)
    for i, label in enumerate(labels):
        x[i, STMT_TO_INDEX[label]] = 1.0
    control_edges = build_control_edges(statements)
    data_edges = build_data_edges(statements)
    return x, edge_tensor(data_edges), edge_tensor(control_edges)


def split_statements(code: str) -> list[str]:
    cleaned = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    cleaned = re.sub(r"//.*", " ", cleaned)
    parts = re.split(r"([{};])|\n", cleaned)
    statements: list[str] = []
    current: list[str] = []
    for part in parts:
        if part is None:
            continue
        text = part.strip()
        if not text:
            continue
        current.append(text)
        if text in {";", "{", "}"}:
            stmt = " ".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
    if current:
        statements.append(" ".join(current).strip())
    return [stmt for stmt in statements if stmt]


def classify_statement(stmt: str) -> str:
    text = stmt.strip()
    lower = text.lower()
    if not text:
        return "NULL"
    if lower.startswith("return ;") or lower == "return;" or lower == "return":
        return "ReturnVoidStmt"
    if lower.startswith("return"):
        return "ReturnStmt"
    if lower.startswith("throw"):
        return "ThrowStmt"
    if lower.startswith("switch"):
        return "LookupSwitchStmt"
    if lower.startswith("case") or lower.startswith("default"):
        return "TableSwitchStmt"
    if lower.startswith(("if", "for", "while", "do")):
        return "IfStmt"
    if lower.startswith(("break", "continue", "goto")):
        return "GotoStmt"
    if any(word in lower for word in ["scanf", "printf", "cin", "cout", "gets", "puts", "strlen", "strcmp"]):
        return "InvokeStmt"
    if looks_like_definition(lower):
        return "DefinitionStmt"
    if is_assignment(text):
        return "AssignStmt"
    if "(" in text and ")" in text:
        return "InvokeStmt"
    return "NopStmt"


def looks_like_definition(lower: str) -> bool:
    tokens = lower.replace("*", " ").replace("&", " ").split()
    return bool(tokens and tokens[0] in TYPE_WORDS)


def is_assignment(text: str) -> bool:
    if "==" in text or "<=" in text or ">=" in text or "!=" in text:
        text = text.replace("==", "").replace("<=", "").replace(">=", "").replace("!=", "")
    return "=" in text or "+=" in text or "-=" in text or "*=" in text or "/=" in text


def build_control_edges(statements: list[str]) -> list[tuple[int, int]]:
    n = len(statements)
    edges: list[tuple[int, int]] = []
    for i in range(n - 1):
        edges.append((i, i + 1))
    for i, stmt in enumerate(statements[:-1]):
        lower = stmt.lower().strip()
        if lower.startswith(("if", "for", "while", "switch")) and i + 2 < n:
            edges.append((i, i + 2))
        if lower.startswith(("for", "while")) and i > 0:
            edges.append((i, max(0, i - 1)))
    return edges


def build_data_edges(statements: list[str]) -> list[tuple[int, int]]:
    last_def: dict[str, int] = {}
    edges: list[tuple[int, int]] = []
    for i, stmt in enumerate(statements):
        identifiers = [tok for tok in IDENT_RE.findall(stmt) if tok not in KEYWORDS]
        defined = defined_identifier(stmt)
        for name in identifiers:
            if name == defined:
                continue
            if name in last_def:
                edges.append((last_def[name], i))
        if defined:
            last_def[defined] = i
    return edges


def defined_identifier(stmt: str) -> str | None:
    text = stmt.strip()
    match = re.search(r"\b([_A-Za-z]\w*)\s*(?:=|\+=|-=|\*=|/=)", text)
    if match:
        return match.group(1)
    tokens = text.replace("*", " ").replace("&", " ").replace(",", " ").split()
    if tokens and tokens[0] in TYPE_WORDS and len(tokens) > 1:
        candidate = re.sub(r"[^_A-Za-z0-9]", "", tokens[1])
        if candidate and IDENT_RE.fullmatch(candidate):
            return candidate
    return None


def edge_tensor(edges: list[tuple[int, int]]) -> torch.Tensor:
    if not edges:
        return torch.empty((2, 0), dtype=torch.long)
    return torch.tensor(edges, dtype=torch.long).t().contiguous()


if __name__ == "__main__":
    raise SystemExit(main())
