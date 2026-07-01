from __future__ import annotations

import difflib
import re
from collections import Counter
from functools import lru_cache
from typing import Any


TOKEN_RE = re.compile(
    r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|"
    r"\b\d+(?:\.\d+)?\b|"
    r"[A-Za-z_][A-Za-z0-9_]*|"
    r"==|!=|<=|>=|&&|\|\||\+\+|--|->|::|[{}()[\].,;:+\-*/%<>=!&|?]"
)
COMMENT_RE = re.compile(r"//.*?$|/\*.*?\*/", re.MULTILINE | re.DOTALL)
METHOD_CALL_RE = re.compile(r"(?:\.|::)\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(")
NEW_TYPE_RE = re.compile(r"\bnew\s+([A-Za-z_][A-Za-z0-9_$.]*)")
TYPE_NAME_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*(?:\.[A-Z][A-Za-z0-9_]*)*)\b")

JAVA_KEYWORDS = {
    "abstract",
    "assert",
    "boolean",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extends",
    "final",
    "finally",
    "float",
    "for",
    "goto",
    "if",
    "implements",
    "import",
    "instanceof",
    "int",
    "interface",
    "long",
    "native",
    "new",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "static",
    "strictfp",
    "super",
    "switch",
    "synchronized",
    "this",
    "throw",
    "throws",
    "transient",
    "try",
    "void",
    "volatile",
    "while",
    "true",
    "false",
    "null",
}

CONTROL_KEYWORDS = {
    "if",
    "else",
    "for",
    "while",
    "switch",
    "case",
    "try",
    "catch",
    "finally",
    "return",
    "throw",
    "break",
    "continue",
}


def structural_clone_features(code_a: str, code_b: str) -> dict[str, Any]:
    """Return nonleaky clone-detection features from two Java snippets."""
    norm_a = normalized_tokens(code_a)
    norm_b = normalized_tokens(code_b)
    raw_a = raw_tokens(code_a)
    raw_b = raw_tokens(code_b)
    api_a = api_sequence(code_a)
    api_b = api_sequence(code_b)
    control_a = [token for token in norm_a if token in CONTROL_KEYWORDS]
    control_b = [token for token in norm_b if token in CONTROL_KEYWORDS]

    features: dict[str, Any] = {
        "norm_token_jaccard": jaccard(Counter(norm_a), Counter(norm_b)),
        "raw_token_jaccard": jaccard(Counter(raw_a), Counter(raw_b)),
        "norm_token_lcs_min": lcs_ratio(norm_a, norm_b, denom="min"),
        "norm_token_lcs_avg": lcs_ratio(norm_a, norm_b, denom="avg"),
        "raw_token_lcs_min": lcs_ratio(raw_a, raw_b, denom="min"),
        "sequence_match_ratio": sequence_match_ratio(norm_a, norm_b),
        "token_count_min": float(min(len(norm_a), len(norm_b))),
        "token_count_max": float(max(len(norm_a), len(norm_b))),
        "token_count_ratio": ratio(min(len(norm_a), len(norm_b)), max(len(norm_a), len(norm_b))),
        "api_jaccard": jaccard(Counter(api_a), Counter(api_b)),
        "api_lcs_min": lcs_ratio(api_a, api_b, denom="min"),
        "api_lcs_avg": lcs_ratio(api_a, api_b, denom="avg"),
        "api_count_min": float(min(len(api_a), len(api_b))),
        "api_count_max": float(max(len(api_a), len(api_b))),
        "control_jaccard": jaccard(Counter(control_a), Counter(control_b)),
        "control_lcs_min": lcs_ratio(control_a, control_b, denom="min"),
        "control_lcs_avg": lcs_ratio(control_a, control_b, denom="avg"),
        "control_count_min": float(min(len(control_a), len(control_b))),
        "control_count_max": float(max(len(control_a), len(control_b))),
    }
    for k in [2, 3, 4, 5]:
        norm_grams_a = kgrams(norm_a, k)
        norm_grams_b = kgrams(norm_b, k)
        features[f"norm_{k}gram_jaccard"] = set_jaccard(norm_grams_a, norm_grams_b)
        features[f"norm_{k}gram_containment"] = containment(norm_grams_a, norm_grams_b)
        raw_grams_a = kgrams(raw_a, k)
        raw_grams_b = kgrams(raw_b, k)
        features[f"raw_{k}gram_jaccard"] = set_jaccard(raw_grams_a, raw_grams_b)
        features[f"raw_{k}gram_containment"] = containment(raw_grams_a, raw_grams_b)
    features["max_structural_similarity"] = max(
        features["norm_token_lcs_min"],
        features["norm_3gram_containment"],
        features["norm_4gram_containment"],
        features["api_lcs_min"],
    )
    features["embedded_clone_signal"] = min(features["norm_token_lcs_min"], 1.0 - abs(1.0 - features["token_count_ratio"]))
    features["api_minus_token_jaccard"] = features["api_jaccard"] - features["norm_token_jaccard"]
    features["bucket_max_structural_similarity"] = score_bucket(features["max_structural_similarity"])
    features["bucket_norm_3gram_containment"] = score_bucket(features["norm_3gram_containment"])
    features["bucket_api_lcs_min"] = score_bucket(features["api_lcs_min"])
    return features


