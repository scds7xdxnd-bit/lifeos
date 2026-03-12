#!/usr/bin/env python3
"""Seed calendar time-canvas fixture cases into the database."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path

from lifeos import create_app
from lifeos.core.users.models import User
from lifeos.core.auth.password import hash_password
from lifeos.domains.calendar.models.calendar_event import CalendarEvent
from lifeos.domains.calendar.services.calendar_service import create_calendar_event
from lifeos.extensions import db

FIXTURE_PATH = Path("lifeos/tests/fixtures/calendar_time_canvas_cases.json")


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _to_event_window(entry: dict) -> tuple[datetime, datetime | None]:
    start_raw = entry["start"]
    end_raw = entry.get("end")
    all_day = bool(entry.get("all_day"))

    if "T" in start_raw:
        start_dt = _parse_datetime(start_raw)
    else:
        start_dt = datetime.combine(_parse_date(start_raw), time.min)

    if end_raw:
        if "T" in end_raw:
            end_dt = _parse_datetime(end_raw)
        else:
            end_dt = datetime.combine(_parse_date(end_raw), time.min)
    else:
        end_dt = None

    if all_day:
        # Treat end date as inclusive; convert to exclusive boundary for overlap queries.
        if end_dt is None:
            end_dt = start_dt + timedelta(days=1)
        else:
            end_dt = end_dt + timedelta(days=1)
    return start_dt, end_dt


def _load_fixtures() -> dict:
    if not FIXTURE_PATH.exists():
        raise SystemExit(f"Fixture not found: {FIXTURE_PATH}")
    return json.loads(FIXTURE_PATH.read_text())


def _get_or_create_user(email: str) -> User:
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(email=email, password_hash=hash_password("calendar-seed-123"))
    db.session.add(user)
    db.session.commit()
    return user


def _purge_fixture_events(user_id: int) -> None:
    CalendarEvent.query.filter_by(user_id=user_id).filter(
        CalendarEvent.metadata_.op("->>")("fixture") == "calendar_time_canvas_cases"
    ).delete(synchronize_session=False)
    db.session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed calendar time-canvas fixture cases.")
    parser.add_argument("--email", default="calendar.qa@example.com", help="User email for seeded events.")
    parser.add_argument("--purge", action="store_true", help="Delete existing fixture events before seeding.")
    args = parser.parse_args()

    payload = _load_fixtures()
    cases = payload.get("cases") or []

    app = create_app()
    with app.app_context():
        user = _get_or_create_user(args.email)
        if args.purge:
            _purge_fixture_events(user.id)

        for case in cases:
            case_id = case["id"]
            for idx, entry in enumerate(case["events"], start=1):
                start_dt, end_dt = _to_event_window(entry)
                create_calendar_event(
                    user_id=user.id,
                    title=entry["title"],
                    start_time=start_dt,
                    end_time=end_dt,
                    all_day=bool(entry.get("all_day")),
                    metadata={
                        "case_id": case_id,
                        "fixture": "calendar_time_canvas_cases",
                        "fixture_index": idx,
                    },
                )

    print(f"OK: Seeded {len(cases)} cases for {args.email}")


if __name__ == "__main__":
    main()
