"""Contracts for session lifecycle events (structure-only)."""

from __future__ import annotations

AUTH_SESSION_CREATED = "auth.session.created"
AUTH_SESSION_INVALIDATED = "auth.session.invalidated"
AUTH_SESSION_ADMIN_RESET = "auth.session.admin_reset"

EVENT_CATALOG = {
    AUTH_SESSION_CREATED: {
        "version": "v1",
        "payload": {"session_id": "str", "user_id": "int", "device_id": "str?", "created_at": "datetime"},
    },
    AUTH_SESSION_INVALIDATED: {
        "version": "v1",
        "payload": {
            "session_id": "str",
            "user_id": "int",
            "device_id": "str?",
            "invalidated_at": "datetime",
            "reason": "str?",
        },
    },
    AUTH_SESSION_ADMIN_RESET: {
        "version": "v1",
        "payload": {
            "user_id": "int",
            "session_scope": "str",  # 'single'|'all'
            "session_id": "str?",
            "device_id": "str?",
            "reason": "str?",
            "initiated_by_admin_id": "int?",
        },
    },
}

__all__ = [
    "AUTH_SESSION_CREATED",
    "AUTH_SESSION_INVALIDATED",
    "AUTH_SESSION_ADMIN_RESET",
    "EVENT_CATALOG",
]
