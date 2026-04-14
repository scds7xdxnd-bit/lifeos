"""Finance accounting models (double-entry)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class FinanceCurrency(db.Model):
    """ISO 4217 currency reference data.

    ``is_base`` marks the system default currency. Users set their personal
    base currency via ``user_preference`` key ``finance.base_currency``
    (falls back to the system base if unset).
    """

    __tablename__ = "finance_currency"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(db.String(3), unique=True, nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(db.String(8), nullable=False)
    name: Mapped[str] = mapped_column(db.String(64), nullable=False)
    decimal_places: Mapped[int] = mapped_column(nullable=False, default=2)
    is_base: Mapped[bool] = mapped_column(nullable=False, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FinanceCurrency {self.code}>"


class FinanceExchangeRate(db.Model):
    """User-scoped manual FX rates.

    Rates are locked at transaction creation time (``exchange_rate_to_base``
    on Transaction / JournalLine). This table is the source for that lock.

    ``from_currency`` → ``to_currency`` = ``rate`` as of ``effective_date``.
    The lookup always picks the most recent rate on or before the transaction date.

    Phase 2: manual entry only. Phase 6 will add API-synced rates (source='api').
    """

    __tablename__ = "finance_exchange_rate"
    __table_args__ = (
        db.Index(
            "ix_finance_exchange_rate_user_from_to_date",
            "user_id",
            "from_currency",
            "to_currency",
            "effective_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False, index=True)
    from_currency: Mapped[str] = mapped_column(db.String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(db.String(3), nullable=False)
    # High-precision decimal: e.g. 1316.50000000 for KRW/USD
    rate: Mapped[Decimal] = mapped_column(db.Numeric(19, 10), nullable=False)
    effective_date: Mapped[date] = mapped_column(nullable=False)
    # 'manual' now; 'api' in Phase 6
    source: Mapped[str] = mapped_column(db.String(20), nullable=False, default="manual")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FinanceExchangeRate {self.from_currency}/{self.to_currency} {self.rate}>"


class AccountCategory(db.Model):
    __tablename__ = "finance_account_category"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "base_type",
            "slug",
            name="uq_finance_account_category_user_base_slug",
        ),
        db.Index(
            "ix_finance_account_category_user_base_default",
            "user_id",
            "base_type",
            "is_default",
        ),
        db.Index("ix_finance_account_category_user_base_name", "user_id", "base_type", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=True)
    code: Mapped[str] = mapped_column(db.String(16), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    slug: Mapped[str] = mapped_column(db.String(128), nullable=False)
    base_type: Mapped[str] = mapped_column(db.String(16), nullable=False)
    normal_balance: Mapped[str] = mapped_column(db.String(8), nullable=False, default="debit")
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_system: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Account(db.Model):
    __tablename__ = "finance_account"
    __table_args__ = (
        db.Index("ix_finance_account_user_type", "user_id", "account_type"),
        db.Index("ix_finance_account_user_normalized_name", "user_id", "normalized_name"),
        db.Index("ix_finance_account_user_category", "user_id", "category_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column(db.ForeignKey("finance_account_category.id"), nullable=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    code: Mapped[str] = mapped_column(db.String(32), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(db.Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    # Account's default currency. NULL = user's base currency (resolved at read time).
    default_currency: Mapped[Optional[str]] = mapped_column(db.String(3), nullable=True)

    account_type: Mapped[str] = mapped_column(db.String(16), nullable=False, default="asset", index=True)
    # Allowed values: 'asset', 'liability', 'equity', 'income', 'expense'

    account_subtype: Mapped[str | None] = mapped_column(db.String(64), nullable=True)
    # Examples: 'cash', 'bank', 'loan', 'credit_card', 'salary', 'investment', etc.

    normalized_name: Mapped[str] = mapped_column(db.String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    category: Mapped[AccountCategory] = relationship("AccountCategory")
    journal_lines: Mapped[list["JournalLine"]] = relationship("JournalLine", back_populates="account")

    @property
    def base_type(self) -> str:
        return self.account_type

    @base_type.setter
    def base_type(self, value: str) -> None:
        self.account_type = value


class JournalEntry(db.Model):
    __tablename__ = "finance_journal_entry"
    __table_args__ = (db.Index("ix_finance_journal_entry_user_posted_at", "user_id", "posted_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(db.Text)
    posted_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    lines: Mapped[list["JournalLine"]] = relationship(
        "JournalLine", back_populates="entry", cascade="all, delete-orphan"
    )

    @property
    def is_balanced(self) -> bool:
        debit = sum(line.debit or 0 for line in self.lines)
        credit = sum(line.credit or 0 for line in self.lines)
        return round(debit - credit, 2) == 0


class JournalLine(db.Model):
    __tablename__ = "finance_journal_line"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(db.ForeignKey("finance_journal_entry.id"), index=True, nullable=False)
    account_id: Mapped[int] = mapped_column(db.ForeignKey("finance_account.id"), index=True, nullable=False)
    debit: Mapped[float] = mapped_column(db.Numeric(18, 2), default=0)
    credit: Mapped[float] = mapped_column(db.Numeric(18, 2), default=0)
    memo: Mapped[str | None] = mapped_column(db.Text)
    # Currency of this line's amounts. NULL → inherited from parent transaction → user's base currency.
    currency_code: Mapped[Optional[str]] = mapped_column(db.String(3), nullable=True)
    # FX rate from currency_code to user's base currency, locked at posting time. NULL = 1.0 (same currency).
    exchange_rate_to_base: Mapped[Optional[Decimal]] = mapped_column(db.Numeric(19, 10), nullable=True)

    entry: Mapped[JournalEntry] = relationship(JournalEntry, back_populates="lines")
    account: Mapped[Account] = relationship("Account", back_populates="journal_lines")


class Transaction(db.Model):
    __tablename__ = "finance_transaction"
    __table_args__ = (
        db.Index("ix_finance_transaction_user_occurred_at", "user_id", "occurred_at"),
        db.Index("ix_finance_transaction_calendar_event", "calendar_event_id"),
        db.Index("ix_finance_transaction_is_void", "is_void"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(db.Numeric(18, 2), nullable=False)
    # ISO 4217 code. NULL on legacy rows = user's base currency.
    currency_code: Mapped[Optional[str]] = mapped_column(db.String(3), nullable=True)
    # FX rate from currency_code to user's base currency, locked at transaction creation. NULL = 1.0.
    exchange_rate_to_base: Mapped[Optional[Decimal]] = mapped_column(db.Numeric(19, 10), nullable=True)
    description: Mapped[str | None] = mapped_column(db.Text)
    occurred_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    journal_entry_id: Mapped[int | None] = mapped_column(db.ForeignKey("finance_journal_entry.id"))
    counterparty: Mapped[str | None] = mapped_column(db.String(255))
    category: Mapped[str | None] = mapped_column(db.String(128))

    # Calendar inference fields
    source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
    # Values: 'manual', 'calendar_inferred', 'import', 'api'
    calendar_event_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("calendar_event.id", ondelete="SET NULL"), nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
    inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
    # Values: 'pending', 'confirmed', 'rejected', None for manual

    # Void / edit audit fields
    is_void: Mapped[bool] = mapped_column(nullable=False, default=False)
    void_of_id: Mapped[int | None] = mapped_column(nullable=True)
    edited_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    journal_entry: Mapped[JournalEntry] = relationship(JournalEntry)


class TrialBalanceSetting(db.Model):
    __tablename__ = "finance_trial_balance_setting"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    month: Mapped[str] = mapped_column(db.String(7), nullable=False)  # YYYY-MM
    auto_rollup: Mapped[bool] = mapped_column(default=True)
