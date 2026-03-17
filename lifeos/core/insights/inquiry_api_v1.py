"""Focused Inquiry v1 API endpoints."""

from __future__ import annotations

import json as _json

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.insights.inquiry_schemas import InquiryCreateRequest, InquiryFeedbackRequest, InquiryRefineRequest
from lifeos.core.insights.inquiry_service import (
    INQUIRY_READ_CACHE_SCOPE,
    _serialize_brief_payload,
    create_inquiry,
    get_inquiry,
    list_inquiries,
    record_inquiry_feedback,
    refine_inquiry,
)
from lifeos.core.observability import record_inquiry_error
from lifeos.core.private_alpha import AlphaGateError, alpha_flags, alpha_history_enabled, evaluate_alpha_readiness
from lifeos.core.read_cache import read_cache
from lifeos.core.utils.decorators import csrf_protected, read_only_endpoint
from lifeos.extensions import db


def _pydantic_errors(exc: ValidationError) -> list[dict]:
    """Return JSON-safe error list from a Pydantic v2 ValidationError.

    Pydantic v2 includes the original exception object in ``ctx["error"]``,
    which is not JSON-serializable by Flask's jsonify. Using Pydantic's own
    JSON encoder and then decoding gives us a clean, serializable structure.
    """
    return _json.loads(exc.json())


api_v1_inquiry_bp = Blueprint("inquiry_api_v1", __name__)


def _phase6_enabled() -> bool:
    return bool(current_app.config.get("ENABLE_PHASE6_FOCUSED_INQUIRY", False))


def _feature_disabled_response():
    return jsonify({"ok": False, "error": "not_found"}), 404


def _error_metric_labels(
    *,
    domain: str | None = None,
    cross_domain: bool | None = None,
) -> dict[str, object]:
    resolved_domain = str(domain or "").strip().lower() or "unknown"
    if cross_domain:
        resolved_domain = "cross_domain"
    return {
        "domain": resolved_domain,
        "profile": "unknown",
        "profile_version": "unknown",
        "strategy": "unknown",
        "strategy_version": "unknown",
        "expert_mode": False,
    }


def _labels_from_create_payload(payload: dict[str, object]) -> dict[str, object]:
    domains = payload.get("domains")
    if isinstance(domains, list):
        normalized = [str(item).strip().lower() for item in domains if str(item).strip()]
        if len(normalized) > 1:
            return _error_metric_labels(domain="cross_domain", cross_domain=True)
        if normalized:
            return _error_metric_labels(domain=normalized[0], cross_domain=False)
    domain = payload.get("domain")
    return _error_metric_labels(
        domain=str(domain) if domain is not None else None,
        cross_domain=bool(payload.get("cross_domain")),
    )


def _is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


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
        record_inquiry_error("create", "validation_error", **_labels_from_create_payload(payload))
        return jsonify({"ok": False, "error": "validation_error", "details": _pydantic_errors(exc)}), 400
    except ValueError as exc:
        record_inquiry_error("create", "validation_error", **_labels_from_create_payload(payload))
        return jsonify({"ok": False, "error": str(exc)}), 400

    user_id = int(get_jwt_identity())
    create_labels = _error_metric_labels(
        domain=data.domain,
        cross_domain=data.cross_domain,
    )
    try:
        inquiry, version, deduped = create_inquiry(user_id, data)
    except AlphaGateError as exc:
        record_inquiry_error("create", exc.code, **create_labels)
        return jsonify({"ok": False, "error": exc.code, "details": exc.details}), 403
    except Exception:
        record_inquiry_error("create", "internal_error", **create_labels)
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
        "latest_brief": _serialize_brief_payload(version.brief_payload, brief_hash=version.brief_hash),
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
        record_inquiry_error("list", "validation_error", **_error_metric_labels())
        return jsonify({"ok": False, "error": "validation_error"}), 400
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    if not alpha_history_enabled():
        record_inquiry_error("list", "alpha_history_disabled", **_error_metric_labels())
        return jsonify({"ok": False, "error": "alpha_history_disabled"}), 404

    cache_key = {"view": "list", "limit": limit, "offset": offset}
    cached = read_cache.get(INQUIRY_READ_CACHE_SCOPE, user_id, cache_key)
    if cached is not None:
        return jsonify(cached)

    try:
        items, total = list_inquiries(user_id, limit=limit, offset=offset)
    except AlphaGateError as exc:
        record_inquiry_error("list", exc.code, **_error_metric_labels())
        return jsonify({"ok": False, "error": exc.code, "details": exc.details}), 404
    payload = {"ok": True, "items": items, "total": total, "limit": limit, "offset": offset}
    read_cache.set(INQUIRY_READ_CACHE_SCOPE, user_id, cache_key, payload)
    return jsonify(payload)


