"""Insight persistence models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class InsightRecord(db.Model):
    __tablename__ = "insight_record"
    __table_args__ = (
        db.Index("ix_insight_record_user_created_at", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True)
    event_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("event_record.id"), index=True
    )
    event_type: Mapped[str] = mapped_column(db.String(128), index=True)
    kind: Mapped[str] = mapped_column(db.String(64), index=True)
    message: Mapped[str] = mapped_column(db.Text, nullable=False, default="")
    severity: Mapped[str] = mapped_column(db.String(16), default="info")
    data: Mapped[dict] = mapped_column(db.JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
