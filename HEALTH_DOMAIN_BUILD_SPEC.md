# HEALTH_DOMAIN_BUILD_SPEC.md

**Version:** 1.0
**Date:** 2026-03-27
**Author:** Opus (architectural specification)
**Executor:** Sonnet 4.6 (file-by-file implementation)
**Status:** Approved feature set only — no scope expansion permitted

---

## 0. Build Philosophy & Constraints

### What This Page IS

A calm, editorial surface that answers one question: **"How is my baseline and what needs attention?"** (UI/UX Constitution section 5, Health contract). The user opens this page to observe trends, not to obsess over numbers. It is a gentle record of how they feel — body weight trajectory, training consistency, and nutrition quality — presented with the emotional restraint of a botanical journal.

### What This Page Is NOT

- Not a fitness dashboard with dense KPI tiles
- Not a calorie counter or macro tracker
- Not a medical or diagnostic tool
- Not a gamified body-metrics scoreboard
- Not a cross-domain analytics surface
- Not a predictive health oracle

### Breadth-First Rule

Every section of this spec receives approximately 20% depth before any section reaches 80%. This ensures structural coverage across all 7 surfaces before deep implementation of any single one. Sonnet must build all files to skeleton/functional state before polishing any individual component.

### Emotional Contract (Binding — Constitution section 1)

- **Allowed tone:** calm, encouraged, observational
- **Forbidden tone:** urgent, guilty, shaming, prescriptive
- **Phrasing examples:** "It looks like...", "Based on recent activity...", "You've been consistent this week"
- **Forbidden phrasing:** "You should...", "You failed to...", "You must...", "At this rate you'll..."

### Later-Wave Domain Rules (Constitution section 12.1)

Health is a **later-wave domain** (Phase 7.1). This means:
- Stronger caution labels required on any derived insight
- Explicit scope boundaries on all interpretive text
- Never infer diagnosis, treatment, or clinical framing
- All interpretive text must be preceded by uncertainty language

### Design System Binding

Every component must follow The Botanical Editorial design system (DESIGN.md). The health domain uses these specific accent tokens:

| Token | Value | Usage |
|-------|-------|-------|
| `health-accent-bg` | `#fce8e4` (clay rose) | Icon containers, selected card backgrounds |
| `health-accent-dark` | `#8b4a3a` (rust) | Selected card border, active icon color, micro-label eyebrows |
| `health-gradient` | `linear-gradient(135deg, #fdf0ed, #f5ddd6)` | Selected card gradient fill |

