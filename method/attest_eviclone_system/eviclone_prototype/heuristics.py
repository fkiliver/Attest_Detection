from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


FEATURE_RULES: dict[str, list[str]] = {
    "copy_file": [
        r"\bFiles\.copy\b",
        r"\bFileUtils\.copyFile\b",
        r"\bIOUtils\.copy(?:Large)?\b",
        r"\btransfer(?:From|To)\b",
        r"\bFileChannel\b",
        r"\bFileInputStream\b[\s\S]{0,300}\bFileOutputStream\b",
        r"\bread\s*\([\s\S]{0,250}\bwrite\s*\(",
        r"\bScanner\b[\s\S]{0,250}\bPrintWriter\b",
    ],
    "download_web": [
        r"\bnew\s+URL\b",
        r"\bURL\b[\s\S]{0,160}\bopenStream\s*\(",
        r"\bURLConnection\b",
        r"\bHttpURLConnection\b",
        r"\bHttpClient\b",
        r"\bHttpResponse\b",
        r"https?://",
        r"\bexecute\s*\([\s\S]{0,120}\bHttp",
    ],
    "secure_hash": [
        r"\bMessageDigest\b",
        r"\bdigest\s*\(",
        r"\bSHA-?\d+\b",
        r"\bMD5\b",
    ],
    "zip_decompress": [
        r"\bZipInputStream\b",
        r"\bZipFile\b",
        r"\bZipEntry\b",
        r"\bunzip\b",
        r"\bdecompress\b",
    ],
    "ftp": [
        r"\bFTPClient\b",
        r"\bconnect\s*\(",
        r"\blogin\s*\(",
        r"\bretrieveFile\b",
        r"\bstoreFile\b",
    ],
    "db_update_rollback": [
        r"\bexecuteUpdate\b",
        r"\brollback\s*\(",
        r"\bcommit\s*\(",
        r"\bPreparedStatement\b",
        r"\bjava\.sql\.Connection\b",
        r"\bConnection\s+\w+\s*[=;)]",
    ],
}


TARGET_ALIASES = {
    "copy file": "copy_file",
    "download from web": "download_web",
    "secure hash": "secure_hash",
    "decompress zip archive": "zip_decompress",
    "connect to ftp server": "ftp",
    "execute update and rollback": "db_update_rollback",
    "execute update and rollback.": "db_update_rollback",
    "bubble sort array": "bubble_sort",
}


@dataclass(frozen=True)
class CodeFeatures:
    line_count: int
    token_count: int
    identifiers: set[str]
    feature_hits: dict[str, list[str]]
    return_kind: str
    has_exception_handling: bool
    has_io: bool


def normalize_identifier(value: str) -> str:
    return value.lower()


def extract_identifiers(code: str) -> set[str]:
    keywords = {
        "public",
        "private",
        "protected",
        "static",
        "final",
        "void",
        "return",
        "if",
        "else",
        "for",
        "while",
        "try",
        "catch",
        "finally",
        "new",
        "class",
        "throws",
        "throw",
        "null",
        "true",
        "false",
    }
    return {normalize_identifier(x) for x in IDENT_RE.findall(code) if normalize_identifier(x) not in keywords}


def detect_return_kind(code: str) -> str:
    header = code.strip().split("{", 1)[0]
    if re.search(r"\bvoid\s+\w+\s*\(", header):
        return "void"
    if re.search(r"\b(?:String|CharSequence)\s+\w+\s*\(", header):
        return "text"
    if re.search(r"\bbyte\s*\[\]\s+\w+\s*\(", header):
        return "bytes"
    if re.search(r"\b(?:int|long|double|float|boolean|Boolean|Integer|Long)\s+\w+\s*\(", header):
        return "scalar"
    if "return " in code:
        return "value"
    return "unknown"


def extract_features(code: str) -> CodeFeatures:
    hits: dict[str, list[str]] = {}
    for name, patterns in FEATURE_RULES.items():
        matched = [p for p in patterns if re.search(p, code, flags=re.IGNORECASE)]
        if matched:
            hits[name] = matched
    identifiers = extract_identifiers(code)
    return CodeFeatures(
        line_count=len([line for line in code.splitlines() if line.strip()]),
        token_count=len(IDENT_RE.findall(code)),
        identifiers=identifiers,
        feature_hits=hits,
        return_kind=detect_return_kind(code),
        has_exception_handling=bool(re.search(r"\btry\b|\bcatch\b|\bthrows\b", code)),
        has_io=bool(re.search(r"\bInputStream\b|\bOutputStream\b|\bReader\b|\bWriter\b|\bread\s*\(|\bwrite\s*\(", code)),
    )


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def target_family(functionality_name: str) -> str:
    return TARGET_ALIASES.get(functionality_name.strip().lower(), "unknown")


def feature_summary(features: CodeFeatures) -> dict[str, Any]:
    return {
        "line_count": features.line_count,
        "token_count": features.token_count,
        "feature_families": sorted(features.feature_hits),
        "return_kind": features.return_kind,
        "has_exception_handling": features.has_exception_handling,
        "has_io": features.has_io,
    }


def compare_codes(code_a: str, code_b: str, functionality_name: str) -> dict[str, Any]:
    a = extract_features(code_a)
    b = extract_features(code_b)
    target = target_family(functionality_name)
    families_a = set(a.feature_hits)
    families_b = set(b.feature_hits)
    shared_families = sorted(families_a & families_b)
    identifier_similarity = round(jaccard(a.identifiers, b.identifiers), 4)
    observations: list[str] = []
    risk_flags: list[str] = []

    if target != "unknown":
        if target in families_a and target in families_b:
            observations.append(f"both snippets contain cues for target functionality '{target}'")
        elif target in families_a or target in families_b:
            risk_flags.append(f"target functionality cue '{target}' appears on only one side")
        else:
            risk_flags.append(f"no direct static cue for target functionality '{target}'")
    else:
        observations.append("target functionality is not mapped to a built-in local rule")

    if shared_families:
        observations.append("shared feature families: " + ", ".join(shared_families))
    else:
        risk_flags.append("no shared high-level feature family detected")

    if "copy_file" in shared_families and (("download_web" in families_a) ^ ("download_web" in families_b)):
        risk_flags.append("copy-like IO overlaps with web/local-resource boundary")
    if "download_web" in shared_families and a.return_kind != b.return_kind:
        risk_flags.append("download-like code returns different observable object kinds")
    if identifier_similarity < 0.05:
        risk_flags.append("very low identifier overlap; semantic evidence must come from behavior/API cues")

    return {
        "target_family": target,
        "code_a": feature_summary(a),
        "code_b": feature_summary(b),
        "shared_feature_families": shared_families,
        "identifier_similarity": identifier_similarity,
        "observations": observations,
        "risk_flags": risk_flags,
    }
