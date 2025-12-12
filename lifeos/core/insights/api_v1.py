"""API v1 insights feed endpoints."""

from __future__ import annotations

from datetime import datetime, time
from math import ceil

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.core.insights.models import InsightRecord

api_v1_insights_bp = Blueprint("insights_api_v1", __name__)


def _parse_date(value: str):
    try:
        return datetime.fromisoformat(value).date()
    except Exception:
        return None


@api_v1_insights_bp.get("/feed")
@jwt_required()
def insights_feed_v1():
    """Return paginated insights for the current user with optional filters."""
    user_id = int(get_jwt_identity())
    domain = request.args.get("domain")
    severity = request.args.get("severity")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)

    query = InsightRecord.query.filter(InsightRecord.user_id == user_id)

    if domain:
        query = query.filter(InsightRecord.event_type.like(f"{domain}.%"))
    if severity:
        query = query.filter(InsightRecord.severity == severity)
    if start_date:
        start = _parse_date(start_date)
        if start:
            start_dt = datetime.combine(start, time.min)
            query = query.filter(InsightRecord.created_at >= start_dt)
    if end_date:
        end = _parse_date(end_date)
        if end:
            end_dt = datetime.combine(end, time.max)
            query = query.filter(InsightRecord.created_at <= end_dt)

    query = query.order_by(InsightRecord.created_at.desc())
    total = query.count()
    pages = ceil(total / per_page) if total else 0
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    def _serialize(rec: InsightRecord) -> dict:
        return {
            "id": rec.id,
            "user_id": rec.user_id,
            "message": rec.message,
            "insight_type": rec.kind,
            "severity": rec.severity,
            "data": rec.data or {},
            "source_event_type": rec.event_type,
            "source_event_id": rec.event_id,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
        }

    return jsonify(
        {
            "ok": True,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "items": [_serialize(rec) for rec in items],
        }
    )
