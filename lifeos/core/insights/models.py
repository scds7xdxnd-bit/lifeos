"""Insight persistence models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class InsightRecord(db.Model):
    __tablename__ = "insight_record"
    __table_args__ = (
        db.Index("ix_insight_record_user_created_at", "user_id", "created_at"),
        db.Index("ix_insight_record_user_band_created", "user_id", "confidence_band", "created_at"),
        db.Index("ix_insight_record_user_routing_created", "user_id", "routing", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True)
    event_id: Mapped[int | None] = mapped_column(db.ForeignKey("event_record.id"), index=True)
    event_type: Mapped[str] = mapped_column(db.String(128), index=True)
    kind: Mapped[str] = mapped_column(db.String(64), index=True)
    message: Mapped[str] = mapped_column(db.Text, nullable=False, default="")
    severity: Mapped[str] = mapped_column(db.String(16), default="info")
    confidence_band: Mapped[str | None] = mapped_column(db.String(32), nullable=True)
    routing: Mapped[str | None] = mapped_column(db.String(32), nullable=True)
    data: Mapped[dict] = mapped_column(db.JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
