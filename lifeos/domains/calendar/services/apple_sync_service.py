"""Apple Calendar (iCloud CalDAV) sync service.

Apple Calendar uses CalDAV protocol. For iCloud, users need to generate
an app-specific password at https://appleid.apple.com/

This implementation supports:
1. iCloud Calendar via CalDAV
2. App-specific password authentication (recommended for iCloud)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import defusedxml.ElementTree as ET
import requests
from requests.auth import HTTPBasicAuth

from lifeos.domains.calendar.models.calendar_event import CalendarEvent
from lifeos.domains.calendar.models.oauth_token import CalendarOAuthToken
from lifeos.domains.calendar.services.calendar_service import create_calendar_event
from lifeos.extensions import db

logger = logging.getLogger(__name__)

# iCloud CalDAV endpoints
ICLOUD_CALDAV_URL = "https://caldav.icloud.com"
ICLOUD_PRINCIPAL_URL = f"{ICLOUD_CALDAV_URL}/{{user_id}}/principal/"

# CalDAV XML namespaces
DAV_NS = "DAV:"
CALDAV_NS = "urn:ietf:params:xml:ns:caldav"
APPLE_NS = "http://apple.com/ns/ical/"

NAMESPACES = {
    "D": DAV_NS,
    "C": CALDAV_NS,
    "A": APPLE_NS,
}


class AppleCalendarError(Exception):
    """Base exception for Apple Calendar operations."""

    pass


class AuthenticationError(AppleCalendarError):
    """Raised when authentication fails."""

    pass


class SyncError(AppleCalendarError):
    """Raised when sync operation fails."""

    pass


def save_apple_credentials(
    user_id: int,
    apple_id: str,
    app_password: str,
) -> CalendarOAuthToken:
    """
    Save Apple Calendar credentials for a user.

    Args:
        user_id: User ID
        apple_id: User's Apple ID (email)
        app_password: App-specific password from appleid.apple.com

    Returns:
        Saved token record
    """
    # Store apple_id in refresh_token field (not sensitive)
    # Store app_password in access_token field (encrypted at rest in production)

    token = CalendarOAuthToken.query.filter_by(
        user_id=user_id, provider="apple"
    ).first()

    if token:
        token.access_token = app_password
        token.refresh_token = apple_id  # Store Apple ID here
        token.is_active = True
        token.error_message = None
    else:
        token = CalendarOAuthToken(
            user_id=user_id,
            provider="apple",
            access_token=app_password,
            refresh_token=apple_id,
            is_active=True,
        )
        db.session.add(token)

    db.session.commit()
    return token


def verify_apple_credentials(apple_id: str, app_password: str) -> bool:
    """
    Verify Apple Calendar credentials by making a test request.

    Args:
        apple_id: User's Apple ID
        app_password: App-specific password

    Returns:
        True if credentials are valid
    """
    try:
        # PROPFIND request to verify authentication
        headers = {
            "Content-Type": "application/xml",
            "Depth": "0",
        }

        body = """<?xml version="1.0" encoding="utf-8"?>
        <D:propfind xmlns:D="DAV:">
            <D:prop>
                <D:current-user-principal/>
            </D:prop>
        </D:propfind>"""

        resp = requests.request(
            "PROPFIND",
            ICLOUD_CALDAV_URL,
            headers=headers,
            data=body,
            auth=HTTPBasicAuth(apple_id, app_password),
            timeout=30,
        )

        return resp.status_code in (200, 207)

    except requests.RequestException as e:
        logger.warning(f"Apple credential verification failed: {e}")
        return False


def get_calendars(apple_id: str, app_password: str) -> List[Dict[str, str]]:
    """
    Get list of calendars for the user.

    Args:
        apple_id: User's Apple ID
        app_password: App-specific password

    Returns:
        List of calendar info dicts with 'href', 'name', 'color'
    """
    headers = {
        "Content-Type": "application/xml",
        "Depth": "1",
    }

    body = """<?xml version="1.0" encoding="utf-8"?>
    <D:propfind xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:A="http://apple.com/ns/ical/">
        <D:prop>
            <D:displayname/>
            <D:resourcetype/>
            <A:calendar-color/>
        </D:prop>
    </D:propfind>"""

    try:
        resp = requests.request(
            "PROPFIND",
            f"{ICLOUD_CALDAV_URL}/{apple_id}/calendars/",
            headers=headers,
            data=body,
            auth=HTTPBasicAuth(apple_id, app_password),
            timeout=30,
        )
        resp.raise_for_status()

        calendars = []
        root = ET.fromstring(resp.content)

        for response in root.findall(".//{DAV:}response"):
            href = response.findtext("{DAV:}href", "")
            propstat = response.find("{DAV:}propstat")
            if propstat is None:
                continue

            prop = propstat.find("{DAV:}prop")
            if prop is None:
                continue

            # Check if it's a calendar
            resourcetype = prop.find("{DAV:}resourcetype")
            if (
                resourcetype is None
                or resourcetype.find("{urn:ietf:params:xml:ns:caldav}calendar") is None
            ):
                continue

            name = prop.findtext("{DAV:}displayname", "Untitled")
            color = prop.findtext("{http://apple.com/ns/ical/}calendar-color", "")

            calendars.append(
                {
                    "href": href,
                    "name": name,
                    "color": color[:7] if color else None,  # Strip alpha from #RRGGBBAA
                }
            )

        return calendars

    except requests.RequestException as e:
        logger.error(f"Failed to fetch Apple calendars: {e}")
        raise AppleCalendarError(f"Failed to fetch calendars: {e}") from e


def fetch_calendar_events(
    apple_id: str,
    app_password: str,
    calendar_href: str,
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch events from a specific Apple calendar using REPORT request.

    Args:
        apple_id: User's Apple ID
        app_password: App-specific password
        calendar_href: Calendar path (from get_calendars)
        time_min: Start of time range
        time_max: End of time range

    Returns:
        List of event dicts
    """
    if time_min is None:
        time_min = datetime.utcnow() - timedelta(days=7)
    if time_max is None:
        time_max = datetime.utcnow() + timedelta(days=30)

    headers = {
        "Content-Type": "application/xml",
        "Depth": "1",
    }

    # CalDAV REPORT request for calendar-query
    body = f"""<?xml version="1.0" encoding="utf-8"?>
    <C:calendar-query xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">
        <D:prop>
            <D:getetag/>
            <C:calendar-data/>
        </D:prop>
        <C:filter>
            <C:comp-filter name="VCALENDAR">
                <C:comp-filter name="VEVENT">
                    <C:time-range start="{time_min.strftime('%Y%m%dT%H%M%SZ')}"
                                  end="{time_max.strftime('%Y%m%dT%H%M%SZ')}"/>
                </C:comp-filter>
            </C:comp-filter>
        </C:filter>
    </C:calendar-query>"""

    try:
        url = (
            f"{ICLOUD_CALDAV_URL}{calendar_href}"
            if calendar_href.startswith("/")
            else calendar_href
        )

        resp = requests.request(
            "REPORT",
            url,
            headers=headers,
            data=body,
            auth=HTTPBasicAuth(apple_id, app_password),
            timeout=60,
        )
        resp.raise_for_status()

        events = []
        root = ET.fromstring(resp.content)

        for response in root.findall(".//{DAV:}response"):
            href = response.findtext("{DAV:}href", "")
            etag = response.findtext(".//{DAV:}getetag", "")
            calendar_data = response.findtext(
                ".//{urn:ietf:params:xml:ns:caldav}calendar-data", ""
            )

            if not calendar_data:
                continue

            # Parse iCalendar data
            event = _parse_icalendar(calendar_data, href, etag)
            if event:
                events.append(event)

        return events

    except requests.RequestException as e:
        logger.error(f"Failed to fetch Apple calendar events: {e}")
        raise SyncError(f"Failed to fetch events: {e}") from e


