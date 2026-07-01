"""Detect non-stubbable external dependencies in a code snippet.

When a fragment depends on the network, the filesystem, the clock, randomness,
or other ambient state, the reconstruction step often replaces that dependency
with an in-memory stub. If both sides of a pair are stubbed the same way, their
*observed* behavior can be forced to agree even when the originals differ ---
manufacturing a false ``clone`` verdict (see the BigCloneBench false positives
where two URL-reading methods, one hardcoded and one parameterized with auth,
compared as identical after stubbing).

This module flags such fragments so the pipeline can mark their execution
evidence as untrusted (and prefer a code-reading judgment instead). It reads
ONLY the source code --- never any label --- so it is a legitimate, in-protocol
reliability gate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Pattern -> dependency category. Matched against the raw snippet text. These are
# deliberately conservative: each names a construct whose real behavior depends
# on state the harness cannot faithfully reproduce.
_PATTERNS: list[tuple[str, str]] = [
    # network
    (r"\bnew\s+URL\b|\bURLConnection\b|\bHttpURLConnection\b|openStream\b|"
     r"\bSocket\b|\bServerSocket\b|\bInetAddress\b|\bDatagram|HttpClient\b|"
     r"\.openConnection\b|getResponseCode\b", "network"),
    # filesystem (reading/writing real paths, not just the harness's scratch I/O)
    (r"\bFileInputStream\b|\bFileOutputStream\b|\bFileReader\b|\bFileWriter\b|"
     r"\bRandomAccessFile\b|getResourceAsStream\b|\bFiles\.(?:newInputStream|"
     r"newOutputStream|readAllBytes|copy|move|delete)\b|\bnew\s+File\b", "filesystem"),
    # clock / time
    (r"currentTimeMillis\b|System\.nanoTime\b|\bnew\s+Date\s*\(\s*\)|"
     r"Instant\.now\b|LocalDate(?:Time)?\.now\b|\bnanoTime\b", "clock"),
    # randomness
    (r"\bnew\s+Random\b|Math\.random\b|\bUUID\.randomUUID\b|SecureRandom\b|"
     r"ThreadLocalRandom\b", "random"),
    # process / environment / threads / native
    (r"Runtime\.getRuntime\b|ProcessBuilder\b|System\.getenv\b|System\.getProperty\b|"
     r"\bnew\s+Thread\b|\.start\s*\(\s*\)|loadLibrary\b", "process_env"),
    # database / external services
    (r"\bDriverManager\b|getConnection\b|\bConnection\b\s+\w+\s*=|JdbcTemplate\b|"
     r"createStatement\b", "database"),
]

_COMPILED = [(re.compile(p), cat) for p, cat in _PATTERNS]


@dataclass
class DependencyReport:
    has_external: bool
    categories: list[str]

    def reason(self) -> str:
        return "external dependencies: " + ", ".join(sorted(set(self.categories)))


def _strip_comments_strings(code: str) -> str:
    """Remove // and /* */ comments and string literals so matches are on real
    code, not text inside comments or string constants (e.g. a URL in a message)."""
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.DOTALL)
    code = re.sub(r"//[^\n]*", " ", code)
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    return code


def detect(code: str) -> DependencyReport:
    """Detect external dependencies in a single snippet."""
    cleaned = _strip_comments_strings(code or "")
    cats = [cat for rx, cat in _COMPILED if rx.search(cleaned)]
    return DependencyReport(has_external=bool(cats), categories=cats)


def pair_has_external(code_a: str, code_b: str) -> DependencyReport:
    """Detect external dependencies across a pair (union of both sides)."""
    ra, rb = detect(code_a), detect(code_b)
    cats = ra.categories + rb.categories
    return DependencyReport(has_external=bool(cats), categories=cats)
