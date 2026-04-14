"""Currency service: user base currency preferences + exchange rate CRUD."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from typing import List, Optional

from lifeos.domains.finance.events import FINANCE_EXCHANGE_RATE_SET
from lifeos.domains.finance.models.accounting_models import FinanceCurrency, FinanceExchangeRate
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox

# Key stored in user_preference table
_BASE_CURRENCY_PREF_KEY = "finance.base_currency"
_SYSTEM_DEFAULT_CURRENCY = "USD"


# ---------------------------------------------------------------------------
# User base currency
# ---------------------------------------------------------------------------


def get_user_base_currency(user_id: int) -> str:
    """Return the user's base currency code.

    Falls back to the system base currency (finance_currency.is_base=True),
    then hard-codes USD if no system base is configured.
    """
    # Lazy import to avoid circular dependency; UserPreference is in the user domain.
    try:
        from lifeos.core.user_preferences import get_preference  # type: ignore

        raw = get_preference(user_id, _BASE_CURRENCY_PREF_KEY)
        if raw:
            data = json.loads(raw) if isinstance(raw, str) else raw
            code = data.get("currency") if isinstance(data, dict) else str(data)
            if code:
                return code.upper()
    except Exception:  # pragma: no cover
        pass

    # Fall back to system base currency
    system_base = FinanceCurrency.query.filter_by(is_base=True).first()
    return system_base.code if system_base else _SYSTEM_DEFAULT_CURRENCY


def set_user_base_currency(user_id: int, currency_code: str) -> str:
    """Persist the user's preferred base currency.

    Args:
        user_id: Owning user.
        currency_code: ISO 4217 code (3 chars).

    Returns:
        Normalised currency code that was saved.

    Raises:
        ValueError("invalid_currency") if the code is not in finance_currency table.
    """
    code = (currency_code or "").strip().upper()
    if not code:
        raise ValueError("invalid_currency")

    currency = FinanceCurrency.query.filter_by(code=code).first()
    if not currency:
        raise ValueError("invalid_currency")

    try:
        from lifeos.core.user_preferences import set_preference  # type: ignore

        set_preference(user_id, _BASE_CURRENCY_PREF_KEY, json.dumps({"currency": code}))
    except Exception:  # pragma: no cover
        pass

    return code


# ---------------------------------------------------------------------------
# Exchange rates
# ---------------------------------------------------------------------------


def create_exchange_rate(
    user_id: int,
    from_currency: str,
    to_currency: str,
    rate: Decimal,
    effective_date: date,
) -> FinanceExchangeRate:
    """Create or update a manual exchange rate entry.

    A rate for the same (user_id, from_currency, to_currency, effective_date) tuple
    is overwritten rather than duplicated.

    Args:
        user_id: Owning user.
        from_currency: Source ISO 4217 code.
        to_currency: Target ISO 4217 code.
        rate: Conversion multiplier (from → to). Must be > 0.
        effective_date: The date this rate is valid from.

    Returns:
        Persisted FinanceExchangeRate row.

    Raises:
        ValueError("invalid_currency") if either code is unknown.
        ValueError("same_currency") if from == to.
        ValueError("invalid_rate") if rate <= 0.
    """
    from_code = (from_currency or "").strip().upper()
    to_code = (to_currency or "").strip().upper()

    if from_code == to_code:
        raise ValueError("same_currency")
    if rate <= 0:
        raise ValueError("invalid_rate")

    for code in (from_code, to_code):
        if not FinanceCurrency.query.filter_by(code=code).first():
            raise ValueError("invalid_currency")

    existing = FinanceExchangeRate.query.filter_by(
        user_id=user_id,
        from_currency=from_code,
        to_currency=to_code,
        effective_date=effective_date,
    ).first()

    if existing:
        existing.rate = rate
        fx_row = existing
    else:
        fx_row = FinanceExchangeRate(
            user_id=user_id,
            from_currency=from_code,
            to_currency=to_code,
            rate=rate,
            effective_date=effective_date,
            source="manual",
        )
        db.session.add(fx_row)

    db.session.flush()

    enqueue_outbox(
        FINANCE_EXCHANGE_RATE_SET,
        {
            "rate_id": fx_row.id,
            "user_id": user_id,
            "from_currency": from_code,
            "to_currency": to_code,
            "rate": str(rate),
            "effective_date": effective_date.isoformat(),
            "payload_version": "v1",
        },
        user_id=user_id,
    )

    db.session.commit()
    return fx_row


def get_latest_rate(
    user_id: int,
    from_currency: str,
    to_currency: str,
    as_of: Optional[date] = None,
) -> Optional[Decimal]:
    """Return the most recent manual rate on or before *as_of*.

    Returns ``None`` if no rate exists (caller should treat as 1.0 = same currency
    or raise an appropriate error).
    """
    as_of = as_of or date.today()
    row = (
        FinanceExchangeRate.query.filter_by(
            user_id=user_id,
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper(),
        )
        .filter(FinanceExchangeRate.effective_date <= as_of)
        .order_by(FinanceExchangeRate.effective_date.desc())
        .first()
    )
    return row.rate if row else None


def list_exchange_rates(
    user_id: int,
    from_currency: Optional[str] = None,
    to_currency: Optional[str] = None,
) -> List[FinanceExchangeRate]:
    """Return all manual exchange rates for a user, optionally filtered by currency pair."""
    q = FinanceExchangeRate.query.filter_by(user_id=user_id)
    if from_currency:
        q = q.filter_by(from_currency=from_currency.upper())
    if to_currency:
        q = q.filter_by(to_currency=to_currency.upper())
    return q.order_by(
        FinanceExchangeRate.from_currency.asc(),
        FinanceExchangeRate.to_currency.asc(),
        FinanceExchangeRate.effective_date.desc(),
    ).all()


def list_currencies() -> List[FinanceCurrency]:
    """Return all supported currencies ordered by code."""
    return FinanceCurrency.query.order_by(FinanceCurrency.code.asc()).all()


def get_currency(code: str) -> Optional[FinanceCurrency]:
    """Return a single currency by ISO 4217 code."""
    return FinanceCurrency.query.filter_by(code=code.upper()).first()
