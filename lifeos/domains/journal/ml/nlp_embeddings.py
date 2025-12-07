"""Journal embeddings stub."""

from __future__ import annotations

from lifeos.core.insights.ml.embeddings import embed_text


def embed_entry(title: str, content: str):
    return embed_text(f"{title} {content}")

