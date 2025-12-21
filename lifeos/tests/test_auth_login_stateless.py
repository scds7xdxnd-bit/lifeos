from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.extensions import db


def test_login_clears_stale_flask_session(app, client):
    """Login should ignore and clear any existing Flask session cookie."""
    with app.app_context():
        user = User(email="stateless@example.com", password_hash=hash_password("demo12345"))
        db.session.add(user)
        db.session.commit()

    # Seed a stale Flask session cookie
    with client.session_transaction() as sess:
        sess["stale"] = "1"

    resp = client.post("/auth/login", json={"email": "stateless@example.com", "password": "demo12345"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True

    with client.session_transaction() as sess:
        assert "stale" not in sess
