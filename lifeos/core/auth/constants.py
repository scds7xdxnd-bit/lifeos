"""Session lifecycle constants (structure-only, Phase 3b½ scaffold)."""

from __future__ import annotations

# Session lifecycle states (no behavioral wiring yet; contracts only)
SESSION_STATE_ACTIVE = "active"
SESSION_STATE_INVALIDATED = "invalidated"
SESSION_STATE_EXPIRED = "expired"
SESSION_STATE_ADMIN_RESET = "admin_reset"

# Scope values for admin resets
SESSION_SCOPE_SINGLE = "single"
SESSION_SCOPE_ALL = "all"

__all__ = [
    "SESSION_STATE_ACTIVE",
    "SESSION_STATE_INVALIDATED",
    "SESSION_STATE_EXPIRED",
    "SESSION_STATE_ADMIN_RESET",
    "SESSION_SCOPE_SINGLE",
    "SESSION_SCOPE_ALL",
]
