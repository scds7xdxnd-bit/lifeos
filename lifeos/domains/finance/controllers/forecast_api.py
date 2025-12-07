"""Forecast and schedule API."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.finance.schemas.finance_schemas import ForecastParams, ScheduleRowCreate, ScheduleRowUpdate
from lifeos.domains.finance.services.forecast_service import generate_forecast
from lifeos.domains.finance.services.schedule_service import add_schedule_row, delete_schedule_row, recompute_daily_balances, update_schedule_row

forecast_api_bp = Blueprint("finance_forecast_api", __name__)


@forecast_api_bp.get("/forecast")
@jwt_required()
def get_forecast():
    user_id = int(get_jwt_identity())
    try:
        params = ForecastParams.model_validate(request.args or {})
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "forecast": generate_forecast(user_id, params.days)})


@forecast_api_bp.post("/schedule")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def add_schedule():
    payload = request.get_json(silent=True) or {}
    try:
        data = ScheduleRowCreate.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    row = add_schedule_row(int(get_jwt_identity()), data.account_id, data.event_date, data.amount, data.memo)
    return jsonify({"ok": True, "row_id": row.id})


@forecast_api_bp.post("/schedule/recompute")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def recompute():
    user_id = int(get_jwt_identity())
    balances = recompute_daily_balances(user_id)
    return jsonify({"ok": True, "balances": balances})


@forecast_api_bp.patch("/schedule/<int:row_id>")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def patch_schedule(row_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = ScheduleRowUpdate.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    row = update_schedule_row(
        int(get_jwt_identity()),
        row_id,
        **{k: v for k, v in data.model_dump().items() if v is not None},
    )
    if not row:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@forecast_api_bp.delete("/schedule/<int:row_id>")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def delete_schedule(row_id: int):
    if not delete_schedule_row(int(get_jwt_identity()), row_id):
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})
