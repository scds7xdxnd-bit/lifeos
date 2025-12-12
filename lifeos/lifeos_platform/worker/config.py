"""Configuration helpers for the outbox dispatcher worker."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class DispatchConfig:
    """Runtime knobs for the dispatcher loop."""

    batch_size: int
    poll_interval: float
    max_attempts: int
    backoff_seconds: float
    backoff_multiplier: float

    @classmethod
    def from_env(cls) -> "DispatchConfig":
        """Build config from environment with sensible defaults."""
        return cls(
            batch_size=int(os.environ.get("OUTBOX_BATCH_SIZE", "50")),
            poll_interval=float(os.environ.get("OUTBOX_POLL_INTERVAL", "5")),
            max_attempts=int(os.environ.get("OUTBOX_MAX_ATTEMPTS", "5")),
            backoff_seconds=float(os.environ.get("OUTBOX_BACKOFF_SECONDS", "5")),
            backoff_multiplier=float(os.environ.get("OUTBOX_BACKOFF_MULTIPLIER", "2")),
        )
