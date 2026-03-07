# Calendar-First Architecture - Frontend Update

**Date:** 2025-12-07  
**Status:** Complete  
**Backend Spec:** `CALENDAR_FIRST_ARCHITECTURE.md`, `CALENDAR_FIRST_IMPLEMENTATION_UPDATE.md`

---

## Overview

Frontend implementation for the Calendar-First Architecture initiative. The calendar is now the primary input surface for capturing life activities, with automatic interpretation into domain records (finance, health, habits, skills, projects, relationships).

---

## New Files

### Templates

#### `lifeos/templates/calendar/index.html`
Main calendar view with:
- **Quick Stats Cards**: Events today, this week, pending interpretations
- **Date Range Filter**: Start/end date pickers, source filter
- **Events List**: Grouped by date, color-coded, with tags and duration
- **Create/Edit Modal**: Full event form with all fields
- **Event Detail Modal**: View details, interpretations, edit/delete actions
- **Auth Integration**: Login hint, disabled state when not authenticated

#### `lifeos/templates/calendar/review.html`
Interpretation review workflow:
- **Domain Filter**: Filter by finance, health, habits, skills, projects, relationships
- **Stats Summary**: Pending, confirmed, rejected counts
- **Interpretation Cards**: Domain icon, record type, confidence score, matched keywords
- **Action Buttons**: Confirm (creates domain record), Reject, Ignore
- **Animated Removal**: Cards animate out on action completion
- **How It Works**: User education section explaining the workflow

### JavaScript Module

#### `lifeos/static/js/calendar-api.js`

**Public API (exposed as `window.lifeosCalendar`):**

| Function | Description |
|----------|-------------|
| `listEvents(options)` | List events with date range, source, pagination |
| `getEvent(eventId)` | Get single event with interpretations |
| `createEvent(data)` | Create new calendar event |
| `updateEvent(eventId, data)` | Update existing event |
| `deleteEvent(eventId)` | Delete event |
| `getPendingInterpretations(options)` | Get pending interpretations for review |
| `updateInterpretation(id, status)` | Update interpretation status |
| `confirmInterpretation(id)` | Confirm → creates domain record |
| `rejectInterpretation(id)` | Reject interpretation |
| `ignoreInterpretation(id)` | Ignore interpretation |
| `getEventsForDate(date)` | Utility: events for a specific day |
| `getEventsThisWeek()` | Utility: events for current week |
| `getPendingCount(domain?)` | Utility: count pending interpretations |
| `DOMAINS` | Constants: domain metadata (name, icon, color) |
| `SOURCES` | Constants: source labels |

**Usage:**
```javascript
const { listEvents, createEvent, confirmInterpretation } = window.lifeosCalendar;

// List events for a date range
const events = await listEvents({
  start_date: '2025-12-01T00:00:00',
  end_date: '2025-12-31T23:59:59',
  source: 'manual'
});

// Create a new event
const event = await createEvent({
  title: 'Gym workout',
  start_time: '2025-12-07T18:00:00',
  end_time: '2025-12-07T19:00:00',
  location: 'Fitness Center',
  tags: ['fitness', 'health']
});

// Confirm an interpretation (creates domain record)
await confirmInterpretation(42);
```

---

## Modified Files

### `lifeos/templates/layouts/base.html`

**Changes:**
1. Added Calendar link to navigation (first position, with 📅 icon)
2. Added `calendar-api.js` to global script loading
3. Updated module availability check to include `lifeosCalendar`

**Navigation Order:**
```
📅 Calendar | Finance | Journal | Trial Balance | ... | Projects
```

---

## API Endpoints Used

### Calendar Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendar/events` | List events (query: `start_date`, `end_date`, `source`, `limit`, `offset`) |
| GET | `/api/calendar/events/<id>` | Get single event with interpretations |
| POST | `/api/calendar/events` | Create event |
| PATCH | `/api/calendar/events/<id>` | Update event |
| DELETE | `/api/calendar/events/<id>` | Delete event |

### Interpretations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/calendar/interpretations/pending` | List pending interpretations (query: `domain`, `limit`, `offset`) |
| PATCH | `/api/calendar/interpretations/<id>` | Update status (`confirmed`, `rejected`, `ignored`) |

---

