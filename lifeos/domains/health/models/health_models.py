"""Health domain models (biometrics, workouts, nutrition)."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class Biometric(db.Model):
    __tablename__ = "health_biometric"
    __table_args__ = (db.Index("ix_health_biometric_user_date", "user_id", "date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(default=date.today, nullable=False)
    weight: Mapped[float | None] = mapped_column(db.Numeric(10, 2))
    body_fat_pct: Mapped[float | None] = mapped_column(db.Numeric(5, 2))
    resting_hr: Mapped[int | None] = mapped_column(db.Integer)
    energy_level: Mapped[int | None] = mapped_column(db.Integer)
    stress_level: Mapped[int | None] = mapped_column(db.Integer)
    notes: Mapped[str | None] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Workout(db.Model):
    __tablename__ = "health_workout"
    __table_args__ = (
        db.Index("ix_health_workout_user_date", "user_id", "date"),
        db.Index("ix_health_workout_calendar_event", "calendar_event_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(default=date.today, nullable=False)
    workout_type: Mapped[str] = mapped_column(db.String(64), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    intensity: Mapped[str] = mapped_column(db.String(16), nullable=False)
    calories_est: Mapped[float | None] = mapped_column(db.Numeric(10, 2))
    notes: Mapped[str | None] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Calendar inference fields
    source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
    calendar_event_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("calendar_event.id", ondelete="SET NULL"), nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
    inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)


class NutritionLog(db.Model):
    __tablename__ = "health_nutrition_log"
    __table_args__ = (
        db.Index("ix_health_nutrition_log_user_date", "user_id", "date"),
        db.Index("ix_health_nutrition_log_calendar_event", "calendar_event_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(default=date.today, nullable=False)
    meal_type: Mapped[str] = mapped_column(db.String(32), nullable=False)
    items: Mapped[str] = mapped_column(db.Text, nullable=False)
    calories_est: Mapped[float | None] = mapped_column(db.Numeric(10, 2))
    quality_score: Mapped[int | None] = mapped_column(db.Integer)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Calendar inference fields
    source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
    calendar_event_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("calendar_event.id", ondelete="SET NULL"), nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
    inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)


__all__ = ["Biometric", "Workout", "NutritionLog"]
