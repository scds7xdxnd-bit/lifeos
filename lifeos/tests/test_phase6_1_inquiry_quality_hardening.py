"""Phase 6.1 focused inquiry quality hardening tests."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 6.1 Quality",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase6-1-quality-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_quality_metadata_is_deterministic_for_same_scope_and_as_of(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase61-quality-a@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 120},
                user_id=user.id,
                created_at=datetime(2026, 2, 3, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    payload = {
        "question": "How did finance look for this timeframe?",
        "domain": "finance",
        "cross_domain": False,
        "timeframe_start": "2026-02-01",
        "timeframe_end": "2026-02-07",
        "as_of_ts": "2026-02-07T12:00:00",
        "context_text": "I felt spend was high",
    }
    first = client.post("/api/v1/inquiries", json=payload, headers=headers)
    second = client.post("/api/v1/inquiries", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200

    first_quality = first.get_json()["latest_brief"]["quality_metadata"]
    second_quality = second.get_json()["latest_brief"]["quality_metadata"]
    assert json.dumps(first_quality, sort_keys=True) == json.dumps(second_quality, sort_keys=True)


def test_quality_metadata_reports_sparse_domains_and_refine_guidance(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase61-quality-b@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 44},
                user_id=user.id,
                created_at=datetime(2026, 2, 3, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Compare finance and habits this week.",
            "domains": ["finance", "habits"],
            "cross_domain": True,
            "timeframe_start": "2026-02-01",
            "timeframe_end": "2026-02-07",
            "as_of_ts": "2026-02-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    quality = response.get_json()["latest_brief"]["quality_metadata"]

    assert quality["findings_total"] >= 1
    assert quality["findings_with_evidence"] <= quality["findings_total"]
    assert 0.0 <= quality["evidence_coverage_ratio"] <= 1.0
    assert "habits" in quality["sparse_domains"]
    assert quality["refine_guidance"]
    assert any("sparse domains" in item.lower() for item in quality["refine_guidance"])


def test_quality_metadata_never_promotes_context_text(app, client):
    context_text = "PRIVATE_CONTEXT_SIGNAL_9999"
    with app.app_context():
        user, tokens = _user_tokens("phase61-quality-c@example.com")
        db.session.add(
            EventRecord(
                event_type="journal.entry.created",
                payload={"title": "check-in"},
                user_id=user.id,
                created_at=datetime(2026, 2, 3, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What happened in journal this week?",
            "domain": "journal",
            "cross_domain": False,
            "timeframe_start": "2026-02-01",
            "timeframe_end": "2026-02-07",
            "as_of_ts": "2026-02-07T23:00:00",
            "context_text": context_text,
        },
        headers=headers,
    )
    assert response.status_code == 201
    quality = response.get_json()["latest_brief"]["quality_metadata"]
    assert context_text not in json.dumps(quality, sort_keys=True)
