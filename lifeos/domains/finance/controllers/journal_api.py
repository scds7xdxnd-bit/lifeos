"""Journal API for finance domain."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from sqlalchemy.orm import selectinload

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.finance.mappers import map_journal_entry_request
from lifeos.domains.finance.models.accounting_models import JournalEntry, JournalLine
from lifeos.domains.finance.schemas.finance_schemas import JournalEntryCreateRequest
from lifeos.domains.finance.services.accounting_service import (
    post_journal_entry_with_totals,
)
from lifeos.extensions import limiter

journal_api_bp = Blueprint("finance_journal_api", __name__)


@journal_api_bp.get("/journal")
@jwt_required()
@limiter.limit("240/minute")
def list_journal_entries():
    user_id = int(get_jwt_identity())
    # Get total count per user to present a user-scoped entry number (avoids global ID confusion)
    total_count = JournalEntry.query.filter_by(user_id=user_id).count()
    entries = (
        JournalEntry.query.filter_by(user_id=user_id)
        .options(selectinload(JournalEntry.lines))
        .order_by(JournalEntry.posted_at.desc())
        .limit(50)
        .all()
    )

    # entry_number counts down from the user's total, matching the displayed order
    payload = []
    for idx, e in enumerate(entries):
        entry_number = max(total_count - idx, 1)
        debit_total = float(sum((line.debit or 0) for line in e.lines))
        credit_total = float(sum((line.credit or 0) for line in e.lines))

        payload.append(
            {
                "id": e.id,
                "entry_number": entry_number,
                "description": e.description,
                "posted_at": e.posted_at.isoformat(),
                "lines": len(e.lines),
                "debit_total": debit_total,
                "credit_total": credit_total,
            }
        )

    return jsonify({"ok": True, "entries": payload, "total_entries": total_count})


@journal_api_bp.get("/journal/entries/<int:entry_id>")
@jwt_required()
@limiter.limit("240/minute")
def get_journal_entry_detail(entry_id: int):
    """Return a single journal entry with line-level detail and totals."""

    user_id = int(get_jwt_identity())
    entry = (
        JournalEntry.query.options(selectinload(JournalEntry.lines).selectinload(JournalLine.account))
        .filter_by(id=entry_id, user_id=user_id)
        .first()
    )

    if not entry:
        return jsonify({"ok": False, "error": "not_found"}), 404

    debit_total = float(sum((line.debit or 0) for line in entry.lines))
    credit_total = float(sum((line.credit or 0) for line in entry.lines))

    lines = []
    for line in entry.lines:
        lines.append(
            {
                "id": line.id,
                "account_id": line.account_id,
                "account_name": line.account.name if line.account else None,
                "debit": float(line.debit or 0),
                "credit": float(line.credit or 0),
                "memo": line.memo,
            }
        )

    return jsonify(
        {
            "ok": True,
            "entry": {
                "id": entry.id,
                "description": entry.description,
                "posted_at": entry.posted_at.isoformat(),
                "debit_total": debit_total,
                "credit_total": credit_total,
                "lines": lines,
            },
        }
    )


@journal_api_bp.post("/journal/entries")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("120/minute")
def create_journal_entry():
    payload = request.get_json(silent=True) or {}
    payload["user_id"] = int(get_jwt_identity())
    try:
        data = JournalEntryCreateRequest.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )

    try:
        entry, debit_total, credit_total = post_journal_entry_with_totals(
            user_id=data.user_id,
            description=data.description or "",
            lines=map_journal_entry_request(data),
            posted_at=data.posted_at,
        )
    except ValueError as exc:
        code = str(exc)
        if code in {"unbalanced_entry", "validation_error"}:
            return jsonify({"ok": False, "error": code}), 400
        if code == "inactive_account":
            return jsonify({"ok": False, "error": code}), 400
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify(
        {
            "ok": True,
            "entry_id": entry.id,
            "total_debit": float(debit_total),
            "total_credit": float(credit_total),
        }
    )
