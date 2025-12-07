"""User and profile models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin

from lifeos.extensions import db


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class User(db.Model, TimestampMixin, UserMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(db.String(255))
    timezone: Mapped[str | None] = mapped_column(db.String(64))
    is_active: Mapped[bool] = mapped_column(default=True)

    preferences: Mapped[list["UserPreference"]] = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("Role", secondary="user_role", backref="users", lazy="joined")

    @property
    def role_codes(self) -> list[str]:
        return [role.name for role in self.roles] if self.roles else []


class UserPreference(db.Model, TimestampMixin):
    __tablename__ = "user_preference"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True)
    key: Mapped[str] = mapped_column(db.String(128), nullable=False)
    value: Mapped[dict] = mapped_column(db.JSON, nullable=False, default=dict)

    user: Mapped[User] = relationship("User", back_populates="preferences")
