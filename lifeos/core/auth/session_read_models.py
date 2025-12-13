"""Read-model contracts for sessions (projection-only, never for authz)."""

from __future__ import annotations

from typing import Iterable

from lifeos.core.auth.session_models import SessionIdentity


class SessionReadModel:
    """Placeholder projection that can be rebuilt via event replay."""

    def __init__(self, sessions: Iterable[SessionIdentity] | None = None):
        self.sessions = list(sessions or [])

    def as_dict(self) -> list[dict]:
        return [session.__dict__ for session in self.sessions]


__all__ = ["SessionReadModel"]
