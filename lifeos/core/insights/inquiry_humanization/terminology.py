"""Plain-language substitutions for humanized inquiry text."""

from __future__ import annotations

import re
from typing import Iterable

_GENERIC_REPLACEMENTS = (
    ("canonical records", "saved records"),
    ("canonical record", "saved record"),
    ("canonical evidence", "saved support"),
    ("selected inquiry timeframe", "selected time range"),
    ("selected inquiry time frame", "selected time range"),
    ("selected timeframe", "selected time range"),
    ("selected time frame", "selected time range"),
    ("comparable windows", "matching time windows"),
    ("comparable window", "matching time window"),
    ("active window", "current time window"),
    ("prior comparable window", "earlier matching time window"),
    ("evidence coverage", "how much supporting history is available"),
    ("bounded pattern", "pattern seen in the selected time range"),
    ("synthesis", "combined summary"),
    ("approved pair alignment", "the two selected areas showing up together"),
    ("cross-domain", "cross-area"),
)


def _replacement_pattern(source: str) -> re.Pattern[str] | None:
    parts = [re.escape(part) for part in re.sub(r"[-_]+", " ", str(source or "").strip()).split() if part]
    if not parts:
        return None
    joiner = r"[\s_-]+"
    return re.compile(rf"(?<![A-Za-z0-9]){joiner.join(parts)}(?![A-Za-z0-9])", flags=re.IGNORECASE)


def _apply_replacements(text: str, replacements: Iterable[tuple[str, str]]) -> str:
    rendered = text
    for source, target in replacements:
        pattern = _replacement_pattern(source)
        if pattern is None:
            continue
        rendered = pattern.sub(str(target), rendered)
    return rendered


def simplify_text(text: str, replacements: Iterable[tuple[str, str]] = ()) -> str:
    rendered = str(text or "")
    rendered = _apply_replacements(rendered, _GENERIC_REPLACEMENTS)
    rendered = _apply_replacements(rendered, replacements)
    rendered = re.sub(r"\s+", " ", rendered).strip()
    return rendered


__all__ = ["simplify_text"]
