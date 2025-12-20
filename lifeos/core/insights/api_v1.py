"""API v1 insights feed endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.schemas import InsightsFeedQuery
from lifeos.core.insights.services import list_insights_feed
from lifeos.core.utils.decorators import read_only_endpoint
from lifeos.readmodels.projections.review_queue import fetch_review_queue_projection

api_v1_insights_bp = Blueprint("insights_api_v1", __name__)


@api_v1_insights_bp.get("/feed")
@jwt_required()
@read_only_endpoint
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


@api_v1_insights_bp.get("/review")
@jwt_required()
@read_only_endpoint
def insights_review_queue_v1():
    """Return review-only insights (confidence_band=needs_review)."""
    user_id = int(get_jwt_identity())
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    items = fetch_review_queue_projection(user_id, limit=limit, offset=offset)
    payload = [
        {
            "id": rec.id,
            "insight_type": rec.kind,
            "message": rec.message,
            "severity": rec.severity,
            "event_type": rec.event_type,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "data": rec.data or {},
        }
        for rec in items
    ]
    return jsonify({"ok": True, "items": payload, "limit": limit, "offset": offset})
