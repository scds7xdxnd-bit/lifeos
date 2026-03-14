"""Deterministic duplicate reduction for humanized sections."""

from __future__ import annotations

from lifeos.core.insights.inquiry_humanization.contracts import HumanizedBlock


def dedupe_blocks(blocks: list[HumanizedBlock]) -> tuple[HumanizedBlock, ...]:
    deduped: list[HumanizedBlock] = []
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    for block in blocks:
        key = (
            " ".join(block.text.split()).lower(),
            tuple(block.source_finding_ids),
            tuple(block.source_limitation_ids),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(block)
    return tuple(deduped)


__all__ = ["dedupe_blocks"]
