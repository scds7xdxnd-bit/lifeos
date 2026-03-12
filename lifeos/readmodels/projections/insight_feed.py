"""Insight feed projection (read-only, Phase 3a)."""

from __future__ import annotations

from lifeos.core.events.semantic_contracts import EVENT_SEMANTIC_CONTRACTS
from lifeos.core.insights.schemas import InsightsFeedQuery
from lifeos.core.insights.services import list_insights_feed
from lifeos.readmodels.contracts import ReadModelContract

INSIGHT_FEED_CONTRACT = ReadModelContract(
    name="insight_feed",
    domain="insights",
    consumed_events=list(EVENT_SEMANTIC_CONTRACTS.keys()),
    replay_start_version="v1",
    idempotency_key="event_id",
    type="timeline",
    rebuild_strategy="cached query over insight_record with deterministic ordering",
)


def fetch_insight_feed_projection(user_id: int, filters: InsightsFeedQuery):
    """Return a read-only insight feed projection."""
    return list_insights_feed(user_id=user_id, filters=filters)


__all__ = ["INSIGHT_FEED_CONTRACT", "fetch_insight_feed_projection"]
