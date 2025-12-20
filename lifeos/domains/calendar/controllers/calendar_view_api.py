"""Calendar view-semantic APIs (day/week/month) and ledger."""

from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.domains.calendar.schemas import (
    DayViewParams,
    LedgerParams,
    MonthViewParams,
    WeekViewParams,
)
from lifeos.domains.calendar.services.calendar_service import (
    get_day_view,
    get_ledger,
    get_month_view,
    get_week_view,
)
from lifeos.extensions import limiter
from lifeos.core.utils.decorators import read_only_endpoint

calendar_view_api_bp = Blueprint("calendar_view_api", __name__)


def _json_error(exc: ValidationError):
    return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()})


@calendar_view_api_bp.get("/day")
@jwt_required()
@limiter.limit("240/minute")
@read_only_endpoint
def day_view():
    """Deterministic day view: returns all events overlapping the day."""
    user_id = int(get_jwt_identity())
    try:
        params = DayViewParams.model_validate({"date_value": request.args.get("date")})
    except ValidationError as exc:
        return _json_error(exc), 400
    target = params.date_value or date.today()
    data = get_day_view(user_id, target)
    return (
        jsonify(
            {
                "ok": True,
                "window_start": data["window_start"],
                "window_end": data["window_end"],
                "events": data["events"],
            }
        ),
        200,
    )


@calendar_view_api_bp.get("/week")
@jwt_required()
@limiter.limit("240/minute")
@read_only_endpoint
def week_view():
    """Deterministic week view: 7-day window from provided start date."""
    user_id = int(get_jwt_identity())
    try:
        params = WeekViewParams.model_validate({"start": request.args.get("start")})
    except ValidationError as exc:
        return _json_error(exc), 400
    start_date = params.start or date.today()
    data = get_week_view(user_id, start_date)
    return (
        jsonify(
            {
                "ok": True,
                "window_start": data["window_start"],
                "window_end": data["window_end"],
                "events": data["events"],
            }
        ),
        200,
    )


@calendar_view_api_bp.get("/month")
@jwt_required()
@limiter.limit("240/minute")
@read_only_endpoint
def month_view():
    """Deterministic month view with backend-owned spillover days."""
    user_id = int(get_jwt_identity())
    try:
        params = MonthViewParams.model_validate({"year": request.args.get("year"), "month": request.args.get("month")})
    except ValidationError as exc:
        return _json_error(exc), 400
    data = get_month_view(user_id, params.year, params.month)
    return (
        jsonify(
            {
                "ok": True,
                "window_start": data["window_start"],
                "window_end": data["window_end"],
                "spillover_days": data["spillover_days"],
                "events": data["events"],
            }
        ),
        200,
    )


@calendar_view_api_bp.get("/ledger")
@jwt_required()
@limiter.limit("240/minute")
@read_only_endpoint
def ledger_view():
    """Chronological ledger anchored at today (or provided anchor) with cursor pagination."""
    user_id = int(get_jwt_identity())
    try:
        params = LedgerParams.model_validate(
            {
                "anchor": request.args.get("anchor"),
                "direction": request.args.get("direction") or "backward",
                "limit": request.args.get("limit"),
                "cursor": request.args.get("cursor"),
            }
        )
    except ValidationError as exc:
        return _json_error(exc), 400

    anchor = params.anchor or date.today()
    data = get_ledger(
        user_id=user_id,
        anchor_date=anchor,
        direction=params.direction,
        limit=params.limit,
        cursor=params.cursor,
    )
    return (
        jsonify(
            {
                "ok": True,
                "anchor": data["anchor"],
                "direction": data["direction"],
                "cursor": data["cursor"],
                "next_cursor": data["next_cursor"],
                "prev_cursor": data["prev_cursor"],
                "events": data["events"],
            }
        ),
        200,
    )
