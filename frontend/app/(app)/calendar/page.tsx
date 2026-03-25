'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight } from 'lucide-react'

import { calendarApi, type CalendarEvent, type CreateEventInput } from '@/lib/api/calendar'
import { getAppTranslations } from '@/lib/translations/app'
import { useLang } from '@/lib/useLang'

type ViewMode = 'month' | 'week' | 'day'
type ModalMode = 'create' | 'edit' | null
type EditorAnchor = { top: number; left: number }
type Meridiem = 'AM' | 'PM'
type ActiveTimeSuggestions = 'start' | 'end' | null

type CalendarQueryData = {
  ok: boolean
  events: CalendarEvent[]
}

const QUERY_KEY = ['calendar-events'] as const
const EDITOR_WIDTH = 340

function fmtDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return iso
  }
}

function fmtTime(iso: string) {
  try {
    return new Date(iso).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
  } catch {
    return ''
  }
}

function toDateKey(date: Date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

function startOfWeek(date: Date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() - d.getDay())
  return d
}

function buildMonthGrid(date: Date) {
  const first = startOfMonth(date)
  const firstWeekday = first.getDay()
  const cursor = new Date(first)
  cursor.setDate(first.getDate() - firstWeekday)

  const cells: Date[] = []
  for (let i = 0; i < 42; i += 1) {
    cells.push(new Date(cursor))
    cursor.setDate(cursor.getDate() + 1)
  }
  return cells
}

function buildWeekGrid(date: Date) {
  const cursor = startOfWeek(date)
  const cells: Date[] = []
  for (let i = 0; i < 7; i += 1) {
    cells.push(new Date(cursor))
    cursor.setDate(cursor.getDate() + 1)
  }
  return cells
}

function formatDateInputValue(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function parseIsoToDateParts(iso?: string | null) {
  if (!iso) {
    return {
      date: '',
      hour: '9',
      minute: '00',
      meridiem: 'AM' as Meridiem,
    }
  }

  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) {
    return {
      date: '',
      hour: '9',
      minute: '00',
      meridiem: 'AM' as Meridiem,
    }
  }

  const hour24 = date.getHours()
  const meridiem: Meridiem = hour24 >= 12 ? 'PM' : 'AM'
  const hour12 = hour24 % 12 === 0 ? 12 : hour24 % 12

  return {
    date: formatDateInputValue(date),
    hour: String(hour12),
    minute: String(date.getMinutes()).padStart(2, '0'),
    meridiem,
  }
}

function combineDateAndTimeToIso(dateValue: string, hour: string, minute: string, meridiem: Meridiem) {
  if (!dateValue) return undefined

  let numericHour = Number.parseInt(hour, 10)
  const numericMinute = Number.parseInt(minute, 10)

  if (Number.isNaN(numericHour) || numericHour < 1 || numericHour > 12) numericHour = 12
  if (Number.isNaN(numericMinute) || numericMinute < 0 || numericMinute > 59) return undefined

  let hour24 = numericHour % 12
  if (meridiem === 'PM') hour24 += 12

  const [year, month, day] = dateValue.split('-').map((p) => Number.parseInt(p, 10))
  if (!year || !month || !day) return undefined

  const local = new Date(year, month - 1, day, hour24, numericMinute, 0, 0)
  if (Number.isNaN(local.getTime())) return undefined
  return local.toISOString()
}

function formatSummaryDate(date: Date, lang: string) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  if (lang === 'ko' || lang === 'zh') {
    return `${y}/${m}/${d}`
  }
  return `${d}/${m}/${y}`
}

