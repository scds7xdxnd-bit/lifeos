"""Insights core event catalog (Focused Inquiry lifecycle)."""

from __future__ import annotations

INQUIRY_REQUESTED = "inquiry.requested"
INQUIRY_CONTEXT_SUBMITTED = "inquiry.context.submitted"
INQUIRY_BRIEF_GENERATED = "inquiry.brief.generated"
INQUIRY_BRIEF_VIEWED = "inquiry.brief.viewed"
INQUIRY_REFINED = "inquiry.refined"

EVENT_CATALOG = {
    INQUIRY_REQUESTED: {
        "version": "v1",
        "payload": {
            "inquiry_id": "int",
            "lens": "str",
            "domains": "list[str]",
            "timeframe_start": "date",
            "timeframe_end": "date",
            "as_of_ts": "datetime",
            "normalized_hash": "str",
        },
    },
    INQUIRY_CONTEXT_SUBMITTED: {
        "version": "v1",
        "payload": {
            "inquiry_id": "int",
            "context_non_evidence": "str",
        },
    },
    INQUIRY_BRIEF_GENERATED: {
        "version": "v1",
        "payload": {
            "inquiry_id": "int",
            "version_id": "int",
            "brief_hash": "str",
            "as_of_ts": "datetime",
        },
    },
    INQUIRY_BRIEF_VIEWED: {
        "version": "v1",
        "payload": {
            "inquiry_id": "int",
            "version_id": "int?",
        },
    },
    INQUIRY_REFINED: {
        "version": "v1",
        "payload": {
            "inquiry_id": "int",
            "previous_version": "int",
            "domains": "list[str]",
            "as_of_ts": "datetime",
            "normalized_hash": "str",
        },
    },
}

__all__ = [
    "INQUIRY_REQUESTED",
    "INQUIRY_CONTEXT_SUBMITTED",
    "INQUIRY_BRIEF_GENERATED",
    "INQUIRY_BRIEF_VIEWED",
    "INQUIRY_REFINED",
    "EVENT_CATALOG",
]
