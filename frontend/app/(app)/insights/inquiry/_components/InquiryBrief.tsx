'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import type { BriefData, BriefFinding, EvidenceRef, HumanizedBriefSection, InquiryVersion } from '@/lib/api/inquiries'
import {
  badgeClass, confidenceVariant, confidenceText,
  answerabilityVariant, answerabilityText,
  coveragePercent, fmtDate,
  domainLabel, categoryLabel, titleFromToken,
  isTimelineFinding, timelineScopeAllowed, timelineSectionLabel,
  TIMELINE_SECTION_ORDER, DOMAIN_REFINE_HINTS, EXPERT_RENDERED_DOMAINS,
  buildNextQuestions,
} from './helpers'

// ── Sub-components ────────────────────────────────────────────────────────────

function Badge({ label, variant = 'neutral' }: { label: string; variant?: 'confirmed' | 'informational' | 'needs_review' | 'neutral' }) {
  return <span className={badgeClass(variant)}>{label}</span>
}

function EvidenceRefRow({ ref: r }: { ref: EvidenceRef }) {
  if (r.source_kind === 'read_model') {
    return <li className="text-xs text-muted-foreground">Projection count: events {r.event_count ?? 0}, insights {r.insight_count ?? 0}</li>
  }
  const type = r.event_type ?? r.insight_type ?? r.source_kind ?? 'record'
  const id = r.source_id ? `#${r.source_id}` : (r.source_ref ?? '')
  const created = r.created_at ? ` · ${fmtDate(r.created_at)}` : ''
  return <li className="text-xs text-muted-foreground">{type}{id ? ` ${id}` : ''}{created}</li>
}

function EvidenceGroup({ domain, refs }: { domain: string; refs: EvidenceRef[] }) {
  return (
    <div className="mt-1.5">
      <div className="text-xs font-medium text-muted-foreground">{domainLabel(domain)}</div>
      <ul className="ml-2 space-y-0.5">
        {refs.length ? refs.map((r, i) => <EvidenceRefRow key={i} ref={r} />) : <li className="text-xs text-muted-foreground">No evidence refs.</li>}
      </ul>
    </div>
  )
}

function groupByDomain(refs: EvidenceRef[]): [string, EvidenceRef[]][] {
  const map = new Map<string, EvidenceRef[]>()
  refs.forEach((r) => {
    const d = r.domain ?? 'unknown'
    if (!map.has(d)) map.set(d, [])
    map.get(d)!.push(r)
  })
  return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b))
}

function FindingCard({ finding, domain }: { finding: BriefFinding; domain: string }) {
  const variant = confidenceVariant(finding.confidence_label ?? '')
  const grouped = groupByDomain(finding.evidence_refs ?? [])
  return (
    <div className="rounded-xl bg-white/40 p-3.5 space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div className="space-y-1 flex-1">
          {finding.finding_category && (
            <span className="text-xs text-muted-foreground">{categoryLabel(finding.finding_category, domain)}</span>
          )}
          <p className="text-sm">{finding.claim || 'No claim provided.'}</p>
        </div>
        <Badge label={confidenceText(finding.confidence_label ?? '')} variant={variant} />
      </div>
      {finding.relevance_reason && (
        <p className="text-xs text-muted-foreground">
          <span className="font-medium">Why this matters{finding.relevance_rank ? ` (rank ${finding.relevance_rank})` : ''}:</span>{' '}
          {finding.relevance_reason}
        </p>
      )}
      <p className="text-xs text-muted-foreground italic">{finding.uncertainty_note || 'No uncertainty note.'}</p>
      <div className="pt-1">
        {grouped.length ? grouped.map(([d, refs]) => <EvidenceGroup key={d} domain={d} refs={refs} />) : (
          <p className="text-xs text-muted-foreground">No evidence refs.</p>
        )}
      </div>
    </div>
  )
}