@api_v1_inquiry_bp.get("/<int:inquiry_id>")
@jwt_required()
def get_inquiry_v1(inquiry_id: int):
    if not _phase6_enabled():
        return _feature_disabled_response()

    user_id = int(get_jwt_identity())
    payload = get_inquiry(
        user_id,
        inquiry_id,
        technical_view_expanded=_is_truthy(request.args.get("technical_view")),
    )
    if payload is None:
        record_inquiry_error("detail", "not_found", **_error_metric_labels())
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
        record_inquiry_error("refine", "validation_error", **_labels_from_create_payload(payload))
        return jsonify({"ok": False, "error": "validation_error", "details": _pydantic_errors(exc)}), 400
    except ValueError as exc:
        record_inquiry_error("refine", "validation_error", **_labels_from_create_payload(payload))
        return jsonify({"ok": False, "error": str(exc)}), 400

    user_id = int(get_jwt_identity())
    refine_labels = _error_metric_labels(
        domain=data.domain,
        cross_domain=bool(data.cross_domain),
    )
    try:
        inquiry, version = refine_inquiry(user_id, inquiry_id, data)
    except AlphaGateError as exc:
        record_inquiry_error("refine", exc.code, **refine_labels)
        return jsonify({"ok": False, "error": exc.code, "details": exc.details}), 403
    except ValueError as exc:
        if str(exc) == "not_found":
            record_inquiry_error("refine", "not_found", **refine_labels)
            return jsonify({"ok": False, "error": "not_found"}), 404
        record_inquiry_error("refine", "validation_error", **refine_labels)
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        record_inquiry_error("refine", "internal_error", **refine_labels)
        raise

    return jsonify(
        {
            "ok": True,
            "inquiry_id": inquiry.id,
            "version_id": version.id,
            "version_number": version.version_number,
            "brief": _serialize_brief_payload(version.brief_payload, brief_hash=version.brief_hash),
        }
    )


@api_v1_inquiry_bp.get("/readiness")
@jwt_required()
@read_only_endpoint
def get_inquiry_readiness_v1():
    if not _phase6_enabled():
        return _feature_disabled_response()
    user_id = int(get_jwt_identity())
    readiness = evaluate_alpha_readiness(user_id)
    return jsonify({"ok": True, "readiness": readiness.to_payload(), "alpha": alpha_flags().to_bootstrap_payload()})


@api_v1_inquiry_bp.post("/<int:inquiry_id>/feedback")
@jwt_required()
@csrf_protected
def record_inquiry_feedback_v1(inquiry_id: int):
    if not _phase6_enabled():
        return _feature_disabled_response()

    payload = request.get_json(silent=True) or {}
    try:
        data = InquiryFeedbackRequest.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": _pydantic_errors(exc)}), 400
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    user_id = int(get_jwt_identity())
    try:
        feedback, deduped = record_inquiry_feedback(user_id, inquiry_id, data)
        db.session.commit()
    except AlphaGateError as exc:
        return jsonify({"ok": False, "error": exc.code, "details": exc.details}), 403
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"ok": False, "error": "feedback_retryable_failure", "retryable": True}), 503

    return jsonify({"ok": True, "feedback_id": feedback.id, "deduped": deduped}), 200 if deduped else 201
