import type { BriefData, BriefFinding } from '@/lib/api/inquiries'

// ── Domain catalog ────────────────────────────────────────────────────────────

export const DOMAIN_CATALOG = [
  { key: 'calendar', label: 'Calendar' },
  { key: 'finance', label: 'Finance' },
  { key: 'habits', label: 'Habits' },
  { key: 'skills', label: 'Skills' },
  { key: 'health', label: 'Health' },
  { key: 'projects', label: 'Projects' },
  { key: 'relationships', label: 'Relationships' },
  { key: 'journal', label: 'Journal' },
]

export const CROSS_DOMAIN_PAIR_CATALOG = [
  { key: 'finance__habits', profile: 'finance_habits_v1', domains: ['finance', 'habits'] },
  { key: 'projects__skills', profile: 'projects_skills_v1', domains: ['projects', 'skills'] },
  { key: 'journal__habits', profile: 'journal_habits_v1', domains: ['journal', 'habits'] },
  { key: 'health__habits', profile: 'health_habits_v1', domains: ['health', 'habits'] },
  { key: 'projects__calendar', profile: 'projects_calendar_v1', domains: ['projects', 'calendar'] },
  { key: 'relationships__journal', profile: 'relationships_journal_v1', domains: ['relationships', 'journal'] },
]

export const EXPERT_RENDERED_DOMAINS = new Set(['finance', 'habits', 'projects', 'skills', 'journal', 'relationships', 'health'])
export const TIMELINE_FIRST_WAVE_DOMAINS = new Set(['finance', 'habits', 'projects', 'skills', 'calendar'])
export const TIMELINE_FIRST_WAVE_APPROVED_PAIR_KEYS = new Set(['finance__habits', 'projects__skills', 'projects__calendar'])

export const TIMELINE_SECTION_BY_CLAIM_TYPE: Record<string, string> = {
  prior_window_comparison: 'Compared with prior window',
  baseline_relative_change: 'Change over time',
  trend_direction: 'Change over time',
  recurrence_observation: 'Recurring pattern',
  continuity_or_break: 'Recurring pattern',
  volatility_description: 'Stability / instability',
  episodic_vs_sustained: 'Recent or sustained',
  approved_pair_alignment_persistence: 'Recent or sustained',
}

export const TIMELINE_SECTION_ORDER = [
  'Change over time',
  'Compared with prior window',
  'Recurring pattern',
  'Stability / instability',
  'Recent or sustained',
]

export const DOMAIN_CATEGORY_LABELS: Record<string, Record<string, string>> = {
  cross_domain: {
    co_occurrence_observation: 'Co-occurrence observation',
    temporal_alignment: 'Temporal alignment',
    trend_alignment: 'Trend alignment',
    coverage_gap: 'Coverage gap',
    structural_dependency_observation: 'Structural dependency observation',
    inconsistency_flag: 'Inconsistency flag',
  },
  finance: { cashflow_coverage: 'Cashflow coverage', ledger_signal: 'Ledger signal', evidence_gap: 'Evidence gap' },
  habits: { adherence_coverage: 'Adherence coverage', consistency_signal: 'Consistency signal', evidence_gap: 'Evidence gap' },
  projects: { execution_coverage: 'Execution coverage', completion_signal: 'Completion signal', evidence_gap: 'Evidence gap' },
  skills: { practice_coverage: 'Practice coverage', progression_signal: 'Progression signal', evidence_gap: 'Evidence gap' },
  journal: { reflection_cadence: 'Reflection cadence', mood_tag_pattern: 'Mood/tag pattern', evidence_gap: 'Evidence gap' },
  relationships: { interaction_cadence: 'Interaction cadence', channel_distribution: 'Channel distribution', evidence_gap: 'Evidence gap' },
  health: { metric_coverage: 'Metric coverage', trend_signal: 'Trend signal', evidence_gap: 'Evidence gap' },
}

