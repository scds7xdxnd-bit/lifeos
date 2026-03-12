# LifeOS Calendar-First Architecture Specification

**Status:** Architectural Design (approved by Architect)
**Date:** 2025-12-07
**Author:** LifeOS Architect

---

## 1. Executive Summary

LifeOS is evolving from a **domain-centric** to a **calendar-first, event-centric** experience. The Calendar becomes the primary input surface where users record their life activities (meals, workouts, meetings, study sessions, purchases). A new **Calendar Interpreter** layer analyzes these calendar events and derives structured records across existing domains (Finance, Health, Habits, Skills, Projects, Relationships).

This design:
- Introduces a new **Calendar domain** (`lifeos/domains/calendar/`)
- Adds a **Calendar Interpreter** layer (`lifeos/core/interpreter/`)
- Extends existing domain models with **inferred record** capabilities
- Maintains full backward compatibility with manual workflows

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Calendar UI │  │ Google Cal  │  │ Apple Cal   │  │ Manual Entry│         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CALENDAR DOMAIN                                      │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ CalendarEvent (id, user_id, title, description, start_time,        │     │
│  │                end_time, location, source, recurrence_rule, ...)   │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ calendar_service.py: create/update/delete events                   │     │
│  │ Emits: calendar.event.created/updated/deleted                      │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼ Event Bus
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CALENDAR INTERPRETER (Core Layer)                      │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ Subscribes to: calendar.event.created, calendar.event.updated      │     │
│  │ Applies: rule-based classification (title, description, time, etc) │     │
│  │ Calls: domain services via defined interfaces                      │     │
│  │ Emits: domain.*.inferred events                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  Classification Rules Engine:                                                │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │ • Meal keywords → health.meal.inferred                             │     │
│  │ • Workout/gym/run → health.workout.inferred                        │     │
│  │ • Shopping/purchase → finance.transaction.inferred                 │     │
│  │ • Meeting with <person> → relationships.interaction.inferred       │     │
│  │ • Study/practice <skill> → skills.practice.inferred               │     │
│  │ • Project work → projects.work_session.inferred                   │     │
│  │ • Habit-linked keywords → habits.habit.logged (inferred)          │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXISTING DOMAINS (Extended)                          │
│                                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Finance   │ │   Health    │ │   Habits    │ │   Skills    │           │
│  │ +source     │ │ +source     │ │ +source     │ │ +source     │           │
│  │ +calendar_  │ │ +calendar_  │ │ +calendar_  │ │ +calendar_  │           │
│  │  event_id   │ │  event_id   │ │  event_id   │ │  event_id   │           │
│  │ +confidence │ │ +confidence │ │ +confidence │ │ +confidence │           │
│  │ +status     │ │ +status     │ │ +status     │ │ +status     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                                              │
│  ┌─────────────┐ ┌─────────────┐                                            │
│  │  Projects   │ │Relationships│                                            │
│  │ +source     │ │ +source     │                                            │
│  │ +calendar_  │ │ +calendar_  │                                            │
│  │  event_id   │ │  event_id   │                                            │
│  │ +confidence │ │ +confidence │                                            │
│  │ +status     │ │ +status     │                                            │
│  └─────────────┘ └─────────────┘                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Calendar Domain Design

### 3.1 Folder Structure

```
lifeos/domains/calendar/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── calendar_event.py          # CalendarEvent, CalendarEventTag, CalendarRecurrence
├── services/
│   ├── __init__.py
│   ├── calendar_service.py        # CRUD, query, hooks to interpreter
│   └── sync_service.py            # Future: Google/Apple Calendar sync
├── controllers/
│   ├── __init__.py
│   ├── calendar_api.py            # JSON API endpoints
│   └── calendar_pages.py          # HTML UI routes
├── schemas/
│   ├── __init__.py
│   └── calendar_schemas.py        # Pydantic DTOs
├── events.py                      # Event catalog: calendar.event.*
├── mappers.py                     # DTO ↔ model converters
└── tasks.py                       # Periodic sync tasks (future)
```

### 3.2 Data Model: `CalendarEvent`

