"""Persistence contracts for session lifecycle (structure-first, minimal admin reset path)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from lifeos.core.auth.constants import SESSION_STATE_ADMIN_RESET
from lifeos.core.auth.models import AuthSession, JWTBlocklist, SessionToken
from lifeos.extensions import db


class SessionRepository:
    """Repository for session state. Implementations must stay additive and idempotent."""

    def __init__(self, session=None):
        self._session = session or db.session

    def admin_reset(
        self,
        user_id: int,
        *,
        session_id: Optional[str] = None,
    ) -> tuple[list[str], int]:
        """Mark sessions for a user as revoked/admin_reset.

        Returns:
            revoked_ids: list of session token JTIs revoked
            auth_session_count: number of auth_session rows marked admin_reset
        """
        now = datetime.utcnow()
        query = SessionToken.query.filter_by(user_id=user_id)
        if session_id:
            query = query.filter(SessionToken.jti == session_id)
        tokens = query.all()
        revoked_ids: list[str] = []
        for token in tokens:
            if not token.revoked:
                token.revoked = True
            if token.jti:
                revoked_ids.append(token.jti)
                if not JWTBlocklist.query.filter_by(jti=token.jti).first():
                    self._session.add(JWTBlocklist(jti=token.jti, created_by=None))

        # Also mark structured auth_session rows if present
        session_query = AuthSession.query.filter_by(user_id=user_id)
        if session_id:
            session_query = session_query.filter(AuthSession.session_id == session_id)
        auth_session_count = 0
        for record in session_query.all():
            if record.lifecycle_state != SESSION_STATE_ADMIN_RESET:
                record.lifecycle_state = SESSION_STATE_ADMIN_RESET
            if record.invalidated_at is None:
                record.invalidated_at = now
            auth_session_count += 1
        # No commit; service layer coordinates commit with outbox emission.
        return revoked_ids, auth_session_count

    def list_sessions(self, user_id: int) -> list[SessionToken]:
        """Read-only current session tokens for a user (for future projections; not for authz)."""
        return SessionToken.query.filter_by(user_id=user_id).order_by(SessionToken.created_at.desc()).all()


__all__ = ["SessionRepository"]
