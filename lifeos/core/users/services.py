"""User service layer."""

from __future__ import annotations

from typing import Optional

from lifeos.core.auth.models import Role
from lifeos.core.auth.password import hash_password
from lifeos.core.private_alpha import alpha_enabled, alpha_flags
from lifeos.core.users.models import User
from lifeos.core.users.preferences import set_preference
from lifeos.core.users.schemas import UserCreateRequest, UserUpdateRequest
from lifeos.extensions import db


def get_user(user_id: int) -> Optional[User]:
    return User.query.get(user_id)


def create_user(payload: UserCreateRequest) -> User:
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        timezone=payload.timezone,
        password_hash=hash_password(payload.password),
    )
    db.session.add(user)
    _ensure_default_roles(user)
    db.session.commit()
    return user


def update_user(user: User, payload: UserUpdateRequest) -> User:
    if payload.email:
        user.email = payload.email
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.timezone is not None:
        user.timezone = payload.timezone
    if payload.password:
        user.password_hash = hash_password(payload.password)
    if payload.is_active is not None:
        user.is_active = payload.is_active
    db.session.commit()
    return user


def update_preferences(user: User, prefs: dict) -> User:
    for key, value in prefs.items():
        set_preference(user, key, value)
    db.session.commit()
    return user


def _ensure_default_roles(user: User) -> None:
    """
    Assign baseline roles for new users.

    All users get standard write access to all domains by default.
    This ensures a consistent experience across the platform.
    """
    if alpha_enabled():
        flags = alpha_flags()
        default_codes = tuple(
            dict.fromkeys(["user", "alpha_user", *[f"{domain}:write" for domain in flags.visible_domains]])
        )
    else:
        default_codes = (
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
    for code in default_codes:
        role = Role.query.filter_by(name=code).first()
        if not role:
            role = Role(name=code, description=f"Auto-created role {code}")
            db.session.add(role)
        if role not in user.roles:
            user.roles.append(role)
