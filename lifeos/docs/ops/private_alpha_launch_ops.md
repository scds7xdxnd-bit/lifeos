# Private Alpha Launch Ops Runbook

Scope: simplest reliable deployment and rollout discipline for invite-only private alpha.

## 1. Operating invariants
- Invite-only access is mandatory.
- User cap remains bounded to `10–30`.
- Inquiry is humanized-by-default with canonical technical brief available on the same screen.
- Alpha-visible domains are `calendar, habits, projects, skills`.
- Alpha-visible cross-domain pair profiles are `projects_calendar_v1, projects_skills_v1`.
- No assistant/chat fallback behavior is allowed.

## 2. Required flags and defaults
Private-alpha scope flags:
- `ENABLE_PRIVATE_ALPHA=true`
- `ALPHA_INVITE_ONLY=true`
- `ALPHA_MAX_USERS=30`
- `ALPHA_VISIBLE_DOMAINS=calendar,habits,projects,skills`
- `ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES=projects_calendar_v1,projects_skills_v1`
- `ALPHA_ENABLE_TECHNICAL_BRIEF=true`
- `ALPHA_ENABLE_HISTORY=true`
- `ALPHA_ENABLE_INQUIRY_FEEDBACK=true`
- `ALPHA_HIDE_DOMAIN_CRUD=true`
- `ALPHA_REQUIRE_DATA_READINESS=true`
- `ALPHA_ENABLE_CALENDAR_SYNC=true`
- `ALPHA_SUPPORT_CONTACT=<support channel>`

Inquiry/runtime flags that must also be enabled:
- `ENABLE_PHASE6_FOCUSED_INQUIRY=true`
- `ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES=true`
- `PHASE8_ENABLED_PAIR_PROFILES=projects_calendar_v1,projects_skills_v1`
- `ENABLE_PHASE9_TIMELINE_INTELLIGENCE=true`
- `PHASE9_ENABLED_TIMELINE_PROFILES=calendar_timeline_v1,habits_timeline_v1,projects_timeline_v1,skills_timeline_v1,projects_calendar_timeline_v1,projects_skills_timeline_v1`
- `ENABLE_PHASE10_INQUIRY_HUMANIZATION=true`

Migration gate:
- `PHASE6_INQUIRY_MIGRATION_HEAD=20260314_private_alpha_feedback_linkage`

## 3. Observability contract
Private-alpha metrics (required):
- `lifeos_private_alpha_active_users`
- `lifeos_private_alpha_user_cap`
- `lifeos_private_alpha_user_cap_utilization_ratio`
- `lifeos_private_alpha_enabled`
- `lifeos_private_alpha_invites_issued_total`
- `lifeos_private_alpha_invites_accepted_total`
- `lifeos_private_alpha_invites_rejected_total{reason}`
- `lifeos_private_alpha_readiness_evaluated_total{status}`
- `lifeos_private_alpha_readiness_blocked_total{reason}`
- `lifeos_inquiry_feedback_submitted_total{feedback_type,surface,deduped}`
- `lifeos_inquiry_feedback_submitted_by_domain_total{domain,profile,...}`

Derived recordings (required):
- `lifeos:private_alpha_active_user_cap_utilization:ratio`
- `lifeos:private_alpha_invite_acceptance_rate:ratio`
- `lifeos:private_alpha_invite_rejection_rate:ratio`
- `lifeos:private_alpha_readiness_completion_rate:ratio`
- `lifeos:private_alpha_readiness_blocked_rate:ratio`
- `lifeos:private_alpha_feedback_submission_rate:per_second`
- `lifeos:private_alpha_inquiry_failure_rate:ratio`
- `lifeos:private_alpha_inquiry_latency_p95:seconds`
- `lifeos:private_alpha_humanization_fallback_rate:ratio`
- `lifeos:private_alpha_technical_brief_expansion_rate:ratio`

Alerts (required):
- `PrivateAlphaUserCapNearLimit`
- `PrivateAlphaUserCapReached`
- `PrivateAlphaInviteRejectionRateHigh`
- `PrivateAlphaReadinessBlockedHigh`
- `PrivateAlphaInquiryFailureRateHigh`
- `PrivateAlphaHumanizationFallbackRateHigh`