**Table:** `calendar_event`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int` | PK | Primary key |
| `user_id` | `int` | FK → user.id, NOT NULL, INDEX | Owner |
| `title` | `str(255)` | NOT NULL | Event title (e.g., "Lunch with John") |
| `description` | `text` | NULL | Extended details |
| `start_time` | `datetime` | NOT NULL, INDEX | Event start (UTC) |
| `end_time` | `datetime` | NULL | Event end (UTC); NULL = all-day or instant |
| `all_day` | `bool` | DEFAULT false | Whether this is an all-day event |
| `location` | `str(512)` | NULL | Location text or address |
| `source` | `str(32)` | NOT NULL, DEFAULT 'manual' | 'manual', 'sync_google', 'sync_apple', 'api' |
| `external_id` | `str(255)` | NULL, INDEX | External calendar event ID (for sync) |
| `recurrence_rule` | `str(255)` | NULL | RRULE string (future: recurring events) |
| `color` | `str(16)` | NULL | Hex color code for UI |
| `is_private` | `bool` | DEFAULT false | Privacy flag |
| `tags` | `JSON` | DEFAULT [] | Array of user-defined tags |
| `metadata` | `JSON` | DEFAULT {} | Extensible key-value data |
| `created_at` | `datetime` | DEFAULT now() | Record creation |
| `updated_at` | `datetime` | DEFAULT now(), ON UPDATE | Last modification |

**Indexes:**
- `ix_calendar_event_user_start` → `(user_id, start_time)` — primary query pattern
- `ix_calendar_event_user_end` → `(user_id, end_time)` — range queries
- `ix_calendar_event_user_source` → `(user_id, source)` — filter by source
- `ux_calendar_event_user_external` → `(user_id, external_id)` UNIQUE WHERE external_id IS NOT NULL — sync deduplication

### 3.3 Data Model: `CalendarEventInterpretation`

**Table:** `calendar_event_interpretation`

Stores the interpreter's classification result for each calendar event. Enables:
- Tracking which domains were inferred from an event
- User review/confirmation workflow
- Re-interpretation on event update

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `int` | PK | Primary key |
| `calendar_event_id` | `int` | FK → calendar_event.id, NOT NULL, INDEX | Source event |
| `user_id` | `int` | FK → user.id, NOT NULL, INDEX | Owner (denormalized for queries) |
| `domain` | `str(32)` | NOT NULL | Target domain: 'finance', 'health', 'habits', etc. |
| `record_type` | `str(64)` | NOT NULL | Specific record type: 'transaction', 'workout', 'meal', etc. |
| `record_id` | `int` | NULL | FK to created domain record (once created) |
| `confidence_score` | `float` | NOT NULL, DEFAULT 0.0 | 0.0–1.0 classification confidence |
| `status` | `str(16)` | NOT NULL, DEFAULT 'inferred' | 'inferred', 'confirmed', 'rejected', 'ignored' |
| `classification_data` | `JSON` | DEFAULT {} | Rule match details, extracted values |
| `created_at` | `datetime` | DEFAULT now() | When interpretation was created |
| `updated_at` | `datetime` | DEFAULT now() | When status was last changed |

**Indexes:**
- `ix_interpretation_event` → `(calendar_event_id)`
- `ix_interpretation_user_domain` → `(user_id, domain, status)` — dashboard queries
- `ix_interpretation_user_status` → `(user_id, status)` — pending review queries

---

## 4. Calendar Interpreter Design

### 4.1 Location

```
lifeos/core/interpreter/
├── __init__.py
├── calendar_interpreter.py        # Main interpreter class
├── classification_rules.py        # Rule definitions
├── domain_adapters.py             # Service interface adapters
└── constants.py                   # Keywords, patterns, thresholds
```

### 4.2 Architecture

The Calendar Interpreter:
1. **Subscribes** to `calendar.event.created` and `calendar.event.updated` via the event bus
2. **Classifies** the event using rule-based pattern matching on title/description/time/location
3. **Creates** `CalendarEventInterpretation` records for each potential domain match
4. **Calls** domain services to create inferred records (via domain adapters)
5. **Emits** `domain.*.inferred` events for downstream processing (insights, notifications)

### 4.3 Classification Rules Engine

```python
# lifeos/core/interpreter/classification_rules.py

CLASSIFICATION_RULES = {
    "finance": {
        "transaction": {
            "keywords": ["shopping", "grocery", "purchase", "bought", "paid", "spent", "store", "mall"],
            "patterns": [r"(?i)(buy|bought|purchase|pay|paid|spend|spent)\s+(.+)"],
            "time_hints": None,  # No time-based rules
            "confidence_base": 0.7,
        },
    },
    "health": {
        "meal": {
            "keywords": ["breakfast", "lunch", "dinner", "brunch", "eating", "restaurant", "cafe", "coffee"],
            "patterns": [r"(?i)(lunch|dinner|breakfast|brunch)\s+(with|at)\s+(.+)"],
            "time_hints": {  # Time-based confidence boost
                "breakfast": (6, 10),
                "lunch": (11, 14),
                "dinner": (17, 21),
            },
            "confidence_base": 0.75,
        },
        "workout": {
            "keywords": ["gym", "workout", "run", "running", "yoga", "swim", "exercise", "training", "fitness"],
            "patterns": [r"(?i)(gym|workout|run|yoga|training)\s*(.*)"],
            "time_hints": None,
            "confidence_base": 0.85,
        },
    },
    "habits": {
        "habit_log": {
            "keywords": [],  # Dynamic: matched against user's habit names
            "patterns": [],
            "time_hints": None,
            "confidence_base": 0.8,
        },
    },
    "skills": {
        "practice": {
            "keywords": ["study", "practice", "learn", "lesson", "class", "course", "tutorial"],
            "patterns": [r"(?i)(study|practice|learn|lesson)\s+(.+)"],
            "time_hints": None,
            "confidence_base": 0.75,
        },
    },
    "projects": {
        "work_session": {
            "keywords": ["work on", "working on", "project", "meeting about", "sprint", "standup"],
            "patterns": [r"(?i)(work(?:ing)?\s+on|project)\s+(.+)"],
            "time_hints": None,
            "confidence_base": 0.7,
        },
    },
    "relationships": {
        "interaction": {
            "keywords": ["meeting", "call", "coffee with", "lunch with", "dinner with", "hangout"],
            "patterns": [r"(?i)(meeting|call|coffee|lunch|dinner|hangout)\s+with\s+(.+)"],
            "time_hints": None,
            "confidence_base": 0.8,
        },
    },
}
```

### 4.4 Domain Adapters (Service Interfaces)

```python
# lifeos/core/interpreter/domain_adapters.py

