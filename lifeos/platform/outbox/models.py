"""Transactional outbox message model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class OutboxMessage(db.Model):
    __tablename__ = "platform_outbox"
    __table_args__ = (
        db.Index("ix_platform_outbox_user_available_at", "user_id", "available_at"),
        db.Index("ix_platform_outbox_user_status", "user_id", "status", "available_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True)
    event_type: Mapped[str] = mapped_column(db.String(128), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(db.JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(db.String(32), nullable=False, default="pending")
    attempts: Mapped[int] = mapped_column(default=0)
    available_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    last_error: Mapped[str | None] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
