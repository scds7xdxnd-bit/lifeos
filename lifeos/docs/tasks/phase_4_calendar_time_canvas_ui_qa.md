# Phase 4 Calendar Time-Canvas UI - QA Structure

**Scope:** Visual + behavioral verification only (no API/semantic changes).
**Feature Flag:** `CALENDAR_TIME_CANVAS_UI` (default false).
**Objective:** Validate time-canvas rendering parity with Apple-style grammar while preserving Phase 3b/3c correctness.

---

## 1. Preconditions

- Phase 3b/3c metrics are green.
- Feature flag enabled in the target environment.
- Test data seeded for the cases listed in `lifeos/tests/fixtures/calendar_time_canvas_cases.json`.

---

## 1.1 Playwright Seeded Data Harness (Required for QA)

**Goal:** Provide deterministic, repeatable datasets for UI regression tests without new APIs or schema changes.

**Inputs**
- Fixture: `lifeos/tests/fixtures/calendar_time_canvas_cases.json`
- Seeder: `scripts/ops/seed_calendar_time_canvas_cases.py`
- Snapshot output path: `docs/tasks/phase_4_calendar_time_canvas_ui_snapshots/`

**Required env vars**
- `BASE_URL` (example: `http://127.0.0.1:8000`)
- `CALENDAR_EMAIL` (seeded user, default `calendar.qa@example.com`)
- `CALENDAR_PASSWORD` (seeded user password, default `calendar-seed-123`)
- `CALENDAR_TIME_CANVAS_UI=true`
- `SEED_CASE` (fixture case id or `all`)
- `RESET` (`1` to clear and reseed; optional)

**Execution flow (manual or Playwright global setup)**
1. Seed the target case(s) using the seeder script.
2. Launch the calendar UI with the feature flag enabled.
3. Navigate Day/Week/Month views per case and capture snapshots.
4. Save snapshots as `case_<id>.png` in the snapshot output path.

**Playwright capture command**
```
pip install playwright
playwright install chromium
PYTHONPATH=. scripts/ops/seed_calendar_time_canvas_cases.py --purge
CALENDAR_TIME_CANVAS_UI=true \
BASE_URL=http://127.0.0.1:8000 \
CALENDAR_EMAIL=calendar.qa@example.com \
CALENDAR_PASSWORD=calendar-seed-123 \
OUTPUT_DIR=lifeos/docs/tasks/phase_4_calendar_time_canvas_ui_snapshots \
python3 scripts/ops/capture_calendar_time_canvas_snapshots.py
```
The script also captures `case_<id>_quickview.png` for quick-view popovers.

**Non-goals**
- No test-only APIs.
- No schema changes.
- No UI changes to support tests.
- No contract or semantic validation.

**Acceptance criteria**
- Seeded datasets are reproducible across runs.
- Snapshots exist for all case IDs.
- Snapshot filenames match case IDs exactly.
- Playwright runs do not mutate server state.

---

## 1.2 Manual Snapshot Capture Flow (QA)

**Goal:** Capture the required baseline PNGs when Playwright is unavailable.

**Steps**
1. Enable `CALENDAR_TIME_CANVAS_UI=true`.
2. Seed fixtures: `scripts/ops/seed_calendar_time_canvas_cases.py --purge`.
3. Log in as the seeded user (`calendar.qa@example.com`).
4. Navigate to each case date and view (Day/Week/Month).
5. Capture `case_<id>.png` for all 8 IDs listed below.
6. Save files to `docs/tasks/phase_4_calendar_time_canvas_ui_snapshots/`.

**Acceptance criteria**
- All eight snapshots exist and match case IDs.
- Quick-view popover is captured for one event per view.

---

## 2. View x Event-Type Matrix (Required Coverage)

| View | Timed Single | Overlap (2) | Overlap (3+) | All-Day Single | All-Day Multi-Day | Month Multi-Day Bars | Overflow (+N) | Quick-View Popover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Day | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ✅ | ✅ |
| Week | ✅ | ✅ | ✅ | ✅ | ✅ | N/A | ✅ | ✅ |
| Month | N/A | N/A | N/A | ✅ | ✅ | ✅ | ✅ | ✅ |

**Notes**
- Month view uses multi-day bars; timed events are not shown in hourly lanes.
- Overflow must be validated in Day/Week all-day track and Month cell list.

---

## 3. Snapshot Set (Baseline Visual Regression)

Capture snapshots for the following case IDs (from the fixture file):

- `day_basic_overlap`
- `day_all_day_stack`
- `week_overlap_dense`
- `week_all_day_overflow`
- `month_multi_day_bars`
- `month_overflow`
- `dst_forward_day`
- `dst_fall_back_day`

**Capture guidance**
- Use the same viewport size for all captures (recommended: 1440x900).
- Include quick-view popover snapshots for one event in each view.
- Store captures under `docs/tasks/phase_4_calendar_time_canvas_ui_snapshots/` with filenames `case_<id>.png`.

---

## 4. Edge-Case Coverage Checklist

- DST forward day: event starting before the jump and ending after (no visual compression).
- DST fall-back day: two events around the repeated hour (no overlap inversion).
- Multi-day spanning month boundary (month view bar continuity).
- All-day stack order stability (deterministic order by start time).
- Overflow threshold correctness (+N more appears at correct count).
- Quick-view popover renders title, time range, and calendar accent; dismiss works.

---

## 5. Pass/Fail Criteria

**Pass if:**
- All matrix cells are exercised and match Apple-style interaction grammar.
- No UI contract error banners appear.
- No layout regressions (overlaps, all-day stacking, multi-day bars, overflow).
- All Phase 3 metrics remain unchanged/green during verification.

**Fail if:**
- Any event overlaps/stacking appear incorrect.
- Overflow displays incorrect count or loses events.
- Quick-view popover fails to render or dismiss.

---

## 6. Verification Notes Template

```
Date:
Environment:
Feature flag:
Cases executed:
Snapshot paths:
Findings:
Metrics status (projection/determinism/contract):
Sign-off:
```

---

## 7. Verification Record (Completed)

```
Date: 2025-12-25
Environment: local dev (macOS), LifeOS http://127.0.0.1:8000
Feature flag: CALENDAR_TIME_CANVAS_UI=true
Cases executed: day_basic_overlap, day_all_day_stack, week_overlap_dense, week_all_day_overflow, month_multi_day_bars, month_overflow, dst_forward_day, dst_fall_back_day
Snapshot paths: lifeos/docs/tasks/phase_4_calendar_time_canvas_ui_snapshots/case_<id>.png (+ week quickview captures)
Findings: No visual regressions reported; quick-view popover snapshots captured for week overlap/overflow cases
Metrics status (projection/determinism/contract): 0 / 0 / 0
Sign-off: QA Approved
```
