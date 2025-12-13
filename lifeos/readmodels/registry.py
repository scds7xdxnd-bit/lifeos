"""Declarative registry for read models (structure only)."""

from __future__ import annotations

from typing import Iterable, Optional

from lifeos.readmodels.contracts import ReadModelContract


class ReadModelRegistry:
    """Registry of read model contracts (no implementation; define interfaces only)."""

    def list(self) -> Iterable[ReadModelContract]:
        raise NotImplementedError

    def get(self, name: str) -> Optional[ReadModelContract]:
        raise NotImplementedError


__all__ = ["ReadModelRegistry"]