class DomainAdapter:
    """Base class for domain service adapters."""

    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
    ) -> int | None:
        """Create an inferred record in the domain. Return record ID or None."""
        raise NotImplementedError


class FinanceAdapter(DomainAdapter):
    """Adapter for finance domain inferred transactions."""

    def create_inferred_record(self, user_id, calendar_event_id, confidence_score, extracted_data):
        from lifeos.domains.finance.services import transaction_service
        return transaction_service.create_inferred_transaction(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            description=extracted_data.get("description"),
            amount_hint=extracted_data.get("amount"),  # May be None
            category_hint=extracted_data.get("category"),
            occurred_at=extracted_data.get("occurred_at"),
        )


class HealthMealAdapter(DomainAdapter):
    """Adapter for health meal logging."""

    def create_inferred_record(self, user_id, calendar_event_id, confidence_score, extracted_data):
        from lifeos.domains.health.services import health_service
        return health_service.log_inferred_meal(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            meal_type=extracted_data.get("meal_type"),
            description=extracted_data.get("description"),
            logged_at=extracted_data.get("logged_at"),
        )


class HealthWorkoutAdapter(DomainAdapter):
    """Adapter for health workout logging."""

    def create_inferred_record(self, user_id, calendar_event_id, confidence_score, extracted_data):
        from lifeos.domains.health.services import health_service
        return health_service.log_inferred_workout(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            workout_type=extracted_data.get("workout_type"),
            duration_minutes=extracted_data.get("duration_minutes"),
            logged_at=extracted_data.get("logged_at"),
        )


class HabitsAdapter(DomainAdapter):
    """Adapter for habits logging."""

    def create_inferred_record(self, user_id, calendar_event_id, confidence_score, extracted_data):
        from lifeos.domains.habits.services import habits_service
        return habits_service.log_inferred_habit(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            habit_id=extracted_data.get("habit_id"),
            logged_date=extracted_data.get("logged_date"),
            value=extracted_data.get("value"),
        )


class SkillsAdapter(DomainAdapter):
    """Adapter for skills practice logging."""

    def create_inferred_record(self, user_id, calendar_event_id, confidence_score, extracted_data):
        from lifeos.domains.skills.services import skills_service
        return skills_service.log_inferred_practice(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            skill_id=extracted_data.get("skill_id"),
            skill_name=extracted_data.get("skill_name"),  # For auto-create
            duration_minutes=extracted_data.get("duration_minutes"),
            practiced_at=extracted_data.get("practiced_at"),
        )


class ProjectsAdapter(DomainAdapter):
    """Adapter for projects work session logging."""

    def create_inferred_record(self, user_id, calendar_event_id, confidence_score, extracted_data):
        from lifeos.domains.projects.services import projects_service
        return projects_service.log_inferred_work_session(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            project_id=extracted_data.get("project_id"),
            project_name=extracted_data.get("project_name"),  # For auto-match
            task_id=extracted_data.get("task_id"),
            duration_minutes=extracted_data.get("duration_minutes"),
            logged_at=extracted_data.get("logged_at"),
        )


class RelationshipsAdapter(DomainAdapter):
    """Adapter for relationships interaction logging."""

    def create_inferred_record(self, user_id, calendar_event_id, confidence_score, extracted_data):
        from lifeos.domains.relationships.services import relationships_service
        return relationships_service.log_inferred_interaction(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            person_id=extracted_data.get("person_id"),
            person_name=extracted_data.get("person_name"),  # For auto-match
            interaction_type=extracted_data.get("interaction_type"),
            logged_at=extracted_data.get("logged_at"),
        )
```

### 4.5 Main Interpreter Class

```python
# lifeos/core/interpreter/calendar_interpreter.py

