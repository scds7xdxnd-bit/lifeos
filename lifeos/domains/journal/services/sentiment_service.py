"""Simple sentiment heuristic."""

from __future__ import annotations


def analyze_sentiment(content: str) -> str:
    lowered = content.lower()
    if any(word in lowered for word in ("great", "good", "happy", "excited")):
        return "positive"
    if any(word in lowered for word in ("bad", "sad", "angry", "tired")):
        return "negative"
    return "neutral"
