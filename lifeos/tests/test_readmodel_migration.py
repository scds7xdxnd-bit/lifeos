"""Schema guardrails for the readmodel bootstrap migration."""

from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from lifeos.extensions import db


def test_readmodel_tables_and_constraints_exist(app):
    """Migration should create readmodel tables with the uniqueness guardrail."""
    inspector = sa.inspect(db.engine)
    tables = set(inspector.get_table_names())
    assert "readmodel_state" in tables
    assert "readmodel_run" in tables

    constraints = {c["name"] for c in inspector.get_unique_constraints("readmodel_state")}
    assert "uq_readmodel_state_model_version" in constraints


def test_readmodel_state_enforces_model_version_uniqueness(app):
    """
    The idempotency metadata must be unique per model/version to guarantee deterministic replay.
    """
    insert_stmt = sa.text(
        """
        INSERT INTO readmodel_state
            (model_name, model_version, domain, model_type, idempotency_key, consumed_events)
        VALUES
            (:model_name, :model_version, :domain, :model_type, :idempotency_key, :consumed_events)
        """
    )
    params = {
        "model_name": "finance.trial_balance_projection",
        "model_version": "v1",
        "domain": "finance",
        "model_type": "aggregate",
        "idempotency_key": "entry_id",
        "consumed_events": "[]",
    }

    with db.session.begin_nested():
        db.session.execute(insert_stmt, params)
        db.session.flush()
        with pytest.raises(IntegrityError):
            db.session.execute(insert_stmt, params)
            db.session.flush()


def test_readmodel_run_defaults_pending_status(app):
    """Replay runs should default to pending when inserted without explicit status."""
    insert_stmt = sa.text(
        """
        INSERT INTO readmodel_run (model_name, model_version)
        VALUES (:model_name, :model_version)
        """
    )
    with db.session.begin_nested():
        db.session.execute(insert_stmt, {"model_name": "insights.feed_projection", "model_version": "v1"})
        db.session.flush()
        row = db.session.execute(
            sa.text(
                """
                SELECT status FROM readmodel_run
                WHERE model_name = :model_name AND model_version = :model_version
                """
            ),
            {"model_name": "insights.feed_projection", "model_version": "v1"},
        ).one()
        assert row.status == "pending"
