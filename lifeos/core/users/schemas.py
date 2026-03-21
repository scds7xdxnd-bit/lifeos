"""Typed schemas for user IO."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

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
    onboarding_completed: bool = False

    model_config = ConfigDict(from_attributes=True)


class OnboardingStatusResponse(BaseModel):
    completed: bool = False
    domains: List[str] = []
    calendar_source: Optional[str] = None


class OnboardingStepRequest(BaseModel):
    step: str = Field(pattern=r"^(domains|calendar|complete)$")
    data: Dict[str, Any] = {}


def serialize_user(user: "User") -> "UserResponse":
    """Build a UserResponse with merged preferences."""
    prefs = get_preferences(user)
    onboarding_pref = prefs.get("onboarding_completed", {})
    onboarding_done = onboarding_pref.get("v", False) if isinstance(onboarding_pref, dict) else False
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        timezone=user.timezone,
        is_active=user.is_active,
        preferences=prefs,
        role_codes=user.role_codes,
        onboarding_completed=onboarding_done,
    )
