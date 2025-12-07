"""Calendar API controllers."""

from __future__ import annotations

from flask import Blueprint, jsonify, redirect, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.calendar.schemas import (
    CalendarEventCreate,
    CalendarEventListParams,
    CalendarEventUpdate,
    InterpretationUpdate,
)
from lifeos.domains.calendar.services import (
    create_calendar_event,
    delete_calendar_event,
    get_calendar_event,
    get_pending_interpretations,
    list_calendar_events,
    update_calendar_event,
    update_interpretation_status,
)
from lifeos.domains.calendar.services.google_sync_service import (
    GoogleCalendarError,
    disconnect_google_calendar,
    exchange_code_for_tokens,
    get_authorization_url,
    get_sync_status,
    save_oauth_token,
    sync_google_calendar,
)
from lifeos.extensions import limiter

calendar_api_bp = Blueprint("calendar_api", __name__)


# ==================== Calendar Events ====================


@calendar_api_bp.get("/events")
@jwt_required()
@limiter.limit("240/minute")
def list_events():
    """
    List calendar events with optional date range filter.
    
    Query Parameters:
    - start_date: ISO datetime (optional)
    - end_date: ISO datetime (optional)
    - source: 'manual', 'sync_google', 'sync_apple', 'api' (optional)
    - limit: max results (default 50, max 500)
    - offset: pagination offset (default 0)
    """
    user_id = int(get_jwt_identity())

    try:
        params = CalendarEventListParams.model_validate(request.args)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    events = list_calendar_events(
        user_id=user_id,
        start_date=params.start_date,
        end_date=params.end_date,
        source=params.source,
        limit=params.limit,
        offset=params.offset,
    )

    return jsonify({
        "ok": True,
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat() if e.end_time else None,
                "all_day": e.all_day,
                "location": e.location,
                "source": e.source,
                "color": e.color,
                "is_private": e.is_private,
                "tags": e.tags,
                "duration_minutes": e.duration_minutes,
                "created_at": e.created_at.isoformat(),
            }
            for e in events
        ],
    }), 200


@calendar_api_bp.get("/events/<int:event_id>")
@jwt_required()
@limiter.limit("240/minute")
def get_event(event_id: int):
    """Get a single calendar event with its interpretations."""
    user_id = int(get_jwt_identity())

    event = get_calendar_event(user_id, event_id)
    if not event:
        return jsonify({"ok": False, "error": "not_found"}), 404

    return jsonify({
        "ok": True,
        "event": {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "all_day": event.all_day,
            "location": event.location,
            "source": event.source,
            "external_id": event.external_id,
            "color": event.color,
            "is_private": event.is_private,
            "tags": event.tags,
            "duration_minutes": event.duration_minutes,
            "created_at": event.created_at.isoformat(),
            "updated_at": event.updated_at.isoformat(),
            "interpretations": [
                {
                    "id": i.id,
                    "domain": i.domain,
                    "record_type": i.record_type,
                    "record_id": i.record_id,
                    "confidence_score": float(i.confidence_score),
                    "status": i.status,
                    "classification_data": i.classification_data,
                }
                for i in event.interpretations
            ],
        },
    }), 200


