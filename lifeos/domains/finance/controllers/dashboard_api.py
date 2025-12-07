"""Finance dashboard API."""

from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.domains.finance.services.dashboard_service import get_dashboard

dashboard_api_bp = Blueprint("finance_dashboard_api", __name__)


@dashboard_api_bp.get("/dashboard")
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    data = get_dashboard(user_id)
    return jsonify({"ok": True, **data})
