# Private Alpha Product/Admin Ops SOP

Owner: Product Ops / Admin Ops
Status: Launch-control SOP (binding for private alpha operations)

## 1. Scope and invariants
- Invite-only access is mandatory. No public signup.
- Active-user cap must remain within `10-30` and never exceed `ALPHA_MAX_USERS`.
- Product framing must remain inquiry-first and non-assistant.
- Visible domains are only `calendar, habits, projects, skills`.
- Visible cross-domain pairs are only `projects + calendar` and `projects + skills`.
- Technical brief access remains available on the inquiry result surface.

## 2. Roles and ownership
- Product Ops Lead: owns cohort gates, invite approvals, and launch decisions.
- Admin Ops: executes invite issue/reissue/revoke actions and keeps ledger current.
- Support Operator: first-line user support for invite/onboarding/readiness/login.
- Backend on-call: auth/invite/readiness/feedback runtime issues.
- Frontend on-call: UX copy/surface confusion and support-path rendering issues.
- DevOps on-call: flag/config/monitoring drift, alert handling, rollout checks.
- QA: regression confirmation before cohort expansion.

## 3. Invite lifecycle SOP
### 3.1 Invite states
- `issued`: token created and sent.
- `accepted`: invite consumed during registration.
- `revoked`: invite manually invalidated by Admin Ops.
- `expired`: invite no longer valid.
- `rejected`: registration blocked (`invite_invalid`, `invite_email_mismatch`, etc.).

### 3.2 Listing invites
To view all issued invites and their current status:
- `python scripts/ops/private_alpha_invite_admin.py list`
- Filter by status: `python scripts/ops/private_alpha_invite_admin.py list --status pending`
- Valid status filters: `pending`, `accepted`, `expired`, `revoked`

Output columns: `id`, `email`, `status`, `created` (ISO 8601), `expires` (ISO 8601), `token_hash_tail` (last 6 chars for ledger reconciliation).

### 3.3 Pre-issue checks (required)
1. Confirm current cohort gate is open (internal, 3, 10, or staged expansion).
2. Run strict rollout check:
   - `bash scripts/ops/private_alpha_rollout_check.sh` with expected envs.
3. Confirm no firing `phase="alpha"` alerts.
4. Confirm capacity using DB + metrics:
   - `accepted_users < cohort_target`
   - `accepted_users + pending_invites < cohort_target`
   - `accepted_users + pending_invites < ALPHA_MAX_USERS`

`pending_invites` means invites with `accepted_at IS NULL`, `revoked_at IS NULL`, and `expires_at` not elapsed.

### 3.4 Issue procedure
1. Add candidate to invite ledger with `status=pending_approval`.
2. Product Ops Lead approves issue.
3. Admin Ops checks capacity:
   - `PYTHONPATH=. python3 scripts/ops/private_alpha_invite_admin.py status --cohort-target <target>`
4. Admin Ops issues invite token:
   - `PYTHONPATH=. python3 scripts/ops/private_alpha_invite_admin.py issue --email <email> --cohort-target <target> --issued-by-user-id <admin_user_id>`
5. Store only last 6 chars of token in ledger (`token_tail`) for reconciliation.
6. Send user message with:
   - invite link `/login?token=...&email=...`
   - supported scope statement
   - support contact path
7. Update ledger `status=sent` and timestamp.

### 3.5 Reissue procedure
Use only for `invite_expired`, `invite_invalid` (copy/paste), or mail-delivery failure.
1. Verify identity and invited email match ledger record.
2. Revoke prior active invite for same email before new issue.
3. Issue replacement token.
4. Mark prior row `status=reissued_from` and link new invite id.
5. Record reason category in ledger.

### 3.6 Revocation procedure
Allowed reasons:
- cohort pause
- compromised/forwarded token
- wrong recipient email
- policy violation or explicit admin decision

Steps:
1. Product Ops Lead approval.
2. Admin Ops revokes invite:
   - `PYTHONPATH=. python3 scripts/ops/private_alpha_invite_admin.py revoke --invite-id <id> --reason "<reason>"`
3. Ledger updated with `revoked_at` and `revoked_reason`.
4. Notify user if invite was previously sent.

### 3.7 Over-issuing prevention rule
- Maintain `cohort_target` variable in ledger (`3`, `10`, `15`, `20`, `30`).
- Hard issuance formula:
  - `issue_allowed = cohort_target - accepted_users - pending_invites`
- If `issue_allowed <= 0`, stop invite issuance.
- If `lifeos:private_alpha_active_user_cap_utilization:ratio >= 0.85`, require explicit Product Ops + DevOps sign-off before any additional invite.

### 3.8 Daily Google Sheet automation (optional but recommended)
Use this to auto-refresh invite status (`pending|accepted|revoked|expired`) to a shared Google Sheet.

