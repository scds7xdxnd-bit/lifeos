"""Reusable decorators for controllers/services."""

from __future__ import annotations

from functools import wraps
from typing import Callable, Iterable, TypeVar

from flask import current_app, jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
from sqlalchemy import event as sa_event

from lifeos.core.auth.csrf import get_session_csrf_token, get_session_id, validate_csrf_token
from lifeos.extensions import db

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
    """Validate CSRF token from header X-CSRF-Token.

    JWT Bearer auth is inherently CSRF-safe (browsers cannot auto-attach
    Authorization headers in cross-site requests), so we skip session-based
    CSRF validation when a valid JWT is present.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):  # type: ignore[misc]
        if not current_app.config.get("WTF_CSRF_ENABLED", True):
            return fn(*args, **kwargs)

        auth_header = request.headers.get("Authorization", "")

        # JWT Bearer tokens are not vulnerable to CSRF — the browser cannot
        # automatically attach them.  Skip session-based CSRF for API callers
        # that authenticate via JWT.
        if auth_header.startswith("Bearer "):
            try:
                verify_jwt_in_request()
                return fn(*args, **kwargs)
            except JWTExtendedException:
                pass  # fall through to normal CSRF validation

        token = request.headers.get("X-CSRF-Token")
        if not validate_csrf_token(token or ""):
            expected = get_session_csrf_token()
            request_id = request.headers.get("X-Request-Id") or request.headers.get("X-Request-ID")
            auth_header_present = bool(auth_header)
            current_app.logger.warning(
                "csrf_failed",
                extra={
                    "event": "csrf_failed",
                    "expected_source": "session",
                    "session_id": get_session_id(),
                    "expected_csrf": expected,
                    "received_csrf": token,
                    "auth_header_present": auth_header_present,
                    "request_id": request_id,
                    "build_id": current_app.config.get("BUILD_ID"),
                    "path": request.path,
                    "method": request.method,
                },
            )
            return jsonify({"ok": False, "error": "csrf_failed"}), 403
        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def read_only_endpoint(fn: F) -> F:
    """Ensure read-only endpoints do not mutate persistence state."""

    @wraps(fn)
    def wrapper(*args, **kwargs):  # type: ignore[misc]
        try:
            from lifeos.core.observability import (
                record_contract_violation,
                record_projection_check,
                record_projection_error,
            )
        except Exception:
            record_contract_violation = None
            record_projection_check = None
            record_projection_error = None

        if record_projection_check:
            record_projection_check()

        if db.session.new or db.session.dirty or db.session.deleted:
            db.session.rollback()
            if record_projection_error:
                record_projection_error()
            if record_contract_violation:
                record_contract_violation()
            return jsonify({"ok": False, "error": "read_only_violation"}), 409

        did_flush = {"value": False}

        def _mark_flush(session, flush_context, instances):
            if session.new or session.dirty or session.deleted:
                did_flush["value"] = True

        sa_event.listen(db.session, "before_flush", _mark_flush)
        try:
            response = fn(*args, **kwargs)
        finally:
            sa_event.remove(db.session, "before_flush", _mark_flush)

        if did_flush["value"] or db.session.new or db.session.dirty or db.session.deleted:
            db.session.rollback()
            if record_projection_error:
                record_projection_error()
            if record_contract_violation:
                record_contract_violation()
            return jsonify({"ok": False, "error": "read_only_violation"}), 409
        return response

    setattr(wrapper, "_read_only", True)
    return wrapper  # type: ignore[return-value]
