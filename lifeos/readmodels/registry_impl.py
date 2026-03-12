"""Concrete read model registry for Phase 3a."""

from __future__ import annotations

from typing import Iterable, Optional

from lifeos.readmodels.contracts import ReadModelContract
from lifeos.readmodels.projections import INSIGHT_FEED_CONTRACT, REVIEW_QUEUE_CONTRACT
from lifeos.readmodels.registry import ReadModelRegistry


class DefaultReadModelRegistry(ReadModelRegistry):
    """Registry of read-only projections used in Phase 3a."""

    def __init__(self) -> None:
        self._contracts = {
            INSIGHT_FEED_CONTRACT.name: INSIGHT_FEED_CONTRACT,
            REVIEW_QUEUE_CONTRACT.name: REVIEW_QUEUE_CONTRACT,
        }

    def list(self) -> Iterable[ReadModelContract]:
        return self._contracts.values()

    def get(self, name: str) -> Optional[ReadModelContract]:
        return self._contracts.get(name)


__all__ = ["DefaultReadModelRegistry"]
