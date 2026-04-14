"""Accounting service: double-entry operations."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List, Optional, Tuple

from lifeos.core.read_cache import read_cache
from lifeos.domains.finance.events import (
    FINANCE_ACCOUNT_CATEGORY_UPDATED,
    FINANCE_ACCOUNT_CREATED,
    FINANCE_ACCOUNT_DEACTIVATED,
    FINANCE_ACCOUNT_UPDATED,
    FINANCE_JOURNAL_POSTED,
)
from lifeos.domains.finance.models.accounting_models import (
    Account,
    AccountCategory,
    JournalEntry,
    JournalLine,
)
from lifeos.domains.finance.services.suggestion_service import suggest_accounts
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox

FINANCE_READ_CACHE_SCOPE = "finance.reads"

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
    read_cache.bump(FINANCE_READ_CACHE_SCOPE, user_id)
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
    "asset": [
        "cash",
        "bank",
        "savings",
        "investment",
        "receivable",
        "prepaid",
        "property",
        "other",
    ],
    "liability": ["credit_card", "loan", "mortgage", "payable", "other"],
    "equity": ["contributed", "retained_earnings", "other"],
    "income": ["salary", "allowance", "bonus", "scholarship", "investment", "business", "rental", "other"],
    "expense": [
        "rent",
        "utilities",
        "groceries",
        "dining",
        "transportation",
        "education",
        "personal_care",
        "health",
        "insurance",
        "entertainment",
        "subscriptions",
        "gifts",
        "other",
    ],
}

# ---------------------------------------------------------------------------
# Account code taxonomy
# ---------------------------------------------------------------------------
# Code format:  T BB SS  (5 digits, all numeric)
#   T  = type digit:  1=asset 2=liability 3=equity 4=income 5=expense
#   BB = subtype block (00-19 reserved for standard subtypes,
#                       20-99 for user-defined subtypes)
#   SS = sequence within block (01-99)
#
# Example: 10001 = first asset/cash-bank account
#          50101 = first expense/groceries account
#          52001 = first expense/user-defined-block-20 account
#
# Currency does NOT affect the code — it is stored on the account row
# (default_currency) and is a separate dimension.  Two accounts of the
# same subtype in different currencies receive consecutive sequence numbers
# within the same block (e.g. 10001 USD checking, 10002 KRW checking).

_TYPE_PREFIX: Dict[str, int] = {
    "asset": 1,
    "liability": 2,
    "equity": 3,
    "income": 4,
    "expense": 5,
}

# Standard subtype → block index (00-19)
_STANDARD_BLOCK: Dict[str, Dict[str, int]] = {
    "asset": {
        "cash": 0,
        "bank": 0,
        "savings": 0,  # Cash & Bank
        "investment": 1,  # Investments
        "receivable": 2,  # Receivables
        "prepaid": 3,  # Prepaid & other current
        "property": 4,  # Fixed / property
        "other": 9,
    },
    "liability": {
        "credit_card": 0,  # Credit cards
        "loan": 1,
        "mortgage": 1,  # Loans & mortgages
        "payable": 2,  # Accounts payable / subscriptions
        "other": 9,
    },
    "equity": {
        "contributed": 0,  # Opening balance / paid-in
        "retained_earnings": 1,
        "other": 9,
    },
    "income": {
        "salary": 0,
        "allowance": 0,
        "bonus": 0,
        "scholarship": 0,  # Earned income
        "investment": 1,  # Passive / investment
        "business": 2,
        "rental": 2,  # Business / side income
        "other": 9,
    },
    "expense": {
        "rent": 0,
        "utilities": 0,  # Housing
        "groceries": 1,
        "dining": 1,  # Food & dining
        "transportation": 2,  # Transport
        "education": 3,  # Education
        "personal_care": 4,  # Personal care
        "health": 5,
        "insurance": 5,  # Health & medical
        "entertainment": 6,
        "subscriptions": 6,  # Entertainment
        "gifts": 7,  # Gifts & donations
        "other": 9,
    },
}

# User-defined subtype blocks start here (leaves 00-19 for standard types)
_USER_BLOCK_START = 20


def _get_subtype_block(user_id: int, account_type: str, account_subtype: str | None) -> int:
    """Return the BB block number for the given type + subtype combination.

    Standard subtypes map to fixed blocks.  Unknown (user-defined) subtypes
    are assigned the next available block in [_USER_BLOCK_START, 99] by
    scanning existing account codes for this user+type pair.
    """
    subtype = (account_subtype or "").strip().lower() or None
    standard = _STANDARD_BLOCK.get(account_type, {})

    if subtype and subtype in standard:
        return standard[subtype]
    if not subtype:
        return standard.get("other", 9)

    # User-defined: check if we already allocated a block for this subtype
    T = _TYPE_PREFIX[account_type]
    existing = (
        Account.query.filter_by(user_id=user_id, account_type=account_type, account_subtype=subtype)
        .filter(Account.code.isnot(None))
        .with_entities(Account.code)
        .first()
    )
    if existing and existing.code:
        try:
            c = int(existing.code)
            if c // 10000 == T:
                block = (c % 10000) // 100
                if block >= _USER_BLOCK_START:
                    return block
        except (ValueError, TypeError):
            pass

    # Allocate a new block: find the highest user-defined block in use for
    # this user+type, then add 1.  Start at _USER_BLOCK_START.
    used_blocks: set[int] = set()
    all_codes = (
        Account.query.filter_by(user_id=user_id, account_type=account_type)
        .filter(Account.code.isnot(None))
        .with_entities(Account.code)
        .all()
    )
    for (code_str,) in all_codes:
        try:
            c = int(code_str)
            if c // 10000 == T:
                block = (c % 10000) // 100
                if block >= _USER_BLOCK_START:
                    used_blocks.add(block)
        except (ValueError, TypeError):
            pass

    for b in range(_USER_BLOCK_START, 100):
        if b not in used_blocks:
            return b
    return standard.get("other", 9)  # fallback: collapse into "other"


def assign_account_code(user_id: int, account_type: str, account_subtype: str | None) -> str:
    """Return the next available 5-digit account code for the given taxonomy.

    Code anatomy:  T BB SS
      T  – type digit (1-5)
      BB – subtype block (00-99)
      SS – sequence within block (01-99)

    The function finds the lowest unused SS in the target block for this user.
    Currency is not encoded; same-subtype accounts in different currencies
    simply receive consecutive sequence numbers.
    """
    T = _TYPE_PREFIX.get(account_type, 5)
    block = _get_subtype_block(user_id, account_type, account_subtype)
    block_base = T * 10000 + block * 100  # e.g. 10000 for asset/bank

    # Collect codes already in this block for this user
    all_codes = (
        Account.query.filter_by(user_id=user_id, account_type=account_type)
        .filter(Account.code.isnot(None))
        .with_entities(Account.code)
        .all()
    )
    used_seq: set[int] = set()
    for (code_str,) in all_codes:
        try:
            c = int(code_str)
            seq = c - block_base
            if 1 <= seq <= 99:
                used_seq.add(seq)
        except (ValueError, TypeError):
            pass

    for seq in range(1, 100):
        if seq not in used_seq:
            return f"{block_base + seq:05d}"

    # All 99 slots full — append an overflow suffix
    return f"{block_base + 99:05d}"


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

    base_query = Account.query.filter(Account.user_id == user_id).filter(Account.is_active.is_(True))

    # Prefix matches (ordered first, newest first)
    prefix_matches = (
        base_query.filter(Account.normalized_name.startswith(normalized_query))
        .order_by(Account.created_at.desc())
        .limit(limit)
        .all()
    )

    if len(prefix_matches) >= limit:
        return prefix_matches[:limit]

    # Substring matches (fill remaining slots)
    remaining = limit - len(prefix_matches)
    substring_matches = (
        base_query.filter(Account.normalized_name.contains(normalized_query))
        .filter(~Account.normalized_name.startswith(normalized_query))
        .order_by(Account.created_at.desc())
        .limit(remaining)
        .all()
    )

    results = prefix_matches + substring_matches
    if len(results) >= limit:
        return results[:limit]

    remaining = limit - len(results)
    tokens = re.findall(r"[a-z0-9]+", normalized_query)
    if not tokens:
        return results
    pattern = "%" + "%".join(tokens) + "%"
    fallback_query = base_query.filter(Account.name.ilike(pattern))
    if results:
        fallback_query = fallback_query.filter(~Account.id.in_([acc.id for acc in results]))
    fallback_matches = fallback_query.order_by(Account.created_at.desc()).limit(remaining).all()

    return results + fallback_matches


def get_suggested_accounts(user_id: int, query: str, limit: int = 10, include_ml: bool = True) -> List[dict]:
    """Get suggested accounts combining existing search + optional ML suggestions."""
    query = (query or "").strip()
    # Derive a safe search limit: if caller asks for fewer than 3, search with that limit (never negative).
    search_limit = limit if limit <= 2 else max(1, limit - 2)

    # Get existing accounts
    try:
        existing = search_accounts(user_id, query, limit=search_limit)
    except ValueError:
        return []

    def _serialize(acc: Account) -> dict:
        return {
            "id": acc.id,
            "name": acc.name,
            "account_type": acc.account_type,
            "account_subtype": acc.account_subtype,
            "is_existing": True,
        }

    results = [_serialize(acc) for acc in existing]
    if not include_ml:
        return results[:limit]

    # Use ML ranking to supplement results (keeping existing semantics for empty/invalid queries).
    if len(results) >= limit:
        return results[:limit]
    if not query:
        return results

    ml_ranked_ids = suggest_accounts(user_id, query) or []
    if not ml_ranked_ids:
        return results[:limit]

    already_added = {item["id"] for item in results}
    # Fetch any accounts not already in the base search to merge by ML rank.
    missing_ids = [acc_id for acc_id in ml_ranked_ids if acc_id not in already_added]
    if missing_ids:
        extra_accounts = (
            Account.query.filter(Account.user_id == user_id)
            .filter(Account.id.in_(missing_ids))
            .filter(Account.is_active.is_(True))
            .all()
        )
        account_map = {acc.id: acc for acc in extra_accounts}
    else:
        account_map = {}

    for acc_id in ml_ranked_ids:
        if len(results) >= limit:
            break
        if acc_id in already_added:
            continue
        account = account_map.get(acc_id)
        if not account:
            continue
        results.append(_serialize(account))
        already_added.add(acc_id)

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
            read_cache.bump(FINANCE_READ_CACHE_SCOPE, user_id)
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
    read_cache.bump(FINANCE_READ_CACHE_SCOPE, user_id)
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
        code=assign_account_code(user_id, base_type, account_subtype),
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
    read_cache.bump(FINANCE_READ_CACHE_SCOPE, user_id)
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
    read_cache.bump(FINANCE_READ_CACHE_SCOPE, user_id)
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


def update_account(
    user_id: int,
    account_id: int,
    name: str | None = None,
    description: str | None = None,
    account_subtype: str | None = None,
    category_id: int | None = None,
    category_name_new: str | None = None,
    default_currency: str | None = None,
) -> Account:
    """Update editable fields on an account (PATCH semantics — only supplied fields change).

    Raises:
        ValueError("not_found") if the account does not belong to user_id.
        ValueError("inactive_account") if the account is deactivated.
        ValueError("invalid_name") if name fails validation.
        ValueError("invalid_account_subtype") if subtype is invalid for this type.
        ValueError("invalid_category") if category_id / category_name_new are invalid.
    """
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        raise ValueError("not_found")
    if not account.is_active:
        raise ValueError("inactive_account")

    changed_fields: List[str] = []

    if name is not None:
        clean_name = (name or "").strip()
        if not clean_name or len(clean_name) > 255:
            raise ValueError("invalid_name")
        account.name = clean_name
        account.normalized_name = _normalize_name(clean_name)
        changed_fields.append("name")

    if description is not None:
        account.description = description.strip() or None
        changed_fields.append("description")

    if account_subtype is not None:
        subtype_clean = (account_subtype or "").strip() or None
        if subtype_clean and subtype_clean not in get_account_subtypes(account.account_type):
            raise ValueError("invalid_account_subtype")
        account.account_subtype = subtype_clean
        changed_fields.append("account_subtype")

    if default_currency is not None:
        account.default_currency = default_currency.strip().upper() or None
        changed_fields.append("default_currency")

    # Category update (mirrors update_account_category logic inline)
    if category_name_new or category_id is not None:
        base_type = account.account_type
        if category_name_new:
            category = create_custom_account_category(user_id, base_type, category_name_new, is_default=False)
        elif category_id:
            category = _get_category_for_user(user_id, category_id)
        else:
            category = None

        if category and category.base_type != base_type:
            raise ValueError("invalid_category")

        account.category_id = category.id if category else None
        changed_fields.append("category_id")

    if not changed_fields:
        return account

    db.session.flush()

    enqueue_outbox(
        FINANCE_ACCOUNT_UPDATED,
        {
            "account_id": account.id,
            "user_id": user_id,
            "fields": changed_fields,
            "updated_at": datetime.utcnow().isoformat(),
            "payload_version": "v1",
        },
        user_id=user_id,
    )

    db.session.commit()
    read_cache.bump(FINANCE_READ_CACHE_SCOPE, user_id)
    return account


def deactivate_account(user_id: int, account_id: int) -> Account:
    """Soft-delete an account by marking it inactive.

    The account is hidden from active lists and blocked from new transactions.
    Historical journal lines remain intact.

    Raises:
        ValueError("not_found") if the account does not belong to user_id.
        ValueError("already_inactive") if the account is already deactivated.
    """
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        raise ValueError("not_found")
    if not account.is_active:
        raise ValueError("already_inactive")

    account.is_active = False
    db.session.flush()

    enqueue_outbox(
        FINANCE_ACCOUNT_DEACTIVATED,
        {
            "account_id": account.id,
            "user_id": user_id,
            "deactivated_at": datetime.utcnow().isoformat(),
            "payload_version": "v1",
        },
        user_id=user_id,
    )

    db.session.commit()
    read_cache.bump(FINANCE_READ_CACHE_SCOPE, user_id)
    return account
