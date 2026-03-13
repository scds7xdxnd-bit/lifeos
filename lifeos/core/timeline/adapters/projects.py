"""Projects timeline adapter."""

from __future__ import annotations

from lifeos.core.events.event_models import EventRecord
from lifeos.core.timeline.adapters.base import TimelineAdapter, build_event_observation


def _projects_observation(event: EventRecord, timezone_token: str):
    payload = event.payload or {}
    anchor = payload.get("logged_at") or payload.get("completed_at") or event.created_at
    return build_event_observation(
        event=event,
        timezone_token=timezone_token,
        anchor_value=anchor,
        value=1.0,
    )


PROJECTS_TIMELINE_ADAPTER = TimelineAdapter(
    domain="projects",
    supported_event_types=("projects.task.completed", "projects.task.logged"),
    value_label="recorded activity",
    observation_label="project activity",
    supports_streaks=False,
    build_observation=_projects_observation,
)


__all__ = ["PROJECTS_TIMELINE_ADAPTER"]
