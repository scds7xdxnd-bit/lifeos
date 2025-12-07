"""Relationship person model."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class Person(db.Model):
    __tablename__ = "relationships_person"
    __table_args__ = (
        db.Index("ux_relationships_person_user_name", "user_id", "name", unique=True),
        db.Index("ix_relationships_person_user_importance", "user_id", "importance_level"),
        db.Index("ix_relationships_person_user_type", "user_id", "relationship_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    relationship_type: Mapped[str | None] = mapped_column(db.String(64))
    importance_level: Mapped[int | None] = mapped_column()
    tags: Mapped[list] = mapped_column(db.JSON, default=list)
    notes: Mapped[str | None] = mapped_column(db.Text)
    birthday: Mapped[date | None] = mapped_column()
    first_met_date: Mapped[date | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    interactions: Mapped[list["Interaction"]] = relationship(
        "Interaction",
        back_populates="person",
        cascade="all, delete-orphan",
    )
