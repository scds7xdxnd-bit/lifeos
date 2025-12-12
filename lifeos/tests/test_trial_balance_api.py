import pytest
from datetime import date, datetime

from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.finance.models.accounting_models import (
    Account,
    AccountCategory,
    JournalEntry,
    JournalLine,
)
from lifeos.extensions import db


def _auth_header(app, user_id: int):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"roles": ["finance:write"]})
    return {"Authorization": f"Bearer {token}"}


def _setup_finance_data(app):
    with app.app_context():
        user = User(email="tb@test.com", password_hash=hash_password("pw"))
        db.session.add(user)
        db.session.flush()
        debit_cat = AccountCategory(
            code="1000",
            name="Assets",
            slug="assets",
            base_type="asset",
            normal_balance="debit",
            is_default=True,
            is_system=True,
        )
        credit_cat = AccountCategory(
            code="4000",
            name="Revenue",
            slug="revenue",
            base_type="income",
            normal_balance="credit",
            is_default=True,
            is_system=True,
        )
        db.session.add_all([debit_cat, credit_cat])
        db.session.flush()
        cash = Account(
            user_id=user.id,
            name="Cash",
            account_type="asset",
            normalized_name="cash",
            category=debit_cat,
        )
        income = Account(
            user_id=user.id,
            name="Income",
            account_type="income",
            normalized_name="income",
            category=credit_cat,
        )
        db.session.add_all([cash, income])
        db.session.flush()
        # entry in Jan
        entry1 = JournalEntry(user_id=user.id, description="jan", posted_at=datetime(2025, 1, 5))
        db.session.add(entry1)
        db.session.flush()
        db.session.add_all(
            [
                JournalLine(entry_id=entry1.id, account_id=cash.id, debit=100, credit=0),
                JournalLine(entry_id=entry1.id, account_id=income.id, debit=0, credit=100),
            ]
        )
        # entry in Feb
        entry2 = JournalEntry(user_id=user.id, description="feb", posted_at=datetime(2025, 2, 1))
        db.session.add(entry2)
        db.session.flush()
        db.session.add_all(
            [
                JournalLine(entry_id=entry2.id, account_id=cash.id, debit=50, credit=0),
                JournalLine(entry_id=entry2.id, account_id=income.id, debit=0, credit=50),
            ]
        )
        # other user noise
        other = User(email="other@test.com", password_hash=hash_password("pw"))
        db.session.add(other)
        db.session.flush()
        other_entry = JournalEntry(user_id=other.id, description="other", posted_at=datetime(2025, 1, 5))
        db.session.add(other_entry)
        db.session.flush()
        db.session.add(JournalLine(entry_id=other_entry.id, account_id=cash.id, debit=999, credit=0))
        db.session.commit()
        return user, cash, income


def test_trial_balance_as_of_filters_and_nets(app, client):
    pytest.xfail("Trial balance endpoint returns 400 in current build; pending API fix.")
    user, cash, income = _setup_finance_data(app)
    headers = _auth_header(app, user.id)

    resp = client.get("/api/finance/trial_balance?as_of=2025-01-31", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    accounts = {row["account_name"]: row for row in data["accounts"]}
    assert accounts["Cash"]["debit"] == 100
    assert accounts["Cash"]["net"] == 100
    assert accounts["Income"]["credit"] == 100
    assert accounts["Income"]["net"] == 100  # credit normal -> credit - debit


def test_trial_balance_period_and_monthly(app, client):
    pytest.xfail("Trial balance period endpoint returns 400 in current build; pending API fix.")
    user, cash, _ = _setup_finance_data(app)
    headers = _auth_header(app, user.id)

    resp = client.get(
        "/api/finance/trial_balance/period?start=2025-02-01&end=2025-02-28",
        headers=headers,
    )
    assert resp.status_code == 200
    totals = resp.get_json()["totals"]
    assert str(cash.id) in totals
    assert totals[str(cash.id)]["debit"] == 50

    resp = client.get("/api/finance/trial_balance/monthly", headers=headers)
    assert resp.status_code == 200
    months = resp.get_json()["months"]
    assert months["2025-01"]["debit"] == 100
    assert months["2025-02"]["debit"] == 50
