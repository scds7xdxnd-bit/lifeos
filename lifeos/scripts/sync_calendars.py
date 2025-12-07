"""CLI command for syncing Google and Apple Calendars.

Usage:
    flask sync-calendars                  # Sync all (Google + Apple)
    flask sync-calendars --provider google
    flask sync-calendars --provider apple
    flask sync-calendars --user 1         # Sync for specific user
"""

from __future__ import annotations

import click
from flask import current_app
from flask.cli import with_appcontext


@click.command("sync-calendars")
@click.option("--user", "-u", type=int, help="Sync for specific user ID only")
@click.option("--provider", "-p", type=click.Choice(["google", "apple", "all"]), default="all", help="Provider to sync")
@with_appcontext
def sync_calendars_command(user: int | None, provider: str):
    """Sync calendar connections for Google and/or Apple."""
    from lifeos.domains.calendar.tasks import (
        sync_all_google_calendars,
        sync_all_apple_calendars,
        sync_google_calendar_for_user,
        sync_apple_calendar_for_user,
    )
    from lifeos.domains.calendar.services.google_sync_service import GoogleCalendarError
    from lifeos.domains.calendar.services.apple_sync_service import AppleCalendarError

    if user:
        # Sync specific user
        if provider in ("google", "all"):
            click.echo(f"Syncing Google Calendar for user {user}...")
            try:
                stats = sync_google_calendar_for_user(user)
                click.echo(f"  ✓ Google: Created {stats['created']}, Updated {stats['updated']}, Deleted {stats['deleted']}")
            except GoogleCalendarError as e:
                click.echo(f"  ✗ Google: {e}", err=True)
        
        if provider in ("apple", "all"):
            click.echo(f"Syncing Apple Calendar for user {user}...")
            try:
                stats = sync_apple_calendar_for_user(user)
                click.echo(f"  ✓ Apple: Created {stats['created']}, Updated {stats['updated']}, Deleted {stats.get('deleted', 0)}")
            except AppleCalendarError as e:
                click.echo(f"  ✗ Apple: {e}", err=True)
    else:
        # Sync all users
        if provider in ("google", "all"):
            click.echo("Syncing all Google Calendar connections...")
            stats = sync_all_google_calendars()
            click.echo(
                f"  ✓ Google: {stats['synced_users']} users | "
                f"Created: {stats['created']}, Updated: {stats['updated']}, "
                f"Deleted: {stats['deleted']}, Errors: {stats['errors']}"
            )
        
        if provider in ("apple", "all"):
            click.echo("Syncing all Apple Calendar connections...")
            stats = sync_all_apple_calendars()
            click.echo(
                f"  ✓ Apple: {stats['synced_users']} users | "
                f"Created: {stats['created']}, Updated: {stats['updated']}, "
                f"Deleted: {stats['deleted']}, Errors: {stats['errors']}"
            )


def register_commands(app):
    """Register CLI commands with the app."""
    app.cli.add_command(sync_calendars_command)
