"""Review queue projection (read-only, Phase 3a)."""

from __future__ import annotations

from typing import List

from lifeos.core.events.semantic_contracts import EVENT_SEMANTIC_CONTRACTS
from lifeos.core.insights.models import InsightRecord
from lifeos.readmodels.contracts import ReadModelContract

REVIEW_QUEUE_CONTRACT = ReadModelContract(
    name="insight_review_queue",
    domain="insights",
    consumed_events=list(EVENT_SEMANTIC_CONTRACTS.keys()),
    replay_start_version="v1",
    idempotency_key="event_id",
    type="timeline",
    rebuild_strategy="cached query filtered in-memory by confidence_band",
)


def fetch_review_queue_projection(user_id: int, limit: int = 50, offset: int = 0) -> List[InsightRecord]:
    """Return a review-only insight projection (confidence_band=needs_review)."""
    query = (
        InsightRecord.query.filter_by(user_id=user_id)
        .order_by(InsightRecord.created_at.desc())
        .offset(offset)
        .limit(limit * 4)
    )
    items = query.all()
    review_items = []
    for rec in items:
        band = (rec.confidence_band or "").lower() if rec.confidence_band else ""
        routing = (rec.routing or "").lower() if rec.routing else ""
        if not band or not routing:
            data = rec.data or {}
            if not isinstance(data, dict):
                continue
            band = band or str(data.get("confidence_band") or "").lower()
            routing = routing or str(data.get("routing") or "").lower()
        if band == "needs_review" or routing == "review_only":
            review_items.append(rec)
        if len(review_items) >= limit:
            break
    return review_items


__all__ = ["REVIEW_QUEUE_CONTRACT", "fetch_review_queue_projection"]
