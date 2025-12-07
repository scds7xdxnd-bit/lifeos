# LifeOS Calendar-First Architecture Update

**Role:** Backend Implementation Handoff
**Scope:** Calendar domain, Event interpreter, Inferred records workflow
**Status:** Implemented (pending test runner verification)

---

## 1) Context & Goals

This update implements the **Calendar-First Architecture** initiative, which positions the calendar as the primary data capture point for all life domains. The key concepts:

- **Calendar as Hub:** Users manage their schedule naturally; the system infers domain records from events.
- **Interpreter Layer:** A core component classifies calendar events into target domains (finance, health, habits, skills, projects, relationships).
- **Inferred Records:** Low-friction data entry where users confirm or reject system-generated records.
- **Confidence Scoring:** Classification confidence determines whether records are auto-created or queued for review.

## 2) New Components

### 2.1 Calendar Domain (`lifeos/domains/calendar/`)

| File | Purpose |
|------|---------|
| `models/calendar_event.py` | `CalendarEvent` and `CalendarEventInterpretation` SQLAlchemy models |
| `events.py` | Event catalog: `calendar.event.created`, `calendar.event.updated`, `calendar.interpretation.confirmed`, etc. |
| `schemas/__init__.py` | Pydantic schemas for request/response validation |
| `services/calendar_service.py` | CRUD operations, interpretation confirmation/rejection |
| `controllers/calendar_api.py` | REST API blueprint (`/api/calendar`) |
| `controllers/calendar_pages.py` | HTML page blueprint (`/calendar`) - placeholder |
| `mappers.py` | DTO converters for API responses |
| `tasks.py` | Background sync tasks placeholder |

### 2.2 Interpreter Layer (`lifeos/core/interpreter/`)

| File | Purpose |
|------|---------|
| `constants.py` | Domain identifiers, record types, thresholds (`MINIMUM_CONFIDENCE_THRESHOLD=0.5`) |
| `classification_rules.py` | Pattern-based classification with regex keywords per domain |
| `calendar_interpreter.py` | Main interpreter class, subscribes to calendar events, creates interpretations |
| `domain_adapters.py` | Abstract adapter pattern for creating inferred records in target domains |

### 2.3 Migration

- `20251206_calendar_initial.py`: Creates `calendar_event` and `calendar_event_interpretation` tables with indexes.

## 3) Data Model

### CalendarEvent

```python
class CalendarEvent(db.Model):
    id: int                  # PK
    user_id: int             # FK → user.id
    title: str               # Event title (max 255)
    description: str | None  # Optional details
    start_time: datetime     # Required
    end_time: datetime | None
    all_day: bool            # Default False
    location: str | None     # Max 512
    source: str              # 'manual', 'sync_google', 'sync_apple', 'api'
    external_id: str | None  # For sync deduplication
    recurrence_rule: str | None  # Future: RRULE support
    color: str | None        # UI customization
    is_private: bool         # Default False
    tags: list               # JSON array
    metadata_: dict          # JSON object
    created_at: datetime
    updated_at: datetime
```

### CalendarEventInterpretation

```python
class CalendarEventInterpretation(db.Model):
    id: int                    # PK
    calendar_event_id: int     # FK → calendar_event.id
    user_id: int               # FK → user.id
    domain: str                # 'finance', 'health', 'habits', etc.
    record_type: str           # 'transaction', 'workout', 'meal', etc.
    record_id: int | None      # FK to domain record if created
    confidence_score: float    # 0.0 - 1.0
    status: str                # 'inferred', 'confirmed', 'rejected'
    classification_data: dict  # Extracted fields
    created_at: datetime
    updated_at: datetime
```

## 4) API Endpoints

All endpoints require JWT authentication unless noted.

### Calendar Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendar/events` | List events (query: `start_date`, `end_date`) |
| POST | `/api/calendar/events` | Create event |
| GET | `/api/calendar/events/<id>` | Get single event |
| PUT | `/api/calendar/events/<id>` | Update event |
| DELETE | `/api/calendar/events/<id>` | Delete event |

### Interpretations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendar/interpretations` | List pending interpretations |
| POST | `/api/calendar/interpretations/<id>/confirm` | Confirm and create domain record |
| POST | `/api/calendar/interpretations/<id>/reject` | Reject interpretation |

## 5) Classification Flow

