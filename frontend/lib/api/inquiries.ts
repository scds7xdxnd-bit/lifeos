import { apiGet, apiPost } from './client'

// ── Evidence ─────────────────────────────────────────────────────────────────

export interface EvidenceRef {
  domain: string
  source_id?: string
  source_ref?: string
  source_kind?: string
  event_type?: string
  insight_type?: string
  created_at?: string
  event_count?: number
  insight_count?: number
}

// ── Findings ─────────────────────────────────────────────────────────────────

export interface BriefFinding {
  claim: string
  confidence_label: string
  uncertainty_note: string
  evidence_refs: EvidenceRef[]
  finding_category?: string
  relevance_rank?: number
  relevance_reason?: string
  source_domains?: string[]
  timeline_context?: {
    claim_type: string
    active_window_label: string
    comparison_label: string
    coverage_status: string
  }
}

// ── Brief sub-objects ─────────────────────────────────────────────────────────

export interface BriefProfile {
  domain: string
  profile: string
  profile_version: string
  strategy: string
  strategy_version: string
  expert_mode: boolean
  finding_categories?: string[]
}

export interface Answerability {
  classification: string
  reason: string
  evidence_coverage_ratio?: number
  supporting_finding_count?: number
}

export interface DirectAnswer {
  text: string
  note?: string
  supporting_claims?: string[]
}

export interface QualityMetadata {
  findings_total: number
  findings_with_evidence: number
  evidence_coverage_ratio: number
  structure_gaps?: string[]
  sparse_domains?: string[]
  refine_guidance?: string[]
}

export interface TimelineMetadata {
  timeline_profile_id: string
  timeline_profile_version: string
  timezone_token: string
  window_spec_token: string
  baseline_policy_token: string
  insufficiency_count?: number
  comparison_coverage?: {
    prior_window_available: boolean
    baseline_windows_available: number
    baseline_windows_required: number
    recurrence_windows_available: number
    trend_windows_available: number
  }
}

export interface HumanizedBlock {
  text: string
  confidence_label?: string
  source_finding_ids?: string[]
  source_limitation_ids?: string[]
  evidence_refs?: EvidenceRef[]
}

export interface HumanizedBriefSection {
  title?: string
  section_id?: string
  blocks: HumanizedBlock[]
}

export interface HumanizedBrief {
  answer: {
    text: string
    source_finding_ids?: string[]
    source_limitation_ids?: string[]
  }
  sections: HumanizedBriefSection[]
  metadata?: { technical_view_available?: boolean }
}

// ── Full brief data ───────────────────────────────────────────────────────────

export interface BriefData {
  summary: string
  lens: string
  domains: string[]
  timeframe: { start: string; end: string }
  as_of_ts?: string
  findings: BriefFinding[]
  limits: string[]
  uncertainty_note?: string
  direct_answer?: DirectAnswer
  answerability?: Answerability
  bounded_patterns?: { pattern_category: string; finding_count: number; note?: string }[]
  brief_profile?: BriefProfile
  quality_metadata?: QualityMetadata
  timeline_metadata?: TimelineMetadata
  productization_metadata?: {
    limitation_count_before?: number
    limitation_count_after?: number
    limitation_redundancy_removed?: number
  }
  refine_guidance?: string[]
  context_non_evidence?: { label?: string; text?: string; note?: string }
  humanized_brief?: HumanizedBrief
}

// ── Inquiry + version ─────────────────────────────────────────────────────────

export interface InquiryVersion {
  id: number
  version_number: number
  brief: BriefData
}

export interface Inquiry {
  id: number
  question: string
  domain: string
  domains: string[]
  lens?: string
  timeframe: { start: string; end: string }
  as_of_ts?: string
  last_version_number: number
  created_at: string
  updated_at?: string
  context_non_evidence?: { text?: string }
  versions?: InquiryVersion[]
  latest_brief?: InquiryVersion
}

// ── API response types ────────────────────────────────────────────────────────

export interface InquiryResult {
  ok: boolean
  inquiry_id?: number
  version_id?: number
  version_number?: number
  deduped?: boolean
  inquiry?: Inquiry
  brief?: BriefData
  latest_brief?: InquiryVersion
}

export interface InquiryDetailResult {
  ok: boolean
  inquiry: Inquiry
}

export interface ReadinessResult {
  ok: boolean
  readiness: {
    ready: boolean
    ready_domains: string[]
    domain_event_counts: Record<string, number>
    next_step: string
  }
  alpha: {
    enabled: boolean
    visible_domains: string[]
    enabled_pair_profiles: string[]
  }
}

// ── Input types ───────────────────────────────────────────────────────────────

export interface CreateInquiryInput {
  question: string
  domain: string
  domains: string[]
  cross_domain: boolean
  timeframe_start: string
  timeframe_end: string
  as_of_ts?: string
  context_text?: string
}

// ── API functions ─────────────────────────────────────────────────────────────

export const inquiriesApi = {
  create: (input: CreateInquiryInput) =>
    apiPost<InquiryResult>('/api/v1/inquiries', input),

  refine: (id: number, input: CreateInquiryInput) =>
    apiPost<InquiryResult>(`/api/v1/inquiries/${id}/refine`, input),

  list: (limit = 20, offset = 0) =>
    apiGet<{ ok: boolean; items: Inquiry[] }>(
      `/api/v1/inquiries?limit=${limit}&offset=${offset}`,
    ),

  get: (id: number) =>
    apiGet<InquiryDetailResult>(`/api/v1/inquiries/${id}`),

  readiness: () =>
    apiGet<ReadinessResult>('/api/v1/inquiries/readiness'),

  feedback: (id: number, versionId: number, feedbackType: string, surface: string, note?: string) =>
    apiPost<{ ok: boolean; deduped?: boolean }>(`/api/v1/inquiries/${id}/feedback`, {
      version_id: versionId,
      feedback_type: feedbackType,
      surface,
      note: note || null,
    }),
}
