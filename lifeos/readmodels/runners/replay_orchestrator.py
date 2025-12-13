"""Replay orchestrator interfaces (structure only)."""

from __future__ import annotations

from typing import Iterable, Optional

from lifeos.readmodels.contracts import ReadModelContract


class ReplayOrchestrator:
    """Coordinate deterministic replay of immutable events into read models."""

    def replay_all(self, contract: ReadModelContract) -> None:
        """Replay full event stream for the contract."""
        raise NotImplementedError

    def replay_range(
        self,
        contract: ReadModelContract,
        start_event_id: Optional[int] = None,
        end_event_id: Optional[int] = None,
        user_ids: Optional[Iterable[int]] = None,
    ) -> None:
        """Replay a bounded event range and/or user scope."""
        raise NotImplementedError


__all__ = ["ReplayOrchestrator"]
