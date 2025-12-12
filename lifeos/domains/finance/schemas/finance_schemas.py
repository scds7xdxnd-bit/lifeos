"""Pydantic schemas for finance domain."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    user_id: int
    name: str = Field(min_length=1, max_length=255)
    account_type: Literal["asset", "liability", "equity", "income", "expense"]
    category_id: Optional[int] = None
    category_name_new: Optional[str] = Field(default=None, max_length=128)
    account_subtype: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class AccountResponse(AccountCreate):
    id: int

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

    q: str = Field(min_length=1, max_length=100, description="Search query")
    limit: int = Field(default=20, ge=1, le=100, description="Max results")
    include_ml: bool = Field(default=True, description="Include ML suggestions")


class AccountInlineCreate(BaseModel):
    """Request body for inline account creation."""

    name: str = Field(min_length=1, max_length=255, description="Account display name")
    account_type: Literal["asset", "liability", "equity", "income", "expense"] = Field(description="Type of account")
    account_subtype: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Optional subtype (e.g., 'cash', 'bank', 'loan')",
    )
    category_id: Optional[int] = Field(default=None, description="Existing category ID to assign")
    category_name_new: Optional[str] = Field(
        default=None,
        max_length=128,
        description="New category name to create and assign",
    )


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
    """Response for GET /finance/accounts/subtypes/<type>."""

    account_type: str
    subtypes: List[str]


class JournalLineSchema(BaseModel):
    account_id: int
    debit: float = Field(0, ge=0)
    credit: float = Field(0, ge=0)
    memo: Optional[str] = None


class JournalEntryCreate(BaseModel):
    user_id: int
    description: Optional[str] = None
    lines: List[JournalLineSchema]


class JournalEntryLineInput(BaseModel):
    account_id: int
    dc: Literal["D", "C"]
    amount: Decimal = Field(gt=0)
    memo: Optional[str] = Field(default=None, max_length=512)


class JournalEntryCreateRequest(BaseModel):
    user_id: int
    description: Optional[str] = Field(default=None, max_length=512)
    posted_at: Optional[datetime] = None
    lines: List[JournalEntryLineInput] = Field(min_length=2, max_length=100)


class TransactionCreate(BaseModel):
    user_id: int
    debit_account_id: int
    credit_account_id: int
    amount: float
    description: Optional[str] = None
    suggested_account_ids: Optional[list[int]] = None


class ScheduleRowCreate(BaseModel):
    account_id: int
    event_date: date
    amount: float
    memo: Optional[str] = None


class ScheduleRowUpdate(BaseModel):
    account_id: Optional[int] = None
    event_date: Optional[date] = None
    amount: Optional[float] = None
    memo: Optional[str] = None


class ForecastParams(BaseModel):
    days: int = Field(default=30, ge=1, le=365)


class ReceivableCreate(BaseModel):
    counterparty: str
    principal: float
    start_date: date
    due_date: Optional[date] = None
    interest_rate: Optional[float] = None


class ReceivableUpdate(BaseModel):
    counterparty: Optional[str] = None
    principal: Optional[float] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    interest_rate: Optional[float] = None


class ReceivableEntryCreate(BaseModel):
    amount: float
    entry_date: date
    memo: Optional[str] = None


class ReceivableResponse(BaseModel):
    id: int
    counterparty: str
    principal: float
    start_date: date
    due_date: Optional[date]
    interest_rate: Optional[float]

    model_config = ConfigDict(from_attributes=True)


class ReceivableEntryResponse(BaseModel):
    id: int
    tracker_id: int
    entry_date: date
    amount: float
    memo: Optional[str]

    model_config = ConfigDict(from_attributes=True)


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
