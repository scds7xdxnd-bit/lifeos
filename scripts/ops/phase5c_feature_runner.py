#!/usr/bin/env python3
"""Phase 5c feature store runner (daily + window rebuild)."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, time, timedelta
from typing import Iterable, Optional

from lifeos import create_app
from lifeos.core.events.event_models import EventRecord
from lifeos.core.feature_store.models import FeatureStoreEntry
from lifeos.core.feature_store.service import build_feature_write, write_feature
from lifeos.core.users.models import User
from lifeos.extensions import db

FEATURE_VERSION = "1.0.0"
LIFECYCLE_STATE = "shadow"
BACKFILL_POLICY = "allowed"

CANONICAL_EVENT_TYPES = {
    "insight_viewed": "insight.viewed.count",
    "insight_dismissed": "insight.dismissed.count",
    "insight_saved": "insight.saved.count",
    "insight_shared": "insight.shared.count",
    "insight_feedback_positive": "insight.feedback_positive.count",
    "insight_feedback_negative": "insight.feedback_negative.count",
    "insight_reported_issue": "insight.reported_issue.count",
}

ALIAS_ACTION_MAP = {
    "dismiss": "insight_dismissed",
    "dismissed": "insight_dismissed",
    "snooze": "insight_dismissed",
    "act": "insight_feedback_positive",
    "feedback_positive": "insight_feedback_positive",
    "feedback_negative": "insight_feedback_negative",
    "reported_issue": "insight_reported_issue",
    "saved": "insight_saved",
    "shared": "insight_shared",
    "viewed": "insight_viewed",
}


def _iter_users(user_id: int | None = None) -> Iterable[User]:
    if user_id is not None:
        user = User.query.get(int(user_id))
        return [user] if user else []
    return User.query.all()


def _date_range(start: date, end: date) -> Iterable[date]:
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def _window_bounds(as_of_date: date, window_days: int) -> tuple[datetime, datetime]:
    end_ts = datetime.combine(as_of_date, time.max)
    start_date = as_of_date - timedelta(days=window_days - 1)
    start_ts = datetime.combine(start_date, time.min)
    return start_ts, end_ts


def _canonical_event_type(event: EventRecord) -> Optional[str]:
    if event.event_type in CANONICAL_EVENT_TYPES:
        return event.event_type
    if event.event_type == "insights.action":
        action = str((event.payload or {}).get("action") or "").strip().lower()
        return ALIAS_ACTION_MAP.get(action)
    return None


def _collect_events(user_id: int, start_ts: datetime, end_ts: datetime) -> list[EventRecord]:
    return (
        EventRecord.query.filter(EventRecord.user_id == user_id)
        .filter(EventRecord.created_at >= start_ts)
        .filter(EventRecord.created_at <= end_ts)
        .order_by(EventRecord.created_at.asc())
        .all()
    )


def _aggregate_events(events: Iterable[EventRecord]) -> dict[str, dict]:
    counts: dict[str, dict] = {}
    for event in events:
        canonical = _canonical_event_type(event)
        if not canonical:
            continue
        bucket = counts.setdefault(
            canonical,
            {"count": 0, "event_ids": [], "event_types": set()},
        )
        bucket["count"] += 1
        bucket["event_ids"].append(event.id)
        bucket["event_types"].add(event.event_type)
    return counts


def _provenance(events: dict) -> dict:
    event_ids = events.get("event_ids") or []
    sample_ids = event_ids[:50]
    digest = hashlib.sha256(",".join(str(eid) for eid in event_ids).encode("utf-8")).hexdigest()
    return {
        "event_count": len(event_ids),
        "event_ids_sample": sample_ids,
        "event_ids_hash": digest,
    }


def _write_counts(
    *,
    user_id: int,
    as_of_ts: datetime,
    window: str,
    counts: dict[str, dict],
    upsert_safe: bool,
) -> int:
    stored = 0
    for canonical_type, payload in counts.items():
        feature_name = CANONICAL_EVENT_TYPES.get(canonical_type)
        if not feature_name:
            continue
        provenance = _provenance(payload)
        source_types = sorted(payload.get("event_types") or [])
        feature = build_feature_write(
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
            feature_name=feature_name,
            value=int(payload.get("count") or 0),
            dtype="int",
            window=window,
            as_of_ts=as_of_ts,
            feature_version=FEATURE_VERSION,
            source_event_types=source_types,
            provenance_ref=provenance,
            lifecycle_state=LIFECYCLE_STATE,
            backfill_policy=BACKFILL_POLICY,
            upsert_safe=upsert_safe,
        )
        write_feature(feature)
        stored += 1
    return stored


def _run_window(
    *,
    user_id: int,
    as_of_date: date,
    window_days: int,
    upsert_safe: bool,
) -> int:
    start_ts, end_ts = _window_bounds(as_of_date, window_days)
    events = _collect_events(user_id, start_ts, end_ts)
    counts = _aggregate_events(events)
    window_label = f"{window_days}d"
    return _write_counts(
        user_id=user_id,
        as_of_ts=end_ts,
        window=window_label,
        counts=counts,
        upsert_safe=upsert_safe,
    )


def _verify_window(
    *,
    user_id: int,
    as_of_date: date,
    window_days: int,
) -> int:
    start_ts, end_ts = _window_bounds(as_of_date, window_days)
    events = _collect_events(user_id, start_ts, end_ts)
    counts = _aggregate_events(events)
    mismatches = 0
    for canonical_type, payload in counts.items():
        feature_name = CANONICAL_EVENT_TYPES.get(canonical_type)
        if not feature_name:
            continue
        record = FeatureStoreEntry.query.filter_by(
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
            feature_name=feature_name,
            as_of_ts=end_ts,
            feature_version=FEATURE_VERSION,
        ).first()
        expected = int(payload.get("count") or 0)
        if not record:
            mismatches += 1
            continue
        stored_value = record.value
        if int(stored_value or 0) != expected:
            mismatches += 1
    return mismatches


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase 5c feature store computations.")
    parser.add_argument("--mode", choices=("daily", "window", "both"), default="both")
    parser.add_argument("--as-of", dest="as_of", default=None)
    parser.add_argument("--window-days", default="1,7,30")
    parser.add_argument("--start-date", dest="start_date", default=None)
    parser.add_argument("--end-date", dest="end_date", default=None)
    parser.add_argument("--user-id", type=int, default=None)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    window_days = [int(item) for item in args.window_days.split(",") if item.strip()]

    app = create_app()
    with app.app_context():
        users = _iter_users(args.user_id)
        processed = 0
        stored_total = 0
        mismatches_total = 0

        if args.start_date and args.end_date:
            start = date.fromisoformat(args.start_date)
            end = date.fromisoformat(args.end_date)
            dates = list(_date_range(start, end))
        else:
            dates = [as_of]

        for user in users:
            if not user:
                continue
            for target_date in dates:
                for days in window_days:
                    if args.verify:
                        mismatches_total += _verify_window(
                            user_id=user.id,
                            as_of_date=target_date,
                            window_days=days,
                        )
                    if args.mode in ("window", "both") or (args.mode == "daily" and days == 1):
                        stored_total += _run_window(
                            user_id=user.id,
                            as_of_date=target_date,
                            window_days=days,
                            upsert_safe=bool(args.start_date and args.end_date),
                        )
            processed += 1

        if args.verify:
            print("phase5c: verification mismatches=%d" % mismatches_total)
        print(
            "phase5c: users=%d stored=%d windows=%s dates=%d"
            % (processed, stored_total, ",".join(str(d) for d in window_days), len(dates))
        )


if __name__ == "__main__":
    main()
