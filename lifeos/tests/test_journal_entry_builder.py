from __future__ import annotations

import pytest
from datetime import datetime

pytestmark = pytest.mark.integration

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.finance.events import FINANCE_JOURNAL_POSTED
from lifeos.domains.finance.models.accounting_models import (
    AccountCategory,
    JournalEntry,
)
from lifeos.domains.finance.services.accounting_service import create_account
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox.models import OutboxMessage


def _auth_headers(token: str, csrf_token: str | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token
    return headers


def _prime_csrf(client) -> str:
    """Place a CSRF token in the test client session and return it."""
    token = "test-csrf-token"
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _seed_accounts(user_id: int):
    asset = AccountCategory(
        code="1000",
        name="Cash",
        slug="cash",
        base_type="asset",
        normal_balance="debit",
        is_default=True,
        is_system=True,
    )
    revenue = AccountCategory(
        code="4000",
        name="Revenue",
        slug="revenue",
        base_type="income",
        normal_balance="credit",
        is_default=True,
        is_system=True,
    )
    db.session.add_all([asset, revenue])
    db.session.commit()
    debit_account = create_account(user_id, "Cash", "asset", category_id=asset.id)
    credit_account = create_account(user_id, "Revenue", "income", category_id=revenue.id)
    return debit_account, credit_account


def test_post_journal_entry_smoke_logged_in(app, client):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="journal@example.com",
                password="secret123",
                full_name="JRNL",
                timezone="UTC",
            )
        )
        debit_account, credit_account = _seed_accounts(user.id)
        tokens = issue_tokens(user)
    csrf_token = _prime_csrf(client)

    payload = {
        "description": "Smoke journal",
        "posted_at": datetime.utcnow().isoformat(),
        "lines": [
            {
                "account_id": debit_account.id,
                "dc": "D",
                "amount": 125.5,
                "memo": "debit line",
            },
            {
                "account_id": credit_account.id,
                "dc": "C",
                "amount": 125.5,
                "memo": "credit line",
            },
        ],
    }
    resp = client.post(
        "/api/finance/journal/entries",
        json=payload,
        headers=_auth_headers(tokens["access_token"], csrf_token),
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    entry_id = body["entry_id"]
    assert body["total_debit"] == 125.5
    assert body["total_credit"] == 125.5

    with app.app_context():
        entry = JournalEntry.query.get(entry_id)
        assert entry is not None
        assert len(entry.lines) == 2
        outbox = OutboxMessage.query.filter_by(event_type=FINANCE_JOURNAL_POSTED, user_id=user.id).first()
        assert outbox is not None
        assert outbox.status == "pending"
        assert outbox.payload["entry_id"] == entry.id
        assert outbox.payload["line_count"] == 2


def test_unbalanced_entry_rejected(app, client):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="unbalanced@example.com",
                password="secret123",
                full_name="Unbalanced",
                timezone="UTC",
            )
        )
        debit_account, credit_account = _seed_accounts(user.id)
        tokens = issue_tokens(user)
    csrf_token = _prime_csrf(client)

    payload = {
        "description": "Should fail",
        "lines": [
            {"account_id": debit_account.id, "dc": "D", "amount": 50},
            {"account_id": credit_account.id, "dc": "C", "amount": 10},
        ],
    }
    resp = client.post(
        "/api/finance/journal/entries",
        json=payload,
        headers=_auth_headers(tokens["access_token"], csrf_token),
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"] == "unbalanced_entry"

    with app.app_context():
        assert JournalEntry.query.count() == 0
        assert OutboxMessage.query.filter_by(event_type=FINANCE_JOURNAL_POSTED).count() == 0


def test_journal_page_exposes_telemetry_hook_when_configured(app, client, monkeypatch):
    monkeypatch.setenv("LIFEOS_TELEMETRY_ENDPOINT", "https://telemetry.example.com/beacon")
    resp = client.get("/finance/journal")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "lifeos:telemetry" in html
    assert "LIFEOS_TELEMETRY_ENDPOINT" in html