function TimelineFindingCard({ finding }: { finding: BriefFinding }) {
  const ctx = finding.timeline_context!
  const variant = confidenceVariant(finding.confidence_label ?? '')
  const grouped = groupByDomain(finding.evidence_refs ?? [])
  const isInsufficient = ctx.coverage_status === 'insufficient'
    || finding.uncertainty_note?.toLowerCase().includes('insufficient')
    || finding.uncertainty_note?.toLowerCase().includes('sparse')
    || !grouped.length

  return (
    <div className={`rounded-xl p-3.5 space-y-2 ${isInsufficient ? 'bg-amber-50/50' : 'bg-white/40'}`}>
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm flex-1">{finding.claim || 'No temporal claim provided.'}</p>
        <Badge label={confidenceText(finding.confidence_label ?? '')} variant={variant} />
      </div>
      <div className="flex flex-wrap gap-2">
        <span className="text-xs bg-secondary text-muted-foreground px-2 py-0.5 rounded">Active: {ctx.active_window_label || 'Unavailable'}</span>
        <span className="text-xs bg-secondary text-muted-foreground px-2 py-0.5 rounded">Compared: {ctx.comparison_label || 'Unavailable'}</span>
      </div>
      <p className="text-xs text-muted-foreground italic">{finding.uncertainty_note || 'No temporal uncertainty note.'}</p>
      {isInsufficient && (
        <p className="text-xs text-amber-700">
          {!grouped.length ? 'Insufficient temporal provenance: no evidence references.' : 'Insufficient history for full temporal interpretation.'}
        </p>
      )}
      {grouped.map(([d, refs]) => <EvidenceGroup key={d} domain={d} refs={refs} />)}
    </div>
  )
}

