from __future__ import annotations

import pytest
from flask_jwt_extended import create_access_token

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.extensions import db

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _enable_csrf(app):
    app.config["WTF_CSRF_ENABLED"] = True
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


def _auth_headers(
    app,
    user_id: int,
    csrf_token: str | None = None,
    roles: list[str] | None = None,
) -> dict[str, str]:
    with app.app_context():
        claims = {"roles": roles or []}
        access = create_access_token(identity=str(user_id), additional_claims=claims)
    headers = {"Authorization": f"Bearer {access}"}
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token
    return headers


def _session_cookie_value(app, client) -> str:
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    cookie = client.get_cookie(cookie_name)
    if not cookie:
        raise AssertionError("session cookie not set")
    return cookie.value


def test_csrf_mismatch_forbidden(app, client):
    user = _create_user(app)
    _prime_csrf(client, token="expected-token")
    headers = _auth_headers(app, user.id, csrf_token="wrong-token")

    resp = client.post("/api/habits", json={"name": "Mismatch"}, headers=headers)
    assert resp.status_code == 403
    body = resp.get_json()
    assert body["error"] == "csrf_failed"


def test_csrf_match_allows_write(app, client):
    user = _create_user(app)
    csrf_token = _prime_csrf(client, token="expected-token")
    headers = _auth_headers(app, user.id, csrf_token=csrf_token)

    resp = client.post("/api/habits", json={"name": "Match"}, headers=headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True


def test_csrf_survives_restart_same_secret(app, client):
    user = _create_user(app)
    csrf_token = _prime_csrf(client, token="stable-token")
    session_cookie = _session_cookie_value(app, client)
    headers = _auth_headers(app, user.id, csrf_token=csrf_token)

    new_client = app.test_client()
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    new_client.set_cookie(cookie_name, session_cookie, domain="localhost")

    resp = new_client.post("/api/habits", json={"name": "Restart ok"}, headers=headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True


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
    headers = {
        **_auth_headers(app, user.id, csrf_token=csrf_token, roles=roles),
        "Content-Type": "application/json",
    }

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
