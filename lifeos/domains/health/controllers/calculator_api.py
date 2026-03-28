"""Calorie calculator API controller."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.health import services
from lifeos.domains.health.mappers import map_calorie_report
from lifeos.domains.health.schemas.calculator_schemas import CalculatorInput, ReportListParams

calculator_api_bp = Blueprint("calculator_api", __name__)


@calculator_api_bp.post("/calculate")
@jwt_required()
@csrf_protected
def calculate_and_save():
    """
    Run the calorie calculator, persist the report, and return the result.
    Also saves height/age/gender to UserPreference if save_profile is true.
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = CalculatorInput.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    user_id = int(get_jwt_identity())

    computed = services.calculate(
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

    warnings = services.get_warnings(
        gender=data.gender,
        daily_calories=computed["daily_calories"],
        tdee=computed["tdee"],
        goal_type=data.goal_type,
    )

    report = services.create_report(
        user_id,
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        age_years=data.age_years,
        gender=data.gender,
        body_fat_pct=data.body_fat_pct,
        activity_level=data.activity_level,
        goal_type=data.goal_type,
        goal_weight_kg=data.goal_weight_kg,
        goal_timeline_months=data.goal_timeline_months,
        computed=computed,
    )

    if data.save_profile:
        services.save_health_profile(
            user_id,
            height_cm=data.height_cm,
            age_years=data.age_years,
            gender=data.gender,
        )

    return (
        jsonify(
            {
                "ok": True,
                "report": map_calorie_report(report),
                "warnings": warnings,
            }
        ),
        201,
    )


@calculator_api_bp.get("/reports")
@jwt_required()
def list_reports():
    """List all calorie reports for the authenticated user."""
    user_id = int(get_jwt_identity())
    try:
        params = ReportListParams.model_validate(dict(request.args))
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    items, total = services.list_reports(user_id, page=params.page, per_page=params.per_page)
    pages = (total + params.per_page - 1) // params.per_page if params.per_page else 1
    return jsonify(
        {
            "ok": True,
            "reports": [map_calorie_report(r) for r in items],
            "page": params.page,
            "pages": pages,
            "total": total,
        }
    )


@calculator_api_bp.get("/reports/latest")
@jwt_required()
def latest_report():
    """Get the latest calorie report. Used by optimizer for constraint auto-population."""
    user_id = int(get_jwt_identity())
    report = services.get_latest_report(user_id)
    if not report:
        return jsonify({"ok": True, "report": None})
    return jsonify({"ok": True, "report": map_calorie_report(report)})


@calculator_api_bp.get("/reports/<int:report_id>")
@jwt_required()
def get_report(report_id: int):
    """Get a single report by ID."""
    user_id = int(get_jwt_identity())
    report = services.get_report(user_id, report_id)
    if not report:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "report": map_calorie_report(report)})


@calculator_api_bp.delete("/reports/<int:report_id>")
@jwt_required()
@csrf_protected
def delete_report(report_id: int):
    """Delete a calorie report by ID, scoped to authenticated user."""
    user_id = int(get_jwt_identity())
    deleted = services.delete_report(user_id, report_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True}), 200


@calculator_api_bp.patch("/reports/<int:report_id>")
@jwt_required()
@csrf_protected
def update_report(report_id: int):
    """Re-calculate and update an existing report with new inputs."""
    payload = request.get_json(silent=True) or {}
    try:
        data = CalculatorInput.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    user_id = int(get_jwt_identity())
    report = services.update_report(
        user_id,
        report_id,
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
    if not report:
        return jsonify({"ok": False, "error": "not_found"}), 404

    warnings = services.get_warnings(
        gender=data.gender,
        daily_calories=report.daily_calories,
        tdee=report.tdee,
        goal_type=data.goal_type,
    )
    return jsonify({"ok": True, "report": map_calorie_report(report), "warnings": warnings})


@calculator_api_bp.get("/prefill")
@jwt_required()
def get_prefill():
    """
    Get auto-fill data for the calculator form:
    - Latest biometric (weight, body_fat_pct)
    - Saved health profile (height, age, gender)
    """
    user_id = int(get_jwt_identity())
    biometric = services.get_latest_biometric(user_id)
    profile = services.get_health_profile(user_id)
    return jsonify(
        {
            "ok": True,
            "biometric": biometric,
            "profile": profile,
        }
    )
