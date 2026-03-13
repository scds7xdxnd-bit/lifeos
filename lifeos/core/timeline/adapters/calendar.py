"""Calendar timeline adapter."""

from __future__ import annotations

from lifeos.core.events.event_models import EventRecord
from lifeos.core.timeline.adapters.base import TimelineAdapter, build_event_observation


def _calendar_observation(event: EventRecord, timezone_token: str):
    payload = event.payload or {}
    return build_event_observation(
        event=event,
        timezone_token=timezone_token,
        anchor_value=payload.get("start_time") or payload.get("synced_at") or event.created_at,
        value=1.0,
    )


CALENDAR_TIMELINE_ADAPTER = TimelineAdapter(
    domain="calendar",
    supported_event_types=("calendar.event.created", "calendar.event.synced"),
    value_label="scheduled activity",
    observation_label="calendar events",
    supports_streaks=False,
    build_observation=_calendar_observation,
)


__all__ = ["CALENDAR_TIMELINE_ADAPTER"]
