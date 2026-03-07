# Phase 4 - Calendar Time-Canvas UI (DevOps)

**Audience:** DevOps, QA, Architecture
**Scope:** Feature flag, staged rollout, monitoring during release.
**Non-goals:** No API changes, no backend/layout changes.

## Feature flag
Use `CALENDAR_TIME_CANVAS_UI` to gate the new UI.

Suggested defaults:
- Local/dev: `false` until ready to validate
- Staging: `true` for verification
- Production: ramp from `false` to `true` after metrics stay green

Set via environment:
```bash
CALENDAR_TIME_CANVAS_UI=true
```

## Staged rollout plan
1) **Staging**
   - Enable `CALENDAR_TIME_CANVAS_UI=true`
   - Verify calendar day/week/month views
   - Confirm Phase 3 metrics are green
2) **Production canary**
   - Enable flag for a short window (manual toggle)
   - Monitor dashboards and alerts for 30-60 minutes
3) **Production full**
   - Keep flag enabled
   - Continue monitoring for 24 hours

Rollback: set `CALENDAR_TIME_CANVAS_UI=false` and redeploy/restart.

## Monitoring during release
Run:
```bash
BASE_URL=http://127.0.0.1:8000 \
PROM_URL=http://127.0.0.1:9090 \
PYTHON_BIN=./.venv/bin/python \
./scripts/ops/phase4_calendar_rollout_check.sh
```

Expected:
- `/metrics` includes Phase 3b/3c metrics
- No Phase 3b alerts firing

## Acceptance criteria
- Flag toggles without API changes.
- Read latency does not regress beyond Phase 3c-1 baselines.
- Projection correctness errors, determinism failures, and contract violations remain 0.
