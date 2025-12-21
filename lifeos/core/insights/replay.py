"""Deterministic replay harness for insights (Phase 3a)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from lifeos.core.insights.routing import enforce_confidence_routing
from lifeos.core.insights.rules import (
    cross_rules,
    finance_rules,
    habit_rules,
    health_rules,
    project_rules,
    skill_rules,
)


@dataclass(frozen=True)
class ReplayEvent:
    event_type: str
    payload: dict
    user_id: int | None = None


RULE_PIPELINE = [
    finance_rules.apply_rules,
    habit_rules.apply_rules,
    health_rules.apply_rules,
    skill_rules.apply_rules,
    project_rules.apply_rules,
]


def _apply_rules(event: ReplayEvent, include_cross_rules: bool) -> List[dict]:
    insights: List[dict] = []
    for rule_fn in RULE_PIPELINE:
        insights.extend(rule_fn(event) or [])
    if include_cross_rules:
        insights.extend(cross_rules.apply_rules(event) or [])
    return insights


def replay_insights(
    events: Iterable[ReplayEvent],
    *,
    include_cross_rules: bool = False,
) -> List[dict]:
    """Replay a sequence of events into deterministic insight outputs."""
    output: List[dict] = []
    for ev in events:
        produced = _apply_rules(ev, include_cross_rules=include_cross_rules)
        for ins in produced:
            insight_type = ins.get("type") or "generic"
            context = dict(ins.get("context") or {})
            band, routing = enforce_confidence_routing(
                insight_type=insight_type,
                event_type=ev.event_type,
                severity=ins.get("severity"),
                context=context,
            )
            context.setdefault("confidence_band", band)
            context.setdefault("routing", routing)
            output.append(
                {
                    "type": insight_type,
                    "message": ins.get("message") or "",
                    "severity": ins.get("severity") or "info",
                    "context": context,
                    "event_type": ev.event_type,
                }
            )
    return output


__all__ = ["ReplayEvent", "replay_insights"]
