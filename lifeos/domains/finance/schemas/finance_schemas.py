"""Pydantic schemas for finance domain."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------


class CurrencyResponse(BaseModel):
    code: str
    symbol: str
    name: str
    decimal_places: int
    is_base: bool

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------


class AccountCreate(BaseModel):
    user_id: int
    name: str = Field(min_length=1, max_length=255)
    account_type: Literal["asset", "liability", "equity", "income", "expense"]
    category_id: Optional[int] = None
    category_name_new: Optional[str] = Field(default=None, max_length=128)
    account_subtype: Optional[str] = None
    description: Optional[str] = None


class AccountResponse(AccountCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AccountListFilter(BaseModel):
    """Query parameters for GET /accounts list endpoint."""

    account_type: Optional[Literal["asset", "liability", "equity", "income", "expense"]] = None
    account_subtype: Optional[str] = Field(default=None, max_length=64)
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)


class AccountUpdate(BaseModel):
    """Fields editable on an existing account (PATCH /accounts/<id>)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1024)
    account_subtype: Optional[str] = Field(default=None, max_length=64)
    category_id: Optional[int] = None
    category_name_new: Optional[str] = Field(default=None, max_length=128)
    default_currency: Optional[str] = Field(default=None, max_length=3)


# ---------------------------------------------------------------------------
# Exchange rates
# ---------------------------------------------------------------------------


class ExchangeRateCreate(BaseModel):
    from_currency: str = Field(min_length=3, max_length=3)
    to_currency: str = Field(min_length=3, max_length=3)
    rate: Decimal = Field(gt=0)
    effective_date: date


class ExchangeRateResponse(BaseModel):
    id: int
    user_id: int
    from_currency: str
    to_currency: str
    rate: Decimal
    effective_date: date
    source: str

    model_config = ConfigDict(from_attributes=True)


class AccountCategoryCreate(BaseModel):
    base_type: Literal["asset", "liability", "equity", "income", "expense"]
    name: str = Field(min_length=1, max_length=128)
    is_default: bool = False


class AccountCategoryResponse(BaseModel):
    id: int
    name: str
    base_type: str
    is_default: bool
    is_system: bool

    model_config = ConfigDict(from_attributes=True)


class AccountSearchQuery(BaseModel):
    """Query parameters for account search/typeahead."""

    q: Optional[str] = Field(default="", max_length=100, description="Search query (empty returns [])")
    limit: int = Field(default=20, ge=1, le=100, description="Max results")
    include_ml: bool = Field(default=True, description="Include ML suggestions")


class AccountInlineCreate(BaseModel):
    """Request body for inline account creation."""

    name: str = Field(min_length=1, max_length=255, description="Account display name")
    account_type: Literal["asset", "liability", "equity", "income", "expense"] = Field(description="Type of account")
    account_subtype: Optional[str] = Field(default=None, max_length=64)
    category_id: Optional[int] = Field(default=None, description="Existing category ID to assign")
    category_name_new: Optional[str] = Field(default=None, max_length=128)
    description: Optional[str] = Field(default=None, max_length=1024)


class AccountUpdateCategory(BaseModel):
    category_id: Optional[int] = None
    category_name_new: Optional[str] = Field(default=None, max_length=128)


class AccountSearchResult(BaseModel):
    """Single account in search results."""

    id: int
    name: str
    account_type: str
    account_subtype: Optional[str]
    is_existing: bool = True

    model_config = ConfigDict(from_attributes=True)


class AccountSubtypesResponse(BaseModel):
    account_type: str
    subtypes: List[str]


# ---------------------------------------------------------------------------
# Journal lines and entries
# ---------------------------------------------------------------------------


class JournalLineSchema(BaseModel):
    account_id: int
    debit: float = Field(0, ge=0)
    credit: float = Field(0, ge=0)
    memo: Optional[str] = None
    currency_code: Optional[str] = Field(default=None, max_length=3)


class JournalEntryCreate(BaseModel):
    user_id: int
    description: Optional[str] = None
    lines: List[JournalLineSchema]


class JournalEntryLineInput(BaseModel):
    account_id: int
    dc: Literal["D", "C"]
    amount: Decimal = Field(gt=0)
    memo: Optional[str] = Field(default=None, max_length=512)
    currency_code: Optional[str] = Field(default=None, max_length=3)


class JournalEntryCreateRequest(BaseModel):
    user_id: int
    description: Optional[str] = Field(default=None, max_length=512)
    posted_at: Optional[datetime] = None
    lines: List[JournalEntryLineInput] = Field(min_length=2, max_length=100)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------


class TransactionCreate(BaseModel):
    """Simple two-account transaction (auto-generates a balanced journal entry)."""

    user_id: int
    debit_account_id: int
    credit_account_id: int
    amount: float = Field(gt=0)
    # ISO 4217 code. Defaults to user's base currency if omitted.
    currency_code: Optional[str] = Field(default=None, max_length=3)
    description: Optional[str] = Field(default=None, max_length=512)
    occurred_at: Optional[datetime] = None
    counterparty: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=128)
    suggested_account_ids: Optional[list[int]] = None


