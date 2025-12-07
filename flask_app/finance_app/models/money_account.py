from __future__ import annotations

from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from finance_app.extensions import db


class AccountType(str, Enum):
    CASH = "cash"
    CHECKING = "checking"
    SAVINGS = "savings"


class MoneyScheduleAccount(db.Model):
    """Money schedule account included in forecast calculations."""

    __tablename__ = "money_schedule_accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(
        SQLEnum(AccountType, name="money_schedule_account_type"),
        nullable=False,
    )
    currency = db.Column(db.String(10), default="KRW", nullable=False)
    current_balance = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    is_included_in_closing = db.Column(db.Boolean, default=True, nullable=False)

    scheduled_transactions = relationship(
        "finance_app.models.scheduled_transaction.ScheduledTransaction",
        back_populates="account",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    snapshots = relationship(
        "finance_app.models.money_schedule.AccountSnapshot",
        back_populates="account",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "name",
            "currency",
            name="uq_money_schedule_account_name_currency",
        ),
    )

    def __repr__(self) -> str:
        return f"<MoneyAccount id={self.id} name={self.name!r}>"


# Backwards-compatible alias for imports expecting `Account`
Account = MoneyScheduleAccount
