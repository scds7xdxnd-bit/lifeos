# Calendar Event Creation UX - DevOps Runbook

## Purpose
Provide a lightweight smoke test for the new calendar event creation UX markup without changing CI/CD pipelines.

## Smoke test (markup)
- Script: `scripts/ops/calendar_event_creation_ux_smoketest.sh`
- Fetches `/calendar` and verifies:
  - Unified “When” block and start/end controls
  - Four duration presets (15/30/45/60)
  - Advanced options toggle and section
  - Curated 10-color palette
  - Time options datalist

### Usage
```bash
# Defaults to http://localhost:8000/calendar
scripts/ops/calendar_event_creation_ux_smoketest.sh

# Staging example
BASE_URL="https://staging.lifeos.example.com" scripts/ops/calendar_event_creation_ux_smoketest.sh
```

## Rollout notes
- No pipeline changes required.
- Run after frontend deploys or template edits to ensure UX contract remains intact.
- Pair with manual smoke checks for date/time defaults and duration presets.
