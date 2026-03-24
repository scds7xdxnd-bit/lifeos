'use client'

import { useEffect, useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient, useQueries } from '@tanstack/react-query'
import {
  skillsApi,
  type CreateSkillInput,
  type SkillForecast,
  type SkillOverviewCard,
} from '@/lib/api/skills'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import { Input } from '@/components/ui/input'
import { Plus, Clock, Play, Leaf } from 'lucide-react'

function fmtMinutes(m: number, labels: { minuteShort: string; hourShort: string }) {
  if (m < 60) return `${m}${labels.minuteShort}`
  const h = Math.floor(m / 60)
  const rem = m % 60
  return rem ? `${h}${labels.hourShort} ${rem}${labels.minuteShort}` : `${h}${labels.hourShort}`
}

function addDaysIso(dateIso: string, days: number): string {
  const base = dateIso ? new Date(dateIso) : new Date()
  if (Number.isNaN(base.getTime())) {
    const fallback = new Date()
    fallback.setDate(fallback.getDate() + days)
    return fallback.toISOString().slice(0, 10)
  }
  base.setDate(base.getDate() + days)
  return base.toISOString().slice(0, 10)
}

function fmtCompactDate(dateIso: string): string {
  const parsed = new Date(dateIso)
  if (Number.isNaN(parsed.getTime())) return dateIso
  return parsed.toISOString().slice(0, 10)
}

function formatGoalValue(
  value: number,
  goalType: 'sessions' | 'hours' | 'milestones',
  labels: { hourShort: string }
): string {
  if (!Number.isFinite(value)) return '-'
  if (goalType === 'hours') {
    return `${Number(value.toFixed(1))}${labels.hourShort}`
  }
  return `${Math.max(0, Math.round(value))}`
}

function formatGoalPace(
  value: number,
  goalType: 'sessions' | 'hours' | 'milestones',
  labels: { notEnoughDataYet: string; milestonesLabel: string; sessions: string; hourShort: string; weekShort: string }
): string {
  if (!Number.isFinite(value) || value <= 0) return labels.notEnoughDataYet
  if (goalType === 'hours') {
    return `${Number(value.toFixed(1))} ${labels.hourShort}/${labels.weekShort}`
  }
  if (goalType === 'milestones') {
    return `${Math.round(value)} ${labels.milestonesLabel}/${labels.weekShort}`
  }
  return `${Math.round(value)} ${labels.sessions}/${labels.weekShort}`
}

function buildWeeklyCadenceSlots(skill: { sessions_last_7: number; recent_sessions: Array<{ practiced_at: string }> } | null): boolean[] {
  const slots = Array.from({ length: 7 }, () => false)
  if (!skill) return slots

  const recentDateSet = new Set(
    skill.recent_sessions
      .map((session) => new Date(session.practiced_at))
      .filter((date) => !Number.isNaN(date.getTime()))
      .map((date) => date.toISOString().slice(0, 10)),
  )

  if (recentDateSet.size > 0) {
    for (let i = 0; i < 7; i += 1) {
      const day = new Date()
      day.setUTCHours(0, 0, 0, 0)
      day.setUTCDate(day.getUTCDate() - (6 - i))
      slots[i] = recentDateSet.has(day.toISOString().slice(0, 10))
    }
    return slots
  }

  const fallbackCount = Math.max(0, Math.min(7, skill.sessions_last_7 || 0))
  for (let i = 0; i < fallbackCount; i += 1) {
    slots[6 - i] = true
  }
  return slots
}

function cardNextActionNarrative(params: {
  requiresGoalSetup: boolean
  progressState: 'on_track' | 'at_risk' | 'completed'
  forecastState?: 'on_track' | 'at_risk' | 'completed' | 'insufficient_data'
  cadenceActiveDays: number
  labels: {
    setupGoalThenPractice: string
    keepEndpointStable: string
    recoverMomentum: string
    sustainRhythm: string
    focusedSession: string
  }
}): string {
  if (params.requiresGoalSetup) {
    return params.labels.setupGoalThenPractice
  }
  if (params.progressState === 'completed') {
    return params.labels.keepEndpointStable
  }
  if (params.progressState === 'at_risk' || params.forecastState === 'at_risk') {
    return params.labels.recoverMomentum
  }
  if (params.cadenceActiveDays >= 4) {
    return params.labels.sustainRhythm
  }
  return params.labels.focusedSession
}

type ForecastScenario = 'keep_pace' | 'plus_one_session' | 'plus_thirty_minutes'
type DensityMode = 'compact' | 'comfortable'
type SortMode = 'urgency' | 'momentum' | 'alphabetical'
type AttentionReason = 'stalled' | 'below_pace' | 'deadline_risk'

function applyForecastScenario(
  forecast: SkillForecast,
  scenario: ForecastScenario,
): {
  projectedMinutes: number
  projectedSessions: number
  projectedGoalProgressRatio: number | null
} {
  const baseMinutes = forecast.projection.projected_minutes_next_window
  const baseSessions = forecast.projection.projected_sessions_next_window
  const avgSessionMinutes =
    forecast.baseline.sessions_last_14 > 0
      ? forecast.baseline.total_minutes_last_14 / forecast.baseline.sessions_last_14
      : 30

  const scenarioMinutes =
    scenario === 'plus_one_session'
      ? baseMinutes + Math.round(avgSessionMinutes)
      : scenario === 'plus_thirty_minutes'
        ? baseMinutes + 30
        : baseMinutes

  const scenarioSessions =
    scenario === 'plus_one_session'
      ? baseSessions + 1
      : scenario === 'plus_thirty_minutes'
        ? baseSessions + (avgSessionMinutes > 0 ? Math.max(0, Math.round(30 / avgSessionMinutes)) : 0)
        : baseSessions

  let scenarioRatio = forecast.projection.projected_goal_progress_ratio
  if (forecast.goal && forecast.projection.projected_goal_progress_ratio !== null) {
    const current = forecast.goal.current_value
    const target = forecast.goal.target_value
    const baselineProjectedTotal = forecast.projection.projected_goal_progress_ratio * target
    const baselineIncrement = Math.max(0, baselineProjectedTotal - current)

    let factor = 1
    if (forecast.goal.goal_type === 'sessions') {
      factor = baseSessions > 0 ? scenarioSessions / baseSessions : scenario === 'plus_one_session' ? 1.2 : 1
    } else if (forecast.goal.goal_type === 'hours') {
      factor = baseMinutes > 0 ? scenarioMinutes / baseMinutes : scenario === 'plus_thirty_minutes' ? 1.2 : 1
    } else {
      factor = 1
    }

    const adjustedProjected = current + baselineIncrement * factor
    scenarioRatio = Math.max(0, Math.min(adjustedProjected / target, 3))
  }

  return {
    projectedMinutes: scenarioMinutes,
    projectedSessions: scenarioSessions,
    projectedGoalProgressRatio: scenarioRatio,
  }
}

function daysUntilIso(dateIso: string | null | undefined): number | null {
  if (!dateIso) return null
  const target = new Date(dateIso)
  if (Number.isNaN(target.getTime())) return null
  const now = new Date()
  const utcNow = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
  const utcTarget = Date.UTC(target.getUTCFullYear(), target.getUTCMonth(), target.getUTCDate())
  return Math.ceil((utcTarget - utcNow) / (1000 * 60 * 60 * 24))
}

function deriveAttentionReasons(params: {
  card: SkillOverviewCard
  forecast?: SkillForecast
  sessionsLast7: number
}): AttentionReason[] {
  const reasons: AttentionReason[] = []
  const stalled =
    params.sessionsLast7 <= 0 &&
    (params.card.session_count > 0 || params.card.risk_reason === 'no_recent_sessions' || params.forecast?.risk_reason === 'no_recent_sessions')
  const belowPace =
    !params.card.requires_goal_setup &&
    (params.card.progress_state === 'at_risk' || params.forecast?.forecast_state === 'at_risk')
  const deadlineDays = daysUntilIso(params.card.goal?.deadline)
  const deadlineRisk = deadlineDays !== null && deadlineDays >= 0 && deadlineDays <= 14 && belowPace

  if (stalled) reasons.push('stalled')
  if (belowPace) reasons.push('below_pace')
  if (deadlineRisk) reasons.push('deadline_risk')
  return reasons
}

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
}

