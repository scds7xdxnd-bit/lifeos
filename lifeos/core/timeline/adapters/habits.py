"""Habits timeline adapter."""

from __future__ import annotations

from lifeos.core.events.event_models import EventRecord
from lifeos.core.timeline.adapters.base import TimelineAdapter, build_event_observation


def _habits_observation(event: EventRecord, timezone_token: str):
    payload = event.payload or {}
    return build_event_observation(
        event=event,
        timezone_token=timezone_token,
        anchor_value=payload.get("logged_date") or event.created_at,
        value=1.0,
    )


HABITS_TIMELINE_ADAPTER = TimelineAdapter(
    domain="habits",
    supported_event_types=("habits.habit.logged",),
    value_label="logged activity",
    observation_label="habit logs",
    supports_streaks=True,
    build_observation=_habits_observation,
)


__all__ = ["HABITS_TIMELINE_ADAPTER"]
