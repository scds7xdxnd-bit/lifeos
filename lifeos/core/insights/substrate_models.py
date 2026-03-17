"""Phase 5a insight substrate models: timeline events and interpretations."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class TimelineEvent(db.Model):
    __tablename__ = "timeline_event"
    __table_args__ = (
        db.UniqueConstraint("user_id", "event_id", name="uq_timeline_event_user_event"),
        db.Index("ix_timeline_event_user_start", "user_id", "timestamp_start"),
        db.Index("ix_timeline_event_user_domain_start", "user_id", "source_domain", "timestamp_start"),
        db.Index("ix_timeline_event_user_type_start", "user_id", "event_type", "timestamp_start"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(db.String(128), nullable=False)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True)
    timestamp_start: Mapped[datetime] = mapped_column(nullable=False, index=True)
    timestamp_end: Mapped[datetime | None] = mapped_column(nullable=True)
    source_domain: Mapped[str] = mapped_column(db.String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(db.String(128), nullable=False)
    source_object_ref: Mapped[str | None] = mapped_column(db.String(128))
    raw_payload: Mapped[dict] = mapped_column(db.JSON, default=dict)
    ingested_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)


class Interpretation(db.Model):
    __tablename__ = "interpretation"
    __table_args__ = (
        db.UniqueConstraint("user_id", "fingerprint", name="uq_interpretation_user_fingerprint"),
        db.Index("ix_interpretation_user_status_created", "user_id", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True)
    interpretation_type: Mapped[str] = mapped_column(db.String(128), nullable=False)
    input_event_ids: Mapped[list] = mapped_column(db.JSON, default=list)
    proposed_writes: Mapped[list] = mapped_column(db.JSON, default=list)
    applied_writes: Mapped[list | None] = mapped_column(db.JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(db.Numeric(3, 2), nullable=False)
    evidence: Mapped[str] = mapped_column(db.Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(db.String(16), nullable=False, default="proposed")
    reversible_plan: Mapped[dict] = mapped_column(db.JSON, default=dict)
    fingerprint: Mapped[str] = mapped_column(db.String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    decided_at: Mapped[datetime | None] = mapped_column(nullable=True)


class UserFeedbackEvent(db.Model):
    __tablename__ = "user_feedback_event"
    __table_args__ = (
        db.Index("ix_user_feedback_user_created", "user_id", "created_at"),
        db.Index("ix_user_feedback_user_type", "user_id", "feedback_type"),
        db.Index("ix_user_feedback_user_fingerprint", "user_id", "fingerprint"),
        db.Index("ix_user_feedback_user_inquiry_created", "user_id", "inquiry_id", "created_at"),
        db.Index(
            "ix_user_feedback_user_inquiry_version_created",
            "user_id",
            "inquiry_version_id",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True)
    interpretation_id: Mapped[int | None] = mapped_column(db.ForeignKey("interpretation.id"), index=True)
    inquiry_id: Mapped[int | None] = mapped_column(db.ForeignKey("inquiry_request.id"), index=True, nullable=True)
    inquiry_version_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("inquiry_brief_version.id"),
        index=True,
        nullable=True,
    )
    feedback_type: Mapped[str] = mapped_column(db.String(32), nullable=False)
    fingerprint: Mapped[str | None] = mapped_column(db.String(128), nullable=True)
    payload: Mapped[dict] = mapped_column(db.JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)


__all__ = ["TimelineEvent", "Interpretation", "UserFeedbackEvent"]
