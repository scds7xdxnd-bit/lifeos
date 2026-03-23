# Phase 12 Skills v2 — Phase 2 Path and Action Flow

Status: Complete
Owner: Backend + Frontend + QA
Target Window: 2026-03-22 to 2026-03-30
Related Constitution: lifeos/docs/ui_ux_constitution.md §5 (Skills)
Related Architecture: lifeos/docs/lifeos_architecture.md

## Objective
Add deterministic path guidance on each skill while preserving one dominant card action and full fallback compatibility.

## Scope (Phase 2)
- Introduce deterministic path API endpoint per skill.
- Keep goals and path behind feature flags (`ENABLE_PHASE12_SKILLS_GOALS`, `ENABLE_PHASE12_SKILLS_PATH`).
- Wire frontend skills page to prefer overview contract and gracefully fallback to legacy list.
- Keep dominant card action as Continue Practice.
- Add minimal additive schema support required by this flow (goal fields on `skill`, optional `step_id` on `skill_practice_session`).

Out of Scope:
- Forecast/recommendation engine (`ENABLE_PHASE12_SKILLS_FORECAST`).
- New non-deterministic scoring logic.
- Large or unrelated database schema redesigns beyond the additive fields above.

## Backend Deliverables
1. `GET /api/skills/overview` (Phase 1 carry-forward, goals-flag gated).
2. `GET /api/skills/{skill_id}/path` (Phase 2, path-flag gated).
3. Deterministic status derivation:
   - `completed`: progress ratio >= 1.0
   - `at_risk`: no recent sessions in required window
   - `on_track`: otherwise
4. Deterministic path steps:
   - continue_practice
   - setup_goal or review_goal
   - optional recovery step when at risk

## Frontend Deliverables
1. Skills page prefers overview cards when available.
2. Falls back to legacy list payload when overview endpoint is disabled/not available.
3. Shows deterministic progress state badge and goal progress strip.
4. Maintains one dominant action button per card.

## QA Matrix (Phase 2)
1. Goals flag OFF + Path flag OFF:
   - overview returns 404
   - path returns 404
   - skills page still renders legacy list
2. Goals flag ON:
   - overview returns cards with required fields
   - card state values are only on_track/at_risk/completed
3. Path flag ON:
   - path returns deterministic ordered steps
   - missing skill returns 404
4. Compatibility:
   - create/log/delete skill updates both list and overview surface after mutation

## Exit Criteria
- Backend tests for overview + path flags pass.
- Frontend renders correctly with overview success and fallback modes.
- No breaking change to existing `/api/skills` consumers.

## Follow-up Phase
- Phase 3 forecast/guidance work is tracked in `lifeos/docs/tasks/phase_12_skills_v2_phase3_forecast_guidance.md`.
