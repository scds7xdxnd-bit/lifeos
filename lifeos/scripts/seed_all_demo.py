"""Seed roles/permissions, admin user, and demo finance data in one go.

Usage:
    python -m lifeos.scripts.seed_all_demo --admin-email admin@example.com --admin-password admin12345
"""

from __future__ import annotations

import click

from lifeos import create_app
from lifeos.extensions import db
from lifeos.scripts.seed_admin import seed_admin_user, seed_roles_and_permissions
from lifeos.scripts.seed_demo import (
    seed_accounts,
    seed_demo_user,
    seed_journal_and_transactions,
    seed_receivables,
)


@click.command()
@click.option("--admin-email", default="admin@example.com", show_default=True)
@click.option("--admin-password", default="admin12345", show_default=True)
def main(admin_email: str, admin_password: str) -> None:
    app = create_app()
    with app.app_context():
        seed_roles_and_permissions()
        seed_admin_user(admin_email, admin_password, full_name="Admin")

        # Demo finance data
        demo_user = seed_demo_user()
        _, accounts = seed_accounts(demo_user.id)
        seed_journal_and_transactions(demo_user.id, accounts)
        seed_receivables(demo_user.id)

        db.session.commit()
        click.echo(f"Seeded admin ({admin_email}) and demo data for {demo_user.email}")


if __name__ == "__main__":
    main()
