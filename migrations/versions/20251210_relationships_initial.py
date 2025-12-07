"""add relationships tables

Revision ID: 20251210_relationships_initial
Revises: 20251209_habits_initial
Create Date: 2025-12-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251210_relationships_initial"
down_revision = "20251209_habits_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "relationships_person",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("relationship_type", sa.String(length=64)),
        sa.Column("importance_level", sa.Integer()),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("notes", sa.Text()),
        sa.Column("birthday", sa.Date()),
        sa.Column("first_met_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ux_relationships_person_user_name", "relationships_person", ["user_id", "name"], unique=True)
    op.create_index("ix_relationships_person_user_importance", "relationships_person", ["user_id", "importance_level"])
    op.create_index("ix_relationships_person_user_type", "relationships_person", ["user_id", "relationship_type"])

    op.create_table(
        "relationships_interaction",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("person_id", sa.Integer(), sa.ForeignKey("relationships_person.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column("method", sa.String(length=64)),
        sa.Column("notes", sa.Text()),
        sa.Column("sentiment", sa.String(length=32)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_relationships_interaction_user_date", "relationships_interaction", ["user_id", "date"])
    op.create_index("ix_relationships_interaction_person_date", "relationships_interaction", ["user_id", "person_id", "date"])


def downgrade():
    op.drop_index("ix_relationships_interaction_person_date", table_name="relationships_interaction")
    op.drop_index("ix_relationships_interaction_user_date", table_name="relationships_interaction")
    op.drop_table("relationships_interaction")
    op.drop_index("ix_relationships_person_user_type", table_name="relationships_person")
    op.drop_index("ix_relationships_person_user_importance", table_name="relationships_person")
    op.drop_index("ux_relationships_person_user_name", table_name="relationships_person")
    op.drop_table("relationships_person")
