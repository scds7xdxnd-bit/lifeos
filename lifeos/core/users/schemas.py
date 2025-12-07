"""Typed schemas for user IO."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from lifeos.core.users.preferences import get_preferences

if TYPE_CHECKING:
    from lifeos.core.users.models import User


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    timezone: Optional[str] = None


class UserCreateRequest(UserBase):
    password: str = Field(min_length=8)


class UserUpdateRequest(UserBase):
    password: Optional[str] = Field(default=None, min_length=8)
    is_active: Optional[bool] = True


class LoginRequest(BaseModel):
    email: str
    password: str


class UserPreferenceSchema(BaseModel):
    key: str
    value: Dict[str, Any]


class UserResponse(UserBase):
    # Response should not re-validate persisted emails (demo domains, etc.)
    email: str
    id: int
    is_active: bool
    preferences: Dict[str, Any] = {}
    role_codes: List[str] = []

    model_config = ConfigDict(from_attributes=True)


def serialize_user(user: "User") -> "UserResponse":
    """Build a UserResponse with merged preferences."""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        timezone=user.timezone,
        is_active=user.is_active,
        preferences=get_preferences(user),
        role_codes=user.role_codes,
    )
