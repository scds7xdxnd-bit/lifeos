import pytest
from datetime import date

from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.models import Role
from lifeos.core.users.models import User
from lifeos.core.auth.password import hash_password
from lifeos.domains.finance.models.accounting_models import AccountCategory, Account
from lifeos.domains.finance.models.schedule_models import MoneyScheduleRow
from lifeos.extensions import db


def auth_header(app, user_id: int, roles=None):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"roles": roles or []})
    return {"Authorization": f"Bearer {token}"}


def setup_finance_user(app):
    with app.app_context():
        role = Role.query.filter_by(name="finance:write").first()
        if not role:
            role = Role(name="finance:write")
            db.session.add(role)
            db.session.commit()
        user = User(email="forecast@test.com", password_hash=hash_password("pw"))
        user.roles.append(role)
        db.session.add(user)
        cat = AccountCategory(
            code="9999",
            name="Test",
            slug="test",
            base_type="asset",
            normal_balance="debit",
            is_default=True,
            is_system=True,
        )
        db.session.add(cat)
        db.session.flush()
        acct = Account(
            user_id=user.id,
            name="TestAcct",
            account_type="asset",
            normalized_name="testacct",
            category=cat,
        )
        db.session.add(acct)
        db.session.commit()
        return user, acct


def test_add_and_delete_schedule(app, client):
    user, acct = setup_finance_user(app)
    headers = auth_header(app, user.id, roles=["finance:write"])

    # add schedule
    resp = client.post(
        "/api/finance/schedule",
        json={
            "account_id": acct.id,
            "event_date": date.today().isoformat(),
            "amount": 10,
        },
        headers=headers | {"Content-Type": "application/json", "X-CSRF-Token": "test"},
    )
    assert resp.status_code == 200
    row_id = resp.get_json()["row_id"]
    assert MoneyScheduleRow.query.get(row_id)

    # forecast endpoint
    resp = client.get("/api/finance/forecast", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True

    # delete schedule
    resp = client.delete(
        f"/api/finance/schedule/{row_id}",
        headers=headers | {"Content-Type": "application/json", "X-CSRF-Token": "test"},
    )
    assert resp.status_code == 200
    assert MoneyScheduleRow.query.get(row_id) is None
