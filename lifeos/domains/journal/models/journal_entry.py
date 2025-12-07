"""Personal journal entry."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class JournalEntry(db.Model):
    __tablename__ = "journal_entry"
    __table_args__ = (
        db.Index("ix_journal_entry_user_entry_date", "user_id", "entry_date"),
        db.Index("ix_journal_entry_user_created_at", "user_id", "created_at"),
        db.Index("ix_journal_entry_user_mood", "user_id", "mood"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(db.String(255))
    body: Mapped[str] = mapped_column(db.Text, nullable=False)
    mood: Mapped[int | None] = mapped_column(db.Integer)
    tags: Mapped[list] = mapped_column(db.JSON, default=list)
    entry_date: Mapped[date] = mapped_column(default=date.today, nullable=False)
    is_private: Mapped[bool] = mapped_column(default=True)
    sentiment_score: Mapped[float | None] = mapped_column(db.Numeric(5, 2))
    emotion_label: Mapped[str | None] = mapped_column(db.String(64))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
