from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from flask_jwt_extended import create_access_token

from lifeos.core.insights.substrate_models import Interpretation, TimelineEvent
from lifeos.core.read_cache import read_cache
from lifeos.core.users.models import User
from lifeos.core.interpreter.calendar_interpreter import CalendarInterpreter, CALENDAR_READ_CACHE_SCOPE
from lifeos.domains.calendar import tasks as calendar_tasks
from lifeos.domains.calendar.models.calendar_event import CalendarEvent, CalendarEventInterpretation
from lifeos.domains.calendar.models.oauth_token import CalendarOAuthToken
from lifeos.domains.calendar.services import apple_sync_service, calendar_service, google_sync_service
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox.models import OutboxMessage
from lifeos.lifeos_platform.outbox.services import EventBusAdapter


pytestmark = pytest.mark.unit


def _auth_headers(app, user_id: int, roles: list[str] | None = None) -> dict[str, str]:
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"roles": roles or []})
    return {"Authorization": f"Bearer {token}"}


def _ensure_user(email: str) -> User:
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(email=email, password_hash="test")
    db.session.add(user)
    db.session.commit()
    return user


def test_ensure_user_returns_existing_user(app):
    with app.app_context():
        first = _ensure_user("ensure-user-existing@example.com")
        second = _ensure_user("ensure-user-existing@example.com")
        assert second.id == first.id


def test_admin_debug_timeline_events_invalid_limit_returns_400(app, client):
    with app.app_context():
        user = _ensure_user("admin-debug-limit@example.com")
    headers = _auth_headers(app, user.id, roles=["admin"])
    resp = client.get("/admin/debug/timeline-events?limit=not-an-int", headers=headers)
    assert resp.status_code == 400
    assert resp.get_json() == {"ok": False, "error": "validation_error"}


def test_admin_debug_interpretations_invalid_limit_returns_400(app, client):
    with app.app_context():
        user = _ensure_user("admin-debug-interpretation-limit@example.com")
    headers = _auth_headers(app, user.id, roles=["admin"])
    resp = client.get("/admin/debug/interpretations?limit=oops", headers=headers)
    assert resp.status_code == 400
    assert resp.get_json() == {"ok": False, "error": "validation_error"}


def test_admin_debug_timeline_and_interpretations_return_rows(app, client):
    with app.app_context():
        admin_user = _ensure_user("admin-debug@example.com")
        target_user = _ensure_user("admin-debug-target@example.com")

        event = TimelineEvent(
            event_id="evt-debug-1",
            user_id=target_user.id,
            timestamp_start=datetime.utcnow(),
            source_domain="calendar",
            event_type="calendar.event.created",
            source_object_ref="calendar_event:1",
            raw_payload={"source": "test"},
        )
        db.session.add(event)
        db.session.flush()
        db.session.add(
            Interpretation(
                user_id=target_user.id,
                interpretation_type="calendar_transaction_candidate",
                input_event_ids=[event.event_id],
                proposed_writes=[],
                confidence=0.61,
                evidence="test evidence",
                fingerprint="fp-admin-debug-1",
            )
        )
        db.session.commit()

    headers = _auth_headers(app, admin_user.id, roles=["admin"])
    timeline = client.get(
        f"/admin/debug/timeline-events?user_id={target_user.id}&limit=10&offset=0",
        headers=headers,
    )
    assert timeline.status_code == 200
    timeline_body = timeline.get_json()
    assert timeline_body["ok"] is True
    assert timeline_body["items"]
    assert timeline_body["items"][0]["event_id"] == "evt-debug-1"

    interpretations = client.get(
        f"/admin/debug/interpretations?user_id={target_user.id}&limit=10&offset=0",
        headers=headers,
    )
    assert interpretations.status_code == 200
    interp_body = interpretations.get_json()
    assert interp_body["ok"] is True
    assert interp_body["items"]
    assert interp_body["items"][0]["interpretation_type"] == "calendar_transaction_candidate"


