"""Harness template loading and hole-filling.

A harness *template* is a fixed driver with named holes (``@@SNIPPET@@``,
``@@SETUP@@``, ``@@INVOKE@@``, ``@@OBSERVE@@`` for Java). Stage 2 asks the LLM to
produce the contents of those holes; this module substitutes them into the
template to yield compilable source. Keeping the substitution here (not in the
LLM output) guarantees the fixed infrastructure is byte-identical every time.
"""

from __future__ import annotations

from pathlib import Path

_SUPPORT = Path(__file__).resolve().parent.parent / "harness_support"

# Ordered holes per language. The LLM must supply exactly these keys.
# C is compiled as C++ (valid for the OJClone programs), so it shares the cpp
# template and holes.
HOLES: dict[str, list[str]] = {
    "java": ["SNIPPET", "SETUP", "INVOKE", "OBSERVE"],
    "cpp": ["SNIPPET", "SETUP", "INVOKE", "OBSERVE"],
    "c": ["SNIPPET", "SETUP", "INVOKE", "OBSERVE"],
}

_TEMPLATES: dict[str, Path] = {
    "java": _SUPPORT / "java" / "Harness.template.java",
    "cpp": _SUPPORT / "cpp" / "harness.template.cpp",
    "c": _SUPPORT / "cpp" / "harness.template.cpp",
}


def load_template(language: str) -> str:
    path = _TEMPLATES[language]
    return path.read_text(encoding="utf-8")


def fill_template(language: str, holes: dict[str, str]) -> str:
    """Substitute ``holes`` into the template for ``language``.

    Raises if a required hole is missing or an unknown hole is supplied.
    """
    required = set(HOLES[language])
    given = set(holes)
    missing = required - given
    if missing:
        raise ValueError(f"missing harness holes: {sorted(missing)}")
    extra = given - required
    if extra:
        raise ValueError(f"unexpected harness holes: {sorted(extra)}")
    src = load_template(language)
    for name in HOLES[language]:
        token = f"@@{name}@@"
        count = src.count(token)
        if count == 0:
            raise ValueError(f"template for {language} lacks hole {token}")
        if count > 1:
            # The token must appear exactly once (at its insertion point). More
            # than one means the template's own documentation used the literal
            # token, which a blind replace would corrupt. Fail loudly instead.
            raise ValueError(
                f"template for {language} contains {token} {count} times; "
                f"it must appear exactly once (refer to it by bare name in docs)"
            )
        src = src.replace(token, holes[name])
    return src
