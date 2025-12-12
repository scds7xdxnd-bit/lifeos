"""Insight services: persist, query, and simple event lookups."""

from __future__ import annotations

from datetime import datetime, timedelta
from math import ceil
from typing import Iterable, List, Sequence, Tuple

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.schemas import InsightsFeedQuery
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


def list_insights_feed(
    user_id: int,
    filters: InsightsFeedQuery,
) -> Tuple[List[InsightRecord], int, int, int]:
    """Return paginated insights scoped to a user with optional filters."""
    query = InsightRecord.query.filter(InsightRecord.user_id == user_id)

    if filters.domain:
        query = query.filter(InsightRecord.event_type.like(f"{filters.domain}.%"))
    if filters.severity:
        query = query.filter(InsightRecord.severity == filters.severity)
    if filters.start_date:
        start_dt = datetime.combine(filters.start_date, datetime.min.time())
        query = query.filter(InsightRecord.created_at >= start_dt)
    if filters.end_date:
        end_dt = datetime.combine(filters.end_date, datetime.max.time())
        query = query.filter(InsightRecord.created_at <= end_dt)

    query = query.order_by(InsightRecord.created_at.desc())

    total = query.count()
    page = filters.page
    per_page = filters.per_page
    pages = ceil(total / per_page) if total else 0

    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total, page, pages
