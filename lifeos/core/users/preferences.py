"""Default and merged preferences for users."""

from __future__ import annotations

from typing import Any, Dict

from lifeos.core.users.models import User, UserPreference

DEFAULT_PREFS: Dict[str, Any] = {
    "currency": "USD",
    "language": "en",
    "timezone": "UTC",
    "insights_opt_in": True,
}


def get_preferences(user: User) -> Dict[str, Any]:
    """Merge stored preferences with defaults."""
    prefs = DEFAULT_PREFS.copy()
    for pref in user.preferences:
        prefs[pref.key] = pref.value
    return prefs


def set_preference(user: User, key: str, value: Any) -> None:
    existing = next((p for p in user.preferences if p.key == key), None)
    if existing:
        existing.value = value
    else:
        user.preferences.append(UserPreference(key=key, value=value))

