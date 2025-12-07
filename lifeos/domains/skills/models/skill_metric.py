"""Skill metrics (speed, accuracy, etc.)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class SkillMetric(db.Model):
    __tablename__ = "skill_metric"

    id: Mapped[int] = mapped_column(primary_key=True)
    skill_id: Mapped[int] = mapped_column(db.ForeignKey("skill.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    value: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    skill: Mapped["Skill"] = relationship("Skill", back_populates="metrics")
