"""Domain adapters for timeline observations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from lifeos.core.events.event_models import EventRecord
from lifeos.core.timeline.contracts import TimelineObservation
from lifeos.core.timeline.semantics import isoformat_utc, local_date_from_value


@dataclass(frozen=True)
class TimelineAdapter:
    domain: str
    supported_event_types: tuple[str, ...]
    value_label: str
    observation_label: str
    supports_streaks: bool
    build_observation: Callable[[EventRecord, str], TimelineObservation | None]

    def matches(self, event_type: str | None) -> bool:
        value = str(event_type or "")
        return value in set(self.supported_event_types)


def build_event_observation(
    *,
    event: EventRecord,
    timezone_token: str,
    anchor_value: object,
    value: float,
) -> TimelineObservation | None:
    anchor_local_date = local_date_from_value(anchor_value, timezone_token)
    if anchor_local_date is None:
        return None
    anchor_ts = event.created_at
    if isinstance(anchor_value, str):
        try:
            from datetime import datetime

            parsed = datetime.fromisoformat(anchor_value)
            anchor_ts = parsed
        except ValueError:
            pass
    elif hasattr(anchor_value, "isoformat") and hasattr(anchor_value, "year"):
        anchor_ts = anchor_value  # datetime/date path; converted later for evidence labels.
    if getattr(anchor_ts, "hour", None) is None:
        from datetime import datetime, time

        anchor_ts = datetime.combine(anchor_local_date, time.min)
    return TimelineObservation(
        domain=str(event.event_type or "").split(".", 1)[0],
        source_kind="event_record",
        source_id=event.id,
        source_ref=f"event:{event.id}" if event.id is not None else None,
        event_type=event.event_type,
        anchor_ts=anchor_ts,
        anchor_local_date=anchor_local_date,
        created_at=event.created_at,
        value=float(value or 0.0),
        metadata={
            "anchor_iso": isoformat_utc(anchor_ts),
            "payload": dict(event.payload or {}),
        },
    )


__all__ = ["TimelineAdapter", "build_event_observation"]
