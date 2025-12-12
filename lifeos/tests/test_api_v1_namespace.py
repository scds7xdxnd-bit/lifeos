from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.services import list_insights_feed
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db


def _create_user(email_prefix: str):
    email = f"{email_prefix}-{uuid4().hex}@example.com"
    return create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="API v1 User",
            timezone="UTC",
        )
    )


def _api_v1_login(client, email: str, password: str) -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    body = resp.get_json() or {}
    assert resp.status_code == 200, f"Expected 200 from /api/v1/auth/login, got {resp.status_code}"
    assert body.get("ok") is True
    assert body.get("access_token")
    assert body.get("refresh_token")
    assert body.get("csrf_token")
    assert body.get("user")
    return body


class TestApiV1Auth:
    def test_api_v1_login_returns_tokens_and_user(self, app, client):
        with app.app_context():
            user = _create_user("api-v1-login")
            user_email = user.email

        body = _api_v1_login(client, user_email, "secret123")

        assert body["user"]["email"] == user_email
        assert set(body).issuperset({"access_token", "refresh_token", "csrf_token", "user", "ok"})

    def test_api_v1_refresh_issues_new_access_token(self, app, client):
        with app.app_context():
            user = _create_user("api-v1-refresh")
            user_email = user.email

        login_body = _api_v1_login(client, user_email, "secret123")

        refresh_token = login_body["refresh_token"]
        csrf_token = login_body["csrf_token"]
        headers = {"Authorization": f"Bearer {refresh_token}", "X-CSRF-Token": csrf_token}

        resp = client.post("/api/v1/auth/refresh", headers=headers)
        data = resp.get_json() or {}

        assert resp.status_code == 200
        assert data.get("ok") is True
        assert data.get("access_token")
        assert data["access_token"] != login_body["access_token"]


