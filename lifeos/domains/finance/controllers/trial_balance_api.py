"""Trial balance API (read-only)."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.domains.finance.schemas.finance_schemas import PeriodBalanceFilter, TrialBalanceFilter
from lifeos.domains.finance.services import trial_balance_service

trial_balance_api_bp = Blueprint("trial_balance_api", __name__)


@trial_balance_api_bp.get("/trial_balance")
@jwt_required()
def trial_balance():
    payload = request.args or {}
    try:
        data = TrialBalanceFilter.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    result = trial_balance_service.trial_balance_view(user_id, as_of=data.as_of)
    return jsonify({"ok": True, "accounts": result.get("accounts", []), "categories": result.get("categories", [])})


@trial_balance_api_bp.get("/trial_balance/period")
@jwt_required()
def period_balance():
    payload = request.args or {}
    try:
        data = PeriodBalanceFilter.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    totals = trial_balance_service.period_balance(user_id, start_date=data.start, end_date=data.end)
    return jsonify({"ok": True, "totals": totals})


@trial_balance_api_bp.get("/trial_balance/monthly")
@jwt_required()
def monthly_rollup():
    user_id = int(get_jwt_identity())
    rollup = trial_balance_service.monthly_rollup(user_id)
    return jsonify({"ok": True, "months": rollup})
