"""Manual replay CLI contract (structure only)."""

from __future__ import annotations

from typing import Optional

from lifeos.readmodels.contracts import ReadModelContract


def replay_command(
    contract: ReadModelContract,
    start_event_id: Optional[int] = None,
    end_event_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> None:
    """Manual replay entrypoint contract: replay events into a read model."""
    raise NotImplementedError


__all__ = ["replay_command"]