def strip_comments(code: str) -> str:
    return COMMENT_RE.sub(" ", code)


def raw_tokens(code: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(strip_comments(code))]


def normalized_tokens(code: str) -> list[str]:
    result: list[str] = []
    for token in TOKEN_RE.findall(strip_comments(code)):
        lowered = token.lower()
        if token.startswith(("\"", "'")):
            result.append("STR")
        elif re.fullmatch(r"\d+(?:\.\d+)?", token):
            result.append("NUM")
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
            result.append(lowered if lowered in JAVA_KEYWORDS else "ID")
        else:
            result.append(token)
    return result


def api_sequence(code: str) -> list[str]:
    stripped = strip_comments(code)
    sequence: list[str] = []
    sequence.extend(f"call:{name.lower()}" for name in METHOD_CALL_RE.findall(stripped))
    sequence.extend(f"new:{name.split('.')[-1].lower()}" for name in NEW_TYPE_RE.findall(stripped))
    sequence.extend(f"type:{name.split('.')[-1].lower()}" for name in TYPE_NAME_RE.findall(stripped))
    return sequence


def kgrams(tokens: list[str], k: int) -> set[tuple[str, ...]]:
    if len(tokens) < k:
        return set()
    return {tuple(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def set_jaccard(a: set[tuple[str, ...]], b: set[tuple[str, ...]]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def containment(a: set[tuple[str, ...]], b: set[tuple[str, ...]]) -> float:
    if not a and not b:
        return 1.0
    smaller = min(len(a), len(b))
    return len(a & b) / smaller if smaller else 0.0


def jaccard(a: Counter[str], b: Counter[str]) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 1.0
    intersection = sum(min(a[key], b[key]) for key in keys)
    union = sum(max(a[key], b[key]) for key in keys)
    return intersection / union if union else 0.0


def lcs_ratio(a: list[str], b: list[str], *, denom: str) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    length = approximate_lcs_length(tuple(a[:500]), tuple(b[:500]))
    if denom == "min":
        return ratio(length, min(len(a), len(b)))
    if denom == "avg":
        return ratio(length * 2.0, len(a) + len(b))
    return 0.0


@lru_cache(maxsize=4096)
def approximate_lcs_length(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return sum(block.size for block in matcher.get_matching_blocks())


def sequence_match_ratio(a: list[str], b: list[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a[:700], b[:700], autojunk=False).ratio()


def ratio(numerator: float, denominator: float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def score_bucket(value: float) -> str:
    if value >= 0.9:
        return "very_high"
    if value >= 0.75:
        return "high"
    if value >= 0.55:
        return "medium"
    if value >= 0.3:
        return "low"
    return "very_low"
