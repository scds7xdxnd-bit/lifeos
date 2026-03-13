"""Skills timeline adapter."""

from __future__ import annotations

from lifeos.core.events.event_models import EventRecord
from lifeos.core.timeline.adapters.base import TimelineAdapter, build_event_observation


def _skills_observation(event: EventRecord, timezone_token: str):
    payload = event.payload or {}
    duration = payload.get("duration_minutes")
    try:
        value = float(duration or 0.0)
    except (TypeError, ValueError):
        value = 0.0
    return build_event_observation(
        event=event,
        timezone_token=timezone_token,
        anchor_value=payload.get("practiced_at") or event.created_at,
        value=value,
    )


SKILLS_TIMELINE_ADAPTER = TimelineAdapter(
    domain="skills",
    supported_event_types=("skills.practice.logged",),
    value_label="practice minutes",
    observation_label="practice sessions",
    supports_streaks=True,
    build_observation=_skills_observation,
)


__all__ = ["SKILLS_TIMELINE_ADAPTER"]
