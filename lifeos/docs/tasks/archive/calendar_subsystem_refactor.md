# Task: Calendar Subsystem Refactor (Deterministic Views, Ledger, Analysis Split)
Status: Completed · Owner: Architecture → All Teams · Archived after cross-team delivery (backend/frontend/DB/ML/QA/DevOps)

## Purpose
Fix calendar structural flaw: grid views currently depend on ad-hoc frontend filters. We must enforce backend-owned, deterministic time windows for Day/Week/Month, separate analysis/search, and treat the List view as an event ledger anchored to “today.” ML needs replayable, filter-free temporal context.

## Non-Negotiable Principles
- Calendar grids are time-bounded renderers (no filters affect visibility).
- Filtering belongs to analysis/search only.
- Backend owns window logic (overlap + spillover).
- List view is a chronological ledger with cursor/anchor at “today.”
- ML safety: deterministic windows, replayable streams, no hidden UI state.

## Deliverables by Team
- **Backend**: Ship view-semantic APIs (`/calendar/day|week|month`) with overlap logic and spillover; ledger API with cursor/anchor=today; deprecate filter-driven grid queries; keep search endpoint separate for filters.
- **Frontend**: Remove filters from grid visibility; consume view APIs per window; implement ledger as scrollable Y-overflow anchored to today via ledger API; use filters only in analysis/search surface; no client-side spillover/visibility inference.
- **DB**: Add/confirm indexes for time-window overlap and ledger ordering; additive-only (e.g., `(user_id, start_time, end_time)`, `(user_id, start_time, id)`); optional normalized date columns if needed for month/day overlap; no destructive changes.
- **ML/Intelligence**: Consume deterministic windows/ledger; maintain raw vs inferred separation; leverage stable windows for habit/time allocation; no UI-filtered subsets in training/eval.
- **DevOps**: Roll out new endpoints (optional feature flag); monitor correctness metrics (window overlap counts, ledger cursor errors, TZ warnings); maintain legacy endpoints during cutover.
- **QA**: Test matrix for day/week/month overlap (all-day, spanning, DST), spillover correctness, ledger anchoring/pagination; verify filters do not change grid membership; accept criteria per view.

## Interfaces & Notes
- Use `lifeos/docs/lifeos_architecture.md` (calendar sections) as the authoritative contract.
- No UI redesign; no token/cookie/device changes; no mobile/offline scope.
- When complete, move this file to `archive/` with outcomes and links to PRs.

## Detailed Cross-Team Technical Structure (authoritative)

Below is the cross-team technical structure to refactor the Calendar subsystem into deterministic, ML-safe, time-bounded views with a separate analytical surface. No UI mockups; all contracts and responsibilities are explicit.

### A. System-Level Architecture Overview
- Data flow (textual): Frontend requests view-semantic endpoints (day/week/month) → Backend applies deterministic time-window logic → DB returns events via indexed range scans → Backend returns canonical event sets → Frontend renders without filters. Ledger view uses cursor-based chronological API anchored at “today.” Analysis/search uses separate filtered endpoints (not used by calendar views). ML consumes the same canonical event streams and ledger, ensuring replayability.
- Separation of concerns:
  - Calendar navigation: Day/Week/Month views are purely time-bounded renderers. No filters affect visibility.
  - Event storage: `calendar_event` table remains source of truth; indexes optimized for range queries.
  - Event ledger: Chronological, scrollable list API with cursor/anchor at “today,” independent of grid navigation.
  - Analysis/filtering: Dedicated analytical/search endpoints; filters never drive grid visibility.
  - ML interpretation & replay: Interpreter and downstream ML consume deterministic event windows and ledger streams; no hidden UI state.

### B. Backend Team Deliverables
- New view-semantic APIs (pure time windows):
  - `GET /api/v1/calendar/day?date=YYYY-MM-DD`
  - `GET /api/v1/calendar/week?start=YYYY-MM-DD` (7-day window; includes spillover rules)
  - `GET /api/v1/calendar/month?year=YYYY&month=MM` (includes leading/trailing days for grid; backend owns spillover selection)
  - Visibility rule: return all events where `event.start < window_end` AND `event.end > window_start` (treat all-day and instant events appropriately).
- Event ledger API:
  - `GET /api/v1/calendar/ledger?anchor=today|YYYY-MM-DD&direction=forward|backward&limit=N&cursor=...`
  - Chronological ordering by start_time, tie-broken by id; defaults anchor to “today.”
- Spillover ownership: Backend computes leading/trailing days for month grids; frontend never infers.
- Compatibility:
  - Maintain existing endpoints but mark view endpoints as authoritative for grid rendering.
  - Deprecate filter-driven calendar queries; keep analytical/search endpoints separate (e.g., `/api/v1/calendar/search` with filters).
- Contracts & schemas:
  - Response includes: events, window_start, window_end, timezone_used, spillover_days (month only), anchor (ledger).
  - All times returned in user’s canonical timezone; backend enforces TZ normalization.
- Non-responsibilities: No device/browser heuristics; no client-side filtering hints; no inferred visibility flags from frontend state.

