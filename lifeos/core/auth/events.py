"""Auth domain event catalog."""

from __future__ import annotations

from lifeos.core.auth.session_events import (
    AUTH_SESSION_ADMIN_RESET,
    AUTH_SESSION_CREATED,
    AUTH_SESSION_INVALIDATED,
)

AUTH_USER_REGISTERED = "auth.user.registered"
AUTH_USER_USERNAME_REMINDER_REQUESTED = "auth.user.username_reminder_requested"
AUTH_USER_PASSWORD_RESET_REQUESTED = "auth.user.password_reset_requested"
AUTH_USER_PASSWORD_RESET_COMPLETED = "auth.user.password_reset_completed"

EVENT_CATALOG = {
    AUTH_USER_REGISTERED: {
        "version": "v1",
        "payload": {
            "user_id": "int",
            "email": "str",
            "full_name": "str?",
            "timezone": "str?",
        },
    },
    AUTH_USER_USERNAME_REMINDER_REQUESTED: {
        "version": "v1",
        "payload": {
            "user_id": "int?",
            "email": "str",
        },
    },
    AUTH_USER_PASSWORD_RESET_REQUESTED: {
        "version": "v1",
        "payload": {
            "user_id": "int?",
            "email": "str",
            "expires_at": "datetime?",
        },
    },
    AUTH_USER_PASSWORD_RESET_COMPLETED: {
        "version": "v1",
        "payload": {
            "user_id": "int",
            "reset_id": "int",
        },
    },
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
            "session_scope": "str",
            "session_id": "str?",
            "device_id": "str?",
            "reason": "str?",
            "initiated_by_admin_id": "int?",
        },
    },
}

__all__ = [
    "AUTH_USER_REGISTERED",
    "AUTH_USER_USERNAME_REMINDER_REQUESTED",
    "AUTH_USER_PASSWORD_RESET_REQUESTED",
    "AUTH_USER_PASSWORD_RESET_COMPLETED",
    "AUTH_SESSION_CREATED",
    "AUTH_SESSION_INVALIDATED",
    "AUTH_SESSION_ADMIN_RESET",
    "EVENT_CATALOG",
]
