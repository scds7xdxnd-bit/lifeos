# Phase 12 Skills v2 — Phase 3 Forecast and Guidance

Status: In Progress
Owner: Backend + Frontend + QA
Target Window: 2026-03-23 to 2026-03-31
Related Constitution: lifeos/docs/ui_ux_constitution.md §5 (Skills)
Related Architecture: lifeos/docs/lifeos_architecture.md

## Objective
Add deterministic, flag-gated forecast guidance for Skills so users can see likely near-term trajectory without changing existing behavior when forecast is disabled.

## Scope (Phase 3)
- Add deterministic forecast endpoint per skill (`GET /api/skills/{skill_id}/forecast`).
- Keep forecast behind feature flag (`ENABLE_PHASE12_SKILLS_FORECAST`).
- Add read-only forecast panel on skill cards when forecast data is available.
- Add human-readable reason copy for forecast state to improve clarity.

Out of Scope:
- Non-deterministic recommendation engines.
- Causal explanations or ML-driven inference.
- New schema migrations beyond Phase 1/2 additive changes.

## Backend Deliverables
1. Forecast endpoint contract with typed payload:
   - baseline metrics (last 14 days)
   - projected window metrics
   - forecast state and risk reason
2. Feature-flag gate behavior:
   - forecast disabled -> 404 not_found
3. Deterministic horizon handling:
   - query parameter `horizon_days`
   - clamped range for safety
4. Integration tests for disabled/enabled/not-found/projection payload.

## Frontend Deliverables
1. Skills API contract includes forecast response types.
2. Skills page reads forecast data and shows a read-only forecast panel per card.
3. Forecast copy remains advisory and deterministic.
4. Existing create/practice/edit flows remain unchanged.

## QA Matrix (Phase 3)
1. Forecast flag OFF:
   - `/api/skills/{id}/forecast` returns 404.
   - UI shows no forecast panel and remains functional.
2. Forecast flag ON + valid skill:
   - endpoint returns baseline/projection/state payload.
   - UI renders forecast summary and reason text.
3. Forecast flag ON + missing skill:
   - endpoint returns 404 not_found.
4. Horizon safety:
   - out-of-range horizon is clamped by backend contract.

## Exit Criteria
- Backend forecast endpoint tests pass.
- Frontend build + tests pass with forecast panel enabled.
- Feature-flag fallback path validated (forecast OFF behavior unchanged).
