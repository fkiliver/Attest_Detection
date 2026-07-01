"""Rule-based normalization and comparison of two harnesses' observations.

Stage 4 compares snippet A's and snippet B's per-case outputs (the tagged JSON
values produced by the harness canonicalizer). Many differences are harmless
representation artifacts — float rounding, collection ordering, trailing
whitespace — and we erase those with fixed rules BEFORE invoking the LLM diff
explainer on whatever residual difference remains. Erasing the easy cases keeps
the LLM's job narrow (precision) and cheap.

The comparison understands the harness's tagged encodings:
  {"__f64__": n}          -> float, compared with absolute+relative tolerance
  {"__bytes__"|"__bytes_ref__": ...} -> raw bytes, equal iff sha256 (and len) match
  {"__bignum__": s}       -> exact decimal string compare
  {"__opaque__": cls}     -> only equal if same class + same toString
  {"error": {type,message}} (at result level) -> compare primarily on type
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .config import DecisionConfig


@dataclass
class CaseDiff:
    """A residual difference for one input case, to hand to the LLM explainer."""

    id: str
    a: Any
    b: Any


def results_by_id(outputs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index a harness ``outputs.json`` by case id (the alignment key)."""
    out: dict[str, dict[str, Any]] = {}
    for r in (outputs or {}).get("results", []):
        if isinstance(r, dict) and "id" in r:
            out[str(r["id"])] = r
    return out


def _is_tag(v: Any, key: str) -> bool:
    return isinstance(v, dict) and key in v


def _floats_equal(x: float, y: float, cfg: DecisionConfig) -> bool:
    if math.isnan(x) and math.isnan(y):
        return True
    if math.isinf(x) or math.isinf(y):
        return x == y
    return abs(x - y) <= max(cfg.float_abs_eps, cfg.float_rel_eps * max(abs(x), abs(y)))


def _coerce_f64(v: Any) -> float | None:
    if _is_tag(v, "__f64__"):
        inner = v["__f64__"]
        if isinstance(inner, str):
            return {"NaN": math.nan, "Infinity": math.inf, "-Infinity": -math.inf}.get(inner)
        return float(inner)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return None


def values_equivalent(a: Any, b: Any, cfg: DecisionConfig, *, unordered: bool = False) -> bool:
    """Return True if observations ``a`` and ``b`` are behaviorally equivalent.

    Applies tolerance to floats, sha256 equality to byte blobs, and (optionally)
    order-insensitive comparison to lists.
    """
    # bytes blobs: compare by digest (and length when inline)
    a_b = _bytes_sig(a)
    b_b = _bytes_sig(b)
    if a_b is not None or b_b is not None:
        return a_b is not None and a_b == b_b

    # floats (tagged or bare numeric vs tagged): tolerance compare
    fa, fb = _coerce_f64(a), _coerce_f64(b)
    if fa is not None and fb is not None:
        # but don't collapse an integer-vs-float intent unless both numeric;
        # here both are numeric so tolerance is appropriate
        return _floats_equal(fa, fb, cfg)

    if _is_tag(a, "__bignum__") or _is_tag(b, "__bignum__"):
        return _is_tag(a, "__bignum__") and _is_tag(b, "__bignum__") and a["__bignum__"] == b["__bignum__"]

    if _is_tag(a, "__opaque__") or _is_tag(b, "__opaque__"):
        return a == b  # only equal if identical class + toString

    # primitives
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    if isinstance(a, (int,)) and isinstance(b, (int,)):
        return a == b

    # lists
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        if unordered:
            return _multiset_equal(a, b, cfg)
        return all(values_equivalent(x, y, cfg) for x, y in zip(a, b))

    # dicts (objects / composite observations)
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(values_equivalent(a[k], b[k], cfg, unordered=unordered) for k in a)

    return a == b