class SplitLineCreate(BaseModel):
    """One debit leg in a split transaction."""

    account_id: int
    amount: float = Field(gt=0)
    memo: Optional[str] = Field(default=None, max_length=512)


class SplitTransactionCreate(BaseModel):
    """Transaction split across multiple expense/debit accounts.

    The user provides one source (credit) account and N destination (debit)
    accounts. The sum of split_lines must equal total_amount (tolerance 0.005).
    """

    user_id: int
    credit_account_id: int
    total_amount: float = Field(gt=0)
    currency_code: Optional[str] = Field(default=None, max_length=3)
    description: Optional[str] = Field(default=None, max_length=512)
    occurred_at: Optional[datetime] = None
    counterparty: Optional[str] = Field(default=None, max_length=255)
    split_lines: List[SplitLineCreate] = Field(min_length=2, max_length=50)


class TransferTransactionCreate(BaseModel):
    """Move funds between two of the user's own accounts (no income/expense).

    Both accounts must be of type 'asset' or 'liability'.
    """

    user_id: int
    from_account_id: int
    to_account_id: int
    amount: float = Field(gt=0)
    currency_code: Optional[str] = Field(default=None, max_length=3)
    description: Optional[str] = Field(default=None, max_length=512)
    occurred_at: Optional[datetime] = None


class TransactionUpdate(BaseModel):
    """Fields editable within the 24-hour grace period.

    Amount and account changes require void + re-entry to preserve the
    double-entry audit trail.
    """

    description: Optional[str] = Field(default=None, max_length=512)
    counterparty: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=128)
    occurred_at: Optional[datetime] = None


class TransactionVoidRequest(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=512)


class TransactionListFilter(BaseModel):
    """Query parameters for GET /transactions."""

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    account_id: Optional[int] = None
    category: Optional[str] = Field(default=None, max_length=128)
    counterparty: Optional[str] = Field(default=None, max_length=255)
    currency_code: Optional[str] = Field(default=None, max_length=3)
    min_amount: Optional[float] = Field(default=None, ge=0)
    max_amount: Optional[float] = Field(default=None, ge=0)
    source: Optional[str] = Field(default=None, max_length=32)
    include_void: bool = False
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    currency_code: Optional[str]
    description: Optional[str]
    occurred_at: datetime
    journal_entry_id: Optional[int]
    counterparty: Optional[str]
    category: Optional[str]
    source: str
    is_void: bool
    void_of_id: Optional[int]
    edited_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------


class ScheduleRowCreate(BaseModel):
    account_id: int
    event_date: date
    amount: float
    memo: Optional[str] = None
    currency_code: Optional[str] = Field(default=None, max_length=3)


class ScheduleRowUpdate(BaseModel):
    account_id: Optional[int] = None
    event_date: Optional[date] = None
    amount: Optional[float] = None
    memo: Optional[str] = None
    currency_code: Optional[str] = Field(default=None, max_length=3)


class ForecastParams(BaseModel):
    days: int = Field(default=30, ge=1, le=365)


# ---------------------------------------------------------------------------
# Receivables
# ---------------------------------------------------------------------------


class ReceivableCreate(BaseModel):
    counterparty: str
    principal: float
    currency_code: Optional[str] = Field(default=None, max_length=3)
    start_date: date
    due_date: Optional[date] = None
    interest_rate: Optional[float] = None


class ReceivableUpdate(BaseModel):
    counterparty: Optional[str] = None
    principal: Optional[float] = None
    currency_code: Optional[str] = Field(default=None, max_length=3)
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    interest_rate: Optional[float] = None


class ReceivableEntryCreate(BaseModel):
    amount: float
    currency_code: Optional[str] = Field(default=None, max_length=3)
    entry_date: date
    memo: Optional[str] = None


class ReceivableResponse(BaseModel):
    id: int
    counterparty: str
    principal: float
    currency_code: Optional[str]
    start_date: date
    due_date: Optional[date]
    interest_rate: Optional[float]

    model_config = ConfigDict(from_attributes=True)


class ReceivableEntryResponse(BaseModel):
    id: int
    tracker_id: int
    entry_date: date
    amount: float
    currency_code: Optional[str]
    memo: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Trial balance
# ---------------------------------------------------------------------------


class TrialBalanceFilter(BaseModel):
    as_of: Optional[date] = None


class PeriodBalanceFilter(BaseModel):
    start: date
    end: date


class TrialBalanceRow(BaseModel):
    account_id: int
    account_name: str
    account_code: Optional[str] = None
    category_name: Optional[str] = None
    normal_balance: str
    debit: float
    credit: float
    net: float
