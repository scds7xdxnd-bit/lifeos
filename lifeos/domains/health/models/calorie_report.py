"""Calorie report model for health calculator."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class CalorieReport(db.Model):
    __tablename__ = "health_calorie_report"
    __table_args__ = (db.Index("ix_health_calorie_report_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)

    # Input snapshot
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    height_cm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    age_years: Mapped[int] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(db.String(16), nullable=False)
    body_fat_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    activity_level: Mapped[str] = mapped_column(db.String(32), nullable=False)
    goal_type: Mapped[str] = mapped_column(db.String(16), nullable=False)
    goal_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    goal_timeline_months: Mapped[int | None] = mapped_column(nullable=True)

    # Computed values
    method_used: Mapped[str] = mapped_column(db.String(32), nullable=False)
    lean_body_mass: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    bmr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    activity_multiplier: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    tdee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Delta breakdown
    delta_bw: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    total_delta_kcal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    delta_kcal_per_day: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    kcal_per_kg_used: Mapped[int | None] = mapped_column(nullable=True)

    # Daily targets
    daily_calories: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    protein_g_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fat_g_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    carbs_g_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fiber_g_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Monthly targets
    monthly_calories: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    monthly_protein_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monthly_fat_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monthly_carbs_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monthly_fiber_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
