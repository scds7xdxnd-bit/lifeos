"""Add inferred record columns to domain tables for Calendar-First architecture.

This migration adds the following columns to domain tables that support 
calendar-inferred records:
- source: 'manual', 'calendar', 'import', 'api' (default: 'manual')
- calendar_event_id: FK to calendar_event (nullable)
- confidence_score: 0.0-1.0 classification confidence (nullable)
- inference_status: 'inferred', 'confirmed', 'rejected' (nullable)

Tables affected:
- finance_transaction
- health_workout
- health_nutrition_log
- skill_practice_session
- project_task_log
- relationships_interaction

Revision ID: 20251207_domains_inferred_columns
Revises: 20251206_calendar_initial
Create Date: 2025-12-07 12:00:00.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251207_domains_inferred_columns"
down_revision = "20251206_calendar_initial"
branch_labels = None
depends_on = None


def _get_inspector():
    """Get database inspector for checking existing schema."""
    conn = op.get_bind()
    return inspect(conn)


def _has_column(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = _get_inspector()
    try:
        columns = [c["name"] for c in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False


def _has_table(table_name: str) -> bool:
    """Check if a table exists."""
    inspector = _get_inspector()
    return table_name in inspector.get_table_names()


def _has_index(table_name: str, index_name: str) -> bool:
    """Check if an index exists on a table."""
    inspector = _get_inspector()
    try:
        indexes = inspector.get_indexes(table_name)
        return any(idx["name"] == index_name for idx in indexes)
    except Exception:
        return False


def _add_inferred_columns(table_name: str) -> None:
    """Add standard inferred record columns to a table."""
    
    # Add source column
    if not _has_column(table_name, "source"):
        op.add_column(
            table_name,
            sa.Column("source", sa.String(32), nullable=False, server_default="manual")
        )
    
    # Add calendar_event_id column (FK)
    # Note: SQLite doesn't support adding FK constraints after table creation
    if not _has_column(table_name, "calendar_event_id"):
        op.add_column(
            table_name,
            sa.Column("calendar_event_id", sa.Integer(), nullable=True)
        )
    
    # Add confidence_score column
    if not _has_column(table_name, "confidence_score"):
        op.add_column(
            table_name,
            sa.Column("confidence_score", sa.Float(), nullable=True)
        )
    
    # Add inference_status column
    if not _has_column(table_name, "inference_status"):
        op.add_column(
            table_name,
            sa.Column("inference_status", sa.String(16), nullable=True)
        )


def _create_inference_index(table_name: str) -> None:
    """Create index on (user_id, inference_status) for pending review queries."""
    index_name = f"ix_{table_name}_user_inference_status"
    if not _has_index(table_name, index_name):
        op.create_index(
            index_name,
            table_name,
            ["user_id", "inference_status"]
        )


def upgrade() -> None:
    """Add inferred record columns to all domain tables."""
    
    # List of tables to update with inferred columns
    tables = [
        "finance_transaction",
        "health_workout",
        "health_nutrition_log",
        "skill_practice_session",
        "project_task_log",
        "relationships_interaction",
    ]
    
    for table in tables:
        if _has_table(table):
            _add_inferred_columns(table)
            _create_inference_index(table)


def downgrade() -> None:
    """Remove inferred record columns from domain tables."""
    
    tables = [
        "finance_transaction",
        "health_workout",
        "health_nutrition_log",
        "skill_practice_session",
        "project_task_log",
        "relationships_interaction",
    ]
    
    for table in tables:
        if _has_table(table):
            # Drop index
            index_name = f"ix_{table}_user_inference_status"
            try:
                op.drop_index(index_name, table_name=table)
            except Exception:
                pass
            
            # Drop columns
            for col in ["inference_status", "confidence_score", "calendar_event_id", "source"]:
                try:
                    op.drop_column(table, col)
                except Exception:
                    pass
