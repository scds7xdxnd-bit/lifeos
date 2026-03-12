import pytest
from datetime import date

from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.unit

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.extensions import db
from lifeos.domains.finance.models.receivable_models import (
    ReceivableTracker,
    ReceivableManualEntry,
)


def _auth_headers(app, user_id: int):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"roles": ["finance:write"]})
    return {"Authorization": f"Bearer {token}", "X-CSRF-Token": "test"}


def _create_user(app):
    with app.app_context():
        user = User(email="recv@test.com", password_hash=hash_password("pw"))
        db.session.add(user)
        db.session.commit()
        return user


def test_create_and_log_receivable(app, client):
    user = _create_user(app)
    headers = _auth_headers(app, user.id)

    resp = client.post(
        "/api/finance/receivables",
        json={
            "counterparty": "Client",
            "principal": 1000,
            "start_date": date.today().isoformat(),
        },
        headers=headers,
    )
    assert resp.status_code == 201
    tracker_id = resp.get_json()["tracker"]["id"]

    resp = client.post(
        f"/api/finance/receivables/{tracker_id}/entries",
        json={"amount": 100, "entry_date": date.today().isoformat(), "memo": "partial"},
        headers=headers,
    )
    assert resp.status_code == 201
    entry_id = resp.get_json()["entry"]["id"]

    with app.app_context():
        assert ReceivableTracker.query.get(tracker_id)
        assert ReceivableManualEntry.query.get(entry_id)

    resp = client.get(f"/api/finance/receivables/{tracker_id}/entries", headers=headers)
    assert resp.status_code == 200
    items = resp.get_json()["items"]
    assert len(items) == 1


def test_update_and_delete_receivable(app, client):
    user = _create_user(app)
    headers = _auth_headers(app, user.id)

    created = client.post(
        "/api/finance/receivables",
        json={
            "counterparty": "Delete Me Co",
            "principal": 250,
            "start_date": date.today().isoformat(),
        },
        headers=headers,
    )
    assert created.status_code == 201
    tracker_id = created.get_json()["tracker"]["id"]

    updated = client.patch(
        f"/api/finance/receivables/{tracker_id}",
        json={"counterparty": "Updated Co"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.get_json()["tracker"]["counterparty"] == "Updated Co"

    deleted = client.delete(f"/api/finance/receivables/{tracker_id}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.get_json() == {"ok": True}
