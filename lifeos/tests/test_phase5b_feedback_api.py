from __future__ import annotations

from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.substrate_models import UserFeedbackEvent
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _create_user_with_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 5b Feedback",
            timezone="UTC",
        )
    )
    tokens = issue_tokens(user)
    return user, tokens


def _prime_csrf(client, token: str = "phase5b-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _auth_headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_feedback_api_records_and_dedupes(app, client):
    with app.app_context():
        user, tokens = _create_user_with_tokens("phase5b-feedback-one@example.com")
        source_event = EventRecord(
            event_type="calendar.event.created",
            payload={"event_id": "c1"},
            user_id=user.id,
            created_at=datetime.utcnow(),
        )
        db.session.add(source_event)
        db.session.flush()
        insight = InsightRecord(
            user_id=user.id,
            event_id=source_event.id,
            event_type=source_event.event_type,
            kind="finance_calendar_obligation_risk",
            message="message",
            severity="info",
            priority=70,
            delivery_policy="feed",
            data={"window_end": "2025-01-10", "window_days": 30},
        )
        db.session.add(insight)
        db.session.commit()

    csrf = _prime_csrf(client)
    payload = {
        "insight_id": insight.id,
        "action": "dismiss",
        "reason": "not_me",
        "context": {"window_end": "2025-01-10", "window_days": 30},
    }
    headers = _auth_headers(tokens["access_token"], csrf)
    first = client.post("/api/v1/insights/feedback", json=payload, headers=headers)
    assert first.status_code == 201
    assert first.get_json()["ok"] is True

    second = client.post("/api/v1/insights/feedback", json=payload, headers=headers)
    assert second.status_code == 200
    assert second.get_json()["deduped"] is True

    with app.app_context():
        assert UserFeedbackEvent.query.filter_by(user_id=user.id, feedback_type="dismiss").count() == 1
        assert EventRecord.query.filter_by(user_id=user.id, event_type="insight_dismissed").count() == 1


def test_feedback_api_validation_errors(app, client):
    app.config["WTF_CSRF_ENABLED"] = True
    with app.app_context():
        user, tokens = _create_user_with_tokens("phase5b-feedback-two@example.com")
        source_event = EventRecord(
            event_type="calendar.event.created",
            payload={"event_id": "c2"},
            user_id=user.id,
            created_at=datetime.utcnow(),
        )
        db.session.add(source_event)
        db.session.flush()
        insight = InsightRecord(
            user_id=user.id,
            event_id=source_event.id,
            event_type=source_event.event_type,
            kind="finance_calendar_obligation_risk",
            message="message",
            severity="info",
            priority=70,
            delivery_policy="feed",
            data={},
        )
        db.session.add(insight)
        db.session.commit()

    csrf = _prime_csrf(client)
    headers = _auth_headers(tokens["access_token"], csrf)

    bad_action = client.post(
        "/api/v1/insights/feedback",
        json={"insight_id": insight.id, "action": "unknown"},
        headers=headers,
    )
    assert bad_action.status_code == 400
    assert bad_action.get_json()["error"] == "invalid_action"

    bad_reason = client.post(
        "/api/v1/insights/feedback",
        json={"insight_id": insight.id, "action": "dismiss", "reason": "made_up"},
        headers=headers,
    )
    assert bad_reason.status_code == 400
    assert bad_reason.get_json()["error"] == "invalid_reason"

    missing_identity = client.post(
        "/api/v1/insights/feedback",
        json={"action": "dismiss"},
        headers=headers,
    )
    assert missing_identity.status_code == 400
    assert missing_identity.get_json()["error"] == "invalid_insight"

    not_found = client.post(
        "/api/v1/insights/feedback",
        json={"insight_id": 999999, "action": "dismiss"},
        headers=headers,
    )
    assert not_found.status_code == 404
    assert not_found.get_json()["error"] == "not_found"

    no_csrf = client.post(
        "/api/v1/insights/feedback",
        json={"insight_id": insight.id, "action": "dismiss"},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert no_csrf.status_code == 403
    assert no_csrf.get_json()["error"] == "csrf_failed"
