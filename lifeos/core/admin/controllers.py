"""Admin/debug endpoints (non-production only)."""

from __future__ import annotations

import dataclasses

from flask import Blueprint, abort, current_app, jsonify
from flask_jwt_extended import jwt_required

from lifeos.core.insights.telemetry import insight_telemetry
from lifeos.core.utils.decorators import require_roles

admin_debug_bp = Blueprint("admin_debug", __name__)


@admin_debug_bp.get("/admin/debug/insight-telemetry")
@jwt_required()
@require_roles({"admin"})
def get_insight_telemetry():
    """Expose an in-memory snapshot of insight telemetry for debugging."""
    env = (current_app.config.get("ENV") or "").lower()
    if env == "production" and not current_app.debug:
        abort(404)

    snapshot = insight_telemetry.snapshot()
    return jsonify({"ok": True, "telemetry": dataclasses.asdict(snapshot)})
