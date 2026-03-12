"""Focused Inquiry v1 API endpoints."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.insights.inquiry_schemas import InquiryCreateRequest, InquiryRefineRequest
from lifeos.core.insights.inquiry_service import (
    INQUIRY_READ_CACHE_SCOPE,
    create_inquiry,
    get_inquiry,
    list_inquiries,
    refine_inquiry,
)
from lifeos.core.observability import record_inquiry_error
from lifeos.core.read_cache import read_cache
from lifeos.core.utils.decorators import csrf_protected, read_only_endpoint

api_v1_inquiry_bp = Blueprint("inquiry_api_v1", __name__)


def _phase6_enabled() -> bool:
    return bool(current_app.config.get("ENABLE_PHASE6_FOCUSED_INQUIRY", False))


def _feature_disabled_response():
    return jsonify({"ok": False, "error": "not_found"}), 404


@api_v1_inquiry_bp.post("")
@api_v1_inquiry_bp.post("/")
@jwt_required()
@csrf_protected
def create_inquiry_v1():
    if not _phase6_enabled():
        return _feature_disabled_response()

    payload = request.get_json(silent=True) or {}
    try:
        data = InquiryCreateRequest.model_validate(payload)
    except ValidationError as exc:
        record_inquiry_error("create", "validation_error")
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    except ValueError as exc:
        record_inquiry_error("create", "validation_error")
        return jsonify({"ok": False, "error": str(exc)}), 400

    user_id = int(get_jwt_identity())
    try:
        inquiry, version, deduped = create_inquiry(user_id, data)
    except Exception:
        record_inquiry_error("create", "internal_error")
        raise
    response = {
        "ok": True,
        "deduped": deduped,
        "inquiry_id": inquiry.id,
        "version_id": version.id,
        "inquiry": {
            "id": inquiry.id,
            "question": inquiry.question,
            "lens": inquiry.lens,
            "domain": inquiry.primary_domain,
            "domains": inquiry.domains,
            "timeframe": {
                "start": inquiry.timeframe_start.date().isoformat(),
                "end": inquiry.timeframe_end.date().isoformat(),
            },
            "as_of_ts": inquiry.as_of_ts.isoformat(),
            "context_non_evidence": {
                "label": "Context (not evidence)",
                "text": inquiry.user_input_context or "",
            },
        },
        "latest_brief": version.brief_payload,
    }
    return jsonify(response), 201 if not deduped else 200


@api_v1_inquiry_bp.get("")
@api_v1_inquiry_bp.get("/")
@jwt_required()
@read_only_endpoint
def list_inquiries_v1():
    if not _phase6_enabled():
        return _feature_disabled_response()

    user_id = int(get_jwt_identity())
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        record_inquiry_error("list", "validation_error")
        return jsonify({"ok": False, "error": "validation_error"}), 400
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    cache_key = {"view": "list", "limit": limit, "offset": offset}
    cached = read_cache.get(INQUIRY_READ_CACHE_SCOPE, user_id, cache_key)
    if cached is not None:
        return jsonify(cached)

    items, total = list_inquiries(user_id, limit=limit, offset=offset)
    payload = {"ok": True, "items": items, "total": total, "limit": limit, "offset": offset}
    read_cache.set(INQUIRY_READ_CACHE_SCOPE, user_id, cache_key, payload)
    return jsonify(payload)


@api_v1_inquiry_bp.get("/<int:inquiry_id>")
@jwt_required()
def get_inquiry_v1(inquiry_id: int):
    if not _phase6_enabled():
        return _feature_disabled_response()

    user_id = int(get_jwt_identity())
    payload = get_inquiry(user_id, inquiry_id)
    if payload is None:
        record_inquiry_error("detail", "not_found")
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "inquiry": payload})


@api_v1_inquiry_bp.post("/<int:inquiry_id>/refine")
@jwt_required()
@csrf_protected
def refine_inquiry_v1(inquiry_id: int):
    if not _phase6_enabled():
        return _feature_disabled_response()

    payload = request.get_json(silent=True) or {}
    try:
        data = InquiryRefineRequest.model_validate(payload)
    except ValidationError as exc:
        record_inquiry_error("refine", "validation_error")
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    except ValueError as exc:
        record_inquiry_error("refine", "validation_error")
        return jsonify({"ok": False, "error": str(exc)}), 400

    user_id = int(get_jwt_identity())
    try:
        inquiry, version = refine_inquiry(user_id, inquiry_id, data)
    except ValueError as exc:
        if str(exc) == "not_found":
            record_inquiry_error("refine", "not_found")
            return jsonify({"ok": False, "error": "not_found"}), 404
        record_inquiry_error("refine", "validation_error")
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        record_inquiry_error("refine", "internal_error")
        raise

    return jsonify(
        {
            "ok": True,
            "inquiry_id": inquiry.id,
            "version_id": version.id,
            "version_number": version.version_number,
            "brief": version.brief_payload,
        }
    )
