"""Authentication and permission models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class Role(db.Model, TimestampMixin):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(64), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), default="")

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", secondary="role_permission", back_populates="roles"
    )


class Permission(db.Model, TimestampMixin):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(db.String(128), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(db.String(255), default="")

    roles: Mapped[list[Role]] = relationship("Role", secondary="role_permission", back_populates="permissions")


class RolePermission(db.Model):
    __tablename__ = "role_permission"

    role_id: Mapped[int] = mapped_column(db.ForeignKey("role.id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(db.ForeignKey("permission.id"), primary_key=True)


class UserRole(db.Model):
    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(db.ForeignKey("role.id"), primary_key=True)


class SessionToken(db.Model, TimestampMixin):
    __tablename__ = "session_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)
    jti: Mapped[str] = mapped_column(db.String(64), nullable=False, unique=True)
    revoked: Mapped[bool] = mapped_column(default=False)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AuthSession(db.Model, TimestampMixin):
    __tablename__ = "auth_session"
    __table_args__ = (
        db.UniqueConstraint("session_id", name="uq_auth_session_session_id"),
        db.Index("ix_auth_session_user", "user_id"),
        db.Index("ix_auth_session_user_state", "user_id", "lifecycle_state"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(db.String(128), nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(db.String(32), nullable=False, default="active")
    device_id: Mapped[str | None] = mapped_column(db.String(128), nullable=True)
    invalidated_at: Mapped[datetime | None] = mapped_column(nullable=True)


class JWTBlocklist(db.Model, TimestampMixin):
    __tablename__ = "jwt_blocklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(db.String(64), unique=True, nullable=False)
    created_by: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"))


class PasswordResetToken(db.Model, TimestampMixin):
    __tablename__ = "password_reset_token"
    __table_args__ = (
        db.Index("ix_password_reset_user_expires_at", "user_id", "expires_at"),
        db.Index("ix_password_reset_jti", "jti"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)
    jti: Mapped[str] = mapped_column(db.String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(nullable=True)
    attempts: Mapped[int] = mapped_column(default=0)
