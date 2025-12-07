"""Schemas for auth flows (register, recovery, reset)."""

from __future__ import annotations

import re
from typing import Optional
from zoneinfo import available_timezones

from pydantic import BaseModel, EmailStr, Field, field_validator

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
