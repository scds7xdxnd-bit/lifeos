"""Adapter contracts for deterministic inquiry humanization."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HumanizationAdapter:
    key: str
    replacements: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    event_record_label_singular: str = "saved record"
    event_record_label_plural: str = "saved records"


__all__ = ["HumanizationAdapter"]
