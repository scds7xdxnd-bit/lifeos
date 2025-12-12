"""Database models for readmodel replay metadata."""

from __future__ import annotations

from datetime import datetime

from lifeos.extensions import db


class ReadModelState(db.Model):
    __tablename__ = "readmodel_state"
    __table_args__ = (
        db.UniqueConstraint("model_name", "model_version", name="uq_readmodel_state_model_version"),
        db.Index("ix_readmodel_state_domain", "domain"),
        db.Index("ix_readmodel_state_last_replayed_event", "last_replayed_event_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(128), nullable=False)
    model_version = db.Column(db.String(32), nullable=False, default="v1")
    domain = db.Column(db.String(64), nullable=False)
    model_type = db.Column(db.String(32), nullable=False)
    idempotency_key = db.Column(db.String(255), nullable=False)
    replay_start_version = db.Column(db.String(64), nullable=True)
    rebuild_strategy = db.Column(db.String(255), nullable=True)
    consumed_events = db.Column(db.JSON, nullable=True)
    last_replayed_event_id = db.Column(db.BigInteger, nullable=True)
    last_replay_run_id = db.Column(db.Integer, nullable=True)
    last_replayed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ReadModelRun(db.Model):
    __tablename__ = "readmodel_run"
    __table_args__ = (
        db.Index("ix_readmodel_run_model", "model_name", "model_version"),
        db.Index("ix_readmodel_run_started_at", "started_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(128), nullable=False)
    model_version = db.Column(db.String(32), nullable=False, default="v1")
    status = db.Column(db.String(32), nullable=False, default="pending")
    event_start_id = db.Column(db.BigInteger, nullable=True)
    event_end_id = db.Column(db.BigInteger, nullable=True)
    replay_scope = db.Column(db.JSON, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
