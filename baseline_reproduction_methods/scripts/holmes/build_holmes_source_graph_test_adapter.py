from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import torch


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_holmes_ojclone_adapter import PairData, code_to_graph, load_functions, read_pairs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a HOLMES-compatible source-graph test adapter.")
    parser.add_argument("--source-dir", type=Path, required=True, help="Directory with data.jsonl and test.txt")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--prefix", default="bcbEA")
    parser.add_argument("--dataset-name", default="BCB-LLM-Refined-HardCases")
    parser.add_argument("--max-nodes", type=int, default=256)
    args = parser.parse_args()

    functions = load_functions(args.source_dir / "data.jsonl")
    pairs = read_pairs(args.source_dir / "test.txt")
    processed_dir = args.output_dir / args.prefix / "test" / "processed"
    raw_dir = args.output_dir / args.prefix / "test" / "raw"
    processed_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    graph_cache: dict[str, tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = {}
    label_counts: Counter[str] = Counter()
    raw_lines: list[str] = []
    for out_idx, (idx1, idx2, label) in enumerate(pairs):
        if idx1 not in functions or idx2 not in functions:
            raise ValueError(f"pair {out_idx} references missing function id(s): {idx1}, {idx2}")
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

    raw_file = raw_dir / "test.txt"
    raw_file.write_text("".join(raw_lines), encoding="utf-8")
    manifest = {
        "schema_version": "eviclone-holmes-source-graph-test-adapter/v1",
        "dataset_name": args.dataset_name,
        "source_dir": str(args.source_dir),
        "output_dir": str(args.output_dir),
        "prefix": args.prefix,
        "max_nodes": args.max_nodes,
        "rows": len(pairs),
        "function_rows": len(functions),
        "graph_cache_entries": len(graph_cache),
        "label_counts": dict(sorted(label_counts.items())),
        "processed_dir": str(processed_dir),
        "raw_file": str(raw_file),
        "claim_boundary": (
            "HOLMES-compatible lightweight source graph adapter. This preserves the HOLMES model input shape "
            "but is not the original HOLMES PDG extraction pipeline."
        ),
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "rows": len(pairs)}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
