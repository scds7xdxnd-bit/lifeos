"""Phase 5a insight substrate tables.

Revision ID: 20251226_phase5a_insight_substrate_tables
Revises: 20251224_insight_feed_indexes
Create Date: 2025-12-26
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251226_phase5a_insight_substrate_tables"
down_revision = "20251224_insight_feed_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "timeline_event",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=True, index=True),
        sa.Column("timestamp_start", sa.DateTime(), nullable=False),
        sa.Column("timestamp_end", sa.DateTime(), nullable=True),
        sa.Column("source_domain", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("source_object_ref", sa.String(length=128), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("ingested_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("user_id", "event_id", name="uq_timeline_event_user_event"),
    )
    op.create_index("ix_timeline_event_user_start", "timeline_event", ["user_id", "timestamp_start"])
    op.create_index(
        "ix_timeline_event_user_domain_start",
        "timeline_event",
        ["user_id", "source_domain", "timestamp_start"],
    )
    op.create_index(
        "ix_timeline_event_user_type_start",
        "timeline_event",
        ["user_id", "event_type", "timestamp_start"],
    )

    op.create_table(
        "interpretation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=True, index=True),
        sa.Column("interpretation_type", sa.String(length=128), nullable=False),
        sa.Column("input_event_ids", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("proposed_writes", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("applied_writes", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="proposed"),
        sa.Column("reversible_plan", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("fingerprint", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("decided_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "fingerprint", name="uq_interpretation_user_fingerprint"),
    )
    op.create_index(
        "ix_interpretation_user_status_created",
        "interpretation",
        ["user_id", "status", "created_at"],
    )

    op.create_table(
        "user_feedback_event",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=True, index=True),
        sa.Column("interpretation_id", sa.Integer(), sa.ForeignKey("interpretation.id"), nullable=True, index=True),
        sa.Column("feedback_type", sa.String(length=32), nullable=False),
        sa.Column("fingerprint", sa.String(length=128), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_user_feedback_user_created", "user_feedback_event", ["user_id", "created_at"])
    op.create_index("ix_user_feedback_user_type", "user_feedback_event", ["user_id", "feedback_type"])
    op.create_index("ix_user_feedback_user_fingerprint", "user_feedback_event", ["user_id", "fingerprint"])


def downgrade():
    op.drop_index("ix_user_feedback_user_fingerprint", table_name="user_feedback_event")
    op.drop_index("ix_user_feedback_user_type", table_name="user_feedback_event")
    op.drop_index("ix_user_feedback_user_created", table_name="user_feedback_event")
    op.drop_table("user_feedback_event")

    op.drop_index("ix_interpretation_user_status_created", table_name="interpretation")
    op.drop_table("interpretation")

    op.drop_index("ix_timeline_event_user_type_start", table_name="timeline_event")
    op.drop_index("ix_timeline_event_user_domain_start", table_name="timeline_event")
    op.drop_index("ix_timeline_event_user_start", table_name="timeline_event")
    op.drop_table("timeline_event")