function HumanizedSection({ section }: { section: HumanizedBriefSection }) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {section.title ?? section.section_id ?? 'Section'}
      </p>
      {!section.blocks.length ? (
        <p className="text-xs text-muted-foreground">No readable blocks available.</p>
      ) : (
        section.blocks.map((block, i) => {
          const variant = block.confidence_label ? confidenceVariant(block.confidence_label) : 'neutral'
          const grouped = groupByDomain(block.evidence_refs ?? [])
          const findingIds = block.source_finding_ids ?? []
          const limitIds = block.source_limitation_ids ?? []
          return (
            <div key={i} className="rounded-xl bg-white/40 p-3.5 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm flex-1">{block.text || 'No humanized block text.'}</p>
                <Badge
                  label={block.confidence_label ? confidenceText(block.confidence_label) : 'Context block'}
                  variant={variant}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Finding IDs: {findingIds.length ? findingIds.join(', ') : 'none'} · Limitation IDs: {limitIds.length ? limitIds.join(', ') : 'none'}
              </p>
              {grouped.map(([d, refs]) => <EvidenceGroup key={d} domain={d} refs={refs} />)}
            </div>
          )
        })
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

interface InquiryBriefProps {
  brief: BriefData | null
  versions: InquiryVersion[]
  selectedVersionId: number | null
  inquiryId: number | null
  alphaFeedbackEnabled: boolean
  onVersionSelect: (v: InquiryVersion) => void
  onFeedback: (type: string, surface: string, note: string) => void
  feedbackStatus: { text: string; tone: string } | null
  alertMessage: { text: string; tone: string } | null
}

export function InquiryBrief({
  brief,
  versions,
  selectedVersionId,
  inquiryId,
  alphaFeedbackEnabled,
  onVersionSelect,
  onFeedback,
  feedbackStatus,
  alertMessage,
}: InquiryBriefProps) {
  const [technicalOpen, setTechnicalOpen] = useState(false)
  const [feedbackNote, setFeedbackNote] = useState('')

  const humanizedBrief = brief?.humanized_brief
  const technicalViewAvailable = Boolean(humanizedBrief?.metadata?.technical_view_available)

  // Reset technical toggle when brief changes
  const showTechnical = !humanizedBrief || technicalOpen

  if (!brief) {
    return (
      <div
        className="p-5 sm:p-7"
        style={{
          background: '#ffffff',
          borderRadius: '0 16px 16px 16px',
          boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
        }}
      >
        <div>
          <h3
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontSize: '1.125rem',
              fontWeight: 400,
              color: '#4b6646',
              letterSpacing: '-0.03em',
            }}
          >
            Generated Brief
          </h3>
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72', marginTop: '4px' }}>
            Summary first, then evidence, then limits.
          </p>
        </div>
        <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72', marginTop: '16px' }}>
          No brief generated yet.
        </p>
      </div>
    )
  }

  const findings = brief.findings ?? []
  const temporalFindings = findings.filter(isTimelineFinding)
  const nonTemporalFindings = findings.filter((f) => !isTimelineFinding(f))

  const confidenceLabels = new Set(findings.map((f) => f.confidence_label?.toLowerCase()).filter(Boolean))
  const overallConfidence = confidenceLabels.size === 0 ? 'neutral'
    : confidenceLabels.size > 1 ? 'neutral'
    : confidenceVariant(Array.from(confidenceLabels)[0] as string)
  const overallConfidenceText = confidenceLabels.size === 0 ? 'No confidence labels'
    : confidenceLabels.size > 1 ? 'Mixed confidence'
    : confidenceText(Array.from(confidenceLabels)[0] as string)

  const metaParts: string[] = []
  if (brief.lens) metaParts.push(`Lens: ${brief.lens}`)
  if (brief.domains?.length) metaParts.push(`Domains: ${brief.domains.map((d) => domainLabel(d)).join(', ')}`)
  if (brief.timeframe?.start && brief.timeframe?.end) metaParts.push(`Window: ${brief.timeframe.start} → ${brief.timeframe.end}`)
  if (brief.as_of_ts) metaParts.push(`As of ${fmtDate(brief.as_of_ts)}`)
  const selectedVersion = versions.find((v) => v.id === selectedVersionId)
  if (selectedVersion) metaParts.unshift(`v${selectedVersion.version_number}`)

  const briefProfile = brief.brief_profile
  const isCrossDomain = brief.lens === 'cross_domain' && (brief.domains?.length ?? 0) === 2
  const categoryDomain = isCrossDomain ? 'cross_domain' : (briefProfile?.domain ?? '')

  const isExpert = Boolean(briefProfile?.expert_mode && EXPERT_RENDERED_DOMAINS.has(briefProfile?.domain ?? ''))
  const nextQuestions = buildNextQuestions(brief)

  const qualityMeta = brief.quality_metadata
  const prodMeta = brief.productization_metadata
  const timelineAllowed = timelineScopeAllowed(brief)

  return (
    <div
      className="p-5 sm:p-7 space-y-5"
      style={{
        background: '#ffffff',
        borderRadius: '0 16px 16px 16px',
        boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
      }}
    >
      {/* Header */}
      <div>
        <h3
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '1.125rem',
            fontWeight: 400,
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          Generated Brief
        </h3>
        <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72', marginTop: '4px' }}>
          Summary first, then evidence, then limits.
        </p>
      </div>

      {/* Alert banner */}
      {alertMessage?.text && (
        <div className={`text-sm px-3 py-2 rounded-md ${
          alertMessage.tone === 'error' ? 'bg-destructive/10 text-destructive'
            : alertMessage.tone === 'warning' ? 'bg-amber-50 text-amber-800'
            : 'bg-secondary text-foreground'
        }`}>
          {alertMessage.text}
        </div>
      )}

      {/* Version chips */}
      {versions.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {versions.map((v) => (
            <button
              key={v.id}
              onClick={() => onVersionSelect(v)}
              className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                v.id === selectedVersionId
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-muted-foreground hover:bg-secondary/80'
              }`}
            >
              v{v.version_number}
            </button>
          ))}
        </div>
      )}

      {/* Brief toolbar */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <p className="text-xs text-muted-foreground">{metaParts.join(' · ')}</p>
        <div className="flex items-center gap-2">
          <Badge label={overallConfidenceText} variant={overallConfidence} />
          {technicalViewAvailable && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setTechnicalOpen(!technicalOpen)}
            >
              {technicalOpen ? 'Hide technical brief' : 'Technical brief'}
            </Button>
          )}
        </div>
      </div>

      {/* ── Humanized brief ── */}
      {humanizedBrief && (
        <section className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Readable Brief</p>
          <div className="bg-white/50 rounded-xl p-5 space-y-2">
            <p className="text-sm font-medium">{humanizedBrief.answer?.text || 'No humanized summary generated.'}</p>
            <p className="text-xs text-muted-foreground">Answerability and confidence remain canonical in the blocks below.</p>
            <p className="text-xs text-muted-foreground">
              Source finding IDs: {humanizedBrief.answer?.source_finding_ids?.join(', ') || 'none'} ·
              Source limitation IDs: {humanizedBrief.answer?.source_limitation_ids?.join(', ') || 'none'}
            </p>
          </div>
          <div className="space-y-4">
            {humanizedBrief.sections.map((s, i) => <HumanizedSection key={i} section={s} />)}
          </div>
        </section>
      )}

      {/* ── Feedback ── */}
      {alphaFeedbackEnabled && inquiryId && selectedVersionId && (
        <section className="border-t border-border pt-4 space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Feedback</p>
          <p className="text-xs text-muted-foreground">
            Surface: {showTechnical ? 'technical brief' : 'humanized brief'}
          </p>
          <div className="flex flex-wrap gap-2">
            {(['helpful', 'unclear', 'too_technical', 'not_useful_yet'] as const).map((ft) => (
              <Button
                key={ft}
                variant="secondary"
                size="sm"
                onClick={() => onFeedback(ft, showTechnical ? 'technical' : 'humanized', feedbackNote)}
              >
                {ft.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </Button>
            ))}
          </div>
          <div className="space-y-1.5">
            <label className="text-xs text-muted-foreground">Optional note</label>
            <textarea
              rows={2}
              maxLength={280}
              placeholder="Optional feedback note"
              value={feedbackNote}
              onChange={(e) => setFeedbackNote(e.target.value)}
              className="w-full rounded-xl border border-white/40 bg-white/50 backdrop-blur-sm px-3.5 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring/30"
            />
          </div>
          {feedbackStatus?.text && (
            <p className={`text-xs ${feedbackStatus.tone === 'error' ? 'text-destructive' : feedbackStatus.tone === 'success' ? 'text-green-700' : 'text-muted-foreground'}`}>
              {feedbackStatus.text}
            </p>
          )}
        </section>
      )}

      {/* ── Technical brief (shown when no humanized brief, or when toggled open) ── */}
      {showTechnical && (
        <section className="space-y-4 border-t border-border pt-4">
          {humanizedBrief && (
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Technical Brief — Canonical structured view
            </p>
          )}

          {/* Summary */}
          <Block label="Summary">
            <p className="text-sm">{brief.summary || 'No summary generated.'}</p>
          </Block>

          {/* Direct answer */}
          {brief.direct_answer && (
            <Block label="Direct Answer">
              <p className="text-sm font-medium">{brief.direct_answer.text || 'No direct answer generated.'}</p>
              <p className="text-xs text-muted-foreground mt-1">{brief.direct_answer.note || 'Derived from evidence-bounded findings only.'}</p>
              {brief.direct_answer.supporting_claims?.length ? (
                <ul className="mt-2 space-y-0.5">
                  {brief.direct_answer.supporting_claims.map((c, i) => <li key={i} className="text-xs text-muted-foreground">· {c}</li>)}
                </ul>
              ) : (
                <p className="text-xs text-muted-foreground mt-1">No supporting claims listed.</p>
              )}
            </Block>
          )}

          {/* Answerability */}
          {brief.answerability && (
            <Block label="Answerability Status">
              <div className="flex items-center gap-2 flex-wrap">
                <Badge
                  label={answerabilityText(brief.answerability.classification ?? '')}
                  variant={answerabilityVariant(brief.answerability.classification ?? '')}
                />
                <span className="text-xs text-muted-foreground">
                  {Number.isFinite(brief.answerability.evidence_coverage_ratio)
                    ? `${coveragePercent(brief.answerability.evidence_coverage_ratio)} coverage · `
                    : ''}
                  {brief.answerability.supporting_finding_count ?? 0} supporting findings
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {brief.answerability.reason || 'Answerability details unavailable.'}
              </p>
            </Block>
          )}

          {/* Timeline findings */}
          {timelineAllowed && temporalFindings.length > 0 && (
            <Block label="Timeline Findings">
              {brief.timeline_metadata && (
                <div className="text-xs text-muted-foreground space-y-0.5 mb-3">
                  <p>Profile {brief.timeline_metadata.timeline_profile_id} (v{brief.timeline_metadata.timeline_profile_version}) · Window {brief.timeline_metadata.window_spec_token} · Timezone {brief.timeline_metadata.timezone_token}</p>
                  {brief.timeline_metadata.comparison_coverage && (
                    <p>
                      Prior window {brief.timeline_metadata.comparison_coverage.prior_window_available ? 'available' : 'unavailable'} ·
                      Baseline {brief.timeline_metadata.comparison_coverage.baseline_windows_available}/{brief.timeline_metadata.comparison_coverage.baseline_windows_required}
                    </p>
                  )}
                </div>
              )}
              {(() => {
                const grouped = new Map<string, BriefFinding[]>()
                temporalFindings.forEach((f) => {
                  const sec = timelineSectionLabel(f.timeline_context?.claim_type ?? f.finding_category ?? '')
                  if (!grouped.has(sec)) grouped.set(sec, [])
                  grouped.get(sec)!.push(f)
                })
                const ordered = [
                  ...TIMELINE_SECTION_ORDER.filter((s) => grouped.has(s)),
                  ...Array.from(grouped.keys()).filter((s) => !TIMELINE_SECTION_ORDER.includes(s)),
                ]
                return ordered.map((sectionName) => (
                  <div key={sectionName} className="space-y-2 mt-2">
                    <p className="text-xs font-medium text-muted-foreground">{sectionName}</p>
                    {grouped.get(sectionName)!.map((f, i) => <TimelineFindingCard key={i} finding={f} />)}
                  </div>
                ))
              })()}
            </Block>
          )}

          {/* Bounded patterns */}
          {(brief.bounded_patterns?.length ?? 0) > 0 && (
            <Block label="What This Means">
              <ul className="space-y-1">
                {brief.bounded_patterns!.map((p, i) => (
                  <li key={i} className="text-sm">
                    <strong>{categoryLabel(p.pattern_category, isCrossDomain ? 'cross_domain' : (briefProfile?.domain ?? ''))}</strong>
                    {' '}({p.finding_count}){p.note ? ` — ${p.note}` : ''}
                  </li>
                ))}
              </ul>
            </Block>
          )}

          {/* Domain profile */}
          {briefProfile && (
            <Block label="Domain Profile">
              <p className="text-sm">
                {briefProfile.expert_mode ? `${domainLabel(briefProfile.domain)} expert brief profile active.` : `${domainLabel(briefProfile.domain)} generic brief profile active.`}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {titleFromToken(briefProfile.profile)} (v{briefProfile.profile_version}) · {titleFromToken(briefProfile.strategy)} (v{briefProfile.strategy_version})
              </p>
              {(briefProfile.finding_categories?.length ?? 0) > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {briefProfile.finding_categories!.map((c) => (
                    <span key={c} className="text-xs bg-secondary text-muted-foreground px-2 py-0.5 rounded">
                      {categoryLabel(c, briefProfile.domain)}
                    </span>
                  ))}
                </div>
              )}
              {isExpert && (DOMAIN_REFINE_HINTS[briefProfile.domain.toLowerCase()] ?? []).length > 0 && (
                <ul className="mt-2 space-y-0.5">
                  {DOMAIN_REFINE_HINTS[briefProfile.domain.toLowerCase()].map((h, i) => (
                    <li key={i} className="text-xs text-muted-foreground">· {h}</li>
                  ))}
                </ul>
              )}
            </Block>
          )}

          {/* Evidence / findings */}
          <Block label="Evidence">
            {!nonTemporalFindings.length ? (
              <p className="text-xs text-muted-foreground">
                {temporalFindings.length ? 'No additional non-temporal findings.' : 'No findings generated for this scope.'}
              </p>
            ) : isExpert || isCrossDomain ? (
              (() => {
                const grouped = new Map<string, BriefFinding[]>()
                nonTemporalFindings.forEach((f) => {
                  const k = f.finding_category ?? 'uncategorized'
                  if (!grouped.has(k)) grouped.set(k, [])
                  grouped.get(k)!.push(f)
                })
                const preferred = briefProfile?.finding_categories ?? []
                const ordered = [
                  ...preferred.filter((k) => grouped.has(k)),
                  ...Array.from(grouped.keys()).filter((k) => !preferred.includes(k)).sort(),
                ]
                return ordered.map((cat) => (
                  <div key={cat} className="space-y-2 mt-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-muted-foreground">{categoryLabel(cat, categoryDomain)}</span>
                      <span className="text-xs bg-secondary text-muted-foreground px-1.5 py-0.5 rounded">{grouped.get(cat)!.length}</span>
                    </div>
                    {grouped.get(cat)!.map((f, i) => <FindingCard key={i} finding={f} domain={categoryDomain} />)}
                  </div>
                ))
              })()
            ) : (
              <div className="space-y-2">
                {nonTemporalFindings.map((f, i) => <FindingCard key={i} finding={f} domain={categoryDomain} />)}
              </div>
            )}
          </Block>

          {/* Limitations */}
          <Block label="Deduplicated Limitations">
            <p className="text-xs text-muted-foreground italic mb-2">{brief.uncertainty_note || 'No uncertainty note provided.'}</p>
            {prodMeta && Number.isFinite(prodMeta.limitation_count_before) && (
              <p className="text-xs text-muted-foreground mb-2">
                {prodMeta.limitation_count_after} active limitation{prodMeta.limitation_count_after === 1 ? '' : 's'} retained from {prodMeta.limitation_count_before}.
                {(prodMeta.limitation_redundancy_removed ?? 0) > 0 && ` · ${prodMeta.limitation_redundancy_removed} repeated limit${prodMeta.limitation_redundancy_removed === 1 ? '' : 's'} consolidated`}
              </p>
            )}
            {!brief.limits?.length ? (
              <p className="text-xs text-muted-foreground">No explicit limits reported.</p>
            ) : (
              <ul className="space-y-0.5">
                {brief.limits.map((l, i) => <li key={i} className="text-xs text-muted-foreground">· {l}</li>)}
              </ul>
            )}
          </Block>

          {/* Quality */}
          {qualityMeta && (
            <Block label="Quality & Coverage">
              <p className="text-sm">{qualityMeta.findings_with_evidence} of {qualityMeta.findings_total} findings include evidence references.</p>
              <p className="text-xs text-muted-foreground">Evidence coverage: {coveragePercent(qualityMeta.evidence_coverage_ratio)}</p>
              {(qualityMeta.structure_gaps?.length ?? 0) > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-muted-foreground">Structure gaps</p>
                  <ul className="space-y-0.5 mt-1">
                    {qualityMeta.structure_gaps!.map((g, i) => <li key={i} className="text-xs text-muted-foreground">· {g.replace(/_/g, ' ')}</li>)}
                  </ul>
                </div>
              )}
              {(qualityMeta.sparse_domains?.length ?? 0) > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-muted-foreground">Sparse domains</p>
                  <ul className="space-y-0.5 mt-1">
                    {qualityMeta.sparse_domains!.map((d, i) => <li key={i} className="text-xs text-muted-foreground">· {domainLabel(d)}</li>)}
                  </ul>
                </div>
              )}
              {(qualityMeta.refine_guidance?.length ?? 0) > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-muted-foreground">Refine guidance</p>
                  <ul className="space-y-0.5 mt-1">
                    {qualityMeta.refine_guidance!.map((g, i) => <li key={i} className="text-xs text-muted-foreground">· {g}</li>)}
                  </ul>
                </div>
              )}
            </Block>
          )}

          {/* Refine guidance */}
          {(brief.refine_guidance?.length ?? 0) > 0 && (
            <Block label="Refine Guidance">
              <ul className="space-y-0.5">
                {brief.refine_guidance!.map((g, i) => <li key={i} className="text-xs text-muted-foreground">· {g}</li>)}
              </ul>
            </Block>
          )}

          {/* Context */}
          <Block label="Context (not evidence)">
            {brief.context_non_evidence ? (
              <>
                <p className="text-sm">{brief.context_non_evidence.text || 'No user context provided.'}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {brief.context_non_evidence.note || 'User context is framing only and not treated as factual evidence.'}
                </p>
              </>
            ) : (
              <p className="text-xs text-muted-foreground">No user context provided.</p>
            )}
          </Block>

          {/* Next questions */}
          <Block label="Next Questions">
            <ul className="space-y-0.5">
              {nextQuestions.map((q, i) => <li key={i} className="text-xs text-muted-foreground">· {q}</li>)}
            </ul>
          </Block>
        </section>
      )}
    </div>
  )
}

// ── Block layout helper ───────────────────────────────────────────────────────

function Block({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{label}</p>
      {children}
    </div>
  )
}
