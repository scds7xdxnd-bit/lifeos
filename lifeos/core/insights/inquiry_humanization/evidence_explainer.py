"""Deterministic evidence-to-meaning renderers for humanized inquiry output."""

from __future__ import annotations

from collections import Counter

from lifeos.core.insights.inquiry_humanization.adapters import HumanizationAdapter
from lifeos.core.insights.inquiry_humanization.contracts import CanonicalFinding


def explain_evidence(finding: CanonicalFinding, adapter: HumanizationAdapter) -> str:
    refs = list(finding.evidence_refs)
    if not refs:
        return "Support is limited in the saved record for this point."
    kinds = Counter(str(ref.get("source_kind") or "") for ref in refs)
    domains = sorted({str(ref.get("domain") or "") for ref in refs if str(ref.get("domain") or "").strip()})
    if len(domains) > 1:
        return f"Support comes from saved records across {', '.join(domains)} in the selected time range."
    count = len(refs)
    if kinds.get("event_record", 0) > 0:
        label = adapter.event_record_label_plural if count != 1 else adapter.event_record_label_singular
        return f"Support comes from {count} {label} in the selected time range."
    if kinds.get("insight_record", 0) > 0:
        return "Support comes from earlier saved insight records in the selected time range."
    return "Support comes from saved summary counts in the selected time range."


__all__ = ["explain_evidence"]
