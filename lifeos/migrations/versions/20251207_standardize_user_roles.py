"""Backfill standardized domain roles for existing users.

Revision ID: 20251207_standardize_user_roles
Revises: 20251207_domains_inferred_columns
Create Date: 2025-12-07

This migration ensures all existing users have the standard set of domain
write roles that new users receive. Previously only 'user' and 'finance:write'
were assigned by default, causing permission errors when accessing other domains.

Roles added:
- calendar:write
- health:write
- habits:write
- skills:write
- projects:write
- relationships:write
- journal:write
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision: str = "20251207_standardize_user_roles"
down_revision: Union[str, None] = "20251207_domains_inferred_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mark as two-phase due to data manipulation
TWO_PHASE = True


# Standard domain write roles that all users should have
STANDARD_DOMAIN_ROLES = [
    ("calendar:write", "Write access to calendar domain"),
    ("health:write", "Write access to health domain"),
    ("habits:write", "Write access to habits domain"),
    ("skills:write", "Write access to skills domain"),
    ("projects:write", "Write access to projects domain"),
    ("relationships:write", "Write access to relationships domain"),
    ("journal:write", "Write access to journal domain"),
]


def upgrade() -> None:
    """
    Create missing domain roles and assign them to all existing users.

    This ensures all users have consistent write permissions across all domains.
    """
    bind = op.get_bind()
    session = Session(bind=bind)

    # Define table references for raw SQL operations
    role_table = sa.table(
        "role",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    user_role_table = sa.table(
        "user_role",
        sa.column("user_id", sa.Integer),
        sa.column("role_id", sa.Integer),
    )
    user_table = sa.table(
        "user",
        sa.column("id", sa.Integer),
    )

    # Step 1: Create any missing roles
    for role_name, role_description in STANDARD_DOMAIN_ROLES:
        # Check if role exists
        result = session.execute(sa.select(role_table.c.id).where(role_table.c.name == role_name)).fetchone()

        if not result:
            # Create the role
            session.execute(
                role_table.insert().values(
                    name=role_name,
                    description=role_description,
                )
            )

    session.commit()

    # Step 2: Get all user IDs and role IDs
    users = session.execute(sa.select(user_table.c.id)).fetchall()
    roles = {}
    for role_name, _ in STANDARD_DOMAIN_ROLES:
        result = session.execute(sa.select(role_table.c.id).where(role_table.c.name == role_name)).fetchone()
        if result:
            roles[role_name] = result[0]

    # Step 3: Assign missing roles to each user
    for (user_id,) in users:
        for role_name, role_id in roles.items():
            # Check if user already has this role
            existing = session.execute(
                sa.select(user_role_table.c.user_id).where(
                    sa.and_(
                        user_role_table.c.user_id == user_id,
                        user_role_table.c.role_id == role_id,
                    )
                )
            ).fetchone()

            if not existing:
                # Assign role to user
                session.execute(
                    user_role_table.insert().values(
                        user_id=user_id,
                        role_id=role_id,
                    )
                )

    session.commit()


def downgrade() -> None:
    """
    Remove the newly added domain roles from users (but keep the roles themselves).

    Note: This only removes the user-role associations, not the role definitions.
    The roles may still be needed for users created after this migration was applied.
    """
    bind = op.get_bind()
    session = Session(bind=bind)

    role_table = sa.table(
        "role",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    user_role_table = sa.table(
        "user_role",
        sa.column("user_id", sa.Integer),
        sa.column("role_id", sa.Integer),
    )

    # Get role IDs for the standard domain roles
    role_names = [name for name, _ in STANDARD_DOMAIN_ROLES]
    role_ids = session.execute(sa.select(role_table.c.id).where(role_table.c.name.in_(role_names))).fetchall()

    # Remove user-role associations for these roles
    for (role_id,) in role_ids:
        session.execute(user_role_table.delete().where(user_role_table.c.role_id == role_id))

    session.commit()
