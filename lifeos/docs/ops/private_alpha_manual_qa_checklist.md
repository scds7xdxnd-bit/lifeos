# Private Alpha Manual QA Checklist

Owner: QA
Scope: ratified private alpha launch boundaries only.

## 1. Invite-only access
- Verify `POST /auth/register` without `invite_token` is blocked with `invite_required`.
- Verify invalid invite token is blocked with `invite_invalid`.
- Verify expired invite token is blocked with `invite_expired`.
- Verify already-used invite token is blocked with `invite_already_used`.
- Verify valid invite token allows registration for invited email.

## 2. Alpha shell and navigation
- Sign in as non-admin alpha user.
- Verify primary nav contains only:
  - `Inquiry`
  - `History`
  - `Data`
  - `Account / Help`
- Verify broad domain nav is not primary in alpha shell (`Finance`, `Journal`, `Health`, `Relationships` absent from top nav).

## 3. Domain and pair gating
- Verify visible single domains:
  - `calendar`
  - `habits`
  - `projects`
  - `skills`
- Verify hidden/non-alpha domains are blocked:
  - `finance`
  - `journal`
  - `health`
  - `relationships`
- Verify live cross-domain pairs:
  - `projects + calendar`
  - `projects + skills`
- Verify unsupported pairs are blocked.

## 4. Onboarding/readiness
- Verify not-ready state returns clear blocker and next step.
- Verify ready state after adding recent events in visible scope.
- Verify readiness endpoint: `GET /api/v1/inquiries/readiness`.

## 5. Inquiry flow
- Create inquiry in visible scope.
- Verify results render humanized brief by default.
- Verify technical brief can be expanded on same surface.
- Verify refine creates new version and history shows both versions.
- Verify feedback submit works and remains on same result surface.

## 6. Fallback behavior
- Humanization failure: verify canonical fallback is returned and UI remains usable.
- Timeline failure: verify non-temporal fallback result is returned.
- Unsupported cross-domain request: verify blocked response with explicit error.
- Insufficient evidence: verify insufficiency state is explicit, not broken output.

## 7. Guardrails
- Verify no assistant/chat framing:
  - no transcript UI
  - no assistant persona language
- Verify no recommendation/causal/prediction leakage in inquiry result text.
- Verify no dashboard overload in inquiry-first shell.
- Verify evidence references remain visible.
- Verify confidence labels are preserved.
- Verify technical brief access is always available when enabled.

## 8. Support path visibility
- Verify `/insights/account-help` exposes a visible support contact path.
- Verify support path covers:
  - invite/access issues
  - onboarding/readiness confusion
  - login escalation
  - inquiry concern escalation

## 9. Deployed smoke suite (must run against live alpha env)
- Verify web and Prometheus endpoints are reachable before smoke execution.
- Run strict launch gate:
  - `BASE_URL=<alpha_base_url> PROM_URL=<prom_url> EXPECT_MIGRATION_MATCH=true PRIVATE_ALPHA_ENABLED=true ALPHA_EXPECT_INVITE_ONLY=true ALPHA_EXPECT_MAX_USERS=30 ALPHA_EXPECT_VISIBLE_DOMAINS=calendar,habits,projects,skills ALPHA_EXPECT_PAIR_PROFILES=projects_calendar_v1,projects_skills_v1 ALPHA_EXPECT_TECHNICAL_BRIEF=true ALPHA_EXPECT_HISTORY=true ALPHA_EXPECT_INQUIRY_FEEDBACK=true ALPHA_EXPECT_HIDE_DOMAIN_CRUD=true ALPHA_EXPECT_REQUIRE_DATA_READINESS=true ALPHA_EXPECT_CALENDAR_SYNC=true bash scripts/ops/private_alpha_rollout_check.sh`
- Capture rollout snapshot:
  - `PROM_URL=<prom_url> SNAPSHOT_LABEL=alpha-<stage> bash scripts/ops/private_alpha_snapshot.sh`
- Verify DB migration parity:
  - `python -m alembic current`
  - `python -m alembic heads`
  - expected head: `20260314_private_alpha_feedback_linkage`
- Verify migration mismatch metric equals zero:
  - `lifeos_phase6_inquiry_migration_mismatch{expected_head="20260314_private_alpha_feedback_linkage"} 0.0`

## 10. Staged manual signoff gates
- Internal rollout gate:
  - strict launch gate command passes
  - no firing alpha alerts
  - invite-only enforced and public signup blocked
  - humanized default + technical brief same-surface verified
  - unsupported domains and unsupported pairs hidden/blocked
- 3-user concierge gate:
  - internal rollout gate complete
  - Product Ops support path staffed and visible
  - invite ledger and support intake artifacts in active use
  - no unresolved P0/P1 defects for invite/readiness/inquiry/fallback
- 10-user expansion gate:
  - 3-user concierge gate complete
  - stability window completed with no sustained alpha alert failures
  - no scope leakage (hidden domains, unsupported pairs, assistant/chat framing)
  - fallback behavior remains safe (`humanization -> canonical`, insufficiency explicit, no broken results)
