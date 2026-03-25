"""Seed random calendar events for a user.

Usage examples:
  python -m lifeos.scripts.seed_calendar_random --email demo@lifeos.test --count 60
  python -m lifeos.scripts.seed_calendar_random --email you@example.com --count 40 --days-back 10 --days-forward 45
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

import click

from lifeos import create_app
from lifeos.core.users.models import User
from lifeos.domains.calendar.services import create_calendar_event
from lifeos.scripts.seed_demo import seed_demo_user

EVENT_TITLES = [
    "Team standup",
    "Deep work block",
    "Workout session",
    "Project review",
    "Lunch with friend",
    "Skill practice",
    "Finance check-in",
    "Doctor appointment",
    "Reading hour",
    "Design sync",
    "Code review",
    "Planning session",
    "Weekly reflection",
    "Focus sprint",
    "Therapy session",
    "Dinner reservation",
    "Client call",
    "Habit reset",
    "Walking break",
    "Study session",
]

LOCATIONS = [
    "Home",
    "Office",
    "Cafe",
    "Gym",
    "Online",
    "Library",
    "Co-working space",
    "Park",
    "Downtown",
    None,
]


@click.command()
@click.option("--email", default="demo@lifeos.test", show_default=True, help="User email to seed events for.")
@click.option("--count", default=50, show_default=True, type=click.IntRange(1, 500), help="Number of events to create.")
@click.option(
    "--days-back",
    default=14,
    show_default=True,
    type=click.IntRange(0, 365),
    help="How many days in the past to include.",
)
@click.option(
    "--days-forward",
    default=60,
    show_default=True,
    type=click.IntRange(1, 730),
    help="How many days in the future to include.",
)
def main(email: str, count: int, days_back: int, days_forward: int) -> None:
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if not user and email == "demo@lifeos.test":
            user = seed_demo_user()

        if not user:
            raise click.ClickException(
                f"User '{email}' not found. Create/login this user first, or run with --email demo@lifeos.test."
            )

        start_window = datetime.now().replace(second=0, microsecond=0) - timedelta(days=days_back)
        end_window = datetime.now().replace(second=0, microsecond=0) + timedelta(days=days_forward)
        window_days = max((end_window.date() - start_window.date()).days, 1)

        created = 0
        for _ in range(count):
            day_offset = random.randint(0, window_days)
            day = start_window.date() + timedelta(days=day_offset)

            hour = random.randint(7, 20)
            minute = random.choice([0, 30])
            start_dt = datetime(day.year, day.month, day.day, hour, minute)

            duration_minutes = random.choice([30, 60, 90, 120])
            end_dt = start_dt + timedelta(minutes=duration_minutes)

            title = random.choice(EVENT_TITLES)
            location = random.choice(LOCATIONS)
            all_day = random.random() < 0.08

            if all_day:
                start_dt = datetime(day.year, day.month, day.day, 0, 0)
                end_dt = datetime(day.year, day.month, day.day, 23, 59)

            create_calendar_event(
                user_id=user.id,
                title=title,
                start_time=start_dt,
                end_time=end_dt,
                location=location,
                all_day=all_day,
                source="manual",
            )
            created += 1

        click.echo(f"Seeded {created} random calendar events for {user.email} (user_id={user.id}).")


if __name__ == "__main__":
    main()
