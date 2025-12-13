# Backend Design Spec — Phase 3a (Cross-Domain Intelligence)

Context
- LifeOS architecture v2.1 (2025-12-10): Calendar-First Phase 2 complete; CI/CD green; events/outbox in place; insights engine rule-based.
- Goal of Phase 3a: Deliver cross-domain intelligence by correlating calendar + journal + domain events to surface actionable insights; add read models/projections where needed; preserve event-first, domain-isolation rules.

Scope (deliverable set)
1) Event Completeness & Telemetry
- Ensure all domains emit cataloged events with payload versions; add missing events in domain `events.py` and tests in `test_architecture_constraints`.
- Add telemetry counters/metrics for insight generation (counts, latency, coverage, FP/FN where available).

2) Projections/Read Models (lightweight)
- Add read-side helpers or cached queries (no heavy infra yet) to support cross-signal queries:
  - Recent calendar events (by source, by domain interpretation).
  - Journal entries (by entry_date, mood).
  - Domain summaries: habits logs (last 30d), health biometrics/workouts, finance transactions (by category), projects task completion velocity.
- Keep in services; optional materialized view per DB if simple; document and gate via config if DB-specific.

3) Insights Rules (cross-domain)
- Extend `lifeos/core/insights/rules/` with cross-domain rules that consume events:
  - Sleep/energy vs habit completion streaks
  - Calendar workload vs project task completion
  - Spend vs mood (finance.transaction.created + journal.mood)
  - Workout frequency vs stress/energy trends
- Rules must be deterministic, stateless, feature-flagged; use service helpers for read models; persist via existing `insight_record`.

4) Confidence-Aware Pipelines
- For interpretations/inferred records: standardize handling of `confidence_score`, `inferred_status`; flag low-confidence (<0.6) for review; auto-route high-confidence with audit.
- Ensure inferred events are logged with model/payload versions.

5) APIs (read-only)
- Add endpoints for insights feed/read models if needed (JSON), keeping controllers thin. Reuse existing blueprints (e.g., `/api/insights`, domain pages consuming read models).

Non-goals
- No new broker; stay on outbox + in-memory bus.
- No heavy ML; only rules and existing inference.
- No schema-destructive changes.

File/Module Targets
- `lifeos/core/insights/rules/cross_rules.py`: add Phase 3a rules with feature flags.
- `lifeos/core/insights/services.py` (if needed): helper to fetch recent events/read models.
- `lifeos/domains/*/events.py`: ensure completeness and payload versions for emitted events.
- `lifeos/domains/*/services/` read-model helpers:
  - Habits: recent logs (last 30d), streak computations.
  - Health: recent biometrics/workouts/nutrition summaries.
  - Finance: recent transactions by category, spend totals.
  - Projects: task completion velocity (count per week).
  - Calendar: recent events, interpretations with confidence.
  - Journal: recent entries with mood/tags.
- `lifeos/domains/*/controllers/` (optional): read-only endpoints for insights feed (if not already in insights API).
- `lifeos/tests/test_architecture_constraints.py`: update allowlists/catalog checks.
- `lifeos/tests/` add rule-level tests for new cross rules and read-model helpers.

Implementation Notes
- No cross-domain imports: use services/read helpers or event data snapshots.
- Feature flags: gate new rules; default ON for safe rules, OFF for experimental.
- Performance: cap lookback windows (e.g., 30/90 days) and paginate read endpoints.
- Metrics: log counters for insights generated, rule hit rates, and error handling.

Expected Tests
- Unit tests for each new rule function (inputs → insights).
- Service tests for read-model helpers (correct aggregation, user scoping).
- Architecture constraint tests updated to include new events.
- Optional integration: insights API returns aggregated feed with new signals.
