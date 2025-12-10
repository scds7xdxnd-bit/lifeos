from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.journal.models import JournalEntry
from lifeos.platform.outbox.models import OutboxMessage
from lifeos.domains.journal.events import JOURNAL_ENTRY_CREATED
from lifeos.extensions import db


def _prime_csrf(client) -> str:
    token = "test-csrf-token"
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _auth_headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_create_journal_entry_success(app, client):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="journal-api@example.com",
                password="secret123",
                full_name="Journal",
                timezone="UTC",
            )
        )
        tokens = issue_tokens(user)
    csrf_token = _prime_csrf(client)

    payload = {"title": "Day 1", "body": "Great day", "tags": ["gratitude"], "mood": 3}
    resp = client.post(
        "/api/journal",
        json=payload,
        headers=_auth_headers(tokens["access_token"], csrf_token),
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True
    entry_id = body["entry"]["id"]

    with app.app_context():
        entry = JournalEntry.query.get(entry_id)
        assert entry is not None
        assert entry.body == "Great day"
        outbox = OutboxMessage.query.filter_by(event_type=JOURNAL_ENTRY_CREATED, user_id=user.id).first()
        assert outbox is not None
        assert outbox.payload["entry_id"] == entry.id


def test_create_journal_entry_missing_body_fails_validation(app, client):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="journal-bad@example.com",
                password="secret123",
                full_name="Journal",
                timezone="UTC",
            )
        )
        tokens = issue_tokens(user)
    csrf_token = _prime_csrf(client)

    payload = {"title": "Empty body", "body": ""}
    resp = client.post(
        "/api/journal",
        json=payload,
        headers=_auth_headers(tokens["access_token"], csrf_token),
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["ok"] is False
