'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { habitsApi, type Habit, type CreateHabitInput } from '@/lib/api/habits'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import type { HabitsPageTranslations } from '@/lib/translations/app'
import { Repeat, Plus, X, Trash2, CheckCircle2, Flame, Undo2, Check, Clock } from 'lucide-react'
import { AlertDialog } from '@base-ui/react/alert-dialog'
import { HabitDetailPanel } from './_components/HabitDetailPanel'

type HabitStudioCopy = {
  habitStudio: string
  habitStudioTitle: string
  habitStudioSubtitle: string
  frequency: string
  scheduledTime: string
  hour: string
  minute: string
  am: string
  pm: string
  liveReflection: string
  yourNextRitual: string
  preview: string
  frequencyLabel: string
  ritualLabel: string
  timeLabel: string
  namePending: string
  timeNotSet: string
  timeCueHint: string
  affirmationTitleBase: string
  affirmationBodyBase: string
  affirmationTipBase: string
  affirmationTitleStrong: string
  affirmationBodyStrong: string
  affirmationTipStrong: string
  affirmationTitleNear: string
  affirmationBodyNear: string
  affirmationTipNeedsDescription: string
  affirmationTipNeedsTime: string
  signalActionFocusedName: string
  signalClearFrequency: string
  signalTimeCueEnabled: string
  signalContextDescription: string
  tipCelebrateStart: string
  tipCelebrateName: string
  tipTimeAnchorSet: string
  tipTimeAnchorMissing: string
  tipMeaningSet: string
  tipMeaningMissing: string
  tipConsistency: string
  showReflection: string
  hideReflection: string
}

const habitStudioCopy: Record<'en' | 'ko' | 'zh', HabitStudioCopy> = {
  en: {
    habitStudio: 'Habit Studio',
    habitStudioTitle: 'Design Your Next Ritual',
    habitStudioSubtitle: 'Keep it clear, kind, and repeatable. The right panel encourages you as you shape the ritual.',
    frequency: 'Frequency',
    scheduledTime: 'Preferred time',
    hour: 'Hour',
    minute: 'Minute',
    am: 'AM',
    pm: 'PM',
    liveReflection: 'Live Reflection',
    yourNextRitual: 'Your next ritual',
    preview: 'Preview',
    frequencyLabel: 'Frequency',
    ritualLabel: 'Ritual',
    timeLabel: 'Time',
    namePending: 'Name pending',
    timeNotSet: 'Not set yet',
    timeCueHint: 'Add a preferred time to activate smart cue messaging.',
    affirmationTitleBase: 'You are building something that can really stick.',
    affirmationBodyBase: 'Start simple and specific. Every small completion is evidence that you can trust your own rhythm.',
    affirmationTipBase: 'Tip: Use a clear action word so your next step feels obvious.',
    affirmationTitleStrong: 'Beautifully defined. You are ready to begin.',
    affirmationBodyStrong: 'You now have frequency, timing, and intent. This is how gentle structure turns into momentum.',
    affirmationTipStrong: 'Tip: Keep week one light. Winning early helps the habit stay.',
    affirmationTitleNear: 'Great foundation. One final detail will make it easier.',
    affirmationBodyNear: 'You are very close. Add one more cue so this ritual feels effortless to start.',
    affirmationTipNeedsDescription: 'Tip: Add one line about why this matters to you.',
    affirmationTipNeedsTime: 'Tip: Add a preferred time so your cue is easier to notice.',
    signalActionFocusedName: 'Action-focused name',
    signalClearFrequency: 'Clear frequency selected',
    signalTimeCueEnabled: 'Time cue enabled',
    signalContextDescription: 'Context in description',
    tipCelebrateStart: 'A gentle start is still a powerful start. Name the action you can return to this week.',
    tipCelebrateName: '{name} already sounds intentional. You are creating a rhythm with purpose.',
    tipTimeAnchorSet: 'Great anchor: {time}. Consistent timing makes follow-through easier.',
    tipTimeAnchorMissing: 'Add a preferred time to reduce decision fatigue and make this easier to keep.',
    tipMeaningSet: 'Your description adds meaning. Meaning is fuel on low-energy days.',
    tipMeaningMissing: 'Add one short reason. Purpose helps habits survive busy weeks.',
    tipConsistency: 'You do not need perfection. You only need to return to this rhythm again tomorrow.',
    showReflection: 'Show reflection',
    hideReflection: 'Hide reflection',
  },
  ko: {
    habitStudio: '습관 스튜디오',
    habitStudioTitle: '다음 리추얼을 설계해 보세요',
    habitStudioSubtitle: '구체적이고 부드럽게, 반복 가능하게 만들어 보세요. 오른쪽 패널이 입력에 맞춰 응원해 줍니다.',
    frequency: '빈도',
    scheduledTime: '선호 시간',
    hour: '시',
    minute: '분',
    am: '오전',
    pm: '오후',
    liveReflection: '실시간 리플렉션',
    yourNextRitual: '당신의 다음 리추얼',
    preview: '미리보기',
    frequencyLabel: '빈도',
    ritualLabel: '리추얼',
    timeLabel: '시간',
    namePending: '이름 입력 대기',
    timeNotSet: '아직 설정 안 함',
    timeCueHint: '선호 시간을 설정하면 스마트 알림 문구가 활성화됩니다.',
    affirmationTitleBase: '지속 가능한 좋은 흐름을 만들고 있어요.',
    affirmationBodyBase: '작고 분명하게 시작해 보세요. 작은 완료가 쌓일수록 스스로를 더 믿게 됩니다.',
    affirmationTipBase: '팁: 동사 중심 이름을 쓰면 바로 실행하기 쉬워요.',
    affirmationTitleStrong: '아주 좋아요. 시작할 준비가 되었어요.',
    affirmationBodyStrong: '빈도, 시간, 의도가 잘 갖춰졌어요. 이런 구조가 꾸준함을 만듭니다.',
    affirmationTipStrong: '팁: 첫 주는 가볍게. 초반 성공이 습관을 오래가게 해요.',
    affirmationTitleNear: '기반이 좋아요. 한 가지만 더하면 더 쉬워져요.',
    affirmationBodyNear: '거의 완성됐어요. 시작 장벽을 낮출 마지막 단서를 더해 보세요.',
    affirmationTipNeedsDescription: '팁: 왜 중요한지 한 줄만 적어 보세요.',
    affirmationTipNeedsTime: '팁: 선호 시간을 추가하면 시작 신호를 더 쉽게 알아차릴 수 있어요.',
    signalActionFocusedName: '행동 중심 이름',
    signalClearFrequency: '빈도 선택 완료',
    signalTimeCueEnabled: '시간 신호 활성화',
    signalContextDescription: '설명 맥락 포함',
    tipCelebrateStart: '작게 시작해도 충분히 강력해요. 이번 주에 돌아올 행동을 이름 붙여 보세요.',
    tipCelebrateName: '{name}이라는 이름이 이미 의도를 잘 담고 있어요. 좋은 리듬이 시작됐어요.',
    tipTimeAnchorSet: '{time} 앵커가 좋아요. 일정한 시간은 실행을 더 쉽게 만듭니다.',
    tipTimeAnchorMissing: '선호 시간을 추가하면 결정 피로를 줄이고 꾸준함을 높일 수 있어요.',
    tipMeaningSet: '설명이 의미를 더해줘요. 의미는 지친 날의 연료가 됩니다.',
    tipMeaningMissing: '짧은 이유를 한 줄 적어 보세요. 목적이 바쁜 주에도 습관을 지켜줘요.',
    tipConsistency: '완벽할 필요는 없어요. 내일 다시 돌아오면 충분해요.',
    showReflection: '리플렉션 보기',
    hideReflection: '리플렉션 숨기기',
  },
  zh: {
    habitStudio: '习惯工作室',
    habitStudioTitle: '设计你的下一个仪式',
    habitStudioSubtitle: '保持清晰、温和、可重复。右侧面板会根据你的输入实时鼓励你。',
    frequency: '频率',
    scheduledTime: '偏好时间',
    hour: '小时',
    minute: '分钟',
    am: '上午',
    pm: '下午',
    liveReflection: '实时反馈',
    yourNextRitual: '你的下一个仪式',
    preview: '预览',
    frequencyLabel: '频率',
    ritualLabel: '仪式',
    timeLabel: '时间',
    namePending: '待填写名称',
    timeNotSet: '尚未设置',
    timeCueHint: '添加偏好时间以启用智能时间提示。',
    affirmationTitleBase: '你正在建立一个真正能坚持下去的节奏。',
    affirmationBodyBase: '从简单且具体开始。每一次小完成，都会让你更相信自己的节奏。',
    affirmationTipBase: '提示：用清晰的动作词命名，更容易马上执行。',
    affirmationTitleStrong: '定义得很好，你已经可以开始了。',
    affirmationBodyStrong: '你已经具备频率、时间和意图。温和而稳定的结构会带来持续动力。',
    affirmationTipStrong: '提示：第一周保持轻量。早期成功最能帮助习惯留存。',
    affirmationTitleNear: '基础很稳，再补一个细节会更顺手。',
    affirmationBodyNear: '你已经很接近了。再加一个提示信号，让开始变得更轻松。',
    affirmationTipNeedsDescription: '提示：补上一句“为什么这件事重要”。',
    affirmationTipNeedsTime: '提示：添加偏好时间，让提示更容易被注意到。',
    signalActionFocusedName: '动作导向名称',
    signalClearFrequency: '已选择清晰频率',
    signalTimeCueEnabled: '时间提示已启用',
    signalContextDescription: '描述包含背景',
    tipCelebrateStart: '温和的开始同样有力量。先命名一个本周可重复的动作。',
    tipCelebrateName: '{name} 这个名称很有方向感，你正在建立有意图的节奏。',
    tipTimeAnchorSet: '很棒的时间锚点：{time}。固定时间会显著降低执行阻力。',
    tipTimeAnchorMissing: '加上偏好时间可减少决策疲劳，让坚持更容易。',
    tipMeaningSet: '这段描述赋予了意义。意义会在低能量时继续推动你。',
    tipMeaningMissing: '补一句简短理由。目的感能让习惯跨过忙碌周期。',
    tipConsistency: '不需要完美。明天再回到这个节奏，就已经在前进。',
    showReflection: '显示反馈',
    hideReflection: '收起反馈',
  },
}

