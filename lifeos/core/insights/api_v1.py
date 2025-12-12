"""API v1 insights feed endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.schemas import InsightsFeedQuery
from lifeos.core.insights.services import list_insights_feed

api_v1_insights_bp = Blueprint("insights_api_v1", __name__)


@api_v1_insights_bp.get("/feed")
@jwt_required()
def insights_feed_v1():
    """Return paginated insights for the current user with optional filters."""
    user_id = int(get_jwt_identity())
    try:
        filters = InsightsFeedQuery.model_validate(request.args)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    items, total, page, pages = list_insights_feed(user_id, filters)
    per_page = filters.per_page

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
