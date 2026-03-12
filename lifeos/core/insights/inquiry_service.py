"""Focused Inquiry v1 service stack (validator -> router -> brief assembly -> history)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, time
from time import perf_counter
from typing import Iterable

from flask import current_app, has_app_context
from sqlalchemy import or_

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.inquiry_cross_domain.engine import synthesize_cross_domain_brief
from lifeos.core.insights.inquiry_cross_domain.pairs.base import CrossDomainPairProfile
from lifeos.core.insights.inquiry_cross_domain.registry import get_cross_domain_strategy
from lifeos.core.insights.inquiry_quality import evaluate_inquiry_brief_quality
from lifeos.core.insights.inquiry_schemas import InquiryCreateRequest, InquiryRefineRequest
from lifeos.core.insights.inquiry_strategies import (
    GENERIC_BRIEF_PROFILE,
    enforce_claim_guardrail,
    get_domain_strategy,
    strategy_token_for_scope,
)
from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile
from lifeos.core.insights.models import InquiryBriefVersion, InquiryRequest, InsightRecord
from lifeos.core.observability import (
    record_inquiry_blocked_claims,
    record_inquiry_created,
    record_inquiry_generated,
    record_inquiry_refine_after_low_coverage,
    record_inquiry_refine_after_low_quality,
    record_inquiry_refined,
    record_inquiry_replay_mismatch,
    record_inquiry_viewed,
)
from lifeos.core.read_cache import read_cache
from lifeos.extensions import db

INQUIRY_READ_CACHE_SCOPE = "inquiry.reads"
MAX_EVIDENCE_EVENTS_PER_DOMAIN = 3
MAX_EVIDENCE_INSIGHTS_PER_DOMAIN = 2
LOW_COVERAGE_THRESHOLD = 0.8
_SOURCE_KIND_PRIORITY = {
    "event_record": 0,
    "insight_record": 1,
    "read_model": 2,
}


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
    strategy_profile_token = strategy_token_for_scope(
        lens=scope.lens,
        primary_domain=scope.primary_domain,
        domains=scope.domains,
    )
    if scope.lens == "cross_domain" and len(scope.domains) == 2:
        active_pair_profile = _resolve_cross_domain_profile(scope.domains)
        if active_pair_profile is not None:
            strategy_profile_token = (
                f"{active_pair_profile.profile}:"
                f"{active_pair_profile.profile_version}:"
                f"{active_pair_profile.strategy_version}"
            )
        else:
            strategy_profile_token = (
                f"{GENERIC_BRIEF_PROFILE['profile']}:"
                f"{GENERIC_BRIEF_PROFILE['profile_version']}:"
                f"{GENERIC_BRIEF_PROFILE['strategy_version']}"
            )
    return {
        "question": scope.question,
        "lens": scope.lens,
        "domains": scope.domains,
        "timeframe_start": scope.timeframe_start.isoformat(),
        "timeframe_end": scope.timeframe_end.isoformat(),
        "as_of_ts": scope.as_of_ts.isoformat(),
        "context_text": scope.context_text or "",
        "context_semantics": "non_evidence",
        "strategy_profile_token": strategy_profile_token,
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


def _sorted_cross_domain_evidence_refs(refs: list[dict]) -> list[dict]:
    return sorted(
        refs,
        key=lambda item: (
            str(item.get("created_at") or ""),
            _SOURCE_KIND_PRIORITY.get(str(item.get("source_kind") or ""), 99),
            int(item.get("source_id") or 0),
            str(item.get("source_ref") or ""),
        ),
    )


def _finding_confidence(*, event_count: int, insight_count: int, mixed_domains: bool) -> str:
    if mixed_domains:
        return "needs_review"
    if event_count + insight_count >= 3:
        return "informational"
    return "needs_review"


def _strategy_profile_metadata(
    *,
    scope: InquiryScope,
    strategy: DomainStrategyProfile | None,
    cross_domain_profile: CrossDomainPairProfile | None,
    finding_categories: list[str],
) -> dict[str, object]:
    if cross_domain_profile is not None:
        return {
            "profile": cross_domain_profile.profile,
            "profile_version": cross_domain_profile.profile_version,
            "strategy": cross_domain_profile.strategy,
            "strategy_version": cross_domain_profile.strategy_version,
            "domain": cross_domain_profile.domain,
            "expert_mode": True,
            "finding_categories": sorted(set(finding_categories)),
        }
    if strategy is None:
        return {
            **GENERIC_BRIEF_PROFILE,
            "domain": scope.primary_domain if scope.lens == "domain" else "cross_domain",
            "expert_mode": False,
            "finding_categories": sorted(set(finding_categories)),
        }
    return {
        "profile": strategy.profile,
        "profile_version": strategy.profile_version,
        "strategy": strategy.strategy,
        "strategy_version": strategy.strategy_version,
        "domain": strategy.domain,
        "expert_mode": True,
        "finding_categories": sorted(set(finding_categories)),
    }


def _phase8_pair_profiles_enabled() -> bool:
    if not has_app_context():
        return False
    return bool(current_app.config.get("ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES", False))


def _phase8_enabled_pair_profiles() -> set[str] | None:
    if not has_app_context():
        return None
    configured = current_app.config.get("PHASE8_ENABLED_PAIR_PROFILES")
    if not configured:
        return None
    if isinstance(configured, str):
        raw_items = configured.split(",")
    else:
        raw_items = list(configured)
    allowed = {str(item).strip() for item in raw_items if str(item).strip()}
    return allowed or None


def _resolve_cross_domain_profile(domains: list[str]) -> CrossDomainPairProfile | None:
    if len(domains) != 2:
        return None
    if not _phase8_pair_profiles_enabled():
        return None
    profile = get_cross_domain_strategy(domains)
    if profile is None:
        return None
    allowed_profiles = _phase8_enabled_pair_profiles()
    if allowed_profiles is not None and profile.profile not in allowed_profiles:
        return None
    return profile


def _prioritize_domain_events(events: list[EventRecord], strategy: DomainStrategyProfile) -> list[EventRecord]:
    return sorted(
        events,
        key=lambda event: (
            strategy.event_priority(event.event_type),
            event.created_at.isoformat() if event.created_at else "",
            event.id,
        ),
    )


def _prioritize_domain_insights(insights: list[InsightRecord], strategy: DomainStrategyProfile) -> list[InsightRecord]:
    return sorted(
        insights,
        key=lambda insight: (
            strategy.insight_priority(insight.kind),
            insight.created_at.isoformat() if insight.created_at else "",
            insight.id,
        ),
    )


def _assemble_domain_expert_brief(
    *,
    strategy: DomainStrategyProfile,
    scope: InquiryScope,
    domain_events: list[EventRecord],
    domain_insights: list[InsightRecord],
) -> tuple[list[dict], list[str], list[dict], list[str]]:
    prioritized_events = _prioritize_domain_events(domain_events, strategy)
    prioritized_insights = _prioritize_domain_insights(domain_insights, strategy)

    aggregate = _aggregate_ref(
        domain=strategy.domain,
        timeframe_start=scope.timeframe_start,
        timeframe_end=scope.timeframe_end,
        as_of_ts=scope.as_of_ts,
        event_count=len(prioritized_events),
        insight_count=len(prioritized_insights),
    )
    evidence_refs = [aggregate]
    evidence_refs.extend(_serialize_event_ref(event) for event in prioritized_events[:MAX_EVIDENCE_EVENTS_PER_DOMAIN])
    evidence_refs.extend(
        _serialize_insight_ref(insight) for insight in prioritized_insights[:MAX_EVIDENCE_INSIGHTS_PER_DOMAIN]
    )
    evidence_refs = _sorted_evidence_refs(evidence_refs)

    findings: list[dict] = []
    limits: list[str] = []
    refine_guidance = list(strategy.refine_guidance)
    total_records = len(prioritized_events) + len(prioritized_insights)

    if total_records == 0:
        raw_claim = f"No canonical {strategy.domain} records were found in the selected inquiry timeframe."
        claim = enforce_claim_guardrail(
            raw_claim,
            allowed_prefixes=strategy.allowed_claim_prefixes,
            forbidden_tokens=strategy.forbidden_claim_tokens,
            fallback=f"No canonical {strategy.domain} records were observed in the selected timeframe.",
        )
        findings.append(
            {
                "claim": claim,
                "finding_category": strategy.gap_category,
                "evidence_refs": evidence_refs,
                "confidence_label": "needs_review",
                "uncertainty_note": strategy.limitation_language[0],
                "source_domains": [strategy.domain],
            }
        )
        limits.append(f"{strategy.domain}: {strategy.limitation_language[0]}")
        return findings, limits, evidence_refs, refine_guidance

    coverage_claim = (
        f"{strategy.domain.title()} evidence includes {len(prioritized_events)} events and "
        f"{len(prioritized_insights)} related insight records in scope."
    )
    coverage_claim = enforce_claim_guardrail(
        coverage_claim,
        allowed_prefixes=strategy.allowed_claim_prefixes,
        forbidden_tokens=strategy.forbidden_claim_tokens,
        fallback=f"{strategy.domain.title()} evidence volume was observed in scope.",
    )
    findings.append(
        {
            "claim": coverage_claim,
            "finding_category": strategy.coverage_category,
            "evidence_refs": evidence_refs,
            "confidence_label": _finding_confidence(
                event_count=len(prioritized_events),
                insight_count=len(prioritized_insights),
                mixed_domains=False,
            ),
            "uncertainty_note": (
                strategy.limitation_language[0] if total_records < 3 else strategy.limitation_language[1]
            ),
            "source_domains": [strategy.domain],
        }
    )

    if prioritized_insights:
        signal_claim = (
            f"{strategy.domain.title()} derived signals are present in {len(prioritized_insights)} insight records."
        )
        signal_claim = enforce_claim_guardrail(
            signal_claim,
            allowed_prefixes=strategy.allowed_claim_prefixes,
            forbidden_tokens=strategy.forbidden_claim_tokens,
            fallback=f"{strategy.domain.title()} derived signals were observed in the selected timeframe.",
        )
        findings.append(
            {
                "claim": signal_claim,
                "finding_category": strategy.signal_category,
                "evidence_refs": evidence_refs,
                "confidence_label": _finding_confidence(
                    event_count=len(prioritized_events),
                    insight_count=len(prioritized_insights),
                    mixed_domains=False,
                ),
                "uncertainty_note": strategy.limitation_language[1],
                "source_domains": [strategy.domain],
            }
        )

    limits.append(f"{strategy.domain}: {strategy.limitation_language[1]}")
    return findings, limits, evidence_refs, refine_guidance


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
    domain_refine_guidance: list[str] = []
    blocked_claim_count = 0
    active_cross_domain_profile = None
    if scope.lens == "cross_domain" and len(scope.domains) == 2:
        active_cross_domain_profile = _resolve_cross_domain_profile(scope.domains)
    applied_strategy = (
        get_domain_strategy(scope.primary_domain) if scope.lens == "domain" and len(scope.domains) == 1 else None
    )

    if active_cross_domain_profile:
        synthesis = synthesize_cross_domain_brief(
            profile=active_cross_domain_profile,
            timeframe_start=scope.timeframe_start,
            timeframe_end=scope.timeframe_end,
            as_of_ts=scope.as_of_ts,
            events_by_domain=events_by_domain,
            insights_by_domain=insights_by_domain,
        )
        findings.extend(synthesis.findings)
        limits.extend(synthesis.limits)
        provenance_refs.extend(synthesis.provenance_refs)
        domain_refine_guidance.extend(synthesis.refine_guidance)
        blocked_claim_count = synthesis.blocked_claim_count
    elif applied_strategy:
        domain = scope.primary_domain
        strategy_findings, strategy_limits, strategy_refs, strategy_guidance = _assemble_domain_expert_brief(
            strategy=applied_strategy,
            scope=scope,
            domain_events=events_by_domain.get(domain, []),
            domain_insights=insights_by_domain.get(domain, []),
        )
        findings.extend(strategy_findings)
        limits.extend(strategy_limits)
        provenance_refs.extend(strategy_refs)
        domain_refine_guidance.extend(strategy_guidance)
    else:
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
            evidence_refs.extend(
                _serialize_event_ref(event) for event in domain_events[:MAX_EVIDENCE_EVENTS_PER_DOMAIN]
            )
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
                claim = (
                    f"{domain.title()} shows {len(domain_events)} events and "
                    f"{len(domain_insights)} related insights."
                )
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
                    "finding_category": "coverage",
                    "evidence_refs": evidence_refs,
                    "confidence_label": confidence_label,
                    "uncertainty_note": uncertainty_note,
                    "source_domains": [domain],
                }
            )

    if scope.lens == "cross_domain" and active_cross_domain_profile is None:
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
                "finding_category": "cross_domain_coverage",
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
    if active_cross_domain_profile:
        summary = (
            f"Cross-domain pair brief ({active_cross_domain_profile.profile_version}) for "
            f"{active_cross_domain_profile.domain} covers {total_events} events and "
            f"{total_insights} prior insight records."
        )
        if total_events + total_insights == 0:
            summary = (
                f"Cross-domain pair brief for {active_cross_domain_profile.domain} found no canonical records "
                "in the selected timeframe."
            )
    elif applied_strategy:
        summary = (
            f"{scope.primary_domain.title()} domain expert brief ({applied_strategy.profile_version}) "
            f"covers {total_events} events and {total_insights} prior insight records."
        )
    else:
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
    payload["brief_profile"] = _strategy_profile_metadata(
        scope=scope,
        strategy=applied_strategy,
        cross_domain_profile=active_cross_domain_profile,
        finding_categories=[str(item.get("finding_category") or "") for item in findings],
    )
    payload["quality_metadata"] = evaluate_inquiry_brief_quality(
        payload,
        preferred_refine_guidance=domain_refine_guidance,
    )
    if scope.lens == "cross_domain":
        payload["blocked_claim_count"] = int(blocked_claim_count)
    if active_cross_domain_profile is not None:
        return payload, _sorted_cross_domain_evidence_refs(provenance_refs)
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


def _quality_state_from_metadata(quality_metadata: dict[str, object] | None) -> str | None:
    if not isinstance(quality_metadata, dict):
        return None
    findings_total = int(quality_metadata.get("findings_total") or 0)
    coverage = float(quality_metadata.get("evidence_coverage_ratio") or 0.0)
    structure_gaps = list(quality_metadata.get("structure_gaps") or [])
    sparse_domains = list(quality_metadata.get("sparse_domains") or [])
    if findings_total == 0:
        return "empty"
    if coverage < LOW_COVERAGE_THRESHOLD:
        return "low_coverage"
    if structure_gaps or sparse_domains:
        return "needs_refine"
    return "sufficient"


def _quality_storage_fields(brief_payload: dict) -> dict[str, object]:
    quality_metadata = brief_payload.get("quality_metadata") if isinstance(brief_payload, dict) else None
    if not isinstance(quality_metadata, dict):
        return {
            "quality_findings_total": None,
            "quality_findings_with_evidence": None,
            "quality_evidence_coverage_ratio": None,
            "quality_structure_gaps": None,
            "quality_sparse_domains": None,
            "quality_refine_guidance": None,
            "quality_state": None,
        }
    structure_gaps = sorted({str(item) for item in list(quality_metadata.get("structure_gaps") or []) if item})
    sparse_domains = sorted({str(item) for item in list(quality_metadata.get("sparse_domains") or []) if item})
    refine_guidance = [str(item) for item in list(quality_metadata.get("refine_guidance") or []) if item]
    return {
        "quality_findings_total": int(quality_metadata.get("findings_total") or 0),
        "quality_findings_with_evidence": int(quality_metadata.get("findings_with_evidence") or 0),
        "quality_evidence_coverage_ratio": float(quality_metadata.get("evidence_coverage_ratio") or 0.0),
        "quality_structure_gaps": structure_gaps,
        "quality_sparse_domains": sparse_domains,
        "quality_refine_guidance": refine_guidance,
        "quality_state": _quality_state_from_metadata(quality_metadata),
    }


def _brief_profile_storage_fields(brief_payload: dict) -> dict[str, object]:
    brief_profile = brief_payload.get("brief_profile") if isinstance(brief_payload, dict) else None
    if not isinstance(brief_profile, dict):
        return {
            "brief_profile": None,
            "brief_profile_version": None,
            "brief_strategy": None,
            "brief_strategy_version": None,
            "brief_domain": None,
            "brief_expert_mode": None,
            "finding_categories": None,
        }
    finding_categories = sorted({str(item) for item in list(brief_profile.get("finding_categories") or []) if item})
    return {
        "brief_profile": str(brief_profile.get("profile") or "") or None,
        "brief_profile_version": str(brief_profile.get("profile_version") or "") or None,
        "brief_strategy": str(brief_profile.get("strategy") or "") or None,
        "brief_strategy_version": str(brief_profile.get("strategy_version") or "") or None,
        "brief_domain": str(brief_profile.get("domain") or "") or None,
        "brief_expert_mode": bool(brief_profile.get("expert_mode")),
        "finding_categories": finding_categories,
    }


def _cross_domain_storage_fields(brief_payload: dict) -> dict[str, object]:
    if not isinstance(brief_payload, dict):
        return {
            "cross_domain_profile": None,
            "cross_domain_profile_version": None,
            "selected_domains": None,
            "selected_domains_key": None,
            "blocked_claim_count": None,
        }
    lens = str(brief_payload.get("lens") or "").strip().lower()
    if lens != "cross_domain":
        return {
            "cross_domain_profile": None,
            "cross_domain_profile_version": None,
            "selected_domains": None,
            "selected_domains_key": None,
            "blocked_claim_count": None,
        }
    brief_profile = brief_payload.get("brief_profile") if isinstance(brief_payload.get("brief_profile"), dict) else {}
    selected_domains = sorted({str(item) for item in list(brief_payload.get("domains") or []) if item})
    selected_domains_key = "|".join(selected_domains) if selected_domains else None
    return {
        "cross_domain_profile": str(brief_profile.get("profile") or "") or None,
        "cross_domain_profile_version": str(brief_profile.get("profile_version") or "") or None,
        "selected_domains": selected_domains,
        "selected_domains_key": selected_domains_key,
        "blocked_claim_count": int(brief_payload.get("blocked_claim_count") or 0),
    }


def _brief_profile_metric_labels(brief_payload: dict | None) -> dict[str, object]:
    brief_profile = brief_payload.get("brief_profile") if isinstance(brief_payload, dict) else None
    if not isinstance(brief_profile, dict):
        return {
            "domain": "unknown",
            "profile": "unknown",
            "profile_version": "unknown",
            "strategy": "unknown",
            "strategy_version": "unknown",
            "expert_mode": False,
        }
    return {
        "domain": str(brief_profile.get("domain") or "unknown"),
        "profile": str(brief_profile.get("profile") or "unknown"),
        "profile_version": str(brief_profile.get("profile_version") or "unknown"),
        "strategy": str(brief_profile.get("strategy") or "unknown"),
        "strategy_version": str(brief_profile.get("strategy_version") or "unknown"),
        "expert_mode": bool(brief_profile.get("expert_mode")),
    }


def _has_replay_mismatch(
    *,
    user_id: int,
    normalized_hash: str,
    as_of_ts: datetime,
    brief_hash: str,
    exclude_version_id: int | None = None,
) -> bool:
    query = InquiryBriefVersion.query.filter(
        InquiryBriefVersion.user_id == user_id,
        InquiryBriefVersion.normalized_hash == normalized_hash,
        InquiryBriefVersion.as_of_ts == as_of_ts,
        InquiryBriefVersion.brief_hash != brief_hash,
    )
    if exclude_version_id is not None:
        query = query.filter(InquiryBriefVersion.id != exclude_version_id)
    return query.first() is not None


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
    quality_storage_fields = _quality_storage_fields(brief_payload)
    brief_profile_storage_fields = _brief_profile_storage_fields(brief_payload)
    cross_domain_storage_fields = _cross_domain_storage_fields(brief_payload)
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
        **quality_storage_fields,
        **brief_profile_storage_fields,
        **cross_domain_storage_fields,
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
    profile_labels = _brief_profile_metric_labels(brief_payload)
    record_inquiry_generated(
        latency_seconds=generation_latency_seconds,
        is_empty=findings_with_evidence == 0,
        findings_total=findings_total,
        findings_with_evidence=findings_with_evidence,
        quality_metadata=brief_payload.get("quality_metadata") if isinstance(brief_payload, dict) else None,
        **profile_labels,
    )
    if scope.lens == "cross_domain":
        record_inquiry_blocked_claims(int(brief_payload.get("blocked_claim_count") or 0), **profile_labels)
    if _has_replay_mismatch(
        user_id=user_id,
        normalized_hash=normalized_hash,
        as_of_ts=scope.as_of_ts,
        brief_hash=brief_hash,
        exclude_version_id=version.id,
    ):
        record_inquiry_replay_mismatch(**profile_labels)
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
    previous_quality_metadata: dict[str, object] | None = None
    if previous and isinstance(previous.brief_payload, dict):
        raw_quality = previous.brief_payload.get("quality_metadata")
        if isinstance(raw_quality, dict):
            previous_quality_metadata = raw_quality
    previous_profile_labels = _brief_profile_metric_labels(previous.brief_payload if previous else None)
    previous_version_number = previous.version_number if previous else 0
    record_inquiry_refine_after_low_quality(previous_quality_metadata, **previous_profile_labels)
    record_inquiry_refine_after_low_coverage(previous_quality_metadata, **previous_profile_labels)

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
    quality_storage_fields = _quality_storage_fields(brief_payload)
    brief_profile_storage_fields = _brief_profile_storage_fields(brief_payload)
    cross_domain_storage_fields = _cross_domain_storage_fields(brief_payload)
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
        **quality_storage_fields,
        **brief_profile_storage_fields,
        **cross_domain_storage_fields,
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
    profile_labels = _brief_profile_metric_labels(brief_payload)
    record_inquiry_refined(**profile_labels)
    findings_total, findings_with_evidence = _brief_evidence_stats(brief_payload)
    record_inquiry_generated(
        latency_seconds=generation_latency_seconds,
        is_empty=findings_with_evidence == 0,
        findings_total=findings_total,
        findings_with_evidence=findings_with_evidence,
        quality_metadata=brief_payload.get("quality_metadata") if isinstance(brief_payload, dict) else None,
        **profile_labels,
    )
    if scope.lens == "cross_domain":
        record_inquiry_blocked_claims(int(brief_payload.get("blocked_claim_count") or 0), **profile_labels)
    if _has_replay_mismatch(
        user_id=user_id,
        normalized_hash=normalized_hash,
        as_of_ts=scope.as_of_ts,
        brief_hash=brief_hash,
        exclude_version_id=version.id,
    ):
        record_inquiry_replay_mismatch(**profile_labels)
    return inquiry, version
