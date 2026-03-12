"""Phase 6 inquiry determinism tests."""

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


def _create_user_with_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 6 Determinism",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase6-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_same_input_and_as_of_returns_byte_identical_brief(app, client):
    with app.app_context():
        user, tokens = _create_user_with_tokens("phase6-determinism-a@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 120},
                user_id=user.id,
                created_at=datetime(2026, 1, 2, 8, 0, 0),
            )
        )
        db.session.commit()

    csrf = _prime_csrf(client)
    headers = _headers(tokens["access_token"], csrf)
    payload = {
        "question": "How did finance look in this window?",
        "domain": "finance",
        "cross_domain": False,
        "timeframe_start": "2026-01-01",
        "timeframe_end": "2026-01-05",
        "as_of_ts": "2026-01-05T12:00:00",
        "context_text": "I think this week felt expensive",
    }
    first = client.post("/api/v1/inquiries", json=payload, headers=headers)
    second = client.post("/api/v1/inquiries", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200

    first_brief = first.get_json()["latest_brief"]
    second_brief = second.get_json()["latest_brief"]
    assert json.dumps(first_brief, sort_keys=True) == json.dumps(second_brief, sort_keys=True)


def test_different_as_of_allows_output_delta(app, client):
    with app.app_context():
        user, tokens = _create_user_with_tokens("phase6-determinism-b@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 50},
                    user_id=user.id,
                    created_at=datetime(2026, 1, 1, 9, 0, 0),
                ),
                EventRecord(
                    event_type="habits.habit.logged",
                    payload={"habit_id": 1},
                    user_id=user.id,
                    created_at=datetime(2026, 1, 4, 9, 0, 0),
                ),
            ]
        )
        db.session.commit()

    csrf = _prime_csrf(client)
    headers = _headers(tokens["access_token"], csrf)
    base_payload = {
        "question": "What changed between habits and finance?",
        "domains": ["finance", "habits"],
        "cross_domain": True,
        "timeframe_start": "2026-01-01",
        "timeframe_end": "2026-01-07",
        "context_text": "I want to compare both domains",
    }

    early = client.post(
        "/api/v1/inquiries",
        json=base_payload | {"as_of_ts": "2026-01-02T00:00:00"},
        headers=headers,
    )
    later = client.post(
        "/api/v1/inquiries",
        json=base_payload | {"as_of_ts": "2026-01-06T00:00:00"},
        headers=headers,
    )
    assert early.status_code == 201
    assert later.status_code == 201
    early_brief = early.get_json()["latest_brief"]
    later_brief = later.get_json()["latest_brief"]
    assert json.dumps(early_brief, sort_keys=True) != json.dumps(later_brief, sort_keys=True)


def test_finding_and_evidence_order_is_deterministic(app, client):
    with app.app_context():
        user, tokens = _create_user_with_tokens("phase6-determinism-c@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="projects.task.completed",
                    payload={"task": "ship"},
                    user_id=user.id,
                    created_at=datetime(2026, 1, 2, 9, 0, 0),
                ),
                EventRecord(
                    event_type="projects.task.completed",
                    payload={"task": "verify"},
                    user_id=user.id,
                    created_at=datetime(2026, 1, 3, 9, 0, 0),
                ),
            ]
        )
        db.session.commit()

    csrf = _prime_csrf(client)
    headers = _headers(tokens["access_token"], csrf)
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How are projects progressing?",
            "domain": "projects",
            "cross_domain": False,
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-07",
            "as_of_ts": "2026-01-07T00:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    findings = response.get_json()["latest_brief"]["findings"]
    assert findings == sorted(findings, key=lambda item: (",".join(item["source_domains"]), item["claim"]))
    for finding in findings:
        refs = finding["evidence_refs"]
        assert refs == sorted(
            refs,
            key=lambda item: (
                str(item.get("domain") or ""),
                str(item.get("source_kind") or ""),
                str(item.get("event_type") or item.get("source_ref") or ""),
                int(item.get("source_id") or 0),
            ),
        )
