"""Google Calendar OAuth and sync service."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests
from flask import current_app

from lifeos.domains.calendar.models.calendar_event import CalendarEvent
from lifeos.domains.calendar.models.oauth_token import CalendarOAuthToken
from lifeos.domains.calendar.services.calendar_service import create_calendar_event
from lifeos.extensions import db

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"


class GoogleCalendarError(Exception):
    """Base exception for Google Calendar operations."""

    pass


class TokenRefreshError(GoogleCalendarError):
    """Raised when token refresh fails."""

    pass


class SyncError(GoogleCalendarError):
    """Raised when sync operation fails."""

    pass


def get_authorization_url(user_id: int, state: Optional[str] = None) -> str:
    """
    Generate Google OAuth authorization URL.

    Args:
        user_id: User initiating the OAuth flow
        state: Optional state parameter for CSRF protection

    Returns:
        Authorization URL to redirect user to
    """
    config = current_app.config

    params = {
        "client_id": config["GOOGLE_CLIENT_ID"],
        "redirect_uri": config["GOOGLE_REDIRECT_URI"],
        "response_type": "code",
        "scope": " ".join(config["GOOGLE_CALENDAR_SCOPES"]),
        "access_type": "offline",  # Get refresh token
        "prompt": "consent",  # Force consent to get refresh token
        "state": state or str(user_id),
    }

    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
    """
    Exchange authorization code for access and refresh tokens.

    Args:
        code: Authorization code from OAuth callback

    Returns:
        Token response dict with access_token, refresh_token, expires_in

    Raises:
        GoogleCalendarError: If token exchange fails
    """
    config = current_app.config

    payload = {
        "client_id": config["GOOGLE_CLIENT_ID"],
        "client_secret": config["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": config["GOOGLE_REDIRECT_URI"],
        "grant_type": "authorization_code",
        "code": code,
    }

    try:
        resp = requests.post(GOOGLE_TOKEN_URL, data=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"Token exchange failed: {e}")
        raise GoogleCalendarError(f"Failed to exchange code: {e}") from e


def refresh_access_token(oauth_token: CalendarOAuthToken) -> CalendarOAuthToken:
    """
    Refresh an expired access token.

    Args:
        oauth_token: Token record with refresh_token

    Returns:
        Updated token record

    Raises:
        TokenRefreshError: If refresh fails
    """
    if not oauth_token.refresh_token:
        raise TokenRefreshError("No refresh token available")

    config = current_app.config

    payload = {
        "client_id": config["GOOGLE_CLIENT_ID"],
        "client_secret": config["GOOGLE_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": oauth_token.refresh_token,
    }

    try:
        resp = requests.post(GOOGLE_TOKEN_URL, data=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        oauth_token.access_token = data["access_token"]
        oauth_token.expires_at = datetime.utcnow() + timedelta(
            seconds=data.get("expires_in", 3600)
        )
        oauth_token.error_message = None
        db.session.commit()

        return oauth_token

    except requests.RequestException as e:
        logger.error(f"Token refresh failed for user {oauth_token.user_id}: {e}")
        oauth_token.error_message = str(e)
        oauth_token.is_active = False
        db.session.commit()
        raise TokenRefreshError(f"Failed to refresh token: {e}") from e


def save_oauth_token(user_id: int, token_data: Dict[str, Any]) -> CalendarOAuthToken:
    """
    Save or update OAuth token for a user.

    Args:
        user_id: User ID
        token_data: Token response from Google

    Returns:
        Saved token record
    """
    expires_at = None
    if "expires_in" in token_data:
        expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

    # Find existing or create new
    token = CalendarOAuthToken.query.filter_by(
        user_id=user_id, provider="google"
    ).first()

    if token:
        token.access_token = token_data["access_token"]
        token.refresh_token = token_data.get("refresh_token", token.refresh_token)
        token.expires_at = expires_at
        token.is_active = True
        token.error_message = None
    else:
        token = CalendarOAuthToken(
            user_id=user_id,
            provider="google",
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=expires_at,
            is_active=True,
        )
        db.session.add(token)

    db.session.commit()
    return token


def get_valid_token(user_id: int) -> Optional[CalendarOAuthToken]:
    """
    Get a valid (non-expired) token for the user, refreshing if needed.

    Args:
        user_id: User ID

    Returns:
        Valid token or None if unavailable
    """
    token = CalendarOAuthToken.query.filter_by(
        user_id=user_id, provider="google", is_active=True
    ).first()

    if not token:
        return None

    if token.is_expired:
        try:
            token = refresh_access_token(token)
        except TokenRefreshError:
            return None

    return token


def disconnect_google_calendar(user_id: int) -> bool:
    """
    Disconnect Google Calendar for a user.

    Args:
        user_id: User ID

    Returns:
        True if disconnected, False if no connection existed
    """
    token = CalendarOAuthToken.query.filter_by(
        user_id=user_id, provider="google"
    ).first()

    if not token:
        return False

    db.session.delete(token)
    db.session.commit()
    return True


def fetch_google_events(
    oauth_token: CalendarOAuthToken,
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
    max_results: int = 250,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Fetch events from Google Calendar API.

    Args:
        oauth_token: Valid OAuth token
        time_min: Start of time range (default: now)
        time_max: End of time range (default: 30 days from now)
        max_results: Maximum events to fetch

    Returns:
        Tuple of (events list, next sync token)

    Raises:
        SyncError: If API request fails
    """
    if time_min is None:
        time_min = datetime.utcnow() - timedelta(days=7)
    if time_max is None:
        time_max = datetime.utcnow() + timedelta(days=30)

    headers = {
        "Authorization": f"Bearer {oauth_token.access_token}",
    }

    params: Dict[str, Any] = {
        "maxResults": max_results,
        "singleEvents": "true",
        "orderBy": "startTime",
        "timeMin": time_min.isoformat() + "Z",
        "timeMax": time_max.isoformat() + "Z",
    }

    # Use sync token for incremental sync if available
    if oauth_token.sync_token:
        params = {"syncToken": oauth_token.sync_token}

    try:
        resp = requests.get(
            f"{GOOGLE_CALENDAR_API}/calendars/primary/events",
            headers=headers,
            params=params,
            timeout=30,
        )

        # Handle invalid sync token - full sync needed
        if resp.status_code == 410:
            logger.info(
                f"Sync token expired for user {oauth_token.user_id}, performing full sync"
            )
            oauth_token.sync_token = None
            db.session.commit()
            return fetch_google_events(oauth_token, time_min, time_max, max_results)

        resp.raise_for_status()
        data = resp.json()

        events = data.get("items", [])
        next_sync_token = data.get("nextSyncToken")

        return events, next_sync_token

    except requests.RequestException as e:
        logger.error(
            f"Failed to fetch Google events for user {oauth_token.user_id}: {e}"
        )
        raise SyncError(f"Failed to fetch events: {e}") from e


