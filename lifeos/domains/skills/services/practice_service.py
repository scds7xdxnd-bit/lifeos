"""Practice session service layer."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from lifeos.domains.skills.models.skill_models import PracticeSession, Skill
from lifeos.extensions import db


def get_session(user_id: int, session_id: int) -> Optional[PracticeSession]:
    return PracticeSession.query.filter_by(id=session_id, user_id=user_id).first()


def list_sessions(user_id: int, skill_id: Optional[int] = None, limit: int = 50):
    query = PracticeSession.query.filter_by(user_id=user_id)
    if skill_id:
        query = query.filter_by(skill_id=skill_id)
    return query.order_by(PracticeSession.practiced_at.desc()).limit(limit).all()


def upsert_session(
    user_id: int,
    skill_id: int,
    *,
    duration_minutes: int,
    intensity: Optional[int],
    notes: Optional[str],
    practiced_at: Optional[datetime],
) -> PracticeSession:
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first()
    if not skill:
        raise ValueError("not_found")
    session = PracticeSession(
        user_id=user_id,
        skill_id=skill_id,
        duration_minutes=duration_minutes,
        intensity=intensity,
        notes=notes,
        practiced_at=practiced_at or datetime.utcnow(),
    )
    db.session.add(session)
    db.session.commit()
    return session
