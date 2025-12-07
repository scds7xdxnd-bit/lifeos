"""Event persistence and dispatch."""

from __future__ import annotations

from typing import Optional

from lifeos.core.events.event_bus import event_bus
from lifeos.core.events.event_models import EventRecord
from lifeos.extensions import db


def log_event(event_type: str, payload: dict, user_id: Optional[int] = None) -> EventRecord:
    """Persist an event and publish to subscribers."""
    record = EventRecord(event_type=event_type, payload=payload, user_id=user_id)
    db.session.add(record)
    db.session.commit()
    event_bus.publish(record)
    return record

