"""Bootstrap readmodel metadata tables and isolation for replay.

Revision ID: 20251220_readmodels_bootstrap
Revises: 0c76fa610e14
Create Date: 2025-12-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251220_readmodels_bootstrap"
down_revision = "0c76fa610e14"
branch_labels = None
depends_on = None

# TWO_PHASE to keep alignment with prior cross-domain hardening
TWO_PHASE = True


def upgrade():
    op.create_table(
        "readmodel_state",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False, server_default="v1"),
        sa.Column("domain", sa.String(length=64), nullable=False),
        sa.Column("model_type", sa.String(length=32), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("replay_start_version", sa.String(length=64), nullable=True),
        sa.Column("rebuild_strategy", sa.String(length=255), nullable=True),
        sa.Column("consumed_events", sa.JSON(), nullable=True),
        sa.Column("last_replayed_event_id", sa.BigInteger(), nullable=True),
        sa.Column("last_replay_run_id", sa.Integer(), nullable=True),
        sa.Column("last_replayed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint("model_name", "model_version", name="uq_readmodel_state_model_version"),
    )
    op.create_index("ix_readmodel_state_domain", "readmodel_state", ["domain"])
    op.create_index(
        "ix_readmodel_state_last_replayed_event",
        "readmodel_state",
        ["last_replayed_event_id"],
    )

    op.create_table(
        "readmodel_run",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("model_version", sa.String(length=32), nullable=False, server_default="v1"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("event_start_id", sa.BigInteger(), nullable=True),
        sa.Column("event_end_id", sa.BigInteger(), nullable=True),
        sa.Column("replay_scope", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_readmodel_run_model",
        "readmodel_run",
        ["model_name", "model_version"],
    )
    op.create_index("ix_readmodel_run_started_at", "readmodel_run", ["started_at"])


def downgrade():
    op.drop_index("ix_readmodel_run_started_at", table_name="readmodel_run")
    op.drop_index("ix_readmodel_run_model", table_name="readmodel_run")
    op.drop_table("readmodel_run")

    op.drop_index("ix_readmodel_state_last_replayed_event", table_name="readmodel_state")
    op.drop_index("ix_readmodel_state_domain", table_name="readmodel_state")
    op.drop_table("readmodel_state")