class CalendarInterpreter:
    """
    Subscribes to calendar events, classifies them, and creates inferred domain records.
    """

    def __init__(self):
        self.adapters = {
            ("finance", "transaction"): FinanceAdapter(),
            ("health", "meal"): HealthMealAdapter(),
            ("health", "workout"): HealthWorkoutAdapter(),
            ("habits", "habit_log"): HabitsAdapter(),
            ("skills", "practice"): SkillsAdapter(),
            ("projects", "work_session"): ProjectsAdapter(),
            ("relationships", "interaction"): RelationshipsAdapter(),
        }

    def register_subscriptions(self):
        """Register event bus subscriptions."""
        from lifeos.core.events.event_bus import event_bus
        event_bus.subscribe("calendar.event.created", self.on_calendar_event)
        event_bus.subscribe("calendar.event.updated", self.on_calendar_event)

    def on_calendar_event(self, event: EventRecord):
        """Handle calendar event creation/update."""
        payload = event.payload
        user_id = payload["user_id"]
        calendar_event_id = payload["calendar_event_id"]
        title = payload["title"]
        description = payload.get("description", "")
        start_time = payload["start_time"]
        end_time = payload.get("end_time")
        location = payload.get("location", "")

        # Classify the event
        classifications = self.classify(
            user_id=user_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
        )

        # Create interpretations and inferred records
        for classification in classifications:
            self.create_interpretation_and_record(
                user_id=user_id,
                calendar_event_id=calendar_event_id,
                classification=classification,
            )

    def classify(self, user_id, title, description, start_time, end_time, location):
        """
        Apply classification rules to extract domain-specific interpretations.
        Returns list of (domain, record_type, confidence, extracted_data) tuples.
        """
        # Implementation uses CLASSIFICATION_RULES + user's habits/skills/projects
        ...

    def create_interpretation_and_record(self, user_id, calendar_event_id, classification):
        """Create CalendarEventInterpretation and call domain adapter."""
        domain, record_type, confidence, extracted_data = classification

        # Create interpretation record
        interpretation = CalendarEventInterpretation(
            calendar_event_id=calendar_event_id,
            user_id=user_id,
            domain=domain,
            record_type=record_type,
            confidence_score=confidence,
            status="inferred",
            classification_data=extracted_data,
        )
        db.session.add(interpretation)

        # Call domain adapter to create inferred record
        adapter = self.adapters.get((domain, record_type))
        if adapter:
            record_id = adapter.create_inferred_record(
                user_id=user_id,
                calendar_event_id=calendar_event_id,
                confidence_score=confidence,
                extracted_data=extracted_data,
            )
            interpretation.record_id = record_id

        db.session.commit()

        # Emit inferred event
        self.emit_inferred_event(domain, record_type, user_id, calendar_event_id, interpretation.id, confidence)

    def emit_inferred_event(self, domain, record_type, user_id, calendar_event_id, interpretation_id, confidence):
        """Emit domain.*.inferred event to the bus."""
        from lifeos.lifeos_platform.outbox import enqueue
        event_type = f"{domain}.{record_type}.inferred"
        enqueue(
            user_id=user_id,
            event_type=event_type,
            payload={
                "user_id": user_id,
                "calendar_event_id": calendar_event_id,
                "interpretation_id": interpretation_id,
                "confidence_score": confidence,
                "created_at": datetime.utcnow().isoformat(),
            },
        )


# Global singleton (initialized in app factory)
calendar_interpreter = CalendarInterpreter()
```

---

## 5. Domain Model Extensions

### 5.1 Common Inferred Record Fields

Each domain that supports inferred records must add these columns (nullable, backward-compatible):

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `source` | `str(32)` | DEFAULT 'manual' | 'manual', 'calendar', 'import', 'api' |
| `calendar_event_id` | `int` | FK → calendar_event.id, NULL | Source calendar event (if any) |
| `confidence_score` | `float` | NULL | 0.0–1.0 inference confidence (NULL for manual) |
| `inference_status` | `str(16)` | NULL | 'inferred', 'confirmed', 'rejected' (NULL for manual) |

### 5.2 Domain-Specific Extensions

#### Finance: `finance_transaction`
```python
# Add columns:
source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
calendar_event_id: Mapped[int | None] = mapped_column(db.ForeignKey("calendar_event.id"), nullable=True)
confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)

# Index: (user_id, inference_status) for pending review queries
```

#### Health: `health_workout`, `health_nutrition_log`
```python
# Add columns to both tables:
source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
calendar_event_id: Mapped[int | None] = mapped_column(db.ForeignKey("calendar_event.id"), nullable=True)
confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
```

#### Habits: `habit_log`
```python
# Add columns:
source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
calendar_event_id: Mapped[int | None] = mapped_column(db.ForeignKey("calendar_event.id"), nullable=True)
confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
```

#### Skills: `skill_practice_session`
```python
# Add columns:
source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
calendar_event_id: Mapped[int | None] = mapped_column(db.ForeignKey("calendar_event.id"), nullable=True)
confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
```

#### Projects: `project_task_log`
```python
# Add columns:
source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
calendar_event_id: Mapped[int | None] = mapped_column(db.ForeignKey("calendar_event.id"), nullable=True)
confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
```

#### Relationships: `relationships_interaction`
```python
# Add columns:
source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
calendar_event_id: Mapped[int | None] = mapped_column(db.ForeignKey("calendar_event.id"), nullable=True)
confidence_score: Mapped[float | None] = mapped_column(db.Numeric(3, 2), nullable=True)
inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)
```

---

## 6. Event Catalog Extensions

### 6.1 Calendar Domain Events

**File:** `lifeos/domains/calendar/events.py`

```python
CALENDAR_EVENT_CREATED = "calendar.event.created"
CALENDAR_EVENT_UPDATED = "calendar.event.updated"
CALENDAR_EVENT_DELETED = "calendar.event.deleted"