def test_insights_feed_uses_cache_hit(app, client, monkeypatch):
    from lifeos.core.insights import api_v1 as insights_api

    with app.app_context():
        user = _ensure_user("insights-feed-cache-hit@example.com")
    headers = _auth_headers(app, user.id, roles=["insights:read"])
    cached_payload = {"ok": True, "page": 1, "per_page": 20, "total": 0, "pages": 0, "items": []}

    monkeypatch.setattr(insights_api.read_cache, "get", lambda scope, uid, key: cached_payload)

    def _should_not_run(*args, **kwargs):
        raise AssertionError("list_insights_feed should not run on cache hit")  # pragma: no cover

    monkeypatch.setattr(insights_api, "list_insights_feed", _should_not_run)

    resp = client.get("/api/v1/insights/feed", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json() == cached_payload


def test_insights_feed_sets_cache_on_miss(app, client, monkeypatch):
    from lifeos.core.insights import api_v1 as insights_api

    with app.app_context():
        user = _ensure_user("insights-feed-cache-miss@example.com")
    headers = _auth_headers(app, user.id, roles=["insights:read"])

    captured: dict[str, object] = {}

    monkeypatch.setattr(insights_api.read_cache, "get", lambda scope, uid, key: None)

    def _capture_set(scope, uid, key, value, ttl=None):
        captured["scope"] = scope
        captured["uid"] = uid
        captured["value"] = value

    monkeypatch.setattr(insights_api.read_cache, "set", _capture_set)
    monkeypatch.setattr(insights_api, "list_insights_feed", lambda uid, filters: ([], 0, filters.page, 0))

    resp = client.get("/api/v1/insights/feed?page=2&per_page=5", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["page"] == 2
    assert captured["scope"] == insights_api.INSIGHTS_READ_CACHE_SCOPE
    assert captured["uid"] == user.id


def test_insights_review_queue_uses_cache_hit(app, client, monkeypatch):
    from lifeos.core.insights import api_v1 as insights_api

    with app.app_context():
        user = _ensure_user("insights-review-cache-hit@example.com")
    headers = _auth_headers(app, user.id, roles=["insights:read"])
    cached_payload = {"ok": True, "items": [{"id": 1}], "limit": 10, "offset": 0}

    monkeypatch.setattr(insights_api.read_cache, "get", lambda scope, uid, key: cached_payload)
    monkeypatch.setattr(
        insights_api,
        "fetch_review_queue_projection",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not query projection on cache hit")),
    )

    resp = client.get("/api/v1/insights/review?limit=10&offset=0", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json() == cached_payload


def test_insights_review_queue_sets_cache_on_miss(app, client, monkeypatch):
    from lifeos.core.insights import api_v1 as insights_api

    with app.app_context():
        user = _ensure_user("insights-review-cache-miss@example.com")
    headers = _auth_headers(app, user.id, roles=["insights:read"])

    captured: dict[str, object] = {}

    monkeypatch.setattr(insights_api.read_cache, "get", lambda scope, uid, key: None)

    def _capture_set(scope, uid, key, value, ttl=None):
        captured["scope"] = scope
        captured["uid"] = uid
        captured["value"] = value

    monkeypatch.setattr(insights_api.read_cache, "set", _capture_set)
    monkeypatch.setattr(insights_api, "fetch_review_queue_projection", lambda uid, limit, offset: [])

    resp = client.get("/api/v1/insights/review?limit=5&offset=2", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True, "items": [], "limit": 5, "offset": 2}
    assert captured["scope"] == insights_api.INSIGHTS_READ_CACHE_SCOPE
    assert captured["uid"] == user.id


def test_cleanup_old_interpretations_bumps_cache_per_user(app, monkeypatch):
    with app.app_context():
        user_a = _ensure_user("cleanup-user-a@example.com")
        user_b = _ensure_user("cleanup-user-b@example.com")
        old_ts = datetime.utcnow() - timedelta(days=120)

        ev_a = CalendarEvent(
            user_id=user_a.id,
            title="a",
            start_time=datetime.utcnow(),
            source="manual",
        )
        ev_b = CalendarEvent(
            user_id=user_b.id,
            title="b",
            start_time=datetime.utcnow(),
            source="manual",
        )
        db.session.add_all([ev_a, ev_b])
        db.session.flush()

        db.session.add_all(
            [
                CalendarEventInterpretation(
                    calendar_event_id=ev_a.id,
                    user_id=user_a.id,
                    domain="finance",
                    record_type="transaction",
                    confidence_score=0.5,
                    status="rejected",
                    created_at=old_ts,
                    updated_at=old_ts,
                    classification_data={},
                ),
                CalendarEventInterpretation(
                    calendar_event_id=ev_b.id,
                    user_id=user_b.id,
                    domain="health",
                    record_type="workout",
                    confidence_score=0.5,
                    status="ignored",
                    created_at=old_ts,
                    updated_at=old_ts,
                    classification_data={},
                ),
            ]
        )
        db.session.commit()

        bumps: list[tuple[str, int]] = []
        monkeypatch.setattr(read_cache, "bump", lambda scope, uid: bumps.append((scope, uid)))

        deleted = calendar_tasks.cleanup_old_interpretations(days=90)
        assert deleted == 2
        assert ("calendar.views", user_a.id) in bumps
        assert ("calendar.views", user_b.id) in bumps


def test_sync_apple_calendar_bumps_cache_when_events_updated(app, monkeypatch):
    with app.app_context():
        user = _ensure_user("apple-sync-cache@example.com")
        db.session.add(
            CalendarOAuthToken(
                user_id=user.id,
                provider="apple",
                access_token="app-password",
                refresh_token="apple-id@example.com",
                is_active=True,
            )
        )
        db.session.add(
            CalendarEvent(
                user_id=user.id,
                title="existing",
                start_time=datetime.utcnow(),
                source="sync_apple",
                external_id="ext-apple-1",
            )
        )
        db.session.commit()

        monkeypatch.setattr(apple_sync_service, "get_calendars", lambda *_: [{"href": "/cal", "color": "#fff"}])
        monkeypatch.setattr(
            apple_sync_service,
            "fetch_calendar_events",
            lambda *_: [
                {
                    "external_id": "ext-apple-1",
                    "title": "updated title",
                    "description": "updated",
                    "location": "office",
                    "start_time": datetime.utcnow(),
                    "end_time": None,
                    "all_day": False,
                }
            ],
        )
        bumps: list[tuple[str, int]] = []
        monkeypatch.setattr(
            apple_sync_service.read_cache,
            "bump",
            lambda scope, uid: bumps.append((scope, uid)),
        )

        stats = apple_sync_service.sync_apple_calendar(user.id)
        assert stats["updated"] == 1
        assert bumps == [(apple_sync_service.CALENDAR_READ_CACHE_SCOPE, user.id)]


def test_sync_google_calendar_bumps_cache_when_events_deleted(app, monkeypatch):
    with app.app_context():
        user = _ensure_user("google-sync-cache@example.com")
        db.session.add(
            CalendarOAuthToken(
                user_id=user.id,
                provider="google",
                access_token="token",
                refresh_token="refresh",
                is_active=True,
            )
        )
        db.session.add(
            CalendarEvent(
                user_id=user.id,
                title="existing google",
                start_time=datetime.utcnow(),
                source="sync_google",
                external_id="ext-google-1",
            )
        )
        db.session.commit()

        monkeypatch.setattr(
            google_sync_service,
            "get_valid_token",
            lambda uid: CalendarOAuthToken.query.filter_by(user_id=uid, provider="google").first(),
        )
        monkeypatch.setattr(
            google_sync_service,
            "fetch_google_events",
            lambda *_: ([{"id": "ext-google-1", "status": "cancelled"}], "next-sync"),
        )
        bumps: list[tuple[str, int]] = []
        monkeypatch.setattr(
            google_sync_service.read_cache,
            "bump",
            lambda scope, uid: bumps.append((scope, uid)),
        )

        stats = google_sync_service.sync_google_calendar(user.id)
        assert stats["deleted"] == 1
        assert bumps == [(google_sync_service.CALENDAR_READ_CACHE_SCOPE, user.id)]


def test_calendar_interpreter_bumps_read_cache(app, monkeypatch):
    from importlib import import_module

    calendar_interpreter_module = import_module("lifeos.core.interpreter.calendar_interpreter")

    with app.app_context():
        user = _ensure_user("calendar-interpreter-cache@example.com")
        event = CalendarEvent(
            user_id=user.id,
            title="Pay rent",
            start_time=datetime.utcnow(),
            source="manual",
        )
        db.session.add(event)
        db.session.commit()

        interpreter = CalendarInterpreter()
        monkeypatch.setattr(
            calendar_interpreter_module,
            "classify_event",
            lambda **kwargs: [
                {
                    "domain": "finance",
                    "record_type": "transaction",
                    "confidence_score": 0.95,
                    "extracted_data": {"amount": 123},
                }
            ],
        )
        monkeypatch.setattr(
            interpreter,
            "_create_interpretation",
            lambda **kwargs: CalendarEventInterpretation(
                calendar_event_id=event.id,
                user_id=user.id,
                domain="finance",
                record_type="transaction",
                confidence_score=0.95,
                status="inferred",
                classification_data={"amount": 123},
            ),
        )
        bumps: list[tuple[str, int]] = []
        monkeypatch.setattr(read_cache, "bump", lambda scope, uid: bumps.append((scope, uid)))

        result = interpreter.interpret_event(event)
        assert len(result) == 1
        assert bumps == [(CALENDAR_READ_CACHE_SCOPE, user.id)]


def test_calendar_service_cache_hits_return_cached_payloads(app, monkeypatch):
    with app.app_context():
        user = _ensure_user("calendar-service-cache-hits@example.com")
        day_payload = {"window_start": "x", "window_end": "y", "events": []}
        week_payload = {"window_start": "w1", "window_end": "w2", "events": []}
        month_payload = {"window_start": "m1", "window_end": "m2", "spillover_days": [], "events": []}
        ledger_payload = {"anchor": "2026-01-01", "events": [], "next_cursor": None, "prev_cursor": None}

        store = {
            ("day", "2026-01-01"): day_payload,
            ("week", "2025-12-29"): week_payload,
            ("month", "2026", "1"): month_payload,
            ("ledger", "2026-01-01"): ledger_payload,
        }

        def _fake_get(scope, uid, key):
            if key.get("view") == "day":
                return store.get(("day", key["date"]))
            if key.get("view") == "week":
                return store.get(("week", key["start_date"]))
            if key.get("view") == "month":
                return store.get(("month", str(key["year"]), str(key["month"])))
            if key.get("view") == "ledger":
                return store.get(("ledger", key["anchor"]))
            return None  # pragma: no cover

        monkeypatch.setattr(calendar_service.read_cache, "get", _fake_get)

        assert calendar_service.get_day_view(user.id, datetime(2026, 1, 1).date()) == day_payload
        assert calendar_service.get_week_view(user.id, datetime(2025, 12, 29).date()) == week_payload
        assert calendar_service.get_month_view(user.id, 2026, 1) == month_payload
        assert calendar_service.get_ledger(user.id, datetime(2026, 1, 1).date()) == ledger_payload


def test_calendar_service_mutations_bump_cache(app, monkeypatch):
    with app.app_context():
        user = _ensure_user("calendar-service-mutations@example.com")
        bumps: list[tuple[str, int]] = []
        monkeypatch.setattr(calendar_service.read_cache, "bump", lambda scope, uid: bumps.append((scope, uid)))

        event = calendar_service.create_calendar_event(
            user_id=user.id,
            title="Initial",
            start_time=datetime.utcnow(),
            source="manual",
        )

        calendar_service.update_calendar_event(user.id, event.id, title="Updated")

        interp = CalendarEventInterpretation(
            calendar_event_id=event.id,
            user_id=user.id,
            domain="finance",
            record_type="transaction",
            confidence_score=0.7,
            status="inferred",
            classification_data={"amount": 20},
        )
        db.session.add(interp)
        db.session.commit()
        calendar_service.update_interpretation_status(user.id, interp.id, "rejected")

        calendar_service.delete_calendar_event(user.id, event.id)

        assert len(bumps) >= 4
        assert all(scope == calendar_service.CALENDAR_READ_CACHE_SCOPE for scope, _ in bumps)
        assert all(uid == user.id for _, uid in bumps)


def test_outbox_event_bus_adapter_creates_event_record_when_missing(app):
    with app.app_context():
        user = _ensure_user("outbox-adapter@example.com")
        message = OutboxMessage(
            event_type="test.event",
            payload={"foo": "bar"},
            user_id=user.id,
            created_at=datetime.utcnow(),
            available_at=datetime.utcnow(),
            status="pending",
            attempts=0,
        )
        db.session.add(message)
        db.session.commit()

        published = []

        class _Bus:
            def publish(self, event):
                published.append(event)

        adapter = EventBusAdapter(bus=_Bus())
        adapter.dispatch(message)

        assert published
        event = published[0]
        assert event.event_type == message.event_type
        assert event.user_id == user.id
