import pytest
from datetime import datetime, timedelta

pytestmark = pytest.mark.unit

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.services import (
    fetch_insights,
    list_insights_feed,
    persist_insights,
    recent_events,
)
from lifeos.core.insights.schemas import InsightsFeedQuery
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
                "priority": 80,
                "delivery_policy": "inbox",
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
        assert first.priority == 50
        assert first.delivery_policy == "feed"
        assert first.message == "first insight"
        assert first.data == {"confidence_band": "informational", "routing": "display"}
        assert second.kind == "alert"
        assert second.severity == "warning"
        assert second.priority == 80
        assert second.delivery_policy == "inbox"
        assert second.data == {
            "foo": "bar",
            "confidence_band": "informational",
            "routing": "display",
        }
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


def test_persist_insights_bumps_read_cache_scope(app, monkeypatch):
    with app.app_context():
        user = _create_user(email="cache-bump@example.com")
        event = _create_event(user)
        bumps: list[tuple[str, int | None]] = []

        monkeypatch.setattr(
            "lifeos.core.insights.services.read_cache.bump",
            lambda scope, uid: bumps.append((scope, uid)),
        )

        saved = persist_insights([{"message": "cache me"}], event)

        assert len(saved) == 1
        assert bumps == [("insights.reads", user.id)]


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


def test_list_insights_feed_applies_ranker_on_default_path(app, monkeypatch):
    with app.app_context():
        user = _create_user(email="feed-rank@example.com")
        event = _create_event(user)
        db.session.add(
            InsightRecord(
                user_id=user.id,
                event_id=event.id,
                event_type=event.event_type,
                kind="generic",
                message="rank me",
                severity="info",
                data={},
                created_at=datetime.utcnow(),
            )
        )
        db.session.commit()

        called = {"value": False}

        def _rank(uid, items, context=None):
            called["value"] = True
            return items

        monkeypatch.setattr("lifeos.core.insights.services.rank_insights", _rank)

        items, total, page, pages = list_insights_feed(
            user.id,
            InsightsFeedQuery(page=1, per_page=20),
        )

        assert called["value"] is True
        assert total == 1
        assert page == 1
        assert pages == 1
        assert len(items) == 1


def test_list_insights_feed_status_filter_path_applies_ranker(app, monkeypatch):
    with app.app_context():
        user = _create_user(email="feed-status@example.com")
        event = _create_event(user)
        db.session.add(
            InsightRecord(
                user_id=user.id,
                event_id=event.id,
                event_type=event.event_type,
                kind="generic",
                message="status record",
                severity="info",
                data={"status": "confirmed"},
                created_at=datetime.utcnow(),
            )
        )
        db.session.commit()

        called = {"value": False}

        def _rank(uid, items, context=None):
            called["value"] = True
            return items

        monkeypatch.setattr("lifeos.core.insights.services.rank_insights", _rank)

        items, total, page, pages = list_insights_feed(
            user.id,
            InsightsFeedQuery(page=1, per_page=10, status="confirmed"),
        )

        assert called["value"] is True
        assert total == 1
        assert page == 1
        assert pages == 1
        assert len(items) == 1


def test_list_insights_feed_status_filter_ignores_non_dict_data(app):
    with app.app_context():
        user = _create_user(email="feed-status-nondict@example.com")
        event = _create_event(user)
        now = datetime.utcnow()
        db.session.add_all(
            [
                InsightRecord(
                    user_id=user.id,
                    event_id=event.id,
                    event_type=event.event_type,
                    kind="good",
                    message="dict status",
                    severity="info",
                    data={"status": "confirmed"},
                    created_at=now,
                ),
                InsightRecord(
                    user_id=user.id,
                    event_id=event.id,
                    event_type=event.event_type,
                    kind="bad-shape",
                    message="list status",
                    severity="info",
                    data=["not", "a", "dict"],
                    created_at=now - timedelta(seconds=1),
                ),
            ]
        )
        db.session.commit()

        items, total, page, pages = list_insights_feed(
            user.id,
            InsightsFeedQuery(page=1, per_page=10, status="confirmed"),
        )

        assert total == 1
        assert page == 1
        assert pages == 1
        assert len(items) == 1
        assert items[0].kind == "good"


