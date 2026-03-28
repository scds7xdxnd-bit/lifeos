"""Food library item model for macro/cost optimizer."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class FoodLibraryItem(db.Model):
    __tablename__ = "health_food_library_item"
    __table_args__ = (db.Index("ix_health_food_library_item_user_name", "user_id", "name", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(256), nullable=False)
    cost_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    calories_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    protein_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    carbohydrate_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fat_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fiber_per_100g: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
