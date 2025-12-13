"""finance advanced account categories

Revision ID: 20251218_finance_advanced_account_categories
Revises: 20251214_health_null_legacy_values
Create Date: 2025-12-06
"""

from __future__ import annotations

import re
from datetime import datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251218_finance_advanced_account_categories"
down_revision = "20251216_drop_legacy_habits_relationships"
branch_labels = None
depends_on = None
TWO_PHASE = True


BASE_TYPE_MAP = {
    "ASSET": "asset",
    "ASSETS": "asset",
    "LIABILITY": "liability",
    "LIABILITIES": "liability",
    "EQUITY": "equity",
    "INCOME": "income",
    "REVENUE": "income",
    "EXPENSE": "expense",
    "EXPENSES": "expense",
}

BASE_TYPE_NORMAL_BALANCE = {
    "asset": "debit",
    "expense": "debit",
    "liability": "credit",
    "equity": "credit",
    "income": "credit",
}


_slug_pattern = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    value = (value or "").lower().strip()
    value = _slug_pattern.sub("-", value)
    value = value.strip("-")
    return value or "uncategorized"


def upgrade():
    conn = op.get_bind()

    # --- schema changes: account categories ---
    op.add_column(
        "finance_account_category", sa.Column("user_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "finance_account_category",
        sa.Column("slug", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "finance_account_category",
        sa.Column("base_type", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "finance_account_category",
        sa.Column(
            "is_default", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "finance_account_category",
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "finance_account_category",
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
    )
    op.add_column(
        "finance_account_category",
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
    )
    op.create_foreign_key(
        "fk_finance_account_category_user",
        "finance_account_category",
        "user",
        ["user_id"],
        ["id"],
    )

    # --- schema changes: accounts ---
    op.alter_column(
        "finance_account", "category_id", existing_type=sa.Integer(), nullable=True
    )
    op.create_index(
        "ix_finance_account_user_category",
        "finance_account",
        ["user_id", "category_id"],
        unique=False,
    )

    # Normalize account_type and normalized_name where missing
    conn.execute(
        sa.text(
            """
        UPDATE finance_account
        SET account_type = 'asset'
        WHERE account_type IS NULL OR account_type = ''
    """
        )
    )
    conn.execute(
        sa.text(
            """
        UPDATE finance_account
        SET normalized_name = lower(trim(name))
        WHERE normalized_name IS NULL OR normalized_name = ''
    """
        )
    )

    # Backfill category base_type/slug/system defaults
    categories = conn.execute(
        sa.text("SELECT id, code, name, normal_balance FROM finance_account_category")
    ).fetchall()
    for row in categories:
        code = (row.code or "").upper()
        base_type = BASE_TYPE_MAP.get(code) or (
            "liability"
            if (row.normal_balance or "debit").lower() == "credit"
            else "asset"
        )
        slug = _slugify(row.name)
        conn.execute(
            sa.text(
                """
                UPDATE finance_account_category
                SET base_type = :base_type, slug = :slug, is_system = COALESCE(is_system, false), is_default = COALESCE(is_default, false), created_at = COALESCE(created_at, :now), updated_at = COALESCE(updated_at, :now)
                WHERE id = :id
                """
            ),
            {
                "id": row.id,
                "base_type": base_type,
                "slug": slug,
                "now": datetime.utcnow(),
            },
        )

    # Insert system defaults per base_type if missing
    for base_type, normal_balance in BASE_TYPE_NORMAL_BALANCE.items():
        slug = f"{base_type}-default"
        name = f"Default ({base_type.title()})"
        existing = conn.execute(
            sa.text(
                """
                SELECT id FROM finance_account_category
                WHERE user_id IS NULL AND base_type = :base_type AND is_default = true
                LIMIT 1
                """
            ),
            {"base_type": base_type},
        ).fetchone()
        if not existing:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO finance_account_category (user_id, code, name, normal_balance, slug, base_type, is_default, is_system, created_at, updated_at)
                    VALUES (NULL, :code, :name, :normal_balance, :slug, :base_type, true, true, :now, :now)
                    """
                ),
                {
                    "code": f"SYS-{base_type.upper()}",
                    "name": name,
                    "normal_balance": normal_balance,
                    "slug": slug,
                    "base_type": base_type,
                    "now": datetime.utcnow(),
                },
            )

    # Build mapping of system default categories
    defaults = conn.execute(
        sa.text(
            """
            SELECT id, base_type FROM finance_account_category
            WHERE user_id IS NULL AND is_default = true
            """
        )
    ).fetchall()
    default_map = {row.base_type: row.id for row in defaults}

    # Assign all accounts to default category matching base_type
    for base_type, cat_id in default_map.items():
        conn.execute(
            sa.text(
                """
                UPDATE finance_account
                SET category_id = :cat_id
                WHERE account_type = :base_type
                """
            ),
            {"cat_id": cat_id, "base_type": base_type},
        )

    # Ensure base_type and slug are non-null after backfill
    op.alter_column(
        "finance_account_category",
        "base_type",
        existing_type=sa.String(length=16),
        nullable=False,
    )
    op.alter_column(
        "finance_account_category",
        "slug",
        existing_type=sa.String(length=128),
        nullable=False,
    )
    op.alter_column(
        "finance_account_category",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False,
    )
    op.alter_column(
        "finance_account_category",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False,
    )

    # Indexes/uniques
    op.create_unique_constraint(
        "uq_finance_account_category_user_base_slug",
        "finance_account_category",
        ["user_id", "base_type", "slug"],
    )
    op.create_index(
        "ix_finance_account_category_user_base_default",
        "finance_account_category",
        ["user_id", "base_type", "is_default"],
        unique=False,
    )
    op.create_index(
        "ix_finance_account_category_user_base_name",
        "finance_account_category",
        ["user_id", "base_type", "name"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_finance_account_category_user_base_name",
        table_name="finance_account_category",
    )
    op.drop_index(
        "ix_finance_account_category_user_base_default",
        table_name="finance_account_category",
    )
    op.drop_constraint(
        "uq_finance_account_category_user_base_slug",
        "finance_account_category",
        type_="unique",
    )
    op.alter_column("finance_account_category", "updated_at", nullable=True)
    op.alter_column("finance_account_category", "created_at", nullable=True)
    op.alter_column("finance_account_category", "slug", nullable=True)
    op.alter_column("finance_account_category", "base_type", nullable=True)
    op.drop_constraint(
        "fk_finance_account_category_user",
        "finance_account_category",
        type_="foreignkey",
    )
    op.drop_column("finance_account_category", "updated_at")
    op.drop_column("finance_account_category", "created_at")
    op.drop_column("finance_account_category", "is_system")
    op.drop_column("finance_account_category", "is_default")
    op.drop_column("finance_account_category", "base_type")
    op.drop_column("finance_account_category", "slug")
    op.drop_column("finance_account_category", "user_id")

    op.drop_index("ix_finance_account_user_category", table_name="finance_account")
    op.alter_column(
        "finance_account", "category_id", existing_type=sa.Integer(), nullable=False
    )
