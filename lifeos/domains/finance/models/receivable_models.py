"""Receivable and loan tracking models."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class ReceivableTracker(db.Model):
    __tablename__ = "finance_receivable_tracker"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    counterparty: Mapped[str] = mapped_column(db.String(255), nullable=False)
    principal: Mapped[float] = mapped_column(db.Numeric(18, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    due_date: Mapped[date | None] = mapped_column(nullable=True)
    interest_rate: Mapped[float | None] = mapped_column(db.Numeric(5, 2))

    manual_entries: Mapped[list["ReceivableManualEntry"]] = relationship(
        "ReceivableManualEntry", back_populates="tracker", cascade="all, delete-orphan"
    )
    loan_group_links: Mapped[list["LoanGroupLink"]] = relationship("LoanGroupLink", back_populates="tracker")


class ReceivableManualEntry(db.Model):
    __tablename__ = "finance_receivable_manual_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    tracker_id: Mapped[int] = mapped_column(db.ForeignKey("finance_receivable_tracker.id"), index=True, nullable=False)
    entry_date: Mapped[date] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(db.Numeric(18, 2), nullable=False)
    memo: Mapped[str | None] = mapped_column(db.Text)

    tracker: Mapped[ReceivableTracker] = relationship("ReceivableTracker", back_populates="manual_entries")


class LoanGroup(db.Model):
    __tablename__ = "finance_loan_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(db.Text)

    links: Mapped[list["LoanGroupLink"]] = relationship(
        "LoanGroupLink", back_populates="group", cascade="all, delete-orphan"
    )


class LoanGroupLink(db.Model):
    __tablename__ = "finance_loan_group_link"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(db.ForeignKey("finance_loan_group.id"), index=True, nullable=False)
    tracker_id: Mapped[int] = mapped_column(db.ForeignKey("finance_receivable_tracker.id"), index=True, nullable=False)

    group: Mapped[LoanGroup] = relationship("LoanGroup", back_populates="links")
    tracker: Mapped[ReceivableTracker] = relationship("ReceivableTracker", back_populates="loan_group_links")
