"""Placeholder device identity contracts (no fingerprinting or persistence)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceId:
    """Opaque device identifier placeholder (Phase 3c will define semantics)."""

    raw: Optional[str] = None


@dataclass
class DeviceFingerprint:
    """Stub for future device fingerprint payload; unused in Phase 3a/3b scaffold."""

    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


__all__ = ["DeviceId", "DeviceFingerprint"]
