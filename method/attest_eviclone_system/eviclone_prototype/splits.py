from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen

from .dataset import ClonePair, load_pairs


CODEXGLUE_SPLIT_URLS = {
    "train": "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/Code-Code/Clone-detection-BigCloneBench/dataset/train.txt",
    "valid": "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/Code-Code/Clone-detection-BigCloneBench/dataset/valid.txt",
    "test": "https://raw.githubusercontent.com/microsoft/CodeXGLUE/main/Code-Code/Clone-detection-BigCloneBench/dataset/test.txt",
}

CODEXGLUE_SPLIT_COUNTS = {
    "train": 901_028,
    "valid": 415_416,
    "test": 415_416,
}
SPLIT_NAMES = ("train", "valid", "test")


def codexglue_ratios() -> dict[str, float]:
    total = float(sum(CODEXGLUE_SPLIT_COUNTS.values()))
    return {name: count / total for name, count in CODEXGLUE_SPLIT_COUNTS.items()}


def parse_split_names(value: str | None) -> tuple[str, ...]:
    if not value or not str(value).strip():
        return ()
    result: list[str] = []
    for part in str(value).split(","):
        name = part.strip().lower()
        if not name:
            continue
        if name not in SPLIT_NAMES:
            raise ValueError(f"unsupported split name: {name}")
        if name not in result:
            result.append(name)
    return tuple(result)


def load_split_pair_ids(split_dir: Path, split_names: tuple[str, ...]) -> set[int]:
    result: set[int] = set()
    for split in split_names:
        path = split_dir / f"{split}.jsonl"
        if not path.exists():
            raise FileNotFoundError(f"split jsonl not found: {path}")
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                text = line.strip()
                if not text:
                    continue
                obj = json.loads(text)
                result.add(int(obj["pair_id"]))
    return result


def resolve_reference_sources(
    train_source: str = "",
    valid_source: str = "",
    test_source: str = "",
) -> dict[str, str]:
    return {
        "train": train_source.strip() or CODEXGLUE_SPLIT_URLS["train"],
        "valid": valid_source.strip() or CODEXGLUE_SPLIT_URLS["valid"],
        "test": test_source.strip() or CODEXGLUE_SPLIT_URLS["test"],
    }


