"""Accounting, journal, receivable, and loan related models."""
import datetime
import uuid
from decimal import Decimal  # noqa: F401  # kept for potential defaults/extensions

from finance_app.extensions import db


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20))
    description = db.Column(db.String(200))
    debit_account = db.Column(db.String(100))
    debit_amount = db.Column(db.Float)
    credit_account = db.Column(db.String(100))
    credit_amount = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    debit_account_id = db.Column(db.Integer, db.ForeignKey("account.id"))
    credit_account_id = db.Column(db.Integer, db.ForeignKey("account.id"))
    date_parsed = db.Column(db.Date)


class AccountSuggestionHint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    kind = db.Column(db.String(10), nullable=False)  # 'debit' or 'credit'
    token = db.Column(db.String(100), nullable=False)
    account_name = db.Column(db.String(120), nullable=False)
    count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)


class SuggestionFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    kind = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text)
    suggested = db.Column(db.String(120))
    actual = db.Column(db.String(120))
    is_correct = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class AccountSuggestionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    currency = db.Column(db.String(10))
    transaction_id = db.Column(db.String(64), index=True)
    line_id = db.Column(db.String(64))
    line_type = db.Column(db.String(10))
    chosen_account = db.Column(db.String(120))
    model_version = db.Column(db.String(64))
    model_path = db.Column(db.String(255))
    probability = db.Column(db.Float)
    raw_features = db.Column(db.JSON)
    predictions = db.Column(db.JSON)
    description = db.Column(db.Text)
    entry_date = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    responded_at = db.Column(db.DateTime)


class AccountCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    side = db.Column(db.String(10), nullable=False, default="both")  # kept for legacy; unused in UI
    order = db.Column(db.Integer, default=0)
    tb_group = db.Column(db.String(20))
    accounts = db.relationship("Account", backref="category", lazy=True)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    code = db.Column(db.String(20))
    name = db.Column(db.String(100), nullable=False)
    side = db.Column(db.String(10), nullable=False, default="both")  # kept for legacy; unused in UI
    category_id = db.Column(db.Integer, db.ForeignKey("account_category.id"))
    order = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    currency_code = db.Column(db.String(10), default="KRW")


class AccountOpeningBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    as_of_date = db.Column(db.Date)


class LoginSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    logout_time = db.Column(db.DateTime)


class TrialBalanceSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    # First TB month (first day of the month). Controls I/E reset behavior.
    first_month = db.Column(db.Date)
    # Date when the user finalized their opening balances (controls calculation cutoff)
    initialized_on = db.Column(db.Date)


class AccountMonthlyBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    opening_bd = db.Column(db.Float, default=0.0)
    period_debit = db.Column(db.Float, default=0.0)
    period_credit = db.Column(db.Float, default=0.0)
    closing_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("user_id", "account_id", "year", "month", name="uq_user_acc_ym"),)


class ReceivableTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    journal_id = db.Column(db.Integer, db.ForeignKey("journal_entry.id"), nullable=False, index=True)
    journal_line_id = db.Column(db.Integer, db.ForeignKey("journal_line.id"), nullable=False, unique=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False, index=True)
    category = db.Column(db.String(20), nullable=False)  # 'receivable' or 'debt'
    contact_name = db.Column(db.String(120))
    transaction_value = db.Column(db.Numeric(18, 2))
    currency_code = db.Column(db.String(10))
    due_date = db.Column(db.Date)
    amount_paid = db.Column(db.Numeric(18, 2))
    payment_dates = db.Column(db.Text)  # JSON-encoded array of ISO date strings
    remaining_amount = db.Column(db.Numeric(18, 2))
    status = db.Column(db.String(20), default="UNPAID")
    notes = db.Column(db.Text)
    linked_line_id = db.Column(db.Integer, db.ForeignKey("journal_line.id"))
    link_kind = db.Column(db.String(20))
    ignored = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ReceivableManualEntry(db.Model):
    __tablename__ = "receivable_manual_entry"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False, index=True)
    category = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency_code = db.Column(db.String(10), nullable=False, default="KRW")
    description = db.Column(db.String(255))
    reference = db.Column(db.String(120))
    memo = db.Column(db.Text)
    contact_name = db.Column(db.String(120))
    transaction_value = db.Column(db.Numeric(18, 2))
    due_date = db.Column(db.Date)
    payment_dates = db.Column(db.Text)
    notes = db.Column(db.Text)
    date = db.Column(db.String(20))
    date_parsed = db.Column(db.Date)
    status = db.Column(db.String(20), default="UNPAID")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class LoanGroup(db.Model):
    __tablename__ = "loan_group"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    direction = db.Column(db.String(20), nullable=False)  # receivable or payable
    counterparty = db.Column(db.String(160))
    currency = db.Column(db.String(10), nullable=False, default="KRW")
    principal_amount = db.Column(db.Numeric(18, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    links = db.relationship("LoanGroupLink", backref="loan_group", lazy=True, cascade="all, delete-orphan")


class LoanGroupLink(db.Model):
    __tablename__ = "loan_group_link"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    loan_group_id = db.Column(db.String(36), db.ForeignKey("loan_group.id"), nullable=False, index=True)
    journal_line_id = db.Column(db.Integer, db.ForeignKey("journal_line.id"), nullable=False, index=True)
    linked_amount = db.Column(db.Numeric(18, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    journal_line = db.relationship("JournalLine", lazy="joined")

    __table_args__ = (db.UniqueConstraint("loan_group_id", "journal_line_id", name="uq_group_line"),)


class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    # Keep date as string for consistency with Transaction and flexible parsing, plus parsed date for sorting
    date = db.Column(db.String(20))
    date_parsed = db.Column(db.Date)
    description = db.Column(db.String(255))
    reference = db.Column(db.String(120), index=True)  # e.g., 'TX:123' for migrated rows, invoice no, etc.
    posted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    lines = db.relationship("JournalLine", backref="journal", lazy=True, cascade="all, delete-orphan")


class JournalLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journal_id = db.Column(db.Integer, db.ForeignKey("journal_entry.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False, index=True)
    # 'D' for debit, 'C' for credit
    dc = db.Column(db.String(1), nullable=False)
    # Amounts: prefer fixed precision. SQLite stores NUMERIC; SQLAlchemy coerces to Decimal when bound.
    amount_base = db.Column(db.Numeric(18, 2), nullable=False)
    currency_code = db.Column(db.String(10))  # optional, e.g., 'USD', 'EUR', 'MYR'
    amount_tx = db.Column(db.Numeric(18, 2))  # original currency amount (if different from base)
    fx_rate_to_base = db.Column(db.Numeric(18, 8))  # rate used for conversion (amount_tx * rate = amount_base)
    memo = db.Column(db.Text)
    line_no = db.Column(db.Integer, default=0)