These accent tokens apply **only on selection or active state**. Unselected cards use `surface-container-lowest` (#ffffff) with standard sage palette.

---

## 1. Approved Feature Set

### 1.1 Baseline Awareness

**Description:** Goal-aware body trajectory, not raw numbers.

**Logic:**
- User sets a weight goal (e.g., 65kg to 70kg bulk)
- Page shows: current weight, delta since tracking start, direction label (bulk / cut / maintain)
- Narrative framing: "You're at 66.2 kg, +1.2 kg since you started tracking"
- Direction-aware: understands whether weight going up is good (bulk) or concerning (cut)
- Computed client-side from `GET /api/health/biometrics` weight history

**Tone:** Progress narrative. "Your weight has moved from X to Y over the past N weeks." Never: "You need to gain X more kg" or "At this rate you'll reach your goal by August."

**Backend dependency:** Goal storage (weight target, direction) does not exist. See section 2 — flagged as `REQUIRES BACKEND WORK`. Without goals, baseline awareness degrades to: current weight + 30-day trend direction (up/down/stable) + delta from first recorded weight. This degraded mode is fully buildable with existing endpoints.

### 1.2 Nutrition Sufficiency

**Description:** Daily sufficiency signal, not calorie counting.

**Logic:**
- Three visual states: `not enough` | `on track` | `surplus`
- `quality_score` (1-5) is the primary visible metric, not raw calories
- Weekly pattern: 7-day dot row showing days with meals logged (analogous to habits completion dots)
- Answers: "Am I consistently eating enough to support my goal?"
- Derived from `GET /api/health/nutrition` filtered to current week

**Tone:** Supportive. "You've been fueling well this week." Never: "You're in a calorie deficit" or "You missed meals on 3 days."

**Backend dependency:** Calorie target storage does not exist. Without a target, sufficiency degrades to: meal logging consistency (days with >= 3 meals logged) + average quality_score trend. The 3-state signal (`not enough` / `on track` / `surplus`) requires a target — without it, show only the quality dot row and logging consistency count. Flagged as `REQUIRES BACKEND WORK`.

### 1.3 Workout Programming

**Description:** Training consistency and progression tracking.

**Logic:**
- Sessions this week vs weekly display (e.g., "3 sessions this week")
- Workout type distribution: are different types represented?
- Intensity trend: is average intensity stable, increasing, or decreasing over the past 4 weeks?
- All derived from `GET /api/health/workouts` with date range filters
- Answers: "Am I training consistently?"

**Tone:** Observational. "3 sessions logged this week." Never: "You're behind on your training schedule" or "You should increase intensity."

**Backend dependency:** Weekly workout target does not exist. Without a target, show only the absolute count ("3 sessions this week") without "of N target" framing. Fully buildable with existing endpoints.

### 1.4 Editorial Presentation

**Description:** Botanical Editorial applied to health data.

**Logic:**
- Newsreader headlines: "Your Week So Far", "Recent Training"
- Clay-rose tinted summary cards on health overview
- Manrope micro-labels: `BIOMETRICS`, `NUTRITION`, `TRAINING`
- Generous whitespace, vertical scan priority
- Specimen card pattern with `border-radius: 0 16px 16px 16px`
- Domain accent only on selected/active cards

**No backend dependency.** Purely presentational.

---

## 2. API Contract (Existing Endpoints Only)

All endpoints are prefixed with `/api/health`. Authentication: JWT Bearer token required. CSRF: `X-CSRF-Token` header required on POST/PATCH/DELETE mutations.

### 2.1 Available Endpoints

#### `GET /api/health/biometrics`

List biometric entries for the authenticated user, ordered by date descending.

**Query parameters:**
| Param | Type | Default | Constraints |
|-------|------|---------|-------------|
| `page` | int | `1` | >= 1 |
| `per_page` | int | `50` | >= 1, <= 200 |
| `start_date` | ISO date string | `null` | Optional |
| `end_date` | ISO date string | `null` | Optional |

**Response (200):**
```json
{
  "ok": true,
  "items": [
    {
      "id": 1,
      "date": "2026-03-27",
      "weight": 66.2,
      "body_fat_pct": 18.5,
      "resting_hr": 62,
      "energy_level": 4,
      "stress_level": 2,
      "notes": "Feeling good after morning walk",
      "created_at": "2026-03-27T08:30:00"
    }
  ],
  "page": 1,
  "pages": 1,
  "total": 1
}
```

All numeric fields in `items` except `id` are nullable. `weight` and `body_fat_pct` are floats. `resting_hr`, `energy_level`, `stress_level` are ints. `energy_level` and `stress_level` range 1-5.

#### `POST /api/health/biometrics`

Create a new biometric entry. One entry per date per user (duplicate returns 409).

**Request body:**
```json
{
  "date": "2026-03-27",
  "weight": 66.2,
  "body_fat_pct": 18.5,
  "resting_hr": 62,
  "energy_level": 4,
  "stress_level": 2,
  "notes": "Optional notes"
}
```

All fields except `date` are optional. `date` defaults to today if omitted. `energy_level` and `stress_level` must be 1-5. `weight` and `body_fat_pct` must be >= 0.

**Response (201):** `{ "ok": true, "biometric": { ...same shape as list item... } }`
**Response (409):** `{ "ok": false, "error": "duplicate" }` — entry already exists for this date
**Response (400):** `{ "ok": false, "error": "validation_error", "details": [...] }`

#### `GET /api/health/workouts`

List workout entries for the authenticated user, ordered by date descending.

**Query parameters:** Same as biometrics (`page`, `per_page`, `start_date`, `end_date`).

**Response (200):**
```json
{
  "ok": true,
  "items": [
    {
      "id": 1,
      "date": "2026-03-27",
      "workout_type": "strength",
      "duration_minutes": 45,
      "intensity": "high",
      "calories_est": 350.0,
      "notes": "Upper body focus",
      "created_at": "2026-03-27T10:00:00"
    }
  ],
  "page": 1,
  "pages": 1,
  "total": 1
}
```

`workout_type` is a free-form string (max 64 chars). `intensity` is one of `"low"`, `"medium"`, `"high"`. `calories_est` is nullable float. `duration_minutes` is int >= 0.

#### `POST /api/health/workouts`

Create a new workout entry.

**Request body:**
```json
{
  "date": "2026-03-27",
  "workout_type": "strength",
  "duration_minutes": 45,
  "intensity": "high",
  "calories_est": 350.0,
  "notes": "Optional notes"
}
```

`workout_type` (required, 1-64 chars), `duration_minutes` (default 0, >= 0), `intensity` (default `"medium"`, must be `"low"` | `"medium"` | `"high"`). `date` defaults to today. `calories_est` and `notes` are optional.

**Response (201):** `{ "ok": true, "workout": { ...same shape as list item... } }`
**Response (400):** `{ "ok": false, "error": "validation_error" }`

#### `GET /api/health/nutrition`

List nutrition log entries for the authenticated user, ordered by date descending.

**Query parameters:** Same as biometrics (`page`, `per_page`, `start_date`, `end_date`).

**Response (200):**
```json
{
  "ok": true,
  "items": [
    {
      "id": 1,
      "date": "2026-03-27",
      "meal_type": "lunch",
      "items": ["chicken", "rice", "vegetables"],
      "calories_est": 650.0,
      "quality_score": 4,
      "created_at": "2026-03-27T12:30:00"
    }
  ],
  "page": 1,
  "pages": 1,
  "total": 1
}
```

`meal_type` is one of `"breakfast"`, `"lunch"`, `"dinner"`, `"snack"`, `"other"`. `items` is an array of strings (parsed server-side from comma/newline-separated text). `calories_est` is nullable float. `quality_score` is nullable int 1-5.

**Note:** The `NutritionCreate` schema requires an `items` field (string, 1-4096 chars) — this is the raw text input that gets parsed into the array on read. Send a comma-separated string: `"chicken, rice, vegetables"`.

#### `POST /api/health/nutrition`

Create a new nutrition log entry.

**Request body:**
```json
{
  "date": "2026-03-27",
  "meal_type": "lunch",
  "items": "chicken, rice, vegetables",
  "calories_est": 650.0,
  "quality_score": 4
}
```

`meal_type` (required, must be `"breakfast"` | `"lunch"` | `"dinner"` | `"snack"` | `"other"`). `items` (required, 1-4096 chars string). `date` defaults to today. `calories_est` and `quality_score` optional. `quality_score` must be 1-5.

**Response (201):** `{ "ok": true, "nutrition": { ...same shape as list item... } }`
**Response (400):** `{ "ok": false, "error": "validation_error" }`

#### `GET /api/health/summary/daily`

Aggregated daily summary across all three health entities.

**Query parameters:**
| Param | Type | Default |
|-------|------|---------|
| `date` | ISO date string | today |

**Response (200):**
```json
{
  "ok": true,
  "summary": {
    "date": "2026-03-27",
    "biometric": {
      "id": 1, "date": "2026-03-27", "weight": 66.2,
      "body_fat_pct": 18.5, "resting_hr": 62,
      "energy_level": 4, "stress_level": 2,
      "notes": null, "created_at": "2026-03-27T08:30:00"
    },
    "workouts": {
      "count": 1,
      "total_duration_minutes": 45,
      "by_type": { "strength": 1 }
    },
    "nutrition": {
      "count": 3,
      "calories_est_total": 1850.0
    },
    "energy_level": 4,
    "stress_level": 2
  }
}
```

`biometric` is null if no entry for that date. `workouts.count` and `nutrition.count` can be 0.

#### `GET /api/health/summary/weekly`

Aggregated weekly summary with biometric averages.

**Query parameters:**
| Param | Type | Default |
|-------|------|---------|
| `start` | ISO date string | today |

Week runs from `start` to `start + 6 days`.

**Response (200):**
```json
{
  "ok": true,
  "summary": {
    "week_start": "2026-03-23",
    "week_end": "2026-03-29",
    "biometric": {
      "average_weight": 66.1,
      "average_resting_hr": 63.0,
      "average_energy_level": 3.5,
      "average_stress_level": 2.2
    },
    "workouts": {
      "count": 3,
      "total_duration_minutes": 135,
      "by_type": { "strength": 2, "cardio": 1 }
    },
    "nutrition": {
      "count": 15,
      "calories_est_total": 9250.0
    }
  }
}
```

All `biometric` averages are nullable floats (null if no data for the week).

### 2.2 Missing Endpoints (REQUIRES BACKEND WORK)

The following endpoints do not exist. Frontend surfaces that depend exclusively on these are marked accordingly in section 4.

| Endpoint | Purpose | Blocks |
|----------|---------|--------|
| `GET /api/health/biometrics/:id` | Individual biometric detail | Detail panel deep view |
| `PATCH /api/health/biometrics/:id` | Edit biometric entry | Edit flow |
| `DELETE /api/health/biometrics/:id` | Delete biometric entry | Delete flow |
| `GET /api/health/workouts/:id` | Individual workout detail | Detail panel deep view |
| `PATCH /api/health/workouts/:id` | Edit workout entry | Edit flow |
| `DELETE /api/health/workouts/:id` | Delete workout entry | Delete flow |
| `GET /api/health/nutrition/:id` | Individual nutrition detail | Detail panel deep view |
| `PATCH /api/health/nutrition/:id` | Edit nutrition entry | Edit flow |
| `DELETE /api/health/nutrition/:id` | Delete nutrition entry | Delete flow |
| `POST /api/health/goals` | Set weight/workout/nutrition goals | Goal-aware baseline, sufficiency signal |
| `GET /api/health/goals` | Retrieve current goals | Goal-aware baseline, sufficiency signal |
| `PATCH /api/health/workouts/:id/confirm` | Confirm inferred workout | Inferred record flow |
| `PATCH /api/health/nutrition/:id/confirm` | Confirm inferred nutrition | Inferred record flow |
| `GET /api/insights?domain=health` | Health insight records | Insight cards surface |

**Impact:** Without goals endpoints, baseline awareness, nutrition sufficiency, and workout programming features operate in **degraded mode** — showing observed trends without goal-relative framing. Without CRUD endpoints (PATCH/DELETE), records are create-only; no edit or delete UI should be rendered. Without confirm endpoints, inferred record confirm/reject flow cannot be built — **skip this surface entirely**. Without insight records endpoint, insight cards surface cannot be built — **skip this surface**.

---

## 3. Component Registry

All new files live under `frontend/app/(app)/health/` and `frontend/lib/api/`. Sonnet must create these files in the order specified in section 6 (Dependency Map).

| # | Component Name | File Path | Responsibility | Max Lines |
|---|---------------|-----------|----------------|-----------|
| 1 | `healthApi` | `frontend/lib/api/health.ts` | TypeScript types + API client methods for all health endpoints | 120 |
| 2 | `HealthPage` | `frontend/app/(app)/health/page.tsx` | Main page: master-detail layout, state management, query orchestration, mobile drawer | 800 |
| 3 | `HealthOverviewCards` | `frontend/app/(app)/health/_components/HealthOverviewCards.tsx` | Three summary cards (biometrics, training, nutrition) for the overview section | 150 |
| 4 | `BiometricTrendCard` | `frontend/app/(app)/health/_components/BiometricTrendCard.tsx` | Weight trend visualization — 30-day sparkline with direction indicator | 120 |
| 5 | `WorkoutSummaryCard` | `frontend/app/(app)/health/_components/WorkoutSummaryCard.tsx` | Weekly workout count, type distribution pills, intensity label | 100 |
| 6 | `NutritionSummaryCard` | `frontend/app/(app)/health/_components/NutritionSummaryCard.tsx` | 7-day quality dot row, meal logging consistency, quality score average | 100 |
| 7 | `HealthDetailPanel` | `frontend/app/(app)/health/_components/HealthDetailPanel.tsx` | Right-side detail panel: shows selected entity's history and stats | 180 |
| 8 | `BiometricLogForm` | `frontend/app/(app)/health/_components/BiometricLogForm.tsx` | Form for logging weight, body fat, vitals, energy, stress | 130 |
| 9 | `WorkoutLogForm` | `frontend/app/(app)/health/_components/WorkoutLogForm.tsx` | Form for logging workout type, duration, intensity | 110 |
| 10 | `NutritionLogForm` | `frontend/app/(app)/health/_components/NutritionLogForm.tsx` | Form for logging meal type, items, quality score | 110 |
| 11 | `HealthEmptyState` | `frontend/app/(app)/health/_components/HealthEmptyState.tsx` | Motivational onboarding card when no health data exists | 60 |
| 12 | `WeightSparkline` | `frontend/app/(app)/health/_components/WeightSparkline.tsx` | Compact SVG sparkline for 30-day weight trend | 80 |
| 13 | `WeeklyWorkoutDots` | `frontend/app/(app)/health/_components/WeeklyWorkoutDots.tsx` | 7-day dot row showing days with workouts logged | 50 |
| 14 | `NutritionQualityDots` | `frontend/app/(app)/health/_components/NutritionQualityDots.tsx` | 7-day dot row showing meal quality scores by day | 50 |

**Total new files: 14**
**Estimated total lines: ~2,060** (within 20% depth budget across 7 surfaces)

---

## 4. Surface Specs

### 4.1 Health Overview Page (Surface 1)

**Primary question:** "How is my baseline and what needs attention?"
**Primary action:** Log (biometric, workout, or nutrition — single CTA that opens a contextual form)
**File:** `frontend/app/(app)/health/page.tsx`

#### Layout

```
Desktop (>= 1024px):
+----------------------------------------------------------+
| HEALTH (micro-label)                            [LOG v]  |
| Your Wellbeing (Newsreader Light 300, 2rem)              |
| A gentle record of how you feel. (Manrope 0.9375rem)    |
+------------------------------------+---------------------+
| Left (60%): Overview + History     | Right (40%): Detail |
|                                    |                     |
| [HealthOverviewCards]              | [HealthDetailPanel] |
|   - BiometricTrendCard             |   - Selected item   |
|   - WorkoutSummaryCard             |   - History list    |
|   - NutritionSummaryCard           |   - Stats           |
|                                    |                     |
| [History Section]                  |                     |
|   - Tabbed: Biometrics |           |                     |
|     Workouts | Nutrition           |                     |
|   - List of recent entries         |                     |
+------------------------------------+---------------------+

Mobile (< 1024px):
+---------------------------+
| HEALTH / Your Wellbeing   |
| [LOG v]                   |
+---------------------------+
| [HealthOverviewCards]     |
|   (stacked vertically)   |
+---------------------------+
| [History Section]         |
|   (tabbed, full width)   |
+---------------------------+
| [Mobile Drawer]           |
|   (detail panel content) |
+---------------------------+
```

#### Data Sources

| Data | Endpoint | Query | Cache Key |
|------|----------|-------|-----------|
| Today's summary | `GET /api/health/summary/daily` | `?date={today}` | `['health', 'daily', today]` |
| Weekly summary | `GET /api/health/summary/weekly` | `?start={monday}` | `['health', 'weekly', monday]` |
| Biometric history | `GET /api/health/biometrics` | `?per_page=30` | `['health', 'biometrics']` |
| Workout history | `GET /api/health/workouts` | `?per_page=30` | `['health', 'workouts']` |
| Nutrition history | `GET /api/health/nutrition` | `?per_page=30` | `['health', 'nutrition']` |

#### Design Tokens Used

| Element | Token | Value |
|---------|-------|-------|
| Page background | `background` | `#f8faf2` |
| Card fill | `surface-container-lowest` | `#ffffff` |
| Section background | `surface-container-low` | `#f1f5eb` |
| Card radius | clipped specimen | `0 16px 16px 16px` |
| Card shadow (rest) | tinted sage | `0 8px 24px rgba(46, 52, 43, 0.06)` |
| Card shadow (hover) | tinted sage hover | `0 30px 60px rgba(46, 52, 43, 0.08)` |
| Card padding | minimum 2rem | `32px` |
| Page title | Newsreader Light 300 | `2rem`, `-0.03em`, `#4b6646` |
| Micro-label | Manrope Bold 700 uppercase | `0.6875rem`, `+0.05em`, `#8b4a3a` |
| Body text | Manrope Regular 400 | `0.875rem`, `1.65 line-height`, `#5a6157` |
| Primary button | gradient pill | `linear-gradient(135deg, #4b6646, #3f5a3a)`, `rounded-full` |

#### Interaction Pattern

- **LOG button:** Primary gradient pill button in page header. On click, opens a dropdown or modal with three options: "Log Biometrics", "Log Workout", "Log Meal". Each opens its respective form component.
- **Card selection:** Clicking a history entry in the left panel selects it and populates the detail panel (desktop) or opens the mobile drawer (mobile).
- **Tab switching:** History section has three tabs (Biometrics, Workouts, Nutrition). Each tab fetches its own list. Selected tab persists in component state.
- **Card entrance animation:** Staggered reveal — `opacity: 0 -> 1`, `translateY(8px -> 0)`, 260ms ease-out, 35ms delay between cards (mirrors habits HAB pattern).

#### Mobile Behavior

- Master-detail collapses to single column
- Detail panel moves into a draggable bottom drawer (86vh max height, `border-radius: 16px 16px 0 0`)
- Drawer has 44px drag handle with 4px centered bar
- Drawer physics: 90% resistance up to 120px, 35% past 120px. Close on >95px drag or >0.65px/ms flick velocity
- LOG button moves to page header for thumb reach
- Overview cards stack vertically with 16px gap

#### State Variables (for Sonnet)

```typescript
// UI state
const [activeTab, setActiveTab] = useState<'biometrics' | 'workouts' | 'nutrition'>('biometrics')
const [selectedItem, setSelectedItem] = useState<{ type: string; id: number } | null>(null)
const [showLogForm, setShowLogForm] = useState<'biometric' | 'workout' | 'nutrition' | null>(null)
const [isCompactViewport, setIsCompactViewport] = useState(false)
const [mobileDetailOpen, setMobileDetailOpen] = useState(false)

// Drawer drag state
const [drawerOffsetY, setDrawerOffsetY] = useState(0)
const [drawerDragging, setDrawerDragging] = useState(false)
const drawerPointerId = useRef<number | null>(null)
const drawerDragStartY = useRef<number | null>(null)

// Reduce motion
const [reduceMotion, setReduceMotion] = useState(false)
```

---

### 4.2 Biometric Logging + History (Surface 2)

**File (form):** `frontend/app/(app)/health/_components/BiometricLogForm.tsx`
**Rendered in:** Modal overlay triggered from page LOG button or empty state CTA

#### Props Interface

```typescript
interface BiometricLogFormProps {
  onClose: () => void
  onSuccess: () => void  // triggers query invalidation
}
```

#### Form Fields

| Field | Type | Label | Input | Constraints | Required |
|-------|------|-------|-------|-------------|----------|
| `date` | date | "Date" | native date input | defaults to today | Yes |
| `weight` | number | "Weight (kg)" | number input, step 0.1 | >= 0 | No |
| `body_fat_pct` | number | "Body fat (%)" | number input, step 0.1 | >= 0 | No |
| `resting_hr` | number | "Resting heart rate" | number input, step 1 | >= 0 | No |
| `energy_level` | 1-5 | "Energy" | 5-dot selector (tap to rate) | 1-5 | No |
| `stress_level` | 1-5 | "Stress" | 5-dot selector (tap to rate) | 1-5 | No |
| `notes` | text | "Notes" | textarea, 3 rows | max 4096 chars | No |

#### Layout

- Centered modal (mirrors habits "Habit Studio" pattern)
- `position: fixed`, `inset: 0`, `z-index: 70`
- Backdrop: `rgba(22, 33, 49, 0.44)`, `backdrop-filter: blur(6px)`
- Form card: `surface-container-lowest` (#ffffff), `border-radius: 0 16px 16px 16px`, max-width 480px
- Padding: 32px
- Two-column grid for weight + body fat on desktop; stacked on mobile
- Energy/stress use a horizontal 5-dot selector (filled dots = selected level, tinted with health accent on selection)
- Submit: primary gradient pill button "Save Entry"
- Cancel: ghost pill button "Cancel"

#### Data Source

- Mutation: `POST /api/health/biometrics`
- On success: invalidate `['health', 'biometrics']`, `['health', 'daily', today]`, `['health', 'weekly', monday]`
- On 409 (duplicate): show inline error "An entry already exists for this date"

#### Interaction

- Form is hidden by default (progressive disclosure — Constitution section 2)
- Opens via explicit user intent (LOG button > "Log Biometrics")
- Closes on backdrop click, Escape key, or Cancel button
- Submit button disables during mutation with "Saving..." label
- 44px minimum touch targets on all interactive elements

#### Biometric History (in page left panel)

History entries render as a scrollable list within the "Biometrics" tab. Each entry is a compact card row:

```
+-----------------------------------------------------+
| Mar 27          66.2 kg    18.5%    62 bpm          |
|                 Energy: ****o  Stress: **ooo        |
+-----------------------------------------------------+
```

- Date: Manrope Bold 600, `0.875rem`, `#2e342b`
- Metrics: Manrope Regular 400, `0.8125rem`, `#5a6157`
- Energy/stress: 5 small dots (8px), filled = `#4b6646`, empty = `#dee5d7`
- Row background: `#f3f7fb` (unselected), health gradient (selected)
- Selected border-left: `2.5px solid #8b4a3a`
- Row padding: `16px 24px`
- Row radius: `0 12px 12px 12px`
- Staggered entrance: 35ms delay per index

---

### 4.3 Workout Logging + History (Surface 3)

**File (form):** `frontend/app/(app)/health/_components/WorkoutLogForm.tsx`

#### Props Interface

```typescript
interface WorkoutLogFormProps {
  onClose: () => void
  onSuccess: () => void
}
```

#### Form Fields

| Field | Type | Label | Input | Constraints | Required |
|-------|------|-------|-------|-------------|----------|
| `date` | date | "Date" | native date input | defaults to today | Yes |
| `workout_type` | string | "Type" | text input with suggestions | 1-64 chars | Yes |
| `duration_minutes` | number | "Duration (min)" | number input, step 5 | >= 0 | Yes (default 0) |
| `intensity` | enum | "Intensity" | 3-pill selector: Low / Medium / High | required | Yes (default "medium") |
| `calories_est` | number | "Estimated calories" | number input | >= 0 | No |
| `notes` | text | "Notes" | textarea, 2 rows | max 4096 chars | No |

#### Layout

- Same modal pattern as BiometricLogForm
- Intensity selector: three pill buttons in a row, mutually exclusive. Selected pill uses health accent: `background: #fce8e4`, `border: 1.5px solid #8b4a3a`, `color: #8b4a3a`. Unselected: `background: #f1f5eb`, `color: #5a6157`.
- workout_type input: plain text, no autocomplete required (user types freely)
- Submit: "Log Workout" primary gradient pill
- Cancel: ghost pill

#### Data Source

- Mutation: `POST /api/health/workouts`
- On success: invalidate `['health', 'workouts']`, `['health', 'daily', today]`, `['health', 'weekly', monday]`

#### Workout History (in page left panel)

Each entry in the "Workouts" tab renders as:

```
+-----------------------------------------------------+
| Mar 27    Strength      45 min    High               |
|           ~350 cal                                   |
+-----------------------------------------------------+
```

- workout_type: Manrope Bold 600, `0.875rem`, capitalize first letter
- Duration + intensity: Manrope Regular 400, `0.8125rem`, `#5a6157`
- Intensity pill: small inline badge — High = `#fce8e4`/`#8b4a3a`, Medium = `#f5f0e4`/`#6b5a35`, Low = `#f1f5eb`/`#5a6157`
- Calories (if present): Manrope 400, `0.75rem`, `#767d72`, prefixed with `~`
- Same selection/styling pattern as biometric history rows

---

### 4.4 Nutrition Logging + History (Surface 4)

**File (form):** `frontend/app/(app)/health/_components/NutritionLogForm.tsx`

#### Props Interface

```typescript
interface NutritionLogFormProps {
  onClose: () => void
  onSuccess: () => void
}
```

#### Form Fields

| Field | Type | Label | Input | Constraints | Required |
|-------|------|-------|-------|-------------|----------|
| `date` | date | "Date" | native date input | defaults to today | Yes |
| `meal_type` | enum | "Meal" | 5-pill selector: Breakfast / Lunch / Dinner / Snack / Other | required | Yes |
| `items` | string | "What did you eat?" | textarea, 3 rows | 1-4096 chars, comma-separated | Yes |
| `quality_score` | 1-5 | "How did it feel?" | 5-dot selector | 1-5 | No |
| `calories_est` | number | "Estimated calories" | number input | >= 0 | No |

#### Layout

- Same modal pattern as other log forms
- Meal type selector: five pill buttons, wrapping on mobile. Selected uses health accent colors. Unselected uses sage palette.
- Quality score: 5 dots with labels "Poor" ... "Great" at ends only. Tapped dot fills with `#4b6646`, others fade.
- `items` textarea: `placeholder="e.g., grilled chicken, brown rice, broccoli"`
- Calories field is visually secondary (smaller, tucked below items) — quality_score is the primary metric per approved feature set
- Submit: "Log Meal" primary gradient pill
- Cancel: ghost pill

#### Data Source

- Mutation: `POST /api/health/nutrition`
- On success: invalidate `['health', 'nutrition']`, `['health', 'daily', today]`, `['health', 'weekly', monday]`

#### Nutrition History (in page left panel)

Each entry in the "Nutrition" tab renders as:

```
+-----------------------------------------------------+
| Mar 27    Lunch         Quality: ****o               |
|           chicken, rice, vegetables                  |
+-----------------------------------------------------+
```

- Meal type: Manrope Bold 600, capitalize, `#2e342b`
- Quality dots: 5 small dots (8px), filled up to score, fill color `#4b6646`, empty `#dee5d7`
- Items: Manrope Regular 400, `0.8125rem`, `#5a6157`, truncated to 2 lines with `...`
- Same selection/styling pattern as other history rows

---

### 4.5 Health Detail Panel (Surface 5)

**File:** `frontend/app/(app)/health/_components/HealthDetailPanel.tsx`

#### Props Interface

```typescript
interface HealthDetailPanelProps {
  selectedItem: { type: 'biometric' | 'workout' | 'nutrition'; id: number } | null
  biometrics: BiometricEntry[]   // from parent query cache
  workouts: WorkoutEntry[]       // from parent query cache
  nutritionLogs: NutritionEntry[] // from parent query cache
  weeklySummary: WeeklySummary | null
}
```

#### Layout

**Desktop:** Sticky right panel (40% width, `position: sticky`, `top: 24px`)
**Mobile:** Content rendered inside the draggable bottom drawer

```
+----------------------------------+
| SELECTED ENTRY (micro-label)     |
|                                  |
| [Entity-specific header]         |
| [Stats grid — 2x2]              |
| [Trend visualization]            |
+----------------------------------+
```

#### Content by Selected Type

**When nothing selected:**
- Centered empty state: Heart icon in clay-rose circle, "Select an entry to see details" in Newsreader 400, `1.125rem`

**When biometric selected:**
- Header: date (Newsreader 400, `1.125rem`), notes if present (Manrope 400, `0.8125rem`)
- Stats grid (2x2): Weight, Body Fat %, Resting HR, Energy/Stress
- Below stats: `WeightSparkline` component showing 30-day weight trend from biometrics list

**When workout selected:**
- Header: workout_type + date
- Stats grid (2x2): Duration, Intensity, Estimated Calories, "This Week" (count from weekly summary)
- Below stats: `WeeklyWorkoutDots` showing 7-day workout pattern

**When nutrition selected:**
- Header: meal_type + date
- Stats grid (2x2): Quality Score, Items count, "Today's Meals" (count from daily summary), "This Week" (count from weekly summary)
- Below stats: `NutritionQualityDots` showing 7-day quality pattern

#### Stats Grid Styling

Each stat card:
```typescript
{
  background: '#fdf0ed',  // health accent tint (lighter than #fce8e4)
  borderRadius: '0 10px 10px 10px',
  padding: '14px',
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
}
```

- Stat label: micro-label pattern, `#8b4a3a`
- Stat value: Newsreader 400, `1.25rem`, `#2e342b`

#### Panel Container Styling

```typescript
{
  background: 'linear-gradient(160deg, #fdf0ed 0%, #ffffff 100%)',
  borderRadius: '0 16px 16px 16px',
  boxShadow: '0 10px 26px rgba(46, 52, 43, 0.07)',
  padding: '24px',
  display: 'flex',
  flexDirection: 'column',
  gap: '24px',
}
```

---

### 4.6 Health Empty State (Surface 6)

**File:** `frontend/app/(app)/health/_components/HealthEmptyState.tsx`

#### Props Interface

```typescript
interface HealthEmptyStateProps {
  onLogBiometric: () => void
  onLogWorkout: () => void
  onLogMeal: () => void
}
```

#### Layout

Centered card displayed when ALL three lists (biometrics, workouts, nutrition) return zero items.

```
+--------------------------------------------------+
|                                                  |
|            [Heart icon in clay-rose circle]       |
|                                                  |
|        "Begin Your Health Journal"               |
|   (Newsreader 400, 1.25rem, #4b6646)            |
|                                                  |
|   A calm place to observe how your body          |
|   feels over time. Start with whatever           |
|   feels natural.                                 |
|   (Manrope 400, 0.875rem, #767d72)              |
|                                                  |
|   [Log Weight]  [Log Workout]  [Log Meal]        |
|   (three secondary pill buttons)                 |
|                                                  |
+--------------------------------------------------+
```

#### Design Tokens

- Card: `surface-container-lowest` (#ffffff), specimen radius, `padding: 3rem`, centered text
- Icon circle: 64px, `background: #fce8e4`, Heart icon 28px in `#8b4a3a`
- Title: Newsreader 400, `1.25rem`, `-0.03em`, `#4b6646`
- Body: Manrope 400, `0.875rem`, `#767d72`, `max-width: 360px`, `line-height: 1.65`
- CTA buttons: three secondary pill buttons (`background: #f1f5eb`, `color: #2e342b`, `border-radius: 100px`, `padding: 8px 20px`)
- Shadow: `0 8px 24px rgba(46, 52, 43, 0.06)`

#### Interaction

- Each button opens its respective log form
- Buttons have 44px min touch target
- Hover: `translateY(-1px)`, shadow deepens

---

### 4.7 Health Insight Cards (Surface 7) — SKIPPED

**Status: REQUIRES BACKEND WORK**

This surface depends on a health-filtered insight records endpoint (`GET /api/insights?domain=health` or similar) that does not exist in the current backend. No frontend component should be built for this surface until the backend endpoint is available.

**When backend is ready, this surface should:**
- Render read-only insight cards consuming `insight_record` data
- Use pull-quote pattern (Newsreader Italic, `#4b6646`, 3px left border in `#ccebc2`)
- Show caution labels (later-wave domain requirement)
- Never infer diagnosis or make predictive claims

---

## 5. Boundaries

### 5.1 Forbidden

These constraints are absolute. Sonnet must not deviate regardless of interpretation.

| # | Constraint | Rationale |
|---|-----------|-----------|
| F1 | Medical diagnosis language, clinical framing | Later-wave domain (Constitution section 12.1) |
| F2 | Calorie counting shame, deficit/surplus anxiety language | Emotional contract violation |
| F3 | Gamification of weight or body metrics (streaks, badges, scores for weigh-ins) | Explicitly cut feature |
| F4 | Predictive health claims ("you will...", "at this rate you'll...") | Explicitly cut; violates Constitution section 15.2 |
| F5 | Dense table defaults, always-on forms | Constitution section 2: progressive disclosure |
| F6 | Additional API endpoints beyond what exists in section 2.1 | Backend boundary — no frontend invention |
| F7 | New database migrations or model changes | Backend boundary |
| F8 | Features listed in EXPLICITLY_CUT (section 0 of prompt) | Scope boundary |
| F9 | "You should..." / "You failed to..." / "You must..." tone | Constitution section 9 |
| F10 | Cross-domain correlation or insight surfacing | Explicitly cut |
| F11 | Sleep, supplement, or recovery features | Not in schema, explicitly cut |
| F12 | Pure black (#000000) text or backgrounds | DESIGN.md rule — use `#2e342b` for dark text |
| F13 | Pure grey shadows (`rgba(0,0,0,...)`) | DESIGN.md rule — tint with `rgba(46,52,43,...)` |
| F14 | 1px borders for sectioning | DESIGN.md no-line rule — bg color shifts only |
| F15 | Square or slightly-rounded buttons | DESIGN.md — all buttons `rounded-full` pill shape |
| F16 | Newsreader for body text | DESIGN.md — Newsreader for headlines only, Manrope for reading |
| F17 | `clip-path` for clipped corners | DESIGN.md — use `border-top-left-radius: 0` |
| F18 | `backdrop-filter: blur()` > 8px | DESIGN.md — crisp glass only |
| F19 | Domain accent as default fill | Accent appears only on selection/active state |
| F20 | Before/after framing | Implies current state is broken |

### 5.2 Required

These constraints are mandatory. Every component must satisfy all applicable requirements.

| # | Constraint | Implementation |
|---|-----------|----------------|
| R1 | Read-first hierarchy (observe then decide then act) | Page loads in read mode showing summaries. Forms hidden. |
| R2 | Progressive disclosure (forms hidden until explicit intent) | LOG button opens form. History shows before edit tools. |
| R3 | Calm tone (Constitution section 9) | All UI copy uses "It looks like...", "Based on recent activity..." |
| R4 | Domain accent only on selection | Cards are white (#ffffff) by default; health gradient only when selected |
| R5 | Accessibility: 44px min touch targets | All buttons, selectors, tappable areas >= 44px height |
| R6 | Accessibility: ARIA labels | All interactive elements have `aria-label`. Forms have `<label>` elements. |
| R7 | Accessibility: semantic HTML | Use `<section>`, `<article>`, `<nav>`, `<h2>`/`<h3>`, `<button>` properly |
| R8 | Direction-aware baseline | Weight trend shows direction (up/down/stable) without judgment |
| R9 | Nutrition sufficiency as primary signal | quality_score dots shown before calories; calories are secondary/muted |
| R10 | Workout consistency as primary signal | Session count is the headline metric, not calories burned |
| R11 | Editorial Newsreader headlines + Manrope body | Page title, section headers = Newsreader. Labels, body = Manrope. |
| R12 | Specimen card pattern | `border-radius: 0 16px 16px 16px` on all cards |
| R13 | No 1px borders | Use bg color shifts (`#f1f5eb` sections on `#f8faf2` page) |
| R14 | Sage-tinted shadows only | `rgba(46, 52, 43, 0.06)` for cards, never `rgba(0,0,0,...)` |
| R15 | Pill-shaped buttons only | `border-radius: 100px` or Tailwind `rounded-full` |
| R16 | 2rem minimum card padding | `padding: 32px` on all card components |
| R17 | `prefers-reduced-motion` support | Check media query; disable animations when user prefers reduced motion |
| R18 | CJK micro-label handling | If label text contains CJK characters: `fontSize: 0.75rem`, no uppercase, `letterSpacing: 0.02em` |
| R19 | Translations via `getAppTranslations(lang).health` | All user-facing text from translation keys, not hardcoded English |

---

## 6. Dependency Map (Build Order DAG)

```
                    ┌─────────────────┐
                    │  1. health.ts   │ (API client — no dependencies)
                    │  lib/api/       │
                    └────────┬────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
      ┌────────▼──────┐  ┌──▼────────┐  ┌─▼──────────────┐
      │ 2. Translations│  │ 3. Empty  │  │ 4. Overview    │
      │ (update app.ts)│  │   State   │  │   Cards (3)    │
      └────────┬──────┘  └──┬────────┘  └─┬──────────────┘
               │            │             │
               │     ┌──────┼─────────────┤
               │     │      │             │
          ┌────▼─────▼──────▼─┐    ┌──────▼──────────┐
          │ 5. Viz Components │    │ 6. Log Forms (3) │
          │  - WeightSparkline│    │  - Biometric     │
          │  - WorkoutDots    │    │  - Workout       │
          │  - NutritionDots  │    │  - Nutrition     │
          └────────┬──────────┘    └──────┬───────────┘
                   │                      │
              ┌────▼──────────────────────▼───┐
              │ 7. HealthDetailPanel          │
              │    (consumes viz + list data) │
              └────────────┬─────────────────┘
                           │
                    ┌──────▼──────────┐
                    │ 8. HealthPage   │
                    │    (orchestrator│
                    │     + layout)   │
                    └─────────────────┘
```

**Build order (sequential with parallelizable steps):**

1. `frontend/lib/api/health.ts` — API client types and methods
2. `frontend/lib/translations/app.ts` — Extend `HealthPageTranslations` interface and add translation keys
3. `frontend/app/(app)/health/_components/HealthEmptyState.tsx` — (parallel with 4-6)
4. `frontend/app/(app)/health/_components/BiometricTrendCard.tsx` — (parallel with 3, 5, 6)
5. `frontend/app/(app)/health/_components/WorkoutSummaryCard.tsx` — (parallel with 3, 4, 6)
6. `frontend/app/(app)/health/_components/NutritionSummaryCard.tsx` — (parallel with 3, 4, 5)
7. `frontend/app/(app)/health/_components/WeightSparkline.tsx` — (parallel with 8, 9)
8. `frontend/app/(app)/health/_components/WeeklyWorkoutDots.tsx` — (parallel with 7, 9)
9. `frontend/app/(app)/health/_components/NutritionQualityDots.tsx` — (parallel with 7, 8)
10. `frontend/app/(app)/health/_components/BiometricLogForm.tsx` — (parallel with 11, 12)
11. `frontend/app/(app)/health/_components/WorkoutLogForm.tsx` — (parallel with 10, 12)
12. `frontend/app/(app)/health/_components/NutritionLogForm.tsx` — (parallel with 10, 11)
13. `frontend/app/(app)/health/_components/HealthOverviewCards.tsx` — depends on 4, 5, 6
14. `frontend/app/(app)/health/_components/HealthDetailPanel.tsx` — depends on 7, 8, 9
15. `frontend/app/(app)/health/page.tsx` — depends on ALL above

---

## 7. Sonnet Execution Instructions

### Pre-flight Checks

Before starting, Sonnet must verify:
1. `frontend/lib/api/client.ts` exists and exports `apiFetch`, `apiGet`, `apiPost`
2. `frontend/lib/translations/app.ts` exists and exports `HealthPageTranslations` interface
3. `frontend/lib/useLang.ts` exists and exports `useLang` hook
4. `frontend/app/(app)/health/page.tsx` exists (current placeholder — will be replaced)
5. `frontend/app/(app)/health/_components/` directory does NOT exist yet (create it)
6. React Query (`@tanstack/react-query`) is available via `frontend/app/providers.tsx`
7. `lucide-react` is available for icons

### File-by-File Checklist

---

#### Step 1: Create `frontend/lib/api/health.ts`

**Action:** Create new file
**Max lines:** 120
**Implements:** TypeScript types for all health API responses + `healthApi` object with methods

**Types to define:**
```typescript
export interface BiometricEntry {
  id: number
  date: string           // ISO date
  weight: number | null
  body_fat_pct: number | null
  resting_hr: number | null
  energy_level: number | null    // 1-5
  stress_level: number | null    // 1-5
  notes: string | null
  created_at: string | null      // ISO datetime
}

export interface WorkoutEntry {
  id: number
  date: string
  workout_type: string
  duration_minutes: number
  intensity: 'low' | 'medium' | 'high'
  calories_est: number | null
  notes: string | null
  created_at: string | null
}

export interface NutritionEntry {
  id: number
  date: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'other'
  items: string[]
  calories_est: number | null
  quality_score: number | null   // 1-5
  created_at: string | null
}

export interface DailySummary {
  date: string
  biometric: BiometricEntry | null
  workouts: { count: number; total_duration_minutes: number; by_type: Record<string, number> }
  nutrition: { count: number; calories_est_total: number }
  energy_level: number | null
  stress_level: number | null
}

export interface WeeklySummary {
  week_start: string
  week_end: string
  biometric: {
    average_weight: number | null
    average_resting_hr: number | null
    average_energy_level: number | null
    average_stress_level: number | null
  }
  workouts: { count: number; total_duration_minutes: number; by_type: Record<string, number> }
  nutrition: { count: number; calories_est_total: number }
}

// Input types for mutations
export interface BiometricCreateInput {
  date?: string
  weight?: number
  body_fat_pct?: number
  resting_hr?: number
  energy_level?: number
  stress_level?: number
  notes?: string
}

export interface WorkoutCreateInput {
  date?: string
  workout_type: string
  duration_minutes?: number
  intensity?: 'low' | 'medium' | 'high'
  calories_est?: number
  notes?: string
}

export interface NutritionCreateInput {
  date?: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'other'
  items: string         // comma-separated text
  calories_est?: number
  quality_score?: number
}
```

**API methods (mirror habits pattern):**
```typescript
export const healthApi = {
  listBiometrics: (params?) => apiGet<ListResponse<BiometricEntry>>(`/api/health/biometrics?${qs}`),
  createBiometric: (data) => apiPost<{ ok: boolean; biometric: BiometricEntry }>('/api/health/biometrics', data),
  listWorkouts: (params?) => apiGet<ListResponse<WorkoutEntry>>(`/api/health/workouts?${qs}`),
  createWorkout: (data) => apiPost<{ ok: boolean; workout: WorkoutEntry }>('/api/health/workouts', data),
  listNutrition: (params?) => apiGet<ListResponse<NutritionEntry>>(`/api/health/nutrition?${qs}`),
  createNutrition: (data) => apiPost<{ ok: boolean; nutrition: NutritionEntry }>('/api/health/nutrition', data),
  dailySummary: (date?) => apiGet<{ ok: boolean; summary: DailySummary }>(`/api/health/summary/daily?date=${date}`),
  weeklySummary: (start?) => apiGet<{ ok: boolean; summary: WeeklySummary }>(`/api/health/summary/weekly?start=${start}`),
}
```

Use a helper `ListResponse<T>` type: `{ ok: boolean; items: T[]; page: number; pages: number; total: number }`.

Build query string from optional params object for list methods (page, per_page, start_date, end_date). Omit undefined values.

**Verification:** Import `healthApi` from another file — must compile without errors. Check that all method signatures match section 2 endpoint contracts exactly.

---

#### Step 2: Update `frontend/lib/translations/app.ts`

**Action:** Edit existing file
**Implements:** Expanded `HealthPageTranslations` interface + English/Korean/Chinese translation objects

**Expand the interface:**
```typescript
export interface HealthPageTranslations {
  eyebrow: string
  title: string
  subtitle: string
  comingSoonTitle: string
  comingSoonBody: string
  // New keys:
  logBiometric: string
  logWorkout: string
  logMeal: string
  log: string
  saving: string
  save: string
  cancel: string
  date: string
  weight: string
  bodyFat: string
  restingHr: string
  energy: string
  stress: string
  notes: string
  workoutType: string
  duration: string
  intensity: string
  low: string
  medium: string
  high: string
  estimatedCalories: string
  mealType: string
  breakfast: string
  lunch: string
  dinner: string
  snack: string
  other: string
  items: string
  itemsPlaceholder: string
  qualityScore: string
  biometrics: string
  workouts: string
  nutrition: string
  emptyTitle: string
  emptyBody: string
  selectEntry: string
  selectedEntry: string
  thisWeek: string
  todaysMeals: string
  weightTrend: string
  sessions: string
  totalDuration: string
  duplicateError: string
  noData: string
}
```

**English values (add to existing `en.health` object):**
```typescript
health: {
  // ... keep existing eyebrow, title, subtitle, comingSoonTitle, comingSoonBody ...
  logBiometric: 'Log Biometrics',
  logWorkout: 'Log Workout',
  logMeal: 'Log Meal',
  log: 'Log',
  saving: 'Saving...',
  save: 'Save Entry',
  cancel: 'Cancel',
  date: 'Date',
  weight: 'Weight (kg)',
  bodyFat: 'Body fat (%)',
  restingHr: 'Resting heart rate',
  energy: 'Energy',
  stress: 'Stress',
  notes: 'Notes',
  workoutType: 'Type',
  duration: 'Duration (min)',
  intensity: 'Intensity',
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  estimatedCalories: 'Estimated calories',
  mealType: 'Meal',
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  dinner: 'Dinner',
  snack: 'Snack',
  other: 'Other',
  items: 'What did you eat?',
  itemsPlaceholder: 'e.g., grilled chicken, brown rice, broccoli',
  qualityScore: 'How did it feel?',
  biometrics: 'Biometrics',
  workouts: 'Workouts',
  nutrition: 'Nutrition',
  emptyTitle: 'Begin Your Health Journal',
  emptyBody: 'A calm place to observe how your body feels over time. Start with whatever feels natural.',
  selectEntry: 'Select an entry to see details',
  selectedEntry: 'Selected Entry',
  thisWeek: 'This Week',
  todaysMeals: "Today's Meals",
  weightTrend: 'Weight Trend',
  sessions: 'sessions',
  totalDuration: 'Total Duration',
  duplicateError: 'An entry already exists for this date.',
  noData: 'No data yet',
},
```

Provide equivalent Korean and Chinese translations for all new keys.

**Verification:** `getAppTranslations('en').health.logBiometric` returns `'Log Biometrics'`. TypeScript compiles without errors on the expanded interface.

---

#### Steps 3-6: Create Leaf Components (Parallel)

These four components have no inter-dependencies and can be built simultaneously.

**Step 3: Create `frontend/app/(app)/health/_components/HealthEmptyState.tsx`**
- Max lines: 60
- Import: Heart icon from `lucide-react`, translations
- Render: centered card with icon circle, title, body text, three CTA buttons
- Props: `{ onLogBiometric, onLogWorkout, onLogMeal }`
- See section 4.6 for exact styling
- Verification: renders correctly with no props-related TypeScript errors; buttons call handlers on click

**Step 4: Create `frontend/app/(app)/health/_components/BiometricTrendCard.tsx`**
- Max lines: 120
- Props: `{ latestWeight: number | null; weightDelta: number | null; trendDirection: 'up' | 'down' | 'stable'; energyLevel: number | null; stressLevel: number | null }`
- Renders: specimen card with weight headline, delta badge (green up arrow for bulk-positive, neutral otherwise), energy/stress dot indicators
- Weight: Newsreader 400, `1.5rem`, `#2e342b`. Delta: Manrope 600, `0.8125rem`, neutral color
- Section label: `BIOMETRICS` micro-label in `#8b4a3a`
- If latestWeight is null: show "No weight recorded" in muted text
- Verification: renders with all-null props without crashing; renders with sample data showing correct values

**Step 5: Create `frontend/app/(app)/health/_components/WorkoutSummaryCard.tsx`**
- Max lines: 100
- Props: `{ sessionsThisWeek: number; totalDurationMinutes: number; workoutTypes: Record<string, number> }`
- Renders: specimen card with session count headline ("3 sessions"), duration subtitle, type distribution as small pill badges
- Section label: `TRAINING` micro-label in `#8b4a3a`
- Session count: Newsreader 400, `1.5rem`, `#2e342b`
- Type pills: `background: #f1f5eb`, `color: #5a6157`, `rounded-full`, `padding: 2px 10px`, `fontSize: 0.6875rem`
- Verification: renders with `sessionsThisWeek=0` showing "0 sessions" correctly

**Step 6: Create `frontend/app/(app)/health/_components/NutritionSummaryCard.tsx`**
- Max lines: 100
- Props: `{ mealsToday: number; averageQuality: number | null; weeklyMealDays: boolean[] }` (weeklyMealDays is 7-element array, Mon-Sun, true = meals logged that day)
- Renders: specimen card with meals-today count, quality score indicator, 7-day dot row
- Section label: `NUTRITION` micro-label in `#8b4a3a`
- Dot row: 8px diameter, filled = `#4b6646`, empty = `#dee5d7`, 6px gap between dots
- Quality: shown as "Quality: X.X / 5" in Manrope 400, `0.875rem`
- Verification: renders with empty data (0 meals, null quality, all-false dots) without crashing

---

#### Steps 7-9: Create Visualization Components (Parallel)

**Step 7: Create `frontend/app/(app)/health/_components/WeightSparkline.tsx`**
- Max lines: 80
- Props: `{ entries: Array<{ date: string; weight: number }> }`
- Renders: compact SVG sparkline (200px wide x 48px tall)
- Line: stroke `#8b4a3a`, strokeWidth 1.5, fill none
- Area: fill `#fce8e4` at 30% opacity below the line
- Dots: 3px circles at first and last points only
- Empty state: dashed horizontal line with "No data" label
- Verification: renders with 0, 1, 2, and 30 data points without visual errors

**Step 8: Create `frontend/app/(app)/health/_components/WeeklyWorkoutDots.tsx`**
- Max lines: 50
- Props: `{ days: Array<{ date: string; hasWorkout: boolean }> }` (7 elements, Mon-Sun)
- Renders: horizontal row of 7 dots with day abbreviations below
- Dot: 10px, filled = `#4b6646`, empty = `#dee5d7`
- Today's unfilled dot: pulsing border animation (`dot-pulse` keyframe, 2s infinite)
- Day labels: Manrope 500, `0.5rem`, `#767d72`
- Verification: renders with mixed true/false array; today's dot pulses if unfilled

**Step 9: Create `frontend/app/(app)/health/_components/NutritionQualityDots.tsx`**
- Max lines: 50
- Props: `{ days: Array<{ date: string; avgQuality: number | null }> }` (7 elements)
- Renders: horizontal row of 7 dots with quality-proportional fill
- Dot: 10px, fill opacity proportional to quality (1=20%, 5=100%), color `#4b6646`
- Null quality: empty dot (`#dee5d7`)
- Day labels: same as WorkoutDots
- Verification: renders with all-null array; renders with mixed values

---

#### Steps 10-12: Create Log Form Components (Parallel)

**Step 10: Create `frontend/app/(app)/health/_components/BiometricLogForm.tsx`**
- Max lines: 130
- See section 4.2 for complete spec
- Uses `useMutation` from React Query with `healthApi.createBiometric`
- On success: call `onSuccess()` which triggers query invalidation in parent
- Handle 409 duplicate error: show inline error message from translations
- Form validation: client-side via controlled state, server-side via API response
- Verification: form opens, fills, submits successfully; duplicate date shows error; empty submit (no fields) still sends valid request (all fields optional except date)

**Step 11: Create `frontend/app/(app)/health/_components/WorkoutLogForm.tsx`**
- Max lines: 110
- See section 4.3 for complete spec
- Intensity pill selector must be keyboard-accessible (arrow keys cycle, Enter selects)
- workout_type input must have at least `aria-label`
- Verification: form submits with minimum fields (workout_type only); intensity defaults to "medium"

**Step 12: Create `frontend/app/(app)/health/_components/NutritionLogForm.tsx`**
- Max lines: 110
- See section 4.4 for complete spec
- meal_type 5-pill selector must wrap on narrow screens
- quality_score dots must show the correct number filled on click
- `items` textarea is required — show validation message if empty on submit
- Verification: form submits with minimum fields (meal_type + items); quality_score is optional

---

#### Step 13: Create `frontend/app/(app)/health/_components/HealthOverviewCards.tsx`

**Action:** Create new file
**Max lines:** 150
**Depends on:** Steps 4, 5, 6

**Props Interface:**
```typescript
interface HealthOverviewCardsProps {
  dailySummary: DailySummary | null
  weeklySummary: WeeklySummary | null
  recentBiometrics: BiometricEntry[]
  isLoading: boolean
}
```

**Implements:** Container component that computes derived props and renders the three summary cards (BiometricTrendCard, WorkoutSummaryCard, NutritionSummaryCard) in a responsive grid.

**Layout:**
- Desktop: 3-column grid, equal widths, 16px gap
- Mobile: single column, 16px gap

**Derived computations (all client-side):**
- `latestWeight`: first non-null weight from `recentBiometrics`
- `weightDelta`: difference between first and last non-null weights in `recentBiometrics`
- `trendDirection`: if delta > 0.5 → 'up', < -0.5 → 'down', else 'stable'
- `sessionsThisWeek`: `weeklySummary.workouts.count`
- `mealsToday`: `dailySummary.nutrition.count`
- `weeklyMealDays`: derive from nutrition list data passed through (requires fetching 7-day nutrition — compute in parent)
- `averageQuality`: compute from this week's nutrition entries

**Section header:** "Your Week So Far" — Newsreader 400, `1.125rem`, `-0.03em`, `#4b6646`. Micro-label above: `OVERVIEW` in `#8b4a3a`.

**Verification:** Renders three cards with loading skeleton when `isLoading=true`. Renders with null summaries showing "No data yet" in each card. Renders with full data showing correct computed values.

---

#### Step 14: Create `frontend/app/(app)/health/_components/HealthDetailPanel.tsx`

**Action:** Create new file
**Max lines:** 180
**Depends on:** Steps 7, 8, 9

See section 4.5 for complete spec.

**Verification:** Renders empty state when `selectedItem` is null. Renders biometric detail with sparkline when biometric selected. Renders workout detail with weekly dots when workout selected. Renders nutrition detail with quality dots when nutrition selected. All stats show correct labels and values.

---

#### Step 15: Replace `frontend/app/(app)/health/page.tsx`

**Action:** Replace existing placeholder file
**Max lines:** 800
**Depends on:** ALL steps above (1-14)

**Implements:** Full health page with:
- Page header (eyebrow + title + subtitle + LOG dropdown)
- Master-detail layout (60/40 desktop, stacked mobile)
- HealthOverviewCards section
- Tabbed history section (Biometrics | Workouts | Nutrition)
- History entry list with selection
- HealthDetailPanel (desktop: sticky right, mobile: drawer)
- HealthEmptyState (when all lists empty)
- Three log form modals (triggered by LOG dropdown)
- Mobile drawer with drag physics
- Responsive breakpoint detection (1024px)
- Reduce motion detection
- React Query setup for all data fetching

**Query setup:**
```typescript
const today = new Date().toISOString().split('T')[0]
const monday = getMonday(new Date()).toISOString().split('T')[0]

const { data: dailyData } = useQuery({
  queryKey: ['health', 'daily', today],
  queryFn: () => healthApi.dailySummary(today),
})

const { data: weeklyData } = useQuery({
  queryKey: ['health', 'weekly', monday],
  queryFn: () => healthApi.weeklySummary(monday),
})

const { data: biometricsData, isLoading: bioLoading } = useQuery({
  queryKey: ['health', 'biometrics'],
  queryFn: () => healthApi.listBiometrics({ per_page: 30 }),
})

const { data: workoutsData, isLoading: workLoading } = useQuery({
  queryKey: ['health', 'workouts'],
  queryFn: () => healthApi.listWorkouts({ per_page: 30 }),
})

const { data: nutritionData, isLoading: nutLoading } = useQuery({
  queryKey: ['health', 'nutrition'],
  queryFn: () => healthApi.listNutrition({ per_page: 30 }),
})
```

**Mutation invalidation pattern (on any successful create):**
```typescript
queryClient.invalidateQueries({ queryKey: ['health'] })
```

**Helper function needed:**
```typescript
function getMonday(d: Date): Date {
  const date = new Date(d)
  const day = date.getDay()
  const diff = date.getDate() - day + (day === 0 ? -6 : 1)
  date.setDate(diff)
  return date
}
```

**Tab implementation:**
- Three tabs: "Biometrics", "Workouts", "Nutrition"
- Tabs render as pill buttons in a row: selected = `background: #fce8e4`, `color: #8b4a3a`; unselected = `background: transparent`, `color: #5a6157`
- Tab content shows the corresponding history list
- Each tab badge shows total count (from query `total` field)

**LOG dropdown:**
- Primary gradient pill button labeled with translations `log` key
- On click: shows three options (Log Biometrics, Log Workout, Log Meal)
- Implementation: simple state toggle with absolute-positioned dropdown card
- Dropdown: `surface-container-lowest`, specimen radius, `box-shadow: 0 8px 24px rgba(46,52,43,0.06)`, three clickable rows with 44px height each
- Each row sets `showLogForm` state to the corresponding form type

**Verification checklist (must pass all before considering this step complete):**
1. Page loads and shows loading skeletons while queries are in flight
2. Empty state renders when all three lists return 0 items
3. Overview cards show correct data from daily/weekly summaries
4. Tab switching shows correct history list
5. Clicking a history entry highlights it and populates the detail panel
6. LOG dropdown opens and each option opens the correct form modal
7. Submitting a form creates the record and updates all visible data
8. Mobile view (< 1024px): overview cards stack, detail opens in drawer
9. Drawer drags and dismisses correctly
10. All text comes from translation keys (no hardcoded English)
11. No TypeScript errors
12. No console warnings or errors
13. Meets all R1-R19 required constraints from section 5.2

---

### Post-Build Verification

After all 15 steps are complete, Sonnet must verify:

1. **Type safety:** `npx tsc --noEmit` passes with zero errors
2. **Visual audit:** Page matches the layout diagrams in section 4.1
3. **Responsive:** Test at 320px, 768px, and 1280px widths
4. **Accessibility:** All buttons have labels, form inputs have associated labels, touch targets >= 44px
5. **Design compliance:** No 1px borders, no pure black text, no grey shadows, all buttons are pills, all cards have clipped TL corner
6. **Tone compliance:** No prescriptive language ("you should"), no shaming language, no predictive claims
7. **Data flow:** Create biometric -> appears in list -> appears in overview card -> appears in detail panel
8. **Error handling:** Duplicate biometric date shows error message, not crash
9. **Empty states:** All three empty conditions (no biometrics, no workouts, no nutrition, and the combined "all empty") render correctly
10. **Motion:** Animations respect `prefers-reduced-motion` media query
