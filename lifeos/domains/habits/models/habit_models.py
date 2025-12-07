"""Habits models with prefixed tables."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class Habit(db.Model):
    __tablename__ = "habits_habit"
    __table_args__ = (
        db.Index("ux_habits_habit_user_name", "user_id", "name", unique=True),
        db.Index("ix_habits_habit_user_domain_link", "user_id", "domain_link"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(db.Text)
    domain_link: Mapped[str | None] = mapped_column(db.String(64))
    schedule_type: Mapped[str] = mapped_column(db.String(32), nullable=False, default="daily")
    target_count: Mapped[int | None] = mapped_column(nullable=True)
    time_of_day: Mapped[str | None] = mapped_column(db.String(32))
    difficulty: Mapped[str | None] = mapped_column(db.String(32))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    logs: Mapped[list["HabitLog"]] = relationship(
        "HabitLog",
        back_populates="habit",
        cascade="all, delete-orphan",
    )


class HabitLog(db.Model):
    __tablename__ = "habits_habit_log"
    __table_args__ = (
        db.Index("ix_habits_log_user_logged_date", "user_id", "logged_date"),
        db.Index("ix_habits_log_habit_logged_date", "habit_id", "logged_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    habit_id: Mapped[int] = mapped_column(
        db.ForeignKey("habits_habit.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    value: Mapped[float | None] = mapped_column(db.Numeric(10, 2))
    note: Mapped[str | None] = mapped_column(db.Text)
    logged_date: Mapped[date] = mapped_column(default=date.today, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    habit: Mapped[Habit] = relationship("Habit", back_populates="logs")
