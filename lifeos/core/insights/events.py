"""Insights core event catalog (Focused Inquiry lifecycle)."""

from __future__ import annotations

INQUIRY_REQUESTED = "inquiry.requested"
INQUIRY_CONTEXT_SUBMITTED = "inquiry.context.submitted"
INQUIRY_BRIEF_GENERATED = "inquiry.brief.generated"
INQUIRY_BRIEF_VIEWED = "inquiry.brief.viewed"
INQUIRY_REFINED = "inquiry.refined"
INQUIRY_FEEDBACK_SUBMITTED = "inquiry.feedback.submitted"

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
            "canonical_brief_hash": "str?",
            "humanization_version": "str?",
            "humanized_brief_hash": "str?",
            "technical_view_available": "bool?",
            "timeline_profile_id": "str?",
            "timeline_profile_version": "str?",
            "timeline_engine_version": "str?",
            "window_spec_token": "str?",
            "active_window_token": "str?",
            "comparison_window_token": "str?",
            "baseline_policy_token": "str?",
            "timezone_token": "str?",
            "evidence_manifest_hash": "str?",
            "comparison_coverage": "dict?",
            "timeline_summary_hash": "str?",
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
    INQUIRY_FEEDBACK_SUBMITTED: {
        "version": "v1",
        "payload": {
            "inquiry_id": "int",
            "version_id": "int",
            "canonical_brief_hash": "str",
            "humanization_version": "str?",
            "surface": "str",
            "feedback_type": "str",
        },
    },
}

__all__ = [
    "INQUIRY_REQUESTED",
    "INQUIRY_CONTEXT_SUBMITTED",
    "INQUIRY_BRIEF_GENERATED",
    "INQUIRY_BRIEF_VIEWED",
    "INQUIRY_REFINED",
    "INQUIRY_FEEDBACK_SUBMITTED",
    "EVENT_CATALOG",
]
