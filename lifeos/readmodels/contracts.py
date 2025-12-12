"""Contracts for declaring replayable read models (interfaces only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional


ReadModelType = Literal["snapshot", "timeline", "aggregate"]


@dataclass
class ReadModelContract:
    """Declarative contract for a read model projection."""

    name: str
    domain: str
    consumed_events: List[str]
    replay_start_version: Optional[str]
    idempotency_key: str
    type: ReadModelType
    rebuild_strategy: Optional[str] = None  # notes on full/partial/checkpoint rules


__all__ = ["ReadModelContract", "ReadModelType"]