EVENT_CATALOG = {
    CALENDAR_EVENT_CREATED: {
        "version": "v1",
        "payload": {
            "calendar_event_id": "int",
            "user_id": "int",
            "title": "str",
            "description": "str?",
            "start_time": "datetime",
            "end_time": "datetime?",
            "all_day": "bool",
            "location": "str?",
            "source": "str",
            "external_id": "str?",
            "tags": "list[str]",
            "created_at": "datetime",
        },
    },
    CALENDAR_EVENT_UPDATED: {
        "version": "v1",
        "payload": {
            "calendar_event_id": "int",
            "user_id": "int",
            "title": "str",
            "description": "str?",
            "start_time": "datetime",
            "end_time": "datetime?",
            "all_day": "bool",
            "location": "str?",
            "source": "str",
            "fields_changed": "list[str]",
            "updated_at": "datetime",
        },
    },
    CALENDAR_EVENT_DELETED: {
        "version": "v1",
        "payload": {
            "calendar_event_id": "int",
            "user_id": "int",
            "deleted_at": "datetime",
        },
    },
}
```

### 6.2 Inferred Events (per domain)

Add to each domain's `events.py`:

**Finance:**
```python
FINANCE_TRANSACTION_INFERRED = "finance.transaction.inferred"
# Payload: { transaction_id, user_id, calendar_event_id, interpretation_id, confidence_score, description?, amount?, occurred_at, created_at }
```

**Health:**
```python
HEALTH_MEAL_INFERRED = "health.meal.inferred"
HEALTH_WORKOUT_INFERRED = "health.workout.inferred"
# Payload: { record_id, user_id, calendar_event_id, interpretation_id, confidence_score, ... }
```

**Habits:**
```python
HABITS_HABIT_LOGGED_INFERRED = "habits.habit.logged.inferred"
# Payload: { log_id, habit_id, user_id, calendar_event_id, interpretation_id, confidence_score, logged_date, ... }
```

**Skills:**
```python
SKILLS_PRACTICE_INFERRED = "skills.practice.inferred"
# Payload: { session_id, skill_id, user_id, calendar_event_id, interpretation_id, confidence_score, duration_minutes, ... }
```

**Projects:**
```python
PROJECTS_WORK_SESSION_INFERRED = "projects.work_session.inferred"
# Payload: { log_id, task_id?, project_id?, user_id, calendar_event_id, interpretation_id, confidence_score, ... }
```

**Relationships:**
```python
RELATIONSHIPS_INTERACTION_INFERRED = "relationships.interaction.inferred"
# Payload: { interaction_id, person_id, user_id, calendar_event_id, interpretation_id, confidence_score, ... }
```

---

## 7. Migration Plan

### 7.1 Migration Sequence

| Order | Filename | Purpose |
|-------|----------|---------|
| 1 | `20251207_calendar_initial.py` | Create `calendar_event`, `calendar_event_interpretation` tables |
| 2 | `20251207_domains_inferred_columns.py` | Add inferred columns to all domain tables |

### 7.2 Migration 1: Calendar Domain

**File:** `lifeos/migrations/versions/20251207_calendar_initial.py`

```python
"""Create calendar domain tables.

Revision ID: 20251207_calendar_initial
Revises: 20251218_backend_updates_validation
Create Date: 2025-12-07
"""

from alembic import op
import sqlalchemy as sa

revision = "20251207_calendar_initial"
down_revision = "20251218_backend_updates_validation"
branch_labels = None
depends_on = None


