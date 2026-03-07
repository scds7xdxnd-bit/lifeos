"""Schemas for auth flows (register, recovery, reset)."""

from __future__ import annotations

import re
from typing import Optional
from zoneinfo import available_timezones

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

from lifeos.core.auth.constants import SESSION_SCOPE_ALL, SESSION_SCOPE_SINGLE

_PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")
_TIMEZONES = available_timezones()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = Field(default=None, max_length=255)
    timezone: Optional[str] = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not _PASSWORD_REGEX.match(v):
            raise ValueError("password must be at least 8 chars and include letters and numbers")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v not in _TIMEZONES:
            raise ValueError("invalid timezone")
        return v


class SessionAdminResetRequest(BaseModel):
    """Admin-only session reset payload (structure-only)."""

    user_id: int
    session_scope: str = Field(default=SESSION_SCOPE_ALL)
    session_id: Optional[str] = None
    reason: str = Field(min_length=1, max_length=255)

    @field_validator("session_scope")
    @classmethod
    def validate_scope(cls, value: str) -> str:
        if value not in (SESSION_SCOPE_ALL, SESSION_SCOPE_SINGLE):
            raise ValueError("invalid_scope")
        return value

    @field_validator("session_id")
    @classmethod
    def ensure_session_id_when_single(cls, value: Optional[str], info: ValidationInfo):
        scope = info.data.get("session_scope")
        if scope == SESSION_SCOPE_SINGLE and not value:
            raise ValueError("session_id_required")
        return value


class ForgotUsernameRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=8)
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not _PASSWORD_REGEX.match(v):
            raise ValueError("password must be at least 8 chars and include letters and numbers")
        return v
