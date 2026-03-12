"""Cross-domain pair profiles."""

from __future__ import annotations

from lifeos.core.insights.inquiry_cross_domain.pairs.finance_habits import FINANCE_HABITS_V1
from lifeos.core.insights.inquiry_cross_domain.pairs.health_habits import HEALTH_HABITS_V1
from lifeos.core.insights.inquiry_cross_domain.pairs.journal_habits import JOURNAL_HABITS_V1
from lifeos.core.insights.inquiry_cross_domain.pairs.projects_calendar import PROJECTS_CALENDAR_V1
from lifeos.core.insights.inquiry_cross_domain.pairs.projects_skills import PROJECTS_SKILLS_V1
from lifeos.core.insights.inquiry_cross_domain.pairs.relationships_journal import RELATIONSHIPS_JOURNAL_V1

PAIR_PROFILES = (
    FINANCE_HABITS_V1,
    PROJECTS_SKILLS_V1,
    JOURNAL_HABITS_V1,
    HEALTH_HABITS_V1,
    PROJECTS_CALENDAR_V1,
    RELATIONSHIPS_JOURNAL_V1,
)

__all__ = [
    "FINANCE_HABITS_V1",
    "PROJECTS_SKILLS_V1",
    "JOURNAL_HABITS_V1",
    "HEALTH_HABITS_V1",
    "PROJECTS_CALENDAR_V1",
    "RELATIONSHIPS_JOURNAL_V1",
    "PAIR_PROFILES",
]
