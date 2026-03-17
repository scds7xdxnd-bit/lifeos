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
    AUTH_PRIVATE_ALPHA_INVITE_ACCEPTED,
    AUTH_PRIVATE_ALPHA_INVITE_ISSUED,
    AUTH_PRIVATE_ALPHA_INVITE_REJECTED,
    AUTH_USER_PASSWORD_RESET_COMPLETED,
    AUTH_USER_PASSWORD_RESET_REQUESTED,
    AUTH_USER_REGISTERED,
    AUTH_USER_USERNAME_REMINDER_REQUESTED,
)
from lifeos.core.auth.models import JWTBlocklist, PasswordResetToken, PrivateAlphaInvite, Role, SessionToken
from lifeos.core.auth.password import hash_password, verify_password
from lifeos.core.auth.schemas import (
    ForgotPasswordRequest,
    ForgotUsernameRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from lifeos.core.observability import (
    record_private_alpha_invite_accepted,
    record_private_alpha_invite_issued,
    record_private_alpha_invite_rejected,
    set_private_alpha_user_state,
)
from lifeos.core.private_alpha import (
    AlphaGateError,
    alpha_enabled,
    alpha_flags,
    hash_invite_token,
    normalize_invite_email,
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

    invite: PrivateAlphaInvite | None = None
    if alpha_enabled():
        _enforce_private_alpha_user_cap()
        invite = _validate_private_alpha_invite(payload.invite_token, normalized_email)

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
    if invite is not None:
        invite.accepted_by_user_id = user.id
        invite.accepted_at = datetime.utcnow()
        record_private_alpha_invite_accepted()
        enqueue_outbox(
            AUTH_PRIVATE_ALPHA_INVITE_ACCEPTED,
            {
                "invite_id": invite.id,
                "invited_email": invite.invited_email,
                "accepted_by_user_id": user.id,
                "accepted_at": invite.accepted_at.isoformat(),
            },
            user_id=user.id,
        )

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
    if alpha_enabled():
        flags = alpha_flags()
        set_private_alpha_user_state(
            active_users=_active_alpha_user_count(),
            max_users=flags.max_users,
            enabled=flags.enabled,
        )

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
    for code in _default_register_roles():
        role = Role.query.filter_by(name=code).first()
        if not role:
            role = Role(name=code, description=f"Auto-created role {code}")
            db.session.add(role)
        if role not in user.roles:
            user.roles.append(role)


def _revoke_user_sessions(user_id: int) -> None:
    SessionToken.query.filter_by(user_id=user_id, revoked=False).update({"revoked": True}, synchronize_session=False)


def issue_private_alpha_invite(
    invited_email: str,
    *,
    issued_by_user_id: int | None = None,
    expires_at: datetime | None = None,
) -> tuple[PrivateAlphaInvite, str]:
    normalized_email = normalize_invite_email(invited_email)
    raw_token = secrets.token_urlsafe(24)
    invite = PrivateAlphaInvite(
        invited_email=normalized_email,
        token_hash=hash_invite_token(raw_token),
        issued_by_user_id=issued_by_user_id,
        expires_at=expires_at,
    )
    db.session.add(invite)
    db.session.flush()
    enqueue_outbox(
        AUTH_PRIVATE_ALPHA_INVITE_ISSUED,
        {
            "invite_id": invite.id,
            "invited_email": normalized_email,
            "issued_by_user_id": issued_by_user_id,
            "expires_at": expires_at.isoformat() if expires_at else None,
        },
        user_id=issued_by_user_id,
    )
    record_private_alpha_invite_issued()
    db.session.commit()
    return invite, raw_token


def _default_register_roles() -> tuple[str, ...]:
    if not alpha_enabled():
        return DEFAULT_REGISTER_ROLES
    flags = alpha_flags()
    roles = ["user", "alpha_user"]
    for domain in flags.visible_domains:
        roles.append(f"{domain}:write")
    return tuple(dict.fromkeys(roles))


def _enforce_private_alpha_user_cap() -> None:
    flags = alpha_flags()
    if not flags.enabled or flags.max_users <= 0:
        set_private_alpha_user_state(active_users=0, max_users=flags.max_users, enabled=flags.enabled)
        return
    active_alpha_users = _active_alpha_user_count()
    set_private_alpha_user_state(active_users=active_alpha_users, max_users=flags.max_users, enabled=flags.enabled)
    if active_alpha_users >= flags.max_users:
        record_private_alpha_invite_rejected("alpha_user_cap_reached")
        raise AlphaGateError("alpha_user_cap_reached", details={"max_users": flags.max_users})


def _validate_private_alpha_invite(raw_token: str | None, normalized_email: str) -> PrivateAlphaInvite | None:
    flags = alpha_flags()
    if not flags.enabled or not flags.invite_only:
        return None
    if not raw_token:
        enqueue_outbox(
            AUTH_PRIVATE_ALPHA_INVITE_REJECTED,
            {"invited_email": normalized_email, "reason": "invite_required"},
            user_id=None,
        )
        record_private_alpha_invite_rejected("invite_required")
        db.session.commit()
        raise AlphaGateError("invite_required")
    invite = PrivateAlphaInvite.query.filter_by(token_hash=hash_invite_token(raw_token)).first()
    now = datetime.utcnow()
    if invite is None:
        enqueue_outbox(
            AUTH_PRIVATE_ALPHA_INVITE_REJECTED,
            {"invited_email": normalized_email, "reason": "invite_invalid"},
            user_id=None,
        )
        record_private_alpha_invite_rejected("invite_invalid")
        db.session.commit()
        raise AlphaGateError("invite_invalid")
    if normalize_invite_email(invite.invited_email) != normalized_email:
        enqueue_outbox(
            AUTH_PRIVATE_ALPHA_INVITE_REJECTED,
            {"invited_email": normalized_email, "reason": "invite_email_mismatch"},
            user_id=None,
        )
        record_private_alpha_invite_rejected("invite_email_mismatch")
        db.session.commit()
        raise AlphaGateError("invite_email_mismatch")
    if invite.revoked_at is not None:
        enqueue_outbox(
            AUTH_PRIVATE_ALPHA_INVITE_REJECTED,
            {"invited_email": normalized_email, "reason": "invite_revoked"},
            user_id=None,
        )
        record_private_alpha_invite_rejected("invite_revoked")
        db.session.commit()
        raise AlphaGateError("invite_revoked")
    if invite.accepted_at is not None:
        enqueue_outbox(
            AUTH_PRIVATE_ALPHA_INVITE_REJECTED,
            {"invited_email": normalized_email, "reason": "invite_already_used"},
            user_id=None,
        )
        record_private_alpha_invite_rejected("invite_already_used")
        db.session.commit()
        raise AlphaGateError("invite_already_used")
    if invite.expires_at is not None and invite.expires_at < now:
        enqueue_outbox(
            AUTH_PRIVATE_ALPHA_INVITE_REJECTED,
            {"invited_email": normalized_email, "reason": "invite_expired"},
            user_id=None,
        )
        record_private_alpha_invite_rejected("invite_expired")
        db.session.commit()
        raise AlphaGateError("invite_expired")
    return invite


def _active_alpha_user_count() -> int:
    role = Role.query.filter_by(name="alpha_user").first()
    if role is None:
        return 0
    return (
        db.session.query(User.id)
        .join(User.roles)
        .filter(Role.name == "alpha_user", User.is_active.is_(True))
        .distinct()
        .count()
    )
