"""Drop legacy habits/relationships tables."""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251216_drop_legacy_habits_relationships"
down_revision = "20251215_projects_init"
branch_labels = None
depends_on = None
TWO_PHASE = True


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = set(inspector.get_table_names())

    for tbl in (
        "habit",
        "habit_log",
        "relationship_contact",
        "relationship_interaction",
    ):
        if tbl in existing_tables:
            op.drop_table(tbl)


def downgrade():
    # No-op: legacy tables intentionally removed.
    pass
