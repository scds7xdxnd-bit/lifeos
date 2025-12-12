"""Auth domain event catalog."""

from __future__ import annotations

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
}

__all__ = [
    "AUTH_USER_REGISTERED",
    "AUTH_USER_USERNAME_REMINDER_REQUESTED",
    "AUTH_USER_PASSWORD_RESET_REQUESTED",
    "AUTH_USER_PASSWORD_RESET_COMPLETED",
    "EVENT_CATALOG",
]
