"""Lightweight CSRF token helpers using the session."""

from __future__ import annotations

import secrets

from flask import session

CSRF_TOKEN_SESSION_KEY = "_csrf_token"
LEGACY_CSRF_TOKEN_SESSION_KEY = "csrf_token"
SESSION_ID_SESSION_KEY = "_session_id"


def _ensure_session_id() -> str:
    session_id = session.get(SESSION_ID_SESSION_KEY)
    if session_id:
        return session_id
    session_id = secrets.token_hex(16)
    session[SESSION_ID_SESSION_KEY] = session_id
    return session_id


def generate_csrf_token() -> str:
    """Return a stable CSRF token per-session."""
    _ensure_session_id()
    token = session.get(CSRF_TOKEN_SESSION_KEY)
    if token:
        return token
    legacy = session.get(LEGACY_CSRF_TOKEN_SESSION_KEY)
    if legacy:
        session[CSRF_TOKEN_SESSION_KEY] = legacy
        return legacy
    token = secrets.token_hex(32)
    session[CSRF_TOKEN_SESSION_KEY] = token
    session[LEGACY_CSRF_TOKEN_SESSION_KEY] = token
    return token


def validate_csrf_token(token: str) -> bool:
    """Validate a provided CSRF token against the session."""
    if not token:
        return False
    expected = session.get(CSRF_TOKEN_SESSION_KEY)
    if not expected:
        expected = session.get(LEGACY_CSRF_TOKEN_SESSION_KEY, "")
        if expected:
            session[CSRF_TOKEN_SESSION_KEY] = expected
    if not expected:
        return False
    _ensure_session_id()
    return secrets.compare_digest(token, expected)


def get_session_csrf_token() -> str | None:
    """Return the current session-bound CSRF token without generating a new one."""
    return session.get(CSRF_TOKEN_SESSION_KEY) or session.get(LEGACY_CSRF_TOKEN_SESSION_KEY)


def get_session_id() -> str | None:
    """Return the session identifier (if established)."""
    return session.get(SESSION_ID_SESSION_KEY)


__all__ = [
    "CSRF_TOKEN_SESSION_KEY",
    "LEGACY_CSRF_TOKEN_SESSION_KEY",
    "SESSION_ID_SESSION_KEY",
    "generate_csrf_token",
    "validate_csrf_token",
    "get_session_csrf_token",
    "get_session_id",
]