/* ── HAB-002 — Relative date formatting ─────────────────────────────────── */

function formatRelativeDate(
  dateStr: string,
  t: HabitsPageTranslations,
): string {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const parsed = new Date(dateStr)
  const target = new Date(parsed.getFullYear(), parsed.getMonth(), parsed.getDate())
  const diffMs = today.getTime() - target.getTime()
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return t.today
  if (diffDays === 1) return t.yesterday
  if (diffDays >= 2 && diffDays <= 7) return `${diffDays} ${t.daysAgo}`

  const month = target.toLocaleString('en-US', { month: 'short' })
  const day = target.getDate()
  if (diffDays <= 365) return `${month} ${day}`

  return `${month} ${day}, ${target.getFullYear()}`
}

/* ── HAB-012 — Time-aware cue logic ────────────────────────────────────── */

function formatTimeDelta(minutes: number): string {
  const h = Math.floor(Math.abs(minutes) / 60)
  const m = Math.abs(minutes) % 60
  if (h === 0) return `${m}m`
  if (m === 0) return `${h}h`
  return `${h}h ${m}m`
}

function getTimeCue(
  scheduledTime: string | null,
  completedToday: boolean,
  t: HabitsPageTranslations,
): { text: string; color: string } | null {
  if (!scheduledTime || completedToday) return null
  const now = new Date()
  const [hh, mm] = scheduledTime.split(':').map(Number)
  const scheduled = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hh, mm)
  const diffMin = Math.round((scheduled.getTime() - now.getTime()) / 60000)

  if (diffMin > 30) {
    return { text: t.dueIn.replace('{time}', formatTimeDelta(diffMin)), color: '#5a6157' }
  }
  if (diffMin >= 0) {
    return { text: t.dueSoon, color: '#b8860b' }
  }
  return { text: t.overdue.replace('{time}', formatTimeDelta(diffMin)), color: '#e8735c' }
}