def test_list_insights_feed_orders_by_priority_then_confidence_then_time(app):
    with app.app_context():
        user = _create_user(email="feed-priority-order@example.com")
        event = _create_event(user)
        now = datetime.utcnow()
        low_priority = InsightRecord(
            user_id=user.id,
            event_id=event.id,
            event_type=event.event_type,
            kind="low",
            message="low priority",
            severity="info",
            priority=20,
            confidence_band="needs_review",
            data={},
            created_at=now,
        )
        high_priority_null_conf = InsightRecord(
            user_id=user.id,
            event_id=event.id,
            event_type=event.event_type,
            kind="high-null",
            message="high null confidence",
            severity="info",
            priority=90,
            confidence_band=None,
            data={},
            created_at=now - timedelta(minutes=1),
        )
        high_priority_with_conf = InsightRecord(
            user_id=user.id,
            event_id=event.id,
            event_type=event.event_type,
            kind="high-conf",
            message="high with confidence",
            severity="info",
            priority=90,
            confidence_band="needs_review",
            data={},
            created_at=now - timedelta(minutes=2),
        )
        db.session.add_all([low_priority, high_priority_null_conf, high_priority_with_conf])
        db.session.commit()

        items, total, page, pages = list_insights_feed(
            user.id,
            InsightsFeedQuery(page=1, per_page=10),
        )

        assert total == 3
        assert page == 1
        assert pages == 1
        assert [item.kind for item in items] == ["high-conf", "high-null", "low"]


def test_list_insights_feed_applies_domain_severity_and_date_filters(app):
    with app.app_context():
        user = _create_user(email="feed-filter-coverage@example.com")
        now = datetime.utcnow()
        in_window = EventRecord(
            event_type="projects.task.completed",
            payload={"task": "ship"},
            user_id=user.id,
            created_at=now - timedelta(hours=2),
        )
        wrong_domain = EventRecord(
            event_type="finance.transaction.created",
            payload={"amount": 99},
            user_id=user.id,
            created_at=now - timedelta(hours=2),
        )
        out_of_window = EventRecord(
            event_type="projects.task.completed",
            payload={"task": "stale"},
            user_id=user.id,
            created_at=now - timedelta(days=14),
        )
        db.session.add_all([in_window, wrong_domain, out_of_window])
        db.session.flush()
        db.session.add_all(
            [
                InsightRecord(
                    user_id=user.id,
                    event_id=in_window.id,
                    event_type=in_window.event_type,
                    kind="match",
                    message="target",
                    severity="warning",
                    priority=50,
                    data={},
                    created_at=in_window.created_at,
                ),
                InsightRecord(
                    user_id=user.id,
                    event_id=wrong_domain.id,
                    event_type=wrong_domain.event_type,
                    kind="domain-miss",
                    message="domain miss",
                    severity="warning",
                    priority=50,
                    data={},
                    created_at=wrong_domain.created_at,
                ),
                InsightRecord(
                    user_id=user.id,
                    event_id=out_of_window.id,
                    event_type=out_of_window.event_type,
                    kind="date-miss",
                    message="date miss",
                    severity="warning",
                    priority=50,
                    data={},
                    created_at=out_of_window.created_at,
                ),
                InsightRecord(
                    user_id=user.id,
                    event_id=in_window.id,
                    event_type=in_window.event_type,
                    kind="severity-miss",
                    message="severity miss",
                    severity="info",
                    priority=50,
                    data={},
                    created_at=in_window.created_at,
                ),
            ]
        )
        db.session.commit()

        items, total, page, pages = list_insights_feed(
            user.id,
            InsightsFeedQuery(
                page=1,
                per_page=10,
                domain="projects",
                severity="warning",
                start_date=(now - timedelta(days=1)).date(),
                end_date=now.date(),
            ),
        )

        assert total == 1
        assert page == 1
        assert pages == 1
        assert len(items) == 1
        assert items[0].kind == "match"
