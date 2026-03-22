"""HAB-016: Offline training script for habit completion prediction models.

Trains one logistic regression model per user, serialized with joblib.
Models are saved to instance/models/habits/ directory.

Usage:
    python -m lifeos.scripts.train_habit_model
    python -m lifeos.scripts.train_habit_model --user-id 1
"""

from __future__ import annotations

import argparse
from pathlib import Path

from lifeos import create_app
from lifeos.domains.habits.ml.habit_prediction import (
    MODEL_VERSION,
    save_model,
    train_model,
)
from lifeos.domains.habits.models import Habit, HabitLog, HabitStat


def train_all(user_id: int | None = None):
    app = create_app()
    with app.app_context():
        model_dir = Path(app.instance_path) / "models" / "habits"
        model_dir.mkdir(parents=True, exist_ok=True)

        query = Habit.query
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        habits = query.all()

        trained = 0
        skipped = 0

        for habit in habits:
            logs = HabitLog.query.filter_by(habit_id=habit.id).order_by(HabitLog.logged_date.asc()).all()
            stat = HabitStat.query.filter_by(habit_id=habit.id).first()

            model, metrics = train_model(logs, stat)
            if model is None:
                skipped += 1
                print(f"  SKIP habit {habit.id} ({habit.name}): " f"{int(metrics['n_samples'])} samples")
                continue

            path = str(model_dir / f"habit_{habit.id}_{MODEL_VERSION}.joblib")
            save_model(model, path)
            trained += 1
            print(
                f"  OK   habit {habit.id} ({habit.name}): "
                f"AUC={metrics['auc']:.3f}, "
                f"samples={int(metrics['n_samples'])}"
            )

        print(f"\nTraining complete: {trained} trained, {skipped} skipped, " f"{len(habits)} habits processed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train habit prediction models")
    parser.add_argument("--user-id", type=int, default=None, help="Train for specific user only")
    args = parser.parse_args()
    train_all(user_id=args.user_id)
