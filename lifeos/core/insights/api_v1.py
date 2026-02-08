"""API v1 insights feed endpoints."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.auth.csrf import get_session_csrf_token, get_session_id, validate_csrf_token
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.personalization import personalization_enabled
from lifeos.core.insights.schemas import (
    ALLOWED_INSIGHT_FEEDBACK_ACTIONS,
    ALLOWED_INSIGHT_FEEDBACK_REASONS,
    InsightFeedbackRequest,
    InsightsFeedQuery,
    InterpretationDecisionRequest,
)
from lifeos.core.insights.services import list_insights_feed
from lifeos.core.insights.substrate_models import Interpretation, UserFeedbackEvent
from lifeos.core.insights.substrate_service import decide_interpretation, list_interpretations
from lifeos.core.read_cache import read_cache
from lifeos.core.utils.decorators import csrf_protected, read_only_endpoint
from lifeos.extensions import db
from lifeos.readmodels.projections.review_queue import fetch_review_queue_projection

api_v1_insights_bp = Blueprint("insights_api_v1", __name__)
INSIGHTS_READ_CACHE_SCOPE = "insights.reads"
PROPOSALS_ROUTE = "/proposals"
PROPOSAL_DECISION_ROUTE = "/proposals/<int:interpretation_id>"


@api_v1_insights_bp.get("/feed")
@jwt_required()
@read_only_endpoint
def insights_feed_v1():
    """Return paginated insights for the current user with optional filters."""
    user_id = int(get_jwt_identity())
    try:
        raw_args = request.args.to_dict(flat=False)
        payload = {key: (vals if len(vals) > 1 else vals[0]) for key, vals in raw_args.items()}
        filters = InsightsFeedQuery.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    cache_key = {
        "view": "feed",
        "page": filters.page,
        "per_page": filters.per_page,
        "domain": sorted(filters.domain or []),
        "severity": filters.severity,
        "status": filters.status,
        "start_date": filters.start_date.isoformat() if filters.start_date else None,
        "end_date": filters.end_date.isoformat() if filters.end_date else None,
        "personalization": personalization_enabled(),
    }
    cached = read_cache.get(INSIGHTS_READ_CACHE_SCOPE, user_id, cache_key)
    if cached is not None:
        return jsonify(cached)

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

    payload = {
        "ok": True,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "items": [_serialize(rec) for rec in items],
    }
    read_cache.set(INSIGHTS_READ_CACHE_SCOPE, user_id, cache_key, payload)
    return jsonify(payload)


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
    cache_key = {"view": "review_queue", "limit": limit, "offset": offset}
    cached = read_cache.get(INSIGHTS_READ_CACHE_SCOPE, user_id, cache_key)
    if cached is not None:
        return jsonify(cached)
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
    response = {"ok": True, "items": payload, "limit": limit, "offset": offset}
    read_cache.set(INSIGHTS_READ_CACHE_SCOPE, user_id, cache_key, response)
    return jsonify(response)


@api_v1_insights_bp.get(PROPOSALS_ROUTE)
@jwt_required()
@read_only_endpoint
def list_proposals_v1():
    """Return proposal interpretations for the current user."""
    user_id = int(get_jwt_identity())
    status = request.args.get("status")
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    items = list_interpretations(user_id, status=status, limit=limit, offset=offset)
    payload = [_serialize_interpretation(item) for item in items]
    return jsonify({"ok": True, "items": payload, "limit": limit, "offset": offset})


@api_v1_insights_bp.patch(PROPOSAL_DECISION_ROUTE)
@jwt_required()
@csrf_protected
def decide_proposal_v1(interpretation_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = InterpretationDecisionRequest.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    correction = None
    if data.person_id or data.method or data.notes:
        correction = {"person_id": data.person_id, "method": data.method, "notes": data.notes}

    try:
        interpretation = decide_interpretation(
            int(get_jwt_identity()),
            interpretation_id,
            action=data.action,
            correction=correction,
        )
    except ValueError as exc:
        code = str(exc)
        if code in {"not_found", "invalid_action", "invalid_proposal"}:
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify({"ok": True, "interpretation": _serialize_interpretation(interpretation)})


@api_v1_insights_bp.post("/feedback")
@jwt_required()
def record_insight_feedback_v1():
    if not _feedback_csrf_allowed():
        return jsonify({"ok": False, "error": "csrf_failed"}), 403
    payload = request.get_json(silent=True) or {}
    if "action" not in payload and "feedback_type" in payload:
        payload["action"] = payload.get("feedback_type")
    if "action" not in payload and "action_type" in payload:
        payload["action"] = payload.get("action_type")

    try:
        data = InsightFeedbackRequest.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    user_id = int(get_jwt_identity())
    action = (data.action or data.feedback_type or "").strip().lower()
    if action not in ALLOWED_INSIGHT_FEEDBACK_ACTIONS:
        return jsonify({"ok": False, "error": "invalid_action"}), 400

    insight_id = data.insight_id
    insight_type = (data.insight_type or "").strip() or None
    insight_record = None
    if insight_id is not None:
        insight_record = InsightRecord.query.filter_by(id=insight_id, user_id=user_id).first()
        if not insight_record:
            return jsonify({"ok": False, "error": "not_found"}), 404
        insight_type = insight_type or insight_record.kind
    if not insight_id and not insight_type:
        return jsonify({"ok": False, "error": "invalid_insight"}), 400

    context = data.context or {}
    reason = (data.reason or data.feedback_reason or "").strip().lower() or None
    if reason and reason not in ALLOWED_INSIGHT_FEEDBACK_REASONS:
        return jsonify({"ok": False, "error": "invalid_reason"}), 400

    session_id = (data.session_id or request.headers.get("X-Session-Id") or "").strip() or None
    request_id = (data.request_id or request.headers.get("X-Request-Id") or str(uuid.uuid4())).strip()
    idempotency_key = (
        data.idempotency_key or request.headers.get("Idempotency-Key") or ""
    ).strip() or _default_idempotency_key(user_id, insight_id, insight_type, action, context)

    fingerprint = _feedback_fingerprint(
        user_id=user_id,
        insight_id=insight_id,
        insight_type=insight_type,
        action=action,
        context=context,
        idempotency_key=idempotency_key,
    )
    existing = UserFeedbackEvent.query.filter_by(
        user_id=user_id,
        feedback_type=action,
        fingerprint=fingerprint,
    ).first()
    if existing:
        return jsonify({"ok": True, "feedback_id": existing.id, "deduped": True}), 200

    feedback_payload = {
        "insight_id": insight_id,
        "insight_type": insight_type,
        "action": action,
        "reason": reason,
        "context": context,
        "client_timestamp": data.timestamp,
        "idempotency_key": idempotency_key,
        "session_id": session_id,
        "request_id": request_id,
    }
    feedback = UserFeedbackEvent(
        user_id=user_id,
        interpretation_id=None,
        feedback_type=action,
        fingerprint=fingerprint,
        payload=feedback_payload,
    )
    db.session.add(feedback)
    db.session.flush()

    event_payload = {
        "feedback_id": feedback.id,
        "insight_id": insight_id,
        "insight_type": insight_type,
        "action": action,
        "reason": reason,
        "context": context,
        "client_timestamp": data.timestamp,
        "session_id": session_id,
        "request_id": request_id,
        "idempotency_key": idempotency_key,
        "recorded_at": datetime.utcnow().isoformat(),
    }
    db.session.add(EventRecord(event_type=_feedback_event_type(action), payload=event_payload, user_id=user_id))
    db.session.commit()
    return jsonify({"ok": True, "feedback_id": feedback.id}), 201


def _serialize_interpretation(item: Interpretation) -> dict:
    return {
        "id": item.id,
        "interpretation_type": item.interpretation_type,
        "input_event_ids": item.input_event_ids,
        "proposed_writes": item.proposed_writes,
        "applied_writes": item.applied_writes,
        "confidence": float(item.confidence),
        "evidence": item.evidence,
        "status": item.status,
        "reversible_plan": item.reversible_plan,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "decided_at": item.decided_at.isoformat() if item.decided_at else None,
    }


def _feedback_fingerprint(
    *,
    user_id: int,
    insight_id: int | None,
    insight_type: str | None,
    action: str,
    context: dict,
    idempotency_key: str | None = None,
) -> str:
    payload = {
        "user_id": user_id,
        "insight_id": insight_id,
        "insight_type": insight_type,
        "action": action,
        "window_end": context.get("window_end"),
        "window_days": context.get("window_days"),
        "idempotency_key": idempotency_key,
    }
    if context:
        context_hash = hashlib.sha256(json.dumps(context, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        payload["context_hash"] = context_hash
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _feedback_csrf_allowed() -> bool:
    if not current_app.config.get("WTF_CSRF_ENABLED", True):
        return True
    token = request.headers.get("X-CSRF-Token")
    if validate_csrf_token(token or ""):
        return True
    current_app.logger.warning(
        "csrf_failed",
        extra={
            "event": "csrf_failed",
            "session_id": get_session_id(),
            "expected_csrf": get_session_csrf_token(),
            "received_csrf": token,
            "build_id": current_app.config.get("BUILD_ID"),
            "path": request.path,
            "method": request.method,
        },
    )
    return False


def _feedback_event_type(action: str) -> str:
    mapping = {
        "viewed": "insight_viewed",
        "dismiss": "insight_dismissed",
        "dismissed": "insight_dismissed",
        "snooze": "insight_dismissed",
        "saved": "insight_saved",
        "shared": "insight_shared",
        "feedback_positive": "insight_feedback_positive",
        "feedback_negative": "insight_feedback_negative",
        "reported_issue": "insight_reported_issue",
        "act": "insight_feedback_positive",
    }
    return mapping.get(action, "insight_dismissed")


def _default_idempotency_key(
    user_id: int,
    insight_id: int | None,
    insight_type: str | None,
    action: str,
    context: dict,
) -> str:
    payload = {
        "user_id": user_id,
        "insight_id": insight_id,
        "insight_type": insight_type,
        "action": action,
        "window_end": context.get("window_end"),
        "window_days": context.get("window_days"),
    }
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
