"""Finance: add account type classification (account_type, account_subtype, normalized_name, created_at).

Revision ID: 20251206_finance_account_type_classification
Revises: 20251206_core_password_reset_token
Create Date: 2025-12-06 10:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251206_finance_account_type_classification"
down_revision = "20251206_core_password_reset_token"
branch_labels = None
depends_on = None

# Mark as two-phase so architecture test allows explicit executes used for backfill
TWO_PHASE = True


def upgrade() -> None:
    # Add new columns to finance_account table
    op.add_column(
        "finance_account",
        sa.Column("account_type", sa.String(16), nullable=False, server_default="asset"),
    )
    op.add_column("finance_account", sa.Column("account_subtype", sa.String(64), nullable=True))
    op.add_column(
        "finance_account",
        sa.Column("normalized_name", sa.String(255), nullable=False, server_default=""),
    )
    op.add_column(
        "finance_account",
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for new columns
    op.create_index("ix_finance_account_type", "finance_account", ["account_type"])
    op.create_index("ix_finance_account_user_type", "finance_account", ["user_id", "account_type"])
    op.create_index("ix_finance_account_normalized_name", "finance_account", ["normalized_name"])
    op.create_index(
        "ix_finance_account_user_normalized_name",
        "finance_account",
        ["user_id", "normalized_name"],
    )

    # Backfill existing data: normalize account names and set default account_type
    # First, normalize the names from existing accounts
    op.execute(
        """
        UPDATE finance_account
        SET normalized_name = LOWER(TRIM(name))
        WHERE normalized_name = '';
    """
    )

    # Map category_id to account_type if category exists; otherwise default to 'asset'
    op.execute(
        """
        UPDATE finance_account
        SET account_type = COALESCE(
            CASE
                WHEN category_id IN (
                    SELECT id FROM finance_account_category WHERE code IN ('ASSET', 'Assets')
                )
                THEN 'asset'
                WHEN category_id IN (
                    SELECT id FROM finance_account_category WHERE code IN ('LIABILITY', 'Liabilities')
                )
                THEN 'liability'
                WHEN category_id IN (
                    SELECT id FROM finance_account_category WHERE code IN ('EQUITY', 'Equity')
                )
                THEN 'equity'
                WHEN category_id IN (
                    SELECT id FROM finance_account_category WHERE code IN ('INCOME', 'Income')
                )
                THEN 'income'
                WHEN category_id IN (
                    SELECT id FROM finance_account_category WHERE code IN ('EXPENSE', 'Expenses')
                )
                THEN 'expense'
                ELSE 'asset'
            END,
            'asset'
        )
        WHERE account_type = 'asset';
    """
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_finance_account_user_normalized_name", table_name="finance_account")
    op.drop_index("ix_finance_account_normalized_name", table_name="finance_account")
    op.drop_index("ix_finance_account_user_type", table_name="finance_account")
    op.drop_index("ix_finance_account_type", table_name="finance_account")

    # Drop columns
    op.drop_column("finance_account", "created_at")
    op.drop_column("finance_account", "normalized_name")
    op.drop_column("finance_account", "account_subtype")
    op.drop_column("finance_account", "account_type")
