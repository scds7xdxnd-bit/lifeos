# Phase 12 Skills v2 — Phase 0 Foundation Alignment

Status: In Progress
Owner: Architecture + Backend + Frontend + QA
Target Window: 2026-03-22 to 2026-03-29
Related Constitution: lifeos/docs/ui_ux_constitution.md §5 (Skills)
Related Architecture: lifeos/docs/lifeos_architecture.md

## Objective
Define and freeze the minimum contracts required to evolve Skills from session logging to goal-based training without disrupting existing usage.

## Scope (Phase 0 only)
- Freeze UX contract for one primary question/action on Skills cards.
- Freeze data semantics for goals, progress state, and risk state.
- Add rollout flags for safe staged release.
- Publish implementation checklist for Phase 1.

Out of Scope:
- New database migrations for goals/path.
- Major UI rewrites.
- Forecasting and recommendation engines.

## Deliverables
1. Feature flags present in config:
   - ENABLE_PHASE12_SKILLS_GOALS
   - ENABLE_PHASE12_SKILLS_PATH
   - ENABLE_PHASE12_SKILLS_FORECAST
2. Canonical semantics for skill progress states:
   - on_track
   - at_risk
   - completed
3. Goal endpoint taxonomy frozen:
   - hours
   - sessions
   - milestones
   - benchmark
   - deadline
4. Phase 1 execution readiness brief (API + UI + QA acceptance criteria).

## Contract Freeze (Normative)
- Every active skill must have a defined endpoint before it can be considered trainable.
- Every skill card must expose (at minimum): total hours, session count, and progress toward endpoint.
- Skills surface keeps one dominant action per card: Continue Practice.
- At-risk classification is deterministic and auditable (no hidden ML scoring in Phase 0/1).

## Readiness Checklist
- [x] Feature flags added to runtime config.
- [x] Goal endpoint taxonomy documented.
- [x] Status semantics documented.
- [x] Backend API shape for Skills v2 overview agreed (`GET /api/skills/overview`, flag-gated by `ENABLE_PHASE12_SKILLS_GOALS`).
- [x] Frontend card spec and modal flow approved (overview-first render with legacy fallback).
- [x] QA acceptance matrix drafted for Skills v2 Phase 1 (`lifeos/docs/tasks/phase_12_skills_v2_phase2_path_and_action_flow.md`).
- [x] Phase 3 forecast/guidance kickoff documented (`lifeos/docs/tasks/phase_12_skills_v2_phase3_forecast_guidance.md`).

## Phase 1 Handoff Criteria
Proceed to Phase 1 only when:
1. Backend and frontend agree on response contracts for overview/detail.
2. QA signs off on measurable acceptance criteria.
3. Flags are wired into implementation paths (default OFF).

## Notes
- Keep rollout additive and reversible.
- Do not include .claude or .github paths in PR scope for this phase.
