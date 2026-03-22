"""HAB-019: ML smoke tests for habit prediction model.

Validates training pipeline on synthetic fixtures:
- Model trains successfully
- AUC > 0.6 on fixture data (relaxed for CI)
- Output shape correct (float 0.0-1.0)
"""

from datetime import date, timedelta

import pytest

pytestmark = pytest.mark.ml


class FakeLog:
    """Minimal HabitLog-like object for unit testing without DB."""

    def __init__(self, logged_date: date):
        self.logged_date = logged_date
        self.value = None
        self.habit_id = 1
        self.user_id = 1


def _build_fixture_logs(n_days: int = 60, skip_weekends: bool = True) -> list:
    """Generate realistic synthetic logs: logs on weekdays, skips weekends."""
    today = date.today()
    logs = []
    for i in range(n_days):
        d = today - timedelta(days=i)
        if skip_weekends and d.weekday() >= 5:
            continue
        logs.append(FakeLog(d))
    return logs


class TestHabitPredictionTraining:
    """Smoke tests for training pipeline."""

    def test_train_model_returns_model_and_metrics(self):
        from lifeos.domains.habits.ml.habit_prediction import train_model

        logs = _build_fixture_logs(n_days=60)
        model, metrics = train_model(logs, stat=None)
        assert model is not None, "Model should train on 60-day fixture data"
        assert "auc" in metrics
        assert "n_samples" in metrics
        assert metrics["n_samples"] >= 30

    def test_train_model_auc_above_threshold(self):
        """CI smoke: AUC should be > 0.6 on structured fixture data."""
        from lifeos.domains.habits.ml.habit_prediction import train_model

        logs = _build_fixture_logs(n_days=90)
        model, metrics = train_model(logs, stat=None)
        assert model is not None
        assert metrics["auc"] > 0.6, f"AUC {metrics['auc']:.3f} below CI threshold of 0.6"

    def test_train_model_insufficient_data(self):
        from lifeos.domains.habits.ml.habit_prediction import train_model

        logs = _build_fixture_logs(n_days=5)
        model, metrics = train_model(logs, stat=None)
        assert model is None, "Should not train with <14 days of data"

    def test_train_model_empty_logs(self):
        from lifeos.domains.habits.ml.habit_prediction import train_model

        model, metrics = train_model([], stat=None)
        assert model is None
        assert metrics["n_samples"] == 0


class TestHabitPredictionInference:
    """Smoke tests for prediction output."""

    def test_predict_returns_probability(self):
        from lifeos.domains.habits.ml.habit_prediction import (
            predict_completion,
            train_model,
        )

        logs = _build_fixture_logs(n_days=60)
        model, _ = train_model(logs, stat=None)
        assert model is not None

        prob = predict_completion(
            model,
            streak_length=5,
            completion_rate_7d=0.8,
            hours_since_last_log=20.0,
        )
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0

    def test_predict_varies_with_features(self):
        """Prediction should differ for different feature inputs."""
        from lifeos.domains.habits.ml.habit_prediction import (
            predict_completion,
            train_model,
        )

        logs = _build_fixture_logs(n_days=90)
        model, _ = train_model(logs, stat=None)
        assert model is not None

        prob_high = predict_completion(
            model,
            streak_length=30,
            completion_rate_7d=1.0,
            hours_since_last_log=10.0,
        )
        prob_low = predict_completion(
            model,
            streak_length=0,
            completion_rate_7d=0.0,
            hours_since_last_log=168.0,
        )
        # Not necessarily prob_high > prob_low (depends on learned weights),
        # but they should differ
        assert prob_high != prob_low


class TestModelSerialization:
    """Smoke tests for model save/load."""

    def test_save_and_load_roundtrip(self, tmp_path):
        from lifeos.domains.habits.ml.habit_prediction import (
            MODEL_VERSION,
            load_model,
            predict_completion,
            save_model,
            train_model,
        )

        logs = _build_fixture_logs(n_days=60)
        model, _ = train_model(logs, stat=None)
        assert model is not None

        path = str(tmp_path / "test_model.joblib")
        save_model(model, path)
        loaded_model, version = load_model(path)

        assert version == MODEL_VERSION
        # Predictions should be identical
        prob_orig = predict_completion(model, 5, 0.8, 20.0)
        prob_loaded = predict_completion(loaded_model, 5, 0.8, 20.0)
        assert prob_orig == prob_loaded
