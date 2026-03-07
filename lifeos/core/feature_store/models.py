"""Phase 5c feature store models (v1)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class FeatureStoreEntry(db.Model):
    __tablename__ = "features_v1"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "entity_type",
            "entity_id",
            "feature_name",
            "as_of_ts",
            "feature_version",
            name="uq_features_v1_scope_name_asof_version",
        ),
        db.Index("ix_features_v1_user_name_asof", "user_id", "feature_name", "as_of_ts"),
        db.Index("ix_features_v1_entity_name_asof", "entity_type", "entity_id", "feature_name", "as_of_ts"),
        db.Index("ix_features_v1_name_version", "feature_name", "feature_version"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(db.String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(db.String(128), nullable=False)
    feature_name: Mapped[str] = mapped_column(db.String(128), nullable=False)
    dtype: Mapped[str] = mapped_column(db.String(16), nullable=False)
    value: Mapped[object] = mapped_column(db.JSON, nullable=False)
    window: Mapped[str] = mapped_column(db.String(32), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(db.DateTime(), nullable=False)
    as_of_ts: Mapped[datetime] = mapped_column(db.DateTime(), nullable=False)
    feature_version: Mapped[str] = mapped_column(db.String(16), nullable=False)
    source_event_types: Mapped[list] = mapped_column(db.JSON, default=list)
    provenance_ref: Mapped[dict] = mapped_column(db.JSON, default=dict)
    backfill_policy: Mapped[str] = mapped_column(db.String(16), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(db.String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime(), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


__all__ = ["FeatureStoreEntry"]
