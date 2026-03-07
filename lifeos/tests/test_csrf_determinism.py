from __future__ import annotations

import pytest
from flask_jwt_extended import create_access_token

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.extensions import db


@pytest.fixture(autouse=True)
def _enable_csrf(app):
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    return app


def _create_user(app) -> User:
    with app.app_context():
        user = User(email="csrf@example.com", password_hash=hash_password("secret"))
        db.session.add(user)
        db.session.commit()
        return user


def _prime_csrf(client, token: str = "test-csrf-token") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _set_access_cookie(app, client, user_id: int, roles: list[str] | None = None) -> str:
    with app.app_context():
        claims = {"roles": roles or []}
        access = create_access_token(identity=str(user_id), additional_claims=claims)
    cookie_name = app.config.get("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
    client.set_cookie(cookie_name, access, domain="localhost")
    return access


def _access_cookie_value(app, client) -> str:
    cookie_name = app.config.get("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
    cookie = client.get_cookie(cookie_name)
    if not cookie:
        raise AssertionError("access token cookie not set")
    return cookie.value


def _bootstrap_csrf(client) -> str:
    resp = client.get("/api/bootstrap")
    assert resp.status_code == 200
    body = resp.get_json() or {}
    assert body.get("ok") is True
    assert body.get("csrf_token")
    return body["csrf_token"]


def _api_login(client, email: str, password: str) -> dict:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    body = resp.get_json() or {}
    assert resp.status_code == 200
    assert body.get("ok") is True
    assert body.get("access_token")
    return body


def _session_cookie_value(app, client) -> str:
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    cookie = client.get_cookie(cookie_name)
    if not cookie:
        raise AssertionError("session cookie not set")
    return cookie.value


def test_csrf_mismatch_forbidden(app, client):
    user = _create_user(app)
    _set_access_cookie(app, client, user.id)
    _prime_csrf(client, token="expected-token")
    headers = {"X-CSRF-Token": "wrong-token"}

    resp = client.post("/api/habits", json={"name": "Mismatch"}, headers=headers)
    assert resp.status_code == 403
    body = resp.get_json()
    assert body["error"] == "csrf_failed"


def test_csrf_match_allows_write(app, client):
    user = _create_user(app)
    _set_access_cookie(app, client, user.id)
    csrf_token = _prime_csrf(client, token="expected-token")
    headers = {"X-CSRF-Token": csrf_token}

    resp = client.post("/api/habits", json={"name": "Match"}, headers=headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True


def test_csrf_survives_restart_same_secret(app, client):
    user = _create_user(app)
    _set_access_cookie(app, client, user.id)
    csrf_token = _prime_csrf(client, token="stable-token")
    session_cookie = _session_cookie_value(app, client)

    new_client = app.test_client()
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    new_client.set_cookie(cookie_name, session_cookie, domain="localhost")
    access_cookie = _access_cookie_value(app, client)
    access_cookie_name = app.config.get("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
    new_client.set_cookie(access_cookie_name, access_cookie, domain="localhost")

    resp = new_client.post("/api/habits", json={"name": "Restart ok"}, headers={"X-CSRF-Token": csrf_token})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True


def test_csrf_persists_across_reload_after_login(app, client):
    user = _create_user(app)
    login_body = _api_login(client, user.email, "secret")
    access_cookie_name = app.config.get("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
    client.set_cookie(access_cookie_name, login_body["access_token"], domain="localhost")
    csrf_token = _bootstrap_csrf(client)
    headers = {"X-CSRF-Token": csrf_token}

    first = client.post("/api/habits", json={"name": "Reload ok"}, headers=headers)
    assert first.status_code == 201

    session_cookie = _session_cookie_value(app, client)
    access_cookie = _access_cookie_value(app, client)
    reload_client = app.test_client()
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    reload_client.set_cookie(cookie_name, session_cookie, domain="localhost")
    reload_client.set_cookie(access_cookie_name, access_cookie, domain="localhost")

    reload_csrf = _bootstrap_csrf(reload_client)
    reload_headers = {"X-CSRF-Token": reload_csrf}
    second = reload_client.post("/api/habits", json={"name": "Reload ok 2"}, headers=reload_headers)
    assert second.status_code == 201


def test_csrf_persists_across_reload_new_user(app, client):
    email = "csrf-new@example.com"
    register = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "CSRF New",
            "timezone": "UTC",
        },
    )
    assert register.status_code == 200

    login_body = _api_login(client, email, "secret123")
    access_cookie_name = app.config.get("JWT_ACCESS_COOKIE_NAME", "access_token_cookie")
    client.set_cookie(access_cookie_name, login_body["access_token"], domain="localhost")
    csrf_token = _bootstrap_csrf(client)
    headers = {"X-CSRF-Token": csrf_token}

    first = client.post("/api/habits", json={"name": "New reload ok"}, headers=headers)
    assert first.status_code == 201

    session_cookie = _session_cookie_value(app, client)
    access_cookie = _access_cookie_value(app, client)
    reload_client = app.test_client()
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    reload_client.set_cookie(cookie_name, session_cookie, domain="localhost")
    reload_client.set_cookie(access_cookie_name, access_cookie, domain="localhost")

    reload_csrf = _bootstrap_csrf(reload_client)
    reload_headers = {"X-CSRF-Token": reload_csrf}
    second = reload_client.post("/api/habits", json={"name": "New reload ok 2"}, headers=reload_headers)
    assert second.status_code == 201


def test_build_identity_exposed(app, client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["build_id"]

    ping_resp = client.get("/api/v1/ping")
    assert ping_resp.status_code == 200
    assert ping_resp.headers.get("X-LifeOS-Build")


def test_cross_domain_write_sanity(app, client):
    user = _create_user(app)
    csrf_token = _prime_csrf(client, token="domain-token")
    roles = ["finance:write", "calendar:write"]
    _set_access_cookie(app, client, user.id, roles=roles)
    headers = {"X-CSRF-Token": csrf_token, "Content-Type": "application/json"}

    finance_resp = client.post(
        "/api/finance/accounts/inline",
        json={"name": "QA Account", "account_type": "asset", "account_subtype": "bank"},
        headers=headers,
    )
    assert finance_resp.status_code in {200, 201}
    assert finance_resp.get_json()["ok"] is True

    habit_resp = client.post("/api/habits", json={"name": "QA Habit"}, headers=headers)
    assert habit_resp.status_code == 201

    health_resp = client.post("/api/health/biometrics", json={"weight": 70.5}, headers=headers)
    assert health_resp.status_code == 201

    skill_resp = client.post("/api/skills", json={"name": "QA Skill"}, headers=headers)
    assert skill_resp.status_code == 201

    project_resp = client.post("/api/projects", json={"name": "QA Project"}, headers=headers)
    assert project_resp.status_code == 201

    person_resp = client.post("/api/relationships/people", json={"name": "QA Person"}, headers=headers)
    assert person_resp.status_code == 201

    journal_resp = client.post("/api/journal", json={"body": "QA entry"}, headers=headers)
    assert journal_resp.status_code == 201

    calendar_resp = client.post(
        "/api/calendar/events",
        json={"title": "QA Event", "start_time": "2026-02-08T09:00:00"},
        headers=headers,
    )
    assert calendar_resp.status_code == 201


def test_same_origin_session_csrf_allows_post_without_authorization(app, client):
    user = _create_user(app)
    _set_access_cookie(app, client, user.id)
    csrf_token = _bootstrap_csrf(client)
    headers = {"Origin": "http://localhost", "X-CSRF-Token": csrf_token}

    resp = client.post("/api/habits", json={"name": "Session only"}, headers=headers)
    assert resp.status_code == 201


def test_same_origin_session_csrf_blocks_mixed_authorization(app, client):
    user = _create_user(app)
    _set_access_cookie(app, client, user.id)
    csrf_token = _bootstrap_csrf(client)
    with app.app_context():
        access = create_access_token(identity=str(user.id))
    headers = {
        "Origin": "http://localhost",
        "X-CSRF-Token": csrf_token,
        "Authorization": f"Bearer {access}",
    }

    resp = client.post("/api/habits", json={"name": "Mixed auth"}, headers=headers)
    assert resp.status_code == 403
    body = resp.get_json()
    assert body.get("error") == "mixed_auth_forbidden"