def _bytes_sig(v: Any) -> tuple | None:
    if _is_tag(v, "__bytes__"):
        return ("bytes", v.get("sha256"), v.get("len"))
    if _is_tag(v, "__bytes_ref__"):
        ref = v["__bytes_ref__"]
        return ("bytes", ref.get("sha256"), ref.get("len"))
    return None


def _multiset_equal(a: list, b: list, cfg: DecisionConfig) -> bool:
    """Order-insensitive list equality via greedy matching (small lists)."""
    remaining = list(b)
    for x in a:
        for i, y in enumerate(remaining):
            if values_equivalent(x, y, cfg):
                del remaining[i]
                break
        else:
            return False
    return not remaining


# --------------------------------------------------------------------------- #
# Result-level comparison (handles ok / error / void)
# --------------------------------------------------------------------------- #


def compare_result(
    a: dict[str, Any] | None,
    b: dict[str, Any] | None,
    cfg: DecisionConfig,
    *,
    unordered: bool = False,
    text_mode: bool = False,
) -> tuple[bool, str]:
    """Compare two per-case results; return (match, reason).

    ``reason`` names the rule that decided it, for the evidence log. When
    ``text_mode`` is set (the observation is program text/stdout), string values
    are compared after whitespace canonicalization, so trailing newlines/spaces
    don't count as behavioral differences.
    """
    if a is None or b is None:
        # Both sides missing this case: neither harness produced a result for it,
        # which (with partial-crash recovery) means both crashed before reaching
        # it — i.e. identical terminating behavior on this input. Count as a match.
        if a is None and b is None:
            return True, "both crashed before producing this case"
        return False, "missing result on one side"

    a_err, b_err = "error" in a, "error" in b
    if a_err or b_err:
        if a_err and b_err:
            # both threw — compare primarily on exception type
            ta = (a["error"] or {}).get("type")
            tb = (b["error"] or {}).get("type")
            if ta == tb:
                return True, f"both threw {ta}"
            return False, f"different exception types: {ta} vs {tb}"
        return False, "one threw, one returned normally"

    a_void = bool(a.get("void"))
    b_void = bool(b.get("void"))
    if a_void or b_void:
        if a_void and b_void:
            return True, "both void"
        return False, "one void, one produced a value"

    if text_mode and text_values_equal(a.get("ok"), b.get("ok")):
        return True, "text values equivalent (whitespace-normalized)"
    if values_equivalent(a.get("ok"), b.get("ok"), cfg, unordered=unordered):
        return True, "values equivalent (rule-based)"
    return False, "values differ after normalization"


def _normalize_text(s: str) -> str:
    """Canonicalize program text output for comparison.

    OJClone/GCJ-style programs print to stdout, where two functionally identical
    programs routinely differ only in trailing whitespace, a final newline, or
    trailing spaces on lines (e.g. ``"1 2 3"`` vs ``"1 2 3\\n"`` vs ``"1 2 3 "``).
    We erase those representation-only differences before comparing:
      * normalize CRLF/CR to LF,
      * strip trailing spaces/tabs on each line,
      * strip a trailing run of blank lines / whitespace at the very end.
    Inner spacing is preserved (it can be semantically meaningful).
    """
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip(" \t") for ln in s.split("\n")]
    return "\n".join(lines).rstrip("\n \t")


def text_values_equal(a: Any, b: Any) -> bool:
    """Compare two observations as text, after whitespace canonicalization."""
    if isinstance(a, str) and isinstance(b, str):
        return _normalize_text(a) == _normalize_text(b)
    return a == b


def diff_payload(a: dict[str, Any] | None, b: dict[str, Any] | None) -> dict[str, Any]:
    """Compact, LLM-friendly view of a residual difference for one case."""
    def view(r):
        if r is None:
            return None
        if "error" in r:
            return {"error": r["error"]}
        if r.get("void"):
            return {"void": True}
        return {"ok": r.get("ok")}

    return {"a": view(a), "b": view(b)}
