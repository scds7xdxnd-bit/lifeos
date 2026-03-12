"""Phase 5b feature service tests."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.feature_models import FeatureDaily
from lifeos.core.insights.feature_service import (
    compute_features_for_user,
    extract_event_features,
    resolve_event_date,
    store_features_daily,
)
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.calendar.events import CALENDAR_EVENT_CREATED
from lifeos.domains.finance.events import FINANCE_TRANSACTION_CREATED
from lifeos.domains.habits.events import HABITS_HABIT_LOGGED
from lifeos.domains.health.events import HEALTH_METRIC_UPDATED
from lifeos.domains.journal.events import JOURNAL_ENTRY_CREATED
from lifeos.extensions import db


@pytest.mark.unit
def test_extract_event_features_calendar_obligation_and_late_night():
    event = EventRecord(
        event_type=CALENDAR_EVENT_CREATED,
        payload={
            "title": "Rent payment",
            "start_time": "2025-01-10T22:30:00",
        },
    )

    features = extract_event_features(event)

    assert features["calendar.event.count"] == 1.0
    assert features["calendar.obligation.count"] == 1.0
    assert features["calendar.event.late_night.count"] == 1.0


@pytest.mark.unit
def test_extract_event_features_finance_spend_negative_only():
    negative = EventRecord(
        event_type=FINANCE_TRANSACTION_CREATED,
        payload={"amount": -120.5},
    )
    positive = EventRecord(
        event_type=FINANCE_TRANSACTION_CREATED,
        payload={"amount": 150.0},
    )

    neg_features = extract_event_features(negative)
    pos_features = extract_event_features(positive)

    assert neg_features["finance.transaction.count"] == 1.0
    assert neg_features["finance.spend.total"] == 120.5
    assert pos_features["finance.transaction.count"] == 1.0
    assert "finance.spend.total" not in pos_features


@pytest.mark.unit
def test_extract_event_features_journal_stress_tags():
    event = EventRecord(
        event_type=JOURNAL_ENTRY_CREATED,
        payload={"mood": "stressed", "tags": ["work", "stress"]},
    )

    features = extract_event_features(event)

    assert features["journal.entry.count"] == 1.0
    assert features["journal.stress.count"] == 1.0


@pytest.mark.unit
def test_extract_event_features_health_sleep_low():
    event = EventRecord(
        event_type=HEALTH_METRIC_UPDATED,
        payload={"metric": "sleep_hours", "value": 5.5},
    )

    features = extract_event_features(event)

    assert features["health.sleep_low.count"] == 1.0


@pytest.mark.unit
def test_resolve_event_date_from_payload():
    event = EventRecord(
        event_type=CALENDAR_EVENT_CREATED,
        payload={"start_time": "2025-01-10T09:00:00"},
    )

    assert resolve_event_date(event) == date(2025, 1, 10)


@pytest.mark.unit
def test_store_features_daily_upserts(app):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="phase5b-features@example.com",
                password="secret123",
                full_name="Phase 5b Features",
                timezone="UTC",
            )
        )
        feature_date = date(2025, 1, 10)
        store_features_daily(
            user.id,
            {feature_date: {"calendar.event.count": 2.0}},
        )
        store_features_daily(
            user.id,
            {feature_date: {"calendar.event.count": 3.5}},
        )

        rows = FeatureDaily.query.filter_by(
            user_id=user.id,
            feature_date=feature_date,
            feature_key="calendar.event.count",
        ).all()
        assert len(rows) == 1
        assert float(rows[0].feature_value) == 3.5


@pytest.mark.unit
def test_compute_features_for_user_window_filters_dates(app):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="phase5b-window@example.com",
                password="secret123",
                full_name="Phase 5b Window",
                timezone="UTC",
            )
        )
        inside = EventRecord(
            event_type=FINANCE_TRANSACTION_CREATED,
            payload={"amount": -200.0, "occurred_at": "2025-01-08T12:00:00"},
            user_id=user.id,
            created_at=datetime(2025, 1, 8, 12, 0, 0),
        )
        outside = EventRecord(
            event_type=FINANCE_TRANSACTION_CREATED,
            payload={"amount": -99.0, "occurred_at": "2024-12-01T12:00:00"},
            user_id=user.id,
            created_at=datetime(2024, 12, 1, 12, 0, 0),
        )
        extra = EventRecord(
            event_type=HABITS_HABIT_LOGGED,
            payload={"logged_date": "2025-01-08"},
            user_id=user.id,
            created_at=datetime(2025, 1, 8, 9, 0, 0),
        )
        db.session.add_all([inside, outside, extra])
        db.session.commit()

        features = compute_features_for_user(user.id, date(2025, 1, 1), date(2025, 1, 10))

        assert date(2025, 1, 8) in features
        assert date(2024, 12, 1) not in features
        assert features[date(2025, 1, 8)]["finance.transaction.count"] == 1.0
        assert features[date(2025, 1, 8)]["finance.spend.total"] == 200.0
        assert features[date(2025, 1, 8)]["habits.log.count"] == 1.0
