"""Cross-domain correlation rules using recent events."""

from __future__ import annotations

from typing import List

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.services import recent_events


def apply_rules(event: EventRecord) -> List[dict]:
    user_id = event.user_id
    if not user_id:
        return []

    insights: List[dict] = []

    # Finance spend + poor sleep heuristic
    if event.event_type == "finance.transaction.created":
        amount = float(event.payload.get("amount") or 0.0)
        if amount < 0:
            amount = -amount
        if amount >= 100:
            sleep_events = recent_events(user_id, ["health.metric.updated"], days=3, limit=5)
            low_sleep = any(
                (e.payload.get("metric") == "sleep_hours" and float(e.payload.get("value") or 0.0) < 6.0)
                for e in sleep_events
            )
            if low_sleep:
                insights.append(
                    {
                        "type": "finance_sleep_spend",
                        "message": "High spending while sleep is low. Consider pausing major purchases after short sleep.",
                        "severity": "warning",
                        "context": {"amount": amount, "recent_sleep_events": len(sleep_events)},
                    }
                )

    # Habit streak boosts project completion insight
    if event.event_type == "projects.task.completed":
        habit_logs = recent_events(user_id, ["habits.habit.logged"], days=7, limit=10)
        streaks = [int(ev.payload.get("streak") or 0) for ev in habit_logs if ev.payload.get("streak") is not None]
        if streaks and max(streaks) >= 5:
            insights.append(
                {
                    "type": "habit_project_synergy",
                    "message": "Strong habit streak alongside task completions. Keep the routine to sustain project velocity.",
                    "severity": "info",
                    "context": {"max_streak": max(streaks), "tasks_completed": 1},
                }
            )

    # Skill practice + journal sentiment check
    if event.event_type == "skills.practice.logged":
        journal_events = recent_events(user_id, ["journal.entry.created"], days=3, limit=5)
        moods = [ev.payload.get("mood") for ev in journal_events if ev.payload.get("mood")]
        if moods and any(m.lower() in {"tired", "sad", "stressed"} for m in moods if isinstance(m, str)):
            insights.append(
                {
                    "type": "skill_mood_uplift",
                    "message": "Practice sessions follow low-mood journal entries. Track whether practice improves mood.",
                    "severity": "info",
                    "context": {"journal_moods": moods},
                }
            )

    return insights
