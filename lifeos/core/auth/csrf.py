"""Lightweight CSRF token helpers using the session."""

from __future__ import annotations

import secrets
from flask import session

CSRF_TOKEN_SESSION_KEY = "_csrf_token"


def generate_csrf_token() -> str:
    """Return a stable CSRF token per-session."""
    token = session.get(CSRF_TOKEN_SESSION_KEY)
    if not token:
        token = secrets.token_hex(32)
        session[CSRF_TOKEN_SESSION_KEY] = token
    return token


def validate_csrf_token(token: str) -> bool:
    """Validate a provided CSRF token against the session."""
    if not token:
        return False
    return secrets.compare_digest(token, session.get(CSRF_TOKEN_SESSION_KEY, ""))

