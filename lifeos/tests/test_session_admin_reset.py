"""Tests for admin-driven session reset (CLI/service path)."""

from __future__ import annotations

import pytest

from lifeos.core.auth.constants import SESSION_SCOPE_SINGLE, SESSION_STATE_ADMIN_RESET
from lifeos.core.auth.models import AuthSession, JWTBlocklist, SessionToken
from lifeos.core.auth.session_services import SessionLifecycleService
from lifeos.core.users.models import User
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox.models import OutboxMessage


def test_admin_reset_marks_sessions_and_enqueues_event(app):
    """Admin reset should revoke tokens, mark auth_session, and enqueue an event."""
    user = User(email="reset@example.com", password_hash="pw")
    db.session.add(user)
    db.session.flush()
    db.session.add(SessionToken(user_id=user.id, jti="jti-1", revoked=False))
    db.session.add(AuthSession(user_id=user.id, session_id="jti-1", lifecycle_state="active"))
    db.session.commit()

    service = SessionLifecycleService()
    result = service.admin_reset(
        user_id=user.id,
        session_scope=SESSION_SCOPE_SINGLE,
        session_id="jti-1",
        reason="ops reset",
    )

    assert result["reset_count"] == 1
    token = SessionToken.query.filter_by(jti="jti-1").first()
    assert token.revoked is True
    auth_session = AuthSession.query.filter_by(session_id="jti-1").first()
    assert auth_session.lifecycle_state == SESSION_STATE_ADMIN_RESET
    assert auth_session.invalidated_at is not None
    assert JWTBlocklist.query.filter_by(jti="jti-1").count() == 1
    message = OutboxMessage.query.filter_by(event_type="auth.session.admin_reset", user_id=user.id).first()
    assert message is not None
    assert message.payload["reason"] == "ops reset"
    assert message.payload["session_scope"] == SESSION_SCOPE_SINGLE


def test_admin_reset_requires_reason(app):
    """Reason must be provided for admin reset."""
    user = User(email="reset2@example.com", password_hash="pw")
    db.session.add(user)
    db.session.flush()
    service = SessionLifecycleService()

    with pytest.raises(ValueError):
        service.admin_reset(user_id=user.id, reason="  ")
