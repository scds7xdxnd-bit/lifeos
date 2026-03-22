"""Backfill scheduled_time from legacy time_of_day values.

Policy (idempotent):
- Only updates rows where scheduled_time IS NULL and time_of_day is set.
- Maps coarse legacy buckets to default local times:
  - morning   -> 08:00
  - afternoon -> 13:00
  - evening   -> 19:00
  - night     -> 21:00

Usage:
  /Users/ammarhakimi/Dev/finance_app_clean/.venv/bin/python -m lifeos.scripts.backfill_habit_scheduled_time --dry-run
  /Users/ammarhakimi/Dev/finance_app_clean/.venv/bin/python -m lifeos.scripts.backfill_habit_scheduled_time
"""

from __future__ import annotations

import argparse
from datetime import time

from lifeos import create_app
from lifeos.domains.habits.models.habit_models import Habit
from lifeos.extensions import db

_TIME_OF_DAY_MAPPING = {
    "morning": time(8, 0),
    "afternoon": time(13, 0),
    "evening": time(19, 0),
    "night": time(21, 0),
}


def backfill(*, dry_run: bool = False) -> tuple[int, int, int]:
    app = create_app()
    with app.app_context():
        habits = Habit.query.filter(Habit.scheduled_time.is_(None)).filter(Habit.time_of_day.isnot(None)).all()

        scanned = len(habits)
        updated = 0
        skipped = 0

        for habit in habits:
            raw = (habit.time_of_day or "").strip().lower()
            mapped = _TIME_OF_DAY_MAPPING.get(raw)
            if mapped is None:
                skipped += 1
                continue
            habit.scheduled_time = mapped
            updated += 1

        if dry_run:
            db.session.rollback()
        else:
            db.session.commit()

        return scanned, updated, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill habits scheduled_time")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview updates without committing",
    )
    args = parser.parse_args()

    scanned, updated, skipped = backfill(dry_run=args.dry_run)
    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(f"[{mode}] scanned={scanned} updated={updated} skipped_unmapped={skipped}")


if __name__ == "__main__":
    main()
