"""Ablation helpers — the non-execution verdict and input-synthesis variants.

The ablation TOGGLES live in :class:`~attest.config.AblationConfig`; the
pipeline reads them. This module holds the alternative logic a toggle selects:

  * ``no_execution`` -> :func:`text_similarity_verdict`, which decides clone-ness
    from the textual similarity of the two COMPLETED (made-runnable) harnesses
    instead of their runtime behavior. This isolates the contribution of real
    execution from the contribution of the completion step itself.
"""

from __future__ import annotations

import difflib
import re

from ..schemas import Verdict


def _normalize_code(src: str) -> list[str]:
    """Crude tokenization for similarity: drop comments/whitespace, keep tokens."""
    # strip block and line comments
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    src = re.sub(r"//.*", " ", src)
    # tokens: identifiers, numbers, or single non-space symbols
    return re.findall(r"[A-Za-z_]\w+|\d+|[^\s\w]", src)


def text_similarity(a: str, b: str) -> float:
    """Token-sequence similarity ratio in [0, 1]."""
    ta, tb = _normalize_code(a), _normalize_code(b)
    if not ta and not tb:
        return 1.0
    return difflib.SequenceMatcher(None, ta, tb).ratio()


def text_similarity_verdict(
    source_a: str, source_b: str, threshold: float
) -> tuple[Verdict, float]:
    """Clone iff the completed harnesses are textually similar enough."""
    sim = text_similarity(source_a, source_b)
    verdict = Verdict.CLONE if sim >= threshold else Verdict.NON_CLONE
    return verdict, sim
