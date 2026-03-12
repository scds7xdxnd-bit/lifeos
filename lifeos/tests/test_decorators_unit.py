from __future__ import annotations

import builtins
from uuid import uuid4

import pytest
from flask_jwt_extended.exceptions import JWTExtendedException

from lifeos.core.users.models import User
from lifeos.core.utils import decorators
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def test_require_roles_returns_401_when_jwt_verification_fails(app, monkeypatch):
    @decorators.require_roles({"admin"})
    def _handler():
        return {"ok": True}

    def _raise():
        raise JWTExtendedException("missing token")

    monkeypatch.setattr(decorators, "verify_jwt_in_request", _raise)

    with app.test_request_context():
        response, status = _handler()

    assert status == 401
    assert response.get_json() == {"ok": False, "error": "unauthorized"}


def test_require_roles_allows_non_admin_when_required_roles_present(app, monkeypatch):
    @decorators.require_roles({"finance:write"})
    def _handler():
        return {"ok": True}

    monkeypatch.setattr(decorators, "verify_jwt_in_request", lambda: None)
    monkeypatch.setattr(decorators, "get_jwt", lambda: {"roles": ["finance:write"]})

    with app.test_request_context():
        response = _handler()

    assert response == {"ok": True}


def test_csrf_protected_passes_through_when_csrf_disabled(app):
    @decorators.csrf_protected
    def _handler():
        return {"ok": True}

    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_request_context(headers={"X-CSRF-Token": "ignored"}):
        response = _handler()

    assert response == {"ok": True}


def test_csrf_protected_allows_valid_token(app, monkeypatch):
    @decorators.csrf_protected
    def _handler():
        return {"ok": True}

    app.config["WTF_CSRF_ENABLED"] = True
    monkeypatch.setattr(decorators, "validate_csrf_token", lambda token: token == "valid")

    with app.test_request_context(headers={"X-CSRF-Token": "valid"}):
        response = _handler()

    assert response == {"ok": True}


def test_read_only_endpoint_blocks_when_session_already_dirty(app):
    @decorators.read_only_endpoint
    def _handler():
        return {"ok": True}

    email = f"readonly-dirty-{uuid4().hex}@example.com"
    with app.test_request_context():
        db.session.add(User(email=email, password_hash="x"))
        response, status = _handler()
        assert status == 409
        assert response.get_json() == {"ok": False, "error": "read_only_violation"}

    assert User.query.filter_by(email=email).first() is None


def test_read_only_endpoint_handles_missing_observability_module(app, monkeypatch):
    @decorators.read_only_endpoint
    def _handler():
        return {"ok": True}

    original_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "lifeos.core.observability":
            raise ImportError("forced import failure")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    with app.test_request_context():
        response = _handler()

    assert response == {"ok": True}
