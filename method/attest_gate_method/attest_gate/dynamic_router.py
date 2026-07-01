from __future__ import annotations

from typing import Any


def coerce_label(value: Any) -> int | None:
    if value in (0, 1):
        return int(value)
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed in (0, 1) else None


def coerce_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NA", "N/A", "NULL", "NONE"}:
        return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None
