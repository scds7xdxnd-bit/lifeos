"""Personal AI assistant stub."""

from __future__ import annotations

from typing import List

from lifeos.core.insights.engine import insights_engine
from lifeos.core.insights.ml.embeddings import embed_text


class AIAssistant:
    """Simple assistant that can echo queries and surface insights."""

    def __init__(self) -> None:
        self.memory: List[dict] = []

    def remember(self, item: dict) -> None:
        item = {**item, "vector": embed_text(str(item))}
        self.memory.append(item)

    def query(self, prompt: str) -> dict:
        # In a real system we'd retrieve top memories; here we return a placeholder.
        related = [m for m in self.memory[-3:]]
        insights = []  # Could pull from insights_engine cache
        return {
            "reply": f"I received your prompt: '{prompt}'. ({len(related)} related memories)",
            "related": related,
            "insights": insights,
        }


assistant = AIAssistant()

