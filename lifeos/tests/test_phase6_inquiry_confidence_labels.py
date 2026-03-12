"""Phase 6 inquiry confidence vocabulary tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.contracts import CONFIDENCE_VOCABULARY
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 6 Confidence",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase6-confidence-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_inquiry_confidence_labels_use_canonical_vocabulary(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase6-confidence-a@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 99},
                user_id=user.id,
                created_at=datetime(2026, 1, 2, 12, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How is finance doing?",
            "domain": "finance",
            "cross_domain": False,
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-10",
            "as_of_ts": "2026-01-10T00:00:00",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    brief = resp.get_json()["latest_brief"]
    allowed = set(CONFIDENCE_VOCABULARY)
    for finding in brief["findings"]:
        assert finding["confidence_label"] in allowed
        assert "confidence_score" not in finding


def test_mixed_quality_evidence_caps_at_needs_review(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase6-confidence-b@example.com")
        # Only one selected domain has events -> mixed quality in cross-domain synthesis.
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 40},
                user_id=user.id,
                created_at=datetime(2026, 1, 3, 12, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Compare finance and habits.",
            "domains": ["finance", "habits"],
            "cross_domain": True,
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-10",
            "as_of_ts": "2026-01-10T00:00:00",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    findings = resp.get_json()["latest_brief"]["findings"]
    mixed = [item for item in findings if len(item["source_domains"]) > 1]
    assert mixed
    for finding in mixed:
        assert finding["confidence_label"] == "needs_review"
