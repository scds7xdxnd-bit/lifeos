"""Habits JSON API controllers (thin, schema-validated)."""

from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.habits.schemas.habit_schemas import (
    HabitCreate,
    HabitDetailResponse,
    HabitLogCreate,
    HabitLogResponse,
    HabitLogUpdate,
    HabitSummaryResponse,
    HabitUpdate,
)
from lifeos.domains.habits import services as habit_services

habit_api_bp = Blueprint("habit_api", __name__)


@habit_api_bp.get("")
@jwt_required()
def list_habits():
    user_id = int(get_jwt_identity())
    habits = habit_services.list_habits(user_id)
    payload = [
        HabitSummaryResponse(
            id=item["habit"].id,
            name=item["habit"].name,
            description=item["habit"].description,
            schedule_type=item["habit"].schedule_type,
            target_count=item["habit"].target_count,
            time_of_day=item["habit"].time_of_day,
            difficulty=item["habit"].difficulty,
            is_active=item["habit"].is_active,
            count=item["count"],
            last_logged_date=item["last_logged_date"],
            completed_today=item["completed_today"],
        ).model_dump()
        for item in habits
    ]
    return jsonify({"ok": True, "habits": payload})


@habit_api_bp.post("")
@jwt_required()
@csrf_protected
def create_habit():
    payload = request.get_json(silent=True) or {}
    try:
        data = HabitCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    try:
        habit = habit_services.create_habit(user_id=user_id, **data.model_dump())
    except ValueError as exc:
        code = str(exc)
        if code == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "habit_id": habit.id}), 201


@habit_api_bp.get("/<int:habit_id>")
@jwt_required()
def habit_detail(habit_id: int):
    user_id = int(get_jwt_identity())
    detail = habit_services.get_habit_detail(user_id, habit_id)
    if not detail:
        return jsonify({"ok": False, "error": "not_found"}), 404
    habit = detail["habit"]
    resp = HabitDetailResponse(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        schedule_type=habit.schedule_type,
        target_count=habit.target_count,
        time_of_day=habit.time_of_day,
        difficulty=habit.difficulty,
        is_active=habit.is_active,
        stats=detail["stats"],
        logs=[HabitLogResponse(id=log.id, habit_id=log.habit_id, logged_date=log.logged_date, value=log.value, note=log.note) for log in detail["logs"]],
    )
    return jsonify({"ok": True, "habit": resp.model_dump()})


@habit_api_bp.patch("/<int:habit_id>")
@jwt_required()
@csrf_protected
def update_habit(habit_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = HabitUpdate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    habit = habit_services.update_habit(user_id, habit_id, **{k: v for k, v in data.model_dump().items() if v is not None})
    if not habit:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@habit_api_bp.post("/<int:habit_id>/deactivate")
@jwt_required()
@csrf_protected
def deactivate_habit(habit_id: int):
    user_id = int(get_jwt_identity())
    habit = habit_services.deactivate_habit(user_id, habit_id)
    if not habit:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@habit_api_bp.delete("/<int:habit_id>")
@jwt_required()
@csrf_protected
def delete_habit(habit_id: int):
    user_id = int(get_jwt_identity())
    deleted = habit_services.delete_habit(user_id, habit_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@habit_api_bp.post("/<int:habit_id>/logs")
@jwt_required()
@csrf_protected
def create_log(habit_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = HabitLogCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    try:
        log = habit_services.log_habit_completion(user_id, habit_id, **data.model_dump())
    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        if code == "inactive":
            return jsonify({"ok": False, "error": "inactive"}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "log": HabitLogResponse(id=log.id, habit_id=log.habit_id, logged_date=log.logged_date, value=log.value, note=log.note).model_dump()})


@habit_api_bp.patch("/logs/<int:log_id>")
@jwt_required()
@csrf_protected
def update_log(log_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = HabitLogUpdate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    log = habit_services.update_habit_log(user_id, log_id, **{k: v for k, v in data.model_dump().items() if v is not None})
    if not log:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@habit_api_bp.delete("/logs/<int:log_id>")
@jwt_required()
@csrf_protected
def delete_log(log_id: int):
    user_id = int(get_jwt_identity())
    deleted = habit_services.delete_habit_log(user_id, log_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})
