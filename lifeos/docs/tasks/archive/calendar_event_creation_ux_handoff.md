# LifeOS - Calendar Event Creation UX Hand-Off Specification

Audience: Frontend Engineering, QA
Owner: Product / Architecture
Sprint Context: Phase 1 - UX Alignment Sprint
Status: Completed (Archived)

---

## 1. Purpose
This specification defines the required UX behavior and defaults for the "Add / Edit Event" flow in LifeOS Calendar.

Goals:
- Minimize cognitive and interaction cost
- Align event creation with human intent
- Treat time as a first-class, legible concept
- Remove unnecessary manual configuration

This is not a visual redesign request. It is a behavioral and interaction contract.

---

## 2. Core UX Principle
Event creation should assume the most probable intent and require correction, not construction.

---

## 3. Required Default Behavior (Non-Negotiable)

### 3.1 Temporal Defaults
When a user opens "New Event":
- Start time:
  - Defaults to current local time, rounded to the nearest logical increment (e.g., 5 or 15 minutes)
  - Uses locale-aware 12-hour format with AM/PM where applicable
- End time:
  - Defaults to Start + 1 hour
  - Automatically inherits the same calendar day as Start
- End date:
  - Must not require manual input unless the user explicitly changes it

No empty date or time fields are allowed on initial render.

### 3.2 Same-Day Assumption
- Events are assumed to be single-day events by default.
- The UI must not require duplicate date entry.
- Cross-day events are treated as an explicit override, not the baseline.

---

## 4. Time Interaction Model

### 4.1 Unified Time Control
- Date and time must be treated as a single conceptual control.
- Users should not be forced to mentally coordinate:
  - date field + time field + end field

Frontend may implement this as:
- A combined picker, or
- A coordinated start/end control

Behavior must reflect one temporal object, not separate inputs.

### 4.2 Duration-First Editing (Preferred)
The system must support duration-based adjustment as a first-class interaction.

Required preset durations:
- 15 minutes
- 30 minutes
- 45 minutes
- 1 hour (default)

Selecting a preset:
- Updates End time automatically
- Preserves Start time
- Does not require manual typing

Manual time entry must remain available as an override.

---

## 5. Time Format and Localization
- Default display format: 12-hour with AM/PM
- Format must be locale-aware
- Internal storage format is unchanged (implementation detail, not surfaced)

QA must verify correct formatting across supported locales.

---

## 6. Color Selection Constraints

### 6.1 Simplification Requirement
- Replace unrestricted color picker with a curated palette.
- Exactly 10 predefined colors.
- Colors must be:
  - Visually distinct
  - Mutually harmonious
  - Reusable across the system

Color is secondary metadata, not a primary decision point.

---

## 7. Progressive Disclosure Rules
The following elements must not compete with primary input:
- End date/time adjustments
- Duration overrides
- Advanced options (location, tags, privacy)

Primary flow must emphasize:
1) Title
2) When it happens
3) Save

Everything else is supportive.

---

## 8. Explicit Non-Goals
Out of scope:
- Natural language parsing ("Dinner at 7")
- AI-assisted scheduling
- Recurrence rules
- Multi-event creation
- Visual styling changes unrelated to behavior

---

## 9. QA Acceptance Criteria

### 9.1 Default Creation
Opening "New Event" shows:
- Start = now
- End = +1 hour
- Same day
- Valid save without touching date/time fields

### 9.2 Duration Presets
- Selecting each preset correctly adjusts End time
- No date drift occurs
- Presets override manual end time cleanly

### 9.3 Same-Day Integrity
- Editing Start time does not force End date changes
- End date only diverges when explicitly changed

### 9.4 Localization
- Time format reflects locale
- AM/PM displays correctly
- No mixed formats appear

### 9.5 Color Palette
- Only 10 colors are selectable
- Selected color persists correctly

---

## 10. Success Definition
This change is successful if:
- A user can create a valid event in one continuous motion
- Manual typing of date/time is optional, not required
- The system feels like it is helping, not asking

---

## 11. Architectural Note
These defaults and behaviors are now part of the LifeOS temporal contract. Future calendar features must conform unless explicitly overridden by product decision.
