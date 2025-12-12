"""Relationship interaction model."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db

if TYPE_CHECKING:
    from .person_models import Person


class Interaction(db.Model):
    __tablename__ = "relationships_interaction"
    __table_args__ = (
        db.Index("ix_relationships_interaction_user_date", "user_id", "date"),
        db.Index("ix_relationships_interaction_person_date", "user_id", "person_id", "date"),
        db.Index("ix_relationships_interaction_calendar_event", "calendar_event_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    person_id: Mapped[int] = mapped_column(
        db.ForeignKey("relationships_person.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    date: Mapped[date] = mapped_column(default=date.today, nullable=False)
    method: Mapped[str | None] = mapped_column(db.String(64))
    notes: Mapped[str | None] = mapped_column(db.Text)
    sentiment: Mapped[str | None] = mapped_column(db.String(32))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Calendar inference fields
    source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
    calendar_event_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("calendar_event.id", ondelete="SET NULL"), nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
    inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)

    person: Mapped["Person"] = relationship("Person", back_populates="interactions")
