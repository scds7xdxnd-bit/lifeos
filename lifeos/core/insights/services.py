"""Insight services: persist, query, and simple event lookups."""

from __future__ import annotations

from datetime import datetime, timedelta
from math import ceil
from typing import Iterable, List, Sequence, Tuple

from sqlalchemy import desc, nullslast, or_

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.personalization import rank_insights
from lifeos.core.insights.routing import enforce_confidence_routing
from lifeos.core.insights.schemas import InsightsFeedQuery
from lifeos.core.insights.telemetry import insight_telemetry
from lifeos.core.read_cache import read_cache
from lifeos.extensions import db

INSIGHTS_READ_CACHE_SCOPE = "insights.reads"
DEFAULT_INSIGHT_PRIORITY = 50
DEFAULT_DELIVERY_POLICY = "feed"


def persist_insights(
    insights: Sequence[dict],
    event: EventRecord,
) -> List[InsightRecord]:
    """Save generated insights tied to the originating event."""
    saved: List[InsightRecord] = []
    for ins in insights:
        insight_type = ins.get("type") or "generic"
        context = dict(ins.get("context") or {})
        priority = int(ins.get("priority") or DEFAULT_INSIGHT_PRIORITY)
        delivery_policy = str(ins.get("delivery_policy") or DEFAULT_DELIVERY_POLICY)
        confidence_band, routing = enforce_confidence_routing(
            insight_type=insight_type,
            event_type=event.event_type,
            severity=ins.get("severity"),
            context=context,
        )
        context.setdefault("confidence_band", confidence_band)
        context.setdefault("routing", routing)
        insight_telemetry.record_confidence(insight_type, confidence_band)
        rec = InsightRecord(
            user_id=event.user_id,
            event_id=event.id,
            event_type=event.event_type,
            kind=insight_type,
            message=ins.get("message") or "",
            severity=ins.get("severity") or "info",
            confidence_band=confidence_band,
            routing=routing,
            priority=priority,
            delivery_policy=delivery_policy,
            data=context,
        )
        db.session.add(rec)
        saved.append(rec)
    if saved:
        db.session.commit()
        read_cache.bump(INSIGHTS_READ_CACHE_SCOPE, event.user_id)
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
        domain_filters = [InsightRecord.event_type.like(f"{domain}.%") for domain in filters.domain]
        if domain_filters:
            query = query.filter(or_(*domain_filters))
    if filters.severity:
        query = query.filter(InsightRecord.severity == filters.severity)
    if filters.start_date:
        start_dt = datetime.combine(filters.start_date, datetime.min.time())
        query = query.filter(InsightRecord.created_at >= start_dt)
    if filters.end_date:
        end_dt = datetime.combine(filters.end_date, datetime.max.time())
        query = query.filter(InsightRecord.created_at <= end_dt)

    query = query.order_by(
        desc(InsightRecord.priority),
        nullslast(desc(InsightRecord.confidence_band)),
        desc(InsightRecord.created_at),
    )

    page = filters.page
    per_page = filters.per_page

    if filters.status:
        # Apply status filtering in-memory to avoid DB-specific JSON expressions.
        all_items = query.all()

        def _record_status(rec: InsightRecord) -> str | None:
            data = rec.data or {}
            if not isinstance(data, dict):
                return None
            status = data.get("status") or data.get("inference_status")
            return status.lower() if isinstance(status, str) else None

        filtered_items = [rec for rec in all_items if _record_status(rec) == filters.status]
        total = len(filtered_items)
        pages = ceil(total / per_page) if total else 0
        start = (page - 1) * per_page
        end = start + per_page
        items = filtered_items[start:end]
        items = rank_insights(user_id, items, context={"filters": filters})
        return items, total, page, pages

    total = query.count()
    pages = ceil(total / per_page) if total else 0

    items = query.offset((page - 1) * per_page).limit(per_page).all()
    items = rank_insights(user_id, items, context={"filters": filters})
    return items, total, page, pages
