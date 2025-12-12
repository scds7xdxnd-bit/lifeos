import pytest
from datetime import datetime, date

from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.finance.models.accounting_models import (
    Account,
    AccountCategory,
    Transaction,
)
from lifeos.domains.finance.models.schedule_models import (
    MoneyScheduleRow,
    MoneyScheduleDailyBalance,
)
from lifeos.domains.finance.models.receivable_models import (
    ReceivableTracker,
    ReceivableManualEntry,
)
from lifeos.extensions import db


def _auth_headers(app, user_id: int):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"roles": ["finance:write"]})
    return {"Authorization": f"Bearer {token}"}


def _seed_finance(app):
    with app.app_context():
        user = User(email="dash@test.com", password_hash=hash_password("pw"))
        db.session.add(user)
        db.session.flush()
        cat = AccountCategory(
            code="1000",
            name="Asset",
            slug="asset",
            base_type="asset",
            normal_balance="debit",
            is_default=True,
            is_system=True,
        )
        db.session.add(cat)
        db.session.flush()
        acct = Account(
            user_id=user.id,
            name="Cash",
            account_type="asset",
            normalized_name="cash",
            category=cat,
        )
        db.session.add(acct)
        db.session.flush()
        txn = Transaction(
            user_id=user.id,
            amount=50,
            description="test",
            occurred_at=datetime.utcnow(),
        )
        db.session.add(txn)
        db.session.add(MoneyScheduleRow(user_id=user.id, account_id=acct.id, event_date=date.today(), amount=25))
        db.session.add(MoneyScheduleDailyBalance(user_id=user.id, as_of=date.today(), balance=25))
        tracker = ReceivableTracker(
            user_id=user.id,
            counterparty="Client",
            principal=100,
            start_date=date.today(),
        )
        db.session.add(tracker)
        db.session.flush()
        db.session.add(ReceivableManualEntry(tracker_id=tracker.id, entry_date=date.today(), amount=50))
        db.session.commit()
        return user


def test_dashboard_api(app, client):
    user = _seed_finance(app)
    headers = _auth_headers(app, user.id)
    resp = client.get("/api/finance/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["receivables_total"] >= 150  # principal + entry
    assert data["accounts"]
    assert data["recent_transactions"]
    assert data["upcoming_schedule"]
    assert data["forecast"]