def upgrade():
    # calendar_event table
    op.create_table(
        "calendar_event",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("all_day", sa.Boolean(), nullable=False, default=False),
        sa.Column("location", sa.String(512), nullable=True),
        sa.Column("source", sa.String(32), nullable=False, default="manual"),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("recurrence_rule", sa.String(255), nullable=True),
        sa.Column("color", sa.String(16), nullable=True),
        sa.Column("is_private", sa.Boolean(), nullable=False, default=False),
        sa.Column("tags", sa.JSON(), nullable=False, default=[]),
        sa.Column("metadata", sa.JSON(), nullable=False, default={}),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Indexes for calendar_event
    op.create_index("ix_calendar_event_user_start", "calendar_event", ["user_id", "start_time"])
    op.create_index("ix_calendar_event_user_end", "calendar_event", ["user_id", "end_time"])
    op.create_index("ix_calendar_event_user_source", "calendar_event", ["user_id", "source"])
    op.create_index(
        "ux_calendar_event_user_external",
        "calendar_event",
        ["user_id", "external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )

    # calendar_event_interpretation table
    op.create_table(
        "calendar_event_interpretation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("calendar_event_id", sa.Integer(), sa.ForeignKey("calendar_event.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("domain", sa.String(32), nullable=False),
        sa.Column("record_type", sa.String(64), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3, 2), nullable=False, default=0.0),
        sa.Column("status", sa.String(16), nullable=False, default="inferred"),
        sa.Column("classification_data", sa.JSON(), nullable=False, default={}),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Indexes for calendar_event_interpretation
    op.create_index("ix_interpretation_user_domain", "calendar_event_interpretation", ["user_id", "domain", "status"])
    op.create_index("ix_interpretation_user_status", "calendar_event_interpretation", ["user_id", "status"])


def downgrade():
    op.drop_table("calendar_event_interpretation")
    op.drop_table("calendar_event")
```

### 7.3 Migration 2: Domain Inferred Columns

**File:** `lifeos/migrations/versions/20251207_domains_inferred_columns.py`

```python
"""Add inferred record columns to domain tables.

Revision ID: 20251207_domains_inferred_columns
Revises: 20251207_calendar_initial
Create Date: 2025-12-07
"""

from alembic import op
import sqlalchemy as sa

revision = "20251207_domains_inferred_columns"
down_revision = "20251207_calendar_initial"
branch_labels = None
depends_on = None


def upgrade():
    # Finance: finance_transaction
    op.add_column("finance_transaction", sa.Column("source", sa.String(32), nullable=False, server_default="manual"))
    op.add_column("finance_transaction", sa.Column("calendar_event_id", sa.Integer(), sa.ForeignKey("calendar_event.id"), nullable=True))
    op.add_column("finance_transaction", sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True))
    op.add_column("finance_transaction", sa.Column("inference_status", sa.String(16), nullable=True))
    op.create_index("ix_finance_transaction_inference_status", "finance_transaction", ["user_id", "inference_status"])

    # Health: health_workout
    op.add_column("health_workout", sa.Column("source", sa.String(32), nullable=False, server_default="manual"))
    op.add_column("health_workout", sa.Column("calendar_event_id", sa.Integer(), sa.ForeignKey("calendar_event.id"), nullable=True))
    op.add_column("health_workout", sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True))
    op.add_column("health_workout", sa.Column("inference_status", sa.String(16), nullable=True))

    # Health: health_nutrition_log
    op.add_column("health_nutrition_log", sa.Column("source", sa.String(32), nullable=False, server_default="manual"))
    op.add_column("health_nutrition_log", sa.Column("calendar_event_id", sa.Integer(), sa.ForeignKey("calendar_event.id"), nullable=True))
    op.add_column("health_nutrition_log", sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True))
    op.add_column("health_nutrition_log", sa.Column("inference_status", sa.String(16), nullable=True))

    # Habits: habit_log
    op.add_column("habit_log", sa.Column("source", sa.String(32), nullable=False, server_default="manual"))
    op.add_column("habit_log", sa.Column("calendar_event_id", sa.Integer(), sa.ForeignKey("calendar_event.id"), nullable=True))
    op.add_column("habit_log", sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True))
    op.add_column("habit_log", sa.Column("inference_status", sa.String(16), nullable=True))

    # Skills: skill_practice_session
    op.add_column("skill_practice_session", sa.Column("source", sa.String(32), nullable=False, server_default="manual"))
    op.add_column("skill_practice_session", sa.Column("calendar_event_id", sa.Integer(), sa.ForeignKey("calendar_event.id"), nullable=True))
    op.add_column("skill_practice_session", sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True))
    op.add_column("skill_practice_session", sa.Column("inference_status", sa.String(16), nullable=True))

    # Projects: project_task_log
    op.add_column("project_task_log", sa.Column("source", sa.String(32), nullable=False, server_default="manual"))
    op.add_column("project_task_log", sa.Column("calendar_event_id", sa.Integer(), sa.ForeignKey("calendar_event.id"), nullable=True))
    op.add_column("project_task_log", sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True))
    op.add_column("project_task_log", sa.Column("inference_status", sa.String(16), nullable=True))

    # Relationships: relationships_interaction
    op.add_column("relationships_interaction", sa.Column("source", sa.String(32), nullable=False, server_default="manual"))
    op.add_column("relationships_interaction", sa.Column("calendar_event_id", sa.Integer(), sa.ForeignKey("calendar_event.id"), nullable=True))
    op.add_column("relationships_interaction", sa.Column("confidence_score", sa.Numeric(3, 2), nullable=True))
    op.add_column("relationships_interaction", sa.Column("inference_status", sa.String(16), nullable=True))


def downgrade():
    # Reverse all column additions (in reverse order)
    for table in ["relationships_interaction", "project_task_log", "skill_practice_session",
                  "habit_log", "health_nutrition_log", "health_workout", "finance_transaction"]:
        for col in ["inference_status", "confidence_score", "calendar_event_id", "source"]:
            op.drop_column(table, col)

    op.drop_index("ix_finance_transaction_inference_status", "finance_transaction")
```

---

## 8. API Endpoints

### 8.1 Calendar API

**File:** `lifeos/domains/calendar/controllers/calendar_api.py`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/calendar/events` | List events with date range filter |
| `GET` | `/api/calendar/events/<id>` | Get single event |
| `POST` | `/api/calendar/events` | Create new event |
| `PATCH` | `/api/calendar/events/<id>` | Update event |
| `DELETE` | `/api/calendar/events/<id>` | Delete event |
| `GET` | `/api/calendar/events/<id>/interpretations` | Get event's interpretations |
| `PATCH` | `/api/calendar/interpretations/<id>` | Confirm/reject interpretation |

### 8.2 Request/Response Schemas

```python
# lifeos/domains/calendar/schemas/calendar_schemas.py

class CalendarEventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    all_day: bool = False
    location: str | None = None
    color: str | None = None
    is_private: bool = False
    tags: list[str] = []

class CalendarEventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    all_day: bool | None = None
    location: str | None = None
    color: str | None = None
    is_private: bool | None = None
    tags: list[str] | None = None

class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime | None
    all_day: bool
    location: str | None
    source: str
    color: str | None
    is_private: bool
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    interpretations: list["InterpretationResponse"] | None = None

class InterpretationResponse(BaseModel):
    id: int
    domain: str
    record_type: str
    record_id: int | None
    confidence_score: float
    status: str
    classification_data: dict

class InterpretationUpdate(BaseModel):
    status: Literal["confirmed", "rejected", "ignored"]
```

---

## 9. Domain Service Interface Specifications

Each domain must implement these service methods to support calendar-inferred records:

### 9.1 Finance Domain

