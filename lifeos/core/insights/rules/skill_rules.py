"""Skill development rules."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from lifeos.core.events.event_models import EventRecord

if TYPE_CHECKING:
    from lifeos.core.insights.replay import ReplayEvent


def apply_rules(event: EventRecord | "ReplayEvent") -> List[dict]:
    if event.event_type == "skills.practice.logged":
        minutes = event.payload.get("minutes", 0)
        return [
            {
                "type": "skill_practice",
                "message": f"Practice logged ({minutes} minutes).",
                "severity": "info",
                "context": event.payload,
            }
        ]
    return []
