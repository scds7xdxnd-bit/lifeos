"""Add calendar domain tables.

Revision ID: 20251206_calendar_initial
Revises: 20251206_finance_account_categories_update
Create Date: 2025-12-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251206_calendar_initial"
down_revision: Union[str, None] = "20251206_finance_account_categories_update"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create calendar_event and calendar_event_interpretation tables."""
    # Calendar Event table
    op.create_table(
        "calendar_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column(
            "all_day", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False
        ),
        sa.Column("location", sa.String(length=512), nullable=True),
        sa.Column(
            "source",
            sa.String(length=32),
            server_default="manual",
            nullable=False,
            comment="manual, sync_google, sync_apple, api",
        ),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("recurrence_rule", sa.String(length=255), nullable=True),
        sa.Column("color", sa.String(length=16), nullable=True),
        sa.Column(
            "is_private", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False
        ),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_calendar_event_user_start",
        "calendar_event",
        ["user_id", "start_time"],
    )
    op.create_index(
        "ix_calendar_event_user_end",
        "calendar_event",
        ["user_id", "end_time"],
    )
    op.create_index(
        "ix_calendar_event_user_source",
        "calendar_event",
        ["user_id", "source"],
    )
    op.create_index(
        "ux_calendar_event_user_external",
        "calendar_event",
        ["user_id", "external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )

    # Calendar Event Interpretation table
    op.create_table(
        "calendar_event_interpretation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("calendar_event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "domain",
            sa.String(length=50),
            nullable=False,
            comment="Target domain: finance, health, habits, skills, projects, relationships",
        ),
        sa.Column(
            "record_type",
            sa.String(length=50),
            nullable=False,
            comment="Record type within domain: transaction, workout, meal, etc.",
        ),
        sa.Column(
            "confidence_score",
            sa.Float(),
            nullable=False,
            comment="ML/rule confidence 0.0-1.0",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="inferred",
            comment="inferred, confirmed, rejected",
        ),
        sa.Column(
            "classification_data",
            sa.JSON(),
            nullable=True,
            comment="Extracted fields from classification",
        ),
        sa.Column(
            "record_id",
            sa.Integer(),
            nullable=True,
            comment="ID of created record in target domain (if created)",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["calendar_event_id"], ["calendar_event.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_interpretation_user_status",
        "calendar_event_interpretation",
        ["user_id", "status"],
    )
    op.create_index(
        "ix_interpretation_user_domain",
        "calendar_event_interpretation",
        ["user_id", "domain", "status"],
    )
    op.create_index(
        "ix_interpretation_event",
        "calendar_event_interpretation",
        ["calendar_event_id"],
    )


def downgrade() -> None:
    """Drop calendar tables."""
    op.drop_index("ix_interpretation_event", table_name="calendar_event_interpretation")
    op.drop_index(
        "ix_interpretation_user_domain", table_name="calendar_event_interpretation"
    )
    op.drop_index(
        "ix_interpretation_user_status", table_name="calendar_event_interpretation"
    )
    op.drop_table("calendar_event_interpretation")

    op.drop_index("ux_calendar_event_user_external", table_name="calendar_event")
    op.drop_index("ix_calendar_event_user_source", table_name="calendar_event")
    op.drop_index("ix_calendar_event_user_end", table_name="calendar_event")
    op.drop_index("ix_calendar_event_user_start", table_name="calendar_event")
    op.drop_table("calendar_event")
