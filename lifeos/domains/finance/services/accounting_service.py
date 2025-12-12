"""Accounting service: double-entry operations."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Optional, Tuple

from lifeos.domains.finance.events import (
    FINANCE_ACCOUNT_CATEGORY_UPDATED,
    FINANCE_ACCOUNT_CREATED,
    FINANCE_JOURNAL_POSTED,
)
from lifeos.domains.finance.models.accounting_models import (
    Account,
    AccountCategory,
    JournalEntry,
    JournalLine,
)
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox

MAX_DESCRIPTION_LENGTH = 512
MAX_JOURNAL_LINES = 100
BALANCE_TOLERANCE = Decimal("0.005")
TWO_PLACES = Decimal(".01")


def post_journal_entry(
    user_id: int,
    description: str,
    lines: List[dict],
    posted_at: Optional[datetime] = None,
    max_lines: int = MAX_JOURNAL_LINES,
) -> JournalEntry:
    """Create a balanced journal entry with validation and emit event via outbox."""
    entry, _, _ = _create_journal_entry(user_id, description, lines, posted_at, max_lines=max_lines)
    return entry


def post_journal_entry_with_totals(
    user_id: int,
    description: str,
    lines: List[dict],
    posted_at: Optional[datetime] = None,
    max_lines: int = MAX_JOURNAL_LINES,
) -> Tuple[JournalEntry, Decimal, Decimal]:
    """Create a journal entry and return totals for response payloads."""
    return _create_journal_entry(user_id, description, lines, posted_at, max_lines=max_lines)


def _normalize_journal_lines(lines: List[dict]) -> Tuple[List[dict], Decimal, Decimal]:
    normalized: List[dict] = []
    debit_total = Decimal("0")
    credit_total = Decimal("0")
    has_debit = False
    has_credit = False

    for idx, raw in enumerate(lines, start=1):
        account_id = raw.get("account_id")
        try:
            account_id = int(account_id)
        except (TypeError, ValueError):
            raise ValueError("validation_error")
        if account_id <= 0:
            raise ValueError("validation_error")

        memo = (raw.get("memo") or "").strip() or None
        dc = raw.get("dc")
        amount = raw.get("amount")

        if dc is not None or amount is not None:
            dc = str(dc or "").upper()
            amount_dec = Decimal(str(amount or 0)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            if amount_dec <= 0:
                raise ValueError("validation_error")
            if dc not in {"D", "C"}:
                raise ValueError("validation_error")
            debit = amount_dec if dc == "D" else Decimal("0")
            credit = amount_dec if dc == "C" else Decimal("0")
        else:
            debit = Decimal(str(raw.get("debit") or 0)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            credit = Decimal(str(raw.get("credit") or 0)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            if debit < 0 or credit < 0:
                raise ValueError("validation_error")
            if debit == 0 and credit == 0:
                raise ValueError("validation_error")
            if debit > 0 and credit > 0:
                raise ValueError("validation_error")

        debit_total += debit
        credit_total += credit
        has_debit = has_debit or debit > 0
        has_credit = has_credit or credit > 0
        normalized.append({"account_id": account_id, "debit": debit, "credit": credit, "memo": memo})

    if not has_debit or not has_credit:
        raise ValueError("unbalanced_entry")
    if (debit_total - credit_total).copy_abs() > BALANCE_TOLERANCE:
        raise ValueError("unbalanced_entry")
    return normalized, debit_total, credit_total


def _validate_accounts(user_id: int, account_ids: List[int]) -> None:
    accounts = Account.query.filter(Account.user_id == user_id).filter(Account.id.in_(account_ids)).all()
    if len(accounts) != len(set(account_ids)):
        raise ValueError("not_found")
    inactive = [acct.id for acct in accounts if not acct.is_active]
    if inactive:
        raise ValueError("inactive_account")


def _create_journal_entry(
    user_id: int,
    description: str,
    lines: List[dict],
    posted_at: Optional[datetime],
    max_lines: int,
) -> Tuple[JournalEntry, Decimal, Decimal]:
    desc = (description or "").strip()
    if len(desc) > MAX_DESCRIPTION_LENGTH:
        raise ValueError("validation_error")

    if not lines or len(lines) < 2:
        raise ValueError("validation_error")
    if len(lines) > max_lines:
        raise ValueError("validation_error")

    normalized_lines, debit_total, credit_total = _normalize_journal_lines(lines)
    _validate_accounts(user_id, [line["account_id"] for line in normalized_lines])

    entry = JournalEntry(user_id=user_id, description=desc, posted_at=posted_at or datetime.utcnow())
    for line in normalized_lines:
        entry.lines.append(
            JournalLine(
                account_id=line["account_id"],
                debit=line["debit"],
                credit=line["credit"],
                memo=line.get("memo"),
            )
        )

    db.session.add(entry)
    db.session.flush()

    enqueue_outbox(
        FINANCE_JOURNAL_POSTED,
        {
            "entry_id": entry.id,
            "user_id": user_id,
            "debit_total": float(debit_total),
            "credit_total": float(credit_total),
            "line_count": len(normalized_lines),
        },
        user_id=user_id,
    )
    db.session.commit()
    return entry, debit_total, credit_total


# ==================== Account Search & Inline Creation ====================

# Valid account types (core accounting categories)
VALID_ACCOUNT_TYPES = {"asset", "liability", "equity", "income", "expense"}

# Normal balance defaults per base type
BASE_TYPE_NORMAL_BALANCE: Dict[str, str] = {
    "asset": "debit",
    "expense": "debit",
    "liability": "credit",
    "equity": "credit",
    "income": "credit",
}

# Subtypes per account type
ACCOUNT_SUBTYPES_MAP = {
    "asset": ["cash", "bank", "investment", "property", "other"],
    "liability": ["loan", "credit_card", "payable", "other"],
    "equity": ["contributed", "retained_earnings", "other"],
    "income": ["salary", "investment", "business", "rental", "other"],
    "expense": [
        "groceries",
        "utilities",
        "rent",
        "transportation",
        "entertainment",
        "other",
    ],
}


_slug_pattern = re.compile(r"[^a-z0-9]+")


def _normalize_name(name: str) -> str:
    """Normalize account name: lowercase, trim, deduplicate whitespace."""
    return " ".join(name.lower().strip().split())


def _normalize_category_name(name: str) -> tuple[str, str]:
    """Return (clean_name, slug) for category names."""
    clean = " ".join((name or "").strip().split())
    slug = _slug_pattern.sub("-", clean.lower()).strip("-") or "uncategorized"
    return clean, slug


def _generate_category_code(user_id: int | None, base_type: str, slug: str) -> str:
    """Generate a short unique-ish code respecting 16-char limit."""
    prefix = base_type[:3].upper()
    suffix = abs(hash((user_id, slug))) % 10_000_000
    return f"{prefix}{suffix:07d}"[:16]


def search_accounts(user_id: int, query: str, limit: int = 20) -> List[Account]:
    """
    Search for existing active accounts by normalized name.

    Matches:
    1. Prefix matches (normalized_name starts with query) - ordered first
    2. Substring matches - ordered second
    3. Results ordered by created_at DESC (newest first) within each category

    Args:
        user_id: User ID to scope search
        query: Search query (will be normalized)
        limit: Maximum number of results (default 20)

    Returns:
        List of matching Account objects

    Raises:
        ValueError("invalid_query") if query is too long
    """
    query = (query or "").strip()

    if len(query) > 100:
        raise ValueError("invalid_query")
    if not query:
        return []

    normalized_query = _normalize_name(query)

    # Prefix matches (ordered first, newest first)
    prefix_matches = (
        Account.query.filter(Account.user_id == user_id)
        .filter(Account.is_active.is_(True))
        .filter(Account.normalized_name.startswith(normalized_query))
        .order_by(Account.created_at.desc())
        .limit(limit)
        .all()
    )

    if len(prefix_matches) >= limit:
        return prefix_matches[:limit]

    # Substring matches (fill remaining slots)
    remaining = limit - len(prefix_matches)
    substring_matches = (
        Account.query.filter(Account.user_id == user_id)
        .filter(Account.is_active.is_(True))
        .filter(Account.normalized_name.contains(normalized_query))
        .filter(~Account.normalized_name.startswith(normalized_query))
        .order_by(Account.created_at.desc())
        .limit(remaining)
        .all()
    )

    return prefix_matches + substring_matches


def get_suggested_accounts(user_id: int, query: str, limit: int = 10, include_ml: bool = True) -> List[dict]:
    """Get suggested accounts combining existing search + optional ML suggestions."""
    # Derive a safe search limit: if caller asks for fewer than 3, search with that limit (never negative).
    search_limit = limit if limit <= 2 else max(1, limit - 2)

    # Get existing accounts
    try:
        existing = search_accounts(user_id, query, limit=search_limit)
    except ValueError:
        return []

    results = [
        {
            "id": acc.id,
            "name": acc.name,
            "account_type": acc.account_type,
            "account_subtype": acc.account_subtype,
            "is_existing": True,
        }
        for acc in existing
    ]

    # TODO: Add ML suggestions if enabled (future enhancement)
    # For now, just return existing accounts

    return results[:limit]


def list_account_categories(
    user_id: int, base_type: str | None = None, include_system: bool = True
) -> List[AccountCategory]:
    """List categories for a user plus optional system defaults."""
    query = AccountCategory.query
    if base_type:
        query = query.filter(AccountCategory.base_type == base_type)
    if include_system:
        query = query.filter((AccountCategory.user_id == user_id) | (AccountCategory.user_id.is_(None)))
    else:
        query = query.filter(AccountCategory.user_id == user_id)
    return query.order_by(AccountCategory.base_type.asc(), AccountCategory.name.asc()).all()


def _get_category_for_user(user_id: int, category_id: int) -> AccountCategory:
    category = AccountCategory.query.filter(AccountCategory.id == category_id).first()
    if not category:
        raise ValueError("invalid_category")
    if category.user_id not in {None, user_id}:
        raise ValueError("invalid_category")
    return category


def create_custom_account_category(
    user_id: int, base_type: str, name: str, is_default: bool = False
) -> AccountCategory:
    if base_type not in VALID_ACCOUNT_TYPES:
        raise ValueError("invalid_base_type")
    clean_name, slug = _normalize_category_name(name)
    if not clean_name or len(clean_name) > 128:
        raise ValueError("invalid_name")

    existing = (
        AccountCategory.query.filter(AccountCategory.user_id == user_id)
        .filter(AccountCategory.base_type == base_type)
        .filter(AccountCategory.slug == slug)
        .first()
    )
    if existing:
        if is_default and not existing.is_default:
            AccountCategory.query.filter(
                AccountCategory.user_id == user_id,
                AccountCategory.base_type == base_type,
                AccountCategory.is_default == True,  # noqa: E712
            ).update({"is_default": False})
            existing.is_default = True
            db.session.commit()
        return existing

    code = _generate_category_code(user_id, base_type, slug)
    category = AccountCategory(
        user_id=user_id,
        code=code,
        name=clean_name,
        slug=slug,
        base_type=base_type,
        normal_balance=BASE_TYPE_NORMAL_BALANCE[base_type],
        is_default=is_default,
        is_system=False,
    )
    if is_default:
        AccountCategory.query.filter(
            AccountCategory.user_id == user_id,
            AccountCategory.base_type == base_type,
            AccountCategory.is_default == True,  # noqa: E712
        ).update({"is_default": False})
    db.session.add(category)
    db.session.commit()
    return category


def get_or_create_default_category(user_id: int, base_type: str) -> AccountCategory:
    if base_type not in VALID_ACCOUNT_TYPES:
        raise ValueError("invalid_base_type")

    user_default = (
        AccountCategory.query.filter(AccountCategory.user_id == user_id)
        .filter(AccountCategory.base_type == base_type)
        .filter(AccountCategory.is_default == True)  # noqa: E712
        .first()
    )
    if user_default:
        return user_default

    system_default = (
        AccountCategory.query.filter(AccountCategory.user_id.is_(None))
        .filter(AccountCategory.base_type == base_type)
        .filter(AccountCategory.is_default == True)  # noqa: E712
        .first()
    )
    if system_default:
        return system_default

    # As a fallback, create a user-scoped default to avoid failures
    return create_custom_account_category(user_id, base_type, f"Default {base_type.title()}", is_default=True)


def _validate_account_inputs(name: str, account_type: str, account_subtype: str | None) -> tuple[str, str | None]:
    name = (name or "").strip()
    if not name or len(name) > 255:
        raise ValueError("invalid_name")
    if account_type not in VALID_ACCOUNT_TYPES:
        raise ValueError("invalid_account_type")
    if account_subtype is not None:
        account_subtype = (account_subtype or "").strip() or None
        if account_subtype and account_subtype not in get_account_subtypes(account_type):
            raise ValueError("invalid_account_subtype")
    return name, account_subtype


def create_account(
    user_id: int,
    name: str,
    base_type: str,
    account_subtype: str | None = None,
    category_id: int | None = None,
    category_name_new: str | None = None,
    code: str | None = None,
    description: str | None = None,
) -> Account:
    name, account_subtype = _validate_account_inputs(name, base_type, account_subtype)
    normalized_name = _normalize_name(name)

    existing = (
        Account.query.filter(Account.user_id == user_id)
        .filter(Account.normalized_name == normalized_name)
        .filter(Account.is_active.is_(True))
        .first()
    )
    if existing:
        return existing

    if category_name_new:
        category = create_custom_account_category(user_id, base_type, category_name_new, is_default=False)
    elif category_id:
        category = _get_category_for_user(user_id, category_id)
    else:
        category = get_or_create_default_category(user_id, base_type)

    if category.base_type != base_type:
        raise ValueError("invalid_category")

    account = Account(
        user_id=user_id,
        name=name,
        account_type=base_type,
        account_subtype=account_subtype,
        normalized_name=normalized_name,
        category_id=category.id if category else None,
        code=code,
        description=description,
        is_active=True,
    )

    db.session.add(account)
    db.session.flush()  # assign id for events

    enqueue_outbox(
        FINANCE_ACCOUNT_CREATED,
        {
            "account_id": account.id,
            "user_id": user_id,
            "name": name,
            "account_type": base_type,
            "account_subtype": account_subtype,
            "category_id": category.id if category else None,
            "category_name": category.name if category else None,
            "category_base_type": category.base_type if category else None,
            "created_at": account.created_at.isoformat(),
        },
        user_id=user_id,
    )

    db.session.commit()
    return account


def update_account_category(
    user_id: int,
    account_id: int,
    category_id: int | None = None,
    category_name_new: str | None = None,
) -> Account:
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        raise ValueError("not_found")

    base_type = account.account_type
    if category_name_new:
        category = create_custom_account_category(user_id, base_type, category_name_new, is_default=False)
    elif category_id:
        category = _get_category_for_user(user_id, category_id)
    else:
        category = get_or_create_default_category(user_id, base_type)

    if category.base_type != base_type:
        raise ValueError("invalid_category")

    account.category_id = category.id if category else None
    db.session.add(account)
    db.session.flush()

    enqueue_outbox(
        FINANCE_ACCOUNT_CATEGORY_UPDATED,
        {
            "account_id": account.id,
            "user_id": user_id,
            "category_id": category.id if category else None,
            "category_name": category.name if category else None,
            "category_base_type": category.base_type if category else None,
            "updated_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )

    db.session.commit()
    return account


def get_account_subtypes(account_type: str) -> List[str]:
    """
    Get valid subtypes for a given account type.

    Args:
        account_type: One of 'asset', 'liability', 'equity', 'income', 'expense'

    Returns:
        List of valid subtypes

    Raises:
        ValueError("invalid_account_type") if account_type is not valid
    """
    if account_type not in VALID_ACCOUNT_TYPES:
        raise ValueError("invalid_account_type")

    return ACCOUNT_SUBTYPES_MAP.get(account_type, [])


def create_account_inline(
    user_id: int,
    name: str,
    account_type: str,
    account_subtype: str | None = None,
    category_id: int | None = None,
    category_name_new: str | None = None,
) -> Account:
    """Inline account creation with optional category support."""
    return create_account(
        user_id=user_id,
        name=name,
        base_type=account_type,
        account_subtype=account_subtype,
        category_id=category_id,
        category_name_new=category_name_new,
    )
