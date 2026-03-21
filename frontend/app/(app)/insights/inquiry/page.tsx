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
import { useLang } from '@/lib/useLang'
import { getInquiryTranslations } from '@/lib/translations/inquiry'
import {
  DOMAIN_CATALOG, CROSS_DOMAIN_PAIR_CATALOG, parseApiError,
} from './_components/helpers'

// ── Types ──────────────────────────────────────────────────────────────────────

type StatusMessage = { text: string; tone: 'error' | 'success' | 'warning' | '' } | null

// ── Page ───────────────────────────────────────────────────────────────────────

export default function InquiryPage() {
  const [lang] = useLang()
  const t = getInquiryTranslations(lang)
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

  // ── Legacy surfaces removed from active flow ──────────────────────────────
  const alphaEnabled = false
  const readinessReady = true
  const alphaFeedbackEnabled = false
  const domains = DOMAIN_CATALOG
  const crossDomainPairs = CROSS_DOMAIN_PAIR_CATALOG

  // ── Mutation ───────────────────────────────────────────────────────────────

  const mutation = useMutation({
    mutationFn: ({ payload, refineId }: { payload: CreateInquiryInput; refineId: number | null }) =>
      refineId ? inquiriesApi.refine(refineId, payload) : inquiriesApi.create(payload),

    onSuccess: async (result, { refineId }) => {
      if (!result.ok) {
        setStatusMessage({ text: t.requestFailed, tone: 'error' })
        return
      }

      if (result.deduped) {
        setStatusMessage({ text: t.duplicateDetected, tone: 'warning' })
      } else {
        setStatusMessage({
          text: refineId ? t.refinementComplete : t.briefGenerated,
          tone: 'success',
        })
      }

      queryClient.invalidateQueries({ queryKey: ['inquiries'] })

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
      let message = t.requestFailed
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
    <div className="space-y-8">

      {/* Page header — Botanical Editorial pattern */}
      <div>
        <p
          className="text-xs font-bold uppercase mb-2"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            letterSpacing: '0.05em',
            color: '#4b6646',
          }}
        >
            {t.eyebrow}
        </p>
        <h1
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '2rem',
            fontWeight: 300,
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          {t.title}
        </h1>
        <p
          className="mt-2"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.9375rem',
            color: '#5a6157',
            lineHeight: 1.65,
          }}
        >
          {t.subtitle}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[2fr_3fr] gap-8 items-start">
        {/* Left column: form */}
        <div className="space-y-6">
          <InquiryForm
              t={t.form}
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
          </div>

          {/* Right column: brief */}
          <div>
            {mutation.isPending ? (
              <div
                className="p-10 text-center"
                style={{
                  background: '#ffffff',
                  borderRadius: '0 16px 16px 16px',
                  boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
                }}
              >
                <div
                  className="inline-block w-8 h-8 rounded-full border-2 border-t-transparent animate-spin mb-4"
                  style={{ borderColor: '#4b6646', borderTopColor: 'transparent' }}
                />
                <p
                  style={{
                    fontFamily: 'var(--font-serif), Georgia, serif',
                    fontStyle: 'italic',
                    color: '#767d72',
                    fontSize: '0.9375rem',
                    letterSpacing: '-0.03em',
                  }}
                >
                  {refineTarget ? t.refiningBrief : t.generatingBrief}
                </p>
              </div>
            ) : (
              <InquiryBrief
                t={t.brief}
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
  )
}