1. Create a Google Cloud service account and enable Google Sheets API.
2. Share the target Sheet with the service-account email as Editor.
3. Add repository secrets:
   - `DATABASE_URL` (production DB)
   - `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON, single-line)
   - `PRIVATE_ALPHA_SHEET_ID`
   - `PRIVATE_ALPHA_SHEET_WORKSHEET` (optional, defaults to `invites`)
4. Workflow runs daily at `01:00 UTC` via:
   - `.github/workflows/private-alpha-invite-sheet-sync.yml`
5. Manual trigger available from Actions tab (`workflow_dispatch`).

Local/manual run:
- `PYTHONPATH=. DATABASE_URL=<...> GOOGLE_SERVICE_ACCOUNT_JSON='<json>' python scripts/ops/private_alpha_invite_sheet_sync.py --sheet-id <sheet_id> --worksheet invites`

Sheet columns written by the sync job:
- `invite_id`, `invited_email`, `status`, `created_at`, `expires_at`, `accepted_at`, `revoked_at`, `issued_by_user_id`, `accepted_by_user_id`, `token_hash_tail`, `updated_sync_utc`

## 4. User support path (visible and operational)
Primary user-visible path:
- `Account / Help` page (`/insights/account-help`) with explicit support contact.

Support channels:
- Primary async channel: `ALPHA_SUPPORT_CONTACT` (email or ticket alias).
- Internal escalation channel: `#lifeos-alpha-ops` (ops-only).
- Incident channel: PagerDuty/on-call route for production-impacting failures.

Response SLOs:
- invite/access blockers: first response in 4 business hours
- readiness/onboarding confusion: first response in 8 business hours
- inquiry result/feedback confusion: first response in 8 business hours
- production outage/security concern: immediate on-call escalation

## 5. Onboarding script (user-facing)
Required onboarding script points:
1. LifeOS is a structured personal insight system, not a chatbot/coach/assistant.
2. Supported domains in alpha are `calendar, habits, projects, skills`.
3. Supported cross-domain pairs are only `projects + calendar`, `projects + skills`.
4. Start on Data Readiness (`/insights/data`) before first inquiry.
5. Inquiry output defaults to a humanized brief; technical brief is always available for verification.
6. Feedback is submitted from inquiry results only.
7. Unsupported surfaces/domains are intentionally hidden for reliability.

## 6. Feedback triage and escalation
### 6.1 Intake sources
- In-product feedback (`helpful`, `unclear`, `too_technical`, `too_long`, `incorrect`, `not_useful_yet`, `other`)
- Support tickets
- Concierge call notes

### 6.2 Triage taxonomy
- `ACCESS_INVITE`: token, registration, login, cap blocks
- `ONBOARDING_READINESS`: readiness blocked and setup confusion
- `INQUIRY_QUALITY`: unclear/too technical/too long/not useful
- `INQUIRY_CORRECTNESS`: incorrect claims or confidence concerns
- `UI_NAVIGATION`: inability to find inquiry/history/data/help surfaces
- `POLICY_SCOPE`: unsupported domain/pair requests
- `INCIDENT_RUNTIME`: elevated failure/fallback/latency alerts

### 6.3 Escalation routing
- Backend: ACCESS_INVITE, readiness logic, feedback persistence/API errors
- Frontend: UI_NAVIGATION, onboarding/support copy clarity, visible support path
- DevOps: alert fires, flag drift, rollout check failures
- QA: reproducibility verification and regression confirmation
- Architecture: scope/policy ambiguities and trust-model conflicts

### 6.4 Review cadence
- Internal + 3-user phases: daily triage review
- 10-user phase: 3x weekly plus daily while alerts are active
- 30-user expansion: weekly review plus ad-hoc incident reviews

## 7. Cohort gate rules (go/no-go)
### 7.1 Internal -> 3 concierge
Go only if:
- strict rollout check passes
- no firing alpha alerts for one observation window
- manual QA checklist passes
- support path and on-call rota staffed

### 7.2 3 concierge -> 10 users
Go only if prior phase is stable for 48h and:
- `PrivateAlphaInviteRejectionRateHigh` not firing
- `PrivateAlphaReadinessBlockedHigh` not firing
- `PrivateAlphaInquiryFailureRateHigh` not firing
- `PrivateAlphaHumanizationFallbackRateHigh` not firing
- no unresolved P0/P1 support issues

### 7.3 10 users -> staged expansion to 30
Go only if prior phase is stable for 7 days and:
- no critical alpha alerts
- warning alerts remain below sustained thresholds
- support backlog SLA compliance >= 95%
- Product Ops + DevOps sign-off for each increment (`15`, `20`, `30`)

No-go triggers for all phases:
- cap reached alert firing
- repeat invite/auth failures without mitigation
- unresolved data-loss or trust-model issues
- inability to provide technical brief access on inquiry results

## 8. Required operational artifacts
- Invite ledger: `lifeos/docs/ops/private_alpha_invite_ledger_template.csv`
- Support intake template: `lifeos/docs/ops/private_alpha_support_intake_template.md`
- Launch checklist: `lifeos/docs/ops/private_alpha_manual_qa_checklist.md`
- Launch runbook: `lifeos/docs/ops/private_alpha_launch_ops.md`
- Invite admin helper: `scripts/ops/private_alpha_invite_admin.py`
- Invite Google Sheet sync helper: `scripts/ops/private_alpha_invite_sheet_sync.py`
