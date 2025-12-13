"""Session identity and lifecycle envelopes (contracts only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from lifeos.core.auth.constants import (
    SESSION_SCOPE_ALL,
    SESSION_SCOPE_SINGLE,
    SESSION_STATE_ACTIVE,
)


@dataclass
class SessionIdentity:
    """Lightweight session identity representation; not persisted (Phase 3b½ scaffold)."""

    session_id: str
    user_id: int
    device_id: Optional[str] = None
    created_at: Optional[datetime] = None
    invalidated_at: Optional[datetime] = None
    lifecycle_state: str = SESSION_STATE_ACTIVE


@dataclass
class SessionResetRequest:
    """Represents an admin-driven reset intent."""

    user_id: int
    session_scope: str = SESSION_SCOPE_ALL
    session_id: Optional[str] = None
    reason: Optional[str] = None
    initiated_by_admin_id: Optional[int] = None

    def validate_scope(self) -> None:
        if self.session_scope not in (SESSION_SCOPE_ALL, SESSION_SCOPE_SINGLE):
            raise ValueError("invalid_scope")
        if self.session_scope == SESSION_SCOPE_SINGLE and not self.session_id:
            raise ValueError("session_id_required")


__all__ = ["SessionIdentity", "SessionResetRequest"]
