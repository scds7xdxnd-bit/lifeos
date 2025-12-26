#!/usr/bin/env python3
"""Phase 5b observability snapshot (counts + action rates)."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta

from lifeos import create_app
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord


def _count_insights(since_hours: int) -> dict[str, int]:
    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    rows = (
        InsightRecord.query.filter(InsightRecord.created_at >= cutoff)
        .with_entities(InsightRecord.kind)
        .all()
    )
    counter: Counter[str] = Counter()
    for (kind,) in rows:
        counter[str(kind)] += 1
    return dict(counter)


def _count_actions(since_hours: int) -> dict[str, int]:
    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    rows = (
        EventRecord.query.filter(EventRecord.created_at >= cutoff)
        .filter(EventRecord.event_type == "insights.action")
        .with_entities(EventRecord.payload)
        .all()
    )
    counter: Counter[str] = Counter()
    for (payload,) in rows:
        action = None
        if isinstance(payload, dict):
            action = payload.get("action")
        counter[str(action or "unknown")] += 1
    return dict(counter)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 5b insight observability snapshot.")
    parser.add_argument("--since-hours", type=int, default=24)
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        insights = _count_insights(args.since_hours)
        actions = _count_actions(args.since_hours)

    print("Phase 5b observability snapshot (last %d hours)" % args.since_hours)
    print("Insight counts by type:")
    if not insights:
        print("  (no insights found)")
    else:
        for key, value in sorted(insights.items()):
            print("  %s: %s" % (key, value))

    print("Insight action counts:")
    if not actions:
        print("  (no insight actions found; ensure telemetry ingestion is configured)")
    else:
        for key, value in sorted(actions.items()):
            print("  %s: %s" % (key, value))


if __name__ == "__main__":
    main()
