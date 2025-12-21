"""Calendar domain tasks: periodic sync and maintenance."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger(__name__)


def sync_all_google_calendars() -> Dict[str, int]:
    """
    Sync all active Google Calendar connections.

    Call this periodically (e.g., every 15 minutes via cron or scheduler).

    Returns:
        Dict with total stats across all users
    """
    from lifeos.domains.calendar.models.oauth_token import CalendarOAuthToken
    from lifeos.domains.calendar.services.google_sync_service import (
        GoogleCalendarError,
        sync_google_calendar,
    )

    active_tokens = CalendarOAuthToken.query.filter_by(
        provider="google",
        is_active=True,
    ).all()

    total_stats = {
        "synced_users": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "errors": 0,
    }

    for token in active_tokens:
        try:
            stats = sync_google_calendar(token.user_id)
            total_stats["synced_users"] += 1
            total_stats["created"] += stats["created"]
            total_stats["updated"] += stats["updated"]
            total_stats["deleted"] += stats["deleted"]
        except GoogleCalendarError as e:
            logger.warning(f"Sync failed for user {token.user_id}: {e}")
            total_stats["errors"] += 1

    logger.info(f"Google Calendar bulk sync complete: {total_stats}")
    return total_stats


def sync_google_calendar_for_user(user_id: int) -> dict:
    """
    Sync calendar events from Google Calendar for a specific user.

    Args:
        user_id: User ID to sync

    Returns:
        Sync stats dict
    """
    from lifeos.domains.calendar.services.google_sync_service import (
        sync_google_calendar,
    )

    return sync_google_calendar(user_id)


def sync_apple_calendar_for_user(user_id: int) -> dict:
    """
    Sync calendar events from Apple Calendar for a specific user.

    Args:
        user_id: User ID to sync

    Returns:
        Sync stats dict
    """
    from lifeos.domains.calendar.services.apple_sync_service import sync_apple_calendar

    return sync_apple_calendar(user_id)


def sync_all_apple_calendars() -> Dict[str, int]:
    """
    Sync all active Apple Calendar connections.

    Call this periodically (e.g., every 15 minutes via cron or scheduler).

    Returns:
        Dict with total stats across all users
    """
    from lifeos.domains.calendar.models.oauth_token import CalendarOAuthToken
    from lifeos.domains.calendar.services.apple_sync_service import (
        AppleCalendarError,
        sync_apple_calendar,
    )

    active_tokens = CalendarOAuthToken.query.filter_by(
        provider="apple",
        is_active=True,
    ).all()

    total_stats = {
        "synced_users": 0,
        "created": 0,
        "updated": 0,
        "deleted": 0,
        "errors": 0,
    }

    for token in active_tokens:
        try:
            stats = sync_apple_calendar(token.user_id)
            total_stats["synced_users"] += 1
            total_stats["created"] += stats["created"]
            total_stats["updated"] += stats["updated"]
            total_stats["deleted"] += stats.get("deleted", 0)
        except AppleCalendarError as e:
            logger.warning(f"Apple sync failed for user {token.user_id}: {e}")
            total_stats["errors"] += 1

    logger.info(f"Apple Calendar bulk sync complete: {total_stats}")
    return total_stats


def cleanup_old_interpretations(days: int = 90) -> int:
    """
    Cleanup rejected/ignored interpretations older than N days.

    Returns count of deleted records.
    """
    from lifeos.domains.calendar.models.calendar_event import (
        CalendarEventInterpretation,
    )
    from lifeos.extensions import db

    cutoff = datetime.utcnow() - timedelta(days=days)

    deleted = CalendarEventInterpretation.query.filter(
        CalendarEventInterpretation.status.in_(["rejected", "ignored"]),
        CalendarEventInterpretation.updated_at < cutoff,
    ).delete(synchronize_session=False)

    db.session.commit()
    return deleted


def cleanup_stale_oauth_tokens(days: int = 30) -> int:
    """
    Cleanup inactive OAuth tokens that haven't synced in N days.

    Args:
        days: Days of inactivity before cleanup

    Returns:
        Count of deleted tokens
    """
    from lifeos.domains.calendar.models.oauth_token import CalendarOAuthToken
    from lifeos.extensions import db

    cutoff = datetime.utcnow() - timedelta(days=days)

    deleted = CalendarOAuthToken.query.filter(
        CalendarOAuthToken.is_active.is_(False),
        CalendarOAuthToken.updated_at < cutoff,
    ).delete(synchronize_session=False)

    db.session.commit()
    logger.info(f"Cleaned up {deleted} stale OAuth tokens")
    return deleted
