"""Private alpha inquiry feedback linkage.

Revision ID: 20260314_private_alpha_feedback_linkage
Revises: 20260314_private_alpha_invites
Create Date: 2026-03-14
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260314_private_alpha_feedback_linkage"
down_revision = "20260314_private_alpha_invites"
branch_labels = None
depends_on = None
TWO_PHASE = True


def upgrade():
    with op.batch_alter_table("user_feedback_event") as batch_op:
        batch_op.add_column(sa.Column("inquiry_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("inquiry_version_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_user_feedback_event_inquiry_id",
            "inquiry_request",
            ["inquiry_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            "fk_user_feedback_event_inquiry_version_id",
            "inquiry_brief_version",
            ["inquiry_version_id"],
            ["id"],
        )
    op.create_index(
        "ix_user_feedback_user_inquiry_created",
        "user_feedback_event",
        ["user_id", "inquiry_id", "created_at"],
    )
    op.create_index(
        "ix_user_feedback_user_inquiry_version_created",
        "user_feedback_event",
        ["user_id", "inquiry_version_id", "created_at"],
    )


def downgrade():
    op.drop_index("ix_user_feedback_user_inquiry_version_created", table_name="user_feedback_event")
    op.drop_index("ix_user_feedback_user_inquiry_created", table_name="user_feedback_event")
    with op.batch_alter_table("user_feedback_event") as batch_op:
        batch_op.drop_constraint("fk_user_feedback_event_inquiry_version_id", type_="foreignkey")
        batch_op.drop_constraint("fk_user_feedback_event_inquiry_id", type_="foreignkey")
        batch_op.drop_column("inquiry_version_id")
        batch_op.drop_column("inquiry_id")
