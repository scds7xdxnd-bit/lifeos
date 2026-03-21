"""User controllers (API + HTML pages)."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.users.schemas import (
    OnboardingStepRequest,
    UserCreateRequest,
    UserUpdateRequest,
    serialize_user,
)
from lifeos.core.users.services import (
    create_user,
    get_onboarding_status,
    get_user,
    save_onboarding_step,
    update_preferences,
    update_user,
)

user_api_bp = Blueprint("user_api", __name__)
user_pages_bp = Blueprint("user_pages", __name__)


@user_api_bp.post("")
def api_create_user():
    payload = request.get_json(silent=True) or {}
    data = UserCreateRequest.model_validate(payload)
    user = create_user(data)
    return jsonify({"ok": True, "user": serialize_user(user).model_dump()}), 201


@user_api_bp.get("/me")
@jwt_required()
def api_me():
    user = get_user(get_jwt_identity())
    if not user:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "user": serialize_user(user).model_dump()})


@user_api_bp.patch("/<int:user_id>")
@jwt_required()
def api_update_user(user_id: int):
    user = get_user(user_id)
    if not user:
        return jsonify({"ok": False, "error": "not_found"}), 404
    payload = request.get_json(silent=True) or {}
    data = UserUpdateRequest.model_validate(payload)
    user = update_user(user, data)
    return jsonify({"ok": True, "user": serialize_user(user).model_dump()})


@user_api_bp.post("/<int:user_id>/preferences")
@jwt_required()
def api_update_preferences(user_id: int):
    user = get_user(user_id)
    if not user:
        return jsonify({"ok": False, "error": "not_found"}), 404
    prefs = request.get_json(silent=True) or {}
    update_preferences(user, prefs)
    return jsonify({"ok": True, "preferences": prefs})


@user_api_bp.get("/me/onboarding-status")
@jwt_required()
def api_onboarding_status():
    user = get_user(get_jwt_identity())
    if not user:
        return jsonify({"ok": False, "error": "not_found"}), 404
    status = get_onboarding_status(user)
    return jsonify({"ok": True, **status})


@user_api_bp.post("/me/onboarding")
@jwt_required()
def api_save_onboarding():
    user = get_user(get_jwt_identity())
    if not user:
        return jsonify({"ok": False, "error": "not_found"}), 404
    payload = request.get_json(silent=True) or {}
    try:
        data = OnboardingStepRequest.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "errors": exc.errors()}), 422
    save_onboarding_step(user, data.step, data.data)
    if data.step == "complete":
        from lifeos.core.events.event_service import log_event

        log_event("user.onboarding.completed", {"payload_version": 1}, user_id=user.id)
    return jsonify({"ok": True, "step": data.step})


@user_pages_bp.get("/profile")
@jwt_required(optional=True)
def profile_page():
    user = get_user(get_jwt_identity()) if get_jwt_identity() else None
    return render_template("profile/profile.html", user=user)
