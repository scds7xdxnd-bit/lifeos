"""Session lifecycle service contracts (structure-first; minimal admin reset path only)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from lifeos.core.auth.constants import SESSION_SCOPE_ALL, SESSION_SCOPE_SINGLE
from lifeos.core.auth.session_events import AUTH_SESSION_ADMIN_RESET
from lifeos.core.auth.session_models import SessionResetRequest
from lifeos.core.auth.session_repository import SessionRepository
from lifeos.core.users.models import User
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


class SessionLifecycleService:
    """Lifecycle operations for sessions. Only admin_reset is enabled in Phase 3a/b scaffolding."""

    def __init__(self, repository: Optional[SessionRepository] = None):
        self.repository = repository or SessionRepository()

    def admin_reset(
        self,
        user_id: int,
        *,
        session_scope: str = SESSION_SCOPE_ALL,
        session_id: Optional[str] = None,
        reason: Optional[str] = None,
        initiated_by_admin_id: Optional[int] = None,
    ) -> dict:
        """Minimal admin-driven session reset (revokes refresh tokens + emits contract event)."""
        user = User.query.get(user_id)
        if not user:
            raise ValueError("not_found")

        reason_clean = (reason or "").strip()
        if not reason_clean:
            raise ValueError("reason_required")

        reset_request = SessionResetRequest(
            user_id=user_id,
            session_scope=session_scope,
            session_id=session_id,
            reason=reason_clean,
            initiated_by_admin_id=initiated_by_admin_id,
        )
        reset_request.validate_scope()

        revoked_ids, auth_session_count = self.repository.admin_reset(
            user_id,
            session_id=session_id if reset_request.session_scope == SESSION_SCOPE_SINGLE else None,
        )
        enqueue_outbox(
            AUTH_SESSION_ADMIN_RESET,
            {
                "user_id": user_id,
                "session_scope": reset_request.session_scope,
                "session_id": session_id,
                "device_id": None,
                "reason": reason_clean,
                "initiated_by_admin_id": initiated_by_admin_id,
            },
            user_id=user_id,
        )
        db.session.commit()
        return {
            "reset_count": max(len(revoked_ids), auth_session_count),
            "session_scope": reset_request.session_scope,
            "session_id": session_id,
            "reset_at": datetime.utcnow().isoformat(),
        }


class SessionQueryService:
    """Read-only view of session tokens; never used for authz."""

    def __init__(self, repository: Optional[SessionRepository] = None):
        self.repository = repository or SessionRepository()

    def list_sessions(self, user_id: int):
        return self.repository.list_sessions(user_id)


__all__ = ["SessionLifecycleService", "SessionQueryService"]
