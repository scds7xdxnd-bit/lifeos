"""Admin/debug endpoints (non-production only)."""

from __future__ import annotations

import dataclasses

from flask import Blueprint, abort, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.core.insights.substrate_models import Interpretation, TimelineEvent
from lifeos.core.insights.telemetry import insight_telemetry
from lifeos.core.utils.decorators import require_roles

admin_debug_bp = Blueprint("admin_debug", __name__)


@admin_debug_bp.get("/admin/debug/insight-telemetry")
@jwt_required()
@require_roles({"admin"})
def get_insight_telemetry():
    """Expose an in-memory snapshot of insight telemetry for debugging."""
    env = (current_app.config.get("ENV") or "").lower()
    if env == "production" and not current_app.debug:
        abort(404)

    snapshot = insight_telemetry.snapshot()
    return jsonify({"ok": True, "telemetry": dataclasses.asdict(snapshot)})


@admin_debug_bp.get("/admin/debug/timeline-events")
@jwt_required()
@require_roles({"admin"})
def debug_timeline_events():
    """Admin view of recent timeline events."""
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    user_id_param = request.args.get("user_id")
    user_id = int(user_id_param) if user_id_param else int(get_jwt_identity())

    events = (
        TimelineEvent.query.filter_by(user_id=user_id)
        .order_by(TimelineEvent.timestamp_start.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    payload = [
        {
            "id": e.id,
            "event_id": e.event_id,
            "user_id": e.user_id,
            "timestamp_start": e.timestamp_start.isoformat(),
            "timestamp_end": e.timestamp_end.isoformat() if e.timestamp_end else None,
            "source_domain": e.source_domain,
            "event_type": e.event_type,
            "source_object_ref": e.source_object_ref,
            "ingested_at": e.ingested_at.isoformat(),
        }
        for e in events
    ]
    return jsonify({"ok": True, "items": payload, "limit": limit, "offset": offset})


@admin_debug_bp.get("/admin/debug/interpretations")
@jwt_required()
@require_roles({"admin"})
def debug_interpretations():
    """Admin view of proposal interpretations."""
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    user_id_param = request.args.get("user_id")
    user_id = int(user_id_param) if user_id_param else int(get_jwt_identity())

    items = (
        Interpretation.query.filter_by(user_id=user_id)
        .order_by(Interpretation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    payload = [
        {
            "id": item.id,
            "user_id": item.user_id,
            "interpretation_type": item.interpretation_type,
            "status": item.status,
            "confidence": float(item.confidence),
            "created_at": item.created_at.isoformat(),
            "decided_at": item.decided_at.isoformat() if item.decided_at else None,
            "input_event_ids": item.input_event_ids,
        }
        for item in items
    ]
    return jsonify({"ok": True, "items": payload, "limit": limit, "offset": offset})