1. User creates/updates a calendar event (via API or sync)
2. `calendar.event.created` event emitted to event bus
3. `CalendarInterpreter.on_calendar_event()` receives event
4. `classify_event()` analyzes title, description, location against domain rules
5. Returns list of `{domain, record_type, confidence_score, extracted_data}`
6. For each classification above `MINIMUM_CONFIDENCE_THRESHOLD` (0.5):
   - Creates `CalendarEventInterpretation` record
   - If confidence ≥ 0.7, creates inferred record in target domain via adapter
7. User reviews pending interpretations and confirms/rejects

### Classification Rules

The classifier uses keyword patterns per domain:

| Domain | Keywords (sample) | Base Confidence |
|--------|------------------|-----------------|
| Health/Workout | gym, workout, run, yoga, fitness | 0.80 |
| Health/Meal | breakfast, lunch, dinner, restaurant | 0.75 |
| Finance | buy, pay, shopping, expense, bill | 0.70 |
| Skills | practice, lesson, class, tutorial | 0.70 |
| Relationships | meet, dinner with, coffee with | 0.70 |
| Projects | work, project, meeting, deadline | 0.65 |
| Habits | routine, meditation, journal | 0.60 |

Confidence is boosted by:
- Location keywords matching domain patterns (+0.10)
- Person name extraction for relationships (+0.15)

## 6) Integration Points

### App Factory Registration

```python
# lifeos/__init__.py
from lifeos.domains.calendar.controllers.calendar_api import calendar_api_bp
from lifeos.domains.calendar.controllers.calendar_pages import calendar_pages_bp
from lifeos.core.interpreter import calendar_interpreter

app.register_blueprint(calendar_api_bp, url_prefix="/api/calendar")
app.register_blueprint(calendar_pages_bp, url_prefix="/calendar")
calendar_interpreter.register_subscriptions()
```

### Domain Adapters (Future)

Each domain needs an `inferred_service.py` with functions like:
- `create_inferred_transaction()` for finance
- `log_inferred_workout()` for health
- `log_inferred_habit()` for habits
- etc.

These are called by the interpreter when confidence is high enough.

## 7) Testing

Test file: `lifeos/tests/test_calendar_and_interpreter.py`

Coverage includes:
- `TestClassifyEvent`: Classification rules for gym, dinner, shopping, lessons
- `TestCalendarEventModel`: Model creation and relationships
- `TestCalendarService`: Service CRUD and validation
- `TestCalendarAPI`: API endpoint integration tests

## 8) Frontend Integration Hints

### Event Creation

```javascript
// Create calendar event
const response = await fetch('/api/calendar/events', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({
    title: 'Gym workout',
    start_time: '2024-12-06T18:00:00',
    end_time: '2024-12-06T19:00:00',
    location: 'Fitness Center'
  })
});
```

### Pending Interpretations

```javascript
// Fetch pending interpretations for review UI
const interpretations = await fetch('/api/calendar/interpretations', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Display: "This looks like a workout. Confirm?"
// On confirm:
await fetch(`/api/calendar/interpretations/${id}/confirm`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

### Calendar Sync UI

Future: Calendar settings page for connecting Google/Apple calendars. The `source` and `external_id` fields support deduplication during sync.

## 9) Migration Deployment

```bash
# Run migration
cd lifeos
flask db upgrade 20251206_calendar_initial
```

The migration creates:
- `calendar_event` table with indexes on `(user_id, start_time)`, `(user_id, end_time)`, `(user_id, source)`, unique on `(user_id, external_id)`
- `calendar_event_interpretation` table with indexes on `(user_id, status)`, `(user_id, domain, status)`, `(calendar_event_id)`

## 10) Configuration

| Config Key | Default | Description |
|------------|---------|-------------|
| `ENABLE_CALENDAR_INTERPRETER` | `True` | Enable/disable automatic interpretation |

## 11) Impact Summary

- **Backend:** New calendar domain with full CRUD, interpreter layer for event classification, adapter pattern for domain integration
- **Database:** Two new tables with appropriate indexes; no changes to existing tables
- **Frontend:** New API surface for calendar events and interpretation review workflow
- **Architecture:** Calendar now serves as the hub for capturing data across all life domains

## 12) Next Steps

1. **External Sync:** Implement Google Calendar OAuth + sync in `tasks.py`
2. **ML Enhancement:** Replace regex classification with trained model
3. **Domain Adapters:** Implement `inferred_service.py` in each target domain
4. **Recurrence:** Add RRULE parsing and expansion for recurring events
5. **Notifications:** Alert users when interpretations need review