export const DOMAIN_REFINE_HINTS: Record<string, string[]> = {
  finance: ['Narrow to posting windows if activity spans mixed account types.', 'Specify one account or receivable scope for denser finance evidence.'],
  habits: ['Focus on one habit or cadence window for cleaner adherence signals.', 'Extend the date range when logs are sparse.'],
  projects: ['Constrain to one delivery window when completion records are mixed.', 'Use one project scope if evidence spans unrelated tasks.'],
  skills: ['Limit inquiry to one skill for clearer progression evidence.', 'Extend window if practice sessions are too sparse.'],
  journal: ['Refine to one reflective theme across a tighter time window.', 'Include explicit tag focus if entries span mixed moods/topics.'],
  relationships: ['Refine to one relationship channel when interactions are mixed.', 'Use a narrower recency window to clarify cadence changes.'],
  health: ['Refine to one metric family when records mix multiple signals.', 'Extend the window if metric coverage is too sparse for trend reading.'],
}

// ── Label helpers ─────────────────────────────────────────────────────────────

export function domainLabel(domain: string, catalog = DOMAIN_CATALOG): string {
  return catalog.find((d) => d.key === domain.toLowerCase())?.label ?? domain
}

export function pairLabel(domains: string[]): string {
  return domains.map((d) => domainLabel(d)).join(' + ')
}

export function titleFromToken(value: string): string {
  return value.replace(/[_-]+/g, ' ').trim().replace(/\b\w/g, (c) => c.toUpperCase())
}

export function categoryLabel(category: string, domain: string): string {
  const labels = DOMAIN_CATEGORY_LABELS[domain.toLowerCase()] ?? {}
  return labels[category] ?? titleFromToken(category) ?? 'Uncategorized'
}

// ── Confidence / answerability ────────────────────────────────────────────────

type BadgeVariant = 'confirmed' | 'informational' | 'needs_review' | 'neutral'

export function confidenceVariant(label: string): BadgeVariant {
  const n = label.toLowerCase()
  if (n === 'confirmed') return 'confirmed'
  if (n === 'informational') return 'informational'
  if (n === 'needs_review') return 'needs_review'
  return 'neutral'
}

export function confidenceText(label: string): string {
  const n = label.toLowerCase()
  if (n === 'needs_review') return 'Needs review'
  if (n === 'informational') return 'Informational'
  if (n === 'confirmed') return 'Confirmed'
  return 'Unspecified'
}

export function answerabilityVariant(classification: string): BadgeVariant {
  const n = classification.toLowerCase()
  if (n === 'strong_answerable') return 'confirmed'
  if (n === 'partial_answerable') return 'informational'
  if (n === 'weak_answerable') return 'needs_review'
  return 'neutral'
}

export function answerabilityText(classification: string): string {
  const n = classification.toLowerCase()
  if (n === 'strong_answerable') return 'Strongly answerable'
  if (n === 'partial_answerable') return 'Partially answerable'
  if (n === 'weak_answerable') return 'Weakly answerable'
  return 'Unspecified'
}

export function badgeClass(variant: BadgeVariant): string {
  const base = 'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium'
  if (variant === 'confirmed') return `${base} bg-green-100 text-green-800`
  if (variant === 'informational') return `${base} bg-blue-100 text-blue-800`
  if (variant === 'needs_review') return `${base} bg-amber-100 text-amber-800`
  return `${base} bg-secondary text-muted-foreground`
}

// ── Timeline helpers ──────────────────────────────────────────────────────────

export function isTimelineFinding(finding: BriefFinding): boolean {
  return Boolean(finding?.timeline_context && typeof finding.timeline_context === 'object')
}

export function timelineScopeAllowed(brief: BriefData): boolean {
  const domains = brief.domains?.map((d) => d.toLowerCase()) ?? []
  if (brief.lens === 'domain' && domains.length === 1) {
    return TIMELINE_FIRST_WAVE_DOMAINS.has(domains[0])
  }
  if (brief.lens === 'cross_domain' && domains.length === 2) {
    return TIMELINE_FIRST_WAVE_APPROVED_PAIR_KEYS.has([...domains].sort().join('__'))
  }
  return false
}

