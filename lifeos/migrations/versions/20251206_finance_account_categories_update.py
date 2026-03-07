"""Finance: expand AccountCategory model with user scoping, defaults, and system flags.

Adds columns to finance_account_category:
- user_id: nullable FK for user-scoped categories (NULL = system category)
- slug: normalized name for uniqueness constraint
- base_type: asset/liability/equity/income/expense
- is_default: marks default category per user+base_type
- is_system: distinguishes system-provided from user-created categories
- created_at, updated_at: timestamps

Adds indexes:
- ix_finance_account_category_user_base_default (user_id, base_type, is_default)
- ix_finance_account_category_user_base_name (user_id, base_type, name)
- uq_finance_account_category_user_base_slug (unique constraint)

Adds index on finance_account:
- ix_finance_account_user_category (user_id, category_id)

Revision ID: 20251206_finance_account_categories_update
Revises: 20251218_backend_updates_validation
Create Date: 2025-12-06 17:00:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251206_finance_account_categories_update"
down_revision = "20251218_backend_updates_validation"
branch_labels = None
depends_on = None

# Mark as two-phase migration due to op.execute usage for backfills
TWO_PHASE = True


def _get_inspector():
    """Get database inspector for checking existing schema."""
    conn = op.get_bind()
    return inspect(conn)


def _has_column(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = _get_inspector()
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def _has_index(table_name: str, index_name: str) -> bool:
    """Check if an index exists on a table."""
    inspector = _get_inspector()
    indexes = inspector.get_indexes(table_name)
    return any(idx["name"] == index_name for idx in indexes)


def upgrade() -> None:
    """Add new columns and indexes to finance_account_category.

    SQLite doesn't support ALTER COLUMN, so we add columns as nullable
    with defaults, then backfill data. The model handles NOT NULL at
    application level.
    """

    # =========================================================================
    # 1. Add new columns to finance_account_category
    # =========================================================================

    # Add user_id column (nullable for system categories)
    if not _has_column("finance_account_category", "user_id"):
        op.add_column(
            "finance_account_category",
            sa.Column("user_id", sa.Integer(), nullable=True),
        )
        if not _has_index("finance_account_category", "ix_finance_account_category_user_id"):
            op.create_index(
                "ix_finance_account_category_user_id",
                "finance_account_category",
                ["user_id"],
            )

    # Add slug column (nullable initially, backfill, keep nullable for SQLite)
    if not _has_column("finance_account_category", "slug"):
        op.add_column(
            "finance_account_category",
            sa.Column("slug", sa.String(128), nullable=False, server_default=""),
        )
        # Backfill slug from name (lowercase, replace spaces with underscores)
        op.execute(
            """
            UPDATE finance_account_category
            SET slug = LOWER(REPLACE(REPLACE(TRIM(name), ' ', '_'), '-', '_'))
            WHERE slug = '';
        """
        )

    # Add base_type column
    if not _has_column("finance_account_category", "base_type"):
        op.add_column(
            "finance_account_category",
            sa.Column("base_type", sa.String(16), nullable=False, server_default="asset"),
        )
        # Backfill base_type - infer from normal_balance or default to 'asset'
        op.execute(
            """
            UPDATE finance_account_category
            SET base_type = CASE
                WHEN normal_balance = 'credit' THEN 'liability'
                ELSE 'asset'
            END
            WHERE base_type = 'asset';
        """
        )

    # Add is_default column
    if not _has_column("finance_account_category", "is_default"):
        op.add_column(
            "finance_account_category",
            sa.Column(
                "is_default",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("FALSE"),
            ),
        )

    # Add is_system column
    if not _has_column("finance_account_category", "is_system"):
        op.add_column(
            "finance_account_category",
            sa.Column(
                "is_system",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("TRUE"),
            ),
        )
        # Mark existing categories as system categories
        op.execute("UPDATE finance_account_category SET is_system = TRUE WHERE user_id IS NULL;")

    # Add created_at column
    if not _has_column("finance_account_category", "created_at"):
        op.add_column(
            "finance_account_category",
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )
        # Backfill with current timestamp (SQLite vs Postgres)
        bind = op.get_bind()
        if bind.dialect.name == "sqlite":
            op.execute("UPDATE finance_account_category SET created_at = datetime('now') WHERE created_at IS NULL;")
        else:
            op.execute("UPDATE finance_account_category SET created_at = now() WHERE created_at IS NULL;")

    # Add updated_at column
    if not _has_column("finance_account_category", "updated_at"):
        op.add_column(
            "finance_account_category",
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        # Backfill with current timestamp (SQLite vs Postgres)
        bind = op.get_bind()
        if bind.dialect.name == "sqlite":
            op.execute("UPDATE finance_account_category SET updated_at = datetime('now') WHERE updated_at IS NULL;")
        else:
            op.execute("UPDATE finance_account_category SET updated_at = now() WHERE updated_at IS NULL;")

    # =========================================================================
    # 2. Create indexes on finance_account_category
    # =========================================================================

    if not _has_index("finance_account_category", "ix_finance_account_category_user_base_default"):
        op.create_index(
            "ix_finance_account_category_user_base_default",
            "finance_account_category",
            ["user_id", "base_type", "is_default"],
        )

    if not _has_index("finance_account_category", "ix_finance_account_category_user_base_name"):
        op.create_index(
            "ix_finance_account_category_user_base_name",
            "finance_account_category",
            ["user_id", "base_type", "name"],
        )

    # =========================================================================
    # 3. Create unique constraint (SQLite workaround: create unique index)
    # =========================================================================

    # SQLite doesn't support adding constraints after table creation
    # Use a unique index instead
    if not _has_index("finance_account_category", "uq_finance_account_category_user_base_slug"):
        op.create_index(
            "uq_finance_account_category_user_base_slug",
            "finance_account_category",
            ["user_id", "base_type", "slug"],
            unique=True,
        )

    # =========================================================================
    # 4. Add index on finance_account for category lookup
    # =========================================================================

    if not _has_index("finance_account", "ix_finance_account_user_category"):
        op.create_index(
            "ix_finance_account_user_category",
            "finance_account",
            ["user_id", "category_id"],
        )


def downgrade() -> None:
    """Remove added columns and indexes (for rollback)."""

    # Drop indexes (with existence checks for safety)
    try:
        op.drop_index("ix_finance_account_user_category", table_name="finance_account")
    except Exception:
        pass
    try:
        op.drop_index(
            "uq_finance_account_category_user_base_slug",
            table_name="finance_account_category",
        )
    except Exception:
        pass
    try:
        op.drop_index(
            "ix_finance_account_category_user_base_name",
            table_name="finance_account_category",
        )
    except Exception:
        pass
    try:
        op.drop_index(
            "ix_finance_account_category_user_base_default",
            table_name="finance_account_category",
        )
    except Exception:
        pass
    try:
        op.drop_index("ix_finance_account_category_user_id", table_name="finance_account_category")
    except Exception:
        pass

    # Drop columns
    try:
        op.drop_column("finance_account_category", "updated_at")
    except Exception:
        pass
    try:
        op.drop_column("finance_account_category", "created_at")
    except Exception:
        pass
    try:
        op.drop_column("finance_account_category", "is_system")
    except Exception:
        pass
    try:
        op.drop_column("finance_account_category", "is_default")
    except Exception:
        pass
    try:
        op.drop_column("finance_account_category", "base_type")
    except Exception:
        pass
    try:
        op.drop_column("finance_account_category", "slug")
    except Exception:
        pass
    try:
        op.drop_column("finance_account_category", "user_id")
    except Exception:
        pass
