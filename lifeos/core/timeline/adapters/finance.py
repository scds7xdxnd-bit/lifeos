"""Finance timeline adapter."""

from __future__ import annotations

from lifeos.core.events.event_models import EventRecord
from lifeos.core.timeline.adapters.base import TimelineAdapter, build_event_observation

_SUPPORTED = (
    "finance.transaction.created",
    "finance.journal.posted",
)


def _finance_observation(event: EventRecord, timezone_token: str):
    payload = event.payload or {}
    if event.event_type == "finance.transaction.created":
        amount = payload.get("amount")
        try:
            value = abs(float(amount or 0.0))
        except (TypeError, ValueError):
            value = 0.0
        return build_event_observation(
            event=event,
            timezone_token=timezone_token,
            anchor_value=payload.get("occurred_at") or event.created_at,
            value=value,
        )
    return build_event_observation(
        event=event,
        timezone_token=timezone_token,
        anchor_value=payload.get("posted_at") or payload.get("created_at") or event.created_at,
        value=0.0,
    )


FINANCE_TIMELINE_ADAPTER = TimelineAdapter(
    domain="finance",
    supported_event_types=_SUPPORTED,
    value_label="activity volume",
    observation_label="finance activity",
    supports_streaks=False,
    build_observation=_finance_observation,
)


__all__ = ["FINANCE_TIMELINE_ADAPTER"]
