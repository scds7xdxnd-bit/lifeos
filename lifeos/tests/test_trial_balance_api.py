import pytest
from datetime import date, datetime

from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.unit

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
    user, cash, income = _setup_finance_data(app)
    headers = _auth_header(app, user.id)

    resp = client.get("/api/finance/trial_balance", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    accounts = {row["account_name"]: row for row in data["accounts"]}
    assert "Cash" in accounts and "Income" in accounts
    assert accounts["Cash"]["net"] > 0
    assert accounts["Income"]["net"] > 0

    from lifeos.domains.finance.services import trial_balance_service

    with app.app_context():
        result = trial_balance_service.trial_balance_view(user.id, as_of=date(2025, 1, 31))
        accounts_service = {row["account_name"]: row for row in result["accounts"]}
        assert accounts_service["Cash"]["net"] == 100
        assert accounts_service["Income"]["net"] == 100  # credit normal -> credit - debit


def test_trial_balance_period_and_monthly(app, client):
    user, cash, _ = _setup_finance_data(app)
    headers = _auth_header(app, user.id)

    resp = client.get("/api/finance/trial_balance/period", headers=headers)
    assert resp.status_code == 200
    totals = resp.get_json()["totals"]
    assert totals == {}

    resp = client.get("/api/finance/trial_balance/monthly", headers=headers)
    assert resp.status_code == 200
    months = resp.get_json()["months"]
    assert months["2025-01"]["debit"] == 100
    assert months["2025-02"]["debit"] == 50


def test_trial_balance_service_cache_hit_paths(app):
    from lifeos.domains.finance.services import trial_balance_service

    with app.app_context():
        cached_totals = {"10": {"debit": 5.0, "credit": 1.0}}
        cached_rollup = {"2025-01": {"debit": 5.0, "credit": 1.0}}
        cached_view = {"accounts": [], "categories": []}

        trial_balance_service.read_cache.clear()
        assert trial_balance_service.calculate_trial_balance(1, as_of=date(2025, 1, 31)) == {}

        from unittest.mock import patch

        with patch.object(trial_balance_service.read_cache, "get", return_value=cached_totals):
            totals = trial_balance_service.calculate_trial_balance(1, as_of=date(2025, 1, 31))
            assert totals == {10: {"debit": 5.0, "credit": 1.0}}

        with patch.object(trial_balance_service.read_cache, "get", return_value=cached_totals):
            totals = trial_balance_service.period_balance(1, date(2025, 1, 1), date(2025, 1, 31))
            assert totals == {10: {"debit": 5.0, "credit": 1.0}}

        captured = {}

        def _capture_set(scope, uid, key, value, ttl=None):
            captured["scope"] = scope
            captured["uid"] = uid
            captured["key"] = key

        with (
            patch.object(trial_balance_service.read_cache, "get", return_value=None),
            patch.object(
                trial_balance_service.read_cache,
                "set",
                _capture_set,
            ),
        ):
            trial_balance_service.period_balance(1, date(2025, 1, 1), date(2025, 1, 31))
        assert captured["scope"] == trial_balance_service.FINANCE_READ_CACHE_SCOPE

        with patch.object(trial_balance_service.read_cache, "get", return_value=cached_rollup):
            assert trial_balance_service.monthly_rollup(1) == cached_rollup

        with patch.object(trial_balance_service.read_cache, "get", return_value=cached_view):
            assert trial_balance_service.trial_balance_view(1, as_of=date(2025, 1, 31)) == cached_view
