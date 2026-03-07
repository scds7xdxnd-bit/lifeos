"""Background task to recompute money schedule balances."""

from __future__ import annotations

from lifeos.domains.finance.services.schedule_service import recompute_daily_balances


def run(user_id: int) -> dict:
    return recompute_daily_balances(user_id)
