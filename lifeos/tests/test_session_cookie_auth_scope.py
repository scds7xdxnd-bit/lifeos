from __future__ import annotations

import pytest
from flask_jwt_extended import create_access_token

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.extensions import db

pytestmark = pytest.mark.integration


def _create_user(app, email: str = "session-scope@example.com", password: str = "secret123") -> User:
    with app.app_context():
        user = User(email=email, password_hash=hash_password(password))
        db.session.add(user)
        db.session.commit()
        return user


def _login_cookie_session(client, email: str, password: str) -> dict:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    body = resp.get_json() or {}
    assert body.get("ok") is True
    return body


def _copy_session_cookie(app, source_client, target_client) -> None:
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    cookie = source_client.get_cookie(cookie_name)
    assert cookie is not None
    target_client.set_cookie(cookie_name, cookie.value, domain="localhost")


def test_cookie_only_auth_acceptance_flow(app, client):
    app.config["WTF_CSRF_ENABLED"] = True
    user = _create_user(app)
    _login_cookie_session(client, user.email, "secret123")

    me_resp = client.get("/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.get_json()["ok"] is True

    day_resp = client.get("/api/v1/calendar/day?date=2026-03-04")
    assert day_resp.status_code == 200
    assert day_resp.get_json()["ok"] is True

    reload_client = app.test_client()
    _copy_session_cookie(app, client, reload_client)

    me_after_reload = reload_client.get("/auth/me")
    assert me_after_reload.status_code == 200
    assert me_after_reload.get_json()["ok"] is True

    bootstrap = client.get("/api/bootstrap")
    assert bootstrap.status_code == 200
    csrf_token = bootstrap.get_json()["csrf_token"]
    write_resp = reload_client.post(
        "/api/habits",
        json={"name": "Cookie Auth Habit"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert write_resp.status_code == 201
    assert write_resp.get_json()["ok"] is True


def test_mixed_auth_forbidden_on_scope_routes(app, client):
    user = _create_user(app, email="mixed-auth-scope@example.com")
    _login_cookie_session(client, user.email, "secret123")
    with app.app_context():
        access = create_access_token(identity=str(user.id), additional_claims={"roles": []})

    headers = {"Authorization": f"Bearer {access}", "Origin": "http://localhost"}
    me_resp = client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 403
    assert me_resp.get_json() == {"ok": False, "error": "mixed_auth_forbidden"}
