"""Reusable decorators for controllers/services."""

from __future__ import annotations

from functools import wraps
from typing import Callable, Iterable, TypeVar

from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException

from lifeos.core.auth.csrf import validate_csrf_token

F = TypeVar("F", bound=Callable)


def require_roles(required_roles: Iterable[str]):
    """Enforce that the current JWT includes the given roles."""

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args, **kwargs):  # type: ignore[misc]
            try:
                verify_jwt_in_request()
            except JWTExtendedException:
                return jsonify({"ok": False, "error": "unauthorized"}), 401
            claims = get_jwt() or {}
            roles = set(claims.get("roles") or [])
            if "admin" in roles:
                return fn(*args, **kwargs)
            if not set(required_roles).issubset(roles):
                return jsonify({"ok": False, "error": "forbidden"}), 403
            return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def csrf_protected(fn: F) -> F:
    """Validate CSRF token from header X-CSRF-Token."""

    @wraps(fn)
    def wrapper(*args, **kwargs):  # type: ignore[misc]
        if not current_app.config.get("WTF_CSRF_ENABLED", True):
            return fn(*args, **kwargs)
        token = request.headers.get("X-CSRF-Token")
        if not validate_csrf_token(token or ""):
            return jsonify({"ok": False, "error": "csrf_failed"}), 403
        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
