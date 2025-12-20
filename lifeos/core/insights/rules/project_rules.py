"""Project/task related insights."""

from __future__ import annotations

from typing import List, TYPE_CHECKING

from lifeos.core.events.event_models import EventRecord

if TYPE_CHECKING:
    from lifeos.core.insights.replay import ReplayEvent


def apply_rules(event: EventRecord | "ReplayEvent") -> List[dict]:
    if event.event_type == "projects.task.completed":
        title = event.payload.get("title")
        return [
            {
                "type": "project_task_done",
                "message": f"Task completed: {title}",
                "severity": "info",
                "context": event.payload,
            }
        ]
    return []
