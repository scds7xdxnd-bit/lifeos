"""Lightweight forecasting using scheduled events."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from lifeos.core.read_cache import read_cache
from lifeos.domains.finance.models.schedule_models import MoneyScheduleDailyBalance

FINANCE_READ_CACHE_SCOPE = "finance.reads"


def generate_forecast(user_id: int, days: int = 30) -> List[dict]:
    """Return daily balances for the forecast horizon."""
    start = date.today()
    cache_key = {"view": "forecast", "start": start.isoformat(), "days": days}
    cached = read_cache.get(FINANCE_READ_CACHE_SCOPE, user_id, cache_key)
    if cached is not None:
        return cached
    balances = {
        row.as_of: float(row.balance) for row in MoneyScheduleDailyBalance.query.filter_by(user_id=user_id).all()
    }
    forecast = []
    running_total = 0.0
    for offset in range(days):
        day = start + timedelta(days=offset)
        running_total += balances.get(day, 0.0)
        forecast.append({"date": day.isoformat(), "projected_balance": round(running_total, 2)})
    read_cache.set(FINANCE_READ_CACHE_SCOPE, user_id, cache_key, forecast)
    return forecast
