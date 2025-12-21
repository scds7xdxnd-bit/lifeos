"""Input validation helpers."""

from __future__ import annotations


def require_fields(data: dict, *fields: str) -> None:
    for field in fields:
        if field not in data or data[field] in (None, ""):
            raise ValueError(f"Missing required field: {field}")
