"""Monthly trial balance rollup."""

from __future__ import annotations

from collections import defaultdict

from lifeos.domains.finance.models.accounting_models import JournalLine


def compute_monthly_trial_balance(user_id: int) -> dict:
    """Aggregate debits/credits by month."""
    totals = defaultdict(lambda: {"debit": 0.0, "credit": 0.0})
    lines = (
        JournalLine.query.join(JournalLine.entry)
        .filter(JournalLine.entry.has(user_id=user_id))
        .all()
    )
    for line in lines:
        month = line.entry.posted_at.strftime("%Y-%m")
        totals[month]["debit"] += float(line.debit or 0)
        totals[month]["credit"] += float(line.credit or 0)
    return totals
