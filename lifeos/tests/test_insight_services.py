import pytest
from datetime import datetime, timedelta

pytestmark = [pytest.mark.integration, pytest.mark.ml]

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.services import (
    fetch_insights,
    persist_insights,
    recent_events,
)
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db


def _create_user(email: str = "insight-service@example.com"):
    return create_user(
        UserCreateRequest(
            email=email,
            password="changeme123",
            full_name="Insight Service User",
            timezone="UTC",
        )
    )


def _create_event(
    user,
    event_type: str = "finance.transaction.created",
    created_at: datetime | None = None,
):
    event = EventRecord(
        event_type=event_type,
        payload={"source": "tests"},
        user_id=user.id,
        created_at=created_at or datetime.utcnow(),
    )
    db.session.add(event)
    db.session.commit()
    return event


def test_persist_insights_saves_records_with_defaults(app):
    with app.app_context():
        user = _create_user()
        event = _create_event(user)

        insights = [
            {"message": "first insight"},
            {
                "type": "alert",
                "message": "second insight",
                "severity": "warning",
                "context": {"foo": "bar"},
            },
        ]

        saved = persist_insights(insights, event)

        assert len(saved) == 2
        first, second = saved
        assert first.user_id == user.id
        assert first.event_id == event.id
        assert first.event_type == event.event_type
        assert first.kind == "generic"
        assert first.severity == "info"
        assert first.message == "first insight"
        assert first.data == {}
        assert second.kind == "alert"
        assert second.severity == "warning"
        assert second.data == {"foo": "bar"}
        assert InsightRecord.query.filter_by(user_id=user.id).count() == 2


def test_persist_insights_skips_commit_when_no_insights(app, monkeypatch):
    with app.app_context():
        user = _create_user(email="no-insights@example.com")
        event = _create_event(user)

        commit_called = False

        def _fake_commit():
            nonlocal commit_called
            commit_called = True

        monkeypatch.setattr(db.session, "commit", _fake_commit)

        saved = persist_insights([], event)

        assert saved == []
        assert commit_called is False
        assert InsightRecord.query.count() == 0


def test_recent_events_filters_by_user_type_and_time_window(app):
    with app.app_context():
        user = _create_user(email="recent@example.com")
        other_user = _create_user(email="other@example.com")
        now = datetime.utcnow()

        matching_recent = EventRecord(
            event_type="finance.transaction.created",
            payload={"amount": 100},
            user_id=user.id,
            created_at=now - timedelta(days=1),
        )
        matching_latest = EventRecord(
            event_type="finance.transaction.created",
            payload={"amount": 50},
            user_id=user.id,
            created_at=now - timedelta(hours=1),
        )
        matching_old = EventRecord(
            event_type="finance.transaction.created",
            payload={"amount": 200},
            user_id=user.id,
            created_at=now - timedelta(days=30),
        )
        other_type = EventRecord(
            event_type="health.metric.updated",
            payload={"metric": "sleep_hours"},
            user_id=user.id,
            created_at=now - timedelta(days=2),
        )
        other_user_event = EventRecord(
            event_type="finance.transaction.created",
            payload={"amount": 75},
            user_id=other_user.id,
            created_at=now - timedelta(days=1),
        )
        db.session.add_all(
            [
                matching_recent,
                matching_latest,
                matching_old,
                other_type,
                other_user_event,
            ]
        )
        db.session.commit()

        results = recent_events(user.id, ["finance.transaction.created"], days=7, limit=5)

        assert [evt.id for evt in results] == [matching_latest.id, matching_recent.id]


def test_fetch_insights_orders_most_recent_first(app):
    with app.app_context():
        user = _create_user(email="fetch@example.com")
        event = _create_event(user)
        older = InsightRecord(
            user_id=user.id,
            event_id=event.id,
            event_type=event.event_type,
            kind="generic",
            message="older",
            severity="info",
            data={},
            created_at=datetime.utcnow() - timedelta(hours=2),
        )
        newer = InsightRecord(
            user_id=user.id,
            event_id=event.id,
            event_type=event.event_type,
            kind="generic",
            message="newer",
            severity="info",
            data={},
            created_at=datetime.utcnow() - timedelta(hours=1),
        )
        db.session.add_all([older, newer])
        db.session.commit()

        results = fetch_insights(user.id, limit=1)

        assert len(results) == 1
        assert results[0].id == newer.id
