"""Insight persistence models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class InsightRecord(db.Model):
    __tablename__ = "insight_record"
    __table_args__ = (
        db.Index("ix_insight_record_user_created_at", "user_id", "created_at"),
        db.Index("ix_insight_record_user_band_created", "user_id", "confidence_band", "created_at"),
        db.Index("ix_insight_record_user_routing_created", "user_id", "routing", "created_at"),
        db.Index("ix_insight_record_user_event_type_created", "user_id", "event_type", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), index=True)
    event_id: Mapped[int | None] = mapped_column(db.ForeignKey("event_record.id"), index=True)
    event_type: Mapped[str] = mapped_column(db.String(128), index=True)
    kind: Mapped[str] = mapped_column(db.String(64), index=True)
    message: Mapped[str] = mapped_column(db.Text, nullable=False, default="")
    severity: Mapped[str] = mapped_column(db.String(16), default="info")
    confidence_band: Mapped[str | None] = mapped_column(db.String(32), nullable=True)
    routing: Mapped[str | None] = mapped_column(db.String(32), nullable=True)
    priority: Mapped[int] = mapped_column(db.Integer, nullable=False, default=50)
    delivery_policy: Mapped[str] = mapped_column(db.String(32), nullable=False, default="feed")
    data: Mapped[dict] = mapped_column(db.JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)


class InquiryRequest(db.Model):
    __tablename__ = "inquiry_request"
    __table_args__ = (
        db.Index("ix_inquiry_request_user_created_at", "user_id", "created_at"),
        db.Index("ix_inquiry_request_user_normalized_hash", "user_id", "normalized_hash"),
        db.Index("ix_inquiry_request_user_as_of", "user_id", "as_of_ts"),
        db.Index(
            "ix_inquiry_request_user_domain_timeframe",
            "user_id",
            "primary_domain",
            "timeframe_start",
            "timeframe_end",
        ),
        db.Index(
            "ix_inquiry_request_user_hash_asof",
            "user_id",
            "normalized_hash",
            "as_of_ts",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    question: Mapped[str] = mapped_column(db.Text, nullable=False)
    lens: Mapped[str] = mapped_column(db.String(32), nullable=False)
    primary_domain: Mapped[str] = mapped_column(db.String(32), nullable=False)
    domains: Mapped[list] = mapped_column(db.JSON, nullable=False, default=list)
    timeframe_start: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    timeframe_end: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    as_of_ts: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, index=True)
    normalized_payload: Mapped[dict] = mapped_column(db.JSON, nullable=False, default=dict)
    normalized_hash: Mapped[str] = mapped_column(db.String(64), nullable=False)
    user_input_context: Mapped[str | None] = mapped_column(db.Text, nullable=True)
    context_is_non_evidence: Mapped[bool] = mapped_column(db.Boolean, nullable=False, default=True)
    last_version_number: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0)
    last_version_id: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, index=True)


class InquiryBriefVersion(db.Model):
    __tablename__ = "inquiry_brief_version"
    __table_args__ = (
        db.UniqueConstraint("inquiry_id", "version_number", name="uq_inquiry_version_number"),
        db.Index("ix_inquiry_brief_user_inquiry_version", "user_id", "inquiry_id", "version_number"),
        db.Index("ix_inquiry_brief_created_at", "created_at"),
        db.Index("ix_inquiry_brief_user_created_at", "user_id", "created_at"),
        db.Index("ix_inquiry_brief_user_domain_created", "user_id", "brief_domain", "created_at"),
        db.Index("ix_inquiry_brief_user_expert_created", "user_id", "brief_expert_mode", "created_at"),
        db.Index("ix_inquiry_brief_user_profile_created", "user_id", "brief_profile", "created_at"),
        db.Index(
            "ix_inquiry_brief_user_cross_profile_created",
            "user_id",
            "cross_domain_profile",
            "created_at",
        ),
        db.Index(
            "ix_inquiry_brief_user_cross_profile_version_created",
            "user_id",
            "cross_domain_profile_version",
            "created_at",
        ),
        db.Index(
            "ix_inquiry_brief_user_selected_domains_created",
            "user_id",
            "selected_domains_key",
            "created_at",
        ),
        db.Index(
            "ix_inquiry_brief_user_quality_state_created",
            "user_id",
            "quality_state",
            "created_at",
        ),
        db.Index(
            "ix_inquiry_brief_user_domain_quality_created",
            "user_id",
            "brief_domain",
            "quality_state",
            "created_at",
        ),
        db.Index(
            "ix_inquiry_brief_user_coverage_created",
            "user_id",
            "quality_evidence_coverage_ratio",
            "created_at",
        ),
        db.Index("ix_inquiry_brief_hash", "brief_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    inquiry_id: Mapped[int] = mapped_column(db.ForeignKey("inquiry_request.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(db.Integer, nullable=False)
    brief_payload: Mapped[dict] = mapped_column(db.JSON, nullable=False, default=dict)
    brief_hash: Mapped[str] = mapped_column(db.String(64), nullable=False)
    normalized_hash: Mapped[str] = mapped_column(db.String(64), nullable=False)
    as_of_ts: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    evidence_refs: Mapped[list] = mapped_column(db.JSON, nullable=False, default=list)
    brief_profile: Mapped[str | None] = mapped_column(db.String(64), nullable=True)
    brief_profile_version: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
    brief_strategy: Mapped[str | None] = mapped_column(db.String(64), nullable=True)
    brief_strategy_version: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
    brief_domain: Mapped[str | None] = mapped_column(db.String(32), nullable=True)
    brief_expert_mode: Mapped[bool | None] = mapped_column(db.Boolean, nullable=True)
    cross_domain_profile: Mapped[str | None] = mapped_column(db.String(64), nullable=True)
    cross_domain_profile_version: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
    selected_domains: Mapped[list | None] = mapped_column(db.JSON, nullable=True)
    selected_domains_key: Mapped[str | None] = mapped_column(db.String(128), nullable=True)
    finding_categories: Mapped[list | None] = mapped_column(db.JSON, nullable=True)
    blocked_claim_count: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    quality_findings_total: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    quality_findings_with_evidence: Mapped[int | None] = mapped_column(db.Integer, nullable=True)
    quality_evidence_coverage_ratio: Mapped[float | None] = mapped_column(db.Numeric(6, 4), nullable=True)
    quality_structure_gaps: Mapped[list | None] = mapped_column(db.JSON, nullable=True)
    quality_sparse_domains: Mapped[list | None] = mapped_column(db.JSON, nullable=True)
    quality_refine_guidance: Mapped[list | None] = mapped_column(db.JSON, nullable=True)
    quality_state: Mapped[str | None] = mapped_column(db.String(32), nullable=True)
    parent_version_id: Mapped[int | None] = mapped_column(db.ForeignKey("inquiry_brief_version.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, index=True)
