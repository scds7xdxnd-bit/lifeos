"""Deterministic section ordering for humanized inquiry output."""

from __future__ import annotations

_ORDER = {
    "what_stands_out": 0,
    "why_it_matters": 1,
    "how_sure_this_is": 2,
    "what_to_review_next": 3,
}


def prioritize_sections(section_ids: list[str]) -> list[str]:
    return sorted(section_ids, key=lambda item: (_ORDER.get(item, 99), item))


__all__ = ["prioritize_sections"]
