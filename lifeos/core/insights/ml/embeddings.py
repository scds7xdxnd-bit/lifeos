"""Placeholder embedding utilities for contextual recall."""

from __future__ import annotations

import hashlib
from typing import List


def embed_text(text: str) -> List[float]:
    """Return a deterministic pseudo-embedding vector."""
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # Return a short vector for demo purposes
    return [b / 255 for b in h[:16]]
