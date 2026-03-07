"""API tests for deterministic calendar day/week/month views and ledger."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest
from flask_jwt_extended import create_access_token

from lifeos.domains.calendar.models.calendar_event import CalendarEvent
from lifeos.extensions import db


pytestmark = pytest.mark.unit


def _auth_header(user_id: int) -> dict[str, str]:
    token = create_access_token(identity=str(user_id), additional_claims={"roles": ["calendar:read"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def calendar_user(app):
    with app.app_context():
        user_email = f"calendar-view-{uuid4().hex}@example.com"
        user = db.session.execute(
            db.text("INSERT INTO user (email, password_hash) VALUES (:email, :pw) RETURNING id"),
            {"email": user_email, "pw": "test"},
        ).scalar_one()
        return user


def _create_event(user_id: int, start: datetime, end: datetime | None = None, title: str = "event"):
    event = CalendarEvent(
        user_id=user_id,
        title=title,
        start_time=start,
        end_time=end,
        source="manual",
    )
    db.session.add(event)
    db.session.flush()
    return event


def test_day_view_returns_overlapping_events(client, calendar_user):
    target = date(2025, 3, 15)
    late_previous = datetime(2025, 3, 14, 23, 0)
    early_next = datetime(2025, 3, 15, 8, 0)
    _create_event(calendar_user, start=late_previous, end=early_next, title="overnight")
    _create_event(calendar_user, start=datetime(2025, 3, 16, 9, 0), end=datetime(2025, 3, 16, 10, 0), title="out")

    resp = client.get(
        "/api/v1/calendar/day",
        query_string={"date": target.isoformat()},
        headers=_auth_header(calendar_user),
    )
    payload = resp.get_json()

    assert resp.status_code == 200
    assert payload["ok"] is True
    assert payload["window_start"].startswith("2025-03-15T00:00:00")
    assert payload["window_end"].startswith("2025-03-16T00:00:00")
    assert len(payload["events"]) == 1
    assert payload["events"][0]["title"] == "overnight"


def test_week_view_respects_start_and_overlap(client, calendar_user):
    week_start = date(2025, 3, 10)  # Monday
    _create_event(calendar_user, start=datetime(2025, 3, 11, 9, 0), end=datetime(2025, 3, 11, 10, 0), title="inside")
    _create_event(calendar_user, start=datetime(2025, 3, 17, 12, 0), end=datetime(2025, 3, 17, 13, 0), title="outside")

    resp = client.get(
        "/api/v1/calendar/week",
        query_string={"start": week_start.isoformat()},
        headers=_auth_header(calendar_user),
    )
    payload = resp.get_json()

    assert resp.status_code == 200
    assert payload["ok"] is True
    assert payload["window_start"].startswith("2025-03-10T00:00:00")
    assert payload["window_end"].startswith("2025-03-17T00:00:00")
    titles = [e["title"] for e in payload["events"]]
    assert titles == ["inside"]


def test_month_view_includes_spillover_and_overlap(client, calendar_user):
    # January 2025 grid spans 2024-12-30 to 2025-02-02
    _create_event(
        calendar_user, start=datetime(2024, 12, 31, 18, 0), end=datetime(2024, 12, 31, 19, 0), title="dec spill"
    )
    _create_event(calendar_user, start=datetime(2025, 2, 1, 9, 0), end=datetime(2025, 2, 1, 10, 0), title="feb spill")
    _create_event(calendar_user, start=datetime(2025, 1, 15, 9, 0), end=datetime(2025, 1, 15, 10, 0), title="midmonth")

    resp = client.get(
        "/api/v1/calendar/month",
        query_string={"year": 2025, "month": 1},
        headers=_auth_header(calendar_user),
    )
    payload = resp.get_json()

    assert resp.status_code == 200
    assert payload["ok"] is True
    assert payload["window_start"].startswith("2024-12-30T00:00:00")
    assert payload["window_end"].startswith("2025-02-03T00:00:00")
    spill = set(payload["spillover_days"])
    assert {"2024-12-30", "2024-12-31", "2025-02-01", "2025-02-02"}.issubset(spill)
    titles = [e["title"] for e in payload["events"]]
    assert set(titles) == {"dec spill", "feb spill", "midmonth"}


def test_ledger_backward_orders_events_and_returns_cursors(client, calendar_user):
    anchor = date(2025, 3, 20)
    # Events before and on anchor
    older = _create_event(
        calendar_user, start=datetime(2025, 3, 18, 9, 0), end=datetime(2025, 3, 18, 10, 0), title="older"
    )
    middle = _create_event(
        calendar_user, start=datetime(2025, 3, 19, 9, 0), end=datetime(2025, 3, 19, 10, 0), title="middle"
    )
    newest = _create_event(
        calendar_user, start=datetime(2025, 3, 20, 8, 0), end=datetime(2025, 3, 20, 9, 0), title="anchor-day"
    )
    # Event after anchor should not appear in backward scan
    _create_event(calendar_user, start=datetime(2025, 3, 21, 9, 0), end=datetime(2025, 3, 21, 10, 0), title="future")

    resp = client.get(
        "/api/v1/calendar/ledger",
        query_string={"anchor": anchor.isoformat(), "limit": 3, "direction": "backward"},
        headers=_auth_header(calendar_user),
    )
    payload = resp.get_json()

    assert resp.status_code == 200
    assert payload["ok"] is True
    titles = [e["title"] for e in payload["events"]]
    assert titles == ["older", "middle", "anchor-day"]
    assert payload["cursor"] is None
    assert payload["next_cursor"] is not None
    assert payload["prev_cursor"] is not None
    # Paging forward from prev_cursor should return only the future event
    fwd = client.get(
        "/api/v1/calendar/ledger",
        query_string={"cursor": payload["prev_cursor"], "direction": "forward", "limit": 2},
        headers=_auth_header(calendar_user),
    ).get_json()
    fwd_titles = [e["title"] for e in fwd["events"]]
    assert fwd_titles == ["future"]


@pytest.mark.xfail(reason="Month view returns 500 on validation error (ValueError serialization); should be 400.")
def test_invalid_month_returns_400(client, calendar_user):
    resp = client.get(
        "/api/v1/calendar/month",
        query_string={"year": 2025, "month": 13},
        headers=_auth_header(calendar_user),
    )
    assert resp.status_code == 400
    payload = resp.get_json()
    assert payload["ok"] is False
