"""Auth HTTP controllers (API only)."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, request, session
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from pydantic import ValidationError

from lifeos.core.auth.auth_service import (
    authenticate_user,
    issue_tokens,
    register_user,
    request_password_reset,
    request_username_reminder,
    reset_password,
    revoke_refresh_token,
)
from lifeos.core.auth.csrf import generate_csrf_token
from lifeos.core.auth.schemas import (
    ForgotPasswordRequest,
    ForgotUsernameRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from lifeos.core.users.schemas import LoginRequest, serialize_user
from lifeos.core.utils.decorators import csrf_protected
from lifeos.extensions import limiter

auth_bp = Blueprint("auth_api", __name__)
auth_pages_bp = Blueprint("auth_pages", __name__)


def _jsonable_errors(exc: ValidationError) -> list[dict]:
    errors = exc.errors()
    for err in errors:
        if "ctx" in err and isinstance(err["ctx"], dict):
            err["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
    return errors


@auth_bp.post("/register")
@limiter.limit("5/minute")
def register():
    payload = request.get_json(silent=True) or {}
    try:
        data = RegisterRequest.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "bad_request", "details": _jsonable_errors(exc)}),
            400,
        )
    try:
        result = register_user(
            data,
            auto_issue_tokens=current_app.config.get("AUTO_LOGIN_ON_REGISTER", False),
        )
    except ValueError as exc:
        code = str(exc)
        if code == "email_already_exists":
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "registration_failed"}), 400

    user = result["user"]
    resp = {"ok": True, "user": serialize_user(user).model_dump()}
    if "access_token" in result:
        resp.update(
            {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token"),
                "csrf_token": generate_csrf_token(),
            }
        )
    return jsonify(resp)


@auth_bp.post("/login")
@limiter.limit("10/minute")
def login():
    # Ensure login is stateless even if a stale Flask session cookie is present.
    session.clear()
    payload = request.get_json(silent=True) or {}
    try:
        data = LoginRequest.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "bad_request", "details": _jsonable_errors(exc)}),
            400,
        )
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


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
@limiter.limit("30/minute")
def refresh():
    identity = str(get_jwt_identity())
    new_access = create_access_token(identity=identity)
    return jsonify({"ok": True, "access_token": new_access})


@auth_bp.post("/logout")
@jwt_required(refresh=True)
@csrf_protected
def logout():
    jti = get_jwt().get("jti")
    if jti:
        revoke_refresh_token(jti)
    return jsonify({"ok": True})


@auth_bp.get("/me")
@jwt_required()
def me():
    from lifeos.core.users.models import User  # local import to avoid cycle

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "user": serialize_user(user).model_dump()})


@auth_bp.post("/forgot-username")
@limiter.limit("5/minute")
def forgot_username():
    payload = request.get_json(silent=True) or {}
    try:
        data = ForgotUsernameRequest.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "bad_request", "details": _jsonable_errors(exc)}),
            400,
        )
    request_username_reminder(data)
    return jsonify({"ok": True})


@auth_bp.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password():
    payload = request.get_json(silent=True) or {}
    try:
        data = ForgotPasswordRequest.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "bad_request", "details": _jsonable_errors(exc)}),
            400,
        )
    request_password_reset(data)
    return jsonify({"ok": True})


@auth_bp.post("/reset-password")
@limiter.limit("5/minute")
def reset_password_route():
    payload = request.get_json(silent=True) or {}
    try:
        data = ResetPasswordRequest.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "bad_request", "details": _jsonable_errors(exc)}),
            400,
        )
    try:
        reset_password(data)
    except ValueError:
        return jsonify({"ok": False, "error": "invalid_token"}), 400
    return jsonify({"ok": True})


@auth_pages_bp.get("/login")
def login_page():
    # Read-mode login page; keeps API unchanged.
    return render_template("auth/login.html")
