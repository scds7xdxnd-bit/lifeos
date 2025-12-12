"""Finance API controllers."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.finance.ml.feedback import record_feedback
from lifeos.domains.finance.models.accounting_models import Account
from lifeos.domains.finance.schemas.finance_schemas import (
    AccountCategoryCreate,
    AccountCreate,
    AccountInlineCreate,
    AccountSearchQuery,
    AccountUpdateCategory,
    JournalEntryCreate,
    TransactionCreate,
)
from lifeos.domains.finance.services.accounting_service import (
    create_account,
    create_account_inline,
    create_custom_account_category,
    get_account_subtypes,
    get_suggested_accounts,
    list_account_categories,
    post_journal_entry,
    update_account_category,
)
from lifeos.domains.finance.services.journal_service import record_transaction
from lifeos.domains.finance.services.suggestion_service import suggest_accounts
from lifeos.domains.finance.services.trial_balance_service import (
    calculate_trial_balance,
    net_balance_for_account,
)
from lifeos.extensions import limiter

finance_api_bp = Blueprint("finance_api", __name__)


# ==================== Account Search & Inline Creation ====================


@finance_api_bp.get("/accounts/search")
@jwt_required()
@limiter.limit("240/minute")
def search_accounts_endpoint():
    """
    Search for existing accounts by name (typeahead).

    Query Parameters:
    - q: Search query (required, 1-100 chars)
    - limit: Max results (optional, default 20, max 100)
    - include_ml: Include ML suggestions (optional, default true)

    Returns:
    {
      "ok": true,
      "results": [
        {"id": 1, "name": "Cash", "account_type": "asset", "account_subtype": "cash", "is_existing": true},
        ...
      ]
    }
    """
    user_id = int(get_jwt_identity())

    try:
        data = AccountSearchQuery.model_validate(request.args)
    except Exception:
        return jsonify({"ok": False, "error": "invalid_query"}), 400

    try:
        results = get_suggested_accounts(
            user_id=user_id,
            query=data.q,
            limit=data.limit,
            include_ml=data.include_ml,
        )
        return jsonify({"ok": True, "results": results}), 200
    except ValueError as exc:
        code = str(exc)
        if code == "invalid_query":
            return jsonify({"ok": False, "error": "invalid_query"}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400


@finance_api_bp.post("/accounts/inline")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("120/minute")
def create_account_inline_endpoint():
    """
    Create a new account with minimal input (inline account creation).

    Request Body:
    {
      "name": "My Savings Account",
      "account_type": "asset",
      "account_subtype": "bank"
    }

    Response (201 Created):
    {
      "ok": true,
      "account": {
        "id": 42,
        "name": "My Savings Account",
        "account_type": "asset",
        "account_subtype": "bank",
        "created_at": "2025-12-06T10:30:00Z"
      }
    }

    Response (409 Conflict - already exists, returned as 200 for idempotency):
    {
      "ok": true,
      "account": { ... }
    }
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}

    try:
        data = AccountInlineCreate.model_validate(payload)
    except Exception as exc:
        if isinstance(exc, ValidationError):
            # Surface a more specific error when account_type is invalid
            for err in exc.errors():
                if "account_type" in err.get("loc", ()):  # type: ignore[arg-type]
                    return jsonify({"ok": False, "error": "invalid_account_type"}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        account = create_account_inline(
            user_id=user_id,
            name=data.name,
            account_type=data.account_type,
            account_subtype=data.account_subtype,
            category_id=data.category_id,
            category_name_new=data.category_name_new,
        )
        return (
            jsonify(
                {
                    "ok": True,
                    "account": {
                        "id": account.id,
                        "name": account.name,
                        "account_type": account.account_type,
                        "account_subtype": account.account_subtype,
                        "category_id": account.category_id,
                        "created_at": account.created_at.isoformat(),
                    },
                }
            ),
            201,
        )
    except ValueError as exc:
        code = str(exc)
        if code in {
            "invalid_name",
            "invalid_account_type",
            "invalid_account_subtype",
            "validation_error",
        }:
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400


@finance_api_bp.get("/accounts/subtypes/<account_type>")
@limiter.limit("600/minute")
def get_account_subtypes_endpoint(account_type: str):
    """
    Get valid subtypes for a given account type.

    Path Parameters:
    - account_type: One of 'asset', 'liability', 'equity', 'income', 'expense'

    Response (200 OK):
    {
      "ok": true,
      "account_type": "asset",
      "subtypes": ["cash", "bank", "investment", "property", "other"]
    }

    Response (400 Bad Request):
    {
      "ok": false,
      "error": "invalid_account_type"
    }
    """
    try:
        subtypes = get_account_subtypes(account_type)
        return (
            jsonify(
                {
                    "ok": True,
                    "account_type": account_type,
                    "subtypes": subtypes,
                }
            ),
            200,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "invalid_account_type":
            return jsonify({"ok": False, "error": "invalid_account_type"}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400


# ==================== Account Categories ====================


@finance_api_bp.get("/account-categories")
@jwt_required()
@limiter.limit("240/minute")
def list_account_categories_endpoint():
    base_type = request.args.get("base_type")
    include_system_raw = (request.args.get("include_system") or "true").lower()
    include_system = include_system_raw not in {"false", "0", "no"}

    try:
        if base_type:
            # Validate base_type quickly via subtypes helper
            _ = get_account_subtypes(base_type)
        categories = list_account_categories(
            int(get_jwt_identity()), base_type=base_type, include_system=include_system
        )
    except ValueError as exc:
        code = str(exc)
        if code == "invalid_account_type":
            return jsonify({"ok": False, "error": "invalid_base_type"}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400

    results = [
        {
            "id": cat.id,
            "name": cat.name,
            "base_type": cat.base_type,
            "is_default": bool(cat.is_default),
            "is_system": bool(cat.is_system),
        }
        for cat in categories
    ]
    return jsonify({"ok": True, "categories": results})


@finance_api_bp.post("/account-categories")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("120/minute")
def create_account_category_endpoint():
    payload = request.get_json(silent=True) or {}
    try:
        data = AccountCategoryCreate.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        category = create_custom_account_category(
            user_id=int(get_jwt_identity()),
            base_type=data.base_type,
            name=data.name,
            is_default=data.is_default,
        )
    except ValueError as exc:
        code = str(exc)
        if code in {"invalid_base_type", "invalid_name"}:
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return (
        jsonify(
            {
                "ok": True,
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "base_type": category.base_type,
                    "is_default": bool(category.is_default),
                    "is_system": bool(category.is_system),
                },
            }
        ),
        201,
    )


@finance_api_bp.post("/accounts")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("60/minute")
def create_account_endpoint():
    payload = request.get_json(silent=True) or {}
    payload["user_id"] = int(get_jwt_identity())
    try:
        data = AccountCreate.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        account = create_account(
            user_id=data.user_id,
            name=data.name,
            base_type=data.account_type,
            account_subtype=data.account_subtype,
            category_id=data.category_id,
            category_name_new=data.category_name_new,
            code=data.code,
            description=data.description,
        )
    except ValueError as exc:
        code = str(exc)
        if code in {
            "invalid_name",
            "invalid_account_type",
            "invalid_account_subtype",
            "invalid_base_type",
            "invalid_category",
        }:
            return jsonify({"ok": False, "error": code}), 400
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return (
        jsonify(
            {
                "ok": True,
                "account": {
                    "id": account.id,
                    "name": account.name,
                    "account_type": account.account_type,
                    "account_subtype": account.account_subtype,
                    "category_id": account.category_id,
                    "code": account.code,
                },
            }
        ),
        201,
    )


@finance_api_bp.patch("/accounts/<int:account_id>/category")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("90/minute")
def update_account_category_endpoint(account_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = AccountUpdateCategory.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        account = update_account_category(
            user_id=int(get_jwt_identity()),
            account_id=account_id,
            category_id=data.category_id,
            category_name_new=data.category_name_new,
        )
    except ValueError as exc:
        code = str(exc)
        if code in {"invalid_category", "invalid_base_type", "invalid_name"}:
            return jsonify({"ok": False, "error": code}), 400
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify(
        {"ok": True, "account": {"id": account.id, "category_id": account.category_id}}
    )


@finance_api_bp.post("/journal")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("120/minute")
def post_journal():
    payload = request.get_json(silent=True) or {}
    payload["user_id"] = int(get_jwt_identity())
    data = JournalEntryCreate.model_validate(payload)
    entry = post_journal_entry(
        user_id=data.user_id,
        description=data.description or "",
        lines=[line.model_dump() for line in data.lines],
    )
    return jsonify({"ok": True, "entry_id": entry.id})


@finance_api_bp.post("/transactions")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("180/minute")
def create_transaction():
    payload = request.get_json(silent=True) or {}
    payload["user_id"] = int(get_jwt_identity())
    data = TransactionCreate.model_validate(payload)
    try:
        entry = record_transaction(
            user_id=data.user_id,
            amount=data.amount,
            debit_account_id=data.debit_account_id,
            credit_account_id=data.credit_account_id,
            description=data.description or "",
        )
    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": code}), 404
        if code in {"validation_error", "unbalanced_entry", "inactive_account"}:
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "journal_entry_id": entry.id})


@finance_api_bp.get("/trial-balance")
@jwt_required()
def get_trial_balance():
    user_id = get_jwt_identity()
    totals = calculate_trial_balance(user_id)
    accounts = Account.query.filter_by(user_id=user_id).all()
    payload = []
    for account in accounts:
        payload.append(
            {
                "account_id": account.id,
                "name": account.name,
                "code": account.code,
                "balance": net_balance_for_account(account, totals),
            }
        )
    return jsonify({"ok": True, "accounts": payload})


@finance_api_bp.post("/suggestions/accounts")
@jwt_required()
@csrf_protected
def suggest_account_from_description():
    payload = request.get_json(silent=True) or {}
    description = payload.get("description") or ""
    ranked = suggest_accounts(get_jwt_identity(), description)
    return jsonify({"ok": True, "suggestions": ranked})


@finance_api_bp.post("/suggestions/feedback")
@jwt_required()
@csrf_protected
def suggestion_feedback():
    payload = request.get_json(silent=True) or {}
    suggestion_id = str(payload.get("suggestion_id") or "")
    accepted = bool(payload.get("accepted"))
    score = payload.get("score")
    record_feedback(
        user_id=int(get_jwt_identity()),
        suggestion_id=suggestion_id,
        accepted=accepted,
        score=score,
    )
    return jsonify({"ok": True})
