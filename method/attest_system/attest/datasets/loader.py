"""Dataset loaders for BigCloneBench, OJClone, and GCJ.

All three follow the standard GraphCodeBERT clone-detection layout:
  * ``data.jsonl``  — one object per function: ``{"idx": "<str>", "func": "<code>"}``
  * ``{train,valid,test}.txt`` — tab-separated ``idx1<TAB>idx2<TAB>label`` (0/1)

This module yields normalized :class:`~attest.schemas.Pair` objects with
the correct per-dataset language attached (BCB/GCJ -> java, OJClone -> c).
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from ..schemas import Pair, Snippet

# Default dataset root. Override via the ATTEST_DATA_ROOT environment variable
# or per-call through DatasetSpec.root.
DEFAULT_ROOT = Path(
    os.environ.get("ATTEST_DATA_ROOT", "data/clone_splits")
)

# Per-dataset language (verified by inspecting data.jsonl).
DATASET_LANG = {
    "BigCloneBench": "java",
    "OJClone": "c",
    "GCJ": "java",
}

# Friendly aliases.
ALIASES = {
    "bcb": "BigCloneBench",
    "bigclonebench": "BigCloneBench",
    "ojclone": "OJClone",
    "oj": "OJClone",
    "gcj": "GCJ",
}


@dataclass
class DatasetSpec:
    name: str                      # canonical dataset dir name
    root: Path = DEFAULT_ROOT
    split: str = "test"            # train | valid | test

    @property
    def dir(self) -> Path:
        return self.root / self.name

    @property
    def language(self) -> str:
        return DATASET_LANG[self.name]


def resolve_name(name: str) -> str:
    key = name.strip()
    return ALIASES.get(key.lower(), key)


def _load_funcs(spec: DatasetSpec) -> dict[str, str]:
    funcs: dict[str, str] = {}
    with open(spec.dir / "data.jsonl", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            funcs[str(r["idx"])] = r["func"]
    return funcs


def _iter_pairs_raw(spec: DatasetSpec):
    split_file = spec.dir / f"{spec.split}.txt"
    with open(split_file, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            a, b, lab = parts[0], parts[1], parts[2]
            yield a, b, int(lab)


# Source .pkl files (from DSFM) carry the per-pair RAW clone-type label that the
# binarized {split}.txt discards. For BigCloneBench these are:
#   -5 = non-clone
#    1 = Type-1, 2 = Type-2, 3 = Type-3 (strong/VST-ST),
#    4 = Type-3 (moderate, MT), 5 = WT (weak Type-3 / Type-4) — the noisy bulk.
# The .pkl is a sequence of ((id1,id2), raw_label) objects, positionally aligned
# with {split}.txt (verified). We read it to enable clone-type-stratified eval.
_DSFM_SRC = Path(os.environ.get("ATTEST_DSFM_SRC", "data/dsfm/datasets"))


def _load_raw_labels(spec: DatasetSpec) -> list[int] | None:
    """Load per-pair raw clone-type labels from the source .pkl, aligned with
    {split}.txt order. Returns None if the source file is unavailable."""
    import pickle

    pkl = _DSFM_SRC / spec.name / f"{spec.split}.pkl"
    if not pkl.exists():
        return None
    labels: list[int] = []
    with open(pkl, "rb") as f:
        while True:
            try:
                obj = pickle.load(f)
            except EOFError:
                break
            # obj == ((id1, id2), raw_label)
            try:
                labels.append(int(obj[1]))
            except (IndexError, TypeError, ValueError):
                return None
    return labels


def load_pairs(
    name: str,
    *,
    root: Path | None = None,
    split: str = "test",
    limit: int | None = None,
    balanced: bool = True,
    seed: int = 0,
    max_code_chars: int | None = None,
    clone_types: set[int] | None = None,
) -> list[Pair]:
    """Load pairs from a dataset split as normalized :class:`Pair` objects.

    Args:
        name: dataset name or alias (bcb/ojclone/gcj).
        limit: cap on number of pairs returned (after optional balancing).
        balanced: if True and limited, sample an equal number of clone /
            non-clone pairs (the splits are very imbalanced toward non-clone).
        max_code_chars: skip pairs where either snippet exceeds this length
            (keeps per-pair LLM cost and runtime bounded for the pilot).
        clone_types: if given, restrict POSITIVE (clone) pairs to these raw
            clone-type labels (read from the source .pkl). E.g. {1,2,3,4} keeps
            Type-1/2/3 (reliable labels) and drops the noisy WT bulk (raw 5).
            Negative pairs are unaffected. Requires the source .pkl; raises if
            absent so the caller knows the filter could not be applied.
    """
    spec = DatasetSpec(resolve_name(name), root or DEFAULT_ROOT, split)
    funcs = _load_funcs(spec)
    rng = random.Random(seed)

    raw_labels: list[int] | None = None
    if clone_types is not None:
        raw_labels = _load_raw_labels(spec)
        if raw_labels is None:
            raise FileNotFoundError(
                f"clone_types filter requested but source .pkl not found for "
                f"{spec.name}/{spec.split} (looked in {_DSFM_SRC})"
            )

    pos: list[tuple[str, str, int]] = []
    neg: list[tuple[str, str, int]] = []
    for i, (a, b, lab) in enumerate(_iter_pairs_raw(spec)):
        if a not in funcs or b not in funcs:
            continue
        if max_code_chars is not None and (
            len(funcs[a]) > max_code_chars or len(funcs[b]) > max_code_chars
        ):
            continue
        if lab == 1:
            # Apply the clone-type filter to positives only.
            if clone_types is not None and raw_labels is not None:
                if i >= len(raw_labels) or raw_labels[i] not in clone_types:
                    continue
            pos.append((a, b, lab))
        else:
            neg.append((a, b, lab))

    if limit is not None and balanced:
        k = limit // 2
        rng.shuffle(pos)
        rng.shuffle(neg)
        chosen = pos[:k] + neg[: limit - k]
        rng.shuffle(chosen)
    else:
        chosen = pos + neg
        rng.shuffle(chosen)
        if limit is not None:
            chosen = chosen[:limit]

    lang = spec.language
    out: list[Pair] = []
    for a, b, lab in chosen:
        out.append(
            Pair(
                pair_id=f"{spec.name}_{spec.split}_{a}_{b}",
                a=Snippet(id=a, code=funcs[a], language=lang),
                b=Snippet(id=b, code=funcs[b], language=lang),
                label=lab,
                meta={"dataset": spec.name, "split": spec.split},
            )
        )
    return out
