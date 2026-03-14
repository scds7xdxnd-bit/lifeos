"""Shortening and compression helpers for humanized inquiry rendering."""

from __future__ import annotations

from lifeos.core.insights.inquiry_humanization.terminology import simplify_text

_LIMIT_REWRITES = (
    (
        "Timeline comparison is insufficient because fewer than two closed comparable windows are available.",
        "There is not enough matching time history yet for a full time-based reading.",
    ),
    (
        "Approved pair timeline comparison is insufficient because fewer than two closed "
        "comparable windows are available.",
        "There is not enough shared time history yet for a full pair-based time reading.",
    ),
    (
        "Recurrence interpretation is insufficient because fewer than two comparable windows "
        "contain canonical evidence.",
        "There is not enough repeated saved history yet to judge whether this pattern is recurring.",
    ),
    (
        "Approved pair persistence is insufficient because fewer than two comparable windows "
        "show aligned canonical evidence.",
        "There is not enough repeated shared support yet to judge whether this pair pattern is persistent.",
    ),
)


def compress_claim(text: str, *, replacements: tuple[tuple[str, str], ...] = ()) -> str:
    rendered = simplify_text(text, replacements)
    prefixes = (
        "In the available record, ",
        "Across comparable windows, ",
        "Across closed comparable windows, ",
    )
    for prefix in prefixes:
        if rendered.startswith(prefix):
            rendered = rendered[len(prefix) :]
    return rendered.strip()


def compress_limit(text: str, *, replacements: tuple[tuple[str, str], ...] = ()) -> str:
    for source, target in _LIMIT_REWRITES:
        if text == source:
            return target
    rendered = simplify_text(text, replacements)
    rendered = rendered.replace("Likely gain:", "Expected gain:")
    return rendered.strip()


def compress_answer(text: str, *, replacements: tuple[tuple[str, str], ...] = ()) -> str:
    rendered = simplify_text(text, replacements)
    for prefix in ("Partial answer: ", "Weak answer: "):
        if rendered.startswith(prefix):
            rendered = rendered[len(prefix) :]
    return rendered.strip()


def compress_uncertainty(text: str, *, replacements: tuple[tuple[str, str], ...] = ()) -> str:
    return simplify_text(text, replacements)


__all__ = ["compress_answer", "compress_claim", "compress_limit", "compress_uncertainty"]
