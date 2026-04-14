"""Add currency infrastructure to finance domain.

Creates finance_currency reference table and adds currency_code to all monetary
columns across finance tables. Also adds void/edit audit fields to Transaction.

Revision ID: 20260329_finance_currency_infrastructure
Revises: 20260328_health_calorie_report
Create Date: 2026-03-29
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260329_finance_currency_infrastructure"
down_revision = "20260328_health_calorie_report"
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------
    # 1. Create finance_currency reference table
    # ------------------------------------------------------------------
    op.create_table(
        "finance_currency",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(3), nullable=False, unique=True),
        sa.Column("symbol", sa.String(8), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("decimal_places", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("is_base", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_finance_currency_code", "finance_currency", ["code"])
    op.create_index("ix_finance_currency_is_base", "finance_currency", ["is_base"])

    # ------------------------------------------------------------------
    # 2. Seed common currencies (idempotent: ignored if already present)
    # ------------------------------------------------------------------
    currency_table = sa.table(
        "finance_currency",
        sa.column("code", sa.String(3)),
        sa.column("symbol", sa.String(8)),
        sa.column("name", sa.String(64)),
        sa.column("decimal_places", sa.Integer()),
        sa.column("is_base", sa.Boolean()),
    )
    op.bulk_insert(
        currency_table,
        [
            {"code": "USD", "symbol": "$", "name": "US Dollar", "decimal_places": 2, "is_base": False},
            {"code": "KRW", "symbol": "KRW", "name": "Korean Won", "decimal_places": 0, "is_base": False},
            {"code": "EUR", "symbol": "EUR", "name": "Euro", "decimal_places": 2, "is_base": False},
            {"code": "GBP", "symbol": "GBP", "name": "British Pound", "decimal_places": 2, "is_base": False},
            {"code": "JPY", "symbol": "JPY", "name": "Japanese Yen", "decimal_places": 0, "is_base": False},
            {"code": "CNY", "symbol": "CNY", "name": "Chinese Yuan", "decimal_places": 2, "is_base": False},
            {"code": "SGD", "symbol": "SGD", "name": "Singapore Dollar", "decimal_places": 2, "is_base": False},
            {"code": "AUD", "symbol": "AUD", "name": "Australian Dollar", "decimal_places": 2, "is_base": False},
            {"code": "CAD", "symbol": "CAD", "name": "Canadian Dollar", "decimal_places": 2, "is_base": False},
            {"code": "CHF", "symbol": "CHF", "name": "Swiss Franc", "decimal_places": 2, "is_base": False},
        ],
    )

    # ------------------------------------------------------------------
    # 3. Add currency_code to finance_journal_line
    # ------------------------------------------------------------------
    op.add_column(
        "finance_journal_line",
        sa.Column("currency_code", sa.String(3), nullable=True),
    )

    # ------------------------------------------------------------------
    # 4. Add currency_code to finance_transaction
    #    + void audit fields
    # ------------------------------------------------------------------
    op.add_column(
        "finance_transaction",
        sa.Column("currency_code", sa.String(3), nullable=True),
    )
    op.add_column(
        "finance_transaction",
        sa.Column("is_void", sa.Boolean(), nullable=False, server_default="0"),
    )
    op.add_column(
        "finance_transaction",
        sa.Column("void_of_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "finance_transaction",
        sa.Column("edited_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_finance_transaction_is_void", "finance_transaction", ["is_void"])

    # ------------------------------------------------------------------
    # 5. Add currency_code to finance_money_schedule_row
    # ------------------------------------------------------------------
    op.add_column(
        "finance_money_schedule_row",
        sa.Column("currency_code", sa.String(3), nullable=True),
    )

    # ------------------------------------------------------------------
    # 6. Add currency_code to finance_money_schedule_daily_balance
    # ------------------------------------------------------------------
    op.add_column(
        "finance_money_schedule_daily_balance",
        sa.Column("currency_code", sa.String(3), nullable=True),
    )

    # ------------------------------------------------------------------
    # 7. Add currency_code to finance_money_schedule_scenario_row
    # ------------------------------------------------------------------
    op.add_column(
        "finance_money_schedule_scenario_row",
        sa.Column("currency_code", sa.String(3), nullable=True),
    )

    # ------------------------------------------------------------------
    # 8. Add currency_code to finance_receivable_tracker
    # ------------------------------------------------------------------
    op.add_column(
        "finance_receivable_tracker",
        sa.Column("currency_code", sa.String(3), nullable=True),
    )

    # ------------------------------------------------------------------
    # 9. Add currency_code to finance_receivable_manual_entry
    # ------------------------------------------------------------------
    op.add_column(
        "finance_receivable_manual_entry",
        sa.Column("currency_code", sa.String(3), nullable=True),
    )


def downgrade():
    op.drop_column("finance_receivable_manual_entry", "currency_code")
    op.drop_column("finance_receivable_tracker", "currency_code")
    op.drop_column("finance_money_schedule_scenario_row", "currency_code")
    op.drop_column("finance_money_schedule_daily_balance", "currency_code")
    op.drop_column("finance_money_schedule_row", "currency_code")
    op.drop_index("ix_finance_transaction_is_void", table_name="finance_transaction")
    op.drop_column("finance_transaction", "edited_at")
    op.drop_column("finance_transaction", "void_of_id")
    op.drop_column("finance_transaction", "is_void")
    op.drop_column("finance_transaction", "currency_code")
    op.drop_column("finance_journal_line", "currency_code")
    op.drop_index("ix_finance_currency_is_base", table_name="finance_currency")
    op.drop_index("ix_finance_currency_code", table_name="finance_currency")
    op.drop_table("finance_currency")