def _parse_icalendar(ical_data: str, href: str, etag: str) -> Optional[Dict[str, Any]]:
    """
    Parse iCalendar VEVENT data into a dict.

    Simple parser for common fields. For production, consider using
    the 'icalendar' library.
    """
    event = {
        "href": href,
        "etag": etag,
        "external_id": href,
    }

    lines = ical_data.replace("\r\n ", "").replace("\n ", "").split("\n")
    in_vevent = False

    for line in lines:
        line = line.strip()

        if line == "BEGIN:VEVENT":
            in_vevent = True
            continue
        elif line == "END:VEVENT":
            in_vevent = False
            continue

        if not in_vevent:
            continue

        if ":" not in line:
            continue

        # Handle property parameters (e.g., DTSTART;VALUE=DATE:20231225)
        prop_part, value = line.split(":", 1)
        prop_name = prop_part.split(";")[0]

        if prop_name == "UID":
            event["external_id"] = value
        elif prop_name == "SUMMARY":
            event["title"] = value
        elif prop_name == "DESCRIPTION":
            event["description"] = value
        elif prop_name == "LOCATION":
            event["location"] = value
        elif prop_name == "DTSTART":
            event["start_time"], event["all_day"] = _parse_ical_datetime(
                value, prop_part
            )
        elif prop_name == "DTEND":
            event["end_time"], _ = _parse_ical_datetime(value, prop_part)

    # Validate required fields
    if "title" not in event or "start_time" not in event:
        return None

    return event


