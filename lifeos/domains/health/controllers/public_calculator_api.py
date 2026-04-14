"""Public (unauthenticated) calorie calculator API controller."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from lifeos.domains.health.schemas.public_calculator_schemas import PublicCalculatorInput
from lifeos.domains.health.services import calculator_service
from lifeos.extensions import limiter

public_calculator_api_bp = Blueprint("public_calculator_api", __name__)


@public_calculator_api_bp.post("/calculate")
@limiter.limit("30 per minute")
def public_calculate():
    """
    Run the calorie calculator and return results.

    - No JWT required.
    - No report persistence.
    - No event emission.
    - Rate-limited to 30/min per IP.
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = PublicCalculatorInput.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    computed = calculator_service.calculate(
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        age_years=data.age_years,
        gender=data.gender,
        body_fat_pct=data.body_fat_pct,
        activity_level=data.activity_level,
        goal_type=data.goal_type,
        goal_weight_kg=data.goal_weight_kg,
        goal_timeline_months=data.goal_timeline_months,
    )

    warnings = calculator_service.get_warnings(
        gender=data.gender,
        daily_calories=computed["daily_calories"],
        tdee=computed["tdee"],
        goal_type=data.goal_type,
    )

    return jsonify({"ok": True, "result": computed, "warnings": warnings}), 200
