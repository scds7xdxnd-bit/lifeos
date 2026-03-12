"""Schema guardrails for calendar view/ledger index migration."""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import inspect

from lifeos.domains.calendar.models.calendar_event import CalendarEvent
from lifeos.extensions import db


def test_calendar_event_has_normalized_date_columns(app):
    inspector = inspect(db.engine)
    columns = {col["name"] for col in inspector.get_columns("calendar_event")}
    assert "normalized_start_date" in columns
    assert "normalized_end_date" in columns


def test_calendar_event_indexes_for_view_and_ledger(app):
    inspector = inspect(db.engine)
    index_names = {idx["name"] for idx in inspector.get_indexes("calendar_event")}
    expected = {
        "ix_calendar_event_user_start_end",
        "ix_calendar_event_user_start_id",
        "ix_calendar_event_user_start_date",
        "ix_calendar_event_user_end_date",
    }
    assert expected.issubset(index_names)


def test_normalized_dates_persist_for_new_events(app):
    event = CalendarEvent(
        user_id=1,
        title="with normalized",
        start_time=datetime(2025, 1, 2, 9, 0),
        end_time=datetime(2025, 1, 2, 10, 0),
        normalized_start_date=datetime(2025, 1, 2).date(),
        normalized_end_date=datetime(2025, 1, 2).date(),
    )
    db.session.add(event)
    db.session.flush()

    row = db.session.execute(
        sa.text(
            """
            SELECT normalized_start_date, normalized_end_date
            FROM calendar_event WHERE id = :id
            """
        ),
        {"id": event.id},
    ).one()
    assert str(row.normalized_start_date) == "2025-01-02"
    assert str(row.normalized_end_date) == "2025-01-02"