def split_pairs_to_codexglue(
    dataset_path: Path,
    output_dir: Path,
    *,
    reference_sources: dict[str, str] | None = None,
    unmatched_policy: str = "ratio",
) -> dict[str, object]:
    pairs = load_pairs(dataset_path)
    reference_sources = reference_sources or resolve_reference_sources()
    exact_assignments = match_pairs_against_reference(pairs, reference_sources)
    selected_pairs = [pair for pair in pairs if pair.pair_id in exact_assignments]

    split_sources: dict[int, str] = {pair_id: "codexglue_exact" for pair_id in exact_assignments}
    fallback_assignments: dict[int, str] = {}
    dropped_pairs = 0

    if unmatched_policy == "ratio":
        unmatched_pairs = [pair for pair in pairs if pair.pair_id not in exact_assignments]
        fallback_assignments = stratified_ratio_split(unmatched_pairs, codexglue_ratios())
        exact_assignments.update(fallback_assignments)
        selected_pairs = pairs
        split_sources.update({pair_id: "codexglue_ratio_fallback" for pair_id in fallback_assignments})
    elif unmatched_policy == "drop":
        dropped_pairs = len(pairs) - len(selected_pairs)
    else:
        raise ValueError(f"unsupported unmatched_policy: {unmatched_policy}")

    output_dir.mkdir(parents=True, exist_ok=True)
    by_split: dict[str, list[ClonePair]] = {"train": [], "valid": [], "test": []}
    for pair in selected_pairs:
        split = exact_assignments[pair.pair_id]
        by_split[split].append(pair)

    functions, conflicts = build_function_table(selected_pairs)
    write_function_table(output_dir / "data.jsonl", functions)
    write_pair_files(output_dir, by_split, split_sources)

    summary = {
        "dataset": str(dataset_path.resolve()),
        "output_dir": str(output_dir.resolve()),
        "reference_sources": reference_sources,
        "unmatched_policy": unmatched_policy,
        "total_pairs": len(pairs),
        "selected_pairs": len(selected_pairs),
        "dropped_pairs": dropped_pairs,
        "exact_match_pairs": len([x for x in split_sources.values() if x == "codexglue_exact"]),
        "ratio_fallback_pairs": len([x for x in split_sources.values() if x == "codexglue_ratio_fallback"]),
        "split_counts": {name: len(items) for name, items in by_split.items()},
        "function_count": len(functions),
        "function_conflicts": len(conflicts),
        "function_conflict_ids": conflicts[:20],
        "codexglue_reference_counts": dict(CODEXGLUE_SPLIT_COUNTS),
        "codexglue_reference_ratios": {k: round(v, 6) for k, v in codexglue_ratios().items()},
    }
    (output_dir / "split_manifest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return summary


def match_pairs_against_reference(
    pairs: list[ClonePair],
    reference_sources: dict[str, str],
) -> dict[int, str]:
    lookup: dict[tuple[str, str, int], list[int]] = defaultdict(list)
    for pair in pairs:
        a = str(pair.function_id_a).strip()
        b = str(pair.function_id_b).strip()
        label = int(pair.label)
        lookup[(a, b, label)].append(pair.pair_id)
        if a != b:
            lookup[(b, a, label)].append(pair.pair_id)

    assignments: dict[int, str] = {}
    for split in ("train", "valid", "test"):
        for a, b, label in iter_reference_pairs(reference_sources[split]):
            for pair_id in lookup.get((a, b, label), []):
                current = assignments.get(pair_id)
                if current and current != split:
                    raise ValueError(f"pair {pair_id} matched multiple reference splits: {current} vs {split}")
                assignments[pair_id] = split
    return assignments


def iter_reference_pairs(source: str) -> Iterable[tuple[str, str, int]]:
    if source.startswith("http://") or source.startswith("https://"):
        with urlopen(source) as response:
            for raw in response:
                text = raw.decode("utf-8").strip()
                if not text:
                    continue
                yield parse_reference_line(text, source)
        return

    path = Path(source)
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            yield parse_reference_line(text, str(path))


def parse_reference_line(line: str, source_name: str) -> tuple[str, str, int]:
    parts = line.split()
    if len(parts) != 3:
        raise ValueError(f"invalid reference line in {source_name}: {line!r}")
    return parts[0], parts[1], int(parts[2])


def stratified_ratio_split(
    pairs: list[ClonePair],
    ratios: dict[str, float],
) -> dict[int, str]:
    buckets: dict[tuple[int, str], list[ClonePair]] = defaultdict(list)
    for pair in pairs:
        key = (int(pair.label), str(pair.functionality_id or pair.functionality_name or "unknown"))
        buckets[key].append(pair)

    assignments: dict[int, str] = {}
    for items in buckets.values():
        ordered = sorted(items, key=stable_pair_sort_key)
        counts = allocate_counts(len(ordered), ratios)
        start = 0
        for split in ("train", "valid", "test"):
            end = start + counts[split]
            for pair in ordered[start:end]:
                assignments[pair.pair_id] = split
            start = end
    return assignments


def stable_pair_sort_key(pair: ClonePair) -> str:
    token = "\t".join(
        [
            str(pair.pair_id),
            str(pair.function_id_a),
            str(pair.function_id_b),
            str(pair.label),
            str(pair.functionality_id),
        ]
    )
    return hashlib.sha1(token.encode("utf-8")).hexdigest()


def allocate_counts(total: int, ratios: dict[str, float]) -> dict[str, int]:
    raw = {name: total * ratios[name] for name in ("train", "valid", "test")}
    counts = {name: int(raw[name]) for name in raw}
    remainder = total - sum(counts.values())
    if remainder > 0:
        order = sorted(
            ("train", "valid", "test"),
            key=lambda name: (raw[name] - counts[name], ratios[name]),
            reverse=True,
        )
        for name in order[:remainder]:
            counts[name] += 1
    return counts


def build_function_table(pairs: list[ClonePair]) -> tuple[dict[str, str], list[str]]:
    functions: dict[str, str] = {}
    conflicts: set[str] = set()

    def observe(function_id: str, code: str) -> None:
        existing = functions.get(function_id)
        if existing is None:
            functions[function_id] = code
            return
        if existing != code:
            conflicts.add(function_id)

    for pair in pairs:
        observe(str(pair.function_id_a), pair.code_a)
        observe(str(pair.function_id_b), pair.code_b)
    return functions, sorted(conflicts, key=sort_function_id)


def write_function_table(path: Path, functions: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for function_id in sorted(functions, key=sort_function_id):
            handle.write(json.dumps({"idx": function_id, "func": functions[function_id]}, ensure_ascii=False) + "\n")


def write_pair_files(
    output_dir: Path,
    by_split: dict[str, list[ClonePair]],
    split_sources: dict[int, str],
) -> None:
    for split in ("train", "valid", "test"):
        pairs = sorted(by_split[split], key=lambda item: item.pair_id)
        txt_path = output_dir / f"{split}.txt"
        jsonl_path = output_dir / f"{split}.jsonl"
        with txt_path.open("w", encoding="utf-8", newline="\n") as txt_handle, jsonl_path.open(
            "w", encoding="utf-8", newline="\n"
        ) as jsonl_handle:
            for pair in pairs:
                txt_handle.write(f"{pair.function_id_a}\t{pair.function_id_b}\t{pair.label}\n")
                record = dict(pair.raw or {})
                record["split"] = split
                record["split_source"] = split_sources.get(pair.pair_id, "unknown")
                jsonl_handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def sort_function_id(value: str) -> tuple[int, int | str]:
    text = str(value).strip()
    if text.isdigit():
        return (0, int(text))
    return (1, text)
