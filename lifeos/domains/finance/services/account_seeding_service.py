"""Seed a default Chart of Accounts for new users.

This service creates a personal-finance account tree on first login or on
explicit request. It is idempotent: calling it again for a user who already
has accounts is a no-op.

Account codes are assigned using the same taxonomy as `assign_account_code`:

    T BB SS  (5 digits)
    T  = type digit  (1=asset 2=liability 3=equity 4=income 5=expense)
    BB = subtype block (standard blocks 00-19)
    SS = sequence within block (01-99)

Because we seed from scratch, block counters are maintained in-memory rather
than querying the DB for each account, keeping seeding fast.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from lifeos.domains.finance.events import FINANCE_ACCOUNTS_SEEDED
from lifeos.domains.finance.models.accounting_models import Account, AccountCategory
from lifeos.domains.finance.services.accounting_service import (
    _STANDARD_BLOCK,
    _TYPE_PREFIX,
)
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox

# ---------------------------------------------------------------------------
# Default tree definition
# ---------------------------------------------------------------------------
# Format: (base_type, category_name, is_default, [(account_name, subtype), ...])
# No hardcoded codes — they are computed from the taxonomy at seed time.

_DEFAULT_TREE: List[Tuple[str, str, bool, List[Tuple[str, str]]]] = [
    # ── Assets ──────────────────────────────────────────────────────────────
    (
        "asset",
        "Cash & Bank",
        True,
        [
            ("Checking Account", "bank"),
            ("Savings Account", "savings"),
            ("Cash on Hand", "cash"),
        ],
    ),
    (
        "asset",
        "Investments",
        False,
        [
            ("Brokerage Account", "investment"),
            ("Retirement Account", "investment"),
        ],
    ),
    (
        "asset",
        "Receivables",
        False,
        [
            ("Loans Given Out", "receivable"),
        ],
    ),
    (
        "asset",
        "Prepaid & Other Assets",
        False,
        [
            ("Prepaid Expenses", "prepaid"),
            ("Security Deposit", "other"),
        ],
    ),
    # ── Liabilities ─────────────────────────────────────────────────────────
    (
        "liability",
        "Credit Cards",
        True,
        [
            ("Credit Card", "credit_card"),
        ],
    ),
    (
        "liability",
        "Loans & Mortgages",
        False,
        [
            ("Student Loan", "loan"),
            ("Mortgage", "mortgage"),
        ],
    ),
    (
        "liability",
        "Payables & Subscriptions",
        False,
        [
            ("Rent Payable", "payable"),
            ("Subscription Bills", "payable"),
        ],
    ),
    # ── Equity ──────────────────────────────────────────────────────────────
    (
        "equity",
        "Owner's Equity",
        True,
        [
            ("Opening Balance Equity", "contributed"),
            ("Retained Earnings", "retained_earnings"),
        ],
    ),
    # ── Income ──────────────────────────────────────────────────────────────
    (
        "income",
        "Earned Income",
        True,
        [
            ("Salary / Wages", "salary"),
            ("Scholarship", "scholarship"),
            ("Allowance", "allowance"),
            ("Bonus", "bonus"),
        ],
    ),
    (
        "income",
        "Passive & Other Income",
        False,
        [
            ("Investment Returns", "investment"),
            ("Side Income", "business"),
            ("Other Income", "other"),
        ],
    ),
    # ── Expenses ────────────────────────────────────────────────────────────
    (
        "expense",
        "Housing",
        True,
        [
            ("Rent / Housing", "rent"),
            ("Utilities", "utilities"),
        ],
    ),
    (
        "expense",
        "Food & Dining",
        False,
        [
            ("Groceries", "groceries"),
            ("Dining Out", "dining"),
        ],
    ),
    (
        "expense",
        "Transportation",
        False,
        [
            ("Public Transport", "transportation"),
            ("Car Expenses", "transportation"),
        ],
    ),
    (
        "expense",
        "Education",
        False,
        [
            ("Tuition & Fees", "education"),
            ("Books & Supplies", "education"),
        ],
    ),
    (
        "expense",
        "Personal Care",
        False,
        [
            ("Personal Care", "personal_care"),
        ],
    ),
    (
        "expense",
        "Health & Medical",
        False,
        [
            ("Health Insurance", "insurance"),
            ("Medical Expenses", "health"),
        ],
    ),
    (
        "expense",
        "Entertainment",
        False,
        [
            ("Streaming Services", "subscriptions"),
            ("Recreation", "entertainment"),
        ],
    ),
    (
        "expense",
        "Financial",
        False,
        [
            ("Insurance Premiums", "insurance"),
            ("Gifts & Donations", "gifts"),
        ],
    ),
    (
        "expense",
        "Miscellaneous",
        False,
        [
            ("Miscellaneous", "other"),
        ],
    ),
]

_BASE_TYPE_NORMAL_BALANCE = {
    "asset": "debit",
    "expense": "debit",
    "liability": "credit",
    "equity": "credit",
    "income": "credit",
}


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _category_code(user_id: int, base_type: str, slug: str) -> str:
    return f"U{user_id}_{base_type[:3]}_{slug[:8]}"


def _seed_code(base_type: str, subtype: str, block_counters: Dict[tuple, int]) -> str:
    """Return the next sequential 5-digit code using the taxonomy block map.

    Uses an in-memory counter dict to avoid per-account DB round-trips during
    bulk seeding. block_counters is mutated in place.
    """
    T = _TYPE_PREFIX[base_type]
    block = _STANDARD_BLOCK.get(base_type, {}).get(subtype, _STANDARD_BLOCK.get(base_type, {}).get("other", 9))
    key = (T, block)
    seq = block_counters.get(key, 0) + 1
    block_counters[key] = seq
    return f"{T * 10000 + block * 100 + seq:05d}"


def seed_default_chart_of_accounts(user_id: int) -> dict:
    """Create the default account tree for *user_id* if they have no accounts yet.

    Returns ``{"seeded": bool, "account_count": int, "category_count": int}``.
    No-op if the user already has any accounts (returns seeded=False).
    """
    existing = Account.query.filter_by(user_id=user_id).count()
    if existing > 0:
        return {"seeded": False, "account_count": 0, "category_count": 0}

    category_count = 0
    account_count = 0
    # In-memory block counters: (type_digit, block_number) → next_seq
    block_counters: Dict[tuple, int] = {}

    for base_type, category_name, is_default, accounts in _DEFAULT_TREE:
        slug = _slugify(category_name)
        cat_code = _category_code(user_id, base_type, slug)

        category = AccountCategory.query.filter_by(code=cat_code).first()
        if category is None:
            category = AccountCategory(
                user_id=user_id,
                code=cat_code,
                name=category_name,
                slug=slug,
                base_type=base_type,
                normal_balance=_BASE_TYPE_NORMAL_BALANCE[base_type],
                is_default=is_default,
                is_system=False,
            )
            db.session.add(category)
            db.session.flush()
            category_count += 1

        for acct_name, subtype in accounts:
            code = _seed_code(base_type, subtype, block_counters)
            acct = Account(
                user_id=user_id,
                category_id=category.id,
                name=acct_name,
                code=code,
                account_type=base_type,
                account_subtype=subtype,
                normalized_name=acct_name.lower().strip(),
                is_active=True,
            )
            db.session.add(acct)
            account_count += 1

    db.session.flush()

    enqueue_outbox(
        FINANCE_ACCOUNTS_SEEDED,
        {
            "user_id": user_id,
            "account_count": account_count,
            "category_count": category_count,
            "payload_version": "v1",
        },
        user_id=user_id,
    )

    db.session.commit()
    return {"seeded": True, "account_count": account_count, "category_count": category_count}
