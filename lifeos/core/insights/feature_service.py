"""Feature computation for Phase 5b deterministic insights."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Dict, Iterable, Optional

from sqlalchemy import func

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.feature_models import FeatureDaily
from lifeos.domains.calendar.events import CALENDAR_EVENT_CREATED
from lifeos.domains.finance.events import FINANCE_TRANSACTION_CREATED
from lifeos.domains.habits.events import HABITS_HABIT_LOGGED
from lifeos.domains.health.events import HEALTH_METRIC_UPDATED
from lifeos.domains.journal.events import JOURNAL_ENTRY_CREATED
from lifeos.domains.projects.events import TASK_COMPLETED
from lifeos.domains.relationships.events import REL_INTERACTION_LOGGED
from lifeos.extensions import db

FEATURE_VERSION = "v1"


@dataclass(frozen=True)
class FeatureDefinition:
    key: str
    source_domain: str
    description: str
    version: str = FEATURE_VERSION


FEATURE_DEFINITIONS = {
    "calendar.event.count": FeatureDefinition(
        key="calendar.event.count",
        source_domain="calendar",
        description="Count of calendar events created.",
    ),
    "calendar.event.late_night.count": FeatureDefinition(
        key="calendar.event.late_night.count",
        source_domain="calendar",
        description="Count of late-night calendar events (21:00-04:59).",
    ),
    "calendar.obligation.count": FeatureDefinition(
        key="calendar.obligation.count",
        source_domain="calendar",
        description="Count of calendar events that look like obligations.",
    ),
    "finance.transaction.count": FeatureDefinition(
        key="finance.transaction.count",
        source_domain="finance",
        description="Count of finance transactions recorded.",
    ),
    "finance.spend.total": FeatureDefinition(
        key="finance.spend.total",
        source_domain="finance",
        description="Total absolute spend from finance transactions.",
    ),
    "journal.entry.count": FeatureDefinition(
        key="journal.entry.count",
        source_domain="journal",
        description="Count of journal entries recorded.",
    ),
    "journal.stress.count": FeatureDefinition(
        key="journal.stress.count",
        source_domain="journal",
        description="Count of journal entries tagged as stress/low mood.",
    ),
    "habits.log.count": FeatureDefinition(
        key="habits.log.count",
        source_domain="habits",
        description="Count of habit logs recorded.",
    ),
    "health.sleep_low.count": FeatureDefinition(
        key="health.sleep_low.count",
        source_domain="health",
        description="Count of low-sleep health metrics.",
    ),
    "relationships.interaction.count": FeatureDefinition(
        key="relationships.interaction.count",
        source_domain="relationships",
        description="Count of relationship interactions logged.",
    ),
    "projects.task.completed.count": FeatureDefinition(
        key="projects.task.completed.count",
        source_domain="projects",
        description="Count of project tasks completed.",
    ),
}

SUPPORTED_EVENT_TYPES = {
    CALENDAR_EVENT_CREATED,
    FINANCE_TRANSACTION_CREATED,
    JOURNAL_ENTRY_CREATED,
    HABITS_HABIT_LOGGED,
    HEALTH_METRIC_UPDATED,
    REL_INTERACTION_LOGGED,
    TASK_COMPLETED,
}

OBLIGATION_KEYWORDS = ("rent", "bill", "invoice", "payment", "due", "subscription")
STRESS_TAGS = ("stress", "stressed", "anxious", "overwhelmed", "tired", "sad")


def resolve_event_date(event: EventRecord) -> Optional[date]:
    payload = event.payload or {}
    event_type = event.event_type or ""
    value = None
    if event_type.startswith("calendar.event."):
        value = payload.get("start_time") or payload.get("created_at")
    elif event_type == FINANCE_TRANSACTION_CREATED:
        value = payload.get("occurred_at") or payload.get("created_at")
    elif event_type.startswith("journal.entry."):
        value = payload.get("entry_date") or payload.get("created_at")
    elif event_type == HABITS_HABIT_LOGGED:
        value = payload.get("logged_date")
    elif event_type == HEALTH_METRIC_UPDATED:
        value = payload.get("recorded_at") or payload.get("date")
    elif event_type == REL_INTERACTION_LOGGED:
        value = payload.get("date")
    elif event_type == TASK_COMPLETED:
        value = payload.get("completed_at")
    dt = _parse_datetime(value) or event.created_at
    if isinstance(dt, datetime):
        return dt.date()
    return None


def compute_features_for_user(user_id: int, start_date: date, end_date: date) -> Dict[date, Dict[str, float]]:
    events = (
        EventRecord.query.filter(EventRecord.user_id == user_id)
        .filter(EventRecord.event_type.in_(list(SUPPORTED_EVENT_TYPES)))
        .order_by(EventRecord.created_at.desc())
        .all()
    )
    features_by_date: Dict[date, Dict[str, float]] = {}
    for event in events:
        event_date = resolve_event_date(event)
        if not event_date or event_date < start_date or event_date > end_date:
            continue
        deltas = extract_event_features(event)
        if not deltas:
            continue
        bucket = features_by_date.setdefault(event_date, {})
        for key, value in deltas.items():
            bucket[key] = bucket.get(key, 0.0) + value
    return features_by_date


def store_features_daily(user_id: int, features_by_date: Dict[date, Dict[str, float]]) -> None:
    if not features_by_date:
        return
    for feature_date, features in features_by_date.items():
        for feature_key, feature_value in features.items():
            definition = FEATURE_DEFINITIONS.get(feature_key)
            source_domain = definition.source_domain if definition else feature_key.split(".")[0]
            row = FeatureDaily.query.filter_by(
                user_id=user_id,
                feature_date=feature_date,
                feature_key=feature_key,
                definition_version=FEATURE_VERSION,
            ).first()
            if row:
                row.feature_value = feature_value
                row.updated_at = datetime.utcnow()
            else:
                db.session.add(
                    FeatureDaily(
                        user_id=user_id,
                        feature_date=feature_date,
                        feature_key=feature_key,
                        feature_value=feature_value,
                        source_domain=source_domain,
                        definition_version=FEATURE_VERSION,
                    )
                )
    db.session.commit()


def fetch_window_features(
    user_id: int,
    feature_keys: Iterable[str],
    start_date: date,
    end_date: date,
) -> Dict[str, float]:
    totals = {key: 0.0 for key in feature_keys}
    rows = (
        FeatureDaily.query.filter(FeatureDaily.user_id == user_id)
        .filter(FeatureDaily.feature_key.in_(list(feature_keys)))
        .filter(FeatureDaily.feature_date >= start_date)
        .filter(FeatureDaily.feature_date <= end_date)
        .all()
    )
    for row in rows:
        totals[row.feature_key] = totals.get(row.feature_key, 0.0) + float(row.feature_value or 0.0)
    return totals


def sum_feature(
    user_id: int,
    feature_key: str,
    start_date: date,
    end_date: date,
) -> float:
    total = (
        db.session.query(func.sum(FeatureDaily.feature_value))
        .filter(FeatureDaily.user_id == user_id)
        .filter(FeatureDaily.feature_key == feature_key)
        .filter(FeatureDaily.feature_date >= start_date)
        .filter(FeatureDaily.feature_date <= end_date)
        .scalar()
    )
    return float(total or 0.0)


def extract_event_features(event: EventRecord) -> Dict[str, float]:
    payload = event.payload or {}
    event_type = event.event_type
    features: Dict[str, float] = {}

    if event_type == CALENDAR_EVENT_CREATED:
        features["calendar.event.count"] = 1.0
        title = str(payload.get("title") or "").lower()
        if title and any(keyword in title for keyword in OBLIGATION_KEYWORDS):
            features["calendar.obligation.count"] = 1.0
        start_time = _parse_datetime(payload.get("start_time"))
        if start_time and _is_late_night(start_time):
            features["calendar.event.late_night.count"] = 1.0

    if event_type == FINANCE_TRANSACTION_CREATED:
        features["finance.transaction.count"] = 1.0
        amount = _to_float(payload.get("amount"))
        if amount < 0:
            features["finance.spend.total"] = abs(amount)

    if event_type == JOURNAL_ENTRY_CREATED:
        features["journal.entry.count"] = 1.0
        if _is_stress_entry(payload):
            features["journal.stress.count"] = 1.0

    if event_type == HABITS_HABIT_LOGGED:
        features["habits.log.count"] = 1.0

    if event_type == HEALTH_METRIC_UPDATED:
        metric = str(payload.get("metric") or "").lower()
        value = _to_float(payload.get("value"))
        if metric in {"sleep_hours", "sleep_quality"} and value:
            threshold = 6.0 if metric == "sleep_hours" else 60.0
            if value < threshold:
                features["health.sleep_low.count"] = 1.0

    if event_type == REL_INTERACTION_LOGGED:
        features["relationships.interaction.count"] = 1.0

    if event_type == TASK_COMPLETED:
        features["projects.task.completed.count"] = 1.0

    return features


def _parse_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _is_late_night(dt: datetime) -> bool:
    hour = dt.hour
    return hour >= 21 or hour <= 4


def _is_stress_entry(payload: dict) -> bool:
    mood = payload.get("mood")
    if isinstance(mood, (int, float)) and mood <= 2:
        return True
    if isinstance(mood, str) and mood.strip().lower() in STRESS_TAGS:
        return True
    tags = payload.get("tags") or []
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if isinstance(tags, list):
        for tag in tags:
            if isinstance(tag, str) and tag.strip().lower() in STRESS_TAGS:
                return True
    return False


__all__ = [
    "FEATURE_DEFINITIONS",
    "FEATURE_VERSION",
    "SUPPORTED_EVENT_TYPES",
    "compute_features_for_user",
    "extract_event_features",
    "fetch_window_features",
    "resolve_event_date",
    "store_features_daily",
    "sum_feature",
]
