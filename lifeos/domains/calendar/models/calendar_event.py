"""Calendar event and interpretation models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class CalendarEvent(db.Model):
    """
    Primary calendar event entity.

    Stores user calendar entries from manual input, external sync (Google/Apple),
    or API integrations. Events are interpreted by the CalendarInterpreter to
    create inferred records in other domains.
    """

    __tablename__ = "calendar_event"
    __table_args__ = (
        db.Index("ix_calendar_event_user_start", "user_id", "start_time"),
        db.Index("ix_calendar_event_user_end", "user_id", "end_time"),
        db.Index("ix_calendar_event_user_source", "user_id", "source"),
        db.Index(
            "ux_calendar_event_user_external",
            "user_id",
            "external_id",
            unique=True,
            postgresql_where=db.text("external_id IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)

    # Event content
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(db.Text)

    # Timing
    start_time: Mapped[datetime] = mapped_column(nullable=False, index=True)
    end_time: Mapped[datetime | None] = mapped_column(nullable=True)
    all_day: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Location
    location: Mapped[str | None] = mapped_column(db.String(512))

    # Source tracking
    source: Mapped[str] = mapped_column(db.String(32), nullable=False, default="manual")
    # Values: 'manual', 'sync_google', 'sync_apple', 'api'
    external_id: Mapped[str | None] = mapped_column(db.String(255), nullable=True)

    # Recurrence (future: RRULE support)
    recurrence_rule: Mapped[str | None] = mapped_column(db.String(255))

    # UI customization
    color: Mapped[str | None] = mapped_column(db.String(16))
    is_private: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Extensible data
    tags: Mapped[list] = mapped_column(db.JSON, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", db.JSON, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    interpretations: Mapped[list["CalendarEventInterpretation"]] = relationship(
        "CalendarEventInterpretation",
        back_populates="calendar_event",
        cascade="all, delete-orphan",
    )

    @property
    def duration_minutes(self) -> int | None:
        """Calculate duration in minutes if end_time is set."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None


class CalendarEventInterpretation(db.Model):
    """
    Stores the interpreter's classification result for a calendar event.

    Each interpretation links a calendar event to a potential domain record.
    Users can confirm, reject, or ignore inferred interpretations.
    """

    __tablename__ = "calendar_event_interpretation"
    __table_args__ = (
        db.Index("ix_interpretation_event", "calendar_event_id"),
        db.Index("ix_interpretation_user_domain", "user_id", "domain", "status"),
        db.Index("ix_interpretation_user_status", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    calendar_event_id: Mapped[int] = mapped_column(
        db.ForeignKey("calendar_event.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)

    # Classification result
    domain: Mapped[str] = mapped_column(db.String(32), nullable=False)
    # Values: 'finance', 'health', 'habits', 'skills', 'projects', 'relationships'
    record_type: Mapped[str] = mapped_column(db.String(64), nullable=False)
    # Values: 'transaction', 'workout', 'meal', 'habit_log', 'practice', 'work_session', 'interaction'

    # Link to created domain record (once created)
    record_id: Mapped[int | None] = mapped_column(nullable=True)

    # Classification confidence
    confidence_score: Mapped[float] = mapped_column(db.Numeric(3, 2), nullable=False, default=0.0)

    # Review status
    status: Mapped[str] = mapped_column(db.String(16), nullable=False, default="inferred")
    # Values: 'inferred', 'confirmed', 'rejected', 'ignored'

    # Classification details
    classification_data: Mapped[dict] = mapped_column(db.JSON, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    calendar_event: Mapped[CalendarEvent] = relationship("CalendarEvent", back_populates="interpretations")


__all__ = ["CalendarEvent", "CalendarEventInterpretation"]
