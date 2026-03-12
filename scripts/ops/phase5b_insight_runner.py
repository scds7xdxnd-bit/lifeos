#!/usr/bin/env python3
"""Phase 5b deterministic insight runner (features + insights)."""

from __future__ import annotations

import argparse
import time
from datetime import date, datetime, timedelta
from typing import Iterable

from lifeos import create_app
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.feature_service import (
    SUPPORTED_EVENT_TYPES,
    compute_features_for_user,
    store_features_daily,
)
from lifeos.core.insights.registry import get_enabled_insight_definitions
from lifeos.core.insights.rules import phase5b_rules
from lifeos.core.insights.services import persist_insights
from lifeos.core.users.models import User


def _resolve_window_days() -> int:
    definitions = list(get_enabled_insight_definitions())
    if not definitions:
        return 30
    return max(definition.window_days for definition in definitions)


def _iter_users(user_id: int | None = None) -> Iterable[User]:
    if user_id is not None:
        user = User.query.get(int(user_id))
        return [user] if user else []
    return User.query.all()


def _run_features(window_days: int, user_id: int | None) -> None:
    end_date = date.today()
    start_date = end_date - timedelta(days=window_days - 1)
    users = _iter_users(user_id)
    processed = 0
    for user in users:
        if not user:
            continue
        features_by_date = compute_features_for_user(user.id, start_date, end_date)
        store_features_daily(user.id, features_by_date)
        processed += 1
    print("phase5b: features stored for users=%d window_days=%d" % (processed, window_days))


def _run_insights(since_minutes: int, limit: int, user_id: int | None) -> None:
    cutoff = datetime.utcnow() - timedelta(minutes=since_minutes)
    query = (
        EventRecord.query.filter(EventRecord.event_type.in_(list(SUPPORTED_EVENT_TYPES)))
        .filter(EventRecord.created_at >= cutoff)
        .order_by(EventRecord.created_at.desc())
    )
    if user_id is not None:
        query = query.filter(EventRecord.user_id == int(user_id))
    if limit > 0:
        query = query.limit(limit)

    events = query.all()
    processed = 0
    emitted = 0
    for event in events:
        processed += 1
        insights = phase5b_rules.apply_rules(event)
        if insights:
            persist_insights(insights, event)
            emitted += len(insights)
    print(
        "phase5b: insights processed=%d emitted=%d since_minutes=%d limit=%d"
        % (processed, emitted, since_minutes, limit)
    )


def _phase5b_enabled(app) -> bool:
    return app.config.get("ENABLE_PHASE5B_INSIGHTS", True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 5b features/insights.")
    parser.add_argument("--since-minutes", type=int, default=60)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--mode", choices=("features", "insights", "both"), default="both")
    parser.add_argument("--user-id", type=int, default=None)
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if not _phase5b_enabled(app):
            print("phase5b: insights disabled; exiting")
            return

        window_days = _resolve_window_days()

        def _run_once() -> None:
            if args.mode in ("features", "both"):
                _run_features(window_days, args.user_id)
            if args.mode in ("insights", "both"):
                _run_insights(args.since_minutes, args.limit, args.user_id)

        if args.loop:
            while True:
                _run_once()
                time.sleep(max(1, args.interval_seconds))
        else:
            _run_once()


if __name__ == "__main__":
    main()