```python
# lifeos/domains/finance/services/transaction_service.py

def create_inferred_transaction(
    user_id: int,
    calendar_event_id: int,
    confidence_score: float,
    description: str | None = None,
    amount_hint: float | None = None,
    category_hint: str | None = None,
    occurred_at: datetime | None = None,
) -> int:
    """
    Create an inferred transaction from a calendar event.

    Returns: transaction_id
    """
    tx = Transaction(
        user_id=user_id,
        amount=amount_hint or 0.0,  # User must confirm amount
        description=description,
        category=category_hint,
        occurred_at=occurred_at or datetime.utcnow(),
        source="calendar",
        calendar_event_id=calendar_event_id,
        confidence_score=confidence_score,
        inference_status="inferred",
    )
    db.session.add(tx)
    db.session.commit()

    # Emit event
    enqueue(user_id, FINANCE_TRANSACTION_INFERRED, {...})

    return tx.id


def confirm_inferred_transaction(
    user_id: int,
    transaction_id: int,
    amount: float,
    category: str | None = None,
    debit_account_id: int | None = None,
    credit_account_id: int | None = None,
) -> Transaction:
    """Confirm an inferred transaction with actual data."""
    tx = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    if not tx or tx.inference_status != "inferred":
        raise ValueError("not_found_or_not_inferred")

    tx.amount = amount
    tx.category = category
    tx.inference_status = "confirmed"
    # Optionally create journal entry if accounts provided
    ...
    db.session.commit()
    return tx
```

### 9.2 Health Domain

```python
# lifeos/domains/health/services/health_service.py

def log_inferred_meal(
    user_id: int,
    calendar_event_id: int,
    confidence_score: float,
    meal_type: str,
    description: str | None = None,
    logged_at: datetime | None = None,
) -> int:
    """Create an inferred nutrition log from calendar event."""
    log = NutritionLog(
        user_id=user_id,
        date=(logged_at or datetime.utcnow()).date(),
        meal_type=meal_type,
        items=description or "",
        source="calendar",
        calendar_event_id=calendar_event_id,
        confidence_score=confidence_score,
        inference_status="inferred",
    )
    db.session.add(log)
    db.session.commit()
    enqueue(user_id, HEALTH_MEAL_INFERRED, {...})
    return log.id


def log_inferred_workout(
    user_id: int,
    calendar_event_id: int,
    confidence_score: float,
    workout_type: str,
    duration_minutes: int | None = None,
    logged_at: datetime | None = None,
) -> int:
    """Create an inferred workout from calendar event."""
    workout = Workout(
        user_id=user_id,
        date=(logged_at or datetime.utcnow()).date(),
        workout_type=workout_type,
        duration_minutes=duration_minutes or 0,
        intensity="medium",  # Default; user can refine
        source="calendar",
        calendar_event_id=calendar_event_id,
        confidence_score=confidence_score,
        inference_status="inferred",
    )
    db.session.add(workout)
    db.session.commit()
    enqueue(user_id, HEALTH_WORKOUT_INFERRED, {...})
    return workout.id
```

### 9.3 Habits Domain

```python
# lifeos/domains/habits/services/habits_service.py

def log_inferred_habit(
    user_id: int,
    calendar_event_id: int,
    confidence_score: float,
    habit_id: int,
    logged_date: date,
    value: float | None = None,
) -> int:
    """Create an inferred habit log from calendar event."""
    log = HabitLog(
        user_id=user_id,
        habit_id=habit_id,
        logged_date=logged_date,
        value=value,
        source="calendar",
        calendar_event_id=calendar_event_id,
        confidence_score=confidence_score,
        inference_status="inferred",
    )
    db.session.add(log)
    db.session.commit()
    enqueue(user_id, HABITS_HABIT_LOGGED_INFERRED, {...})
    return log.id
```

### 9.4 Skills Domain

```python
# lifeos/domains/skills/services/skills_service.py

def log_inferred_practice(
    user_id: int,
    calendar_event_id: int,
    confidence_score: float,
    skill_id: int | None = None,
    skill_name: str | None = None,
    duration_minutes: int | None = None,
    practiced_at: datetime | None = None,
) -> int:
    """Create an inferred practice session from calendar event."""
    # Auto-match or create skill if skill_name provided
    if skill_id is None and skill_name:
        skill = Skill.query.filter_by(user_id=user_id, name=skill_name).first()
        if not skill:
            skill = Skill(user_id=user_id, name=skill_name)
            db.session.add(skill)
            db.session.flush()
        skill_id = skill.id

    session = PracticeSession(
        user_id=user_id,
        skill_id=skill_id,
        duration_minutes=duration_minutes or 0,
        practiced_at=practiced_at or datetime.utcnow(),
        source="calendar",
        calendar_event_id=calendar_event_id,
        confidence_score=confidence_score,
        inference_status="inferred",
    )
    db.session.add(session)
    db.session.commit()
    enqueue(user_id, SKILLS_PRACTICE_INFERRED, {...})
    return session.id
```

### 9.5 Projects Domain

