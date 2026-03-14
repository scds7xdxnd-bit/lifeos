"""Approved deterministic phrases for Phase 10."""

from __future__ import annotations

SECTION_TITLES = {
    "what_stands_out": "What stands out",
    "why_it_matters": "Why it matters",
    "how_sure_this_is": "How sure this is",
    "what_to_review_next": "What to review next",
}

ANSWERABILITY_LABELS = {
    "strong_answerable": "Strongly answerable",
    "partial_answerable": "Partially answerable",
    "weak_answerable": "Weakly answerable",
}

ANSWERABILITY_HELPERS = {
    "strong_answerable": "The saved support is strong enough for a direct reading in this scope.",
    "partial_answerable": "The saved support is mixed, so this remains a partial reading.",
    "weak_answerable": "The saved support is limited, so this remains a weak reading.",
}

CONFIDENCE_HELPERS = {
    "confirmed": "Confirmed in the saved record.",
    "informational": "Supported by the saved record in this scope.",
    "suggested": "A suggested reading from the saved record in this scope.",
    "needs_review": "Needs review because the saved support is limited or mixed.",
}

TECHNICAL_VIEW_LABEL = "Technical brief"

__all__ = [
    "ANSWERABILITY_HELPERS",
    "ANSWERABILITY_LABELS",
    "CONFIDENCE_HELPERS",
    "SECTION_TITLES",
    "TECHNICAL_VIEW_LABEL",
]
