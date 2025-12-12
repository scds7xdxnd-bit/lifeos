from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.extensions import db


def test_demo_login_returns_success_not_server_error(app, client):
    """
    Regression guard: login should not 500 when email domain is reserved (demo@lifeos.test).
    """
    with app.app_context():
        user = User(email="demo@lifeos.test", password_hash=hash_password("demo12345"))
        db.session.add(user)
        db.session.commit()

    resp = client.post(
        "/auth/login", json={"email": "demo@lifeos.test", "password": "demo12345"}
    )
    assert (
        resp.status_code == 200
    )  # currently 500 due to EmailStr validation in serialize_user
    body = resp.get_json()
    assert body["ok"] is True
