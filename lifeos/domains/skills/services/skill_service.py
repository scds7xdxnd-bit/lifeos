"""Skill service: CRUD + aggregates and event emission."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func

from lifeos.domains.skills.events import (
    SKILLS_PRACTICE_LOGGED,
    SKILLS_SKILL_CREATED,
    SKILLS_SKILL_DELETED,
    SKILLS_SKILL_UPDATED,
)
from lifeos.domains.skills.models.skill_models import PracticeSession, Skill
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


def create_skill(
    user_id: int,
    *,
    name: str,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    target_level: Optional[int] = None,
    current_level: Optional[int] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Skill:
    name_norm = (name or "").strip()
    if not name_norm:
        raise ValueError("validation_error")

    existing = Skill.query.filter_by(user_id=user_id, name=name_norm).first()
    if existing:
        raise ValueError("duplicate")

    skill = Skill(
        user_id=user_id,
        name=name_norm,
        category=(category or "").strip() or None,
        difficulty=(difficulty or "").strip() or None,
        target_level=target_level,
        current_level=current_level,
        description=(description or "").strip() or None,
        tags=tags or [],
    )
    db.session.add(skill)
    db.session.flush()

    enqueue_outbox(
        SKILLS_SKILL_CREATED,
        {
            "skill_id": skill.id,
            "user_id": user_id,
            "name": skill.name,
            "category": skill.category,
            "difficulty": skill.difficulty,
            "target_level": skill.target_level,
            "current_level": skill.current_level,
            "created_at": skill.created_at.isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return skill


def update_skill(user_id: int, skill_id: int, **fields) -> Optional[Skill]:
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first()
    if not skill:
        return None

    changed_fields: Dict[str, object] = {}
    for key in (
        "name",
        "category",
        "difficulty",
        "target_level",
        "current_level",
        "description",
        "tags",
    ):
        if key in fields:
            val = fields[key]
            if isinstance(val, str):
                val = val.strip()
            setattr(skill, key, val)
            changed_fields[key] = val

    enqueue_outbox(
        SKILLS_SKILL_UPDATED,
        {
            "skill_id": skill.id,
            "user_id": user_id,
            "fields": changed_fields,
            "updated_at": (
                skill.updated_at.isoformat()
                if skill.updated_at
                else datetime.utcnow().isoformat()
            ),
        },
        user_id=user_id,
    )
    db.session.commit()
    return skill


def delete_skill(user_id: int, skill_id: int) -> bool:
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first()
    if not skill:
        return False
    db.session.delete(skill)
    enqueue_outbox(
        SKILLS_SKILL_DELETED,
        {"skill_id": skill_id, "user_id": user_id},
        user_id=user_id,
    )
    db.session.commit()
    return True


def log_practice_session(
    user_id: int,
    skill_id: int,
    *,
    duration_minutes: int,
    intensity: Optional[int] = None,
    notes: Optional[str] = None,
    practiced_at: Optional[datetime] = None,
) -> PracticeSession:
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first()
    if not skill:
        raise ValueError("not_found")
    if duration_minutes <= 0:
        raise ValueError("validation_error")
    session = PracticeSession(
        user_id=user_id,
        skill_id=skill_id,
        duration_minutes=duration_minutes,
        intensity=intensity,
        notes=(notes or "").strip() or None,
        practiced_at=practiced_at or datetime.utcnow(),
    )
    db.session.add(session)
    db.session.flush()
    enqueue_outbox(
        SKILLS_PRACTICE_LOGGED,
        {
            "session_id": session.id,
            "skill_id": skill_id,
            "user_id": user_id,
            "duration_minutes": duration_minutes,
            "intensity": intensity,
            "practiced_at": session.practiced_at.isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return session


def update_practice_session(
    user_id: int, session_id: int, **fields
) -> Optional[PracticeSession]:
    session = PracticeSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return None
    for key in ("duration_minutes", "intensity", "notes", "practiced_at"):
        if key in fields:
            setattr(session, key, fields[key])
    db.session.commit()
    return session


def delete_practice_session(user_id: int, session_id: int) -> bool:
    session = PracticeSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return False
    db.session.delete(session)
    db.session.commit()
    return True


def get_skill_summary(
    user_id: int, skill_id: int, recent_limit: int = 10
) -> Optional[dict]:
    skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first()
    if not skill:
        return None

    aggregates = _aggregate_sessions(user_id, skill_ids=[skill_id])
    agg = aggregates.get(skill_id, {})

    recent_sessions = (
        PracticeSession.query.filter_by(skill_id=skill_id, user_id=user_id)
        .order_by(PracticeSession.practiced_at.desc())
        .limit(recent_limit)
        .all()
    )

    streak = _compute_streak_days(recent_sessions)
    return {
        "skill": skill,
        "totals": agg,
        "recent_sessions": recent_sessions,
        "streak_days": streak,
    }


def list_skills_with_aggregates(
    user_id: int, limit: int = 50, offset: int = 0
) -> List[dict]:
    skills = (
        Skill.query.filter_by(user_id=user_id)
        .order_by(Skill.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    skill_ids = [s.id for s in skills]
    aggregates = _aggregate_sessions(user_id, skill_ids)

    recent_sessions = (
        PracticeSession.query.filter(
            PracticeSession.skill_id.in_(skill_ids), PracticeSession.user_id == user_id
        )
        .order_by(PracticeSession.practiced_at.desc())
        .limit(len(skill_ids) * 5 if skill_ids else 0)
        .all()
    )
    sessions_by_skill: Dict[int, List[PracticeSession]] = {}
    for session in recent_sessions:
        sessions_by_skill.setdefault(session.skill_id, []).append(session)

    payload = []
    for skill in skills:
        agg = aggregates.get(skill.id, {})
        streak = _compute_streak_days(sessions_by_skill.get(skill.id, []))
        payload.append(
            {
                "skill": skill,
                "totals": agg,
                "recent_sessions": sessions_by_skill.get(skill.id, []),
                "streak_days": streak,
            }
        )
    return payload


def _aggregate_sessions(user_id: int, skill_ids: List[int]) -> Dict[int, dict]:
    if not skill_ids:
        return {}
    now = datetime.utcnow()
    seven_days = now - timedelta(days=7)
    thirty_days = now - timedelta(days=30)

    base = (
        db.session.query(
            PracticeSession.skill_id.label("skill_id"),
            func.sum(PracticeSession.duration_minutes).label("total_minutes"),
            func.count(PracticeSession.id).label("session_count"),
            func.max(PracticeSession.practiced_at).label("last_practiced_at"),
        )
        .filter(PracticeSession.user_id == user_id)
        .filter(PracticeSession.skill_id.in_(skill_ids))
        .group_by(PracticeSession.skill_id)
        .all()
    )
    aggregates = {
        row.skill_id: {
            "total_minutes": int(row.total_minutes or 0),
            "session_count": int(row.session_count or 0),
            "last_practiced_at": row.last_practiced_at,
        }
        for row in base
    }

    # last 7 / 30 day counts
    for window, key in (
        (seven_days, "sessions_last_7"),
        (thirty_days, "sessions_last_30"),
    ):
        rows = (
            db.session.query(
                PracticeSession.skill_id,
                func.count(PracticeSession.id).label("count"),
            )
            .filter(PracticeSession.user_id == user_id)
            .filter(PracticeSession.skill_id.in_(skill_ids))
            .filter(PracticeSession.practiced_at >= window)
            .group_by(PracticeSession.skill_id)
            .all()
        )
        for row in rows:
            aggregates.setdefault(
                row.skill_id,
                {"total_minutes": 0, "session_count": 0, "last_practiced_at": None},
            )
            aggregates[row.skill_id][key] = int(row.count or 0)
        for sid in skill_ids:
            aggregates.setdefault(
                sid, {"total_minutes": 0, "session_count": 0, "last_practiced_at": None}
            )
            aggregates[sid].setdefault(key, 0)
    return aggregates


def _compute_streak_days(sessions: List[PracticeSession]) -> int:
    if not sessions:
        return 0
    streak = 0
    last_date = None
    for session in sorted(sessions, key=lambda s: s.practiced_at, reverse=True):
        day = session.practiced_at.date()
        if last_date is None:
            streak = 1
        else:
            delta = (last_date - day).days
            if delta == 1:
                streak += 1
            elif delta == 0:
                continue
            else:
                break
        last_date = day
    return streak
