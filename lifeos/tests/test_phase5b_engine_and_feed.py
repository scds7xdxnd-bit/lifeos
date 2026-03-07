from __future__ import annotations

from datetime import datetime, timedelta

import pytest

import lifeos.core.insights.engine as engine_module
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.schemas import InsightsFeedQuery
from lifeos.core.insights.services import list_insights_feed
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _create_user(email: str):
    return create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 5b Engine",
            timezone="UTC",
        )
    )


def test_insights_engine_subscribes_expected_event_types(monkeypatch):
    subscribed: list[str] = []

    def _subscribe(event_type, _handler):
        subscribed.append(event_type)

    monkeypatch.setattr(engine_module.event_bus, "subscribe", _subscribe)
    engine_module.InsightsEngine()

    assert set(
        [
            "calendar.event.created",
            "finance.transaction.created",
            "finance.journal.posted",
            "journal.entry.created",
            "habits.habit.logged",
            "health.metric.updated",
            "relationships.interaction.logged",
            "skills.practice.logged",
            "projects.task.completed",
        ]
    ).issubset(set(subscribed))


def test_insights_engine_ingest_event_persists_when_rules_emit(monkeypatch):
    event = EventRecord(event_type="calendar.event.created", payload={"event_id": "c1"}, user_id=1)
    monkeypatch.setattr(engine_module.event_bus, "subscribe", lambda *_args, **_kwargs: None)

    monkeypatch.setattr(
        engine_module,
        "RULES",
        [
            ("rule_a", lambda _event: [{"type": "x", "context": {"is_false_positive": True}}]),
            ("rule_b", lambda _event: []),
        ],
    )

    persisted: dict[str, object] = {}
    rule_calls: list[tuple[str, int, int, int]] = []
    event_calls: list[tuple[str, bool]] = []

    monkeypatch.setattr(
        engine_module,
        "persist_insights",
        lambda insights, evt: persisted.update({"insights": insights, "event_type": evt.event_type}),
    )
    monkeypatch.setattr(
        engine_module.insight_telemetry,
        "record_rule",
        lambda name, count, _latency, fp, fn: rule_calls.append((name, count, fp, fn)),
    )
    monkeypatch.setattr(
        engine_module.insight_telemetry,
        "record_event",
        lambda event_type, has_insights, _latency: event_calls.append((event_type, has_insights)),
    )

    engine = engine_module.InsightsEngine()
    insights = engine.ingest_event(event)

    assert len(insights) == 1
    assert persisted["event_type"] == "calendar.event.created"
    assert rule_calls[0] == ("rule_a", 1, 1, 0)
    assert event_calls[0] == ("calendar.event.created", True)


def test_list_insights_feed_orders_by_priority_and_filters_status(app):
    with app.app_context():
        user = _create_user("phase5b-feed-order@example.com")
        source_event = EventRecord(
            event_type="calendar.event.created",
            payload={"event_id": "c1"},
            user_id=user.id,
            created_at=datetime.utcnow(),
        )
        db.session.add(source_event)
        db.session.flush()

        old = InsightRecord(
            user_id=user.id,
            event_id=source_event.id,
            event_type=source_event.event_type,
            kind="a",
            message="old",
            severity="info",
            priority=50,
            delivery_policy="feed",
            confidence_band="informational",
            data={"status": "confirmed"},
            created_at=datetime.utcnow() - timedelta(hours=1),
        )
        high = InsightRecord(
            user_id=user.id,
            event_id=source_event.id,
            event_type=source_event.event_type,
            kind="b",
            message="high",
            severity="info",
            priority=90,
            delivery_policy="feed",
            confidence_band="informational",
            data={"status": "confirmed"},
            created_at=datetime.utcnow() - timedelta(hours=2),
        )
        rejected = InsightRecord(
            user_id=user.id,
            event_id=source_event.id,
            event_type=source_event.event_type,
            kind="c",
            message="rejected",
            severity="info",
            priority=99,
            delivery_policy="feed",
            confidence_band="informational",
            data={"status": "rejected"},
            created_at=datetime.utcnow() - timedelta(hours=3),
        )
        db.session.add_all([old, high, rejected])
        db.session.commit()

        items, total, _page, _pages = list_insights_feed(
            user.id,
            InsightsFeedQuery.model_validate({"status": "confirmed", "per_page": 20}),
        )

        assert total == 2
        assert [row.message for row in items] == ["high", "old"]
