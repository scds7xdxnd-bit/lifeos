"""Persistent event models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class EventRecord(db.Model):
    __tablename__ = "event_record"
    __table_args__ = (
        db.Index("ix_event_record_user_created_at", "user_id", "created_at"),
        db.Index("ix_event_record_user_event_type", "user_id", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(db.String(128), index=True, nullable=False)
    payload: Mapped[dict] = mapped_column(db.JSON, nullable=False, default=dict)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