```python
# lifeos/domains/projects/services/projects_service.py

def log_inferred_work_session(
    user_id: int,
    calendar_event_id: int,
    confidence_score: float,
    project_id: int | None = None,
    project_name: str | None = None,
    task_id: int | None = None,
    duration_minutes: int | None = None,
    logged_at: datetime | None = None,
) -> int:
    """Create an inferred work session log from calendar event."""
    # Auto-match project by name if project_id not provided
    if project_id is None and project_name:
        project = Project.query.filter_by(user_id=user_id, name=project_name).first()
        if project:
            project_id = project.id
            # Find most recent open task
            task = ProjectTask.query.filter_by(project_id=project_id, status="open").first()
            if task:
                task_id = task.id

    if task_id is None:
        # Cannot log work session without a task; create as unlinked or skip
        return None

    log = ProjectTaskLog(
        user_id=user_id,
        task_id=task_id,
        note=f"Inferred from calendar: {duration_minutes or 0} minutes",
        logged_at=logged_at or datetime.utcnow(),
        source="calendar",
        calendar_event_id=calendar_event_id,
        confidence_score=confidence_score,
        inference_status="inferred",
    )
    db.session.add(log)
    db.session.commit()
    enqueue(user_id, PROJECTS_WORK_SESSION_INFERRED, {...})
    return log.id
```

### 9.6 Relationships Domain

```python
# lifeos/domains/relationships/services/relationships_service.py

def log_inferred_interaction(
    user_id: int,
    calendar_event_id: int,
    confidence_score: float,
    person_id: int | None = None,
    person_name: str | None = None,
    interaction_type: str = "meeting",
    logged_at: datetime | None = None,
) -> int:
    """Create an inferred interaction from calendar event."""
    # Auto-match person by name
    if person_id is None and person_name:
        person = Person.query.filter(
            Person.user_id == user_id,
            Person.name.ilike(f"%{person_name}%")
        ).first()
        if person:
            person_id = person.id

    if person_id is None:
        # Cannot log interaction without a person; maybe create one?
        return None

    interaction = Interaction(
        user_id=user_id,
        person_id=person_id,
        interaction_type=interaction_type,
        logged_at=logged_at or datetime.utcnow(),
        source="calendar",
        calendar_event_id=calendar_event_id,
        confidence_score=confidence_score,
        inference_status="inferred",
    )
    db.session.add(interaction)
    db.session.commit()
    enqueue(user_id, RELATIONSHIPS_INTERACTION_INFERRED, {...})
    return interaction.id
```

---

## 10. Backward Compatibility & Non-Breaking Evolution

### 10.1 Existing Manual Workflows

- **All existing manual entry paths remain fully functional.**
- Manual records have `source="manual"`, `calendar_event_id=NULL`, `confidence_score=NULL`, `inference_status=NULL`.
- No changes to existing API contracts for manual entry.

### 10.2 Migration Safety

- All new columns are **nullable** or have **defaults**.
- Existing rows get `source="manual"` via server_default.
- No data transformations on existing records.
- FK to `calendar_event` is nullable; existing records have `NULL`.

### 10.3 Feature Flags

```python
# lifeos/config.py

ENABLE_CALENDAR_INTERPRETER = os.environ.get("ENABLE_CALENDAR_INTERPRETER", "true").lower() in ("1", "true")
```

If disabled, calendar events are stored but not interpreted.

---

## 11. Future Extensions

### 11.1 External Calendar Sync (Phase 2)

- `lifeos/domains/calendar/services/sync_service.py`
- Google Calendar API integration
- Apple Calendar (CalDAV) integration
- Sync tasks in `lifeos/domains/calendar/tasks.py`

### 11.2 ML-Based Classification (Phase 3)

- Replace rule-based classifier with ML model
- Train on confirmed/rejected interpretations
- Improve confidence scores over time

### 11.3 Recurrence Handling (Phase 2)

- Parse RRULE strings
- Generate recurring event instances
- Link instances to parent event

---

## 12. Testing Strategy

### 12.1 Unit Tests

- `lifeos/tests/test_calendar_service.py` — CRUD operations
- `lifeos/tests/test_calendar_interpreter.py` — Classification rules
- `lifeos/tests/test_domain_inferred_*.py` — Per-domain inferred record creation

### 12.2 Integration Tests

- `lifeos/tests/test_calendar_api.py` — API endpoints
- `lifeos/tests/test_calendar_to_domain_flow.py` — End-to-end calendar → interpretation → domain record

### 12.3 Migration Tests

- Verify migration applies cleanly to existing DB with data
- Verify existing records get correct defaults
- Verify rollback works

---

## 13. Deliverables Summary

| Component | Location | Status |
|-----------|----------|--------|
| Calendar domain models | `lifeos/domains/calendar/models/` | New |
| Calendar domain services | `lifeos/domains/calendar/services/` | New |
| Calendar domain controllers | `lifeos/domains/calendar/controllers/` | New |
| Calendar domain schemas | `lifeos/domains/calendar/schemas/` | New |
| Calendar domain events | `lifeos/domains/calendar/events.py` | New |
| Calendar Interpreter | `lifeos/core/interpreter/` | New |
| Domain model extensions | All domain `models/*.py` | Extend |
| Domain service extensions | All domain `services/*.py` | Extend |
| Domain event extensions | All domain `events.py` | Extend |
| Migration: Calendar tables | `20251207_calendar_initial.py` | New |
| Migration: Inferred columns | `20251207_domains_inferred_columns.py` | New |

---

_End of Calendar-First Architecture Specification._