def _parse_ical_datetime(value: str, prop_part: str) -> Tuple[datetime, bool]:
    """Parse iCalendar datetime value."""
    is_date_only = "VALUE=DATE" in prop_part

    if is_date_only:
        # Date only: YYYYMMDD
        dt = datetime.strptime(value[:8], "%Y%m%d")
        return dt, True
    else:
        # DateTime: YYYYMMDDTHHMMSS or YYYYMMDDTHHMMSSZ
        value = value.rstrip("Z")
        try:
            dt = datetime.strptime(value[:15], "%Y%m%dT%H%M%S")
        except ValueError:
            dt = datetime.strptime(value[:8], "%Y%m%d")
        return dt, False


def disconnect_apple_calendar(user_id: int) -> bool:
    """
    Disconnect Apple Calendar for a user.

    Args:
        user_id: User ID

    Returns:
        True if disconnected, False if no connection existed
    """
    token = CalendarOAuthToken.query.filter_by(
        user_id=user_id, provider="apple"
    ).first()

    if not token:
        return False

    db.session.delete(token)
    db.session.commit()
    return True


def sync_apple_calendar(user_id: int) -> Dict[str, int]:
    """
    Sync events from Apple Calendar for a user.

    Args:
        user_id: User ID

    Returns:
        Dict with counts: {"created": N, "updated": N, "deleted": N}
    """
    token = CalendarOAuthToken.query.filter_by(
        user_id=user_id, provider="apple", is_active=True
    ).first()

    if not token:
        raise AppleCalendarError("No valid Apple Calendar connection")

    apple_id = token.refresh_token  # Apple ID stored here
    app_password = token.access_token

    if not apple_id or not app_password:
        raise AppleCalendarError("Invalid Apple credentials")

    stats = {"created": 0, "updated": 0, "deleted": 0}

    try:
        # Get all calendars
        calendars = get_calendars(apple_id, app_password)

        for calendar in calendars:
            events = fetch_calendar_events(
                apple_id,
                app_password,
                calendar["href"],
            )

            for event_data in events:
                external_id = event_data.get("external_id")
                if not external_id:
                    continue

                existing = CalendarEvent.query.filter_by(
                    user_id=user_id, external_id=external_id, source="sync_apple"
                ).first()

                if existing:
                    # Update existing
                    existing.title = event_data.get("title", existing.title)
                    existing.description = event_data.get("description")
                    existing.location = event_data.get("location")
                    existing.start_time = event_data.get(
                        "start_time", existing.start_time
                    )
                    existing.end_time = event_data.get("end_time")
                    existing.all_day = event_data.get("all_day", False)
                    existing.updated_at = datetime.utcnow()
                    stats["updated"] += 1
                else:
                    # Create new
                    create_calendar_event(
                        user_id=user_id,
                        title=event_data.get("title", "Untitled"),
                        start_time=event_data["start_time"],
                        end_time=event_data.get("end_time"),
                        description=event_data.get("description"),
                        location=event_data.get("location"),
                        all_day=event_data.get("all_day", False),
                        source="sync_apple",
                        external_id=external_id,
                        color=calendar.get("color"),
                    )
                    stats["created"] += 1

        # Update sync state
        token.last_sync_at = datetime.utcnow()
        token.error_message = None
        db.session.commit()

        logger.info(f"Apple Calendar sync for user {user_id}: {stats}")
        return stats

    except (AppleCalendarError, requests.RequestException) as e:
        token.error_message = str(e)[:500]
        db.session.commit()
        raise


def get_apple_sync_status(user_id: int) -> Dict[str, Any]:
    """
    Get Apple Calendar sync status for a user.

    Args:
        user_id: User ID

    Returns:
        Status dict with connection info
    """
    token = CalendarOAuthToken.query.filter_by(
        user_id=user_id, provider="apple"
    ).first()

    if not token:
        return {
            "connected": False,
            "provider": "apple",
        }

    return {
        "connected": True,
        "provider": "apple",
        "is_active": token.is_active,
        "apple_id": token.refresh_token,  # Apple ID (not sensitive)
        "last_sync_at": token.last_sync_at.isoformat() if token.last_sync_at else None,
        "error": token.error_message,
        "created_at": token.created_at.isoformat(),
    }
