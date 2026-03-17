'use client'

import { useEffect, useReducer } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { CreateInquiryInput, Inquiry } from '@/lib/api/inquiries'
import {
  DOMAIN_CATALOG, CROSS_DOMAIN_PAIR_CATALOG,
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

// ── Props ─────────────────────────────────────────────────────────────────────

interface InquiryFormProps {
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

  // Hydrate form when refine target changes
  useEffect(() => {
    if (refineTarget) {
      dispatch({ type: 'HYDRATE', from: refineTarget })
    }
  }, [refineTarget])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const { question, primaryDomain, crossDomain, pairKey, start, end, asOf, contextText } = form

    // Validation
    if (question.trim().length < 3) return alert('Enter a clear question (minimum 3 characters).')
    if (!primaryDomain && !crossDomain) return alert('Select a primary domain.')
    if (!start || !end) return alert('Select a valid timeframe.')
    if (start > end) return alert('Timeframe start must be before end.')
    if (crossDomain && !pairKey) return alert('Select an approved cross-domain pair profile.')

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

  const generateDisabled =
    isSubmitting || (alphaEnabled && !readinessReady)

  return (
    <div className="bg-card rounded-xl border border-border p-5 space-y-4">
      <div>
        <h3 className="font-semibold text-foreground">Inquiry Setup</h3>
        <p className="text-sm text-muted-foreground mt-0.5">
          Define scope first. Generate only when the question and domain lens are explicit.
        </p>
      </div>

      {statusMessage?.text && (
        <div className={`text-sm px-3 py-2 rounded-md ${
          statusMessage.tone === 'error' ? 'bg-destructive/10 text-destructive'
            : statusMessage.tone === 'success' ? 'bg-green-50 text-green-800'
            : statusMessage.tone === 'warning' ? 'bg-amber-50 text-amber-800'
            : 'bg-secondary text-foreground'
        }`}>
          {statusMessage.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4" autoComplete="off">
        {/* Question */}
        <div className="space-y-1.5">
          <Label htmlFor="inq-question">Question</Label>
          <textarea
            id="inq-question"
            rows={3}
            maxLength={500}
            required
            placeholder="What exactly am I trying to understand right now?"
            value={form.question}
            onChange={(e) => dispatch({ type: 'SET', field: 'question', value: e.target.value })}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <p className="text-xs text-muted-foreground text-right">{form.question.length}/500</p>
        </div>

        {/* Domain + Timeframe preset */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="inq-domain">Primary domain</Label>
            <select
              id="inq-domain"
              required={!form.crossDomain}
              disabled={form.crossDomain}
              value={form.primaryDomain}
              onChange={(e) => dispatch({ type: 'SET', field: 'primaryDomain', value: e.target.value })}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
            >
              <option value="">Select domain…</option>
              {domains.map((d) => (
                <option key={d.key} value={d.key}>{d.label}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="inq-preset">Timeframe</Label>
            <select
              id="inq-preset"
              value={form.timeframePreset}
              onChange={(e) => dispatch({ type: 'SET_PRESET', preset: e.target.value as FormState['timeframePreset'] })}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="custom">Custom range</option>
            </select>
          </div>
        </div>

        {/* Date range */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <Label htmlFor="inq-start">Start date</Label>
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
          <div className="space-y-1.5">
            <Label htmlFor="inq-end">End date</Label>
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
        <div className="space-y-1.5">
          <Label htmlFor="inq-asof">As of <span className="text-muted-foreground font-normal">(optional)</span></Label>
          <Input
            id="inq-asof"
            type="datetime-local"
            value={form.asOf}
            onChange={(e) => dispatch({ type: 'SET', field: 'asOf', value: e.target.value })}
          />
          <p className="text-xs text-muted-foreground">Locks replay to a deterministic cutoff time.</p>
        </div>

        {/* Cross-domain */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.crossDomain}
              onChange={(e) => {
                dispatch({ type: 'SET', field: 'crossDomain', value: e.target.checked })
                if (e.target.checked && crossDomainPairs.length) {
                  dispatch({ type: 'SET_PAIR', pairKey: crossDomainPairs[0].key, pairs: crossDomainPairs })
                }
              }}
              className="rounded border-input"
            />
            <span className="text-sm">Enable explicit cross-domain mode</span>
          </label>
          <p className="text-xs text-muted-foreground">
            Cross-domain claims are generated only when selected domains are explicit and evidence-backed.
          </p>
        </div>

        {/* Pair selector */}
        {form.crossDomain && crossDomainPairs.length > 0 && (
          <div className="space-y-1.5 pl-4 border-l-2 border-primary/20">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Approved domain pair profile</p>
            <Label htmlFor="inq-pair">Domain pair</Label>
            <select
              id="inq-pair"
              value={form.pairKey}
              onChange={(e) => dispatch({ type: 'SET_PAIR', pairKey: e.target.value, pairs: crossDomainPairs })}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="">Select approved pair…</option>
              {crossDomainPairs.map((p) => (
                <option key={p.key} value={p.key}>
                  {pairLabel(p.domains)} ({p.profile})
                </option>
              ))}
            </select>
            <p className="text-xs text-muted-foreground">
              Cross-domain pair profiles activate only for approved 2-domain scopes.
            </p>
          </div>
        )}

        {/* Context toggle */}
        <div>
          <button
            type="button"
            onClick={() => dispatch({ type: 'SET', field: 'showContext', value: !form.showContext })}
            className="text-sm text-primary hover:underline"
          >
            {form.showContext ? 'Hide optional context' : 'Add optional context'}
          </button>
        </div>

        {form.showContext && (
          <div className="space-y-1.5">
            <Label htmlFor="inq-context">Context <span className="text-muted-foreground font-normal">(not evidence)</span></Label>
            <textarea
              id="inq-context"
              rows={3}
              maxLength={1000}
              placeholder="Optional framing context. This is not treated as factual evidence."
              value={form.contextText}
              onChange={(e) => dispatch({ type: 'SET', field: 'contextText', value: e.target.value })}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <p className="text-xs text-muted-foreground">
              User context is displayed separately and not promoted to system evidence.
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3 pt-1">
          <Button type="submit" disabled={generateDisabled}>
            {isSubmitting
              ? refineTarget ? 'Refining…' : 'Generating…'
              : refineTarget ? 'Refine Brief' : 'Generate Brief'}
          </Button>
          <button
            type="button"
            onClick={handleReset}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Reset setup
          </button>
          {refineTarget && (
            <span className="text-xs text-amber-700 bg-amber-50 px-2 py-1 rounded">
              Refining selected inquiry
            </span>
          )}
        </div>
      </form>
    </div>
  )
}
