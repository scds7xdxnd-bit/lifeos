#!/usr/bin/env python3
"""Phase 5a interpretation runner (background job).

Runs proposal generation for recent timeline events. This is idempotent because
interpretations are fingerprinted in the substrate service.
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta

from lifeos import create_app
from lifeos.core.insights.substrate_models import TimelineEvent
from lifeos.core.insights.substrate_service import generate_interpretations_for_timeline_event


def _run_once(since_minutes: int, limit: int) -> None:
    cutoff = datetime.utcnow() - timedelta(minutes=since_minutes)
    run_started_at = datetime.utcnow()
    query = TimelineEvent.query.filter(TimelineEvent.ingested_at >= cutoff).order_by(
        TimelineEvent.ingested_at.desc()
    )
    if limit > 0:
        query = query.limit(limit)
    events = query.all()

    processed = 0
    proposals = 0
    created = 0

    for event in events:
        processed += 1
        items = generate_interpretations_for_timeline_event(event)
        proposals += len(items)
        for item in items:
            if item.created_at and item.created_at >= run_started_at:
                created += 1

    print(
        "phase5a: processed=%d proposals=%d created=%d since_minutes=%d limit=%d"
        % (processed, proposals, created, since_minutes, limit)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 5a interpretation proposals.")
    parser.add_argument("--since-minutes", type=int, default=60)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval-seconds", type=int, default=60)
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if not app.config.get("ENABLE_TIMELINE_INGESTION", True):
            print("phase5a: timeline ingestion disabled; exiting")
            return
        if not (
            app.config.get("ENABLE_INTERPRETATION_RELATIONSHIP", True)
            or app.config.get("ENABLE_INTERPRETATION_OBLIGATION", False)
        ):
            print("phase5a: no interpretation types enabled; exiting")
            return

        if args.loop:
            while True:
                _run_once(args.since_minutes, args.limit)
                time.sleep(max(1, args.interval_seconds))
        else:
            _run_once(args.since_minutes, args.limit)


if __name__ == "__main__":
    main()
