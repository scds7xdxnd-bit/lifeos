"""Admin session reset CLI (backend-only, no UI).

Usage examples:
    flask admin-reset-sessions --user-id=123 --reason="atlas login mismatch"
    flask admin-reset-sessions --email=user@example.com --reason="ops reset"
    python -m lifeos.scripts.admin_reset_sessions --user-id=123 --reason="ops reset"
"""

from __future__ import annotations

import sys

import click
from flask.cli import with_appcontext
from sqlalchemy import func

from lifeos.core.auth.constants import SESSION_SCOPE_ALL
from lifeos.core.auth.session_services import SessionLifecycleService


@click.command("admin-reset-sessions")
@click.option("--user-id", type=int, help="Target user id for session reset")
@click.option("--email", type=str, help="Target user email (case-insensitive)")
@click.option("--reason", required=True, help="Reason for reset (required)")
@click.option("--initiated-by", type=int, help="Admin user id initiating reset (optional)")
@with_appcontext
def admin_reset_sessions_command(user_id: int | None, email: str | None, reason: str, initiated_by: int | None):
    """Invalidate sessions for a user and emit auth.session.admin_reset via service."""
    reason_clean = (reason or "").strip()
    if not reason_clean:
        click.echo("--reason is required", err=True)
        raise click.Abort()
    if not user_id and not email:
        click.echo("Provide --user-id or --email", err=True)
        raise click.Abort()

    from lifeos.core.users.models import User

    target_user_id = user_id
    if email and not target_user_id:
        normalized = email.strip().lower()
        user = User.query.filter(func.lower(User.email) == normalized).first()
        if not user:
            click.echo(f"User with email {normalized} not found", err=True)
            raise click.Abort()
        target_user_id = user.id

    if not target_user_id:
        click.echo("Could not resolve user_id", err=True)
        raise click.Abort()

    service = SessionLifecycleService()
    try:
        result = service.admin_reset(
            user_id=target_user_id,
            session_scope=SESSION_SCOPE_ALL,
            session_id=None,
            reason=reason_clean,
            initiated_by_admin_id=initiated_by,
        )
    except ValueError as exc:
        if str(exc) == "not_found":
            click.echo(f"User {target_user_id} not found", err=True)
            raise click.Abort()
        if str(exc) == "reason_required":
            click.echo("Reason is required", err=True)
            raise click.Abort()
        raise

    click.echo(
        f"admin_reset ok: user_id={target_user_id} reset_count={result['reset_count']} "
        f"scope={result['session_scope']} reason=\"{reason_clean}\""
    )
    click.echo("Outbox event enqueued; worker will dispatch auth.session.admin_reset.")


def main(argv: list[str] | None = None) -> int:
    """Entry point for python -m lifeos.scripts.admin_reset_sessions."""
    from lifeos import create_app

    app = create_app()
    with app.app_context():
        try:
            admin_reset_sessions_command.main(standalone_mode=False, args=argv)
        except SystemExit as exc:  # click may raise SystemExit
            return exc.code if isinstance(exc.code, int) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