export function timelineSectionLabel(claimType: string): string {
  return TIMELINE_SECTION_BY_CLAIM_TYPE[claimType.toLowerCase()] ?? 'Change over time'
}

// ── Quality ───────────────────────────────────────────────────────────────────

export function clampCoverage(value: number | undefined): number {
  const n = Number(value ?? 0)
  if (isNaN(n) || n < 0) return 0
  if (n > 1) return 1
  return n
}

export function coveragePercent(value: number | undefined): string {
  return `${Math.round(clampCoverage(value) * 100)}%`
}

// ── Date utils ────────────────────────────────────────────────────────────────

export function todayIso(): string {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

export function shiftDateIso(daysBack: number): string {
  const d = new Date()
  d.setDate(d.getDate() - daysBack)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

export function datetimeLocalNow(): string {
  const d = new Date()
  d.setSeconds(0, 0)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}T${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

export function fmtDate(value: string | undefined): string {
  if (!value) return '—'
  const dt = new Date(value)
  return isNaN(dt.getTime()) ? value : dt.toLocaleString()
}

// ── Next questions builder ────────────────────────────────────────────────────

export function buildNextQuestions(brief: BriefData): string[] {
  const findings = brief.findings ?? []
  const questions: string[] = []
  if (!findings.length) questions.push('Would a narrower timeframe help reveal usable evidence?')
  const needsReviewDomains = new Set<string>()
  findings.forEach((f) => {
    if (f.confidence_label?.toLowerCase() === 'needs_review') {
      f.source_domains?.forEach((d) => needsReviewDomains.add(d))
    }
  })
  Array.from(needsReviewDomains).slice(0, 3).forEach((d) => {
    questions.push(`What additional ${domainLabel(d)} records would reduce uncertainty?`)
  })
  if (brief.lens === 'cross_domain') {
    questions.push('Which selected domain should be prioritized for a follow-up scoped inquiry?')
  }
  if (!questions.length) questions.push('Would comparing this scope to a prior timeframe add useful context?')
  return questions.slice(0, 4)
}

// ── Error parsing ─────────────────────────────────────────────────────────────

export function parseApiError(body: Record<string, unknown>, status?: number): string {
  if (status === 409 || body?.error === 'read_only_violation') {
    return 'Read-only contract violation detected. Please refresh and report this issue.'
  }
  if (['contract_mismatch', 'contract_violation', 'schema_mismatch'].includes(String(body?.error ?? ''))) {
    return 'Contract mismatch detected. Please refresh and try again.'
  }
  const alphaErrors: Record<string, string> = {
    alpha_domain_not_visible: 'That domain is not visible in private alpha.',
    alpha_pair_not_enabled: 'That cross-domain pair is not enabled in private alpha.',
    alpha_readiness_not_met: 'Data readiness is not met yet. Open Data Readiness for next steps.',
    alpha_history_disabled: 'Inquiry history is disabled for this private alpha configuration.',
    alpha_pair_required: 'Select one approved cross-domain pair.',
  }
  if (body?.error && alphaErrors[String(body.error)]) return alphaErrors[String(body.error)]
  if (body?.error === 'validation_error') {
    const details = (Array.isArray(body.details) ? body.details : [])
      .map((d: unknown) => (d as { msg?: string; type?: string })?.msg ?? (d as { type?: string })?.type)
      .filter(Boolean)
    return details.length ? `Invalid inquiry: ${details.join('; ')}` : 'Invalid inquiry. Please review scope and timeframe.'
  }
  if (body?.error) return String(body.error).replace(/_/g, ' ')
  if (status === 401) return 'Please sign in.'
  return 'Request failed. Please try again.'
}
