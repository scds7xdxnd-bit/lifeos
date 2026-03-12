from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from flask_jwt_extended import create_access_token

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.substrate_models import Interpretation, UserFeedbackEvent
from lifeos.core.users.models import User
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _auth_headers(app) -> tuple[int, dict[str, str]]:
    with app.app_context():
        user = User(email=f"insights-api-v1-{uuid4().hex}@example.com", password_hash="test")
        db.session.add(user)
        db.session.commit()
        token = create_access_token(identity=str(user.id), additional_claims={"roles": []})
    return int(user.id), {"Authorization": f"Bearer {token}"}


def test_feed_query_validation_error_returns_400(app, client):
    _user_id, headers = _auth_headers(app)
    resp = client.get("/api/v1/insights/feed?page=0", headers=headers)
    body = resp.get_json() or {}
    assert resp.status_code == 400
    assert body.get("ok") is False
    assert body.get("error") == "validation_error"
    assert isinstance(body.get("details"), list)


def test_feed_serializes_service_records(app, client, monkeypatch):
    from lifeos.core.insights import api_v1 as insights_api

    user_id, headers = _auth_headers(app)
    record = InsightRecord(
        id=501,
        user_id=user_id,
        event_id=77,
        event_type="projects.task.completed",
        kind="milestone",
        message="task completed",
        severity="info",
        data={"source": "qa"},
        created_at=datetime(2026, 2, 1, 10, 0, 0),
    )

    monkeypatch.setattr(insights_api.read_cache, "get", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(insights_api.read_cache, "set", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(insights_api, "list_insights_feed", lambda *_args, **_kwargs: ([record], 1, 1, 1))

    resp = client.get("/api/v1/insights/feed", headers=headers)
    body = resp.get_json() or {}
    assert resp.status_code == 200
    assert body.get("ok") is True
    assert body["items"][0]["id"] == 501
    assert body["items"][0]["source_event_type"] == "projects.task.completed"


def test_review_query_invalid_limit_returns_400(app, client):
    _user_id, headers = _auth_headers(app)
    resp = client.get("/api/v1/insights/review?limit=bad&offset=0", headers=headers)
    assert resp.status_code == 400
    assert resp.get_json() == {"ok": False, "error": "validation_error"}


def test_list_proposals_invalid_limit_returns_400(app, client):
    _user_id, headers = _auth_headers(app)
    resp = client.get("/api/v1/insights/proposals?limit=bad&offset=0", headers=headers)
    assert resp.status_code == 400
    assert resp.get_json() == {"ok": False, "error": "validation_error"}


def test_list_proposals_serializes_and_clamps_limit_offset(app, client, monkeypatch):
    from lifeos.core.insights import api_v1 as insights_api

    user_id, headers = _auth_headers(app)
    seen: dict[str, int | str | None] = {}

    def _fake_list_interpretations(uid: int, status: str | None, limit: int, offset: int):
        seen["uid"] = uid
        seen["status"] = status
        seen["limit"] = limit
        seen["offset"] = offset
        return [
            Interpretation(
                id=101,
                user_id=uid,
                interpretation_type="calendar.relationship.interaction",
                input_event_ids=["evt-1"],
                proposed_writes=[{"kind": "interaction"}],
                applied_writes=[],
                confidence=0.73,
                evidence="matched person",
                status="proposed",
                reversible_plan={},
                fingerprint="fp-proposal-1",
                created_at=datetime(2026, 1, 1, 8, 0, 0),
            )
        ]

    monkeypatch.setattr(insights_api, "list_interpretations", _fake_list_interpretations)
    resp = client.get(
        "/api/v1/insights/proposals?status=proposed&limit=999&offset=-2",
        headers=headers,
    )
    body = resp.get_json() or {}
    assert resp.status_code == 200
    assert body.get("ok") is True
    assert body.get("limit") == 200
    assert body.get("offset") == 0
    assert body["items"][0]["id"] == 101
    assert body["items"][0]["confidence"] == pytest.approx(0.73)
    assert seen == {"uid": user_id, "status": "proposed", "limit": 200, "offset": 0}


def test_decide_proposal_invalid_action_validation_error(app, client):
    app.config["WTF_CSRF_ENABLED"] = False
    _user_id, headers = _auth_headers(app)
    resp = client.patch("/api/v1/insights/proposals/77", json={}, headers=headers)
    body = resp.get_json() or {}
    assert resp.status_code == 400
    assert body.get("ok") is False
    assert body.get("error") == "validation_error"
    assert isinstance(body.get("details"), list)


@pytest.mark.parametrize("error_code", ["not_found", "invalid_action", "invalid_proposal"])
def test_decide_proposal_maps_known_errors(app, client, monkeypatch, error_code):
    from lifeos.core.insights import api_v1 as insights_api

    app.config["WTF_CSRF_ENABLED"] = False
    _user_id, headers = _auth_headers(app)

    def _raise(*_args, **_kwargs):
        raise ValueError(error_code)

    monkeypatch.setattr(insights_api, "decide_interpretation", _raise)
    resp = client.patch("/api/v1/insights/proposals/99", json={"action": "accepted"}, headers=headers)
    assert resp.status_code == 400
    assert resp.get_json() == {"ok": False, "error": error_code}


def test_decide_proposal_maps_unknown_error_to_validation_error(app, client, monkeypatch):
    from lifeos.core.insights import api_v1 as insights_api

    app.config["WTF_CSRF_ENABLED"] = False
    _user_id, headers = _auth_headers(app)

    def _raise(*_args, **_kwargs):
        raise ValueError("unexpected_code")

    monkeypatch.setattr(insights_api, "decide_interpretation", _raise)
    resp = client.patch("/api/v1/insights/proposals/99", json={"action": "accepted"}, headers=headers)
    assert resp.status_code == 400
    assert resp.get_json() == {"ok": False, "error": "validation_error"}


def test_decide_proposal_success_includes_serialized_interpretation(app, client, monkeypatch):
    from lifeos.core.insights import api_v1 as insights_api

    app.config["WTF_CSRF_ENABLED"] = False
    user_id, headers = _auth_headers(app)
    seen: dict[str, object] = {}

    def _fake_decide(uid: int, interpretation_id: int, action: str, correction: dict | None = None):
        seen["uid"] = uid
        seen["interpretation_id"] = interpretation_id
        seen["action"] = action
        seen["correction"] = correction
        return Interpretation(
            id=interpretation_id,
            user_id=uid,
            interpretation_type="calendar.relationship.interaction",
            input_event_ids=["evt-1"],
            proposed_writes=[],
            applied_writes=[{"interaction_id": 44}],
            confidence=0.88,
            evidence="deterministic match",
            status="corrected",
            reversible_plan={"undo": []},
            fingerprint=f"fp-{interpretation_id}",
            created_at=datetime(2026, 1, 2, 9, 0, 0),
        )

    monkeypatch.setattr(insights_api, "decide_interpretation", _fake_decide)
    resp = client.patch(
        "/api/v1/insights/proposals/120",
        json={"action": "corrected", "person_id": 7, "method": "manual", "notes": "qa"},
        headers=headers,
    )
    body = resp.get_json() or {}
    assert resp.status_code == 200
    assert body.get("ok") is True
    assert body["interpretation"]["confidence"] == pytest.approx(0.88)
    assert seen == {
        "uid": user_id,
        "interpretation_id": 120,
        "action": "corrected",
        "correction": {"person_id": 7, "method": "manual", "notes": "qa"},
    }


def test_feedback_accepts_feedback_type_alias(app, client):
    app.config["WTF_CSRF_ENABLED"] = False
    user_id, headers = _auth_headers(app)
    resp = client.post(
        "/api/v1/insights/feedback",
        json={"feedback_type": "dismiss", "insight_type": "finance_calendar_obligation_risk"},
        headers=headers,
    )
    body = resp.get_json() or {}
    assert resp.status_code == 201
    assert body.get("ok") is True

    with app.app_context():
        feedback = UserFeedbackEvent.query.filter_by(user_id=user_id, feedback_type="dismiss").one()
        event = EventRecord.query.filter_by(user_id=user_id, event_type="insight_dismissed").one()
        assert feedback.payload.get("action") == "dismiss"
        assert event.payload.get("action") == "dismiss"


def test_feedback_accepts_action_type_alias(app, client):
    app.config["WTF_CSRF_ENABLED"] = False
    user_id, headers = _auth_headers(app)
    resp = client.post(
        "/api/v1/insights/feedback",
        json={"action_type": "act", "insight_type": "journal_habit_reflection_link"},
        headers=headers,
    )
    body = resp.get_json() or {}
    assert resp.status_code == 201
    assert body.get("ok") is True

    with app.app_context():
        feedback = UserFeedbackEvent.query.filter_by(user_id=user_id, feedback_type="act").one()
        event = EventRecord.query.filter_by(user_id=user_id, event_type="insight_feedback_positive").one()
        assert feedback.payload.get("action") == "act"
        assert event.payload.get("action") == "act"


def test_feedback_validation_error_for_invalid_payload_shape(app, client):
    app.config["WTF_CSRF_ENABLED"] = False
    _user_id, headers = _auth_headers(app)
    resp = client.post(
        "/api/v1/insights/feedback",
        json={"feedback_type": "dismiss", "insight_type": "x", "context": "not-an-object"},
        headers=headers,
    )
    body = resp.get_json() or {}
    assert resp.status_code == 400
    assert body.get("ok") is False
    assert body.get("error") == "validation_error"
    assert isinstance(body.get("details"), list)
