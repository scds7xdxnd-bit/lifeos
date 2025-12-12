"""Authentication service layer."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Optional

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from sqlalchemy import func

from lifeos.core.auth.events import (
    AUTH_USER_PASSWORD_RESET_COMPLETED,
    AUTH_USER_PASSWORD_RESET_REQUESTED,
    AUTH_USER_REGISTERED,
    AUTH_USER_USERNAME_REMINDER_REQUESTED,
)
from lifeos.core.auth.models import JWTBlocklist, PasswordResetToken, Role, SessionToken
from lifeos.core.auth.password import hash_password, verify_password
from lifeos.core.auth.schemas import (
    ForgotPasswordRequest,
    ForgotUsernameRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from lifeos.core.users.models import User
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Return the user if credentials are valid."""
    user = User.query.filter_by(email=email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def issue_tokens(user: User) -> dict[str, str]:
    """Create access and refresh tokens for a user."""
    identity = str(user.id)
    access_token = create_access_token(identity=identity, additional_claims={"roles": user.role_codes})
    refresh_token = create_refresh_token(identity=identity)

    # Persist refresh jti for revocation checks
    decoded_refresh = decode_token(refresh_token)
    refresh_jti = decoded_refresh.get("jti")
    expires = decoded_refresh.get("exp")
    db.session.add(
        SessionToken(
            user_id=user.id,
            jti=refresh_jti,
            expires_at=datetime.utcfromtimestamp(expires) if expires else None,
        )
    )
    db.session.commit()

    return {"access_token": access_token, "refresh_token": refresh_token}


def revoke_refresh_token(jti: str) -> None:
    """Revoke a refresh token by JTI."""
    token = SessionToken.query.filter_by(jti=jti).first()
    if token:
        token.revoked = True
    db.session.add(JWTBlocklist(jti=jti))
    db.session.commit()


# --- Registration and recovery flows ---

DEFAULT_TIMEZONE = "utc"
RESET_TOKEN_TTL_MINUTES = 30
RESET_TOKEN_MAX_ATTEMPTS = 5
# Roles granted to every new account by default.
DEFAULT_REGISTER_ROLES = (
    "user",
    "finance:write",
    "calendar:write",
    "health:write",
    "habits:write",
    "skills:write",
    "projects:write",
    "relationships:write",
    "journal:write",
)


def register_user(payload: RegisterRequest, auto_issue_tokens: bool = False) -> dict:
    """Create a user, assign default role, and emit events via outbox."""
    normalized_email = payload.email.strip().lower()
    existing = User.query.filter(func.lower(User.email) == normalized_email).first()
    if existing:
        raise ValueError("email_already_exists")

    timezone = payload.timezone or DEFAULT_TIMEZONE
    user = User(
        email=normalized_email,
        full_name=payload.full_name,
        timezone=timezone,
        password_hash=hash_password(payload.password),
    )

    db.session.add(user)
    _assign_default_role(user)
    db.session.flush()  # ensure user.id for events

    enqueue_outbox(
        AUTH_USER_REGISTERED,
        {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "timezone": user.timezone,
        },
        user_id=user.id,
    )
    enqueue_outbox(
        "auth.email.welcome",
        {"user_id": user.id, "email": user.email, "full_name": user.full_name},
        user_id=user.id,
    )

    db.session.commit()

    tokens = issue_tokens(user) if auto_issue_tokens else {}
    return {"user": user, **tokens}


def request_username_reminder(payload: ForgotUsernameRequest) -> None:
    """Generic response; if user exists, enqueue reminder notification and event."""
    user = User.query.filter(func.lower(User.email) == payload.email).first()
    if user:
        enqueue_outbox(
            AUTH_USER_USERNAME_REMINDER_REQUESTED,
            {"user_id": user.id, "email": user.email},
            user_id=user.id,
        )
        enqueue_outbox(
            "auth.email.username_reminder",
            {"user_id": user.id, "email": user.email},
            user_id=user.id,
        )
        db.session.commit()
    else:
        # Emit an event without user_id to keep metrics without leaking existence.
        enqueue_outbox(
            AUTH_USER_USERNAME_REMINDER_REQUESTED,
            {"email": payload.email},
            user_id=None,
        )
        db.session.commit()


def request_password_reset(payload: ForgotPasswordRequest) -> None:
    """Create a reset token if the user exists; always respond generic."""
    user = User.query.filter(func.lower(User.email) == payload.email).first()
    if not user:
        enqueue_outbox(
            AUTH_USER_PASSWORD_RESET_REQUESTED,
            {"email": payload.email, "user_id": None, "expires_at": None},
            user_id=None,
        )
        db.session.commit()
        return

    raw_token, hashed = _generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
    reset = PasswordResetToken(user_id=user.id, jti=hashed, expires_at=expires_at)
    db.session.add(reset)
    db.session.flush()

    enqueue_outbox(
        AUTH_USER_PASSWORD_RESET_REQUESTED,
        {"user_id": user.id, "email": user.email, "expires_at": expires_at.isoformat()},
        user_id=user.id,
    )
    enqueue_outbox(
        "auth.email.password_reset",
        {
            "user_id": user.id,
            "email": user.email,
            "token": raw_token,
            "expires_at": expires_at.isoformat(),
        },
        user_id=user.id,
    )
    db.session.commit()


def reset_password(payload: ResetPasswordRequest) -> bool:
    """Validate reset token, rotate password, revoke sessions, and emit event."""
    hashed = _hash_token(payload.token)
    token = PasswordResetToken.query.filter_by(jti=hashed).with_for_update().first()
    now = datetime.utcnow()
    if not token or token.used_at or token.expires_at < now or token.attempts >= RESET_TOKEN_MAX_ATTEMPTS:
        if token:
            token.attempts += 1
            db.session.commit()
        raise ValueError("invalid_token")

    user = User.query.get(token.user_id)
    if not user:
        token.attempts += 1
        db.session.commit()
        raise ValueError("invalid_token")

    user.password_hash = hash_password(payload.new_password)
    token.used_at = now
    token.attempts += 1

    _revoke_user_sessions(user.id)

    enqueue_outbox(
        AUTH_USER_PASSWORD_RESET_COMPLETED,
        {"user_id": user.id, "reset_id": token.id},
        user_id=user.id,
    )

    db.session.commit()
    return True


# --- helpers ---


def _generate_reset_token() -> tuple[str, str]:
    raw = secrets.token_urlsafe(32)
    return raw, _hash_token(raw)


def _hash_token(raw: str) -> str:
    return sha256(raw.encode("utf-8")).hexdigest()


def _assign_default_role(user: User) -> None:
    for code in DEFAULT_REGISTER_ROLES:
        role = Role.query.filter_by(name=code).first()
        if not role:
            role = Role(name=code, description=f"Auto-created role {code}")
            db.session.add(role)
        if role not in user.roles:
            user.roles.append(role)


def _revoke_user_sessions(user_id: int) -> None:
    SessionToken.query.filter_by(user_id=user_id, revoked=False).update({"revoked": True}, synchronize_session=False)
