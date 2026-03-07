"""Health signals and alerts."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from lifeos.core.events.event_models import EventRecord

if TYPE_CHECKING:
    from lifeos.core.insights.replay import ReplayEvent


def apply_rules(event: EventRecord | "ReplayEvent") -> List[dict]:
    if event.event_type == "health.metric.updated":
        metric = event.payload.get("metric")
        value = event.payload.get("value")
        return [
            {
                "type": "health_metric",
                "message": f"New health metric {metric}: {value}",
                "severity": "info",
                "context": event.payload,
            }
        ]
    return []
