"""Add exchange rate infrastructure and currency fields to finance domain.

Adds:
  - finance_exchange_rate table (user-scoped manual FX rates)
  - default_currency on finance_account
  - exchange_rate_to_base on finance_transaction + finance_journal_line

Revision ID: 20260329_finance_exchange_rates
Revises: 20260329_finance_currency_infrastructure
Create Date: 2026-03-29
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260329_finance_exchange_rates"
down_revision = "20260329_finance_currency_infrastructure"
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------
    # 1. Create finance_exchange_rate table
    #    Rates are user-scoped for manual entry (Phase 2).
    #    API-synced rates land in a future migration.
    # ------------------------------------------------------------------
    op.create_table(
        "finance_exchange_rate",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("from_currency", sa.String(3), sa.ForeignKey("finance_currency.code"), nullable=False),
        sa.Column("to_currency", sa.String(3), sa.ForeignKey("finance_currency.code"), nullable=False),
        sa.Column("rate", sa.Numeric(19, 10), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index(
        "ix_finance_exchange_rate_user_from_to_date",
        "finance_exchange_rate",
        ["user_id", "from_currency", "to_currency", "effective_date"],
    )

    # ------------------------------------------------------------------
    # 2. Add default_currency to finance_account
    #    NULL = user's base currency (resolved at read time).
    # ------------------------------------------------------------------
    op.add_column(
        "finance_account",
        sa.Column("default_currency", sa.String(3), nullable=True),
    )

    # ------------------------------------------------------------------
    # 3. Add exchange_rate_to_base to finance_transaction
    #    Locked at transaction creation time. 1.0 = same-as-base.
    # ------------------------------------------------------------------
    op.add_column(
        "finance_transaction",
        sa.Column(
            "exchange_rate_to_base",
            sa.Numeric(19, 10),
            nullable=True,
            server_default="1.0",
        ),
    )

    # ------------------------------------------------------------------
    # 4. Add exchange_rate_to_base to finance_journal_line
    # ------------------------------------------------------------------
    op.add_column(
        "finance_journal_line",
        sa.Column(
            "exchange_rate_to_base",
            sa.Numeric(19, 10),
            nullable=True,
            server_default="1.0",
        ),
    )


def downgrade():
    op.drop_column("finance_journal_line", "exchange_rate_to_base")
    op.drop_column("finance_transaction", "exchange_rate_to_base")
    op.drop_column("finance_account", "default_currency")
    op.drop_index("ix_finance_exchange_rate_user_from_to_date", table_name="finance_exchange_rate")
    op.drop_table("finance_exchange_rate")
