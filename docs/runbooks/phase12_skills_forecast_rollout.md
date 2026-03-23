# Phase 12 Skills Forecast Rollout Runbook

## Purpose
Safely roll out the Skills forecast surface behind `ENABLE_PHASE12_SKILLS_FORECAST` with fast rollback and deterministic verification.

## Scope
- Backend endpoint: `GET /api/skills/{skill_id}/forecast`
- Frontend forecast panel on Skills cards
- Feature-flag controlled behavior

## Preconditions
1. Latest migrations are applied.
2. Backend and frontend builds are green.
3. Skills API tests are passing.
4. `ENABLE_PHASE12_SKILLS_GOALS=true` and `ENABLE_PHASE12_SKILLS_PATH=true` are already active.

## Rollout Flags
- `ENABLE_PHASE12_SKILLS_GOALS=true`
- `ENABLE_PHASE12_SKILLS_PATH=true`
- `ENABLE_PHASE12_SKILLS_FORECAST=false` (default before canary)
- `ENABLE_PHASE12_SKILLS_GOALS_STRICT` as desired per environment

## Rollout Steps
1. Baseline check (forecast disabled)
   - Confirm backend health endpoint responds.
   - Confirm app is usable with forecast OFF.
2. Canary enablement
   - Set `ENABLE_PHASE12_SKILLS_FORECAST=true` in canary/staging.
   - Restart backend.
3. Functional verification
   - Skills list renders.
   - Skills cards show forecast panel for active skills.
   - Create/edit/practice flows still behave normally.
4. Observability verification
   - No spike in 5xx responses.
   - Forecast endpoint latency stays within acceptable range.
5. Production enablement
   - Enable forecast flag in production.
   - Restart backend and re-run functional checks.

## Rollback Procedure
1. Set `ENABLE_PHASE12_SKILLS_FORECAST=false`.
2. Restart backend service.
3. Verify skills cards still render without forecast panel.
4. Confirm no regression in create/edit/practice flows.

## Quick Verification Commands
```bash
# Validate effective config + health
bash scripts/ops/phase12_skills_forecast_rollout_check.sh

# Override expected values if needed
EXPECT_SKILLS_FORECAST=true bash scripts/ops/phase12_skills_forecast_rollout_check.sh
```

## Release Notes Template
- Enabled deterministic Skills forecast panel behind feature flag.
- Added advisory forecast reason copy only (no autonomous coaching behavior).
- Forecast can be disabled instantly via `ENABLE_PHASE12_SKILLS_FORECAST=false`.
