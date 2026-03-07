"""Finance-specific rules producing insights."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from lifeos.core.events.event_models import EventRecord

if TYPE_CHECKING:
    from lifeos.core.insights.replay import ReplayEvent


def apply_rules(event: EventRecord | "ReplayEvent") -> List[dict]:
    if event.event_type == "finance.transaction.created":
        amount = event.payload.get("amount")
        category = event.payload.get("category")
        return [
            {
                "type": "finance_spend",
                "message": f"Recorded spending of {amount} in {category}",
                "severity": "info",
                "context": event.payload,
            }
        ]
    if event.event_type == "finance.journal.posted":
        return [
            {
                "type": "journal_posted",
                "message": "Journal posted and balances updated.",
                "severity": "info",
                "context": event.payload,
            }
        ]
    return []