function titleCase(input: string): string {
  return input
    .split(/\s+/)
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

function normalizeTimeInput(time24: string): string {
  const m = /^(\d{2}):(\d{2})$/.exec(time24)
  if (!m) return ''
  const hh = Number(m[1])
  const mm = Number(m[2])
  if (!Number.isFinite(hh) || !Number.isFinite(mm)) return ''
  if (hh < 0 || hh > 23 || mm < 0 || mm > 59) return ''
  return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`
}

function formatTimeForPreview(time24: string, modalCopy: HabitStudioCopy): string {
  const normalized = normalizeTimeInput(time24)
  if (!normalized) return modalCopy.timeNotSet
  const [hRaw, mRaw] = normalized.split(':')
  const h = Number(hRaw)
  const m = Number(mRaw)
  const meridiem: 'AM' | 'PM' = h >= 12 ? 'PM' : 'AM'
  const hour12 = h % 12 === 0 ? 12 : h % 12
  return `${String(hour12).padStart(2, '0')}:${String(m).padStart(2, '0')} ${meridiem === 'AM' ? modalCopy.am : modalCopy.pm}`
}

/* ── Shared style constants ─────────────────────────────────────────────── */

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

function containsCjk(text: string): boolean {
  return /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]/.test(text)
}

function getMicroLabelStyle(label: string, accent = '#767d72'): React.CSSProperties {
  if (containsCjk(label)) {
    return {
      ...microLabel,
      textTransform: 'none',
      fontSize: '0.75rem',
      letterSpacing: '0.02em',
      color: accent,
    }
  }

  return { ...microLabel, color: accent }
}

export default function HabitsPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).habits
  const studio = habitStudioCopy[lang as 'en' | 'ko' | 'zh'] ?? habitStudioCopy.en
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [scheduleType, setScheduleType] = useState('daily')
  const [scheduledTimeInput, setScheduledTimeInput] = useState('')
  const [isCompactViewport, setIsCompactViewport] = useState(false)
  const [mobileReflectionOpen, setMobileReflectionOpen] = useState(false)
  const [tipIdx, setTipIdx] = useState(0)
  const [tipFade, setTipFade] = useState(true)
  const [reduceMotion, setReduceMotion] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Habit | null>(null)
  const [selectedHabitId, setSelectedHabitId] = useState<number | null>(null)
  const [mobileDetailOpen, setMobileDetailOpen] = useState(false)
  const [drawerOffsetY, setDrawerOffsetY] = useState(0)
  const [drawerDragging, setDrawerDragging] = useState(false)
  const [drawerClosing, setDrawerClosing] = useState(false)
  const drawerPointerId = useRef<number | null>(null)
  const drawerDragStartY = useRef<number | null>(null)
  const drawerStartScrollTop = useRef(0)
  const drawerLastY = useRef<number | null>(null)
  const drawerLastTs = useRef<number | null>(null)
  const drawerVelocityY = useRef(0)
  const drawerCloseTimer = useRef<number | null>(null)

  useEffect(() => {
    if (!mobileDetailOpen) {
      setDrawerDragging(false)
      drawerDragStartY.current = null
      drawerStartScrollTop.current = 0
      drawerLastY.current = null
      drawerLastTs.current = null
      drawerVelocityY.current = 0
      if (drawerCloseTimer.current != null) {
        window.clearTimeout(drawerCloseTimer.current)
        drawerCloseTimer.current = null
      }
    }
  }, [mobileDetailOpen])

  useEffect(() => {
    return () => {
      if (drawerCloseTimer.current != null) {
        window.clearTimeout(drawerCloseTimer.current)
      }
    }
  }, [])

  useEffect(() => {
    if (!showForm) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setShowForm(false)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [showForm])

  useEffect(() => {
    const media = window.matchMedia('(max-width: 1023px)')
    const apply = () => setIsCompactViewport(media.matches)
    apply()
    media.addEventListener('change', apply)
    return () => media.removeEventListener('change', apply)
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const apply = () => setReduceMotion(media.matches)
    apply()
    media.addEventListener('change', apply)
    return () => media.removeEventListener('change', apply)
  }, [])

  useEffect(() => {
    if (!showForm) return
    setMobileReflectionOpen(!isCompactViewport)
  }, [showForm, isCompactViewport])

  const { data, isLoading } = useQuery({
    queryKey: ['habits'],
    queryFn: () => habitsApi.list(),
  })
  const habits = data?.habits ?? []

  const createMut = useMutation({
    mutationFn: (input: CreateHabitInput) => habitsApi.create(input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['habits'] })
      setShowForm(false)
      setName('')
      setDescription('')
      setScheduledTimeInput('')
      setTipIdx(0)
      setTipFade(true)
    },
  })

  /* HAB-010 — Animation state: track which habit just got logged */
  const [justLogged, setJustLogged] = useState<Set<number>>(new Set())
  const [celebrateId, setCelebrateId] = useState<number | null>(null)
  const prevStreaks = useRef<Map<number, number>>(new Map())

  // Snapshot streaks before mutation so we can detect milestone crossings
  const snapshotStreaks = useCallback(() => {
    const map = new Map<number, number>()
    for (const h of habits) map.set(h.id, h.current_streak)
    prevStreaks.current = map
  }, [habits])

  const checkMilestone = useCallback((habitId: number) => {
    const prev = prevStreaks.current.get(habitId) ?? 0
    const updated = habits.find((h) => h.id === habitId)
    const next = updated ? updated.current_streak : prev + 1
    for (const m of [7, 30, 100]) {
      if (next >= m && prev < m) {
        setCelebrateId(habitId)
        setTimeout(() => setCelebrateId(null), 2000)
        return
      }
    }
  }, [habits])

  const logMut = useMutation({
    mutationFn: (habitId: number) => {
      snapshotStreaks()
      return habitsApi.log(habitId, {})
    },
    onSuccess: (_data, habitId) => {
      setJustLogged((s) => new Set(s).add(habitId))
      setTimeout(() => setJustLogged((s) => { const n = new Set(s); n.delete(habitId); return n }), 600)
      qc.invalidateQueries({ queryKey: ['habits'] }).then(() => checkMilestone(habitId))
    },
  })

  const undoLogMut = useMutation({
    mutationFn: (logId: number) => habitsApi.deleteLog(logId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['habits'] }),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => habitsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['habits'] }),
  })

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    const scheduledTime = normalizeTimeInput(scheduledTimeInput)
    createMut.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
      schedule_type: scheduleType,
      scheduled_time: scheduledTime || undefined,
    })
  }

  function openMobileDetail(habitId: number) {
    setSelectedHabitId(habitId)
    setDrawerClosing(false)
    setDrawerOffsetY(0)
    setMobileDetailOpen(true)
  }

  function handleDrawerPointerDown(e: React.PointerEvent<HTMLDivElement>) {
    drawerPointerId.current = e.pointerId
    drawerDragStartY.current = e.clientY
    drawerStartScrollTop.current = e.currentTarget.scrollTop
    drawerLastY.current = e.clientY
    drawerLastTs.current = e.timeStamp
    drawerVelocityY.current = 0
    setDrawerDragging(false)
  }

  function handleDrawerPointerMove(e: React.PointerEvent<HTMLDivElement>) {
    if (drawerDragStartY.current == null) return
    if (drawerPointerId.current !== e.pointerId) return
    const delta = e.clientY - drawerDragStartY.current

    // Only begin dragging the sheet if content is at top and gesture is downward.
    if (!drawerDragging) {
      if (delta <= 6) return
      if (drawerStartScrollTop.current > 0 || e.currentTarget.scrollTop > 0) return
      e.currentTarget.setPointerCapture(e.pointerId)
      setDrawerDragging(true)
    }

    const positiveDelta = Math.max(0, delta)
    const resisted = positiveDelta <= 120
      ? positiveDelta * 0.9
      : 108 + (positiveDelta - 120) * 0.35
    setDrawerOffsetY(resisted)

    if (drawerLastY.current != null && drawerLastTs.current != null) {
      const dy = e.clientY - drawerLastY.current
      const dt = e.timeStamp - drawerLastTs.current
      if (dt > 0) {
        drawerVelocityY.current = dy / dt
      }
    }
    drawerLastY.current = e.clientY
    drawerLastTs.current = e.timeStamp
  }

  function handleDrawerPointerUp(e: React.PointerEvent<HTMLDivElement>) {
    if (drawerPointerId.current !== e.pointerId) return
    if (e.currentTarget.hasPointerCapture(e.pointerId)) {
      e.currentTarget.releasePointerCapture(e.pointerId)
    }

    if (!drawerDragging) {
      drawerPointerId.current = null
      drawerDragStartY.current = null
      drawerStartScrollTop.current = 0
      drawerLastY.current = null
      drawerLastTs.current = null
      drawerVelocityY.current = 0
      return
    }

    setDrawerDragging(false)
    drawerPointerId.current = null
    const shouldCloseByDistance = drawerOffsetY > 95
    const shouldCloseByFlick = drawerVelocityY.current > 0.65
    if (shouldCloseByDistance || shouldCloseByFlick) {
      requestDrawerClose()
      return
    }
    setDrawerOffsetY(0)
    drawerDragStartY.current = null
    drawerStartScrollTop.current = 0
    drawerLastY.current = null
    drawerLastTs.current = null
    drawerVelocityY.current = 0
  }

  function requestDrawerClose() {
    if (!mobileDetailOpen || drawerClosing) return
    setDrawerDragging(false)
    setDrawerClosing(true)
    setDrawerOffsetY(typeof window !== 'undefined' ? Math.round(window.innerHeight * 0.95) : 900)
    if (drawerCloseTimer.current != null) {
      window.clearTimeout(drawerCloseTimer.current)
    }
    drawerCloseTimer.current = window.setTimeout(() => {
      setMobileDetailOpen(false)
      drawerCloseTimer.current = null
    }, 240)
  }

  const habitName = name.trim()
  const hasName = habitName.length > 0
  const hasDescription = description.trim().length > 0
  const scheduledTime = normalizeTimeInput(scheduledTimeInput)
  const hasScheduledTime = scheduledTime.length > 0
  const frequencyLabel = scheduleType === 'weekly' ? t.weekly : scheduleType === 'custom' ? t.custom : t.daily
  const scheduledTimeLabel = formatTimeForPreview(scheduledTime, studio)
  const dynamicCue = getTimeCue(scheduledTime || null, false, t)
  const reflectionExpanded = !isCompactViewport || mobileReflectionOpen

  const refinementSignals = [
    { label: studio.signalActionFocusedName, ready: /\b(read|walk|drink|write|practice|stretch|meditate|plan|review|sleep|run|code|study|journal|gym)\b/i.test(habitName) || habitName.length >= 10 },
    { label: studio.signalClearFrequency, ready: Boolean(scheduleType) },
    { label: studio.signalTimeCueEnabled, ready: hasScheduledTime },
    { label: studio.signalContextDescription, ready: hasDescription },
  ]
  const readinessScore = refinementSignals.filter((s) => s.ready).length

  let affirmationTitle = studio.affirmationTitleBase
  let affirmationBody = studio.affirmationBodyBase
  let affirmationTip = studio.affirmationTipBase

  if (readinessScore >= 4) {
    affirmationTitle = studio.affirmationTitleStrong
    affirmationBody = studio.affirmationBodyStrong
    affirmationTip = studio.affirmationTipStrong
  } else if (readinessScore === 3) {
    affirmationTitle = studio.affirmationTitleNear
    affirmationBody = studio.affirmationBodyNear
    affirmationTip = hasScheduledTime
      ? studio.affirmationTipNeedsDescription
      : studio.affirmationTipNeedsTime
  }

  const rotatingTips = [
    hasName
      ? studio.tipCelebrateName.replace('{name}', titleCase(habitName))
      : studio.tipCelebrateStart,
    hasScheduledTime
      ? studio.tipTimeAnchorSet.replace('{time}', scheduledTimeLabel)
      : studio.tipTimeAnchorMissing,
    hasDescription
      ? studio.tipMeaningSet
      : studio.tipMeaningMissing,
    studio.tipConsistency,
  ]
  const activeTip = rotatingTips[tipIdx % rotatingTips.length]

  useEffect(() => {
    if (!showForm) return
    setTipIdx(0)
    setTipFade(true)
    let timeoutId: ReturnType<typeof setTimeout> | null = null
    const timer = setInterval(() => {
      setTipFade(false)
      timeoutId = setTimeout(() => {
        setTipIdx((i) => (i + 1) % rotatingTips.length)
        setTipFade(true)
      }, 300)
    }, 5000)

    return () => {
      clearInterval(timer)
      if (timeoutId !== null) clearTimeout(timeoutId)
    }
  }, [showForm, rotatingTips.length])

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '32px',
        padding: '4px',
      }}
    >
      {/* ── Page header ─────────────────────────────────────── (HAB-008: 32px gap) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#3a5272',
          }}
        >
          {t.eyebrow}
        </p>
        <h1
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '2rem',
            fontWeight: 300,
            color: '#3a5272',
            letterSpacing: '-0.03em',
          }}
        >
          {t.title}
        </h1>
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.9375rem',
            color: '#5a6157',
            lineHeight: 1.65,
          }}
        >
          {t.subtitle}
        </p>
        {/* Mobile-only: New Habit button in header for thumb reach */}
        <button
          onClick={() => setShowForm((v) => !v)}
          className="flex items-center gap-2 sm:hidden"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontWeight: 700,
            fontSize: '0.8125rem',
            color: '#ffffff',
            background: 'linear-gradient(135deg, #3a5272, #2e4460)',
            borderRadius: '100px',
            minHeight: '44px',
            padding: '0 20px',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(58, 82, 114, 0.18)',
            alignSelf: 'flex-start',
            marginTop: '8px',
          }}
        >
          {showForm ? <><X size={14} /> {t.cancel}</> : <><Plus size={14} /> {t.newHabit}</>}
        </button>
      </div>

      {/* ── HAB-007: Master-detail split layout ──────────────── */}
      <div className="flex gap-6">
      {/* ── Left panel: Habits list ───────────────────────── */}
      <div className="w-full lg:w-[60%]">
      <div
        style={{
          background: 'linear-gradient(160deg, #f6f9fc 0%, #ffffff 100%)',
          borderRadius: '0 16px 16px 16px',
          boxShadow: '0 10px 26px rgba(46, 52, 43, 0.07)',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
        }}
      >
        {/* HAB-009 — Section header + desktop New Habit button on same row */}
        <div className="flex items-center justify-between">
          <p
            style={getMicroLabelStyle(t.yourHabits, '#3a5272')}
          >
            {t.yourHabits}
          </p>
          {/* Desktop-only: button inside card, spatially connected to content */}
          <button
            onClick={() => setShowForm((v) => !v)}
            className="hidden sm:flex items-center gap-2"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontWeight: 700,
              fontSize: '0.75rem',
              color: '#ffffff',
              background: 'linear-gradient(135deg, #3a5272, #2e4460)',
              borderRadius: '100px',
              minHeight: '44px',
              padding: '0 16px',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(58, 82, 114, 0.18)',
            }}
          >
            {showForm ? <><X size={12} /> {t.cancel}</> : <><Plus size={12} /> {t.newHabit}</>}
          </button>
        </div>

        {isLoading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse" style={{ height: '64px', borderRadius: '0 12px 12px 12px', background: '#e4edf5' }} />
            ))}
          </div>
        )}

        {/* HAB-011 — Motivational empty state */}
        {!isLoading && habits.length === 0 && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '16px',
              padding: '48px 24px',
            }}
          >
            {/* Botanical illustration placeholder — leaf ring */}
            <div
              style={{
                width: '72px',
                height: '72px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #edf2f8, #d6e3f0)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Repeat size={28} style={{ color: '#3a5272' }} />
            </div>
            <h3
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: '1.25rem',
                fontWeight: 400,
                color: '#3a5272',
                letterSpacing: '-0.03em',
                textAlign: 'center',
              }}
            >
              {t.emptyTitle}
            </h3>
            <p
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.875rem',
                color: '#5a6157',
                lineHeight: 1.65,
                textAlign: 'center',
                maxWidth: '360px',
              }}
            >
              {t.emptyBody}
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2"
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontWeight: 700,
                fontSize: '0.875rem',
                color: '#ffffff',
                background: 'linear-gradient(135deg, #3a5272, #2e4460)',
                borderRadius: '100px',
                padding: '12px 28px',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 4px 20px rgba(58, 82, 114, 0.18)',
                marginTop: '8px',
              }}
            >
              <Plus size={14} /> {t.emptyAction}
            </button>
          </div>
        )}

        {habits.length > 0 && (
          <ul style={{ display: 'flex', flexDirection: 'column', gap: '16px', listStyle: 'none', margin: 0, padding: 0 }}>
            {habits.map((h: Habit, habitIndex) => (
              <li
                key={h.id}
                onClick={() => {
                  if (typeof window !== 'undefined' && window.matchMedia('(max-width: 1023px)').matches) {
                    openMobileDetail(h.id)
                    return
                  }
                  setSelectedHabitId(h.id)
                }}
                style={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '16px',
                  padding: '16px 24px',
                  borderRadius: '0 12px 12px 12px',
                  background: selectedHabitId === h.id ? '#e7eff8' : h.completed_today ? '#e8efe3' : '#f3f7fb',
                  borderLeft: selectedHabitId === h.id
                    ? '2.5px solid #3a5272'
                    : h.completed_today
                    ? '2.5px solid #4b6646'
                    : '2.5px solid transparent',
                  cursor: 'pointer',
                  opacity: reduceMotion ? 1 : 0,
                  animation: reduceMotion ? undefined : 'habitCardReveal 260ms ease-out forwards',
                  animationDelay: reduceMotion ? undefined : `${habitIndex * 35}ms`,
                }}
              >
                {/* HAB-010 — Milestone celebration ring */}
                {celebrateId === h.id && !reduceMotion && <div className="celebrate-ring" />}
                <div style={{ minWidth: 0, flex: 1 }}>
                  <div className="flex items-center" style={{ gap: '8px' }}>
                    <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>
                      {h.name}
                    </p>
                    <button
                      type="button"
                      className="lg:hidden"
                      onClick={(e) => {
                        e.stopPropagation()
                        openMobileDetail(h.id)
                      }}
                      style={{
                        fontFamily: 'var(--font-manrope), sans-serif',
                        fontSize: '0.625rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        color: '#3a5272',
                        background: '#e4edf5',
                        border: 'none',
                        borderRadius: '100px',
                        minHeight: '28px',
                        padding: '0 10px',
                        cursor: 'pointer',
                      }}
                    >
                      Details
                    </button>
                    {/* HAB-001 — Streak badge with flame icon (4-tier milestone escalation) */}
                    {h.current_streak > 0 && (() => {
                      const s = h.current_streak
                      const tier = s >= 100
                        ? { bg: '#fef3e2', color: '#8b6914', flame: 14, glow: '0 0 8px rgba(184,134,11,0.2)' }
                        : s >= 30
                        ? { bg: '#fce8e4', color: '#8b4a3a', flame: 14, glow: 'none' }
                        : s >= 7
                        ? { bg: '#fef3e2', color: '#b8860b', flame: 12, glow: 'none' }
                        : { bg: '#f0f2ec', color: '#5a6157', flame: 10, glow: 'none' }
                      return (
                        <span
                          className="flex items-center"
                          style={{
                            gap: '3px',
                            padding: '2px 8px',
                            background: tier.bg,
                            color: tier.color,
                            borderRadius: '100px',
                            fontSize: '0.625rem',
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontWeight: 700,
                            whiteSpace: 'nowrap',
                            letterSpacing: '0.02em',
                            boxShadow: tier.glow,
                          }}
                        >
                          <Flame size={tier.flame} /> {s} {t.dayStreak}
                        </span>
                      )
                    })()}
                    {h.completed_today && (
                      <span
                        className="flex items-center"
                        style={{
                          gap: '4px',
                          padding: '2px 8px',
                          background: '#d6e8ce',
                          color: '#465642',
                          borderRadius: '100px',
                          fontSize: '0.625rem',
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        <CheckCircle2 size={10} /> {t.done}
                      </span>
                    )}
                  </div>
                  {/* HAB-005 — 7-day completion dot row */}
                  {h.last_7_days && h.last_7_days.length > 0 && (
                    <div className="flex items-center" style={{ gap: '6px', marginTop: '8px' }}>
                      {h.last_7_days.map((day) => {
                        const isToday = day.date === new Date().toISOString().slice(0, 10)
                        return (
                          <span
                            key={day.date}
                            title={day.date}
                            style={{
                              width: '8px',
                              height: '8px',
                              borderRadius: '50%',
                              background: day.logged
                                ? '#4b6646'
                                : isToday
                                ? 'transparent'
                                : '#dee5d7',
                              border: isToday && !day.logged
                                ? '1.5px solid #4b6646'
                                : '1.5px solid transparent',
                              animation: isToday && !day.logged && !reduceMotion ? 'dot-pulse 2s ease-in-out infinite' : 'none',
                              flexShrink: 0,
                            }}
                          />
                        )
                      })}
                    </div>
                  )}
                  <div
                    className="flex flex-wrap items-center justify-between"
                    style={{
                      marginTop: '8px',
                      gap: '10px',
                    }}
                  >
                    <div
                      className="flex flex-wrap items-center"
                      style={{
                        fontFamily: 'var(--font-manrope), sans-serif',
                        fontSize: '0.75rem',
                        color: '#767d72',
                        gap: '12px',
                      }}
                    >
                      <span className="flex items-center" style={{ gap: '4px' }}><Repeat size={11} /> {h.schedule_type}</span>
                      <span>{h.count} {t.logged}</span>
                      {/* HAB-006 — Completion rate percentage */}
                      {h.completion_rate_30d != null && (
                        <span>{Math.round(h.completion_rate_30d * 100)}% {t.thisMonth}</span>
                      )}
                    </div>

                    <div className="flex items-center shrink-0" style={{ gap: '8px' }}>
                      {/* HAB-010 — Checkmark pop on successful log */}
                      {justLogged.has(h.id) && (
                        <span className={reduceMotion ? undefined : 'check-pop'} style={{ color: '#4b6646', display: 'flex' }}>
                          <CheckCircle2 size={24} />
                        </span>
                      )}
                      {/* HAB-003 / HAB-004 — LOG button transforms to Undo when completed today */}
                      {justLogged.has(h.id) ? null : h.completed_today && h.today_log_id ? (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            undoLogMut.mutate(h.today_log_id!)
                          }}
                          disabled={undoLogMut.isPending}
                          className="habit-log-btn"
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            textTransform: 'uppercase' as const,
                            letterSpacing: '0.05em',
                            minHeight: '44px',
                            padding: '0 20px',
                            borderRadius: '100px',
                            border: '1.5px solid rgba(58, 82, 114, 0.25)',
                            cursor: 'pointer',
                            color: '#3a5272',
                            background: 'transparent',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                          }}
                        >
                          <Undo2 size={12} /> {t.undo}
                        </button>
                      ) : h.completed_today ? (
                        <span
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            textTransform: 'uppercase' as const,
                            letterSpacing: '0.05em',
                            minHeight: '44px',
                            padding: '0 20px',
                            borderRadius: '100px',
                            border: '1.5px solid rgba(75, 102, 70, 0.25)',
                            color: '#4b6646',
                            background: 'rgba(75, 102, 70, 0.08)',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '6px',
                          }}
                          aria-live="polite"
                        >
                          <CheckCircle2 size={12} /> {t.done}
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            logMut.mutate(h.id)
                          }}
                          disabled={logMut.isPending}
                          className="habit-log-btn"
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            textTransform: 'uppercase' as const,
                            letterSpacing: '0.05em',
                            minHeight: '44px',
                            padding: '0 20px',
                            borderRadius: '100px',
                            border: 'none',
                            cursor: 'pointer',
                            color: '#ffffff',
                            background: 'linear-gradient(135deg, #3a5272, #2e4460)',
                            boxShadow: '0 4px 12px rgba(58, 82, 114, 0.25)',
                            transition: 'transform 180ms ease, box-shadow 180ms ease, background 180ms ease',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                          }}
                          onMouseEnter={(e) => {
                            if (reduceMotion) return
                            e.currentTarget.style.transform = 'translateY(-1px)'
                            e.currentTarget.style.boxShadow = '0 6px 16px rgba(58, 82, 114, 0.3)'
                          }}
                          onMouseLeave={(e) => {
                            if (reduceMotion) return
                            e.currentTarget.style.transform = 'translateY(0)'
                            e.currentTarget.style.boxShadow = '0 4px 12px rgba(58, 82, 114, 0.25)'
                          }}
                          onMouseDown={(e) => {
                            if (reduceMotion) return
                            e.currentTarget.style.transform = 'scale(0.97)'
                          }}
                          onMouseUp={(e) => {
                            if (reduceMotion) return
                            e.currentTarget.style.transform = 'translateY(-1px)'
                          }}
                        >
                          <Check size={14} /> {t.log}
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation()
                          setDeleteTarget(h)
                        }}
                        className="transition-all duration-200"
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: '#adb4a8',
                          padding: '8px',
                          borderRadius: '100px',
                        }}
                        onMouseEnter={(e) => { e.currentTarget.style.color = '#e8735c'; e.currentTarget.style.background = 'rgba(232, 115, 92, 0.08)' }}
                        onMouseLeave={(e) => { e.currentTarget.style.color = '#adb4a8'; e.currentTarget.style.background = 'none' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  <div
                    className="flex flex-wrap items-center"
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.75rem',
                      color: '#767d72',
                      marginTop: '8px',
                      gap: '12px',
                    }}
                  >
                    {/* HAB-002 — Relative date instead of raw GMT string */}
                    {h.last_logged_date && (
                      <span>{formatRelativeDate(h.last_logged_date, t)}</span>
                    )}
                    {/* HAB-012 — Time-aware cue */}
                    {(() => {
                      const cue = getTimeCue(h.scheduled_time, h.completed_today, t)
                      if (!cue) return null
                      return (
                        <span className="flex items-center" style={{ gap: '4px', color: cue.color, fontWeight: 600 }}>
                          <Clock size={11} /> {cue.text}
                        </span>
                      )
                    })()}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      </div>{/* end left panel */}

      {/* ── Right panel: Detail (desktop only) ────────────── */}
      <div className="hidden lg:block lg:w-[40%]">
        <HabitDetailPanel
          habit={habits.find((h) => h.id === selectedHabitId) ?? null}
          t={{
            detailTitle: t.detailTitle,
            currentStreak: t.currentStreak,
            longestStreak: t.longestStreak,
            completionRate: t.completionRate,
            totalLogs: t.totalLogs,
            last30Days: t.last30Days,
            yearlyHeatmap: t.yearlyHeatmap,
            selectHabit: t.selectHabit,
            days: t.days,
            noData: t.noData,
          }}
          onUpdated={() => {
            qc.invalidateQueries({ queryKey: ['habits'] })
          }}
        />
      </div>
      </div>{/* end split container */}

      {/* Mobile detail drawer */}
      <AlertDialog.Root
        open={mobileDetailOpen && selectedHabitId !== null}
        onOpenChange={(open) => {
          if (open) {
            setDrawerClosing(false)
            setDrawerOffsetY(0)
            setMobileDetailOpen(true)
            return
          }
          requestDrawerClose()
        }}
      >
        <AlertDialog.Portal>
          <AlertDialog.Backdrop
            className="lg:hidden"
            onPointerDown={requestDrawerClose}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(46, 52, 43, 0.32)',
              backdropFilter: 'blur(4px)',
              WebkitBackdropFilter: 'blur(4px)',
              zIndex: 52,
            }}
          />
          <AlertDialog.Popup
            className="lg:hidden"
            onPointerDown={handleDrawerPointerDown}
            onPointerMove={handleDrawerPointerMove}
            onPointerUp={handleDrawerPointerUp}
            onPointerCancel={handleDrawerPointerUp}
            style={{
              position: 'fixed',
              left: '0',
              right: '0',
              bottom: '0',
              zIndex: 53,
              maxHeight: '86vh',
              overflowY: 'auto',
              padding: '16px',
              background: '#f8faf2',
              borderRadius: '16px 16px 0 0',
              boxShadow: '0 -10px 28px rgba(46, 52, 43, 0.18)',
              transform: `translateY(${drawerOffsetY}px)`,
              transition: drawerDragging ? 'none' : 'transform 240ms cubic-bezier(0.22, 1, 0.36, 1)',
            }}
          >
            <div
              aria-hidden="true"
              style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: '20px',
                marginBottom: '6px',
                userSelect: 'none',
                cursor: drawerDragging ? 'grabbing' : 'grab',
              }}
            >
              <div
                style={{
                  width: '44px',
                  height: '4px',
                  borderRadius: '100px',
                  background: 'rgba(118, 125, 114, 0.4)',
                }}
              />
            </div>
            <HabitDetailPanel
              habit={habits.find((h) => h.id === selectedHabitId) ?? null}
              sticky={false}
              t={{
                detailTitle: t.detailTitle,
                currentStreak: t.currentStreak,
                longestStreak: t.longestStreak,
                completionRate: t.completionRate,
                totalLogs: t.totalLogs,
                last30Days: t.last30Days,
                yearlyHeatmap: t.yearlyHeatmap,
                selectHabit: t.selectHabit,
                days: t.days,
                noData: t.noData,
              }}
              onUpdated={() => {
                qc.invalidateQueries({ queryKey: ['habits'] })
              }}
            />
          </AlertDialog.Popup>
        </AlertDialog.Portal>
      </AlertDialog.Root>

      {/* HAB-022 — Delete confirmation dialog */}
      <AlertDialog.Root open={deleteTarget !== null} onOpenChange={(open) => { if (!open) setDeleteTarget(null) }}>
        <AlertDialog.Portal>
          <AlertDialog.Backdrop
            onClick={() => setDeleteTarget(null)}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(46, 52, 43, 0.3)',
              backdropFilter: 'blur(4px)',
              WebkitBackdropFilter: 'blur(4px)',
              zIndex: 50,
            }}
          />
          <AlertDialog.Popup
            style={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 51,
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
            <AlertDialog.Title
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
            </AlertDialog.Title>
            <AlertDialog.Description
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.875rem',
                color: '#5a6157',
                lineHeight: 1.6,
                margin: 0,
              }}
            >
              {t.deleteBody.replace('{name}', deleteTarget?.name ?? '')}
            </AlertDialog.Description>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
              <AlertDialog.Close
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
              </AlertDialog.Close>
              <button
                type="button"
                onClick={() => {
                  if (deleteTarget) {
                    deleteMut.mutate(deleteTarget.id)
                    setDeleteTarget(null)
                  }
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
          </AlertDialog.Popup>
        </AlertDialog.Portal>
      </AlertDialog.Root>

      {/* Habit Studio Modal */}
      {showForm && (
        <div
          role="dialog"
          aria-modal="true"
          onClick={() => setShowForm(false)}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 70,
            background: 'rgba(22, 33, 49, 0.44)',
            backdropFilter: 'blur(6px)',
            WebkitBackdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: 'min(1040px, 100%)',
              maxHeight: 'calc(100vh - 40px)',
              overflowY: 'auto',
              background: '#ffffff',
              borderRadius: '0 18px 18px 18px',
              boxShadow: '0 24px 60px rgba(46, 52, 43, 0.12)',
              padding: '24px',
              position: 'relative',
            }}
          >
            <div className="grid grid-cols-1 lg:grid-cols-5" style={{ gap: '20px' }}>
              <form
                onSubmit={handleCreate}
                className="lg:col-span-3"
                style={{
                  background: '#ffffff',
                  borderRadius: '0 16px 16px 16px',
                  padding: isCompactViewport ? '4px' : '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: isCompactViewport ? '14px' : '20px',
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <p style={{ ...microLabel, color: '#3a5272' }}>{studio.habitStudio}</p>
                  <h2
                    style={{
                      fontFamily: 'var(--font-serif), Georgia, serif',
                      fontSize: isCompactViewport ? '1.45rem' : '1.6rem',
                      fontWeight: 300,
                      color: '#3a5272',
                      letterSpacing: '-0.03em',
                    }}
                  >
                    {studio.habitStudioTitle}
                  </h2>
                  <p
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: isCompactViewport ? '0.8125rem' : '0.875rem',
                      lineHeight: 1.65,
                      color: '#5a6157',
                    }}
                  >
                    {studio.habitStudioSubtitle}
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2" style={{ gap: '16px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label htmlFor="h-name" style={microLabel}>{t.name}</label>
                    <input
                      id="h-name"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder={t.namePlaceholder}
                      style={inputStyle}
                    />
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label htmlFor="h-sched" style={microLabel}>{studio.frequency}</label>
                    <select
                      id="h-sched"
                      value={scheduleType}
                      onChange={(e) => setScheduleType(e.target.value)}
                      style={{
                        ...inputStyle,
                        appearance: 'none' as const,
                        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23767d72' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
                        backgroundRepeat: 'no-repeat',
                        backgroundPosition: 'right 14px center',
                        paddingRight: '36px',
                      }}
                    >
                      <option value="daily">{t.daily}</option>
                      <option value="weekly">{t.weekly}</option>
                      <option value="custom">{t.custom}</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2" style={{ gap: '16px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label htmlFor="h-scheduled-time" style={microLabel}>{studio.scheduledTime}</label>
                    <div
                      style={{
                        background: '#ffffff',
                        border: '1px solid rgba(173, 180, 168, 0.20)',
                        borderRadius: '10px',
                        padding: '10px 12px',
                      }}
                    >
                      <input
                        id="h-scheduled-time"
                        type="time"
                        value={scheduledTimeInput}
                        onChange={(e) => setScheduledTimeInput(e.target.value)}
                        style={{
                          ...inputStyle,
                          border: 'none',
                          borderRadius: '0',
                          padding: 0,
                          background: 'transparent',
                          minHeight: '44px',
                        }}
                      />
                    </div>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label htmlFor="h-desc" style={microLabel}>{t.description}</label>
                    <input
                      id="h-desc"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder={t.optional}
                      style={inputStyle}
                    />
                  </div>
                </div>

                <div
                  className="flex items-center"
                  style={{
                    gap: '10px',
                    position: isCompactViewport ? 'sticky' : 'static',
                    bottom: isCompactViewport ? '0' : undefined,
                    paddingTop: isCompactViewport ? '10px' : undefined,
                    paddingBottom: isCompactViewport ? '6px' : undefined,
                    background: isCompactViewport ? 'rgba(255,255,255,0.94)' : 'transparent',
                    backdropFilter: isCompactViewport ? 'blur(6px)' : undefined,
                    WebkitBackdropFilter: isCompactViewport ? 'blur(6px)' : undefined,
                    zIndex: isCompactViewport ? 3 : undefined,
                  }}
                >
                  <button
                    type="submit"
                    disabled={createMut.isPending}
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontWeight: 700,
                      fontSize: '0.875rem',
                      color: '#ffffff',
                      background: 'linear-gradient(135deg, #3a5272, #2e4460)',
                      borderRadius: '100px',
                      minHeight: '44px',
                      padding: '0 24px',
                      border: 'none',
                      cursor: 'pointer',
                      boxShadow: '0 4px 20px rgba(58, 82, 114, 0.24)',
                    }}
                  >
                    {createMut.isPending ? t.creating : t.createHabit}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontWeight: 700,
                      fontSize: '0.8125rem',
                      color: '#3a5272',
                      background: '#e4edf5',
                      borderRadius: '100px',
                      minHeight: '44px',
                      padding: '0 18px',
                      border: 'none',
                      cursor: 'pointer',
                    }}
                  >
                    {t.cancel}
                  </button>
                </div>
              </form>

              <div
                className="lg:col-span-2"
                style={{
                  borderRadius: '0 16px 16px 16px',
                  background: 'linear-gradient(145deg, #edf2f8 0%, #e4edf5 56%, #deebf7 100%)',
                  boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.6)',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '14px',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <div
                  className={reduceMotion ? undefined : 'float-a'}
                  style={{
                    position: 'absolute',
                    width: '120px',
                    height: '120px',
                    borderRadius: '999px',
                    background: 'radial-gradient(circle, rgba(58,82,114,0.18) 0%, rgba(58,82,114,0) 70%)',
                    top: '-24px',
                    right: '-20px',
                    pointerEvents: 'none',
                  }}
                />
                <div
                  className={reduceMotion ? undefined : 'float-b'}
                  style={{
                    position: 'absolute',
                    width: '96px',
                    height: '96px',
                    borderRadius: '999px',
                    background: 'radial-gradient(circle, rgba(69,110,152,0.18) 0%, rgba(69,110,152,0) 72%)',
                    bottom: '-18px',
                    left: '-12px',
                    pointerEvents: 'none',
                  }}
                />

                  <div className="flex items-center justify-between" style={{ gap: '10px' }}>
                    <p style={{ ...microLabel, color: '#3a5272' }}>{studio.liveReflection}</p>
                    {isCompactViewport && (
                      <button
                        type="button"
                        onClick={() => setMobileReflectionOpen((v) => !v)}
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontSize: '0.6875rem',
                          fontWeight: 700,
                          color: '#3a5272',
                          background: '#dbe7f4',
                          border: 'none',
                          borderRadius: '100px',
                          minHeight: '30px',
                          padding: '0 12px',
                          cursor: 'pointer',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        {reflectionExpanded ? studio.hideReflection : studio.showReflection}
                      </button>
                    )}
                  </div>

                  {reflectionExpanded && (
                    <>
                      <h3
                        style={{
                          fontFamily: 'var(--font-serif), Georgia, serif',
                          fontSize: '1.35rem',
                          fontWeight: 400,
                          color: '#2e342b',
                          letterSpacing: '-0.03em',
                        }}
                      >
                        {hasName ? titleCase(habitName) : studio.yourNextRitual}
                      </h3>

                      <p
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontSize: '0.875rem',
                          color: '#5a6157',
                          lineHeight: 1.6,
                        }}
                      >
                        {affirmationBody}
                      </p>

                      <div
                        style={{
                          background: '#ffffff',
                          borderRadius: '0 12px 12px 12px',
                          padding: '14px',
                          boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '8px',
                        }}
                      >
                        <p style={{ ...microLabel, color: '#767d72' }}>{studio.preview}</p>
                        <p
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.8125rem',
                            color: '#2e342b',
                          }}
                        >
                          {studio.frequencyLabel}: <strong>{frequencyLabel}</strong>
                        </p>
                        <p
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.8125rem',
                            color: '#2e342b',
                          }}
                        >
                          {studio.ritualLabel}: <strong>{hasName ? titleCase(habitName) : studio.namePending}</strong>
                        </p>
                        <p
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.8125rem',
                            color: '#2e342b',
                          }}
                        >
                          {studio.timeLabel}: <strong>{scheduledTimeLabel}</strong>
                        </p>
                        {dynamicCue ? (
                          <span
                            className="flex items-center"
                            style={{
                              gap: '6px',
                              width: 'fit-content',
                              fontFamily: 'var(--font-manrope), sans-serif',
                              fontSize: '0.75rem',
                              fontWeight: 700,
                              color: dynamicCue.color,
                              background: '#f8faf2',
                              borderRadius: '100px',
                              minHeight: '28px',
                              padding: '0 10px',
                            }}
                          >
                            <Clock size={12} /> {dynamicCue.text}
                          </span>
                        ) : (
                          <span
                            style={{
                              fontFamily: 'var(--font-manrope), sans-serif',
                              fontSize: '0.75rem',
                              color: '#767d72',
                            }}
                          >
                            {studio.timeCueHint}
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <p
                          style={{
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.8125rem',
                            fontWeight: 700,
                            color: '#2e4460',
                          }}
                        >
                          {affirmationTitle}
                        </p>
                        {refinementSignals.map((signal) => (
                          <div key={signal.label} className="flex items-center" style={{ gap: '8px' }}>
                            <span
                              style={{
                                width: '18px',
                                height: '18px',
                                borderRadius: '999px',
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                background: signal.ready ? '#d8e6f6' : '#dde4ec',
                                color: signal.ready ? '#2e4460' : '#657489',
                                fontSize: '0.625rem',
                                fontFamily: 'var(--font-manrope), sans-serif',
                                fontWeight: 700,
                              }}
                            >
                              {signal.ready ? '✓' : '•'}
                            </span>
                            <span
                              style={{
                                fontFamily: 'var(--font-manrope), sans-serif',
                                fontSize: '0.75rem',
                                color: '#5a6157',
                              }}
                            >
                              {signal.label}
                            </span>
                          </div>
                        ))}
                      </div>

                      <p
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontSize: '0.75rem',
                          color: '#3a5272',
                          lineHeight: 1.55,
                          opacity: reduceMotion ? 1 : tipFade ? 1 : 0.2,
                          transition: reduceMotion ? 'none' : 'opacity 280ms ease',
                        }}
                      >
                        {activeTip || affirmationTip}
                      </p>
                    </>
                  )}
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes habitCardReveal {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}
