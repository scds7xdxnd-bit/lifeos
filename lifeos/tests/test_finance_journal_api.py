from __future__ import annotations

import pytest
from datetime import datetime

pytestmark = pytest.mark.integration

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.finance.models.accounting_models import AccountCategory
from lifeos.domains.finance.services.accounting_service import create_account
from lifeos.extensions import db


def _prime_csrf(client) -> str:
    token = "test-csrf-token"
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _auth_headers(token: str, csrf_token: str | None = None) -> dict[str, str]:
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token
    return headers


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


def test_get_journal_entry_detail_includes_lines_and_totals(app, client):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="journal-detail@example.com",
                password="secret123",
                full_name="Detail",
                timezone="UTC",
            )
        )
        debit_account, credit_account = _seed_accounts(user.id)
        tokens = issue_tokens(user)
    csrf_token = _prime_csrf(client)

    payload = {
        "description": "Detail entry",
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
    create_resp = client.post(
        "/api/finance/journal/entries",
        json=payload,
        headers=_auth_headers(tokens["access_token"], csrf_token),
    )
    assert create_resp.status_code == 200
    created = create_resp.get_json()
    entry_id = created["entry_id"]

    detail_resp = client.get(
        f"/api/finance/journal/entries/{entry_id}",
        headers=_auth_headers(tokens["access_token"]),
    )
    assert detail_resp.status_code == 200
    body = detail_resp.get_json()

    assert body["ok"] is True
    entry = body["entry"]
    assert entry["id"] == entry_id
    assert entry["debit_total"] == 125.5
    assert entry["credit_total"] == 125.5
    assert len(entry["lines"]) == 2
    assert {line["account_name"] for line in entry["lines"]} == {"Cash", "Revenue"}


def test_list_journal_entries_include_totals(app, client):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="journal-list@example.com",
                password="secret123",
                full_name="List",
                timezone="UTC",
            )
        )
        debit_account, credit_account = _seed_accounts(user.id)
        tokens = issue_tokens(user)
    csrf_token = _prime_csrf(client)

    payload = {
        "description": "List entry",
        "posted_at": datetime.utcnow().isoformat(),
        "lines": [
            {
                "account_id": debit_account.id,
                "dc": "D",
                "amount": 75.0,
                "memo": "debit line",
            },
            {
                "account_id": credit_account.id,
                "dc": "C",
                "amount": 75.0,
                "memo": "credit line",
            },
        ],
    }
    create_resp = client.post(
        "/api/finance/journal/entries",
        json=payload,
        headers=_auth_headers(tokens["access_token"], csrf_token),
    )
    assert create_resp.status_code == 200

    list_resp = client.get(
        "/api/finance/journal",
        headers=_auth_headers(tokens["access_token"]),
    )
    assert list_resp.status_code == 200
    body = list_resp.get_json()

    assert body["ok"] is True
    assert body["total_entries"] >= 1
    entry = body["entries"][0]
    assert entry["debit_total"] == 75.0
    assert entry["credit_total"] == 75.0
    assert entry["lines"] == 2
