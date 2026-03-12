"""add skills tables

Revision ID: 20251205_skills_initial_schema
Revises: 20251206_core_password_reset_token
Create Date: 2025-12-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251205_skills_initial_schema"
down_revision = "20251206_core_password_reset_token"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "skills_skill",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=128)),
        sa.Column("difficulty", sa.String(length=32)),
        sa.Column("target_level", sa.Integer()),
        sa.Column("current_level", sa.Integer()),
        sa.Column("description", sa.Text()),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index(
        "ux_skills_skill_user_name", "skills_skill", ["user_id", "name"], unique=True
    )
    op.create_index(
        "ix_skills_skill_user_category", "skills_skill", ["user_id", "category"]
    )

    op.create_table(
        "skills_skill_practice_session",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "skill_id",
            sa.Integer(),
            sa.ForeignKey("skills_skill.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("intensity", sa.Integer()),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "practiced_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_skills_session_user_practiced_at",
        "skills_skill_practice_session",
        ["user_id", "practiced_at"],
    )
    op.create_index(
        "ix_skills_session_skill_practiced_at",
        "skills_skill_practice_session",
        ["skill_id", "practiced_at"],
    )


def downgrade():
    op.drop_index(
        "ix_skills_session_skill_practiced_at",
        table_name="skills_skill_practice_session",
    )
    op.drop_index(
        "ix_skills_session_user_practiced_at",
        table_name="skills_skill_practice_session",
    )
    op.drop_table("skills_skill_practice_session")
    op.drop_index("ix_skills_skill_user_category", table_name="skills_skill")
    op.drop_index("ux_skills_skill_user_name", table_name="skills_skill")
    op.drop_table("skills_skill")
