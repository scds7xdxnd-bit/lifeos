'use client'

import { useEffect, useReducer } from 'react'
import { Input } from '@/components/ui/input'
import type { CreateInquiryInput, Inquiry } from '@/lib/api/inquiries'
import type { InquiryPageTranslations } from '@/lib/translations/inquiry'
import {
  CROSS_DOMAIN_PAIR_CATALOG,
  todayIso, shiftDateIso, datetimeLocalNow, pairLabel,
} from './helpers'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface DomainOption { key: string; label: string }
export interface CrossDomainPair { key: string; profile: string; domains: string[] }

interface FormState {
  question: string
  primaryDomain: string
  timeframePreset: '7' | '30' | '90' | 'custom'
  start: string
  end: string
  asOf: string
  crossDomain: boolean
  pairKey: string
  showContext: boolean
  contextText: string
}

type FormAction =
  | { type: 'SET'; field: keyof FormState; value: string | boolean }
  | { type: 'SET_PRESET'; preset: '7' | '30' | '90' | 'custom' }
  | { type: 'RESET'; defaultStart: string; defaultEnd: string }
  | { type: 'HYDRATE'; from: Inquiry }
  | { type: 'SET_PAIR'; pairKey: string; pairs: CrossDomainPair[] }

function initForm(defaultStart: string, defaultEnd: string): FormState {
  return {
    question: '',
    primaryDomain: '',
    timeframePreset: '30',
    start: defaultStart,
    end: defaultEnd,
    asOf: datetimeLocalNow(),
    crossDomain: false,
    pairKey: '',
    showContext: false,
    contextText: '',
  }
}

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case 'SET':
      return { ...state, [action.field]: action.value }
    case 'SET_PRESET': {
      if (action.preset === 'custom') return { ...state, timeframePreset: 'custom' }
      const days = Number(action.preset)
      return { ...state, timeframePreset: action.preset, end: todayIso(), start: shiftDateIso(days - 1) }
    }
    case 'RESET':
      return initForm(action.defaultStart, action.defaultEnd)
    case 'HYDRATE': {
      const inq = action.from
      const isCross = inq.lens === 'cross_domain' || (inq.domains?.length ?? 0) > 1
      const matchedPair = isCross
        ? CROSS_DOMAIN_PAIR_CATALOG.find((p) => {
            const key = [...(inq.domains ?? [])].sort().join('__')
            return p.key === key
          })
        : undefined
      const ctxText = inq.context_non_evidence?.text ?? ''
      return {
        question: inq.question ?? '',
        primaryDomain: inq.domain ?? inq.domains?.[0] ?? '',
        timeframePreset: 'custom',
        start: inq.timeframe?.start ?? '',
        end: inq.timeframe?.end ?? '',
        asOf: inq.as_of_ts ? (() => {
          const dt = new Date(inq.as_of_ts!)
          return isNaN(dt.getTime()) ? datetimeLocalNow() :
            `${dt.getFullYear()}-${String(dt.getMonth()+1).padStart(2,'0')}-${String(dt.getDate()).padStart(2,'0')}T${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
        })() : datetimeLocalNow(),
        crossDomain: isCross,
        pairKey: matchedPair?.key ?? '',
        showContext: Boolean(ctxText),
        contextText: ctxText,
      }
    }
    case 'SET_PAIR': {
      const pair = action.pairs.find((p) => p.key === action.pairKey)
      return {
        ...state,
        pairKey: action.pairKey,
        primaryDomain: pair?.domains[0] ?? state.primaryDomain,
      }
    }
    default:
      return state
  }
}

// ── Shared styles ─────────────────────────────────────────────────────────────

const microLabel: React.CSSProperties = {
  fontFamily: 'var(--font-manrope), sans-serif',
  fontSize: '0.6875rem',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: '#767d72',
}

const inputStyle: React.CSSProperties = {
  fontFamily: 'var(--font-manrope), sans-serif',
  fontSize: '0.875rem',
  color: '#2e342b',
  background: '#ffffff',
  border: '1px solid rgba(173, 180, 168, 0.20)',
  borderRadius: '4px',
  padding: '10px 14px',
  outline: 'none',
  width: '100%',
  transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
}

// ── Props ─────────────────────────────────────────────────────────────────────

interface InquiryFormProps {
  t: InquiryPageTranslations['form']
  domains: DomainOption[]
  crossDomainPairs: CrossDomainPair[]
  readinessReady: boolean
  alphaEnabled: boolean
  refineTarget: Inquiry | null
  isSubmitting: boolean
  statusMessage: { text: string; tone: 'error' | 'success' | 'warning' | '' } | null
  onSubmit: (payload: CreateInquiryInput, refineId: number | null) => void
  onReset: () => void
}

// ── Component ─────────────────────────────────────────────────────────────────

export function InquiryForm({
  t,
  domains,
  crossDomainPairs,
  readinessReady,
  alphaEnabled,
  refineTarget,
  isSubmitting,
  statusMessage,
  onSubmit,
  onReset,
}: InquiryFormProps) {
  const defaultStart = shiftDateIso(29)
  const defaultEnd = todayIso()

  const [form, dispatch] = useReducer(formReducer, initForm(defaultStart, defaultEnd))

  useEffect(() => {
    if (refineTarget) {
      dispatch({ type: 'HYDRATE', from: refineTarget })
    }
  }, [refineTarget])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const { question, primaryDomain, crossDomain, pairKey, start, end, asOf, contextText } = form

    if (question.trim().length < 3) return alert(t.alertQuestion)
    if (!primaryDomain && !crossDomain) return alert(t.alertPrimaryDomain)
    if (!start || !end) return alert(t.alertTimeframe)
    if (start > end) return alert(t.alertStartBeforeEnd)
    if (crossDomain && !pairKey) return alert(t.alertSelectPair)

    const pair = crossDomain ? crossDomainPairs.find((p) => p.key === pairKey) : null
    const resolvedDomains = pair ? [...pair.domains] : [primaryDomain]
    const resolvedPrimary = pair ? pair.domains[0] : primaryDomain

    const payload: CreateInquiryInput = {
      question: question.trim(),
      domain: resolvedPrimary,
      domains: resolvedDomains,
      cross_domain: crossDomain,
      timeframe_start: start,
      timeframe_end: end,
    }

    if (asOf) {
      const dt = new Date(asOf)
      if (!isNaN(dt.getTime())) payload.as_of_ts = dt.toISOString()
    }
    if (contextText.trim()) payload.context_text = contextText.trim()

    onSubmit(payload, refineTarget?.id ?? null)
  }

  const handleReset = () => {
    dispatch({ type: 'RESET', defaultStart, defaultEnd })
    onReset()
  }

  const generateDisabled = isSubmitting || (alphaEnabled && !readinessReady)

  return (
    <div
      className="p-5 sm:p-7 space-y-6"
      style={{
        background: '#ffffff',
        borderRadius: '0 16px 16px 16px',
        boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
      }}
    >
      {/* Card header */}
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
          {t.setupTitle}
        </h3>
        <p
          className="mt-1"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.8125rem',
            color: '#767d72',
            lineHeight: 1.65,
          }}
        >
          {t.setupSub}
        </p>
      </div>

      {/* Status message */}
      {statusMessage?.text && (
        <div
          className="px-4 py-3"
          style={{
            borderRadius: '0 12px 12px 12px',
            fontSize: '0.8125rem',
            fontFamily: 'var(--font-manrope), sans-serif',
            ...(statusMessage.tone === 'error' ? {
              background: 'rgba(232, 115, 92, 0.08)',
              color: '#8b4a3a',
            } : statusMessage.tone === 'success' ? {
              background: 'rgba(75, 102, 70, 0.08)',
              color: '#3a5c35',
            } : statusMessage.tone === 'warning' ? {
              background: 'rgba(107, 90, 53, 0.08)',
              color: '#6b5a35',
            } : {
              background: '#f1f5eb',
              color: '#5a6157',
            }),
          }}
        >
          {statusMessage.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5" autoComplete="off">
        {/* Question */}
        <div className="space-y-2">
          <label htmlFor="inq-question" style={microLabel}>{t.question}</label>
          <textarea
            id="inq-question"
            rows={3}
            maxLength={500}
            required
            placeholder={t.questionPlaceholder}
            value={form.question}
            onChange={(e) => dispatch({ type: 'SET', field: 'question', value: e.target.value })}
            style={{
              ...inputStyle,
              resize: 'none',
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = '#4b6646'
              e.currentTarget.style.boxShadow = '0 0 0 2px rgba(75, 102, 70, 0.15)'
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'rgba(173, 180, 168, 0.20)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          />
          <p style={{ ...microLabel, fontWeight: 400, textAlign: 'right' as const }}>{form.question.length}/500</p>
        </div>

        {/* Domain + Timeframe preset */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="inq-domain" style={microLabel}>{t.primaryDomain}</label>
            <select
              id="inq-domain"
              required={!form.crossDomain}
              disabled={form.crossDomain}
              value={form.primaryDomain}
              onChange={(e) => dispatch({ type: 'SET', field: 'primaryDomain', value: e.target.value })}
              style={{
                ...inputStyle,
                ...(form.crossDomain ? { opacity: 0.5 } : {}),
              }}
            >
              <option value="">{t.selectDomain}</option>
              {domains.map((d) => (
                <option key={d.key} value={d.key}>{d.label}</option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label htmlFor="inq-preset" style={microLabel}>{t.timeframe}</label>
            <select
              id="inq-preset"
              value={form.timeframePreset}
              onChange={(e) => dispatch({ type: 'SET_PRESET', preset: e.target.value as FormState['timeframePreset'] })}
              style={inputStyle}
            >
              <option value="7">{t.last7Days}</option>
              <option value="30">{t.last30Days}</option>
              <option value="90">{t.last90Days}</option>
              <option value="custom">{t.customRange}</option>
            </select>
          </div>
        </div>

        {/* Date range */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="inq-start" style={microLabel}>{t.startDate}</label>
            <Input
              id="inq-start"
              type="date"
              required
              value={form.start}
              onChange={(e) => {
                dispatch({ type: 'SET', field: 'start', value: e.target.value })
                dispatch({ type: 'SET', field: 'timeframePreset', value: 'custom' })
              }}
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="inq-end" style={microLabel}>{t.endDate}</label>
            <Input
              id="inq-end"
              type="date"
              required
              value={form.end}
              onChange={(e) => {
                dispatch({ type: 'SET', field: 'end', value: e.target.value })
                dispatch({ type: 'SET', field: 'timeframePreset', value: 'custom' })
              }}
            />
          </div>
        </div>

        {/* As-of */}
        <div className="space-y-2">
          <label htmlFor="inq-asof" style={microLabel}>
            {t.asOf} <span style={{ fontWeight: 400, textTransform: 'none', letterSpacing: 'normal' }}>{t.optional}</span>
          </label>
          <Input
            id="inq-asof"
            type="datetime-local"
            value={form.asOf}
            onChange={(e) => dispatch({ type: 'SET', field: 'asOf', value: e.target.value })}
          />
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
            {t.asOfHint}
          </p>
        </div>

        {/* Cross-domain */}
        <div className="space-y-2">
          <label className="flex items-center gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              checked={form.crossDomain}
              onChange={(e) => {
                dispatch({ type: 'SET', field: 'crossDomain', value: e.target.checked })
                if (e.target.checked && crossDomainPairs.length) {
                  dispatch({ type: 'SET_PAIR', pairKey: crossDomainPairs[0].key, pairs: crossDomainPairs })
                }
              }}
              className="rounded"
              style={{ accentColor: '#4b6646' }}
            />
            <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#2e342b' }}>
              {t.crossDomainMode}
            </span>
          </label>
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
            {t.crossDomainHint}
          </p>
        </div>

        {/* Pair selector */}
        {form.crossDomain && crossDomainPairs.length > 0 && (
          <div
            className="space-y-3 pl-5"
            style={{ borderLeft: '2px solid rgba(75, 102, 70, 0.15)' }}
          >
            <p style={microLabel}>{t.approvedPairProfile}</p>
            <label htmlFor="inq-pair" style={microLabel}>{t.domainPair}</label>
            <select
              id="inq-pair"
              value={form.pairKey}
              onChange={(e) => dispatch({ type: 'SET_PAIR', pairKey: e.target.value, pairs: crossDomainPairs })}
              style={inputStyle}
            >
              <option value="">{t.selectApprovedPair}</option>
              {crossDomainPairs.map((p) => (
                <option key={p.key} value={p.key}>
                  {pairLabel(p.domains)} ({p.profile})
                </option>
              ))}
            </select>
            <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
              {t.pairHint}
            </p>
          </div>
        )}

        {/* Context toggle */}
        <div>
          <button
            type="button"
            onClick={() => dispatch({ type: 'SET', field: 'showContext', value: !form.showContext })}
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.8125rem',
              color: '#767d72',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              textDecoration: 'underline',
              textUnderlineOffset: '3px',
              transition: 'color 0.2s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = '#4b6646' }}
            onMouseLeave={(e) => { e.currentTarget.style.color = '#767d72' }}
          >
            {form.showContext ? t.hideOptionalContext : t.addOptionalContext}
          </button>
        </div>

        {form.showContext && (
          <div className="space-y-2">
            <label htmlFor="inq-context" style={microLabel}>
              {t.context} <span style={{ fontWeight: 400, textTransform: 'none', letterSpacing: 'normal' }}>{t.notEvidence}</span>
            </label>
            <textarea
              id="inq-context"
              rows={3}
              maxLength={1000}
              placeholder={t.contextPlaceholder}
              value={form.contextText}
              onChange={(e) => dispatch({ type: 'SET', field: 'contextText', value: e.target.value })}
              style={{ ...inputStyle, resize: 'none' }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = '#4b6646'
                e.currentTarget.style.boxShadow = '0 0 0 2px rgba(75, 102, 70, 0.15)'
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'rgba(173, 180, 168, 0.20)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            />
            <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
              {t.contextHint}
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-4 pt-2">
          <button
            type="submit"
            disabled={generateDisabled}
            className="btn-pill"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontWeight: 700,
              fontSize: '0.875rem',
              color: '#ffffff',
              background: generateDisabled
                ? '#adb4a8'
                : 'linear-gradient(135deg, #4b6646, #3f5a3a)',
              borderRadius: '100px',
              padding: '12px 28px',
              border: 'none',
              cursor: generateDisabled ? 'not-allowed' : 'pointer',
              boxShadow: generateDisabled ? 'none' : '0 4px 20px rgba(46, 52, 43, 0.18)',
              transition: 'all 0.18s ease',
            }}
          >
            {isSubmitting
              ? refineTarget ? t.refining : t.generating
              : refineTarget ? t.refineBrief : t.generateBrief}
          </button>
          <button
            type="button"
            onClick={handleReset}
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontWeight: 700,
              fontSize: '0.6875rem',
              textTransform: 'uppercase' as const,
              letterSpacing: '0.05em',
              color: '#767d72',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              transition: 'color 0.2s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = '#5a6157' }}
            onMouseLeave={(e) => { e.currentTarget.style.color = '#767d72' }}
          >
            {t.reset}
          </button>
          {refineTarget && (
            <span
              className="px-3 py-1"
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.6875rem',
                fontWeight: 700,
                textTransform: 'uppercase' as const,
                letterSpacing: '0.05em',
                color: '#6b5a35',
                background: '#f5f0e4',
                borderRadius: '100px',
              }}
            >
              {t.refiningSelectedInquiry}
            </span>
          )}
        </div>
      </form>
    </div>
  )
}