### C. Frontend Team Deliverables
- Remove filter influence: Calendar Day/Week/Month views must render exactly what backend returns; no source/tag/domain filters applied to grid visibility.
- Data fetching: Use view-specific endpoints above; request by visible window (date/week/month). No local filtering for visibility.
- List/Ledger view: Implement scrollable Y-overflow ledger backed by ledger API; default scroll anchored to “today” (or provided anchor). Use cursor pagination, not page numbers.
- Anchoring: On load, scroll to anchor event cluster (today); maintain cursor for up/down fetch.
- Non-responsibilities: Frontend must never decide visibility, spillover, or apply hidden filters to grids; must not alter ordering for ledger; must not infer time zones.

### D. Database Team Deliverables
- Model validation: `calendar_event` remains source of truth.
- Indexing:
  - Composite indexes to support window queries: `(user_id, start_time)`, `(user_id, end_time)`, and a covering index for range overlap: `(user_id, start_time, end_time)`.
  - For ledger: `(user_id, start_time, id)` to support stable cursor pagination.
- Schema considerations:
  - Ensure `all_day` semantics and normalized `start_time`/`end_time` with timezone handling are explicit.
  - Optional: persisted `normalized_start_date`/`normalized_end_date` (date only) to accelerate month/day overlap queries (additive columns only, nullable defaults).
- Replay/ML support:
  - Keep events immutable; no destructive updates. For edits, update rows but ensure event_history/audit via existing outbox/event_record as needed.
- Migrations:
  - Additive-only: indexes and optional normalized date columns. No table drops/renames. Coordinate with readmodel projections if materialized views are added later.

### E. ML / Intelligence Team Deliverables
- Ingestion: Consume canonical calendar event streams (from outbox/event bus) and ledger API (if needed) with deterministic windows; no UI-filtered subsets.
- Contracts:
  - Maintain separation of raw events vs inferred records (existing interpreter pattern). No mixing filtered views into training/eval data.
  - Confidence semantics unchanged (already frozen).
- Replay:
  - Use deterministic window queries for temporal context (e.g., week-of, day-of) to align habit/time-allocation models.
- Improvements from determinism:
  - Habit analysis: stable day/week windows without UI filters.
  - Time-allocation modeling: consistent totals per period.
  - Insight generation: reproducible context; no contamination from hidden front-end state.

### F. DevOps Team Deliverables
- Deployment:
  - Roll out new view endpoints behind feature flag if desired (`CALENDAR_VIEW_API_V2`).
  - Maintain legacy endpoints for transition; monitor usage.
- Observability:
  - Metrics: per-view latency, window size correctness checks (count events overlapping vs returned), ledger cursor error rates, timezone mismatch warnings.
  - Logs: audit for view requests (window parameters) and ledger anchors.
- Rollout/compatibility:
  - Staged rollout: ship backend endpoints first, then frontend switches consumption; remove filter-driven grid fetches after verification.
  - Ensure worker/outbox unaffected; no broker changes.

### G. QA Team Deliverables
- Test matrix:
  - Day view: all-day events, instant events, multi-day spanning events, timezone boundaries (DST transitions), events starting before day and ending after.
  - Week view: same as day, plus spillover across weeks.
  - Month view: spillover days correctness; events spanning months appear in all intersecting windows.
  - Ledger: anchor at today; cursor forward/backward; stability of ordering when new events are added (id tie-break).
- Regression risks:
  - TZ normalization errors; off-by-one in overlap logic; legacy filters still applied to grids; ledger anchor misplacement.
- Acceptance criteria:
  - Grids show all events intersecting the window, regardless of source/tag/domain.
  - Filters do not change grid membership; filters only affect analytical/search surfaces.
  - Ledger loads around today by default and paginates chronologically with consistent ordering.

### Design Overview (Problem → Intent → Solution)
- Problem: Calendar grids depend on ad-hoc frontend filters; list view conflates navigation and analysis; non-deterministic visibility harms UX, backend boundaries, and ML replay.
- Intent: Make calendar grids deterministic, time-bounded renderers owned by backend; move filtering to analysis; make ledger a chronological event stream anchored to “today”; ensure ML-safe replay.
- Solution: Introduce view-semantic APIs with backend-enforced overlap logic, separate ledger API, index DB for time windows, remove frontend filter influence on grids, keep analysis/search separate, and maintain replayable event streams.

### Handoff Summaries
- Backend: Build and expose day/week/month view endpoints with strict overlap logic; include spillover handling server-side. Build ledger endpoint with cursor/anchor semantics; default anchor = today. Deprecate filter-driven calendar data paths; keep a separate search/analysis endpoint for filters. No UI/state-based visibility; no token/cookie or device changes. Additive DB/index changes only.
- Frontend: Switch calendar grids to view APIs; remove filters from visibility logic. Implement ledger as scrollable, anchored to today via ledger API. Use filters only in a separate analysis/search surface; never for grid membership. Do not infer visibility, spillover, or timezones client-side.
- Database: Add/confirm indexes for window overlap and ledger ordering; consider nullable normalized date columns for speed (additive). No destructive schema changes; ensure TZ correctness in stored times.
- ML: Consume deterministic window/ledger data; keep raw vs inferred separation; leverage stable windows for habit/time-allocation models; no UI-state contamination.
- DevOps: Roll out new endpoints with optional feature flag; monitor metrics for correctness; keep legacy paths during transition; no broker changes.
- QA: Validate window overlap correctness, TZ edges, spillover, and ledger anchoring/pagination; ensure filters no longer affect grids; lock acceptance criteria per view.
