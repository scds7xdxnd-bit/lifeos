"""Deterministic cross-domain evidence aggregation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord

SOURCE_KIND_PRIORITY = {
    "event_record": 0,
    "insight_record": 1,
    "read_model": 2,
}


@dataclass(frozen=True)
class NormalizedCrossDomainEvidence:
    source_domain: str
    source_kind: str
    source_ref: str
    event_type: str | None
    event_ts: str
    source_id: int | None
    event_count: int | None = None
    insight_count: int | None = None


def _sort_key(item: NormalizedCrossDomainEvidence) -> tuple[str, int, int]:
    return (
        item.event_ts or "",
        SOURCE_KIND_PRIORITY.get(item.source_kind, 99),
        int(item.source_id or 0),
    )


def aggregate_cross_domain_evidence(
    *,
    domains: tuple[str, str],
    timeframe_start: datetime,
    timeframe_end: datetime,
    as_of_ts: datetime,
    events_by_domain: dict[str, list[EventRecord]],
    insights_by_domain: dict[str, list[InsightRecord]],
) -> list[NormalizedCrossDomainEvidence]:
    normalized: list[NormalizedCrossDomainEvidence] = []
    for domain in sorted(domains):
        domain_events = sorted(
            events_by_domain.get(domain, []),
            key=lambda event: (event.created_at.isoformat() if event.created_at else "", event.id),
        )
        domain_insights = sorted(
            insights_by_domain.get(domain, []),
            key=lambda insight: (insight.created_at.isoformat() if insight.created_at else "", insight.id),
        )
        normalized.append(
            NormalizedCrossDomainEvidence(
                source_domain=domain,
                source_kind="read_model",
                source_ref=(
                    f"inquiry.event_count_projection:{domain}:{timeframe_start.date().isoformat()}:"
                    f"{timeframe_end.date().isoformat()}:{as_of_ts.isoformat()}"
                ),
                event_type=None,
                event_ts=as_of_ts.isoformat(),
                source_id=None,
                event_count=len(domain_events),
                insight_count=len(domain_insights),
            )
        )
        for event in domain_events:
            normalized.append(
                NormalizedCrossDomainEvidence(
                    source_domain=domain,
                    source_kind="event_record",
                    source_ref=f"event_record:{event.id}",
                    event_type=event.event_type,
                    event_ts=event.created_at.isoformat() if event.created_at else "",
                    source_id=event.id,
                )
            )
        for insight in domain_insights:
            normalized.append(
                NormalizedCrossDomainEvidence(
                    source_domain=domain,
                    source_kind="insight_record",
                    source_ref=f"insight_record:{insight.id}",
                    event_type=insight.event_type,
                    event_ts=insight.created_at.isoformat() if insight.created_at else "",
                    source_id=insight.id,
                )
            )
    return sorted(normalized, key=_sort_key)


__all__ = [
    "NormalizedCrossDomainEvidence",
    "SOURCE_KIND_PRIORITY",
    "aggregate_cross_domain_evidence",
]
