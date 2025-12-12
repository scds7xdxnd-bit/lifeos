"""Receivable/loan API controllers."""

from __future__ import annotations

import math

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.finance.mappers import map_receivable, map_receivable_entry
from lifeos.domains.finance.schemas.finance_schemas import (
    ReceivableCreate,
    ReceivableEntryCreate,
    ReceivableUpdate,
)
from lifeos.domains.finance.services import receivable_service

receivable_api_bp = Blueprint("finance_receivable_api", __name__)


@receivable_api_bp.get("/receivables")
@jwt_required()
def list_receivables():
    user_id = int(get_jwt_identity())
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    trackers, total = receivable_service.list_receivables(
        user_id, page=page, per_page=per_page
    )
    pages = math.ceil(total / per_page) if per_page else 1
    return jsonify(
        {
            "ok": True,
            "items": [map_receivable(t) for t in trackers],
            "page": page,
            "pages": pages,
            "total": total,
        }
    )


@receivable_api_bp.post("/receivables")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def create_receivable_endpoint():
    payload = request.get_json(silent=True) or {}
    try:
        data = ReceivableCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify(
                {"ok": False, "error": "validation_error", "details": exc.errors()}
            ),
            400,
        )
    user_id = int(get_jwt_identity())
    tracker = receivable_service.create_receivable(
        user_id=user_id,
        counterparty=data.counterparty,
        principal=data.principal,
        start_date=data.start_date,
        due_date=data.due_date,
        interest_rate=data.interest_rate,
    )
    return jsonify({"ok": True, "tracker": map_receivable(tracker)}), 201


@receivable_api_bp.get("/receivables/<int:tracker_id>")
@jwt_required()
def get_receivable(tracker_id: int):
    user_id = int(get_jwt_identity())
    tracker = receivable_service.get_receivable(user_id, tracker_id)
    if not tracker:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "tracker": map_receivable(tracker)})


@receivable_api_bp.patch("/receivables/<int:tracker_id>")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def update_receivable(tracker_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = ReceivableUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify(
                {"ok": False, "error": "validation_error", "details": exc.errors()}
            ),
            400,
        )
    user_id = int(get_jwt_identity())
    tracker = receivable_service.update_receivable(
        user_id,
        tracker_id,
        **{k: v for k, v in data.model_dump().items() if v is not None},
    )
    if not tracker:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "tracker": map_receivable(tracker)})


@receivable_api_bp.delete("/receivables/<int:tracker_id>")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def delete_receivable(tracker_id: int):
    user_id = int(get_jwt_identity())
    deleted = receivable_service.delete_receivable(user_id, tracker_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@receivable_api_bp.get("/receivables/<int:tracker_id>/entries")
@jwt_required()
def list_receivable_entries(tracker_id: int):
    user_id = int(get_jwt_identity())
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    try:
        entries, total = receivable_service.list_receivable_entries(
            user_id, tracker_id, page=page, per_page=per_page
        )
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        raise
    pages = math.ceil(total / per_page) if per_page else 1
    return jsonify(
        {
            "ok": True,
            "items": [map_receivable_entry(e) for e in entries],
            "page": page,
            "pages": pages,
            "total": total,
        }
    )


@receivable_api_bp.post("/receivables/<int:tracker_id>/entries")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def add_receivable_entry(tracker_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = ReceivableEntryCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify(
                {"ok": False, "error": "validation_error", "details": exc.errors()}
            ),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        entry = receivable_service.record_receivable_entry(
            user_id=user_id,
            tracker_id=tracker_id,
            amount=data.amount,
            entry_date=data.entry_date,
            memo=data.memo,
        )
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "entry": map_receivable_entry(entry)}), 201
