"""Admin-only auth controllers (session admin reset scaffold)."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.auth.schemas import SessionAdminResetRequest
from lifeos.core.auth.session_services import SessionLifecycleService
from lifeos.core.utils.decorators import csrf_protected, require_roles

admin_auth_bp = Blueprint("auth_admin_api", __name__)


@admin_auth_bp.post("/session/reset")
@jwt_required()
@require_roles(["admin"])
@csrf_protected
def admin_reset_sessions():
    """Admin-triggered session reset (scope: all or single)."""
    payload = request.get_json(silent=True) or {}
    try:
        data = SessionAdminResetRequest.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    initiator = int(get_jwt_identity())
    service = SessionLifecycleService()
    try:
        result = service.admin_reset(
            user_id=data.user_id,
            session_scope=data.session_scope,
            session_id=data.session_id,
            reason=data.reason,
            initiated_by_admin_id=initiator,
        )
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        if str(exc) == "reason_required":
            return jsonify({"ok": False, "error": "reason_required"}), 400
        raise

    return jsonify({"ok": True, **result})
