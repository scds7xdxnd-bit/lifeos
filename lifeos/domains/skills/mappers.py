"""DTO ↔ dict mappers for skills domain."""

from __future__ import annotations

from lifeos.domains.skills.models.skill_models import PracticeSession, Skill
from lifeos.domains.skills.schemas.skill_schemas import PracticeSessionResponse, SkillSummaryResponse


def map_skill_summary(summary: dict) -> SkillSummaryResponse:
    skill: Skill = summary["skill"]
    totals = summary.get("totals", {})
    recent_sessions = summary.get("recent_sessions", [])
    return SkillSummaryResponse(
        id=skill.id,
        name=skill.name,
        category=skill.category,
        difficulty=skill.difficulty,
        target_level=skill.target_level,
        current_level=skill.current_level,
        description=skill.description,
        tags=skill.tags or [],
        total_minutes=int(totals.get("total_minutes") or 0),
        session_count=int(totals.get("session_count") or 0),
        last_practiced_at=totals.get("last_practiced_at"),
        streak_days=summary.get("streak_days", 0),
        sessions_last_7=int(totals.get("sessions_last_7") or 0),
        sessions_last_30=int(totals.get("sessions_last_30") or 0),
        recent_sessions=[map_session_response(s) for s in recent_sessions],
    )


def map_session_response(session: PracticeSession) -> PracticeSessionResponse:
    return PracticeSessionResponse(
        id=session.id,
        skill_id=session.skill_id,
        duration_minutes=session.duration_minutes,
        intensity=session.intensity,
        notes=session.notes,
        practiced_at=session.practiced_at,
    )
