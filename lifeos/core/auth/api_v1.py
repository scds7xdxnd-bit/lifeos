"""API v1 authentication endpoints (tokens + identity)."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, session
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from pydantic import ValidationError

from lifeos.core.auth.auth_service import authenticate_user, issue_tokens
from lifeos.core.auth.csrf import generate_csrf_token
from lifeos.core.users.schemas import LoginRequest, serialize_user
from lifeos.extensions import limiter

api_v1_auth_bp = Blueprint("auth_api_v1", __name__)


def _jsonable_errors(exc: ValidationError) -> list[dict]:
    errors = exc.errors()
    for err in errors:
        if "ctx" in err and isinstance(err["ctx"], dict):
            err["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
    return errors


@api_v1_auth_bp.post("/login")
@limiter.limit("10/minute")
def login_v1():
    # Avoid carrying over any stale Flask session state into login.
    session.clear()
    payload = request.get_json(silent=True) or {}
    try:
        data = LoginRequest.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "bad_request", "details": _jsonable_errors(exc)}), 400

    user = authenticate_user(data.email, data.password)
    if not user:
        return jsonify({"ok": False, "error": "invalid_credentials"}), 401

    tokens = issue_tokens(user)
    return jsonify(
        {
            "ok": True,
            **tokens,
            "csrf_token": generate_csrf_token(),
            "user": serialize_user(user).model_dump(),
        }
    )


@api_v1_auth_bp.post("/refresh")
@jwt_required(refresh=True)
@limiter.limit("30/minute")
def refresh_v1():
    identity = str(get_jwt_identity())
    claims = get_jwt() or {}
    additional_claims = {}
    if "roles" in claims:
        additional_claims["roles"] = claims["roles"]
    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims or None,
    )
    return jsonify({"ok": True, "access_token": access_token, "csrf_token": generate_csrf_token()})
