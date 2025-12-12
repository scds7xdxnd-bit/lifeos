"""Projects domain initial schema (additive-safe)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251215_projects_init"
down_revision = "20251214_health_null_legacy_values"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    def _has_table(name: str) -> bool:
        return name in inspector.get_table_names()

    def _has_column(table: str, name: str) -> bool:
        return name in {col["name"] for col in inspector.get_columns(table)}

    def _has_index(table: str, name: str) -> bool:
        return any(ix["name"] == name for ix in inspector.get_indexes(table))

    # project table
    if not _has_table("project"):
        op.create_table(
            "project",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "status", sa.String(length=32), nullable=False, server_default="active"
            ),
            sa.Column("target_date", sa.Date(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    else:
        if not _has_column("project", "description"):
            op.add_column("project", sa.Column("description", sa.Text(), nullable=True))
        if not _has_column("project", "target_date"):
            op.add_column("project", sa.Column("target_date", sa.Date(), nullable=True))
        if not _has_column("project", "updated_at"):
            op.add_column(
                "project",
                sa.Column(
                    "updated_at",
                    sa.DateTime(),
                    nullable=True,
                    server_default=sa.func.now(),
                ),
            )
    if not _has_index("project", "ix_project_user_name"):
        op.create_index("ix_project_user_name", "project", ["user_id", "name"])
    if not _has_index("project", "ix_project_user_status"):
        op.create_index("ix_project_user_status", "project", ["user_id", "status"])
    if not _has_index("project", "ix_project_user_target_date"):
        op.create_index(
            "ix_project_user_target_date", "project", ["user_id", "target_date"]
        )

    # project_task table
    if not _has_table("project_task"):
        op.create_table(
            "project_task",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "project_id",
                sa.Integer(),
                sa.ForeignKey("project.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column(
                "status", sa.String(length=32), nullable=False, server_default="open"
            ),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.Column("priority", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    else:
        if not _has_column("project_task", "user_id"):
            op.add_column(
                "project_task", sa.Column("user_id", sa.Integer(), nullable=True)
            )
        if not _has_column("project_task", "priority"):
            op.add_column(
                "project_task", sa.Column("priority", sa.Integer(), nullable=True)
            )
        if not _has_column("project_task", "notes"):
            op.add_column("project_task", sa.Column("notes", sa.Text(), nullable=True))
        if not _has_column("project_task", "updated_at"):
            op.add_column(
                "project_task",
                sa.Column(
                    "updated_at",
                    sa.DateTime(),
                    nullable=True,
                    server_default=sa.func.now(),
                ),
            )
    if not _has_index("project_task", "ix_project_task_user_project_status"):
        op.create_index(
            "ix_project_task_user_project_status",
            "project_task",
            ["user_id", "project_id", "status"],
        )
    if not _has_index("project_task", "ix_project_task_user_due_date"):
        op.create_index(
            "ix_project_task_user_due_date", "project_task", ["user_id", "due_date"]
        )
    if not _has_index("project_task", "ix_project_task_user_project_due_date"):
        op.create_index(
            "ix_project_task_user_project_due_date",
            "project_task",
            ["user_id", "project_id", "due_date"],
        )

    # project_task_log table
    if not _has_table("project_task_log"):
        op.create_table(
            "project_task_log",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "task_id",
                sa.Integer(),
                sa.ForeignKey("project_task.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column(
                "logged_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
            sa.Column("status_snapshot", sa.String(length=32), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    else:
        if not _has_column("project_task_log", "user_id"):
            op.add_column(
                "project_task_log", sa.Column("user_id", sa.Integer(), nullable=True)
            )
        if not _has_column("project_task_log", "status_snapshot"):
            op.add_column(
                "project_task_log",
                sa.Column("status_snapshot", sa.String(length=32), nullable=True),
            )
        if not _has_column("project_task_log", "created_at"):
            op.add_column(
                "project_task_log",
                sa.Column(
                    "created_at",
                    sa.DateTime(),
                    nullable=True,
                    server_default=sa.func.now(),
                ),
            )
    if not _has_index("project_task_log", "ix_project_task_log_user_task_logged_at"):
        op.create_index(
            "ix_project_task_log_user_task_logged_at",
            "project_task_log",
            ["user_id", "task_id", "logged_at"],
        )
    if not _has_index("project_task_log", "ix_project_task_log_user_logged_at"):
        op.create_index(
            "ix_project_task_log_user_logged_at",
            "project_task_log",
            ["user_id", "logged_at"],
        )


def downgrade():
    op.drop_index("ix_project_task_log_user_logged_at", table_name="project_task_log")
    op.drop_index(
        "ix_project_task_log_user_task_logged_at", table_name="project_task_log"
    )
    op.drop_table("project_task_log")
    op.drop_index("ix_project_task_user_project_due_date", table_name="project_task")
    op.drop_index("ix_project_task_user_due_date", table_name="project_task")
    op.drop_index("ix_project_task_user_project_status", table_name="project_task")
    op.drop_table("project_task")
    op.drop_index("ix_project_user_target_date", table_name="project")
    op.drop_index("ix_project_user_status", table_name="project")
    op.drop_index("ix_project_user_name", table_name="project")
    op.drop_table("project")
