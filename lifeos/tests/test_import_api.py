import pytest
import io
from datetime import datetime

from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.finance.models.accounting_models import Account, AccountCategory, JournalEntry
from lifeos.extensions import db


def _auth_headers(app, user_id: int):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"roles": ["finance:write"]})
    return {"Authorization": f"Bearer {token}"}


def _setup_accounts(app):
    with app.app_context():
        user = User(email="import@test.com", password_hash=hash_password("pw"))
        db.session.add(user)
        db.session.flush()
        asset = AccountCategory(
            code="1000",
            name="Asset",
            slug="asset",
            base_type="asset",
            normal_balance="debit",
            is_default=True,
            is_system=True,
        )
        income = AccountCategory(
            code="4000",
            name="Income",
            slug="income",
            base_type="income",
            normal_balance="credit",
            is_default=True,
            is_system=True,
        )
        db.session.add_all([asset, income])
        db.session.flush()
        cash = Account(user_id=user.id, name="Cash", account_type="asset", normalized_name="cash", category=asset)
        revenue = Account(user_id=user.id, name="Revenue", account_type="income", normalized_name="revenue", category=income)
        db.session.add_all([cash, revenue])
        db.session.commit()
        return user, cash, revenue


def _csv_bytes(cash_id, revenue_id):
    content = (
        "description,amount,debit_account_id,credit_account_id,posted_at\n"
        f"Sale 1,100,{cash_id},{revenue_id},2025-02-01\n"
        f"Sale 2,50,{cash_id},{revenue_id},2025-02-02\n"
    )
    return io.BytesIO(content.encode("utf-8"))


def test_import_preview_and_commit(app, client):
    user, cash, revenue = _setup_accounts(app)
    headers = _auth_headers(app, user.id) | {"X-CSRF-Token": "test"}

    file_data = {"file": (_csv_bytes(cash.id, revenue.id), "import.csv")}
    resp = client.post("/api/finance/import/preview", data=file_data, headers=headers, content_type="multipart/form-data")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["count"] == 2

    file_data_commit = {"file": (_csv_bytes(cash.id, revenue.id), "import.csv")}
    resp = client.post("/api/finance/import/commit", data=file_data_commit, headers=headers, content_type="multipart/form-data")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["ok"] is True
    assert payload["created"] == 2

    with app.app_context():
        entries = JournalEntry.query.filter_by(user_id=user.id).all()
        assert len(entries) == 2
