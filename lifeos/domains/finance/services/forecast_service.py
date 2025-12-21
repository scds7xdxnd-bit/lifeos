"""Lightweight forecasting using scheduled events."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from lifeos.domains.finance.models.schedule_models import MoneyScheduleDailyBalance


def generate_forecast(user_id: int, days: int = 30) -> List[dict]:
    """Return daily balances for the forecast horizon."""
    start = date.today()
    balances = {
        row.as_of: float(row.balance) for row in MoneyScheduleDailyBalance.query.filter_by(user_id=user_id).all()
    }
    forecast = []
    running_total = 0.0
    for offset in range(days):
        day = start + timedelta(days=offset)
        running_total += balances.get(day, 0.0)
        forecast.append({"date": day.isoformat(), "projected_balance": round(running_total, 2)})
    return forecast
