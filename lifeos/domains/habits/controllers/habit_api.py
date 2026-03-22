"""Habits JSON API controllers (thin, schema-validated)."""

from __future__ import annotations

import logging
import time
from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.observability import record_habits_analytics_latency
from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.habits import services as habit_services
from lifeos.domains.habits.models.habit_models import Habit, HabitLog, HabitStat
from lifeos.domains.habits.schemas.habit_schemas import (
    HabitCreate,
    HabitDetailResponse,
    HabitHeatmapEntry,
    HabitHeatmapResponse,
    HabitHistoryEntry,
    HabitHistoryResponse,
    HabitLogCreate,
    HabitLogResponse,
    HabitLogUpdate,
    HabitStatsResponse,
    HabitSummaryResponse,
    HabitUpdate,
)

logger = logging.getLogger(__name__)

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
            scheduled_time=item["habit"].scheduled_time,
            difficulty=item["habit"].difficulty,
            is_active=item["habit"].is_active,
            count=item["count"],
            last_logged_date=item["last_logged_date"],
            completed_today=item["completed_today"],
            current_streak=item.get("current_streak", 0),
            completion_rate_30d=item.get("completion_rate_30d"),
            today_log_id=item.get("today_log_id"),
            last_7_days=item.get("last_7_days", []),
        ).model_dump(mode="json")
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
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
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
        scheduled_time=habit.scheduled_time,
        difficulty=habit.difficulty,
        is_active=habit.is_active,
        stats=detail["stats"],
        logs=[
            HabitLogResponse(
                id=log.id,
                habit_id=log.habit_id,
                logged_date=log.logged_date,
                value=log.value,
                note=log.note,
            )
            for log in detail["logs"]
        ],
    )
    return jsonify({"ok": True, "habit": resp.model_dump(mode="json")})


@habit_api_bp.patch("/<int:habit_id>")
@jwt_required()
@csrf_protected
def update_habit(habit_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = HabitUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    habit = habit_services.update_habit(
        user_id,
        habit_id,
        **{k: v for k, v in data.model_dump().items() if v is not None},
    )
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
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
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
    return jsonify(
        {
            "ok": True,
            "log": HabitLogResponse(
                id=log.id,
                habit_id=log.habit_id,
                logged_date=log.logged_date,
                value=log.value,
                note=log.note,
            ).model_dump(mode="json"),
        }
    )


@habit_api_bp.patch("/logs/<int:log_id>")
@jwt_required()
@csrf_protected
def update_log(log_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = HabitLogUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    log = habit_services.update_habit_log(
        user_id, log_id, **{k: v for k, v in data.model_dump().items() if v is not None}
    )
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


# --- HAB-013: Analytics endpoints ---


@habit_api_bp.get("/<int:habit_id>/stats")
@jwt_required()
def habit_stats(habit_id: int):
    t0 = time.monotonic()
    user_id = int(get_jwt_identity())
    stat = HabitStat.query.filter_by(habit_id=habit_id, user_id=user_id).first()
    if not stat:
        return jsonify({"ok": False, "error": "not_found"}), 404
    resp = HabitStatsResponse(
        current_streak=stat.current_streak,
        longest_streak=stat.longest_streak,
        completion_rate_30d=stat.completion_rate_30d,
        total_logs=stat.total_logs,
        last_logged_at=stat.last_logged_at,
    )
    duration = time.monotonic() - t0
    record_habits_analytics_latency("stats", duration)
    if duration > 0.1:
        logger.warning("Slow query: /habits/%s/stats took %.3fs", habit_id, duration)
    return jsonify({"ok": True, "stats": resp.model_dump(mode="json")})


_HISTORY_RANGES = {"7d": 7, "30d": 30, "90d": 90}


def _get_owned_habit_or_none(user_id: int, habit_id: int) -> Habit | None:
    return Habit.query.filter_by(id=habit_id, user_id=user_id).first()


@habit_api_bp.get("/<int:habit_id>/history")
@jwt_required()
def habit_history(habit_id: int):
    t0 = time.monotonic()
    user_id = int(get_jwt_identity())
    habit = _get_owned_habit_or_none(user_id, habit_id)
    if not habit:
        return jsonify({"ok": False, "error": "not_found"}), 404
    range_key = request.args.get("range", "7d")
    days = _HISTORY_RANGES.get(range_key, 7)
    today = date.today()
    start = today - timedelta(days=days - 1)

    logs = (
        HabitLog.query.filter_by(habit_id=habit_id, user_id=user_id)
        .filter(HabitLog.logged_date >= start, HabitLog.logged_date <= today)
        .all()
    )
    log_map = {lg.logged_date: lg for lg in logs}

    entries = []
    for i in range(days):
        d = start + timedelta(days=i)
        lg = log_map.get(d)
        entries.append(
            HabitHistoryEntry(
                date=d,
                logged=lg is not None,
                value=float(lg.value) if lg and lg.value is not None else None,
            )
        )

    resp = HabitHistoryResponse(entries=entries, range=range_key)
    duration = time.monotonic() - t0
    record_habits_analytics_latency("history", duration)
    if duration > 0.1:
        logger.warning("Slow query: /habits/%s/history took %.3fs", habit_id, duration)
    return jsonify({"ok": True, "history": resp.model_dump(mode="json")})


@habit_api_bp.get("/<int:habit_id>/heatmap")
@jwt_required()
def habit_heatmap(habit_id: int):
    t0 = time.monotonic()
    user_id = int(get_jwt_identity())
    habit = _get_owned_habit_or_none(user_id, habit_id)
    if not habit:
        return jsonify({"ok": False, "error": "not_found"}), 404
    year = request.args.get("year", date.today().year, type=int)
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    logs = (
        HabitLog.query.filter_by(habit_id=habit_id, user_id=user_id)
        .filter(HabitLog.logged_date >= start, HabitLog.logged_date <= end)
        .all()
    )
    logged_dates = {lg.logged_date for lg in logs}

    entries = []
    d = start
    while d <= end:
        entries.append(HabitHeatmapEntry(date=d, logged=d in logged_dates))
        d += timedelta(days=1)

    resp = HabitHeatmapResponse(year=year, entries=entries)
    duration = time.monotonic() - t0
    record_habits_analytics_latency("heatmap", duration)
    if duration > 0.1:
        logger.warning("Slow query: /habits/%s/heatmap took %.3fs", habit_id, duration)
    return jsonify({"ok": True, "heatmap": resp.model_dump(mode="json")})
