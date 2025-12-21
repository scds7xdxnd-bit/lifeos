"""Auth background tasks (structure-only hooks)."""

from __future__ import annotations


def queue_session_admin_reset(user_id: int, reason: str | None = None) -> None:
    """Placeholder for queuing an admin reset; intentionally inert in Phase 3a/3b."""
    # Implemented later when background queue for session resets is introduced.
    return None


__all__ = ["queue_session_admin_reset"]