Dashboard:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-private-alpha-dashboard.json`

## 4. Strict launch checks
Strict rollout gate command:

```bash
BASE_URL=http://127.0.0.1:8000 \
PROM_URL=http://127.0.0.1:9090 \
EXPECT_MIGRATION_MATCH=true \
PRIVATE_ALPHA_ENABLED=true \
ALPHA_EXPECT_INVITE_ONLY=true \
ALPHA_EXPECT_MAX_USERS=30 \
ALPHA_EXPECT_VISIBLE_DOMAINS=calendar,habits,projects,skills \
ALPHA_EXPECT_PAIR_PROFILES=projects_calendar_v1,projects_skills_v1 \
ALPHA_EXPECT_TECHNICAL_BRIEF=true \
ALPHA_EXPECT_HISTORY=true \
ALPHA_EXPECT_INQUIRY_FEEDBACK=true \
ALPHA_EXPECT_HIDE_DOMAIN_CRUD=true \
ALPHA_EXPECT_REQUIRE_DATA_READINESS=true \
ALPHA_EXPECT_CALENDAR_SYNC=true \
bash scripts/ops/private_alpha_rollout_check.sh
```

Snapshot capture command:

```bash
PROM_URL=http://127.0.0.1:9090 SNAPSHOT_LABEL=alpha-baseline bash scripts/ops/private_alpha_snapshot.sh
```

## 5. Release-candidate deployment sequence (live)
1. Prepare RC branch and freeze scope:
- No new feature merges after RC cut.
- Only launch-control fixes are allowed until internal validation is complete.

2. Verify runtime env file values:
- Confirm all flags in section 2 are present and exact.
- Confirm `PHASE6_INQUIRY_MIGRATION_HEAD=20260314_private_alpha_feedback_linkage`.

3. Deploy web image/container:
```bash
docker compose pull web || true
docker compose build web
docker compose up -d --force-recreate web
```

4. Verify migration head parity before rollout:
```bash
docker compose exec -T web /bin/sh -lc 'cd /app && PYTHONPATH=. python -m alembic current && PYTHONPATH=. python -m alembic heads'
docker compose exec -T web /bin/sh -lc 'cd /app && PYTHONPATH=. python -m alembic upgrade head'
docker compose exec -T web /bin/sh -lc 'cd /app && PYTHONPATH=. python -m alembic current'
```
- Expected head: `20260314_private_alpha_feedback_linkage`

5. Restart runtime to refresh startup migration parity metric:
```bash
docker compose restart web
```

6. Execute strict rollout and snapshot:
```bash
BASE_URL=http://127.0.0.1:8000 PROM_URL=http://127.0.0.1:9090 EXPECT_MIGRATION_MATCH=true PRIVATE_ALPHA_ENABLED=true ALPHA_EXPECT_VISIBLE_DOMAINS=calendar,habits,projects,skills ALPHA_EXPECT_PAIR_PROFILES=projects_calendar_v1,projects_skills_v1 bash scripts/ops/private_alpha_rollout_check.sh
PROM_URL=http://127.0.0.1:9090 SNAPSHOT_LABEL=alpha-rc bash scripts/ops/private_alpha_snapshot.sh
```

7. Confirm Grafana dashboards load:
- `lifeos-private-alpha`
- `lifeos-inquiry-ops`
- `lifeos-app-monitoring`

## 6. Staged rollout sequence
1. Internal validation:
- Run strict rollout check.
- Confirm no `phase="alpha"` alerts firing for one observation window.

2. Concierge cohort (3 users):
- Issue at most 3 invites.
- Track invite rejection/readiness blocked/humanization fallback rates.
- Pause expansion if warnings are sustained.

3. Alpha cohort (10 users):
- Raise `ALPHA_MAX_USERS=10` only after concierge cohort is stable.
- Keep pair profile scope fixed (`projects_calendar_v1`, `projects_skills_v1`).

4. Expansion cohort (up to 30 users):
- Raise `ALPHA_MAX_USERS` gradually (for example `15 -> 20 -> 30`).
- Only expand if inquiry failure and fallback alerts remain quiet.

## 7. Failure handling and rollback
Primary rollback sequence:
1. Narrow pair scope first:
- Set `PHASE8_ENABLED_PAIR_PROFILES=` (or keep only one pair profile).
- Keep single-domain inquiry active.

2. Disable timeline layer if needed:
- `ENABLE_PHASE9_TIMELINE_INTELLIGENCE=false`

3. Disable humanized-default if needed:
- `ENABLE_PHASE10_INQUIRY_HUMANIZATION=false`
- Canonical brief path remains active.

4. Shell fallback (last step):
- `ENABLE_PRIVATE_ALPHA=false`

Hard rollback invariant:
- Never switch to assistant/chat behavior.

## 8. Frontend alpha shell map
- Inquiry: `/insights/inquiry`
- History: `/insights/history`
- Data readiness: `/insights/data`
- Account/help: `/insights/account-help`
- Invite entrypoint: `/invite?token=<invite_token>`

## 9. Product/Admin launch-control workflow
Use `lifeos/docs/ops/private_alpha_product_admin_ops_sop.md` as the operator source of truth for:
- invite issue/reissue/revoke lifecycle
- anti-over-issuing capacity checks
- user-support intake and escalation routing
- cohort go/no-go approvals

Required artifacts:
- invite ledger template: `lifeos/docs/ops/private_alpha_invite_ledger_template.csv`
- support intake template: `lifeos/docs/ops/private_alpha_support_intake_template.md`
- invite admin helper: `scripts/ops/private_alpha_invite_admin.py`

## 10. Launch-control hard stops
- Do not issue invites when `accepted_users + pending_invites >= cohort_target`.
- Do not issue invites when `accepted_users + pending_invites >= ALPHA_MAX_USERS`.
- Do not proceed to next cohort while any `phase="alpha"` alert is firing.
- Do not remove technical brief access from inquiry results.
- Do not introduce assistant/chat framing as a mitigation path.

## 11. RC freeze sign-off checklist
- [ ] Runtime env and docker-compose flag parity verified against section 2.
- [ ] Live DB head and expected head both at `20260314_private_alpha_feedback_linkage`.
- [ ] `lifeos_phase6_inquiry_migration_mismatch` is `0.0`.
- [ ] Strict rollout check passes with migration match enforced.
- [ ] Snapshot captured and archived (`alpha-rc` label).
- [ ] No `phase="alpha"` alerts firing during observation window.
- [ ] Product Ops confirms invite ledger + support intake workflow is staffed.
