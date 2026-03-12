"""Phase 6 inquiry context non-promotion safety tests."""

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
            full_name="Phase 6 Context",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase6-context-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_context_is_separated_and_not_promoted_to_evidence(app, client):
    context_text = "UNSUPPORTED_ASSERTION_CONTEXT_12345"
    with app.app_context():
        user, tokens = _user_tokens("phase6-context-a@example.com")
        db.session.add(
            EventRecord(
                event_type="journal.entry.created",
                payload={"title": "Daily note"},
                user_id=user.id,
                created_at=datetime(2026, 1, 2, 11, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What happened in journal?",
            "domain": "journal",
            "cross_domain": False,
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-10",
            "as_of_ts": "2026-01-10T00:00:00",
            "context_text": context_text,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    brief = resp.get_json()["latest_brief"]
    context_block = brief["context_non_evidence"]
    assert context_block["label"] == "Context (not evidence)"
    assert context_block["text"] == context_text

    evidence_blob = json.dumps([finding["evidence_refs"] for finding in brief["findings"]], sort_keys=True)
    assert context_text not in evidence_blob
    claims_blob = " ".join(finding["claim"] for finding in brief["findings"])
    assert context_text not in claims_blob
