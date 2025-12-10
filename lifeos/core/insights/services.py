"""Insight services: persist, query, and simple event lookups."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List, Sequence

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.extensions import db


def persist_insights(
    insights: Sequence[dict],
    event: EventRecord,
) -> List[InsightRecord]:
    """Save generated insights tied to the originating event."""
    saved: List[InsightRecord] = []
    for ins in insights:
        rec = InsightRecord(
            user_id=event.user_id,
            event_id=event.id,
            event_type=event.event_type,
            kind=ins.get("type") or "generic",
            message=ins.get("message") or "",
            severity=ins.get("severity") or "info",
            data=ins.get("context") or {},
        )
        db.session.add(rec)
        saved.append(rec)
    if saved:
        db.session.commit()
    return saved


def recent_events(
    user_id: int,
    event_types: Iterable[str],
    days: int = 7,
    limit: int = 20,
) -> List[EventRecord]:
    """Fetch recent events for cross-domain heuristics."""
    since = datetime.utcnow() - timedelta(days=days)
    return (
        EventRecord.query.filter(EventRecord.user_id == user_id)
        .filter(EventRecord.event_type.in_(list(event_types)))
        .filter(EventRecord.created_at >= since)
        .order_by(EventRecord.created_at.desc())
        .limit(limit)
        .all()
    )


def fetch_insights(user_id: int, limit: int = 20) -> List[InsightRecord]:
    return InsightRecord.query.filter_by(user_id=user_id).order_by(InsightRecord.created_at.desc()).limit(limit).all()
