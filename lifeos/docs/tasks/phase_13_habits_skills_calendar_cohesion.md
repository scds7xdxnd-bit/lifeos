# Phase 13 Habits + Skills + Calendar Cohesion

Status: Proposed
Owner: Architecture + Backend + Frontend + QA
Target Window: TBD
Related Constitution: lifeos/docs/ui_ux_constitution.md
Related Architecture: lifeos/docs/lifeos_architecture.md

## Objective
Connect habits, skills, and calendar in a deterministic way so users receive realistic, actionable daily planning support with visible reasoning.

## User Value Hypothesis
Users gain higher consistency and faster skill progress when planning suggestions are constrained by real calendar availability and framed as low-friction next actions.

Expected user value:
- Higher follow-through because suggestions fit actual time blocks.
- Better streak resilience through fallback (micro-session) options.
- Better skill progression through intentional scheduling and recovery.
- Less decision fatigue via ranked, context-aware next actions.
- Better self-understanding through explicit cross-domain trend summaries.

## Scope (Proposed)
1. Shared context layer
- Treat calendar as time reality.
- Treat habits as consistency anchors.
- Treat skills as growth targets.

2. Deterministic recommendation layer
- Rule-based prioritization only.
- No opaque runtime ML decisioning.
- Explicit confidence and reason strings in outputs.

3. Action surface layer
- Daily plan card (one habit, one skill, one admin action).
- In-context suggestions from free time blocks.
- Weekly review with trend and one suggested adjustment.

Out of scope:
- Autonomous assistant behavior.
- Hidden auto-actions without user consent.
- Causal claims beyond observable evidence.
- Predictive scoring not traceable to deterministic features.

## Deterministic Rule Set (Initial)
1. Feasibility first
- Suggest only actions that fit free blocks and configured quiet hours.

2. Streak protection
- If habit streak risk is high, prioritize a minimum viable completion option.

3. Skill continuity
- If planned skill session is missed, propose one replacement slot within 48 hours.

4. Load shedding
- If calendar load crosses threshold, suppress non-critical suggestions.

5. User control
- Every suggestion includes reason text and can be accepted, snoozed, or dismissed.

## Product Surfaces
1. Calendar page integration
- Show optional suggestion chips per day cell and selected-day agenda.
- One-tap convert suggestion into calendar event block.

2. Habits page integration
- Show habit-to-time-fit signals (best slot, fallback slot).

3. Skills page integration
- Show next practice recommendation tied to concrete time windows.

4. Weekly summary surface
- Show cross-domain summary: planned vs completed and next-week adjustment.

## Data and Contracts (Proposed)
1. New read model (cross-domain)
- User-scoped daily planning projection with deterministic feature snapshots.

2. API contracts
- `GET /api/v1/planning/daily`
- `GET /api/v1/planning/weekly`
- `POST /api/v1/planning/actions/{id}/accept`
- `POST /api/v1/planning/actions/{id}/dismiss`

3. Event semantics (proposed)
- `planning.suggestion.generated`
- `planning.suggestion.accepted`
- `planning.suggestion.dismissed`

All events must include `payload_version` and deterministic provenance metadata.

## Rollout Plan
1. Phase 13a: Read-only insights
- Generate suggestions and reasons, no auto-scheduling.

2. Phase 13b: User-confirmed actions
- Allow one-tap accept to create/update calendar blocks.

3. Phase 13c: Guardrailed automation (optional)
- User opt-in for limited auto-reschedule with strict constraints.

## QA Acceptance Matrix (Proposed)
1. Determinism
- Same inputs produce identical suggestions and ordering.

2. Safety
- No suggestions outside user quiet hours.
- No overlapping blocks created by accept flow.

3. Explainability
- Every suggestion includes a readable reason string.

4. Fallback behavior
- If cross-domain projection unavailable, UI degrades gracefully with no broken actions.

## Exit Criteria
- Cross-domain planning APIs stable and versioned.
- Frontend daily and weekly planning surfaces shipped behind feature flags.
- QA matrix passes in staging.
- Operational runbook published before production rollout.