class TestInsightsFeedV1:
    def test_insights_feed_requires_auth(self, client):
        resp = client.get("/api/v1/insights/feed")
        assert resp.status_code == 401

    def test_insights_feed_returns_paginated_items_and_user_scope(self, app, client):
        with app.app_context():
            user = _create_user("insights-feed")
            other_user = _create_user("insights-feed-other")
            user_email = user.email
            user_id = user.id
            other_user_id = other_user.id

            now = datetime.utcnow()
            latest_event = EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 50},
                user_id=user.id,
                created_at=now - timedelta(minutes=1),
            )
            older_event = EventRecord(
                event_type="health.workout.logged",
                payload={"duration": 30},
                user_id=user.id,
                created_at=now - timedelta(days=1),
            )
            other_event = EventRecord(
                event_type="projects.task.completed",
                payload={"task": "other"},
                user_id=other_user_id,
                created_at=now - timedelta(minutes=2),
            )
            db.session.add_all([latest_event, older_event, other_event])
            db.session.commit()

            user_insights = [
                InsightRecord(
                    user_id=user.id,
                    event_id=latest_event.id,
                    event_type=latest_event.event_type,
                    kind="alert",
                    message="latest insight",
                    severity="info",
                    data={"source": "test"},
                    created_at=latest_event.created_at,
                ),
                InsightRecord(
                    user_id=user.id,
                    event_id=older_event.id,
                    event_type=older_event.event_type,
                    kind="summary",
                    message="older insight",
                    severity="warning",
                    data={},
                    created_at=older_event.created_at,
                ),
            ]
            other_insight = InsightRecord(
                user_id=other_user.id,
                event_id=other_event.id,
                event_type=other_event.event_type,
                kind="other",
                message="should not leak",
                severity="info",
                data={},
                created_at=other_event.created_at,
            )
            db.session.add_all(user_insights + [other_insight])
            db.session.commit()

            latest_event_id = latest_event.id
            latest_event_type = latest_event.event_type

        login_body = _api_v1_login(client, user_email, "secret123")
        headers = {
            "Authorization": f"Bearer {login_body['access_token']}",
            "X-CSRF-Token": login_body["csrf_token"],
        }

        resp = client.get("/api/v1/insights/feed", headers=headers)
        payload = resp.get_json() or {}

        assert resp.status_code == 200
        assert payload.get("ok") is True
        assert payload["page"] == 1
        assert payload["total"] == 2
        assert payload["pages"] == 1
        assert isinstance(payload.get("items"), list)
        assert len(payload["items"]) == 2

        first = payload["items"][0]
        assert first["user_id"] == user_id
        assert "created_at" in first

    def test_insights_feed_supports_domain_severity_and_date_filters(self, app):
        with app.app_context():
            user = _create_user("insights-filter")
            now = datetime.utcnow()
            project_event = EventRecord(
                event_type="projects.task.completed",
                payload={"task": "launch"},
                user_id=user.id,
                created_at=now - timedelta(days=1),
            )
            finance_event = EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 200},
                user_id=user.id,
                created_at=now - timedelta(days=1),
            )
            old_health_event = EventRecord(
                event_type="health.workout.logged",
                payload={"duration": 45},
                user_id=user.id,
                created_at=now - timedelta(days=10),
            )
            db.session.add_all([project_event, finance_event, old_health_event])
            db.session.commit()

            insights = [
                InsightRecord(
                    user_id=user.id,
                    event_id=project_event.id,
                    event_type=project_event.event_type,
                    kind="milestone",
                    message="project warning",
                    severity="warning",
                    data={"project": "launch"},
                    created_at=project_event.created_at,
                ),
                InsightRecord(
                    user_id=user.id,
                    event_id=finance_event.id,
                    event_type=finance_event.event_type,
                    kind="spend",
                    message="finance info",
                    severity="info",
                    data={},
                    created_at=finance_event.created_at,
                ),
                InsightRecord(
                    user_id=user.id,
                    event_id=old_health_event.id,
                    event_type=old_health_event.event_type,
                    kind="health",
                    message="stale health insight",
                    severity="warning",
                    data={},
                    created_at=old_health_event.created_at,
                ),
            ]
            db.session.add_all(insights)
            db.session.commit()

            from lifeos.core.insights.schemas import InsightsFeedQuery

            filters = InsightsFeedQuery(
                domain="projects",
                severity="warning",
                start_date=(now - timedelta(days=3)).date(),
                end_date=now.date(),
                page=1,
                per_page=10,
            )
            items, total, page, pages = list_insights_feed(user.id, filters)
            assert total == 1
            assert page == 1
            assert pages == 1
            assert len(items) == 1
            record = items[0]
            assert record.event_type.startswith("projects.")
            assert record.severity == "warning"
            assert record.message == "project warning"

    def test_insights_feed_supports_domain_lists_and_status_filtering(self, app):
        with app.app_context():
            user = _create_user("insights-status")
            now = datetime.utcnow()
            finance_event = EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 100},
                user_id=user.id,
                created_at=now - timedelta(hours=1),
            )
            project_event = EventRecord(
                event_type="projects.task.completed",
                payload={"task": "done"},
                user_id=user.id,
                created_at=now - timedelta(hours=2),
            )
            db.session.add_all([finance_event, project_event])
            db.session.commit()

            records = [
                InsightRecord(
                    user_id=user.id,
                    event_id=finance_event.id,
                    event_type=finance_event.event_type,
                    kind="finance",
                    message="finance inferred",
                    severity="info",
                    data={"status": "inferred"},
                    created_at=finance_event.created_at,
                ),
                InsightRecord(
                    user_id=user.id,
                    event_id=project_event.id,
                    event_type=project_event.event_type,
                    kind="project",
                    message="project confirmed",
                    severity="info",
                    data={"status": "confirmed"},
                    created_at=project_event.created_at,
                ),
            ]
            db.session.add_all(records)
            db.session.commit()

            from lifeos.core.insights.schemas import InsightsFeedQuery

            filters = InsightsFeedQuery(domain=["finance", "projects"], status="confirmed", page=1, per_page=10)
            items, total, page, pages = list_insights_feed(user.id, filters)

            assert total == 1
            assert page == 1
            assert pages == 1
            assert len(items) == 1
            assert items[0].event_type.startswith("projects.")
            assert items[0].data.get("status") == "confirmed"
