"""User controllers (API + HTML pages)."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.core.users.schemas import UserCreateRequest, UserResponse, UserUpdateRequest, serialize_user
from lifeos.core.users.services import create_user, get_user, update_preferences, update_user

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


@user_pages_bp.get("/profile")
@jwt_required(optional=True)
def profile_page():
    user = get_user(get_jwt_identity()) if get_jwt_identity() else None
    return render_template("profile/profile.html", user=user)
