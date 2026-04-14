"""Transaction API — list, get, create, edit, void, split, transfer."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.finance.schemas.finance_schemas import (
    SplitTransactionCreate,
    TransactionCreate,
    TransactionListFilter,
    TransactionUpdate,
    TransactionVoidRequest,
    TransferTransactionCreate,
)
from lifeos.domains.finance.services.journal_service import (
    edit_transaction,
    record_split_transaction,
    record_transaction,
    record_transfer,
    void_transaction,
)
from lifeos.domains.finance.services.transaction_service import (
    get_transaction,
    list_transactions,
)
from lifeos.extensions import limiter

transaction_api_bp = Blueprint("transaction_api", __name__)


def _txn_to_dict(txn) -> dict:
    return {
        "id": txn.id,
        "amount": float(txn.amount),
        "currency_code": txn.currency_code,
        "description": txn.description,
        "occurred_at": txn.occurred_at.isoformat() if txn.occurred_at else None,
        "journal_entry_id": txn.journal_entry_id,
        "counterparty": txn.counterparty,
        "category": txn.category,
        "source": txn.source,
        "is_void": bool(txn.is_void),
        "void_of_id": txn.void_of_id,
        "edited_at": txn.edited_at.isoformat() if txn.edited_at else None,
    }


# ---------------------------------------------------------------------------
# GET /transactions — list with filtering + pagination
# ---------------------------------------------------------------------------


@transaction_api_bp.get("/transactions")
@jwt_required()
@limiter.limit("240/minute")
def list_transactions_endpoint():
    """
    List transactions for the authenticated user with optional filters.

    Query params (all optional):
      start_date, end_date, account_id, category, counterparty,
      currency_code, min_amount, max_amount, source, include_void,
      page (default 1), per_page (default 50, max 200)

    Response:
      {"ok": true, "transactions": [...], "total": N, "page": P, "pages": PP}
    """
    user_id = int(get_jwt_identity())
    raw = request.args.to_dict(flat=True)
    # Coerce boolean string
    if "include_void" in raw:
        raw["include_void"] = raw["include_void"].lower() not in {"false", "0", "no"}
    try:
        flt = TransactionListFilter.model_validate(raw)
    except ValidationError:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    result = list_transactions(
        user_id=user_id,
        start_date=flt.start_date,
        end_date=flt.end_date,
        account_id=flt.account_id,
        category=flt.category,
        counterparty=flt.counterparty,
        currency_code=flt.currency_code,
        min_amount=flt.min_amount,
        max_amount=flt.max_amount,
        source=flt.source,
        include_void=flt.include_void,
        page=flt.page,
        per_page=flt.per_page,
    )
    return jsonify(
        {
            "ok": True,
            "transactions": [_txn_to_dict(t) for t in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "pages": result["pages"],
            "per_page": result["per_page"],
        }
    )


# ---------------------------------------------------------------------------
# GET /transactions/<id>
# ---------------------------------------------------------------------------


@transaction_api_bp.get("/transactions/<int:transaction_id>")
@jwt_required()
@limiter.limit("240/minute")
def get_transaction_endpoint(transaction_id: int):
    user_id = int(get_jwt_identity())
    txn = get_transaction(user_id, transaction_id)
    if txn is None:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "transaction": _txn_to_dict(txn)})


# ---------------------------------------------------------------------------
# POST /transactions — simple two-account transaction
# ---------------------------------------------------------------------------


@transaction_api_bp.post("/transactions")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("180/minute")
def create_transaction_endpoint():
    """
    Create a simple debit/credit transaction (auto-generates a balanced journal entry).
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    payload["user_id"] = user_id
    try:
        data = TransactionCreate.model_validate(payload)
    except ValidationError:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        entry = record_transaction(
            user_id=data.user_id,
            amount=data.amount,
            debit_account_id=data.debit_account_id,
            credit_account_id=data.credit_account_id,
            description=data.description or "",
            currency_code=data.currency_code,
            occurred_at=data.occurred_at,
            counterparty=data.counterparty,
            category=data.category,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        if code in {"validation_error", "unbalanced_entry", "inactive_account"}:
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify({"ok": True, "journal_entry_id": entry.id}), 201


# ---------------------------------------------------------------------------
# POST /transactions/split — split transaction
# ---------------------------------------------------------------------------


@transaction_api_bp.post("/transactions/split")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("120/minute")
def create_split_transaction_endpoint():
    """
    Create a split transaction (one source account, multiple debit legs).
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    payload["user_id"] = user_id
    try:
        data = SplitTransactionCreate.model_validate(payload)
    except ValidationError:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        entry = record_split_transaction(
            user_id=data.user_id,
            credit_account_id=data.credit_account_id,
            total_amount=data.total_amount,
            split_lines=[line.model_dump() for line in data.split_lines],
            description=data.description,
            currency_code=data.currency_code,
            occurred_at=data.occurred_at,
            counterparty=data.counterparty,
        )
    except ValueError as exc:
        code = str(exc)
        if code in {"split_amounts_do_not_balance", "unbalanced_entry"}:
            return jsonify({"ok": False, "error": code}), 400
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify({"ok": True, "journal_entry_id": entry.id}), 201


# ---------------------------------------------------------------------------
# POST /transactions/transfer — between own accounts
# ---------------------------------------------------------------------------


@transaction_api_bp.post("/transactions/transfer")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("120/minute")
def create_transfer_endpoint():
    """
    Transfer funds between two of the user's own asset/liability accounts.
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    payload["user_id"] = user_id
    try:
        data = TransferTransactionCreate.model_validate(payload)
    except ValidationError:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        entry = record_transfer(
            user_id=data.user_id,
            from_account_id=data.from_account_id,
            to_account_id=data.to_account_id,
            amount=data.amount,
            description=data.description,
            currency_code=data.currency_code,
            occurred_at=data.occurred_at,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        if code == "invalid_transfer_accounts":
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify({"ok": True, "journal_entry_id": entry.id}), 201


# ---------------------------------------------------------------------------
# PATCH /transactions/<id> — in-grace-period metadata edit
# ---------------------------------------------------------------------------


@transaction_api_bp.patch("/transactions/<int:transaction_id>")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("120/minute")
def edit_transaction_endpoint(transaction_id: int):
    """
    Edit transaction metadata within the 24-hour grace period.

    Only description, counterparty, category, occurred_at may be changed.
    Amount / account changes require void + re-entry.

    Response:
      {"ok": true, "transaction": {...}}

    Errors:
      403 grace_period_expired — more than 24h since creation
      409 already_void         — transaction has been voided
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    try:
        data = TransactionUpdate.model_validate(payload)
    except ValidationError:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        txn = edit_transaction(
            user_id=user_id,
            transaction_id=transaction_id,
            description=data.description,
            counterparty=data.counterparty,
            category=data.category,
            occurred_at=data.occurred_at,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        if code == "already_void":
            return jsonify({"ok": False, "error": code}), 409
        if code == "grace_period_expired":
            return jsonify({"ok": False, "error": code}), 403
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify({"ok": True, "transaction": _txn_to_dict(txn)})


# ---------------------------------------------------------------------------
# POST /transactions/<id>/void
# ---------------------------------------------------------------------------


@transaction_api_bp.post("/transactions/<int:transaction_id>/void")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("60/minute")
def void_transaction_endpoint(transaction_id: int):
    """
    Void a transaction. Creates a mirror reversal journal entry.

    Request Body (optional):
      {"reason": "Entered wrong amount"}

    Response:
      {"ok": true, "reversal_entry_id": N}
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    try:
        data = TransactionVoidRequest.model_validate(payload)
    except ValidationError:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        _txn, reversal_entry = void_transaction(
            user_id=user_id,
            transaction_id=transaction_id,
            reason=data.reason,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        if code == "already_void":
            return jsonify({"ok": False, "error": code}), 409
        if code == "no_journal_entry":
            return jsonify({"ok": False, "error": code}), 422
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify({"ok": True, "reversal_entry_id": reversal_entry.id})