function formatSummaryTime(date: Date) {
  const hour24 = date.getHours()
  const meridiem = hour24 >= 12 ? 'PM' : 'AM'
  const hour12 = hour24 % 12 === 0 ? 12 : hour24 % 12
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${hour12}:${minute} ${meridiem}`
}

function formatSummaryRange(startIso: string | undefined, endIso: string | undefined, lang: string) {
  if (!startIso) return 'Set start date and time'

  const start = new Date(startIso)
  if (Number.isNaN(start.getTime())) return 'Set start date and time'

  const startDate = formatSummaryDate(start, lang)
  const startTime = formatSummaryTime(start)

  if (!endIso) return `${startDate} ${startTime}`

  const end = new Date(endIso)
  if (Number.isNaN(end.getTime())) return `${startDate} ${startTime}`
  const endTime = formatSummaryTime(end)

  if (start.toDateString() === end.toDateString()) {
    return `${startDate} ${startTime} - ${endTime}`
  }

  const endDate = formatSummaryDate(end, lang)
  return `${startDate} ${startTime} - (${endDate}) ${endTime}`
}

function shiftIsoByDays(iso: string, days: number) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  date.setDate(date.getDate() + days)
  return date.toISOString()
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

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  padding: '10px 10px',
  appearance: 'none',
  WebkitAppearance: 'none',
  MozAppearance: 'none',
  backgroundImage: 'none',
}

const TIME_SLOT_OPTIONS = Array.from({ length: 48 }, (_, idx) => {
  const totalMinutes = idx * 30
  const hour24 = Math.floor(totalMinutes / 60)
  const minute = totalMinutes % 60
  const meridiem: Meridiem = hour24 >= 12 ? 'PM' : 'AM'
  const hour12 = hour24 % 12 === 0 ? 12 : hour24 % 12
  return {
    value: `${String(hour12)}:${String(minute).padStart(2, '0')}:${meridiem}`,
    label: `${hour12}:${String(minute).padStart(2, '0')} ${meridiem}`,
    hour: String(hour12),
    minute: String(minute).padStart(2, '0'),
    meridiem,
  }
})

function clamp(n: number, min: number, max: number) {
  return Math.min(Math.max(n, min), max)
}

function toSlotIndex(hour: string, minute: string, meridiem: Meridiem) {
  let h = Number.parseInt(hour, 10)
  const m = Number.parseInt(minute, 10)
  if (Number.isNaN(h) || h < 1 || h > 12) h = 12
  const safeMinute = Number.isNaN(m) ? 0 : clamp(Math.round(m / 30) * 30, 0, 30)
  let hour24 = h % 12
  if (meridiem === 'PM') hour24 += 12
  return clamp(hour24 * 2 + (safeMinute >= 30 ? 1 : 0), 0, TIME_SLOT_OPTIONS.length - 1)
}

function buildNearbySlots(baseIndex: number, startOffset = 0) {
  const start = clamp(baseIndex + startOffset, 0, TIME_SLOT_OPTIONS.length - 1)
  const end = clamp(baseIndex + 6, 0, TIME_SLOT_OPTIONS.length - 1)
  return TIME_SLOT_OPTIONS.slice(start, end + 1)
}

const appleDateStyle: React.CSSProperties = {
  ...inputStyle,
  border: 'none',
  background: 'transparent',
  boxShadow: 'none',
  padding: '8px 6px',
  minWidth: '152px',
}

const appleTimeStyle: React.CSSProperties = {
  ...selectStyle,
  border: 'none',
  background: 'transparent',
  boxShadow: 'none',
  padding: '8px 6px',
  minWidth: '136px',
  textAlign: 'left',
}

export default function CalendarPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).calendar
  const qc = useQueryClient()
  const viewLabels: Record<ViewMode, string> = {
    month: t.month,
    week: t.week,
    day: t.day,
  }
  const weekdayLabels = [t.weekdaySun, t.weekdayMon, t.weekdayTue, t.weekdayWed, t.weekdayThu, t.weekdayFri, t.weekdaySat]

  const [viewMode, setViewMode] = useState<ViewMode>('month')
  const [monthAnchor, setMonthAnchor] = useState(startOfMonth(new Date()))
  const [selectedDate, setSelectedDate] = useState(new Date())

  const [modalMode, setModalMode] = useState<ModalMode>(null)
  const [pendingDeleteId, setPendingDeleteId] = useState<number | null>(null)
  const [activeEventId, setActiveEventId] = useState<number | null>(null)
  const [draggingEventId, setDraggingEventId] = useState<number | null>(null)
  const [dragOverDateKey, setDragOverDateKey] = useState<string | null>(null)
  const [editorAnchor, setEditorAnchor] = useState<EditorAnchor>({ top: 120, left: 24 })
  const [editingEventId, setEditingEventId] = useState<number | null>(null)
  const [hasInteractedWithForm, setHasInteractedWithForm] = useState(false)
  const [formTitle, setFormTitle] = useState('')
  const [formStartDate, setFormStartDate] = useState('')
  const [formStartHour, setFormStartHour] = useState('9')
  const [formStartMinute, setFormStartMinute] = useState('00')
  const [formStartMeridiem, setFormStartMeridiem] = useState<Meridiem>('AM')
  const [formEndDate, setFormEndDate] = useState('')
  const [formEndHour, setFormEndHour] = useState('9')
  const [formEndMinute, setFormEndMinute] = useState('00')
  const [formEndMeridiem, setFormEndMeridiem] = useState<Meridiem>('AM')
  const [showTimeDetails, setShowTimeDetails] = useState(false)
  const [activeTimeSuggestions, setActiveTimeSuggestions] = useState<ActiveTimeSuggestions>(null)
  const [startTimeDraft, setStartTimeDraft] = useState('9:00 AM')
  const [endTimeDraft, setEndTimeDraft] = useState('9:00 AM')
  const [formLocation, setFormLocation] = useState('')
  const [formAllDay, setFormAllDay] = useState(false)
  const editorRef = useRef<HTMLElement | null>(null)
  const timeDetailsRef = useRef<HTMLDivElement | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: QUERY_KEY,
    queryFn: () => calendarApi.list(200),
  })

  const createMut = useMutation({
    mutationFn: (input: CreateEventInput) => calendarApi.create(input),
    onSuccess: (response) => {
      const created = response.event
      setEditingEventId(created.id)
      setModalMode('edit')
      setActiveEventId(created.id)
      setHasInteractedWithForm(false)
      qc.invalidateQueries({ queryKey: QUERY_KEY })
    },
  })

  const updateMut = useMutation({
    mutationFn: (input: {
      id: number
      title: string
      start_time: string
      end_time?: string
      location?: string
      all_day: boolean
    }) =>
      calendarApi.update(input.id, {
        title: input.title,
        start_time: input.start_time,
        end_time: input.end_time,
        location: input.location,
        all_day: input.all_day,
      }),
    onMutate: async (input) => {
      await qc.cancelQueries({ queryKey: QUERY_KEY })
      const previous = qc.getQueryData<CalendarQueryData>(QUERY_KEY)

      if (previous) {
        qc.setQueryData<CalendarQueryData>(QUERY_KEY, {
          ...previous,
          events: previous.events.map((ev) =>
            ev.id === input.id
              ? {
                  ...ev,
                  title: input.title,
                  start_time: input.start_time,
                  end_time: input.end_time ?? null,
                  location: input.location ?? null,
                  all_day: input.all_day,
                }
              : ev,
          ),
        })
      }

      return { previous }
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        qc.setQueryData(QUERY_KEY, context.previous)
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEY })
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => calendarApi.delete(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: QUERY_KEY })
      const previous = qc.getQueryData<CalendarQueryData>(QUERY_KEY)

      if (previous) {
        qc.setQueryData<CalendarQueryData>(QUERY_KEY, {
          ...previous,
          events: previous.events.filter((ev) => ev.id !== id),
        })
      }

      return { previous }
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        qc.setQueryData(QUERY_KEY, context.previous)
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEY })
    },
  })

  const events = data?.events ?? []
  const editingEvent = useMemo(
    () => (modalMode === 'edit' && editingEventId ? events.find((ev) => ev.id === editingEventId) ?? null : null),
    [modalMode, editingEventId, events],
  )
  const draftStartIso = combineDateAndTimeToIso(formStartDate, formStartHour, formStartMinute, formStartMeridiem)
  const draftEndIso = combineDateAndTimeToIso(formEndDate, formEndHour, formEndMinute, formEndMeridiem)
  const timeSummaryText = formatSummaryRange(draftStartIso, formEndDate ? draftEndIso : undefined, lang)

  const editingStartParts = useMemo(() => (editingEvent ? parseIsoToDateParts(editingEvent.start_time) : null), [editingEvent])
  const editingEndParts = useMemo(() => (editingEvent ? parseIsoToDateParts(editingEvent.end_time) : null), [editingEvent])
  const startFieldsChanged = Boolean(
    editingEvent && editingStartParts && (
      formStartDate !== editingStartParts.date ||
      formStartHour !== editingStartParts.hour ||
      formStartMinute !== editingStartParts.minute ||
      formStartMeridiem !== editingStartParts.meridiem
    ),
  )
  const endFieldsChanged = Boolean(
    editingEvent && editingEndParts && (
      formEndDate !== editingEndParts.date ||
      formEndHour !== editingEndParts.hour ||
      formEndMinute !== editingEndParts.minute ||
      formEndMeridiem !== editingEndParts.meridiem
    ),
  )

  const displayedEvents = useMemo(() => {
    if (modalMode !== 'edit' || !editingEventId) return events

    return events.map((ev) => {
      if (ev.id !== editingEventId) return ev

      const nextStart = draftStartIso ?? ev.start_time
      const nextEnd = formEndDate ? draftEndIso ?? ev.end_time : null

      return {
        ...ev,
        title: formTitle || ev.title,
        start_time: nextStart,
        end_time: nextEnd,
        location: formLocation || null,
        all_day: formAllDay,
      }
    })
  }, [events, modalMode, editingEventId, formTitle, draftStartIso, formEndDate, draftEndIso, formLocation, formAllDay])

  const selectedKey = toDateKey(selectedDate)
  const todayKey = toDateKey(new Date())

  const eventsByDay = useMemo(() => {
    const grouped = new Map<string, CalendarEvent[]>()

    for (const ev of displayedEvents) {
      const key = toDateKey(new Date(ev.start_time))
      const bucket = grouped.get(key)
      if (bucket) {
        bucket.push(ev)
      } else {
        grouped.set(key, [ev])
      }
    }

    for (const [key, value] of grouped.entries()) {
      grouped.set(
        key,
        [...value].sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()),
      )
    }

    return grouped
  }, [displayedEvents])

  const selectedDayEvents = eventsByDay.get(selectedKey) ?? []
  const monthCells = useMemo(() => buildMonthGrid(monthAnchor), [monthAnchor])
  const weekCells = useMemo(() => buildWeekGrid(selectedDate), [selectedDate])

  const rangeLabel = useMemo(() => {
    if (viewMode === 'month') {
      return monthAnchor.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
    }

    if (viewMode === 'week') {
      const start = weekCells[0]
      const end = weekCells[6]
      const left = start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
      const right = end.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
      return `${left} - ${right}`
    }

    return selectedDate.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
  }, [viewMode, monthAnchor, selectedDate, weekCells])

  const startSlotValue = `${formStartHour}:${formStartMinute}:${formStartMeridiem}`
  const endSlotValue = `${formEndHour}:${formEndMinute}:${formEndMeridiem}`

  const parsedStartDraft = parseTypedTime(startTimeDraft)
  const effectiveStartHour = parsedStartDraft?.hour ?? formStartHour
  const effectiveStartMinute = parsedStartDraft?.minute ?? formStartMinute
  const effectiveStartMeridiem = parsedStartDraft?.meridiem ?? formStartMeridiem

  const nearbyStartSlots = useMemo(() => {
    const idx = toSlotIndex(effectiveStartHour, effectiveStartMinute, effectiveStartMeridiem)
    return buildNearbySlots(idx)
  }, [effectiveStartHour, effectiveStartMinute, effectiveStartMeridiem])

  const nearbyEndSlots = useMemo(() => {
    const baseIdx = toSlotIndex(effectiveStartHour, effectiveStartMinute, effectiveStartMeridiem)
    return buildNearbySlots(baseIdx, 1)
  }, [effectiveStartHour, effectiveStartMinute, effectiveStartMeridiem])

  function applyStartSlot(value: string) {
    const [hour, minute, meridiem] = value.split(':')
    setFormStartHour(hour)
    setFormStartMinute(minute)
    setFormStartMeridiem((meridiem as Meridiem) ?? 'AM')
    const label = TIME_SLOT_OPTIONS.find((slot) => slot.value === value)?.label ?? `${hour}:${minute} ${meridiem}`
    setStartTimeDraft(label)

    const nextStartIso = combineDateAndTimeToIso(formStartDate, hour, minute, (meridiem as Meridiem) ?? 'AM')
    const currentEndIso = combineDateAndTimeToIso(
      formEndDate || formStartDate,
      formEndHour,
      formEndMinute,
      formEndMeridiem,
    )
    if (!nextStartIso || !currentEndIso) return

    if (new Date(nextStartIso).getTime() > new Date(currentEndIso).getTime()) {
      const nextEnd = new Date(nextStartIso)
      nextEnd.setMinutes(nextEnd.getMinutes() + 60)
      const endParts = parseIsoToDateParts(nextEnd.toISOString())
      setFormEndDate(endParts.date)
      setFormEndHour(endParts.hour)
      setFormEndMinute(endParts.minute)
      setFormEndMeridiem(endParts.meridiem)
      setEndTimeDraft(`${endParts.hour}:${endParts.minute} ${endParts.meridiem}`)
    }
  }

  function applyEndSlot(value: string) {
    const [hour, minute, meridiem] = value.split(':')
    setFormEndHour(hour)
    setFormEndMinute(minute)
    setFormEndMeridiem((meridiem as Meridiem) ?? 'AM')
    const label = TIME_SLOT_OPTIONS.find((slot) => slot.value === value)?.label ?? `${hour}:${minute} ${meridiem}`
    setEndTimeDraft(label)
  }

  function parseTypedTime(value: string): { hour: string; minute: string; meridiem: Meridiem } | null {
    const raw = value.trim().toUpperCase().replace(/\s+/g, ' ')
    const match = raw.match(/^(\d{1,2})(?::(\d{1,2}))?\s*(AM|PM)$/)
    if (!match) return null

    const parsedHour = Number.parseInt(match[1], 10)
    const parsedMinute = Number.parseInt(match[2] ?? '0', 10)
    const parsedMeridiem = match[3] as Meridiem
    if (Number.isNaN(parsedHour) || parsedHour < 1 || parsedHour > 12) return null
    if (Number.isNaN(parsedMinute) || parsedMinute < 0 || parsedMinute > 59) return null

    return {
      hour: String(parsedHour),
      minute: String(parsedMinute).padStart(2, '0'),
      meridiem: parsedMeridiem,
    }
  }

  function commitStartTimeDraft() {
    const parsed = parseTypedTime(startTimeDraft)
    if (!parsed) {
      setStartTimeDraft(`${formStartHour}:${formStartMinute} ${formStartMeridiem}`)
      return
    }

    setFormStartHour(parsed.hour)
    setFormStartMinute(parsed.minute)
    setFormStartMeridiem(parsed.meridiem)
    setStartTimeDraft(`${parsed.hour}:${parsed.minute} ${parsed.meridiem}`)

    const nextStartIso = combineDateAndTimeToIso(formStartDate, parsed.hour, parsed.minute, parsed.meridiem)
    const currentEndIso = combineDateAndTimeToIso(
      formEndDate || formStartDate,
      formEndHour,
      formEndMinute,
      formEndMeridiem,
    )
    if (!nextStartIso || !currentEndIso) return

    if (new Date(nextStartIso).getTime() > new Date(currentEndIso).getTime()) {
      const nextEnd = new Date(nextStartIso)
      nextEnd.setMinutes(nextEnd.getMinutes() + 60)
      const endParts = parseIsoToDateParts(nextEnd.toISOString())
      setFormEndDate(endParts.date)
      setFormEndHour(endParts.hour)
      setFormEndMinute(endParts.minute)
      setFormEndMeridiem(endParts.meridiem)
      setEndTimeDraft(`${endParts.hour}:${endParts.minute} ${endParts.meridiem}`)
    }
  }

  function commitEndTimeDraft() {
    const parsed = parseTypedTime(endTimeDraft)
    if (!parsed) {
      setEndTimeDraft(`${formEndHour}:${formEndMinute} ${formEndMeridiem}`)
      return
    }

    setFormEndHour(parsed.hour)
    setFormEndMinute(parsed.minute)
    setFormEndMeridiem(parsed.meridiem)
    setEndTimeDraft(`${parsed.hour}:${parsed.minute} ${parsed.meridiem}`)
  }

  function resetForm() {
    setEditingEventId(null)
    setHasInteractedWithForm(false)
    setShowTimeDetails(false)
    setActiveTimeSuggestions(null)
    setStartTimeDraft('9:00 AM')
    setEndTimeDraft('9:00 AM')
    setFormTitle('')
    setFormStartDate('')
    setFormStartHour('9')
    setFormStartMinute('00')
    setFormStartMeridiem('AM')
    setFormEndDate('')
    setFormEndHour('9')
    setFormEndMinute('00')
    setFormEndMeridiem('AM')
    setFormLocation('')
    setFormAllDay(false)
  }

  function closeModal() {
    setModalMode(null)
    resetForm()
  }

  function markInteracted() {
    if (!hasInteractedWithForm) {
      setHasInteractedWithForm(true)
    }
  }

  function getEditorAnchor(target?: HTMLElement | null): EditorAnchor {
    if (!target || typeof window === 'undefined') {
      return { top: 120, left: 24 }
    }

    const rect = target.getBoundingClientRect()
    const gap = 12
    const maxLeft = Math.max(12, window.innerWidth - EDITOR_WIDTH - 12)
    const preferRight = rect.right + gap
    const preferLeft = rect.left - EDITOR_WIDTH - gap

    let left = preferRight <= maxLeft ? preferRight : preferLeft
    if (left < 12) left = 12
    if (left > maxLeft) left = maxLeft

    const panelHeight = 520
    const maxTop = Math.max(12, window.innerHeight - panelHeight - 12)
    const top = Math.min(Math.max(12, rect.top), maxTop)

    return { top, left }
  }

  useEffect(() => {
    if (!modalMode) return

    function handlePointerDown(event: MouseEvent) {
      const target = event.target as Node | null
      if (!target) return

      const targetElement = target instanceof Element ? target : target.parentElement

      if (targetElement?.closest('[data-time-suggestion-menu]') || targetElement?.closest('[data-time-suggestion-option]')) {
        return
      }

      if (editorRef.current && !editorRef.current.contains(target)) {
        closeModal()
        return
      }

      if (showTimeDetails && timeDetailsRef.current && !timeDetailsRef.current.contains(target)) {
        setShowTimeDetails(false)
      }

      if (!targetElement?.closest('[data-time-input-group]')) {
        setActiveTimeSuggestions(null)
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
    }
  }, [modalMode, showTimeDetails])

  function openCreateModal(anchorEl?: HTMLElement | null) {
    const base = new Date(selectedDate)
    base.setHours(9, 0, 0, 0)
    const startParts = parseIsoToDateParts(base.toISOString())
    const endBase = new Date(base)
    endBase.setHours(10, 0, 0, 0)
    const endParts = parseIsoToDateParts(endBase.toISOString())
    setEditorAnchor(getEditorAnchor(anchorEl))
    setEditingEventId(null)
    setFormTitle('')
    setFormStartDate(startParts.date)
    setFormStartHour(startParts.hour)
    setFormStartMinute(startParts.minute)
    setFormStartMeridiem(startParts.meridiem)
    setStartTimeDraft(`${startParts.hour}:${startParts.minute} ${startParts.meridiem}`)
    setFormEndDate(endParts.date)
    setFormEndHour(endParts.hour)
    setFormEndMinute(endParts.minute)
    setFormEndMeridiem(endParts.meridiem)
    setEndTimeDraft(`${endParts.hour}:${endParts.minute} ${endParts.meridiem}`)
    setFormLocation('')
    setFormAllDay(false)
    setShowTimeDetails(false)
    setHasInteractedWithForm(false)
    setModalMode('create')
  }

  function openCreateModalForDay(day: Date, anchorEl?: HTMLElement | null) {
    setSelectedDate(day)
    if (viewMode === 'month') {
      setMonthAnchor(startOfMonth(day))
    }
    setEditorAnchor(getEditorAnchor(anchorEl))

    const base = new Date(day)
    base.setHours(9, 0, 0, 0)
    const startParts = parseIsoToDateParts(base.toISOString())
    const endBase = new Date(base)
    endBase.setHours(10, 0, 0, 0)
    const endParts = parseIsoToDateParts(endBase.toISOString())
    setEditingEventId(null)
    setFormTitle('')
    setFormStartDate(startParts.date)
    setFormStartHour(startParts.hour)
    setFormStartMinute(startParts.minute)
    setFormStartMeridiem(startParts.meridiem)
    setStartTimeDraft(`${startParts.hour}:${startParts.minute} ${startParts.meridiem}`)
    setFormEndDate(endParts.date)
    setFormEndHour(endParts.hour)
    setFormEndMinute(endParts.minute)
    setFormEndMeridiem(endParts.meridiem)
    setEndTimeDraft(`${endParts.hour}:${endParts.minute} ${endParts.meridiem}`)
    setFormLocation('')
    setFormAllDay(false)
    setShowTimeDetails(false)
    setHasInteractedWithForm(false)
    setModalMode('create')
  }

  function openEditModal(ev: CalendarEvent, anchorEl?: HTMLElement | null) {
    const startParts = parseIsoToDateParts(ev.start_time)
    const endParts = parseIsoToDateParts(ev.end_time)
    setEditorAnchor(getEditorAnchor(anchorEl))
    setEditingEventId(ev.id)
    setFormTitle(ev.title)
    setFormStartDate(startParts.date)
    setFormStartHour(startParts.hour)
    setFormStartMinute(startParts.minute)
    setFormStartMeridiem(startParts.meridiem)
    setStartTimeDraft(`${startParts.hour}:${startParts.minute} ${startParts.meridiem}`)
    setFormEndDate(endParts.date)
    setFormEndHour(endParts.hour)
    setFormEndMinute(endParts.minute)
    setFormEndMeridiem(endParts.meridiem)
    setEndTimeDraft(`${endParts.hour}:${endParts.minute} ${endParts.meridiem}`)
    setFormLocation(ev.location ?? '')
    setFormAllDay(ev.all_day)
    setShowTimeDetails(false)
    setHasInteractedWithForm(false)
    setModalMode('edit')
  }

  function shiftRange(delta: number) {
    if (viewMode === 'month') {
      setMonthAnchor((prev) => new Date(prev.getFullYear(), prev.getMonth() + delta, 1))
      return
    }

    if (viewMode === 'week') {
      setSelectedDate((prev) => {
        const d = new Date(prev)
        d.setDate(d.getDate() + delta * 7)
        setMonthAnchor(startOfMonth(d))
        return d
      })
      return
    }

    setSelectedDate((prev) => {
      const d = new Date(prev)
      d.setDate(d.getDate() + delta)
      setMonthAnchor(startOfMonth(d))
      return d
    })
  }

  function jumpToToday() {
    const now = new Date()
    setSelectedDate(now)
    setMonthAnchor(startOfMonth(now))
  }

  function selectDay(day: Date) {
    setSelectedDate(day)
    if (viewMode === 'month') {
      setMonthAnchor(startOfMonth(day))
    }
  }

  function moveEventToDate(eventId: number, targetDate: Date) {
    const ev = events.find((item) => item.id === eventId)
    if (!ev) return

    const start = new Date(ev.start_time)
    if (Number.isNaN(start.getTime())) return

    const originStartOfDay = new Date(start)
    originStartOfDay.setHours(0, 0, 0, 0)
    const targetStartOfDay = new Date(targetDate)
    targetStartOfDay.setHours(0, 0, 0, 0)

    const dayDelta = Math.round((targetStartOfDay.getTime() - originStartOfDay.getTime()) / 86400000)
    if (dayDelta === 0) return

    const nextStart = shiftIsoByDays(ev.start_time, dayDelta)
    const nextEnd = ev.end_time ? shiftIsoByDays(ev.end_time, dayDelta) : undefined

    updateMut.mutate({
      id: ev.id,
      title: ev.title,
      start_time: nextStart,
      end_time: nextEnd,
      location: ev.location ?? undefined,
      all_day: ev.all_day,
    })
  }

  function requestDelete(id: number) {
    setPendingDeleteId(id)
    setActiveEventId(id)
  }

  function cancelDelete() {
    setPendingDeleteId(null)
  }

  function confirmDelete(id: number) {
    setPendingDeleteId(null)
    setActiveEventId((prev) => (prev === id ? null : prev))
    deleteMut.mutate(id)
  }

  useEffect(() => {
    if (!modalMode) return

    if (hasInteractedWithForm && !formTitle.trim()) {
      closeModal()
      return
    }

    if (!hasInteractedWithForm || !formTitle.trim() || !draftStartIso) return

    const effectiveStartTime = editingEvent && !startFieldsChanged ? editingEvent.start_time : draftStartIso
    const effectiveEndTime = formEndDate
      ? editingEvent && !endFieldsChanged
        ? editingEvent.end_time ?? (draftEndIso ?? undefined)
        : (draftEndIso ?? undefined)
      : undefined

    const payload = {
      title: formTitle.trim(),
      start_time: effectiveStartTime,
      end_time: effectiveEndTime,
      location: formLocation.trim(),
      all_day: formAllDay,
    }

    const timer = window.setTimeout(() => {
      if (modalMode === 'create') {
        if (!createMut.isPending) {
          createMut.mutate(payload)
        }
        return
      }

      if (modalMode === 'edit' && editingEventId) {
        updateMut.mutate({ id: editingEventId, ...payload })
      }
    }, 420)

    return () => {
      window.clearTimeout(timer)
    }
  }, [
    modalMode,
    editingEventId,
    hasInteractedWithForm,
    formTitle,
    formLocation,
    formAllDay,
    formEndDate,
    draftStartIso,
    draftEndIso,
    editingEvent,
    startFieldsChanged,
    endFieldsChanged,
  ])

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (modalMode || pendingDeleteId !== null || activeEventId === null) return
      if (event.key !== 'Backspace' && event.key !== 'Delete') return

      const target = event.target as HTMLElement | null
      const tag = target?.tagName?.toLowerCase()
      if (tag === 'input' || tag === 'textarea' || target?.isContentEditable) return

      event.preventDefault()
      requestDelete(activeEventId)
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [activeEventId, modalMode, pendingDeleteId])

  function renderEventsPreview(dayKey: string, maxItems: number) {
    const dayEvents = eventsByDay.get(dayKey) ?? []
    if (dayEvents.length === 0) return null

    return (
      <div className="mt-2 space-y-1">
        {dayEvents.slice(0, maxItems).map((ev) => (
          <button
            key={`preview-${ev.id}`}
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              setActiveEventId(ev.id)
              selectDay(new Date(ev.start_time))
            }}
            onDoubleClick={(e) => {
              e.stopPropagation()
              openEditModal(ev, e.currentTarget)
            }}
            draggable
            onDragStart={(e) => {
              e.stopPropagation()
              setDraggingEventId(ev.id)
              e.dataTransfer.effectAllowed = 'move'
              e.dataTransfer.setData('text/calendar-event-id', String(ev.id))
            }}
            onDragEnd={() => {
              setDraggingEventId(null)
              setDragOverDateKey(null)
            }}
            className="transition-all duration-200 hover:-translate-y-px"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.625rem',
              color: activeEventId === ev.id ? '#ffffff' : '#465642',
              background: activeEventId === ev.id ? '#4b6646' : 'rgba(75, 102, 70, 0.10)',
              borderRadius: '9999px',
              padding: '2px 6px',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              border: 'none',
              cursor: 'pointer',
              display: 'block',
              width: '100%',
              textAlign: 'left',
              transition: 'all 180ms ease',
              opacity: draggingEventId === ev.id ? 0.55 : 1,
            }}
            title={ev.title}
          >
            {ev.title}
          </button>
        ))}
        {dayEvents.length > maxItems && (
          <div
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.625rem',
              color: '#767d72',
              paddingLeft: '2px',
            }}
          >
            +{dayEvents.length - maxItems} more
          </div>
        )}
      </div>
    )
  }

  function renderDayCell(day: Date, compact = false) {
    const dayKey = toDateKey(day)
    const isCurrentMonth = day.getMonth() === monthAnchor.getMonth()
    const isToday = dayKey === todayKey
    const isDragTarget = dragOverDateKey === dayKey

    return (
      <div
        key={dayKey}
        role="button"
        tabIndex={0}
        onClick={() => selectDay(day)}
        onDoubleClick={(e) => openCreateModalForDay(day, e.currentTarget as HTMLElement)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            selectDay(day)
          }
        }}
        onDragEnter={(e) => {
          if (draggingEventId === null) return
          e.preventDefault()
          setDragOverDateKey(dayKey)
        }}
        onDragOver={(e) => {
          if (draggingEventId === null) return
          e.preventDefault()
          e.dataTransfer.dropEffect = 'move'
          if (dragOverDateKey !== dayKey) setDragOverDateKey(dayKey)
        }}
        onDragLeave={() => {
          if (dragOverDateKey === dayKey) setDragOverDateKey(null)
        }}
        onDrop={(e) => {
          if (draggingEventId === null) return
          e.preventDefault()
          moveEventToDate(draggingEventId, day)
          setDraggingEventId(null)
          setDragOverDateKey(null)
        }}
        className="text-left transition-all duration-200"
        style={{
          minHeight: compact ? '92px' : '124px',
          border: 'none',
          cursor: 'pointer',
          borderRadius: '0 12px 12px 12px',
          background: isCurrentMonth ? '#f8faf2' : '#f1f5eb',
          padding: compact ? '8px 9px' : '10px',
          boxShadow: isDragTarget ? '0 0 0 2px rgba(75, 102, 70, 0.35) inset' : 'none',
          opacity: isCurrentMonth || viewMode !== 'month' ? 1 : 0.72,
        }}
      >
        <div className="flex items-center justify-between">
          <span
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontWeight: isToday ? 700 : 600,
              fontSize: '0.75rem',
              color: isToday ? '#3f5a3a' : '#465642',
            }}
          >
            {day.getDate()}
          </span>
          {isToday && (
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: '9999px',
                background: '#4b6646',
              }}
            />
          )}
        </div>

        {renderEventsPreview(dayKey, compact ? 1 : 2)}
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
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
      </div>

      <section
        className="p-4 sm:p-6"
        style={{
          background: '#ffffff',
          borderRadius: '0 16px 16px 16px',
          boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
        }}
      >
        <div className="flex flex-col gap-3 sm:gap-4 mb-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => shiftRange(-1)}
                className="rounded-full"
                aria-label="Previous range"
                style={{
                  width: 34,
                  height: 34,
                  border: 'none',
                  cursor: 'pointer',
                  background: '#f1f5eb',
                  color: '#465642',
                }}
              >
                <ChevronLeft size={16} style={{ margin: '0 auto' }} />
              </button>
              <button
                type="button"
                onClick={() => shiftRange(1)}
                className="rounded-full"
                aria-label="Next range"
                style={{
                  width: 34,
                  height: 34,
                  border: 'none',
                  cursor: 'pointer',
                  background: '#f1f5eb',
                  color: '#465642',
                }}
              >
                <ChevronRight size={16} style={{ margin: '0 auto' }} />
              </button>
            </div>

            <h2
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: '1.25rem',
                fontWeight: 400,
                color: '#4b6646',
                letterSpacing: '-0.03em',
              }}
            >
              {rangeLabel}
            </h2>

            <button
              type="button"
              onClick={jumpToToday}
              className="btn-pill"
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontWeight: 700,
                fontSize: '0.75rem',
                color: '#465642',
                background: '#d6e8ce',
                border: 'none',
                padding: '8px 14px',
                borderRadius: '100px',
                cursor: 'pointer',
              }}
            >
              {t.today}
            </button>
          </div>

          <div className="flex items-center gap-2">
            {(['month', 'week', 'day'] as ViewMode[]).map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => setViewMode(mode)}
                className="btn-pill"
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontWeight: 700,
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  color: viewMode === mode ? '#ffffff' : '#465642',
                  background: viewMode === mode ? 'linear-gradient(135deg, #4b6646, #3f5a3a)' : '#f1f5eb',
                  border: 'none',
                  padding: '8px 14px',
                  borderRadius: '100px',
                  cursor: 'pointer',
                }}
              >
                {viewLabels[mode]}
              </button>
            ))}
          </div>
        </div>

        {viewMode !== 'day' && (
          <div className="grid grid-cols-7 gap-1 mb-2">
            {weekdayLabels.map((label) => (
              <div
                key={label}
                className="text-center"
                style={{
                  ...microLabel,
                  fontSize: '0.625rem',
                  padding: '8px 0',
                }}
              >
                {label}
              </div>
            ))}
          </div>
        )}

        {viewMode === 'month' && <div className="grid grid-cols-7 gap-1 sm:gap-2">{monthCells.map((day) => renderDayCell(day, true))}</div>}

        {viewMode === 'week' && <div className="grid grid-cols-7 gap-1 sm:gap-2">{weekCells.map((day) => renderDayCell(day, false))}</div>}

        {viewMode === 'day' && (
          <div
            style={{
              borderRadius: '0 12px 12px 12px',
              background: '#f8faf2',
              padding: '14px',
            }}
          >
            <h3
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: '1.05rem',
                fontWeight: 400,
                color: '#4b6646',
                letterSpacing: '-0.02em',
                marginBottom: '10px',
              }}
            >
              {selectedDate.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
            </h3>
            {selectedDayEvents.length === 0 && (
              <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>{t.noEvents}</p>
            )}
            {selectedDayEvents.length > 0 && (
              <div className="space-y-2">
                {selectedDayEvents.map((ev) => (
                  <div
                    key={`day-view-${ev.id}`}
                    onClick={() => setActiveEventId(ev.id)}
                    onDoubleClick={(e) => openEditModal(ev, e.currentTarget as HTMLElement)}
                    style={{
                      borderRadius: '9999px',
                      background: 'rgba(75, 102, 70, 0.10)',
                      padding: '8px 12px',
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.8125rem',
                      color: '#465642',
                      cursor: 'pointer',
                    }}
                    title={ev.title}
                  >
                    {ev.title}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      {pendingDeleteId !== null && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-[70] flex items-center justify-center p-4"
          style={{ background: 'rgba(26, 31, 26, 0.32)' }}
          onClick={cancelDelete}
        >
          <div
            className="w-full max-w-sm p-5"
            style={{
              background: '#ffffff',
              borderRadius: '0 14px 14px 14px',
              boxShadow: '0 20px 40px rgba(46, 52, 43, 0.14)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: '1.05rem',
                fontWeight: 400,
                color: '#4b6646',
                letterSpacing: '-0.02em',
                marginBottom: '8px',
              }}
            >
              Delete Event?
            </h3>
            <p
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.8125rem',
                color: '#5a6157',
                marginBottom: '14px',
              }}
            >
              This action cannot be undone.
            </p>
            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={cancelDelete}
                className="btn-pill"
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontWeight: 700,
                  fontSize: '0.75rem',
                  color: '#465642',
                  background: '#d6e8ce',
                  border: 'none',
                  padding: '8px 14px',
                  borderRadius: '100px',
                  cursor: 'pointer',
                }}
              >
                {t.cancel}
              </button>
              <button
                type="button"
                onClick={() => confirmDelete(pendingDeleteId)}
                className="btn-pill"
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontWeight: 700,
                  fontSize: '0.75rem',
                  color: '#ffffff',
                  background: '#e8735c',
                  border: 'none',
                  padding: '8px 14px',
                  borderRadius: '100px',
                  cursor: 'pointer',
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {modalMode && (
        <aside
          role="dialog"
          aria-modal="false"
          className="fixed z-50 w-[320px] sm:w-[340px]"
          ref={editorRef}
          style={{ top: editorAnchor.top, left: editorAnchor.left }}
        >
          <div
            className="w-full p-4 sm:p-5"
            style={{
              background: 'rgba(248, 250, 242, 0.92)',
              backdropFilter: 'blur(8px)',
              border: '1px solid rgba(255, 255, 255, 0.24)',
              borderRadius: '0 16px 16px 16px',
              boxShadow: '0 20px 40px rgba(46, 52, 43, 0.12)',
            }}
          >
            <style>{`
              .event-inline-title::placeholder {
                color: #a8aea3;
                font-weight: 400;
              }
              .event-inline-location::placeholder {
                color: #a8aea3;
              }
            `}</style>
            <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.42)',
                  borderRadius: '0 12px 12px 12px',
                  padding: '10px 12px',
                }}
              >
                <input
                  id="event-title"
                  className="event-inline-title"
                  required
                  value={formTitle}
                  onChange={(e) => {
                    markInteracted()
                    setFormTitle(e.target.value)
                  }}
                  placeholder={t.titlePlaceholder}
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.92rem',
                    lineHeight: 1.4,
                    letterSpacing: '-0.005em',
                    fontWeight: 500,
                    color: '#2e342b',
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    width: '100%',
                    padding: 0,
                  }}
                />
              </div>

              <div
                style={{
                  background: 'rgba(255, 255, 255, 0.36)',
                  borderRadius: '0 12px 12px 12px',
                  padding: '8px 12px',
                }}
              >
                <input
                  id="event-location"
                  className="event-inline-location"
                  value={formLocation}
                  onChange={(e) => {
                    markInteracted()
                    setFormLocation(e.target.value)
                  }}
                  placeholder=""
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.92rem',
                    color: '#2e342b',
                    background: 'transparent',
                    border: 'none',
                    outline: 'none',
                    width: '100%',
                    padding: '4px 0',
                  }}
                />
              </div>

              {!showTimeDetails && (
                <button
                  type="button"
                  onClick={() => setShowTimeDetails(true)}
                  className="w-full text-left"
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.9375rem',
                    color: '#2e342b',
                    background: 'rgba(255, 255, 255, 0.30)',
                    border: 'none',
                    borderRadius: '0 12px 12px 12px',
                    padding: '12px 14px 11px',
                    cursor: 'pointer',
                    transition: 'all 180ms ease',
                    boxShadow: showTimeDetails ? '0 10px 24px rgba(46, 52, 43, 0.08)' : 'none',
                  }}
                >
                  <div className="space-y-1.5">
                    <span
                      style={{
                        fontFamily: 'var(--font-manrope), sans-serif',
                        fontSize: '0.9rem',
                        fontWeight: 600,
                        lineHeight: 1.4,
                        color: '#2e342b',
                      }}
                    >
                      {timeSummaryText}
                    </span>
                  </div>
                </button>
              )}

              {showTimeDetails && (
                <div ref={timeDetailsRef}>
                  <div
                    className="space-y-2"
                    style={{
                      background: 'rgba(255, 255, 255, 0.28)',
                      borderRadius: '0 12px 12px 12px',
                      padding: '12px',
                      border: 'none',
                    }}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                      <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#767d72', fontWeight: 600 }}>{t.start}</span>
                      <div className="flex items-center gap-2" data-time-input-group>
                        <input
                          id="event-start-date"
                          type="date"
                          required
                          value={formStartDate}
                          onChange={(e) => {
                            markInteracted()
                            const nextDate = e.target.value
                            setFormStartDate(nextDate)
                            setFormEndDate(nextDate)

                            const nextStartIso = combineDateAndTimeToIso(nextDate, formStartHour, formStartMinute, formStartMeridiem)
                            const currentEndIso = combineDateAndTimeToIso(nextDate, formEndHour, formEndMinute, formEndMeridiem)
                            if (!nextStartIso || !currentEndIso) return

                            if (new Date(nextStartIso).getTime() > new Date(currentEndIso).getTime()) {
                              const nextEnd = new Date(nextStartIso)
                              nextEnd.setMinutes(nextEnd.getMinutes() + 60)
                              const endParts = parseIsoToDateParts(nextEnd.toISOString())
                              setFormEndDate(endParts.date)
                              setFormEndHour(endParts.hour)
                              setFormEndMinute(endParts.minute)
                              setFormEndMeridiem(endParts.meridiem)
                              setEndTimeDraft(`${endParts.hour}:${endParts.minute} ${endParts.meridiem}`)
                            }
                          }}
                          style={appleDateStyle}
                        />
                        <div className="relative">
                          <input
                            aria-label="Start time"
                            value={startTimeDraft}
                            onFocus={() => setActiveTimeSuggestions('start')}
                            onChange={(e) => {
                              markInteracted()
                              const nextValue = e.target.value
                              setStartTimeDraft(nextValue)
                              const parsed = parseTypedTime(nextValue)
                              if (parsed) {
                                setFormStartHour(parsed.hour)
                                setFormStartMinute(parsed.minute)
                                setFormStartMeridiem(parsed.meridiem)

                                const nextStartIso = combineDateAndTimeToIso(formStartDate, parsed.hour, parsed.minute, parsed.meridiem)
                                const currentEndIso = combineDateAndTimeToIso(
                                  formEndDate || formStartDate,
                                  formEndHour,
                                  formEndMinute,
                                  formEndMeridiem,
                                )
                                if (!nextStartIso || !currentEndIso) return

                                if (new Date(nextStartIso).getTime() > new Date(currentEndIso).getTime()) {
                                  const nextEnd = new Date(nextStartIso)
                                  nextEnd.setMinutes(nextEnd.getMinutes() + 60)
                                  const endParts = parseIsoToDateParts(nextEnd.toISOString())
                                  setFormEndDate(endParts.date)
                                  setFormEndHour(endParts.hour)
                                  setFormEndMinute(endParts.minute)
                                  setFormEndMeridiem(endParts.meridiem)
                                  setEndTimeDraft(`${endParts.hour}:${endParts.minute} ${endParts.meridiem}`)
                                }
                              }
                            }}
                            onBlur={commitStartTimeDraft}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault()
                                ;(e.currentTarget as HTMLInputElement).blur()
                              }
                            }}
                            placeholder="9:00 AM"
                            style={appleTimeStyle}
                          />

                          {activeTimeSuggestions === 'start' && (
                            <div
                              data-time-suggestion-menu
                              className="absolute right-0 mt-1 w-[164px] max-h-52 overflow-y-auto z-20"
                              onMouseDown={(e) => {
                                e.preventDefault()
                                e.stopPropagation()
                              }}
                              style={{
                                background: '#ffffff',
                                borderRadius: '0 12px 12px 12px',
                                border: '1px solid rgba(173, 180, 168, 0.24)',
                                boxShadow: '0 20px 40px rgba(46, 52, 43, 0.14)',
                                padding: '6px',
                              }}
                            >
                              {nearbyStartSlots.map((slot) => (
                                <button
                                  data-time-suggestion-option
                                  key={`start-nearby-${slot.value}`}
                                  type="button"
                                  onMouseDown={(e) => {
                                    e.preventDefault()
                                    e.stopPropagation()
                                    markInteracted()
                                    applyStartSlot(slot.value)
                                    setActiveTimeSuggestions(null)
                                  }}
                                  style={{
                                    fontFamily: 'var(--font-manrope), sans-serif',
                                    fontSize: '0.8125rem',
                                    width: '100%',
                                    textAlign: 'left',
                                    border: 'none',
                                    borderRadius: '9999px',
                                    padding: '7px 10px',
                                    background: slot.value === startSlotValue ? '#d6e8ce' : 'transparent',
                                    color: '#2e342b',
                                    cursor: 'pointer',
                                  }}
                                >
                                  {slot.label}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pt-1">
                      <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#767d72', fontWeight: 600 }}>{t.end}</span>
                      <div className="flex items-center gap-2" data-time-input-group>
                        <input
                          id="event-end-date"
                          type="date"
                          value={formEndDate}
                          onChange={(e) => {
                            markInteracted()
                            setFormEndDate(e.target.value)
                          }}
                          style={{ ...appleDateStyle, opacity: formEndDate ? 1 : 0.85 }}
                        />
                        <div className="relative">
                          <input
                            aria-label="End time"
                            value={endTimeDraft}
                            onFocus={() => {
                              if (!formEndDate) return
                              setActiveTimeSuggestions('end')
                            }}
                            onChange={(e) => {
                              if (!formEndDate) return
                              markInteracted()
                              const nextValue = e.target.value
                              setEndTimeDraft(nextValue)
                              const parsed = parseTypedTime(nextValue)
                              if (parsed) {
                                setFormEndHour(parsed.hour)
                                setFormEndMinute(parsed.minute)
                                setFormEndMeridiem(parsed.meridiem)
                              }
                            }}
                            onBlur={commitEndTimeDraft}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault()
                                ;(e.currentTarget as HTMLInputElement).blur()
                              }
                            }}
                            placeholder="10:00 AM"
                            disabled={!formEndDate}
                            style={{ ...appleTimeStyle, opacity: formEndDate ? 1 : 0.5 }}
                          />

                          {activeTimeSuggestions === 'end' && formEndDate && (
                            <div
                              data-time-suggestion-menu
                              className="absolute right-0 mt-1 w-[164px] max-h-52 overflow-y-auto z-20"
                              onMouseDown={(e) => {
                                e.preventDefault()
                                e.stopPropagation()
                              }}
                              style={{
                                background: '#ffffff',
                                borderRadius: '0 12px 12px 12px',
                                border: '1px solid rgba(173, 180, 168, 0.24)',
                                boxShadow: '0 20px 40px rgba(46, 52, 43, 0.14)',
                                padding: '6px',
                              }}
                            >
                              {nearbyEndSlots.map((slot) => (
                                <button
                                  data-time-suggestion-option
                                  key={`end-nearby-${slot.value}`}
                                  type="button"
                                  onMouseDown={(e) => {
                                    e.preventDefault()
                                    e.stopPropagation()
                                    markInteracted()
                                    applyEndSlot(slot.value)
                                    setActiveTimeSuggestions(null)
                                  }}
                                  style={{
                                    fontFamily: 'var(--font-manrope), sans-serif',
                                    fontSize: '0.8125rem',
                                    width: '100%',
                                    textAlign: 'left',
                                    border: 'none',
                                    borderRadius: '9999px',
                                    padding: '7px 10px',
                                    background: slot.value === endSlotValue ? '#d6e8ce' : 'transparent',
                                    color: '#2e342b',
                                    cursor: 'pointer',
                                  }}
                                >
                                  {slot.label}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <label className="flex items-center gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formAllDay}
                  onChange={(e) => {
                    markInteracted()
                    setFormAllDay(e.target.checked)
                  }}
                  className="rounded"
                  style={{ accentColor: '#4b6646' }}
                />
                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#2e342b' }}>{t.allDay}</span>
              </label>

              <div className="pt-1">
                <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
                  {createMut.isPending || updateMut.isPending ? 'Autosaving...' : 'Changes save automatically'}
                </p>
              </div>
            </form>
          </div>
        </aside>
      )}
    </div>
  )
}
