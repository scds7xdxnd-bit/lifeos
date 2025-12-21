"""Money schedule API."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.finance.schemas.finance_schemas import ScheduleRowCreate
from lifeos.domains.finance.services.schedule_service import (
    add_schedule_row,
    recompute_daily_balances,
)

schedule_api_bp = Blueprint("finance_schedule_api", __name__)


@schedule_api_bp.post("/schedule")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def add_schedule():
    payload = request.get_json(silent=True) or {}
    try:
        data = ScheduleRowCreate.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    row = add_schedule_row(
        int(get_jwt_identity()),
        data.account_id,
        data.event_date,
        data.amount,
        data.memo,
    )
    return jsonify({"ok": True, "row_id": row.id})


@schedule_api_bp.post("/schedule/recompute")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def recompute():
    balances = recompute_daily_balances(int(get_jwt_identity()))
    return jsonify({"ok": True, "balances": balances})
