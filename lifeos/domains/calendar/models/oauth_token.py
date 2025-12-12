"""OAuth token storage for external calendar providers."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class CalendarOAuthToken(db.Model):
    """
    Stores OAuth tokens for external calendar providers (Google, Apple, etc.).

    Each user can have one token per provider. Tokens include refresh capability
    for automatic renewal.
    """

    __tablename__ = "calendar_oauth_token"
    __table_args__ = (
        db.UniqueConstraint("user_id", "provider", name="uq_user_provider"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id"), index=True, nullable=False
    )

    # Provider identifier: 'google', 'apple', etc.
    provider: Mapped[str] = mapped_column(db.String(32), nullable=False)

    # OAuth tokens (encrypted at rest in production)
    access_token: Mapped[str] = mapped_column(db.Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(db.Text)
    token_type: Mapped[str] = mapped_column(db.String(32), default="Bearer")

    # Token expiry
    expires_at: Mapped[datetime | None] = mapped_column()

    # Sync state
    last_sync_at: Mapped[datetime | None] = mapped_column()
    sync_token: Mapped[str | None] = mapped_column(
        db.String(512)
    )  # For incremental sync

    # Status
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    error_message: Mapped[str | None] = mapped_column(db.String(512))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    @property
    def is_expired(self) -> bool:
        """Check if the access token has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at

    @property
    def can_refresh(self) -> bool:
        """Check if we have a refresh token available."""
        return bool(self.refresh_token)
