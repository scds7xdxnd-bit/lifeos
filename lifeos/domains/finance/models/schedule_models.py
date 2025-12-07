"""Money schedule and forecasting models."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class MoneyScheduleRow(db.Model):
    __tablename__ = "finance_money_schedule_row"
    __table_args__ = (db.Index("ix_finance_money_schedule_row_user_event_date", "user_id", "event_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    account_id: Mapped[int] = mapped_column(db.ForeignKey("finance_account.id"), nullable=False)
    event_date: Mapped[date] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(db.Numeric(18, 2), nullable=False)
    memo: Mapped[str | None] = mapped_column(db.Text)


class MoneyScheduleDailyBalance(db.Model):
    __tablename__ = "finance_money_schedule_daily_balance"
    __table_args__ = (db.Index("ix_finance_money_schedule_daily_balance_user_as_of", "user_id", "as_of"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    as_of: Mapped[date] = mapped_column(index=True)
    balance: Mapped[float] = mapped_column(db.Numeric(18, 2), nullable=False)


class MoneyScheduleScenario(db.Model):
    __tablename__ = "finance_money_schedule_scenario"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(db.Text)

    rows: Mapped[list["MoneyScheduleScenarioRow"]] = relationship("MoneyScheduleScenarioRow", back_populates="scenario", cascade="all, delete-orphan")


class MoneyScheduleScenarioRow(db.Model):
    __tablename__ = "finance_money_schedule_scenario_row"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(db.ForeignKey("finance_money_schedule_scenario.id"), index=True, nullable=False)
    base_row_id: Mapped[int] = mapped_column(db.ForeignKey("finance_money_schedule_row.id"), nullable=True)
    delta_amount: Mapped[float] = mapped_column(db.Numeric(18, 2), nullable=False, default=0)

    scenario: Mapped[MoneyScheduleScenario] = relationship("MoneyScheduleScenario", back_populates="rows")
    base_row: Mapped[MoneyScheduleRow | None] = relationship("MoneyScheduleRow")
