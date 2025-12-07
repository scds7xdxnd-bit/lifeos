"""Health API controllers."""

from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.health import services
from lifeos.domains.health.mappers import map_biometric, map_nutrition_log, map_workout
from lifeos.domains.health.schemas.health_schemas import (
    BiometricCreate,
    BiometricListFilter,
    DailySummaryResponse,
    NutritionCreate,
    NutritionListFilter,
    WorkoutCreate,
    WorkoutListFilter,
    WeeklySummaryResponse,
)

health_api_bp = Blueprint("health_api", __name__)


def _parse_query(schema_cls):
    data = {k: v for k, v in request.args.items()}
    try:
        return schema_cls.model_validate(data), None
    except ValidationError as exc:
        return None, exc


@health_api_bp.get("/biometrics")
@jwt_required()
def list_biometrics():
    user_id = int(get_jwt_identity())
    params, err = _parse_query(BiometricListFilter)
    if err:
        return jsonify({"ok": False, "error": "validation_error", "details": err.errors()}), 400
    items, total = services.list_biometrics(
        user_id,
        start_date=params.start_date,
        end_date=params.end_date,
        page=params.page,
        per_page=params.per_page,
    )
    pages = (total + params.per_page - 1) // params.per_page if params.per_page else 1
    return jsonify({"ok": True, "items": [map_biometric(b) for b in items], "page": params.page, "pages": pages, "total": total})


@health_api_bp.post("/biometrics")
@jwt_required()
@csrf_protected
def create_biometric():
    payload = request.get_json(silent=True) or {}
    try:
        data = BiometricCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    try:
        biometric = services.create_biometric_entry(user_id, date_value=data.date, weight=data.weight, body_fat_pct=data.body_fat_pct, resting_hr=data.resting_hr, energy_level=data.energy_level, stress_level=data.stress_level, notes=data.notes)
    except ValueError as exc:
        if str(exc) == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "biometric": map_biometric(biometric)}), 201


@health_api_bp.get("/workouts")
@jwt_required()
def list_workouts():
    user_id = int(get_jwt_identity())
    params, err = _parse_query(WorkoutListFilter)
    if err:
        return jsonify({"ok": False, "error": "validation_error", "details": err.errors()}), 400
    items, total = services.list_workouts(
        user_id,
        start_date=params.start_date,
        end_date=params.end_date,
        page=params.page,
        per_page=params.per_page,
    )
    pages = (total + params.per_page - 1) // params.per_page if params.per_page else 1
    return jsonify({"ok": True, "items": [map_workout(w) for w in items], "page": params.page, "pages": pages, "total": total})


@health_api_bp.post("/workouts")
@jwt_required()
@csrf_protected
def create_workout():
    payload = request.get_json(silent=True) or {}
    try:
        data = WorkoutCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    try:
        workout = services.create_workout(
            user_id,
            date_value=data.date,
            workout_type=data.workout_type,
            duration_minutes=data.duration_minutes,
            intensity=data.intensity,
            calories_est=data.calories_est,
            notes=data.notes,
        )
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "workout": map_workout(workout)}), 201


@health_api_bp.get("/nutrition")
@jwt_required()
def list_nutrition():
    user_id = int(get_jwt_identity())
    params, err = _parse_query(NutritionListFilter)
    if err:
        return jsonify({"ok": False, "error": "validation_error", "details": err.errors()}), 400
    items, total = services.list_nutrition_logs(
        user_id,
        start_date=params.start_date,
        end_date=params.end_date,
        page=params.page,
        per_page=params.per_page,
    )
    pages = (total + params.per_page - 1) // params.per_page if params.per_page else 1
    return jsonify({"ok": True, "items": [map_nutrition_log(n) for n in items], "page": params.page, "pages": pages, "total": total})


@health_api_bp.post("/nutrition")
@jwt_required()
@csrf_protected
def create_nutrition():
    payload = request.get_json(silent=True) or {}
    try:
        data = NutritionCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    try:
        log = services.create_nutrition_log(
            user_id,
            date_value=data.date,
            meal_type=data.meal_type,
            items=data.items,
            calories_est=data.calories_est,
            quality_score=data.quality_score,
        )
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "nutrition": map_nutrition_log(log)}), 201


@health_api_bp.get("/summary/daily")
@jwt_required()
def daily_summary():
    user_id = int(get_jwt_identity())
    date_str = request.args.get("date")
    try:
        summary_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    summary = services.get_daily_summary(user_id, summary_date)
    payload = DailySummaryResponse.model_validate(
        {
            "date": summary["date"],
            "biometric": map_biometric(summary["biometric"]) if summary["biometric"] else None,
            "workouts": summary["workouts"],
            "nutrition": summary["nutrition"],
            "energy_level": summary["energy_level"],
            "stress_level": summary["stress_level"],
        }
    )
    return jsonify({"ok": True, "summary": payload.model_dump()})


@health_api_bp.get("/summary/weekly")
@jwt_required()
def weekly_summary():
    user_id = int(get_jwt_identity())
    start_str = request.args.get("start")
    try:
        week_start = date.fromisoformat(start_str) if start_str else date.today()
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    summary = services.get_weekly_summary(user_id, week_start)
    payload = WeeklySummaryResponse.model_validate(
        {
            "week_start": summary["week_start"],
            "week_end": summary["week_end"],
            "biometric": summary["biometric"],
            "workouts": summary["workouts"],
            "nutrition": summary["nutrition"],
        }
    )
    return jsonify({"ok": True, "summary": payload.model_dump()})