@calendar_api_bp.post("/events")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
@limiter.limit("120/minute")
def create_event():
    """
    Create a new calendar event.
    
    Request Body:
    {
      "title": "Lunch with John",
      "start_time": "2025-12-07T12:00:00",
      "end_time": "2025-12-07T13:00:00",
      "description": "Discuss project plans",
      "location": "Cafe XYZ",
      "all_day": false,
      "tags": ["meeting", "work"]
    }
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}

    try:
        data = CalendarEventCreate.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        event = create_calendar_event(
            user_id=user_id,
            title=data.title,
            start_time=data.start_time,
            end_time=data.end_time,
            description=data.description,
            location=data.location,
            all_day=data.all_day,
            color=data.color,
            is_private=data.is_private,
            tags=data.tags,
            metadata=data.metadata,
        )

        return jsonify({
            "ok": True,
            "event": {
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "created_at": event.created_at.isoformat(),
            },
        }), 201

    except ValueError as exc:
        code = str(exc)
        if code in {"invalid_title", "title_too_long"}:
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400


@calendar_api_bp.patch("/events/<int:event_id>")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
@limiter.limit("120/minute")
def update_event(event_id: int):
    """Update an existing calendar event."""
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}

    try:
        data = CalendarEventUpdate.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        event = update_calendar_event(
            user_id=user_id,
            event_id=event_id,
            title=data.title,
            description=data.description,
            start_time=data.start_time,
            end_time=data.end_time,
            all_day=data.all_day,
            location=data.location,
            color=data.color,
            is_private=data.is_private,
            tags=data.tags,
            metadata=data.metadata,
        )

        return jsonify({
            "ok": True,
            "event": {
                "id": event.id,
                "title": event.title,
                "updated_at": event.updated_at.isoformat(),
            },
        }), 200

    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        if code == "invalid_title":
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400


@calendar_api_bp.delete("/events/<int:event_id>")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
@limiter.limit("60/minute")
def delete_event(event_id: int):
    """Delete a calendar event."""
    user_id = int(get_jwt_identity())

    try:
        delete_calendar_event(user_id, event_id)
        return jsonify({"ok": True}), 200
    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400


# ==================== Interpretations ====================


@calendar_api_bp.get("/interpretations/pending")
@jwt_required()
@limiter.limit("240/minute")
def list_pending_interpretations():
    """
    List pending interpretations awaiting user review.
    
    Query Parameters:
    - domain: filter by domain (optional)
    - limit: max results (default 50)
    - offset: pagination offset (default 0)
    """
    user_id = int(get_jwt_identity())
    domain = request.args.get("domain")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    interpretations = get_pending_interpretations(
        user_id=user_id,
        domain=domain,
        limit=min(limit, 500),
        offset=offset,
    )

    return jsonify({
        "ok": True,
        "interpretations": [
            {
                "id": i.id,
                "calendar_event_id": i.calendar_event_id,
                "domain": i.domain,
                "record_type": i.record_type,
                "confidence_score": float(i.confidence_score),
                "status": i.status,
                "classification_data": i.classification_data,
                "created_at": i.created_at.isoformat(),
            }
            for i in interpretations
        ],
    }), 200


@calendar_api_bp.patch("/interpretations/<int:interpretation_id>")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
@limiter.limit("120/minute")
def update_interpretation(interpretation_id: int):
    """
    Update interpretation status (confirm, reject, ignore).
    
    Request Body:
    {
      "status": "confirmed" | "rejected" | "ignored"
    }
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}

    try:
        data = InterpretationUpdate.model_validate(payload)
    except Exception:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        interpretation = update_interpretation_status(
            user_id=user_id,
            interpretation_id=interpretation_id,
            status=data.status,
        )

        return jsonify({
            "ok": True,
            "interpretation": {
                "id": interpretation.id,
                "status": interpretation.status,
                "updated_at": interpretation.updated_at.isoformat(),
            },
        }), 200

    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        if code == "invalid_status":
            return jsonify({"ok": False, "error": code}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400


# ==================== Google Calendar OAuth ====================


@calendar_api_bp.get("/oauth/google/authorize")
@jwt_required()
def google_oauth_authorize():
    """
    Initiate Google Calendar OAuth flow.
    
    Returns a redirect URL for the user to authorize access.
    """
    user_id = int(get_jwt_identity())
    auth_url = get_authorization_url(user_id, state=str(user_id))
    return jsonify({"ok": True, "authorization_url": auth_url}), 200


@calendar_api_bp.get("/oauth/google/callback")
def google_oauth_callback():
    """
    Handle Google OAuth callback.
    
    Exchanges code for tokens and redirects to calendar page.
    """
    code = request.args.get("code")
    state = request.args.get("state")
    error = request.args.get("error")
    
    if error:
        return redirect(f"/calendar?error={error}")
    
    if not code or not state:
        return redirect("/calendar?error=invalid_callback")
    
    try:
        user_id = int(state)
        token_data = exchange_code_for_tokens(code)
        save_oauth_token(user_id, token_data)
        return redirect("/calendar?connected=google")
    except (ValueError, GoogleCalendarError) as e:
        return redirect(f"/calendar?error={str(e)[:50]}")


@calendar_api_bp.get("/oauth/google/status")
@jwt_required()
def google_oauth_status():
    """
    Get Google Calendar connection status.
    """
    user_id = int(get_jwt_identity())
    status = get_sync_status(user_id)
    return jsonify({"ok": True, **status}), 200


@calendar_api_bp.post("/oauth/google/disconnect")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
def google_oauth_disconnect():
    """
    Disconnect Google Calendar integration.
    """
    user_id = int(get_jwt_identity())
    disconnected = disconnect_google_calendar(user_id)
    return jsonify({"ok": True, "disconnected": disconnected}), 200


@calendar_api_bp.post("/sync/google")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
@limiter.limit("10/minute")
def trigger_google_sync():
    """
    Manually trigger Google Calendar sync.
    """
    user_id = int(get_jwt_identity())
    
    try:
        stats = sync_google_calendar(user_id)
        return jsonify({"ok": True, **stats}), 200
    except GoogleCalendarError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ==================== Apple Calendar (CalDAV) ====================


@calendar_api_bp.post("/oauth/apple/connect")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
def apple_connect():
    """
    Connect Apple Calendar using app-specific password.
    
    Request Body:
    {
        "apple_id": "user@icloud.com",
        "app_password": "xxxx-xxxx-xxxx-xxxx"
    }
    
    Users must generate an app-specific password at:
    https://appleid.apple.com/account/manage
    """
    from lifeos.domains.calendar.services.apple_sync_service import (
        AppleCalendarError,
        save_apple_credentials,
        verify_apple_credentials,
    )
    
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    
    apple_id = payload.get("apple_id", "").strip()
    app_password = payload.get("app_password", "").strip()
    
    if not apple_id or not app_password:
        return jsonify({"ok": False, "error": "apple_id and app_password required"}), 400
    
    # Verify credentials
    if not verify_apple_credentials(apple_id, app_password):
        return jsonify({"ok": False, "error": "invalid_credentials"}), 401
    
    # Save credentials
    save_apple_credentials(user_id, apple_id, app_password)
    
    return jsonify({"ok": True, "message": "Apple Calendar connected"}), 200


@calendar_api_bp.get("/oauth/apple/status")
@jwt_required()
def apple_status():
    """
    Get Apple Calendar connection status.
    """
    from lifeos.domains.calendar.services.apple_sync_service import get_apple_sync_status
    
    user_id = int(get_jwt_identity())
    status = get_apple_sync_status(user_id)
    return jsonify({"ok": True, **status}), 200


@calendar_api_bp.post("/oauth/apple/disconnect")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
def apple_disconnect():
    """
    Disconnect Apple Calendar integration.
    """
    from lifeos.domains.calendar.services.apple_sync_service import disconnect_apple_calendar
    
    user_id = int(get_jwt_identity())
    disconnected = disconnect_apple_calendar(user_id)
    return jsonify({"ok": True, "disconnected": disconnected}), 200


@calendar_api_bp.post("/sync/apple")
@jwt_required()
@csrf_protected
@require_roles({"calendar:write"})
@limiter.limit("10/minute")
def trigger_apple_sync():
    """
    Manually trigger Apple Calendar sync.
    """
    from lifeos.domains.calendar.services.apple_sync_service import (
        AppleCalendarError,
        sync_apple_calendar,
    )
    
    user_id = int(get_jwt_identity())
    
    try:
        stats = sync_apple_calendar(user_id)
        return jsonify({"ok": True, **stats}), 200
    except AppleCalendarError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
