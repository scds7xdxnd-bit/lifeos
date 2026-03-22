"""HAB-016: Habit completion prediction model.

Logistic regression baseline — 4 features, per-user, offline-trained.
Predictions are P(completion_today) ∈ [0.0, 1.0].
NOT surfaced to users in Phase 12d.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from lifeos.domains.habits.models.habit_models import HabitLog, HabitStat

logger = logging.getLogger(__name__)

MODEL_VERSION = "habit_lr_v1"


def _extract_features(
    logs: List[HabitLog],
    stat: Optional[HabitStat],
) -> List[Tuple[np.ndarray, int]]:
    """Build (feature_vector, label) pairs from historical logs.

    For each day the habit existed, produce a feature row:
      [day_of_week, streak_length_at_day, completion_rate_7d, hours_since_last_log]
    Label: 1 if logged that day, 0 otherwise.
    """
    if not logs:
        return []

    logged_dates = {lg.logged_date for lg in logs}
    sorted_dates = sorted(logged_dates)
    if not sorted_dates:
        return []

    start = sorted_dates[0]
    end = date.today()
    samples: List[Tuple[np.ndarray, int]] = []

    # Walk day-by-day from start to end
    streak = 0
    last_logged: Optional[date] = None
    d = start
    while d <= end:
        # Label
        label = 1 if d in logged_dates else 0

        # Feature 1: day of week (0=Mon, 6=Sun)
        dow = d.weekday()

        # Feature 2: streak length going into this day
        streak_at_day = streak

        # Feature 3: completion rate over prior 7 days
        week_start = d - timedelta(days=7)
        week_logged = sum(1 for dd in logged_dates if week_start < dd <= d - timedelta(days=1))
        rate_7d = week_logged / 7.0

        # Feature 4: hours since last log
        if last_logged is not None:
            hours_since = (
                datetime.combine(d, datetime.min.time()) - datetime.combine(last_logged, datetime.min.time())
            ).total_seconds() / 3600.0
        else:
            hours_since = 168.0  # default 1 week

        features = np.array([dow, streak_at_day, rate_7d, hours_since], dtype=np.float64)
        samples.append((features, label))

        # Update running state for next day
        if label == 1:
            streak += 1
            last_logged = d
        else:
            streak = 0

        d += timedelta(days=1)

    return samples


def train_model(
    logs: List[HabitLog],
    stat: Optional[HabitStat] = None,
    test_size: float = 0.2,
) -> Tuple[Optional[LogisticRegression], Dict[str, float]]:
    """Train a per-habit logistic regression model.

    Returns (model, metrics) where metrics includes 'auc' and 'n_samples'.
    Returns (None, metrics) if insufficient data.
    """
    samples = _extract_features(logs, stat)
    metrics: Dict[str, float] = {"n_samples": float(len(samples)), "auc": 0.0}

    if len(samples) < 14:  # need at least 2 weeks of history
        logger.info("Insufficient data for training: %d samples", len(samples))
        return None, metrics

    X = np.array([s[0] for s in samples])
    y = np.array([s[1] for s in samples])

    # Need both classes present
    if len(set(y)) < 2:
        logger.info("Only one class present in labels, skipping training")
        return None, metrics

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=42,
        stratify=y,
    )

    model = LogisticRegression(random_state=42, max_iter=200)
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    try:
        auc = roc_auc_score(y_test, y_prob)
    except ValueError:
        auc = 0.0

    metrics["auc"] = float(auc)
    logger.info("Model trained: AUC=%.3f, samples=%d", auc, len(samples))
    return model, metrics


def predict_completion(
    model: LogisticRegression,
    streak_length: int,
    completion_rate_7d: float,
    hours_since_last_log: float,
    target_date: Optional[date] = None,
) -> float:
    """Predict P(completion_today) for a single habit.

    Returns float in [0.0, 1.0].
    """
    d = target_date or date.today()
    features = np.array(
        [[d.weekday(), streak_length, completion_rate_7d, hours_since_last_log]],
        dtype=np.float64,
    )
    prob = model.predict_proba(features)[0, 1]
    return float(prob)


def save_model(model: LogisticRegression, path: str) -> None:
    """Serialize model to disk."""
    joblib.dump({"model": model, "model_version": MODEL_VERSION}, path)


def load_model(path: str) -> Tuple[LogisticRegression, str]:
    """Load model from disk. Returns (model, model_version)."""
    data = joblib.load(path)
    return data["model"], data["model_version"]
