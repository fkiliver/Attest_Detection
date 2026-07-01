from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ClonePair:
    pair_id: int
    function_id_a: str
    function_id_b: str
    functionality_id: str
    functionality_name: str
    functionality_description: str
    source: str
    label: int
    code_a: str
    code_b: str
    bcb_type: str = ""
    syntactic_type: str = ""
    search_heuristic: str = ""
    raw: dict[str, Any] | None = None

    @classmethod
    def from_json(cls, obj: dict[str, Any]) -> "ClonePair":
        return cls(
            pair_id=int(obj.get("pair_id", 0)),
            function_id_a=str(obj.get("function_id_a", "")),
            function_id_b=str(obj.get("function_id_b", "")),
            functionality_id=str(obj.get("functionality_id", "")),
            functionality_name=str(obj.get("functionality_name", "")),
            functionality_description=str(obj.get("functionality_description", "")),
            source=str(obj.get("source", "")),
            label=int(obj.get("label", 0)),
            code_a=str(obj.get("code_a", "")),
            code_b=str(obj.get("code_b", "")),
            bcb_type=str(obj.get("bcb_type", "")),
            syntactic_type=str(obj.get("syntactic_type", "")),
            search_heuristic=str(obj.get("search_heuristic", "")),
            raw=obj,
        )

    def target_context(self) -> str:
        parts = []
        if self.functionality_name:
            parts.append(f"BCB functionality: {self.functionality_name}")
        if self.functionality_description:
            parts.append(f"Description: {self.functionality_description}")
        return "\n".join(parts)


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{line_no}: {exc}") from exc


def load_pairs(
    path: Path,
    *,
    limit: int = 0,
    offset: int = 0,
    pair_id: int = 0,
) -> list[ClonePair]:
    result: list[ClonePair] = []
    skipped = 0
    for obj in iter_jsonl(path):
        item = ClonePair.from_json(obj)
        if pair_id and item.pair_id != pair_id:
            continue
        if not pair_id and skipped < offset:
            skipped += 1
            continue
        result.append(item)
        if limit and len(result) >= limit:
            break
    return result


def summarize_pairs(items: list[ClonePair]) -> dict[str, Any]:
    label_counts = Counter(str(x.label) for x in items)
    source_counts = Counter(x.source or "unknown" for x in items)
    functionality_counts = Counter(x.functionality_name or x.functionality_id or "unknown" for x in items)
    syntactic_counts = Counter(x.syntactic_type or "unknown" for x in items)
    return {
        "total": len(items),
        "label_counts": dict(sorted(label_counts.items())),
        "source_counts": dict(source_counts.most_common()),
        "functionality_counts": dict(functionality_counts.most_common()),
        "syntactic_type_counts": dict(syntactic_counts.most_common()),
    }
