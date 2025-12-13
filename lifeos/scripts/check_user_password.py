"""Utility CLI to verify a user's password hash.

Usage:
    flask check-user-password --email="user@example.com" --password="secret"
    python -m lifeos.scripts.check_user_password --email="user@example.com" --password="secret"
"""

from __future__ import annotations

import sys

import click
from flask.cli import with_appcontext
from sqlalchemy import func

from lifeos.core.auth.password import verify_password
from lifeos.core.users.models import User


@click.command("check-user-password")
@click.option("--email", required=True, help="User email to check (case-insensitive)")
@click.option("--password", required=True, help="Plaintext password to verify")
@with_appcontext
def check_user_password_command(email: str, password: str):
    """Verify a user's stored password hash against provided plaintext."""
    normalized = email.strip().lower()
    user = User.query.filter(func.lower(User.email) == normalized).first()
    if not user:
        click.echo(f"User not found: {normalized}", err=True)
        raise click.Abort()

    is_valid = verify_password(password, user.password_hash)
    click.echo(f"user_id={user.id} email={user.email}")
    click.echo(f"password_valid={is_valid}")


def main(argv: list[str] | None = None) -> int:
    """Entry point for python -m lifeos.scripts.check_user_password."""
    from lifeos import create_app

    app = create_app()
    with app.app_context():
        try:
            check_user_password_command.main(standalone_mode=False, args=argv)
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
