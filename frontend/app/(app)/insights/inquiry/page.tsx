'use client'

import { useState, useCallback, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { inquiriesApi } from '@/lib/api/inquiries'
import type {
  Inquiry, CreateInquiryInput, InquiryVersion,
} from '@/lib/api/inquiries'
import { InquiryForm } from './_components/InquiryForm'
import { InquiryBrief } from './_components/InquiryBrief'
import { InquiryHistory } from './_components/InquiryHistory'
import {
  DOMAIN_CATALOG, CROSS_DOMAIN_PAIR_CATALOG, parseApiError,
} from './_components/helpers'

// ── Types ──────────────────────────────────────────────────────────────────────

type StatusMessage = { text: string; tone: 'error' | 'success' | 'warning' | '' } | null

// ── Page ───────────────────────────────────────────────────────────────────────

export default function InquiryPage() {
  const queryClient = useQueryClient()
  const searchParams = useSearchParams()

  // ── State ──────────────────────────────────────────────────────────────────

  const [refineTarget, setRefineTarget] = useState<Inquiry | null>(null)
  const [selectedInquiry, setSelectedInquiry] = useState<Inquiry | null>(null)
  const [selectedVersionId, setSelectedVersionId] = useState<number | null>(null)
  const [statusMessage, setStatusMessage] = useState<StatusMessage>(null)
  const [feedbackStatus, setFeedbackStatus] = useState<{ text: string; tone: string } | null>(null)

  // ── Load inquiry from ?inquiry_id= param (linked from history page) ────────

  useEffect(() => {
    const id = searchParams.get('inquiry_id')
    if (!id) return
    const numId = Number(id)
    if (!numId) return
    inquiriesApi.get(numId).then((result) => {
      if (result.ok) {
        setSelectedInquiry(result.inquiry)
        setSelectedVersionId(result.inquiry.latest_brief?.id ?? null)
      }
    })
  }, [searchParams])

  // ── Readiness ──────────────────────────────────────────────────────────────

  const { data: readinessData } = useQuery({
    queryKey: ['readiness'],
    queryFn: () => inquiriesApi.readiness(),
    staleTime: 1000 * 60 * 2,
  })

  const alphaEnabled = readinessData?.alpha?.enabled ?? false
  const readinessReady = readinessData?.readiness?.ready ?? false
  const visibleDomains = readinessData?.alpha?.visible_domains ?? []
  const enabledPairProfiles = readinessData?.alpha?.enabled_pair_profiles ?? []
  const alphaFeedbackEnabled = alphaEnabled

  // Filter catalogs based on alpha scope when alpha is active
  const domains = alphaEnabled
    ? DOMAIN_CATALOG.filter((d) => visibleDomains.includes(d.key))
    : DOMAIN_CATALOG

  const crossDomainPairs = alphaEnabled
    ? CROSS_DOMAIN_PAIR_CATALOG.filter((p) => enabledPairProfiles.includes(p.profile))
    : CROSS_DOMAIN_PAIR_CATALOG

  // ── History ────────────────────────────────────────────────────────────────

  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['inquiries'],
    queryFn: () => inquiriesApi.list(20, 0),
    staleTime: 1000 * 30,
  })

  const historyItems = historyData?.items ?? []

  // ── Mutation ───────────────────────────────────────────────────────────────

  const mutation = useMutation({
    mutationFn: ({ payload, refineId }: { payload: CreateInquiryInput; refineId: number | null }) =>
      refineId ? inquiriesApi.refine(refineId, payload) : inquiriesApi.create(payload),

    onSuccess: async (result, { refineId }) => {
      if (!result.ok) {
        setStatusMessage({ text: 'Request failed. Please try again.', tone: 'error' })
        return
      }

      if (result.deduped) {
        setStatusMessage({ text: 'Duplicate inquiry detected — returning existing brief.', tone: 'warning' })
      } else {
        setStatusMessage({
          text: refineId ? 'Refinement complete.' : 'Brief generated.',
          tone: 'success',
        })
      }

      // Reload history
      queryClient.invalidateQueries({ queryKey: ['inquiries'] })

      // If we have the full inquiry in the response, show it
      if (result.inquiry) {
        setSelectedInquiry(result.inquiry)
        setSelectedVersionId(result.latest_brief?.id ?? result.version_id ?? null)
      } else if (result.inquiry_id) {
        const detail = await inquiriesApi.get(result.inquiry_id)
        if (detail.ok) {
          setSelectedInquiry(detail.inquiry)
          setSelectedVersionId(detail.inquiry.latest_brief?.id ?? null)
        }
      }

      setRefineTarget(null)
    },

    onError: async (err: unknown) => {
      let message = 'Request failed. Please try again.'
      if (err instanceof Response) {
        try {
          const body = await err.json()
          message = parseApiError(body, err.status)
        } catch {
          message = parseApiError({}, err.status)
        }
      } else if (err && typeof err === 'object' && 'body' in err) {
        const e = err as { body?: Record<string, unknown>; status?: number }
        message = parseApiError(e.body ?? {}, e.status)
      }
      setStatusMessage({ text: message, tone: 'error' })
    },
  })

  // ── Handlers ───────────────────────────────────────────────────────────────

  const handleSubmit = useCallback(
    (payload: CreateInquiryInput, refineId: number | null) => {
      setStatusMessage(null)
      mutation.mutate({ payload, refineId })
    },
    [mutation],
  )

  const handleReset = useCallback(() => {
    setRefineTarget(null)
    setStatusMessage(null)
  }, [])

  const handleView = useCallback((inq: Inquiry) => {
    setSelectedInquiry(inq)
    setSelectedVersionId(inq.latest_brief?.id ?? null)
    setRefineTarget(null)
    setStatusMessage(null)
    setFeedbackStatus(null)
  }, [])

  const handleRefine = useCallback((inq: Inquiry) => {
    setRefineTarget(inq)
    setStatusMessage(null)
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [])

  const handleVersionSelect = useCallback((v: InquiryVersion) => {
    setSelectedVersionId(v.id)
    setFeedbackStatus(null)
  }, [])

  const handleFeedback = useCallback(
    async (type: string, surface: string, note: string) => {
      if (!selectedInquiry || !selectedVersionId) return
      try {
        await inquiriesApi.feedback(selectedInquiry.id, selectedVersionId, type, surface, note || undefined)
        setFeedbackStatus({ text: 'Feedback recorded. Thank you.', tone: 'success' })
      } catch {
        setFeedbackStatus({ text: 'Failed to submit feedback.', tone: 'error' })
      }
    },
    [selectedInquiry, selectedVersionId],
  )

  // ── Brief resolution ───────────────────────────────────────────────────────

  const versions = selectedInquiry?.versions ?? (
    selectedInquiry?.latest_brief ? [selectedInquiry.latest_brief] : []
  )

  const activeBrief = (() => {
    if (!selectedInquiry) return null
    if (selectedVersionId) {
      const found = versions.find((v) => v.id === selectedVersionId)
      if (found) return found.brief
    }
    return selectedInquiry.latest_brief?.brief ?? null
  })()

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Inquiry</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Scope a question to a domain and timeframe. Evidence-backed briefs only.
          </p>
        </div>

        {/* Alpha readiness banner */}
        {alphaEnabled && !readinessReady && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
            Data readiness not met.{' '}
            <a href="/insights/data" className="underline hover:no-underline font-medium">
              Check Data Readiness
            </a>{' '}
            for next steps before generating a brief.
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-[2fr_3fr] gap-6 items-start">
          {/* Left column: form + history */}
          <div className="space-y-5">
            <InquiryForm
              domains={domains}
              crossDomainPairs={crossDomainPairs}
              readinessReady={readinessReady}
              alphaEnabled={alphaEnabled}
              refineTarget={refineTarget}
              isSubmitting={mutation.isPending}
              statusMessage={statusMessage}
              onSubmit={handleSubmit}
              onReset={handleReset}
            />

            <InquiryHistory
              items={historyItems}
              isLoading={historyLoading}
              selectedId={selectedInquiry?.id ?? null}
              onView={handleView}
              onRefine={handleRefine}
            />
          </div>

          {/* Right column: brief */}
          <div>
            {mutation.isPending ? (
              <div className="bg-card rounded-xl border border-border p-8 text-center">
                <div className="inline-block w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin mb-3" />
                <p className="text-sm text-muted-foreground">
                  {refineTarget ? 'Refining brief…' : 'Generating brief…'}
                </p>
              </div>
            ) : (
              <InquiryBrief
                brief={activeBrief}
                versions={versions}
                selectedVersionId={selectedVersionId}
                inquiryId={selectedInquiry?.id ?? null}
                alphaFeedbackEnabled={alphaFeedbackEnabled}
                onVersionSelect={handleVersionSelect}
                onFeedback={handleFeedback}
                feedbackStatus={feedbackStatus}
                alertMessage={statusMessage}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
