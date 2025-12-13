"""Habit rules for consistency and streak insights."""

from __future__ import annotations

from typing import List

from lifeos.core.events.event_models import EventRecord


def apply_rules(event: EventRecord) -> List[dict]:
    if event.event_type == "habits.habit.logged":
        streak = event.payload.get("streak")
        return [
            {
                "type": "habit_progress",
                "message": f"You logged a habit. Current streak: {streak}",
                "severity": "info",
                "context": event.payload,
            }
        ]
    return []