def sync_google_calendar(user_id: int) -> Dict[str, int]:
    """
    Sync events from Google Calendar for a user.

    Creates/updates/deletes local CalendarEvent records to match Google Calendar.

    Args:
        user_id: User ID

    Returns:
        Dict with counts: {"created": N, "updated": N, "deleted": N}

    Raises:
        GoogleCalendarError: If sync fails
    """
    token = get_valid_token(user_id)
    if not token:
        raise GoogleCalendarError("No valid Google Calendar connection")

    events, next_sync_token = fetch_google_events(token)

    stats = {"created": 0, "updated": 0, "deleted": 0}

    for g_event in events:
        external_id = g_event.get("id")
        if not external_id:
            continue

        # Check if event was deleted (cancelled)
        if g_event.get("status") == "cancelled":
            existing = CalendarEvent.query.filter_by(
                user_id=user_id, external_id=external_id, source="sync_google"
            ).first()
            if existing:
                db.session.delete(existing)
                stats["deleted"] += 1
            continue

        # Parse event times
        start_data = g_event.get("start", {})
        end_data = g_event.get("end", {})

        all_day = "date" in start_data

        if all_day:
            start_time = datetime.fromisoformat(start_data["date"])
            end_time = (
                datetime.fromisoformat(end_data["date"])
                if end_data.get("date")
                else None
            )
        else:
            start_str = start_data.get("dateTime", "")
            end_str = end_data.get("dateTime", "")
            start_time = (
                datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                if start_str
                else None
            )
            end_time = (
                datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                if end_str
                else None
            )

        if not start_time:
            continue

        title = g_event.get("summary", "Untitled Event")
        description = g_event.get("description")
        location = g_event.get("location")

        # Find existing or create
        existing = CalendarEvent.query.filter_by(
            user_id=user_id, external_id=external_id, source="sync_google"
        ).first()

        if existing:
            # Update existing event
            existing.title = title
            existing.description = description
            existing.location = location
            existing.start_time = start_time
            existing.end_time = end_time
            existing.all_day = all_day
            existing.updated_at = datetime.utcnow()
            stats["updated"] += 1
        else:
            # Create new event (use service to trigger interpreter)
            create_calendar_event(
                user_id=user_id,
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                location=location,
                all_day=all_day,
                source="sync_google",
                external_id=external_id,
            )
            stats["created"] += 1

    # Update sync state
    if next_sync_token:
        token.sync_token = next_sync_token
    token.last_sync_at = datetime.utcnow()
    token.error_message = None
    db.session.commit()

    logger.info(f"Google Calendar sync for user {user_id}: {stats}")
    return stats


def get_sync_status(user_id: int) -> Dict[str, Any]:
    """
    Get Google Calendar sync status for a user.

    Args:
        user_id: User ID

    Returns:
        Status dict with connection info
    """
    token = CalendarOAuthToken.query.filter_by(
        user_id=user_id, provider="google"
    ).first()

    if not token:
        return {
            "connected": False,
            "provider": "google",
        }

    return {
        "connected": True,
        "provider": "google",
        "is_active": token.is_active,
        "last_sync_at": token.last_sync_at.isoformat() if token.last_sync_at else None,
        "error": token.error_message,
        "created_at": token.created_at.isoformat(),
    }
