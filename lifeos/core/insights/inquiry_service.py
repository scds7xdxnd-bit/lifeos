"""Focused Inquiry v1 service stack (validator -> router -> brief assembly -> history)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, time
from time import perf_counter
from typing import Iterable

from sqlalchemy import or_

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.inquiry_schemas import InquiryCreateRequest, InquiryRefineRequest
from lifeos.core.insights.models import InquiryBriefVersion, InquiryRequest, InsightRecord
from lifeos.core.observability import (
    record_inquiry_created,
    record_inquiry_generated,
    record_inquiry_refined,
    record_inquiry_viewed,
)
from lifeos.core.read_cache import read_cache
from lifeos.extensions import db

INQUIRY_READ_CACHE_SCOPE = "inquiry.reads"
MAX_EVIDENCE_EVENTS_PER_DOMAIN = 3
MAX_EVIDENCE_INSIGHTS_PER_DOMAIN = 2


@dataclass(frozen=True)
class InquiryScope:
    lens: str
    domains: list[str]
    primary_domain: str
    timeframe_start: datetime
    timeframe_end: datetime
    as_of_ts: datetime
    question: str
    context_text: str | None


def _normalize_as_of_ts(as_of_ts: datetime | None) -> datetime:
    candidate = as_of_ts or datetime.utcnow()
    if candidate.tzinfo is not None:
        candidate = candidate.astimezone().replace(tzinfo=None)
    return candidate.replace(microsecond=0)


def _normalize_scope_from_create(data: InquiryCreateRequest) -> InquiryScope:
    start_dt = datetime.combine(data.timeframe_start, time.min)
    end_dt = datetime.combine(data.timeframe_end, time.max)
    as_of_ts = _normalize_as_of_ts(data.as_of_ts)
    lens = "cross_domain" if data.cross_domain else "domain"
    domains = sorted(data.domains or [])
    return InquiryScope(
        lens=lens,
        domains=domains,
        primary_domain=domains[0],
        timeframe_start=start_dt,
        timeframe_end=end_dt,
        as_of_ts=as_of_ts,
        question=data.question,
        context_text=data.context_text,
    )


def _normalize_scope_from_refine(existing: InquiryRequest, data: InquiryRefineRequest) -> InquiryScope:
    question = data.question or existing.question
    context_text = data.context_text if data.context_text is not None else existing.user_input_context
    as_of_ts = _normalize_as_of_ts(data.as_of_ts or existing.as_of_ts)

    if data.timeframe_start is not None and data.timeframe_end is not None:
        timeframe_start = datetime.combine(data.timeframe_start, time.min)
        timeframe_end = datetime.combine(data.timeframe_end, time.max)
    else:
        timeframe_start = existing.timeframe_start
        timeframe_end = existing.timeframe_end

    domains = list(existing.domains or [])
    if data.domains is not None:
        domains = sorted(data.domains)
    if data.domain:
        domain_set = set(domains)
        domain_set.add(data.domain)
        domains = sorted(domain_set)
    cross_domain = data.cross_domain if data.cross_domain is not None else (existing.lens == "cross_domain")

    if not domains:
        raise ValueError("domain_required")
    if cross_domain and len(domains) < 2:
        raise ValueError("cross_domain_requires_multiple_domains")
    if not cross_domain and len(domains) != 1:
        raise ValueError("single_domain_required")

    return InquiryScope(
        lens="cross_domain" if cross_domain else "domain",
        domains=domains,
        primary_domain=domains[0],
        timeframe_start=timeframe_start,
        timeframe_end=timeframe_end,
        as_of_ts=as_of_ts,
        question=question,
        context_text=context_text,
    )


def _normalized_payload(scope: InquiryScope) -> dict:
    return {
        "question": scope.question,
        "lens": scope.lens,
        "domains": scope.domains,
        "timeframe_start": scope.timeframe_start.isoformat(),
        "timeframe_end": scope.timeframe_end.isoformat(),
        "as_of_ts": scope.as_of_ts.isoformat(),
        "context_text": scope.context_text or "",
        "context_semantics": "non_evidence",
    }


def _payload_hash(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _domain_prefix_filters(domains: Iterable[str]) -> list:
    return [EventRecord.event_type.like(f"{domain}.%") for domain in domains]


def _domain_from_event_type(event_type: str | None) -> str:
    if not event_type:
        return "unknown"
    return str(event_type).split(".", 1)[0]


def _serialize_event_ref(event: EventRecord) -> dict:
    return {
        "source_kind": "event_record",
        "source_id": event.id,
        "event_type": event.event_type,
        "domain": _domain_from_event_type(event.event_type),
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def _serialize_insight_ref(insight: InsightRecord) -> dict:
    return {
        "source_kind": "insight_record",
        "source_id": insight.id,
        "insight_type": insight.kind,
        "event_type": insight.event_type,
        "domain": _domain_from_event_type(insight.event_type),
        "created_at": insight.created_at.isoformat() if insight.created_at else None,
    }


def _aggregate_ref(
    *,
    domain: str,
    timeframe_start: datetime,
    timeframe_end: datetime,
    as_of_ts: datetime,
    event_count: int,
    insight_count: int,
) -> dict:
    return {
        "source_kind": "read_model",
        "source_ref": (
            f"inquiry.event_count_projection:{domain}:{timeframe_start.date().isoformat()}:"
            f"{timeframe_end.date().isoformat()}:{as_of_ts.isoformat()}"
        ),
        "domain": domain,
        "event_count": event_count,
        "insight_count": insight_count,
    }


def _sorted_evidence_refs(refs: list[dict]) -> list[dict]:
    return sorted(
        refs,
        key=lambda item: (
            str(item.get("domain") or ""),
            str(item.get("source_kind") or ""),
            str(item.get("event_type") or item.get("source_ref") or ""),
            int(item.get("source_id") or 0),
        ),
    )


def _finding_confidence(*, event_count: int, insight_count: int, mixed_domains: bool) -> str:
    if mixed_domains:
        return "needs_review"
    if event_count + insight_count >= 3:
        return "informational"
    return "needs_review"


def _assemble_brief(scope: InquiryScope, user_id: int) -> tuple[dict, list[dict]]:
    prefix_filters = _domain_prefix_filters(scope.domains)

    events = (
        EventRecord.query.filter(EventRecord.user_id == user_id)
        .filter(EventRecord.created_at >= scope.timeframe_start)
        .filter(EventRecord.created_at <= min(scope.timeframe_end, scope.as_of_ts))
        .filter(or_(*prefix_filters))
        .order_by(EventRecord.created_at.asc(), EventRecord.id.asc())
        .all()
    )
    insights = (
        InsightRecord.query.filter(InsightRecord.user_id == user_id)
        .filter(InsightRecord.created_at >= scope.timeframe_start)
        .filter(InsightRecord.created_at <= min(scope.timeframe_end, scope.as_of_ts))
        .filter(or_(*[InsightRecord.event_type.like(f"{domain}.%") for domain in scope.domains]))
        .order_by(InsightRecord.created_at.asc(), InsightRecord.id.asc())
        .all()
    )

    events_by_domain: dict[str, list[EventRecord]] = {domain: [] for domain in scope.domains}
    for event in events:
        domain = _domain_from_event_type(event.event_type)
        if domain in events_by_domain:
            events_by_domain[domain].append(event)

    insights_by_domain: dict[str, list[InsightRecord]] = {domain: [] for domain in scope.domains}
    for insight in insights:
        domain = _domain_from_event_type(insight.event_type)
        if domain in insights_by_domain:
            insights_by_domain[domain].append(insight)

    findings: list[dict] = []
    limits: list[str] = []
    provenance_refs: list[dict] = []

    for domain in scope.domains:
        domain_events = events_by_domain[domain]
        domain_insights = insights_by_domain[domain]
        aggregate = _aggregate_ref(
            domain=domain,
            timeframe_start=scope.timeframe_start,
            timeframe_end=scope.timeframe_end,
            as_of_ts=scope.as_of_ts,
            event_count=len(domain_events),
            insight_count=len(domain_insights),
        )
        evidence_refs = [aggregate]
        evidence_refs.extend(_serialize_event_ref(event) for event in domain_events[:MAX_EVIDENCE_EVENTS_PER_DOMAIN])
        evidence_refs.extend(
            _serialize_insight_ref(insight) for insight in domain_insights[:MAX_EVIDENCE_INSIGHTS_PER_DOMAIN]
        )
        evidence_refs = _sorted_evidence_refs(evidence_refs)
        provenance_refs.extend(evidence_refs)

        total_records = len(domain_events) + len(domain_insights)
        if total_records == 0:
            claim = f"No canonical {domain} records were found in the selected timeframe."
            uncertainty_note = "Evidence is sparse for this domain in the selected window."
            limits.append(f"{domain}: no canonical records in selected timeframe.")
        else:
            claim = f"{domain.title()} shows {len(domain_events)} events and {len(domain_insights)} related insights."
            uncertainty_note = (
                "Evidence is partial; treat this as a directional observation."
                if total_records < 3
                else "Bounded to selected timeframe and explicit domain scope."
            )

        confidence_label = _finding_confidence(
            event_count=len(domain_events),
            insight_count=len(domain_insights),
            mixed_domains=False,
        )

        findings.append(
            {
                "claim": claim,
                "evidence_refs": evidence_refs,
                "confidence_label": confidence_label,
                "uncertainty_note": uncertainty_note,
                "source_domains": [domain],
            }
        )

    if scope.lens == "cross_domain":
        covered_domains = [
            domain for domain in scope.domains if len(events_by_domain[domain]) + len(insights_by_domain[domain]) > 0
        ]
        cross_evidence_refs = [
            _aggregate_ref(
                domain=domain,
                timeframe_start=scope.timeframe_start,
                timeframe_end=scope.timeframe_end,
                as_of_ts=scope.as_of_ts,
                event_count=len(events_by_domain[domain]),
                insight_count=len(insights_by_domain[domain]),
            )
            for domain in scope.domains
        ]
        cross_evidence_refs = _sorted_evidence_refs(cross_evidence_refs)
        provenance_refs.extend(cross_evidence_refs)
        coverage = f"{len(covered_domains)}/{len(scope.domains)}"
        uncertainty_note = (
            "Not all selected domains have sufficient canonical evidence."
            if len(covered_domains) < len(scope.domains)
            else "Cross-domain synthesis is bounded to selected domains only."
        )
        if len(covered_domains) < len(scope.domains):
            limits.append("Cross-domain coverage is incomplete.")
        findings.append(
            {
                "claim": f"Cross-domain coverage was observed in {coverage} selected domains.",
                "evidence_refs": cross_evidence_refs,
                "confidence_label": _finding_confidence(
                    event_count=len(covered_domains),
                    insight_count=0,
                    mixed_domains=True,
                ),
                "uncertainty_note": uncertainty_note,
                "source_domains": scope.domains,
            }
        )

    findings = sorted(
        findings,
        key=lambda item: (
            ",".join(item.get("source_domains", [])),
            item.get("claim", ""),
        ),
    )

    total_events = len(events)
    total_insights = len(insights)
    summary = (
        f"Scoped inquiry for {scope.primary_domain} across {len(scope.domains)} domain(s). "
        f"Evidence includes {total_events} events and {total_insights} prior insight records."
    )
    if total_events + total_insights == 0:
        summary = f"Scoped inquiry for {scope.primary_domain} found no canonical records in the selected timeframe."

    global_uncertainty = (
        "Evidence is bounded to the selected timeframe and explicit scope." if not limits else " ; ".join(limits)
    )

    payload = {
        "summary": summary,
        "findings": findings,
        "context_non_evidence": {
            "label": "Context (not evidence)",
            "text": scope.context_text or "",
            "note": "User-provided context is framing input and not treated as factual evidence.",
        },
        "uncertainty_note": global_uncertainty,
        "limits": limits,
        "question": scope.question,
        "lens": scope.lens,
        "domains": scope.domains,
        "timeframe": {
            "start": scope.timeframe_start.date().isoformat(),
            "end": scope.timeframe_end.date().isoformat(),
        },
        "as_of_ts": scope.as_of_ts.isoformat(),
        "generated_at": scope.as_of_ts.isoformat(),
    }
    return payload, _sorted_evidence_refs(provenance_refs)


def _new_event(*, user_id: int, event_type: str, payload: dict) -> None:
    db.session.add(
        EventRecord(
            event_type=event_type,
            payload=payload,
            user_id=user_id,
            created_at=datetime.utcnow(),
        )
    )


def _serialize_version(version: InquiryBriefVersion) -> dict:
    return {
        "id": version.id,
        "version_number": version.version_number,
        "parent_version_id": version.parent_version_id,
        "created_at": version.created_at.isoformat() if version.created_at else None,
        "brief_hash": version.brief_hash,
        "as_of_ts": version.as_of_ts.isoformat() if version.as_of_ts else None,
        "brief": version.brief_payload,
    }


def _serialize_inquiry(inquiry: InquiryRequest, latest_version: InquiryBriefVersion | None) -> dict:
    return {
        "id": inquiry.id,
        "question": inquiry.question,
        "lens": inquiry.lens,
        "domain": inquiry.primary_domain,
        "domains": inquiry.domains or [],
        "timeframe": {
            "start": inquiry.timeframe_start.date().isoformat(),
            "end": inquiry.timeframe_end.date().isoformat(),
        },
        "as_of_ts": inquiry.as_of_ts.isoformat(),
        "context_non_evidence": {
            "label": "Context (not evidence)",
            "text": inquiry.user_input_context or "",
        },
        "created_at": inquiry.created_at.isoformat() if inquiry.created_at else None,
        "updated_at": inquiry.updated_at.isoformat() if inquiry.updated_at else None,
        "last_version_number": inquiry.last_version_number,
        "latest_brief": _serialize_version(latest_version) if latest_version else None,
    }


def _brief_evidence_stats(brief_payload: dict) -> tuple[int, int]:
    findings = list(brief_payload.get("findings") or [])
    total = len(findings)
    with_evidence = 0
    for item in findings:
        refs = list(item.get("evidence_refs") or [])
        if any(ref.get("source_kind") in {"event_record", "insight_record"} for ref in refs):
            with_evidence += 1
    return total, with_evidence


def create_inquiry(user_id: int, data: InquiryCreateRequest) -> tuple[InquiryRequest, InquiryBriefVersion, bool]:
    scope = _normalize_scope_from_create(data)
    normalized_payload = _normalized_payload(scope)
    normalized_hash = _payload_hash(normalized_payload)

    existing = (
        InquiryRequest.query.filter_by(
            user_id=user_id,
            normalized_hash=normalized_hash,
            as_of_ts=scope.as_of_ts,
        )
        .order_by(InquiryRequest.id.desc())
        .first()
    )
    if existing and existing.last_version_id:
        latest = InquiryBriefVersion.query.filter_by(id=existing.last_version_id, user_id=user_id).first()
        if latest:
            return existing, latest, True

    inquiry = InquiryRequest(
        user_id=user_id,
        question=scope.question,
        lens=scope.lens,
        primary_domain=scope.primary_domain,
        domains=scope.domains,
        timeframe_start=scope.timeframe_start,
        timeframe_end=scope.timeframe_end,
        as_of_ts=scope.as_of_ts,
        normalized_payload=normalized_payload,
        normalized_hash=normalized_hash,
        user_input_context=scope.context_text,
        context_is_non_evidence=True,
    )
    db.session.add(inquiry)
    db.session.flush()

    _new_event(
        user_id=user_id,
        event_type="inquiry.requested",
        payload={
            "inquiry_id": inquiry.id,
            "lens": scope.lens,
            "domains": scope.domains,
            "timeframe_start": scope.timeframe_start.date().isoformat(),
            "timeframe_end": scope.timeframe_end.date().isoformat(),
            "as_of_ts": scope.as_of_ts.isoformat(),
            "normalized_hash": normalized_hash,
        },
    )
    if scope.context_text:
        _new_event(
            user_id=user_id,
            event_type="inquiry.context.submitted",
            payload={
                "inquiry_id": inquiry.id,
                "context_non_evidence": scope.context_text,
            },
        )

    generation_started = perf_counter()
    brief_payload, provenance_refs = _assemble_brief(scope, user_id)
    generation_latency_seconds = perf_counter() - generation_started
    brief_hash = _payload_hash(brief_payload)
    version = InquiryBriefVersion(
        inquiry_id=inquiry.id,
        user_id=user_id,
        version_number=1,
        brief_payload=brief_payload,
        brief_hash=brief_hash,
        normalized_hash=normalized_hash,
        as_of_ts=scope.as_of_ts,
        evidence_refs=provenance_refs,
        parent_version_id=None,
    )
    db.session.add(version)
    db.session.flush()
    inquiry.last_version_number = 1
    inquiry.last_version_id = version.id

    _new_event(
        user_id=user_id,
        event_type="inquiry.brief.generated",
        payload={
            "inquiry_id": inquiry.id,
            "version_id": version.id,
            "brief_hash": brief_hash,
            "as_of_ts": scope.as_of_ts.isoformat(),
        },
    )
    db.session.commit()
    read_cache.bump(INQUIRY_READ_CACHE_SCOPE, user_id)

    record_inquiry_created()
    findings_total, findings_with_evidence = _brief_evidence_stats(brief_payload)
    record_inquiry_generated(
        latency_seconds=generation_latency_seconds,
        is_empty=findings_with_evidence == 0,
        findings_total=findings_total,
        findings_with_evidence=findings_with_evidence,
    )
    return inquiry, version, False


def list_inquiries(user_id: int, *, limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
    total = InquiryRequest.query.filter_by(user_id=user_id).count()
    rows = (
        InquiryRequest.query.filter_by(user_id=user_id)
        .order_by(InquiryRequest.updated_at.desc(), InquiryRequest.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    items: list[dict] = []
    for row in rows:
        latest = InquiryBriefVersion.query.filter_by(id=row.last_version_id, user_id=user_id).first()
        items.append(_serialize_inquiry(row, latest))
    return items, total


def get_inquiry(user_id: int, inquiry_id: int) -> dict | None:
    inquiry = InquiryRequest.query.filter_by(id=inquiry_id, user_id=user_id).first()
    if not inquiry:
        return None
    versions = (
        InquiryBriefVersion.query.filter_by(inquiry_id=inquiry.id, user_id=user_id)
        .order_by(InquiryBriefVersion.version_number.asc())
        .all()
    )
    latest = versions[-1] if versions else None
    _new_event(
        user_id=user_id,
        event_type="inquiry.brief.viewed",
        payload={"inquiry_id": inquiry.id, "version_id": latest.id if latest else None},
    )
    db.session.commit()
    read_cache.bump(INQUIRY_READ_CACHE_SCOPE, user_id)
    record_inquiry_viewed()
    payload = _serialize_inquiry(inquiry, latest)
    payload["versions"] = [_serialize_version(version) for version in versions]
    return payload


def refine_inquiry(
    user_id: int, inquiry_id: int, data: InquiryRefineRequest
) -> tuple[InquiryRequest, InquiryBriefVersion]:
    inquiry = InquiryRequest.query.filter_by(id=inquiry_id, user_id=user_id).first()
    if not inquiry:
        raise ValueError("not_found")

    scope = _normalize_scope_from_refine(inquiry, data)
    normalized_payload = _normalized_payload(scope)
    normalized_hash = _payload_hash(normalized_payload)

    previous = (
        InquiryBriefVersion.query.filter_by(inquiry_id=inquiry.id, user_id=user_id)
        .order_by(InquiryBriefVersion.version_number.desc())
        .first()
    )
    previous_version_number = previous.version_number if previous else 0

    inquiry.question = scope.question
    inquiry.lens = scope.lens
    inquiry.primary_domain = scope.primary_domain
    inquiry.domains = scope.domains
    inquiry.timeframe_start = scope.timeframe_start
    inquiry.timeframe_end = scope.timeframe_end
    inquiry.as_of_ts = scope.as_of_ts
    inquiry.normalized_payload = normalized_payload
    inquiry.normalized_hash = normalized_hash
    inquiry.user_input_context = scope.context_text
    inquiry.context_is_non_evidence = True

    _new_event(
        user_id=user_id,
        event_type="inquiry.refined",
        payload={
            "inquiry_id": inquiry.id,
            "previous_version": previous_version_number,
            "domains": scope.domains,
            "as_of_ts": scope.as_of_ts.isoformat(),
            "normalized_hash": normalized_hash,
        },
    )
    if scope.context_text:
        _new_event(
            user_id=user_id,
            event_type="inquiry.context.submitted",
            payload={
                "inquiry_id": inquiry.id,
                "context_non_evidence": scope.context_text,
            },
        )

    generation_started = perf_counter()
    brief_payload, provenance_refs = _assemble_brief(scope, user_id)
    generation_latency_seconds = perf_counter() - generation_started
    brief_hash = _payload_hash(brief_payload)
    version = InquiryBriefVersion(
        inquiry_id=inquiry.id,
        user_id=user_id,
        version_number=previous_version_number + 1,
        brief_payload=brief_payload,
        brief_hash=brief_hash,
        normalized_hash=normalized_hash,
        as_of_ts=scope.as_of_ts,
        evidence_refs=provenance_refs,
        parent_version_id=previous.id if previous else None,
    )
    db.session.add(version)
    db.session.flush()

    inquiry.last_version_number = version.version_number
    inquiry.last_version_id = version.id

    _new_event(
        user_id=user_id,
        event_type="inquiry.brief.generated",
        payload={
            "inquiry_id": inquiry.id,
            "version_id": version.id,
            "brief_hash": brief_hash,
            "as_of_ts": scope.as_of_ts.isoformat(),
        },
    )
    db.session.commit()
    read_cache.bump(INQUIRY_READ_CACHE_SCOPE, user_id)
    record_inquiry_refined()
    findings_total, findings_with_evidence = _brief_evidence_stats(brief_payload)
    record_inquiry_generated(
        latency_seconds=generation_latency_seconds,
        is_empty=findings_with_evidence == 0,
        findings_total=findings_total,
        findings_with_evidence=findings_with_evidence,
    )
    return inquiry, version
