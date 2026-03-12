"""Personalization hook (Phase 5c readiness, no-op by default)."""

from __future__ import annotations

import os
from typing import List, Optional, Sequence, TypeVar

from flask import current_app

T = TypeVar("T")


def personalization_enabled(config: Optional[dict] = None) -> bool:
    try:
        cfg = config or current_app.config
        return bool(cfg.get("PERSONALIZATION_ENABLED", False))
    except RuntimeError:
        return os.environ.get("PERSONALIZATION_ENABLED", "false").lower() in ("1", "true", "yes")


def rank_insights(
    user_id: int,
    candidates: Sequence[T],
    context: Optional[dict] = None,
) -> List[T]:
    """Return ordered candidates; no-op when personalization is disabled."""
    if not personalization_enabled():
        return list(candidates)
    return list(candidates)


__all__ = ["personalization_enabled", "rank_insights"]