## UI/UX Design

### Color Palette (Domain Icons)

| Domain | Icon | Color |
|--------|------|-------|
| Finance | 💰 | `#0b4f9c` |
| Health | ❤️ | `#dc2626` |
| Habits | 🎯 | `#7c3aed` |
| Skills | 📚 | `#059669` |
| Projects | 📁 | `#ea580c` |
| Relationships | 👥 | `#db2777` |

### Confidence Score Display

| Score Range | Label | Color |
|-------------|-------|-------|
| ≥ 90% | Very High | `#059669` |
| ≥ 70% | High | `#1d7a36` |
| ≥ 50% | Medium | `#d97706` |
| < 50% | Low | `#b3352f` |

### Interpretation Status Badges

| Status | Background | Text |
|--------|------------|------|
| Confirmed | `#d4edda` | `#155724` |
| Rejected | `#f8d7da` | `#721c24` |
| Inferred | `#fff3cd` | `#856404` |

---

## User Workflow

### 1. Create Calendar Event
```
User clicks "+ New Event"
  → Modal opens with form
  → User fills: title, start/end time, location, tags, etc.
  → Submit
  → Event created
  → Interpreter analyzes event (backend)
  → Interpretations created if patterns match
```

### 2. Review Interpretations
```
User clicks "Review Pending" or navigates to /calendar/review
  → Sees list of pending interpretations
  → Each card shows: domain, record type, confidence, matched keywords
  → User clicks:
    • "Confirm" → Domain record created (e.g., workout logged)
    • "Reject" → Interpretation dismissed
    • "Ignore" → Skipped for now
  → Card animates out
  → Stats update
```

### 3. View Event Details
```
User clicks an event in the list
  → Detail modal opens
  → Shows: time, location, description, tags, source
  → Shows interpretations with status badges
  → Can edit or delete event
```

---

## Feature Flags

| Config Key | Default | Description |
|------------|---------|-------------|
| `ENABLE_CALENDAR_INTERPRETER` | `True` | Enable/disable automatic interpretation |

---

## Testing Checklist

- [ ] Calendar index loads with event list
- [ ] Date filter works correctly
- [ ] Source filter works correctly
- [ ] Create event modal opens and saves
- [ ] Edit event modal populates and saves
- [ ] Delete event works with confirmation
- [ ] Event detail modal shows interpretations
- [ ] Review page loads pending interpretations
- [ ] Domain filter works on review page
- [ ] Confirm interpretation creates record
- [ ] Reject interpretation updates status
- [ ] Ignore interpretation updates status
- [ ] Cards animate out on action
- [ ] Stats update after actions
- [ ] Auth sync works (login/logout)
- [ ] Keyboard shortcuts (Escape to close)
- [ ] Pending count badge updates

---

## Dependencies

- `window.lifeosAuth` - Authentication headers
- `window.lifeosCalendar` - Calendar API module (new)

All modules loaded globally via `base.html`.

---

## Architecture Notes

### Calendar as Primary Input

The calendar is designed as the **single entry point** for life data:

1. **User creates event**: "Gym workout at Fitness Center"
2. **Interpreter classifies**: Domain=health, RecordType=workout, Confidence=85%
3. **Interpretation created**: Status=inferred
4. **User confirms**: Status=confirmed, workout record created in health domain
5. **Domain record linked**: `calendar_event_id` set on workout

### Inferred Record Fields

All domain models now include:
- `source`: 'manual', 'calendar', 'import', 'api'
- `calendar_event_id`: FK to calendar_event
- `confidence_score`: 0.0-1.0 inference confidence
- `inference_status`: 'inferred', 'confirmed', 'rejected'

### Cross-Domain Integration

```
Calendar Event
    │
    ├─── Interpretation (health/workout) → Workout record
    │
    ├─── Interpretation (finance/transaction) → Transaction record
    │
    └─── Interpretation (relationships/interaction) → Interaction record
```

---

## Next Steps

1. **External Sync**: Google Calendar OAuth + Apple Calendar integration
2. **ML Enhancement**: Replace regex classification with trained model
3. **Recurring Events**: RRULE parsing and expansion
4. **Notifications**: Alert users when interpretations need review
5. **Weekly Digest**: Summarize confirmed records from calendar events
