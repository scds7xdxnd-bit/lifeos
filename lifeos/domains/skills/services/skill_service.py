"""Skill service: CRUD + aggregates and event emission."""

from __future__ import annotations

from datetime import datetime, timedelta
from math import ceil
from typing import Dict, List, Literal, Optional

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
    goal_type: Optional[str] = None,
    goal_target_value: Optional[int] = None,
    goal_deadline: Optional[datetime] = None,
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
        goal_type=(goal_type or "").strip() or None,
        goal_target_value=goal_target_value,
        goal_deadline=goal_deadline,
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
        "goal_type",
        "goal_target_value",
        "goal_deadline",
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
            "updated_at": (skill.updated_at.isoformat() if skill.updated_at else datetime.utcnow().isoformat()),
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
    step_id: Optional[int] = None,
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
        step_id=step_id,
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


def update_practice_session(user_id: int, session_id: int, **fields) -> Optional[PracticeSession]:
    session = PracticeSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return None
    for key in ("duration_minutes", "intensity", "step_id", "notes", "practiced_at"):
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


def get_skill_summary(user_id: int, skill_id: int, recent_limit: int = 10) -> Optional[dict]:
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


def list_skills_with_aggregates(user_id: int, limit: int = 50, offset: int = 0) -> List[dict]:
    skills = Skill.query.filter_by(user_id=user_id).order_by(Skill.created_at.desc()).offset(offset).limit(limit).all()
    skill_ids = [s.id for s in skills]
    aggregates = _aggregate_sessions(user_id, skill_ids)

    recent_sessions = (
        PracticeSession.query.filter(PracticeSession.skill_id.in_(skill_ids), PracticeSession.user_id == user_id)
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


def list_skill_overview_cards(user_id: int, limit: int = 50, offset: int = 0) -> List[dict]:
    records = list_skills_with_aggregates(user_id=user_id, limit=limit, offset=offset)
    cards: List[dict] = []
    for record in records:
        skill: Skill = record["skill"]
        totals = record.get("totals", {})
        sessions_last_7 = int(totals.get("sessions_last_7") or 0)
        sessions_last_30 = int(totals.get("sessions_last_30") or 0)
        goal = _derive_goal_endpoint(skill, totals=totals)
        progress_state, risk_reason = _derive_progress_state(
            goal=goal, sessions_last_7=sessions_last_7, sessions_last_30=sessions_last_30
        )
        cards.append(
            {
                "skill_id": skill.id,
                "name": skill.name,
                "category": skill.category,
                "total_minutes": int(totals.get("total_minutes") or 0),
                "session_count": int(totals.get("session_count") or 0),
                "progress_state": progress_state,
                "goal": goal,
                "primary_action": "continue_practice",
                "requires_goal_setup": goal is None,
                "risk_reason": risk_reason,
            }
        )
    return cards


def get_skill_path(user_id: int, skill_id: int) -> Optional[dict]:
    summary = get_skill_summary(user_id=user_id, skill_id=skill_id, recent_limit=10)
    if not summary:
        return None

    skill: Skill = summary["skill"]
    totals = summary.get("totals", {})
    sessions_last_7 = int(totals.get("sessions_last_7") or 0)
    sessions_last_30 = int(totals.get("sessions_last_30") or 0)
    goal = _derive_goal_endpoint(skill, totals=totals)
    progress_state, risk_reason = _derive_progress_state(
        goal=goal,
        sessions_last_7=sessions_last_7,
        sessions_last_30=sessions_last_30,
    )

    path_steps: List[dict] = []
    path_steps.append(
        {
            "step_id": "continue_practice",
            "label": "Continue Practice",
            "status": "ready",
            "action": "continue_practice",
        }
    )

    if goal is None:
        path_steps.append(
            {
                "step_id": "define_goal",
                "label": "Define Goal Endpoint",
                "status": "ready",
                "action": "setup_goal",
            }
        )
    elif progress_state == "completed":
        path_steps.append(
            {
                "step_id": "raise_target",
                "label": "Set a New Target",
                "status": "ready",
                "action": "setup_goal",
            }
        )
    else:
        path_steps.append(
            {
                "step_id": "review_progress",
                "label": "Review Goal Progress",
                "status": "ready",
                "action": "review_goal",
            }
        )

    if progress_state == "at_risk":
        path_steps.append(
            {
                "step_id": "recover_consistency",
                "label": "Recover Consistency This Week",
                "status": "recommended",
                "action": "continue_practice",
            }
        )

    next_recommended_step = resolve_next_recommended_step(path_steps)

    return {
        "skill_id": skill.id,
        "progress_state": progress_state,
        "risk_reason": risk_reason,
        "goal": goal,
        "steps": path_steps,
        "next_recommended_step": next_recommended_step,
    }


def get_skill_forecast(user_id: int, skill_id: int, *, horizon_days: int = 7) -> Optional[dict]:
    summary = get_skill_summary(user_id=user_id, skill_id=skill_id, recent_limit=10)
    if not summary:
        return None

    if horizon_days is None:
        horizon_days = 7
    horizon_days = min(max(int(horizon_days), 1), 90)

    skill: Skill = summary["skill"]
    totals = summary.get("totals", {})
    goal = _derive_goal_endpoint(skill, totals=totals)

    now = datetime.utcnow()
    fourteen_days = now - timedelta(days=14)
    aggregate_row = (
        db.session.query(
            func.sum(PracticeSession.duration_minutes).label("total_minutes"),
            func.count(PracticeSession.id).label("session_count"),
        )
        .filter(PracticeSession.skill_id == skill.id, PracticeSession.user_id == user_id)
        .filter(PracticeSession.practiced_at >= fourteen_days)
        .one()
    )

    total_minutes_last_14 = int(aggregate_row.total_minutes or 0)
    sessions_last_14 = int(aggregate_row.session_count or 0)
    avg_daily_minutes_last_14 = float(total_minutes_last_14) / 14.0

    projected_minutes = int(round(avg_daily_minutes_last_14 * float(horizon_days)))
    projected_sessions = int(ceil((float(sessions_last_14) / 14.0) * float(horizon_days)))

    forecast_state: Literal["on_track", "at_risk", "completed", "insufficient_data"] = "on_track"
    risk_reason: Optional[str] = None

    projected_goal_progress_ratio: Optional[float] = None
    if goal is None:
        forecast_state = "at_risk"
        risk_reason = "no_goal_configured"
    elif float(goal.get("progress_ratio") or 0.0) >= 1.0:
        forecast_state = "completed"
    else:
        goal_type = str(goal.get("goal_type") or "")
        current_value = float(goal.get("current_value") or 0.0)
        target_value = float(goal.get("target_value") or 0.0)

        projected_value = current_value
        if sessions_last_14 == 0:
            forecast_state = "at_risk"
            risk_reason = "no_recent_sessions"
        elif sessions_last_14 < 2:
            forecast_state = "insufficient_data"
            risk_reason = "insufficient_history"
        elif goal_type not in {"hours", "sessions"}:
            forecast_state = "insufficient_data"
            risk_reason = "non_projectable_goal_type"
        else:
            if goal_type == "hours":
                projected_value += float(projected_minutes) / 60.0
            elif goal_type == "sessions":
                projected_value += float(projected_sessions)

            if target_value > 0:
                projected_goal_progress_ratio = min(max(projected_value / target_value, 0.0), 1.0)
            forecast_state = "on_track"

    return {
        "skill_id": skill.id,
        "horizon_days": horizon_days,
        "forecast_state": forecast_state,
        "risk_reason": risk_reason,
        "goal": goal,
        "baseline": {
            "avg_daily_minutes_last_14": round(avg_daily_minutes_last_14, 2),
            "sessions_last_14": sessions_last_14,
            "total_minutes_last_14": total_minutes_last_14,
        },
        "projection": {
            "projected_minutes_next_window": projected_minutes,
            "projected_sessions_next_window": projected_sessions,
            "projected_goal_progress_ratio": projected_goal_progress_ratio,
        },
    }


def resolve_next_recommended_step(steps: List[dict]) -> Optional[dict]:
    if not steps:
        return None
    for step in steps:
        if step.get("status") == "recommended":
            return step
    for step in steps:
        if step.get("status") == "ready":
            return step
    return steps[0]


def _derive_goal_endpoint(skill: Skill, *, totals: Optional[dict] = None) -> Optional[dict]:
    goal_type = (skill.goal_type or "").strip().lower()
    target_value = skill.goal_target_value

    if not goal_type or target_value is None or target_value <= 0:
        # Backward-compatible fallback to legacy levels.
        target = skill.target_level
        current = skill.current_level
        if target is None or target <= 0:
            return None
        current_value = current if current is not None else 0
        progress_ratio = min(max(current_value / target, 0.0), 1.0)
        return {
            "goal_type": "milestones",
            "target_value": target,
            "current_value": current_value,
            "progress_ratio": progress_ratio,
            "deadline": None,
        }

    aggregates = totals or {}
    if goal_type == "hours":
        current_value = float(aggregates.get("total_minutes") or 0) / 60.0
    elif goal_type == "sessions":
        current_value = float(aggregates.get("session_count") or 0)
    else:
        current_value = float(skill.current_level or 0)

    progress_ratio = min(max(current_value / float(target_value), 0.0), 1.0)
    return {
        "goal_type": goal_type,
        "target_value": float(target_value),
        "current_value": current_value,
        "progress_ratio": progress_ratio,
        "deadline": skill.goal_deadline,
    }


def _derive_progress_state(
    *,
    goal: Optional[dict],
    sessions_last_7: int,
    sessions_last_30: int,
) -> tuple[Literal["on_track", "at_risk", "completed"], Optional[str]]:
    if goal:
        if float(goal.get("progress_ratio") or 0.0) >= 1.0:
            return "completed", None
        if sessions_last_7 == 0:
            return "at_risk", "no_recent_sessions"
        return "on_track", None

    if sessions_last_30 == 0:
        return "at_risk", "no_recent_sessions"
    return "on_track", None


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
            aggregates.setdefault(sid, {"total_minutes": 0, "session_count": 0, "last_practiced_at": None})
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
