"""Skill and practice session models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

# Forward decl to satisfy type checkers; actual class imported via relationship resolution.
class SkillMetric: ...

from lifeos.extensions import db


class Skill(db.Model):
    __tablename__ = "skill"
    __table_args__ = (
        db.Index("ux_skill_user_name", "user_id", "name", unique=True),
        db.Index("ix_skill_user_category", "user_id", "category"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(db.String(128))
    difficulty: Mapped[str | None] = mapped_column(db.String(32))
    target_level: Mapped[int | None] = mapped_column()
    current_level: Mapped[int | None] = mapped_column()
    description: Mapped[str | None] = mapped_column(db.Text)
    tags: Mapped[list] = mapped_column(db.JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions: Mapped[list["PracticeSession"]] = relationship(
        "PracticeSession",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    metrics: Mapped[list["SkillMetric"]] = relationship(
        "SkillMetric",
        back_populates="skill",
        cascade="all, delete-orphan",
    )


class PracticeSession(db.Model):
    __tablename__ = "skill_practice_session"
    __table_args__ = (
        db.Index("ix_skill_session_user_practiced_at", "user_id", "practiced_at"),
        db.Index("ix_skill_session_skill_practiced_at", "skill_id", "practiced_at"),
        db.Index("ix_skill_session_calendar_event", "calendar_event_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=True)
    skill_id: Mapped[int] = mapped_column(db.ForeignKey("skill.id", ondelete="CASCADE"), index=True, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(default=0)
    intensity: Mapped[int | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column(db.Text)
    practiced_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Calendar inference fields
    source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
    calendar_event_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("calendar_event.id", ondelete="SET NULL"), nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
    inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)

    skill: Mapped[Skill] = relationship("Skill", back_populates="sessions")
