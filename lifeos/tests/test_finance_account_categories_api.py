from __future__ import annotations

import pytest
from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.core.auth.models import Role
from lifeos.extensions import db


def _prime_csrf(client) -> str:
    token = "test-csrf-token"
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _auth_headers(app, user_id: int, with_csrf: bool = False):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"roles": ["finance:write"]})
    headers = {"Authorization": f"Bearer {token}"}
    if with_csrf:
        headers["X-CSRF-Token"] = "test-csrf-token"
    return headers


def _ensure_role(app):
    with app.app_context():
        if not Role.query.filter_by(name="finance:write").first():
            db.session.add(Role(name="finance:write"))
            db.session.commit()


def _create_user(app):
    with app.app_context():
        user = User(email="cat@example.com", password_hash=hash_password("secret"))
        db.session.add(user)
        db.session.commit()
        return user


def test_create_and_list_account_categories(app, client):
    _ensure_role(app)
    user = _create_user(app)
    _prime_csrf(client)
    headers = _auth_headers(app, user.id, with_csrf=True)

    resp = client.post(
        "/api/finance/account-categories",
        json={"base_type": "asset", "name": "Operations", "is_default": True},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True
    cat_id = body["category"]["id"]

    list_resp = client.get(
        "/api/finance/account-categories?base_type=asset&include_system=false",
        headers=_auth_headers(app, user.id),
    )
    assert list_resp.status_code == 200
    categories = list_resp.get_json()["categories"]
    assert any(c["id"] == cat_id for c in categories)


def test_create_account_with_new_category_name(app, client):
    _ensure_role(app)
    user = _create_user(app)
    _prime_csrf(client)
    headers = _auth_headers(app, user.id, with_csrf=True)

    resp = client.post(
        "/api/finance/accounts",
        json={
            "name": "Project Cash",
            "account_type": "asset",
            "category_name_new": "Projects",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True
    assert body["account"]["category_id"] is not None