export default function SkillsPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).skills
  const interpolate = (template: string, values: Record<string, string | number>) =>
    Object.entries(values).reduce((out, [key, value]) => out.replace(`{${key}}`, String(value)), template)

  const goalTypeOptions = [
    { value: 'sessions', label: t.sessionsLabel },
    { value: 'hours', label: t.hoursLabel },
    { value: 'milestones', label: t.milestonesLabel },
  ] as const

  const qc = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createStep, setCreateStep] = useState<1 | 2>(1)
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [goalType, setGoalType] = useState<'sessions' | 'hours' | 'milestones'>('sessions')
  const [goalTarget, setGoalTarget] = useState('')
  const [createError, setCreateError] = useState<string | null>(null)
  const [strictGoalRollout, setStrictGoalRollout] = useState(false)

  const [goalSkillId, setGoalSkillId] = useState<number | null>(null)
  const [goalEditType, setGoalEditType] = useState<'sessions' | 'hours' | 'milestones'>('sessions')
  const [goalEditTarget, setGoalEditTarget] = useState('12')
  const [goalEditDeadline, setGoalEditDeadline] = useState('')
  const [goalEditError, setGoalEditError] = useState<string | null>(null)
  const [goalEditInsight, setGoalEditInsight] = useState<{
    currentValue: number
    pacePerWeek: number
  } | null>(null)

  const [practiceSkillId, setPracticeSkillId] = useState<number | null>(null)
  const [practiceStepId, setPracticeStepId] = useState<string>('')
  const [nextActionHint, setNextActionHint] = useState<string | null>(null)
  const [duration, setDuration] = useState('30')
  const [practiceNotes, setPracticeNotes] = useState('')
  const [practiceCelebration, setPracticeCelebration] = useState<{
    minutesDelta: number
    projectedTotalMinutes: number
    sessionDelta: number
    streakDelta: number
    nextStepLabel: string | null
  } | null>(null)
  const [forecastScenarioBySkill, setForecastScenarioBySkill] = useState<Record<number, ForecastScenario>>({})
  const [insightsSkillId, setInsightsSkillId] = useState<number | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<{ id: number; name: string } | null>(null)
  const [reduceMotion, setReduceMotion] = useState(false)
  const [densityMode, setDensityMode] = useState<DensityMode>('compact')
  const [sortMode, setSortMode] = useState<SortMode>('urgency')

  const { data, isLoading } = useQuery({
    queryKey: ['skills'],
    queryFn: () => skillsApi.list(),
  })

  const { data: overviewData, isLoading: isOverviewLoading } = useQuery({
    queryKey: ['skills', 'overview'],
    queryFn: () => skillsApi.overview(),
    retry: false,
  })

  const { data: practicePathData } = useQuery({
    queryKey: ['skills', 'path', practiceSkillId],
    queryFn: () => skillsApi.path(practiceSkillId as number),
    enabled: practiceSkillId !== null,
    retry: false,
  })

  const createMut = useMutation({
    mutationFn: (input: CreateSkillInput) => skillsApi.create(input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['skills'] })
      qc.invalidateQueries({ queryKey: ['skills', 'overview'] })
      setShowCreateModal(false)
      setCreateStep(1)
      setName('')
      setCategory('')
      setDescription('')
      setGoalType('sessions')
      setGoalTarget('')
      setCreateError(null)
    },
    onError: (error: Error) => {
      if (error.message.includes('goal_required')) {
        setStrictGoalRollout(true)
        setCreateStep(2)
        setCreateError(t.errorGoalRequired)
        return
      }
      setCreateError(t.errorCreateFailed)
    },
  })

  const updateGoalMut = useMutation({
    mutationFn: ({
      skillId,
      goal_type,
      goal_target_value,
      goal_deadline,
    }: {
      skillId: number
      goal_type: 'sessions' | 'hours' | 'milestones'
      goal_target_value: number
      goal_deadline?: string | null
    }) =>
      skillsApi.update(skillId, {
        goal_type,
        goal_target_value,
        goal_deadline: goal_deadline || null,
      }),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ['skills'] })
      qc.invalidateQueries({ queryKey: ['skills', 'overview'] })
      qc.invalidateQueries({ queryKey: ['skills', 'path', variables.skillId] })
      setGoalSkillId(null)
      setGoalEditType('sessions')
      setGoalEditTarget('12')
      setGoalEditDeadline('')
      setGoalEditInsight(null)
      setGoalEditError(null)
    },
    onError: () => {
      setGoalEditError(t.errorUpdateGoalFailed)
    },
  })

  const practiceMut = useMutation({
    mutationFn: ({ skillId, mins, notes, stepId }: { skillId: number; mins: number; notes: string; stepId?: number }) =>
      skillsApi.logPractice(skillId, {
        duration_minutes: mins,
        step_id: stepId,
        notes: notes || undefined,
      }),
    onSuccess: (result, variables) => {
      const previousSkill = skills.find((s) => s.id === variables.skillId)
      qc.invalidateQueries({ queryKey: ['skills'] })
      qc.invalidateQueries({ queryKey: ['skills', 'overview'] })
      if (practiceSkillId !== null) {
        qc.invalidateQueries({ queryKey: ['skills', 'path', practiceSkillId] })
      }
      setNextActionHint(result.next_recommended_step?.label ?? null)
      setPracticeCelebration({
        minutesDelta: variables.mins,
        projectedTotalMinutes: (previousSkill?.total_minutes ?? 0) + variables.mins,
        sessionDelta: 1,
        streakDelta: inferStreakDelta(previousSkill?.last_practiced_at ?? null),
        nextStepLabel: result.next_recommended_step?.label ?? null,
      })
      setPracticeNotes('')
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => skillsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['skills'] })
      qc.invalidateQueries({ queryKey: ['skills', 'overview'] })
    },
  })

  const skills = data?.skills ?? []
  const hasOverviewPayload = Array.isArray(overviewData?.skills)
  const cards: SkillOverviewCard[] = hasOverviewPayload
    ? (overviewData?.skills ?? [])
    : skills.map((s) => ({
        skill_id: s.id,
        name: s.name,
        category: s.category,
        total_minutes: s.total_minutes,
        session_count: s.session_count,
        progress_state: s.streak_days > 0 ? 'on_track' : 'at_risk',
        goal: null,
        primary_action: 'continue_practice',
        requires_goal_setup: true,
        risk_reason: s.streak_days > 0 ? null : 'no_recent_sessions',
      }))

  const summary = overviewData?.summary ?? {
    total_hours: Number((cards.reduce((acc, c) => acc + c.total_minutes, 0) / 60).toFixed(1)),
    total_sessions: cards.reduce((acc, c) => acc + c.session_count, 0),
    at_risk: cards.filter((c) => c.progress_state === 'at_risk').length,
    active: cards.length,
  }
  const showMigrationBanner = hasOverviewPayload && cards.some((c) => c.requires_goal_setup)
  const goalTargetPresets = [8, 12, 20]

  function inferredSuggestedDuration(skillId: number): number {
    const skill = skills.find((s) => s.id === skillId)
    if (!skill) return 30

    const recentDurations = skill.recent_sessions
      .slice(0, 3)
      .map((session) => session.duration_minutes)
      .filter((value) => Number.isFinite(value) && value > 0)

    const baseline =
      recentDurations.length > 0
        ? recentDurations.reduce((acc, value) => acc + value, 0) / recentDurations.length
        : skill.session_count > 0
          ? skill.total_minutes / skill.session_count
          : 30

    const clamped = Math.max(10, Math.min(120, baseline))
    return Math.round(clamped / 5) * 5
  }

  function inferStreakDelta(lastPracticedAt: string | null): number {
    if (!lastPracticedAt) return 1
    const last = new Date(lastPracticedAt)
    const now = new Date()
    return last.toDateString() === now.toDateString() ? 0 : 1
  }

  const forecastQueries = useQueries({
    queries: cards.map((card) => ({
      queryKey: ['skills', 'forecast', card.skill_id],
      queryFn: async () => {
        try {
          return await skillsApi.forecast(card.skill_id)
        } catch (error) {
          const message = error instanceof Error ? error.message : ''
          if (message === 'not_found' || message.includes('API error 404')) {
            return null
          }
          throw error
        }
      },
      retry: false,
      staleTime: 60_000,
    })),
  })

  const forecastBySkillId = new Map<number, SkillForecast>()
  cards.forEach((card, index) => {
    const forecast = forecastQueries[index]?.data?.forecast
    if (forecast) {
      forecastBySkillId.set(card.skill_id, forecast)
    }
  })

  const skillNameById = new Map(skills.map((s) => [s.id, s.name]))
  for (const c of cards) {
    if (!skillNameById.has(c.skill_id)) {
      skillNameById.set(c.skill_id, c.name)
    }
  }

  const selectedPracticeSkill = skills.find((s) => s.id === practiceSkillId) ?? null
  const selectedPanelSkillId = deleteTarget?.id ?? goalSkillId ?? insightsSkillId
  const selectedPanelCard = selectedPanelSkillId !== null ? cards.find((card) => card.skill_id === selectedPanelSkillId) ?? null : null
  const selectedPanelForecast = selectedPanelSkillId !== null ? forecastBySkillId.get(selectedPanelSkillId) : undefined
  const selectedPanelSkill = selectedPanelSkillId !== null ? skills.find((skill) => skill.id === selectedPanelSkillId) ?? null : null
  const suggestedDurationValue = practiceSkillId !== null ? inferredSuggestedDuration(practiceSkillId) : 30
  const durationPresetValues = Array.from(new Set([20, 30, suggestedDurationValue, 45])).sort((a, b) => a - b)
  const createGoalPresets =
    goalType === 'hours' ? [10, 20, 40] : goalType === 'milestones' ? [3, 5, 8] : goalTargetPresets
  const parsedGoalTarget = parseInt(goalEditTarget)
  const safeGoalTarget = Number.isFinite(parsedGoalTarget) && parsedGoalTarget > 0 ? parsedGoalTarget : 0
  const goalCurrentValue = goalEditInsight?.currentValue ?? 0
  const goalPacePerWeek = goalEditInsight?.pacePerWeek ?? 0
  const goalRemaining = Math.max(safeGoalTarget - goalCurrentValue, 0)
  const goalModalSkillName = goalSkillId !== null ? skillNameById.get(goalSkillId) ?? '' : ''
  const goalEtaWeeks = goalPacePerWeek > 0 ? goalRemaining / goalPacePerWeek : null
  const goalEstimatedCompletionDate =
    goalEtaWeeks === null ? null : addDaysIso(new Date().toISOString().slice(0, 10), Math.ceil(goalEtaWeeks * 7))

  const displayCards = useMemo(() => {
    const entries = cards.map((card) => {
      const forecast = forecastBySkillId.get(card.skill_id)
      const backingSkill = skills.find((skill) => skill.id === card.skill_id) ?? null
      const sessionsLast7 = backingSkill?.sessions_last_7 ?? 0
      const cadenceSlots = buildWeeklyCadenceSlots(backingSkill)
      const cadenceActiveDays = cadenceSlots.filter(Boolean).length
      const nextActionNarrative = cardNextActionNarrative({
        requiresGoalSetup: card.requires_goal_setup,
        progressState: card.progress_state,
        forecastState: forecast?.forecast_state,
        cadenceActiveDays,
        labels: {
          setupGoalThenPractice: t.nextActionSetupGoalThenPractice,
          keepEndpointStable: t.nextActionKeepEndpointStable,
          recoverMomentum: t.nextActionRecoverMomentum,
          sustainRhythm: t.nextActionSustainRhythm,
          focusedSession: t.nextActionFocusedSession,
        },
      })
      const attentionReasons = deriveAttentionReasons({
        card,
        forecast,
        sessionsLast7,
      })

      const urgencyScore =
        (attentionReasons.length > 0 ? 50 : 0) +
        (card.progress_state === 'at_risk' || forecast?.forecast_state === 'at_risk' ? 30 : 0) +
        (card.requires_goal_setup ? 10 : 0)
      const momentumScore = sessionsLast7 * 4 + cadenceActiveDays * 2 + Math.min(card.session_count, 20)

      return {
        card,
        forecast,
        backingSkill,
        cadenceSlots,
        cadenceActiveDays,
        sessionsLast7,
        nextActionNarrative,
        attentionReasons,
        urgencyScore,
        momentumScore,
      }
    })

    const sorted = [...entries]
    if (sortMode === 'alphabetical') {
      sorted.sort((a, b) => a.card.name.localeCompare(b.card.name))
      return sorted
    }
    if (sortMode === 'momentum') {
      sorted.sort((a, b) => b.momentumScore - a.momentumScore || a.card.name.localeCompare(b.card.name))
      return sorted
    }
    sorted.sort((a, b) => b.urgencyScore - a.urgencyScore || a.card.name.localeCompare(b.card.name))
    return sorted
  }, [cards, forecastBySkillId, skills, sortMode, t])

  const attentionCards = displayCards.filter((entry) => entry.attentionReasons.length > 0)

  function selectSkillCard(skillId: number) {
    setInsightsSkillId(skillId)
    setGoalSkillId(null)
    setPracticeSkillId(null)
    setDeleteTarget(null)
  }

  function stateChip(card: SkillOverviewCard, forecast?: SkillForecast): { label: string; bg: string; fg: string } {
    const projectedAhead = (forecast?.projection.projected_goal_progress_ratio ?? 0) >= 1
    if (projectedAhead || forecast?.forecast_state === 'completed') {
      return { label: t.statusAhead, bg: '#d6e8ce', fg: '#465642' }
    }
    if (card.progress_state === 'at_risk' || forecast?.forecast_state === 'at_risk') {
      return { label: t.statusAtRisk, bg: '#fce8e4', fg: '#8b4a3a' }
    }
    return { label: t.statusOnTrack, bg: '#e8f0e3', fg: '#3a5c35' }
  }

  function attentionLabel(reason: AttentionReason): string {
    if (reason === 'deadline_risk') return t.attentionDeadlineRisk
    if (reason === 'below_pace') return t.attentionBelowPace
    return t.attentionStalled
  }

  function cardRiskSummary(reasons: AttentionReason[], forecast?: SkillForecast): string | null {
    if (reasons.length > 0) {
      return reasons.map((reason) => attentionLabel(reason)).join(', ')
    }
    if (forecast?.forecast_state === 'insufficient_data') {
      return t.riskNeedMoreHistory
    }
    return null
  }

  function createPreviewHeadline(): string {
    const trimmedName = name.trim()
    if (trimmedName) return trimmedName
    return t.namePlaceholder
  }

  function createPreviewSubline(): string {
    const trimmedCategory = category.trim()
    if (trimmedCategory) return trimmedCategory
    return `${t.category} ${t.optional}`
  }

  function createPreviewGoalLine(): string {
    const targetValue = parseInt(goalTarget)
    if (!Number.isFinite(targetValue) || targetValue <= 0) {
      return interpolate(t.tipGoalOptional, { editGoal: t.editGoal })
    }
    const safeTarget = targetValue
    return `${t.goalEndpoint}: ${safeTarget} ${goalType === 'hours' ? t.hoursLabel : goalType === 'milestones' ? t.milestonesLabel : t.sessions}.`
  }

  function createGoalTypeHelp(goalTypeValue: 'sessions' | 'hours' | 'milestones'): string {
    if (goalTypeValue === 'hours') {
      return t.goalTypeHelpHours
    }
    if (goalTypeValue === 'milestones') {
      return t.goalTypeHelpMilestones
    }
    return t.goalTypeHelpSessions
  }

  function createStudioSignals() {
    const hasName = name.trim().length > 0
    const hasCategory = category.trim().length > 0
    const hasDescription = description.trim().length > 0
    const targetValue = parseInt(goalTarget)
    const hasGoalTarget = Number.isFinite(targetValue) && targetValue > 0

    return [
      { label: t.signalClearSkillName, ready: hasName },
      { label: t.signalCategoryContextAdded, ready: hasCategory },
      { label: t.signalGoalEndpointSelected, ready: hasGoalTarget },
      { label: t.signalDescriptionIncludesIntent, ready: hasDescription },
    ]
  }

  function createStudioTip() {
    const targetValue = parseInt(goalTarget)
    if (!name.trim()) return t.tipNameSkillFirst
    if (!Number.isFinite(targetValue) || targetValue <= 0) {
      return interpolate(t.tipGoalOptional, { editGoal: t.editGoal })
    }
    return t.tipStrongEndpointSet
  }

  function forecastCopy(forecast: SkillForecast): { label: string; reason: string } {
    if (forecast.forecast_state === 'completed') {
      return { label: t.statusCompleted, reason: t.forecastReasonCompleted }
    }
    if (forecast.forecast_state === 'at_risk') {
      if (forecast.risk_reason === 'no_goal_configured') {
        return { label: t.statusAtRisk, reason: t.forecastReasonNoGoalConfigured }
      }
      if (forecast.risk_reason === 'no_recent_sessions') {
        return { label: t.statusAtRisk, reason: t.forecastReasonNoRecentSessions }
      }
      return { label: t.statusAtRisk, reason: t.forecastReasonNeedsConsistency }
    }
    if (forecast.forecast_state === 'insufficient_data') {
      if (forecast.risk_reason === 'non_projectable_goal_type') {
        return {
          label: t.statusInsufficientData,
          reason: t.forecastReasonQualitativeGoal,
        }
      }
      return { label: t.statusInsufficientData, reason: t.forecastReasonNeedMoreHistory }
    }
    return { label: t.statusOnTrack, reason: t.forecastReasonOnTrack }
  }

  function localizePracticeStepLabel(rawLabel: string | null | undefined): string {
    if (!rawLabel) return ''
    const normalized = rawLabel.trim().toLowerCase()
    if (normalized === 'continue practice') {
      return t.continuePractice
    }
    if (normalized === 'review goal progress' || normalized === 'review goal') {
      return t.reviewGoalProgress
    }
    return rawLabel
  }

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    const targetValue = parseInt(goalTarget)
    if (strictGoalRollout && (!targetValue || targetValue <= 0)) {
      setCreateStep(2)
      setCreateError(t.errorGoalRequired)
      return
    }
    setCreateError(null)

    const payload: CreateSkillInput = {
      name: name.trim(),
      category: category.trim() || undefined,
      description: description.trim() || undefined,
    }

    if (createStep === 2 && targetValue > 0) {
      payload.goal_type = goalType
      payload.goal_target_value = targetValue
    }

    createMut.mutate(payload)
  }

  function closeCreateModal() {
    setShowCreateModal(false)
    setCreateStep(1)
    setCreateError(null)
  }

  function openGoalModal(card: SkillOverviewCard) {
    selectSkillCard(card.skill_id)
    setGoalSkillId(card.skill_id)
    const backingSkill = skills.find((skill) => skill.id === card.skill_id)
    const rawGoalType = card.goal?.goal_type
    const safeGoalType =
      rawGoalType === 'sessions' || rawGoalType === 'hours' || rawGoalType === 'milestones'
        ? rawGoalType
        : 'sessions'
    setGoalEditType(safeGoalType)
    setGoalEditTarget(String(card.goal?.target_value ?? 12))
    setGoalEditDeadline(card.goal?.deadline?.slice(0, 10) ?? '')
    const currentValueFromGoal = card.goal?.current_value
    const currentValueFallback =
      safeGoalType === 'hours'
        ? Number(((backingSkill?.total_minutes ?? 0) / 60).toFixed(1))
        : safeGoalType === 'sessions'
          ? backingSkill?.session_count ?? 0
          : backingSkill?.session_count ?? 0
    const pacePerWeek =
      safeGoalType === 'hours'
        ? Number((((backingSkill?.sessions_last_7 ?? 0) * ((backingSkill?.total_minutes ?? 0) / Math.max(backingSkill?.session_count ?? 1, 1))) / 60).toFixed(1))
        : backingSkill?.sessions_last_7 ?? 0
    setGoalEditInsight({
      currentValue: currentValueFromGoal ?? currentValueFallback,
      pacePerWeek,
    })
    setGoalEditError(null)
  }

  function handleGoalSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (goalSkillId === null) return
    const targetValue = parseInt(goalEditTarget)
    if (!targetValue || targetValue <= 0) {
      setGoalEditError(t.errorTargetValueRequired)
      return
    }
    setGoalEditError(null)
    updateGoalMut.mutate({
      skillId: goalSkillId,
      goal_type: goalEditType,
      goal_target_value: targetValue,
      goal_deadline: goalEditDeadline || null,
    })
  }

  function closeGoalModal() {
    setGoalSkillId(null)
    setGoalEditError(null)
  }

  function handlePractice(e: React.FormEvent) {
    e.preventDefault()
    const mins = parseInt(duration)
    if (!practiceSkillId || !mins || mins <= 0) return
    setPracticeCelebration(null)
    const parsedStepId = parseInt(practiceStepId)
    practiceMut.mutate({
      skillId: practiceSkillId,
      mins,
      notes: practiceNotes.trim(),
      stepId: Number.isFinite(parsedStepId) ? parsedStepId : undefined,
    })
  }

  useEffect(() => {
    if (!practicePathData?.path?.next_recommended_step) return
    const recommended = practicePathData.path.next_recommended_step
    const recommendedIndex = practicePathData.path.steps.findIndex((step) => step.step_id === recommended.step_id)
    if (recommendedIndex >= 0) {
      setPracticeStepId(String(recommendedIndex + 1))
    }
  }, [practicePathData])

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const apply = () => setReduceMotion(media.matches)
    apply()
    media.addEventListener('change', apply)
    return () => media.removeEventListener('change', apply)
  }, [])

  function openPracticeModal(skillId: number) {
    setGoalSkillId(null)
    setPracticeSkillId(skillId)
    setPracticeStepId('')
    setPracticeNotes('')
    setDuration(String(inferredSuggestedDuration(skillId)))
    setNextActionHint(null)
    setPracticeCelebration(null)
  }

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="flex flex-col gap-4">
        <div>
          <p
            className="text-xs font-bold uppercase mb-2"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              letterSpacing: '0.05em',
              color: '#6b5a35',
            }}
          >
            {t.eyebrow}
          </p>
          <h1
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontSize: '2rem',
              fontWeight: 300,
              color: '#6b5a35',
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
      </div>

      <section
        className="grid grid-cols-2 md:grid-cols-4 gap-3"
        aria-label="Skills summary"
      >
        {[
          { label: t.summaryTotalHours, value: summary.total_hours.toFixed(1) },
          { label: t.summarySessions, value: summary.total_sessions.toString() },
          { label: t.summaryAtRisk, value: summary.at_risk.toString() },
          { label: t.summaryActive, value: summary.active.toString() },
        ].map((item) => (
          <article
            key={item.label}
            className="p-4"
            style={{
              background: '#ffffff',
              borderRadius: '0 14px 14px 14px',
              boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
            }}
          >
            <p
              style={{
                ...microLabel,
                fontSize: lang === 'ko' || lang === 'zh' ? '0.75rem' : microLabel.fontSize,
                letterSpacing: lang === 'ko' || lang === 'zh' ? '0.03em' : microLabel.letterSpacing,
              }}
            >
              {item.label}
            </p>
            <p
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: lang === 'ko' || lang === 'zh' ? '1.55rem' : '1.4rem',
                color: '#6b5a35',
                letterSpacing: '-0.03em',
              }}
            >
              {item.value}
            </p>
          </article>
        ))}
      </section>

      {showMigrationBanner && (
        <aside
          className="p-4"
          role="status"
          style={{
            background: '#f5f0e4',
            borderRadius: '0 14px 14px 14px',
            color: '#6b5a35',
          }}
        >
          <p style={microLabel}>{t.migrationNoticeTitle}</p>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              lineHeight: 1.5,
            }}
          >
            {t.migrationNoticeBody}
          </p>
        </aside>
      )}

      {/* Create modal */}
      {showCreateModal && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center p-4"
          onClick={closeCreateModal}
          style={{
            background: 'rgba(26, 31, 26, 0.35)',
            backdropFilter: 'blur(6px)',
          }}
        >
          <form
            onSubmit={handleCreate}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-4xl p-6 md:p-8"
            style={{
              background: '#ffffff',
              borderRadius: '0 16px 16px 16px',
              boxShadow: '0 30px 60px rgba(46, 52, 43, 0.08)',
            }}
          >
            <div className="grid grid-cols-1 md:grid-cols-[1.05fr_0.95fr] gap-6 items-stretch" style={{ minHeight: '520px' }}>
                <div className="space-y-4 flex flex-col">
                  <div className="space-y-3">
                    <p style={microLabel}>{interpolate(t.stepOf2, { step: createStep })}</p>
                    <h2
                      style={{
                        fontFamily: 'var(--font-serif), Georgia, serif',
                        fontSize: '1.2rem',
                        color: '#6b5a35',
                        letterSpacing: '-0.03em',
                      }}
                    >
                      {createStep === 1 ? t.skillBasics : t.goalEndpoint}
                    </h2>
                    <div className="flex items-center gap-2" aria-label="Create progress">
                      {[1, 2].map((step) => (
                        <div
                          key={step}
                          className="h-1.5 rounded-full transition-all duration-200 ease-out"
                          style={{
                            width: step === createStep ? 46 : 30,
                            background: step <= createStep ? '#6b5a35' : '#dee5d7',
                          }}
                        />
                      ))}
                    </div>
                  </div>

                  {strictGoalRollout && (
                    <div
                      className="p-3"
                      role="status"
                      style={{
                        background: '#f5f0e4',
                        borderRadius: '0 10px 10px 10px',
                        color: '#6b5a35',
                      }}
                    >
                      <p style={microLabel}>{t.rolloutGateTitle}</p>
                      <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem' }}>
                        {t.rolloutGateBody}
                      </p>
                    </div>
                  )}

                  {createStep === 1 && (
                    <>
                    <div className="space-y-2">
                      <label htmlFor="sk-name" style={microLabel}>{t.name}</label>
                      <input id="sk-name" required value={name} onChange={(e) => setName(e.target.value)} placeholder={t.namePlaceholder} style={inputStyle} />
                    </div>
                    <div className="space-y-2">
                      <label htmlFor="sk-cat" style={microLabel}>{t.category}</label>
                      <input id="sk-cat" value={category} onChange={(e) => setCategory(e.target.value)} placeholder={t.categoryPlaceholder} style={inputStyle} />
                    </div>
                    <div className="space-y-2">
                      <label htmlFor="sk-desc" style={microLabel}>{t.description}</label>
                      <input id="sk-desc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder={t.optional} style={inputStyle} />
                    </div>
                    <div className="flex flex-wrap items-center gap-3 pt-1">
                      <button
                        type="button"
                        onClick={() => {
                          if (!name.trim()) return
                          setCreateError(null)
                          setCreateStep(2)
                        }}
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontWeight: 700,
                          fontSize: '0.875rem',
                          color: '#ffffff',
                          background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                          borderRadius: '100px',
                          padding: '12px 28px',
                          border: 'none',
                          cursor: 'pointer',
                          boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
                        }}
                      >
                        {t.continueAction}
                      </button>

                      <button
                        type="button"
                        onClick={closeCreateModal}
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontWeight: 700,
                          fontSize: '0.8125rem',
                          color: '#6b5a35',
                          background: '#ede4d0',
                          borderRadius: '100px',
                          border: 'none',
                          cursor: 'pointer',
                          padding: '12px 20px',
                        }}
                      >
                        {t.cancel}
                      </button>
                    </div>

                    {createError && (
                      <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#8b4a3a' }}>
                        {createError}
                      </p>
                    )}
                    </>
                  )}

                  {createStep === 2 && (
                    <>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <p style={microLabel}>{t.goalType}</p>
                        <div className="flex flex-wrap gap-2" role="group" aria-label="Create goal type options">
                          {goalTypeOptions.map((option) => {
                            const isActive = goalType === option.value
                            return (
                              <button
                                key={option.value}
                                type="button"
                                onClick={() => setGoalType(option.value)}
                                aria-pressed={isActive}
                                style={{
                                  fontFamily: 'var(--font-manrope), sans-serif',
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                  color: isActive ? '#6b5a35' : '#6f6a5c',
                                  background: isActive ? '#e8ddc3' : '#efe7d6',
                                  borderRadius: '999px',
                                  border: 'none',
                                  padding: '7px 12px',
                                  cursor: 'pointer',
                                }}
                              >
                                {option.label}
                              </button>
                            )
                          })}
                        </div>
                        <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72', lineHeight: 1.5 }}>
                          {createGoalTypeHelp(goalType)}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <label htmlFor="sk-goal-target" style={microLabel}>{t.targetValue}</label>
                        <Input
                          id="sk-goal-target"
                          type="number"
                          min="1"
                          value={goalTarget}
                          onChange={(e) => setGoalTarget(e.target.value)}
                          style={inputStyle}
                        />
                        <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
                          {t.unit}: {goalType === 'hours' ? t.hoursLabel : goalType === 'milestones' ? t.milestonesLabel : t.sessions}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <p style={microLabel}>{t.quickPresets}</p>
                      <div className="flex flex-wrap gap-2">
                        {createGoalPresets.map((preset) => {
                          const isActive = goalTarget === String(preset)
                          return (
                            <button
                              key={preset}
                              type="button"
                              onClick={() => setGoalTarget(String(preset))}
                              style={{
                                fontFamily: 'var(--font-manrope), sans-serif',
                                fontSize: '0.8125rem',
                                fontWeight: 700,
                                color: isActive ? '#6b5a35' : '#5a6157',
                                background: isActive ? '#e8ddc3' : '#ede4d0',
                                borderRadius: '999px',
                                border: 'none',
                                padding: '8px 12px',
                                cursor: 'pointer',
                              }}
                            >
                              {preset}
                            </button>
                          )
                        })}
                      </div>
                    </div>

                    {createError && (
                      <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#8b4a3a' }}>
                        {createError}
                      </p>
                    )}

                    <div className="flex gap-3 pt-1">
                      <button
                        type="button"
                        onClick={() => setCreateStep(1)}
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontWeight: 700,
                          fontSize: '0.8125rem',
                          textTransform: 'uppercase' as const,
                          letterSpacing: '0.05em',
                          color: '#767d72',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          padding: '12px 20px',
                          borderRadius: '100px',
                        }}
                      >
                        {t.back}
                      </button>
                      <button
                        type="submit"
                        disabled={createMut.isPending}
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontWeight: 700,
                          fontSize: '0.875rem',
                          color: '#ffffff',
                          background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                          borderRadius: '100px',
                          padding: '12px 28px',
                          border: 'none',
                          cursor: 'pointer',
                          boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
                        }}
                      >
                        {createMut.isPending ? t.creating : t.createSkill}
                      </button>
                    </div>
                    </>
                  )}
                </div>

                <aside
                  className="h-full flex flex-col"
                  role="status"
                  style={{
                    borderRadius: '0 16px 16px 16px',
                    background: 'linear-gradient(145deg, #f8f3eb 0%, #f5ead5 56%, #efe3cb 100%)',
                    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.6)',
                    padding: '20px',
                    gap: '14px',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      position: 'absolute',
                      width: '120px',
                      height: '120px',
                      borderRadius: '999px',
                      background: 'radial-gradient(circle, rgba(107,90,53,0.18) 0%, rgba(107,90,53,0) 70%)',
                      top: '-24px',
                      right: '-20px',
                      pointerEvents: 'none',
                    }}
                  />
                  <div
                    style={{
                      position: 'absolute',
                      width: '96px',
                      height: '96px',
                      borderRadius: '999px',
                      background: 'radial-gradient(circle, rgba(132,106,64,0.16) 0%, rgba(132,106,64,0) 72%)',
                      bottom: '-18px',
                      left: '-12px',
                      pointerEvents: 'none',
                    }}
                  />

                  <p style={{ ...microLabel, color: '#6b5a35' }}>{t.skillPreview}</p>
                  <h3
                    style={{
                      fontFamily: 'var(--font-serif), Georgia, serif',
                      fontSize: '1.35rem',
                      fontWeight: 400,
                      color: '#6b5a35',
                      letterSpacing: '-0.03em',
                    }}
                  >
                    {createPreviewHeadline()}
                  </h3>
                  <p
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.875rem',
                      color: '#5a6157',
                      lineHeight: 1.55,
                    }}
                  >
                    {createPreviewSubline()}
                  </p>

                  <div
                    style={{
                      background: '#ffffff',
                      borderRadius: '0 14px 14px 14px',
                      padding: '16px',
                    }}
                  >
                    <p style={microLabel}>{t.preview}</p>
                    <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#2e342b', lineHeight: 1.55 }}>
                      {t.category}: <strong>{category.trim() || '-'}</strong>
                    </p>
                    <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#2e342b', lineHeight: 1.55 }}>
                      {t.goalTypeLabel}: <strong>{goalType === 'hours' ? t.hoursLabel : goalType === 'milestones' ? t.milestonesLabel : t.sessions}</strong>
                    </p>
                    <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#2e342b', lineHeight: 1.55 }}>
                      {createPreviewGoalLine()}
                    </p>
                  </div>

                  <p
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '1.05rem',
                      fontWeight: 700,
                      color: '#6b5a35',
                    }}
                  >
                    {t.studioHeading}
                  </p>

                  <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {createStudioSignals().map((signal) => (
                      <li key={signal.label} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span
                          style={{
                            width: '18px',
                            height: '18px',
                            borderRadius: '999px',
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.625rem',
                            fontWeight: 700,
                            color: signal.ready ? '#6b5a35' : '#8f8a7f',
                            background: signal.ready ? '#e8ddc3' : '#efe7d6',
                          }}
                        >
                          {signal.ready ? '✓' : '•'}
                        </span>
                        <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#5a6157' }}>
                          {signal.label}
                        </span>
                      </li>
                    ))}
                  </ul>

                  <p style={{ marginTop: 'auto', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#7a7468', lineHeight: 1.55 }}>
                    {createStudioTip()}
                  </p>
                </aside>
              </div>
          </form>
        </div>
      )}

      {/* Skills + insights layout */}
      <div className="flex flex-col lg:flex-row gap-6 items-start">
        <section
          className="w-full lg:w-[60%] p-7 space-y-5"
          style={{
            background: '#ffffff',
            borderRadius: '0 16px 16px 16px',
            boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
          }}
        >
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <h2
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: '1.125rem',
                fontWeight: 400,
                color: '#6b5a35',
                letterSpacing: '-0.03em',
              }}
            >
              {t.yourSkills}
            </h2>
            <button
              onClick={() => {
                setStrictGoalRollout(false)
                setCreateStep(1)
                setShowCreateModal(true)
              }}
              className="flex items-center gap-2"
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontWeight: 700,
                fontSize: '0.75rem',
                color: '#ffffff',
                background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                borderRadius: '100px',
                minHeight: '44px',
                padding: '0 16px',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(46, 52, 43, 0.18)',
              }}
            >
              <><Plus size={12} /> {t.newSkill}</>
            </button>
          </div>
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-wrap items-center gap-2" aria-label={t.density}>
              <span style={microLabel}>{t.density}</span>
              <button
                type="button"
                onClick={() => setDensityMode('compact')}
                aria-pressed={densityMode === 'compact'}
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  color: densityMode === 'compact' ? '#6b5a35' : '#6f6a5c',
                  background: densityMode === 'compact' ? '#e8ddc3' : '#efe7d6',
                  borderRadius: '999px',
                  border: 'none',
                  padding: '6px 10px',
                  cursor: 'pointer',
                }}
              >
                {t.densityCompact}
              </button>
              <button
                type="button"
                onClick={() => setDensityMode('comfortable')}
                aria-pressed={densityMode === 'comfortable'}
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  color: densityMode === 'comfortable' ? '#6b5a35' : '#6f6a5c',
                  background: densityMode === 'comfortable' ? '#e8ddc3' : '#efe7d6',
                  borderRadius: '999px',
                  border: 'none',
                  padding: '6px 10px',
                  cursor: 'pointer',
                }}
              >
                {t.densityComfortable}
              </button>
            </div>
            <div className="flex items-center gap-2">
              <label htmlFor="skills-sort-mode" style={microLabel}>{t.sortBy}</label>
              <select
                id="skills-sort-mode"
                value={sortMode}
                onChange={(event) => setSortMode(event.target.value as SortMode)}
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  color: '#5a6157',
                  background: '#f1f5eb',
                  border: '1px solid rgba(173, 180, 168, 0.20)',
                  borderRadius: '999px',
                  padding: '6px 12px',
                }}
              >
                <option value="urgency">{t.sortUrgency}</option>
                <option value="momentum">{t.sortMomentum}</option>
                <option value="alphabetical">{t.sortAlphabetical}</option>
              </select>
            </div>
          </div>

          {attentionCards.length > 0 && (
            <div
              className="p-3 space-y-2"
              role="status"
              style={{
                background: '#f5f0e4',
                borderRadius: '0 12px 12px 12px',
              }}
            >
              <p style={microLabel}>{t.needsAttention}</p>
              <div className="flex flex-wrap gap-2">
                {attentionCards.map((entry) => (
                  <button
                    key={`attention-${entry.card.skill_id}`}
                    type="button"
                    onClick={() => selectSkillCard(entry.card.skill_id)}
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: '#8b4a3a',
                      background: '#fce8e4',
                      borderRadius: '999px',
                      border: 'none',
                      padding: '7px 12px',
                      cursor: 'pointer',
                    }}
                  >
                    {entry.card.name}: {attentionLabel(entry.attentionReasons[0])}
                  </button>
                ))}
              </div>
            </div>
          )}
          {(isLoading || isOverviewLoading) && (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => <div key={i} className="h-14 rounded-xl animate-pulse" style={{ background: '#f5f0e4' }} />)}
            </div>
          )}
          {!isLoading && !isOverviewLoading && cards.length === 0 && (
            <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
              {t.noSkills}
            </p>
          )}
          {displayCards.length > 0 && (
            <ul className="space-y-3">
              {displayCards.map((entry, cardIndex) => {
                const { card, forecast, backingSkill, cadenceSlots, cadenceActiveDays, sessionsLast7, nextActionNarrative, attentionReasons } = entry
                const chip = stateChip(card, forecast)
                const progressRatio = Math.max(0, Math.min(1, card.goal?.progress_ratio ?? 0))
                const nowSummary = card.goal
                  ? interpolate(t.nowTowardGoal, { progress: `${Math.round(progressRatio * 100)}%` })
                  : interpolate(t.nowPracticeVolume, {
                      minutes: fmtMinutes(card.total_minutes, { minuteShort: t.minuteShort, hourShort: t.hourShort }),
                      sessions: card.session_count,
                    })
                const riskSummary = cardRiskSummary(attentionReasons, forecast)
                return (
                  <li
                    key={card.skill_id}
                    className="flex items-start justify-between gap-4 transition-all duration-220 card-lift"
                    role="button"
                    tabIndex={0}
                    aria-label={`Open details for ${card.name}`}
                    onClick={() => selectSkillCard(card.skill_id)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault()
                        selectSkillCard(card.skill_id)
                      }
                    }}
                    style={{
                      padding: densityMode === 'compact' ? '12px 14px' : '16px 20px',
                      borderRadius: '0 12px 12px 12px',
                      background: '#f8faf2',
                    }}
                  >
                    <div className="min-w-0 flex-1">
                      <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>
                        {card.name}
                      </p>
                      <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
                        {card.category && (
                          <span
                            className="px-2 py-0.5"
                            style={{
                              background: '#f5f0e4',
                              color: '#6b5a35',
                              borderRadius: '100px',
                              fontSize: '0.625rem',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em',
                            }}
                          >
                            {card.category}
                          </span>
                        )}
                        {densityMode === 'comfortable' && (
                          <>
                            <span className="flex items-center gap-1"><Clock size={11} /> {fmtMinutes(card.total_minutes, { minuteShort: t.minuteShort, hourShort: t.hourShort })}</span>
                            <span>{card.session_count} {t.sessions}</span>
                            <span>{interpolate(t.last7Days, { count: sessionsLast7 })}</span>
                          </>
                        )}
                        <span
                          className="px-2 py-0.5"
                          style={{
                            background: chip.bg,
                            color: chip.fg,
                            borderRadius: '100px',
                            fontSize: '0.625rem',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                          }}
                        >
                          {chip.label}
                        </span>
                      </div>

                      <div
                        className="mt-3 grid gap-2"
                        style={{
                          opacity: reduceMotion ? 1 : 0,
                          animation: reduceMotion ? undefined : 'skillsCardReveal 260ms ease-out forwards',
                          animationDelay: reduceMotion ? undefined : `${cardIndex * 45}ms`,
                        }}
                      >
                        <div>
                          <p style={microLabel}>{t.nowLabel}</p>
                          <p
                            style={{
                              fontFamily: 'var(--font-manrope), sans-serif',
                              fontSize: densityMode === 'compact' ? '0.75rem' : '0.8125rem',
                              color: '#2e342b',
                              lineHeight: 1.45,
                            }}
                          >
                            {nowSummary}
                          </p>
                        </div>
                        <div>
                          <p style={microLabel}>{t.nextLabel}</p>
                          <p
                            style={{
                              fontFamily: 'var(--font-manrope), sans-serif',
                              fontSize: densityMode === 'compact' ? '0.75rem' : '0.8125rem',
                              color: '#5a6157',
                              lineHeight: 1.45,
                            }}
                          >
                            {nextActionNarrative}
                          </p>
                        </div>
                        {riskSummary && (
                          <div>
                            <p style={microLabel}>{t.riskLabel}</p>
                            <p
                              style={{
                                fontFamily: 'var(--font-manrope), sans-serif',
                                fontSize: densityMode === 'compact' ? '0.75rem' : '0.8125rem',
                                color: attentionReasons.length > 0 ? '#8b4a3a' : '#5a6157',
                                lineHeight: 1.45,
                              }}
                            >
                              {riskSummary}
                            </p>
                          </div>
                        )}
                      </div>

                      {densityMode === 'compact' && cadenceActiveDays > 0 && (
                        <div className="mt-2 flex items-center gap-1" aria-label={interpolate(t.weeklyCadenceAria, { name: card.name })}>
                          {cadenceSlots.map((active, index) => (
                            <span
                              key={`${card.skill_id}-cadence-${index}`}
                              style={{
                                width: '7px',
                                height: '7px',
                                borderRadius: '999px',
                                background: active ? '#6b5a35' : '#dfe6d8',
                                display: 'inline-block',
                              }}
                            />
                          ))}
                        </div>
                      )}

                      {densityMode === 'comfortable' && card.goal && (
                        <div className="mt-3">
                          <div
                            className="mt-1"
                            style={{
                              height: '6px',
                              background: '#ebefe4',
                              borderRadius: '100px',
                              overflow: 'hidden',
                            }}
                          >
                            <div
                              style={{
                                width: `${Math.round(progressRatio * 100)}%`,
                                height: '100%',
                                background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                                transition: reduceMotion ? undefined : 'width 240ms ease',
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation()
                          openPracticeModal(card.skill_id)
                        }}
                        className="flex items-center gap-1"
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontSize: '0.6875rem',
                          fontWeight: 700,
                          textTransform: 'uppercase' as const,
                          letterSpacing: '0.05em',
                          padding: '6px 14px',
                          borderRadius: '100px',
                          border: 'none',
                          cursor: 'pointer',
                          color: '#ffffff',
                          background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                          boxShadow: '0 4px 12px rgba(46, 52, 43, 0.15)',
                        }}
                      >
                        <Play size={10} /> {t.continuePractice}
                      </button>
                    </div>
                  </li>
                )
              })}
            </ul>
          )}
        </section>

        <aside
          className="w-full lg:w-[40%] p-4 space-y-4 lg:sticky lg:top-24"
          style={{
            background: '#f8faf2',
            borderRadius: '0 12px 12px 12px',
            border: '1px solid #e8ece2',
          }}
        >
          {selectedPanelCard ? (
            <>
              <div>
                <p style={microLabel}>{t.yourSkills}</p>
                <h3
                  style={{
                    fontFamily: 'var(--font-serif), Georgia, serif',
                    fontSize: '1.1rem',
                    color: '#6b5a35',
                    letterSpacing: '-0.03em',
                  }}
                >
                  {selectedPanelCard.name}
                </h3>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => openGoalModal(selectedPanelCard)}
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    textTransform: 'uppercase' as const,
                    letterSpacing: '0.05em',
                    padding: '6px 12px',
                    borderRadius: '100px',
                    border: 'none',
                    cursor: 'pointer',
                    color: selectedPanelCard.requires_goal_setup ? '#8b4a3a' : '#465642',
                    background: selectedPanelCard.requires_goal_setup ? '#fce8e4' : '#d6e8ce',
                  }}
                >
                  {selectedPanelCard.requires_goal_setup ? t.setGoal : t.editGoal}
                </button>
                <button
                  type="button"
                  onClick={() => setDeleteTarget({ id: selectedPanelCard.skill_id, name: selectedPanelCard.name })}
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.6875rem',
                    fontWeight: 700,
                    textTransform: 'uppercase' as const,
                    letterSpacing: '0.05em',
                    padding: '6px 12px',
                    borderRadius: '100px',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#8b4a3a',
                    background: '#fce8e4',
                  }}
                >
                  {t.deleteConfirm}
                </button>
              </div>

              <div
                className="p-4"
                style={{
                  background: '#ffffff',
                  borderRadius: '0 10px 10px 10px',
                }}
              >
                <div className="space-y-4">
                    <p style={microLabel}>{interpolate(t.insightsTitle, { skill: selectedPanelCard.name })}</p>

                    <div className="space-y-1.5">
                      <p style={microLabel}>{t.weeklyCadence}</p>
                      <div className="flex items-center gap-1" aria-label={interpolate(t.weeklyCadenceAria, { name: selectedPanelCard.name })}>
                        {buildWeeklyCadenceSlots(selectedPanelSkill).map((active, index) => (
                          <span
                            key={`${selectedPanelCard.skill_id}-panel-cadence-${index}`}
                            style={{
                              width: '10px',
                              height: '10px',
                              borderRadius: '999px',
                              background: active ? '#6b5a35' : '#dfe6d8',
                              display: 'inline-block',
                            }}
                          />
                        ))}
                      </div>
                    </div>

                    {selectedPanelForecast ? (
                      <div
                        className="p-4 space-y-2"
                        style={{
                          background: '#f5f0e4',
                          borderRadius: '0 10px 10px 10px',
                        }}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <p style={microLabel}>{interpolate(t.forecast, { days: selectedPanelForecast.horizon_days })}</p>
                          <span
                            className="px-2 py-0.5"
                            style={{
                              background: '#e8f0e3',
                              color: '#3a5c35',
                              borderRadius: '100px',
                              fontFamily: 'var(--font-manrope), sans-serif',
                              fontSize: '0.625rem',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em',
                            }}
                          >
                            {forecastCopy(selectedPanelForecast).label}
                          </span>
                        </div>

                        {(() => {
                          const activeScenario = forecastScenarioBySkill[selectedPanelCard.skill_id] ?? 'keep_pace'
                          const scenarioProjection = applyForecastScenario(selectedPanelForecast, activeScenario)
                          return (
                            <>
                              <p
                                key={`${selectedPanelCard.skill_id}-panel-projected-${activeScenario}`}
                                style={{
                                  fontFamily: 'var(--font-manrope), sans-serif',
                                  fontSize: '0.8125rem',
                                  color: '#6b5a35',
                                  animation: reduceMotion ? undefined : 'skillsFadeSlide 180ms ease-out',
                                }}
                              >
                                {interpolate(t.projectedSummary, {
                                  minutes: fmtMinutes(scenarioProjection.projectedMinutes, {
                                    minuteShort: t.minuteShort,
                                    hourShort: t.hourShort,
                                  }),
                                  sessions: scenarioProjection.projectedSessions,
                                })}
                              </p>
                              <div className="space-y-1.5">
                                <p style={microLabel}>{t.forecastScenarios}</p>
                                <div className="flex flex-wrap gap-2">
                                  {([
                                    { value: 'keep_pace', label: t.scenarioKeepPace },
                                    { value: 'plus_one_session', label: t.scenarioPlusOneSession },
                                    { value: 'plus_thirty_minutes', label: t.scenarioPlusThirtyMinutes },
                                  ] as const).map((scenario) => {
                                    const isActive = activeScenario === scenario.value
                                    return (
                                      <button
                                        key={scenario.value}
                                        type="button"
                                        onClick={() =>
                                          setForecastScenarioBySkill((prev) => ({
                                            ...prev,
                                            [selectedPanelCard.skill_id]: scenario.value,
                                          }))
                                        }
                                        aria-pressed={isActive}
                                        style={{
                                          fontFamily: 'var(--font-manrope), sans-serif',
                                          fontSize: '0.6875rem',
                                          fontWeight: 700,
                                          color: isActive ? '#6b5a35' : '#6f6a5c',
                                          background: isActive ? '#e8ddc3' : '#efe7d6',
                                          borderRadius: '999px',
                                          border: 'none',
                                          padding: '6px 10px',
                                          cursor: 'pointer',
                                          textTransform: 'uppercase',
                                          letterSpacing: '0.04em',
                                          transition: reduceMotion ? undefined : 'transform 140ms ease, background 180ms ease, color 180ms ease',
                                          transform: isActive ? 'translateY(-1px)' : 'translateY(0)',
                                        }}
                                      >
                                        {scenario.label}
                                      </button>
                                    )
                                  })}
                                </div>
                              </div>
                              {scenarioProjection.projectedGoalProgressRatio !== null && (
                                <p
                                  key={`${selectedPanelCard.skill_id}-panel-ratio-${activeScenario}`}
                                  style={{
                                    fontFamily: 'var(--font-manrope), sans-serif',
                                    fontSize: '0.75rem',
                                    color: '#6b5a35',
                                    animation: reduceMotion ? undefined : 'skillsFadeSlide 180ms ease-out',
                                  }}
                                >
                                  {interpolate(t.scenarioProjectedProgress, {
                                    progress: `${Math.round(scenarioProjection.projectedGoalProgressRatio * 100)}%`,
                                  })}
                                </p>
                              )}
                            </>
                          )
                        })()}

                        <p
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.8125rem',
                            color: '#5a6157',
                            lineHeight: 1.5,
                          }}
                        >
                          {forecastCopy(selectedPanelForecast).reason}
                        </p>
                      </div>
                    ) : (
                      <p
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontSize: '0.875rem',
                          color: '#767d72',
                        }}
                      >
                        {t.notAvailableYet}
                      </p>
                    )}
                  </div>
              </div>
            </>
          ) : (
            <div
              style={{
                background: 'linear-gradient(160deg, #f8faf2 0%, #ffffff 100%)',
                borderRadius: '0 16px 16px 16px',
                boxShadow: '0 10px 26px rgba(46, 52, 43, 0.07)',
                padding: '48px 24px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '16px',
                minHeight: '380px',
              }}
            >
              <div
                style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '50%',
                  background: '#f1f5eb',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Leaf size={24} style={{ color: '#767d72' }} />
              </div>
              <p
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.875rem',
                  color: '#767d72',
                  textAlign: 'center',
                }}
              >
                {t.viewInsights}
              </p>
            </div>
          )}
        </aside>
      </div>

      {goalSkillId !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          onClick={closeGoalModal}
          style={{
            background: 'rgba(46, 52, 43, 0.3)',
            backdropFilter: 'blur(4px)',
            WebkitBackdropFilter: 'blur(4px)',
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: '#ffffff',
              borderRadius: '0 16px 16px 16px',
              boxShadow: '0 16px 48px rgba(46, 52, 43, 0.12)',
              padding: '28px',
              maxWidth: '760px',
              width: 'calc(100% - 32px)',
              maxHeight: 'calc(100vh - 48px)',
              overflowY: 'auto',
            }}
          >
            <form onSubmit={handleGoalSubmit} className="space-y-5">
              <h4
                style={{
                  fontFamily: 'var(--font-serif), Georgia, serif',
                  fontSize: '1.125rem',
                  fontWeight: 400,
                  color: '#6b5a35',
                  letterSpacing: '-0.03em',
                }}
              >
                {goalModalSkillName ? interpolate(t.insightsTitle, { skill: goalModalSkillName }) : t.editGoal}
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <p style={microLabel}>{t.goalType}</p>
                  <div className="flex flex-wrap gap-2" role="group" aria-label="Goal type options">
                    {goalTypeOptions.map((option) => {
                      const isActive = goalEditType === option.value
                      return (
                        <button
                          key={option.value}
                          type="button"
                          onClick={() => setGoalEditType(option.value)}
                          aria-pressed={isActive}
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            color: isActive ? '#6b5a35' : '#6f6a5c',
                            background: isActive ? '#e8ddc3' : '#efe7d6',
                            borderRadius: '999px',
                            border: 'none',
                            padding: '7px 12px',
                            cursor: 'pointer',
                          }}
                        >
                          {option.label}
                        </button>
                      )
                    })}
                  </div>
                </div>
                <div className="space-y-2">
                  <label htmlFor="goal-edit-target" style={microLabel}>{t.targetValue}</label>
                  <Input
                    id="goal-edit-target"
                    type="number"
                    min="1"
                    required
                    value={goalEditTarget}
                    onChange={(e) => setGoalEditTarget(e.target.value)}
                  />
                </div>
              </div>

              <div
                className="p-4 space-y-3"
                style={{
                  background: '#f5f0e4',
                  borderRadius: '0 10px 10px 10px',
                }}
              >
                <p style={microLabel}>{t.goalSnapshot}</p>
                <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.9375rem', color: '#6b5a35', lineHeight: 1.55 }}>
                  {formatGoalValue(goalCurrentValue, goalEditType, { hourShort: t.hourShort })} {t.doneSoFar}, {interpolate(t.targetingTotal, {
                    target: safeGoalTarget > 0 ? formatGoalValue(safeGoalTarget, goalEditType, { hourShort: t.hourShort }) : '-',
                  })}
                </p>
                <div
                  className="h-2"
                  style={{
                    background: '#ede4d0',
                    borderRadius: '999px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${safeGoalTarget > 0 ? Math.min(100, Math.round((goalCurrentValue / safeGoalTarget) * 100)) : 0}%`,
                      height: '100%',
                      background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                    }}
                  />
                </div>
                {goalEditType === 'milestones' ? (
                  <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', lineHeight: 1.5 }}>
                    {t.milestoneQualitativeHint}
                  </p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}>
                      {t.pace}:{' '}
                      {formatGoalPace(goalPacePerWeek, goalEditType, {
                        notEnoughDataYet: t.notEnoughDataYet,
                        milestonesLabel: t.milestonesLabel,
                        sessions: t.sessions,
                        hourShort: t.hourShort,
                        weekShort: t.weekShort,
                      })}
                    </p>
                    <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}>
                      {t.eta}: {goalEstimatedCompletionDate ? fmtCompactDate(goalEstimatedCompletionDate) : t.notAvailableYet}
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <p style={microLabel}>{t.quickActions}</p>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      const current = parseInt(goalEditTarget)
                      const base = Number.isFinite(current) && current > 0 ? current : 12
                      setGoalEditTarget(String(Math.ceil(base * 1.1)))
                    }}
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: '#6b5a35',
                      background: '#e8ddc3',
                      borderRadius: '999px',
                      border: 'none',
                      padding: '7px 12px',
                      cursor: 'pointer',
                    }}
                  >
                    {t.raiseTargetBy10}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      const base = goalEditDeadline || new Date().toISOString().slice(0, 10)
                      setGoalEditDeadline(addDaysIso(base, 14))
                    }}
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: '#6f6a5c',
                      background: '#efe7d6',
                      borderRadius: '999px',
                      border: 'none',
                      padding: '7px 12px',
                      cursor: 'pointer',
                    }}
                  >
                    {t.extendTimelineBy14d}
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="goal-edit-deadline" style={microLabel}>{t.deadlineOptional}</label>
                <Input
                  id="goal-edit-deadline"
                  type="date"
                  value={goalEditDeadline}
                  onChange={(e) => setGoalEditDeadline(e.target.value)}
                />
              </div>

              {goalEditError && (
                <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#8b4a3a' }}>
                  {goalEditError}
                </p>
              )}

              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={closeGoalModal}
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.8125rem',
                    fontWeight: 600,
                    color: '#5a6157',
                    background: '#f1f5eb',
                    border: 'none',
                    borderRadius: '100px',
                    padding: '10px 20px',
                    cursor: 'pointer',
                  }}
                >
                  {t.cancel}
                </button>
                <button
                  type="submit"
                  disabled={updateGoalMut.isPending}
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontWeight: 700,
                    fontSize: '0.875rem',
                    color: '#ffffff',
                    background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                    borderRadius: '100px',
                    padding: '12px 28px',
                    border: 'none',
                    cursor: 'pointer',
                    boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
                  }}
                >
                  {updateGoalMut.isPending ? t.saving : t.saveGoal}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {practiceSkillId && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          onClick={() => setPracticeSkillId(null)}
          style={{
            background: 'rgba(46, 52, 43, 0.3)',
            backdropFilter: 'blur(4px)',
            WebkitBackdropFilter: 'blur(4px)',
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: '#ffffff',
              borderRadius: '0 16px 16px 16px',
              boxShadow: '0 16px 48px rgba(46, 52, 43, 0.12)',
              padding: '28px',
              maxWidth: '760px',
              width: 'calc(100% - 32px)',
              maxHeight: 'calc(100vh - 48px)',
              overflowY: 'auto',
            }}
          >
            <form onSubmit={handlePractice} className="space-y-5">
              <h4
                style={{
                  fontFamily: 'var(--font-serif), Georgia, serif',
                  fontSize: '1.125rem',
                  fontWeight: 400,
                  color: '#6b5a35',
                  letterSpacing: '-0.03em',
                }}
              >
                {interpolate(t.continuePracticeTitle, { skill: skillNameById.get(practiceSkillId) ?? '' })}
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="pr-dur" style={microLabel}>{t.durationLabel}</label>
                  <Input id="pr-dur" type="number" min="1" required value={duration} onChange={(e) => setDuration(e.target.value)} />
                  <div className="space-y-2">
                    <p style={microLabel}>{t.suggested}</p>
                    <div className="flex flex-wrap gap-2">
                      {durationPresetValues.map((preset) => {
                        const isActive = duration === String(preset)
                        return (
                          <button
                            key={preset}
                            type="button"
                            onClick={() => setDuration(String(preset))}
                            style={{
                              fontFamily: 'var(--font-manrope), sans-serif',
                              fontSize: '0.75rem',
                              fontWeight: 700,
                              color: isActive ? '#6b5a35' : '#6f6a5c',
                              background: isActive ? '#e8ddc3' : '#efe7d6',
                              borderRadius: '999px',
                              border: 'none',
                              padding: '6px 11px',
                              cursor: 'pointer',
                            }}
                          >
                            {preset}{t.minuteShort}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <label htmlFor="pr-notes" style={microLabel}>{t.notes}</label>
                  <input id="pr-notes" value={practiceNotes} onChange={(e) => setPracticeNotes(e.target.value)} placeholder={t.optional} style={inputStyle} />
                </div>
              </div>

              {(practicePathData?.path?.steps?.length ?? 0) > 0 && (
                <div className="space-y-2">
                  <p style={microLabel}>{t.practiceStep}</p>
                  <div className="flex flex-wrap gap-2" role="group" aria-label="Practice step options">
                    <button
                      type="button"
                      onClick={() => setPracticeStepId('')}
                      aria-pressed={practiceStepId === ''}
                      style={{
                        fontFamily: 'var(--font-manrope), sans-serif',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: practiceStepId === '' ? '#6b5a35' : '#6f6a5c',
                        background: practiceStepId === '' ? '#e8ddc3' : '#efe7d6',
                        borderRadius: '999px',
                        border: 'none',
                        padding: '7px 12px',
                        cursor: 'pointer',
                      }}
                    >
                      {t.auto}
                    </button>
                    {practicePathData?.path?.steps?.map((step, index) => {
                      const value = String(index + 1)
                      const isActive = practiceStepId === value
                      return (
                        <button
                          key={step.step_id}
                          type="button"
                          onClick={() => setPracticeStepId(value)}
                          aria-pressed={isActive}
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            color: isActive ? '#6b5a35' : '#6f6a5c',
                            background: isActive ? '#e8ddc3' : '#efe7d6',
                            borderRadius: '999px',
                            border: 'none',
                            padding: '7px 12px',
                            cursor: 'pointer',
                          }}
                        >
                          {localizePracticeStepLabel(step.label)}
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}

              {selectedPracticeSkill && (
                <div
                  className="p-3"
                  role="status"
                  style={{
                    background: '#f5f0e4',
                    borderRadius: '0 10px 10px 10px',
                    color: '#6b5a35',
                  }}
                >
                  <p style={microLabel}>{t.pacingCue}</p>
                  <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', lineHeight: 1.5 }}>
                    {interpolate(t.pacingCueBody, { minutes: suggestedDurationValue })}
                  </p>
                </div>
              )}

              {practiceCelebration && (
                <div
                  className="p-3"
                  role="status"
                  style={{
                    background: '#e8f0e3',
                    borderRadius: '0 10px 10px 10px',
                    color: '#3a5c35',
                    animation: reduceMotion ? undefined : 'skillsLiftIn 180ms ease-out',
                  }}
                >
                  <p style={microLabel}>{t.sessionSaved}</p>
                  <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', lineHeight: 1.5 }}>
                    {interpolate(t.celebrationSummary, {
                      minutes: practiceCelebration.minutesDelta,
                      sessions: practiceCelebration.sessionDelta,
                      streak: practiceCelebration.streakDelta,
                    })}
                  </p>
                  {practiceCelebration.nextStepLabel && (
                    <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#465642', marginTop: '4px' }}>
                      {interpolate(t.nextUpPrefix, { step: localizePracticeStepLabel(practiceCelebration.nextStepLabel) })}
                    </p>
                  )}
                </div>
              )}

              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => setPracticeSkillId(null)}
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.8125rem',
                    fontWeight: 600,
                    color: '#5a6157',
                    background: '#f1f5eb',
                    border: 'none',
                    borderRadius: '100px',
                    padding: '10px 20px',
                    cursor: 'pointer',
                  }}
                >
                  {t.cancel}
                </button>
                <button
                  type="submit"
                  disabled={practiceMut.isPending}
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontWeight: 700,
                    fontSize: '0.875rem',
                    color: '#ffffff',
                    background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                    borderRadius: '100px',
                    padding: '12px 28px',
                    border: 'none',
                    cursor: 'pointer',
                    boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
                  }}
                >
                  {practiceMut.isPending ? t.logging : t.continuePractice}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteTarget && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          onClick={() => setDeleteTarget(null)}
          style={{
            background: 'rgba(46, 52, 43, 0.3)',
            backdropFilter: 'blur(4px)',
            WebkitBackdropFilter: 'blur(4px)',
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: '#ffffff',
              borderRadius: '0 16px 16px 16px',
              boxShadow: '0 16px 48px rgba(46, 52, 43, 0.12)',
              padding: '28px',
              maxWidth: '400px',
              width: 'calc(100% - 32px)',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
            }}
          >
            <h3
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: '1.125rem',
                fontWeight: 400,
                color: '#2e342b',
                letterSpacing: '-0.03em',
                margin: 0,
              }}
            >
              {t.deleteTitle}
            </h3>
            <p
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.875rem',
                color: '#5a6157',
                lineHeight: 1.6,
                margin: 0,
              }}
            >
              {interpolate(t.deleteBody, { name: deleteTarget.name })}
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
              <button
                type="button"
                onClick={() => setDeleteTarget(null)}
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  color: '#5a6157',
                  background: '#f1f5eb',
                  border: 'none',
                  borderRadius: '100px',
                  padding: '10px 20px',
                  cursor: 'pointer',
                }}
              >
                {t.deleteCancel}
              </button>
              <button
                type="button"
                onClick={() => {
                  deleteMut.mutate(deleteTarget.id)
                  setDeleteTarget(null)
                  setInsightsSkillId(null)
                }}
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.8125rem',
                  fontWeight: 700,
                  color: '#ffffff',
                  background: '#e8735c',
                  border: 'none',
                  borderRadius: '100px',
                  padding: '10px 20px',
                  cursor: 'pointer',
                  boxShadow: '0 4px 12px rgba(232, 115, 92, 0.25)',
                }}
              >
                {t.deleteConfirm}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes skillsCardReveal {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes skillsFadeSlide {
          from {
            opacity: 0;
            transform: translateY(4px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes skillsLiftIn {
          from {
            opacity: 0;
            transform: translateY(4px) scale(0.99);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        @keyframes skillsDotPulse {
          0% {
            transform: scale(1);
            box-shadow: 0 0 0 rgba(107, 90, 53, 0);
          }
          50% {
            transform: scale(1.15);
            box-shadow: 0 0 0 4px rgba(107, 90, 53, 0.12);
          }
          100% {
            transform: scale(1);
            box-shadow: 0 0 0 rgba(107, 90, 53, 0);
          }
        }
      `}</style>

    </div>
  )
}
