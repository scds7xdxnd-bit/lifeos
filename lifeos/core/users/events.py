"""User domain event catalog."""

from __future__ import annotations

USER_ONBOARDING_COMPLETED = "user.onboarding.completed"

EVENT_CATALOG = {
    USER_ONBOARDING_COMPLETED: {
        "version": "v1",
        "payload": {
            "payload_version": "int",
        },
    },
}

__all__ = [
    "USER_ONBOARDING_COMPLETED",
    "EVENT_CATALOG",
]
