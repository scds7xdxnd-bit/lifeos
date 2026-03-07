"""Feature storage models for Phase 5b deterministic insights."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class FeatureDaily(db.Model):
    __tablename__ = "features_daily"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "feature_date",
            "feature_key",
            "definition_version",
            name="uq_features_daily_user_date_key_version",
        ),
        db.Index("ix_features_daily_user_date", "user_id", "feature_date"),
        db.Index("ix_features_daily_user_key_date", "user_id", "feature_key", "feature_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"))
    feature_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    feature_key: Mapped[str] = mapped_column(db.String(128), nullable=False)
    feature_value: Mapped[float] = mapped_column(db.Numeric(14, 4), nullable=False)
    source_domain: Mapped[str] = mapped_column(db.String(64), nullable=False)
    definition_version: Mapped[str] = mapped_column(db.String(16), nullable=False, default="v1")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


__all__ = ["FeatureDaily"]
