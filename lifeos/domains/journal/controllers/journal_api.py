"""Journal JSON API."""

from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.journal.mappers import map_entry
from lifeos.domains.journal.schemas.journal_schemas import (
    JournalEntryCreate,
    JournalEntryListFilter,
    JournalEntryUpdate,
)
from lifeos.domains.journal.services import journal_service

journal_api_bp = Blueprint("journal_api", __name__)


@journal_api_bp.get("")
@jwt_required()
def list_journal():
    user_id = int(get_jwt_identity())
    try:
        filters = JournalEntryListFilter.model_validate(request.args)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    entries, total = journal_service.list_entries(
        user_id=user_id,
        date_from=filters.date_from,
        date_to=filters.date_to,
        mood=filters.mood,
        tag=filters.tag,
        search_text=filters.search_text,
        page=filters.page,
        per_page=filters.per_page,
    )
    pages = (total + filters.per_page - 1) // filters.per_page if filters.per_page else 1
    return jsonify({"ok": True, "items": [map_entry(e) for e in entries], "page": filters.page, "pages": pages, "total": total})


@journal_api_bp.get("/<int:entry_id>")
@jwt_required()
def get_entry(entry_id: int):
    user_id = int(get_jwt_identity())
    entry = journal_service.get_entry(user_id, entry_id)
    if not entry:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "entry": map_entry(entry)})


@journal_api_bp.post("")
@jwt_required()
@csrf_protected
def create_journal_entry():
    payload = request.get_json(silent=True) or {}
    try:
        data = JournalEntryCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    try:
        entry = journal_service.create_entry(
            user_id=user_id,
            title=data.title,
            body=data.body,
            entry_date=data.entry_date or date.today(),
            mood=data.mood,
            tags=data.tags,
            is_private=data.is_private,
            sentiment_score=data.sentiment_score,
            emotion_label=data.emotion_label,
        )
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "entry": map_entry(entry)}), 201


@journal_api_bp.patch("/<int:entry_id>")
@jwt_required()
@csrf_protected
def update_journal_entry(entry_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = JournalEntryUpdate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    entry = journal_service.update_entry(
        user_id,
        entry_id,
        **{k: v for k, v in data.model_dump().items() if v is not None},
    )
    if not entry:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "entry": map_entry(entry)})


@journal_api_bp.delete("/<int:entry_id>")
@jwt_required()
@csrf_protected
def delete_journal_entry(entry_id: int):
    user_id = int(get_jwt_identity())
    deleted = journal_service.delete_entry(user_id, entry_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})
