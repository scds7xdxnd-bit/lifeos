'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight } from 'lucide-react'

import { calendarApi, type CalendarEvent, type CreateEventInput } from '@/lib/api/calendar'
import { getAppTranslations } from '@/lib/translations/app'
import { useLang } from '@/lib/useLang'
import {
  type Meridiem,
  type DayEventSegment,
  type DayTimelineBlock,
  DEFAULT_EVENT_COLOR,
  getEventColorHex,
  hexToRgba,
  darkenHex,
  getCalendarLocale,
  toDateKey,
  startOfMonth,
  buildMonthGrid,
  buildWeekGrid,
  buildYearMonths,
  parseIsoToDateParts,
  combineDateAndTimeToIso,
  formatSummaryRange,
  shiftIsoByDays,
  startOfDayLocal,
  addDaysLocal,
  resolveEventInterval,
  formatHourLabel24,
  TIME_SLOT_OPTIONS,
  toSlotIndex,
  buildNearbySlots,
  parseTypedTime,
} from './calendar-utils'

type ViewMode = 'year' | 'month' | 'week' | 'day'
type ModalMode = 'create' | 'edit' | null
type EditorAnchor = { top: number; left: number }
type ActiveTimeSuggestions = 'start' | 'end' | null

type CalendarQueryData = {
  ok: boolean
  events: CalendarEvent[]
}

const QUERY_KEY = ['calendar-events'] as const
const EDITOR_WIDTH = 340

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
  const calendarLocale = getCalendarLocale(lang)
  const qc = useQueryClient()
  const viewLabels: Record<ViewMode, string> = {
    year: t.year,
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
  const [formColor, setFormColor] = useState(DEFAULT_EVENT_COLOR)
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
      color?: string
    }) =>
      calendarApi.update(input.id, {
        title: input.title,
        start_time: input.start_time,
        end_time: input.end_time,
        location: input.location,
        all_day: input.all_day,
        color: input.color,
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
                  color: input.color ?? null,
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
        color: formColor,
      }
    })
  }, [events, modalMode, editingEventId, formTitle, draftStartIso, formEndDate, draftEndIso, formLocation, formAllDay, formColor])

  const selectedKey = toDateKey(selectedDate)
  const todayKey = toDateKey(new Date())

  const daySegmentsByKey = useMemo(() => {
    const grouped = new Map<string, DayEventSegment[]>()

    for (const event of displayedEvents) {
      const interval = resolveEventInterval(event)
      if (!interval) continue

      const spanStart = startOfDayLocal(interval.start)
      const spanEndInclusive = new Date(interval.end.getTime() - 1)
      const spanEnd = startOfDayLocal(spanEndInclusive)

      for (let cursor = new Date(spanStart); cursor.getTime() <= spanEnd.getTime(); cursor = addDaysLocal(cursor, 1)) {
        const dayKey = toDateKey(cursor)
        const dayStart = startOfDayLocal(cursor)
        const dayEnd = addDaysLocal(dayStart, 1)
        const segmentStart = new Date(Math.max(interval.start.getTime(), dayStart.getTime()))
        const segmentEnd = new Date(Math.min(interval.end.getTime(), dayEnd.getTime()))

        const segment: DayEventSegment = {
          event,
          segmentStart,
          segmentEnd,
          isAllDay: Boolean(event.all_day),
          continuesBefore: interval.start.getTime() < dayStart.getTime(),
          continuesAfter: interval.end.getTime() > dayEnd.getTime(),
        }

        const bucket = grouped.get(dayKey)
        if (bucket) {
          bucket.push(segment)
        } else {
          grouped.set(dayKey, [segment])
        }
      }
    }

    for (const [key, value] of grouped.entries()) {
      grouped.set(
        key,
        [...value].sort((a, b) => {
          if (a.isAllDay !== b.isAllDay) return a.isAllDay ? -1 : 1
          return a.segmentStart.getTime() - b.segmentStart.getTime()
        }),
      )
    }

    return grouped
  }, [displayedEvents])

  const selectedDaySegments = daySegmentsByKey.get(selectedKey) ?? []
  const selectedDayAllDaySegments = selectedDaySegments.filter((segment) => segment.isAllDay)

  const selectedDayTimelineBlocks = useMemo(() => {
    const dayStart = startOfDayLocal(selectedDate)
    const dayEnd = addDaysLocal(dayStart, 1)
    const dayStartMs = dayStart.getTime()
    const dayEndMs = dayEnd.getTime()

    const raw: DayTimelineBlock[] = []
    for (const event of displayedEvents) {
      if (event.all_day) continue

      const interval = resolveEventInterval(event)
      if (!interval) continue
      if (interval.end.getTime() <= dayStartMs || interval.start.getTime() >= dayEndMs) continue

      const clippedStartMs = Math.max(interval.start.getTime(), dayStartMs)
      const clippedEndMs = Math.min(interval.end.getTime(), dayEndMs)
      const startMinute = Math.max(0, Math.floor((clippedStartMs - dayStartMs) / 60000))
      const endMinute = Math.min(1440, Math.ceil((clippedEndMs - dayStartMs) / 60000))
      const safeEndMinute = Math.max(endMinute, Math.min(1440, startMinute + 30))

      raw.push({
        event,
        startMinute,
        endMinute: safeEndMinute,
        startsBeforeDay: interval.start.getTime() < dayStartMs,
        endsAfterDay: interval.end.getTime() > dayEndMs,
        column: 0,
        columnCount: 1,
      })
    }

    const sorted = [...raw].sort((a, b) => {
      if (a.startMinute !== b.startMinute) return a.startMinute - b.startMinute
      return (a.endMinute - a.startMinute) - (b.endMinute - b.startMinute)
    })

    const positioned: DayTimelineBlock[] = []
    let cluster: DayTimelineBlock[] = []
    let clusterEndMinute = -1

    const flushCluster = () => {
      if (cluster.length === 0) return

      const columnsEnd: number[] = []
      let clusterColumnCount = 1

      for (const item of cluster) {
        let column = 0
        while (column < columnsEnd.length && columnsEnd[column] > item.startMinute) {
          column += 1
        }
        columnsEnd[column] = item.endMinute
        item.column = column
        clusterColumnCount = Math.max(clusterColumnCount, column + 1)
      }

      for (const item of cluster) {
        positioned.push({ ...item, columnCount: clusterColumnCount })
      }

      cluster = []
      clusterEndMinute = -1
    }

    for (const item of sorted) {
      if (cluster.length === 0) {
        cluster.push(item)
        clusterEndMinute = item.endMinute
        continue
      }

      if (item.startMinute < clusterEndMinute) {
        cluster.push(item)
        clusterEndMinute = Math.max(clusterEndMinute, item.endMinute)
        continue
      }

      flushCluster()
      cluster.push(item)
      clusterEndMinute = item.endMinute
    }

    flushCluster()
    return positioned
  }, [displayedEvents, selectedDate])
  const monthCells = useMemo(() => buildMonthGrid(monthAnchor), [monthAnchor])
  const yearMonths = useMemo(() => buildYearMonths(monthAnchor), [monthAnchor])
  const weekCells = useMemo(() => buildWeekGrid(selectedDate), [selectedDate])

  const rangeLabel = useMemo(() => {
    if (viewMode === 'year') {
      return monthAnchor.toLocaleDateString(calendarLocale, { year: 'numeric' })
    }

    if (viewMode === 'month') {
      return monthAnchor.toLocaleDateString(calendarLocale, { month: 'long', year: 'numeric' })
    }

    if (viewMode === 'week') {
      const start = weekCells[0]
      const end = weekCells[6]
      const left = start.toLocaleDateString(calendarLocale, { month: 'short', day: 'numeric' })
      const right = end.toLocaleDateString(calendarLocale, { month: 'short', day: 'numeric', year: 'numeric' })
      return `${left} - ${right}`
    }

    return selectedDate.toLocaleDateString(calendarLocale, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
  }, [viewMode, monthAnchor, selectedDate, weekCells, calendarLocale])

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
    setFormColor(DEFAULT_EVENT_COLOR)
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
    setFormColor(DEFAULT_EVENT_COLOR)
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
    setFormColor(DEFAULT_EVENT_COLOR)
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
    setFormColor(getEventColorHex(ev.color))
    setShowTimeDetails(false)
    setHasInteractedWithForm(false)
    setModalMode('edit')
  }

  function shiftRange(delta: number) {
    if (viewMode === 'year') {
      setMonthAnchor((prev) => new Date(prev.getFullYear() + delta, prev.getMonth(), 1))
      setSelectedDate((prev) => new Date(prev.getFullYear() + delta, prev.getMonth(), prev.getDate()))
      return
    }

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
    if (viewMode === 'month' || viewMode === 'year') {
      setMonthAnchor(startOfMonth(day))
    }
  }

  function renderYearMiniMonth(monthStart: Date) {
    const monthCellsLocal = buildMonthGrid(monthStart)
    const monthLabel = monthStart.toLocaleDateString(calendarLocale, { month: 'long' })
    const monthIndex = monthStart.getMonth()

    return (
      <div key={`year-month-${monthStart.getFullYear()}-${monthIndex}`}>
        <h3
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '1rem',
            fontWeight: 600,
            color: '#4b6646',
            letterSpacing: '-0.02em',
            marginBottom: '8px',
          }}
        >
          {monthLabel}
        </h3>

        <div className="grid grid-cols-7">
          {weekdayLabels.map((label) => (
            <div
              key={`year-weekday-${monthIndex}-${label}`}
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.66rem',
                fontWeight: 600,
                color: '#8f958c',
                textAlign: 'center',
                lineHeight: 1,
                paddingBottom: '2px',
              }}
            >
              {label.slice(0, 1)}
            </div>
          ))}

          {monthCellsLocal.map((day) => {
            const dayKey = toDateKey(day)
            const isToday = dayKey === todayKey
            const isInMonth = day.getMonth() === monthIndex
            const isWeekend = day.getDay() === 0 || day.getDay() === 6

            return (
              <button
                key={`year-day-${dayKey}`}
                type="button"
                onClick={() => selectDay(day)}
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.684rem',
                  fontWeight: 600,
                  color: isToday ? '#ffffff' : isInMonth ? (isWeekend ? '#6e7a68' : '#51574f') : '#8a9486',
                  border: 'none',
                  background: isToday ? '#4b6646' : 'transparent',
                  width: '26px',
                  height: '26px',
                  borderRadius: '9999px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  margin: '0 auto',
                  lineHeight: 1,
                }}
                aria-label={day.toLocaleDateString(calendarLocale, { weekday: 'long', month: 'long', day: 'numeric' })}
              >
                {day.getDate()}
              </button>
            )
          })}
        </div>
      </div>
    )
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
      color: ev.color ?? undefined,
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
      color: formColor,
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
    formColor,
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

  function renderEventsPreview(day: Date, maxItems: number) {
    const dayKey = toDateKey(day)
    const daySegments = daySegmentsByKey.get(dayKey) ?? []
    if (daySegments.length === 0) return null

    const dayStart = startOfDayLocal(day)
    const rowEndExclusive = addDaysLocal(dayStart, 7 - day.getDay())
    const laneHeightPx = 17

    const segmentsWithMeta = daySegments
      .map((segment) => {
        const ev = segment.event
        const interval = resolveEventInterval(ev)
        if (!interval) return null

        const eventStartDay = startOfDayLocal(interval.start)
        const eventEndDayExclusive = startOfDayLocal(interval.end)
        const totalDays = Math.max(1, Math.round((eventEndDayExclusive.getTime() - eventStartDay.getTime()) / 86400000))
        const isMultiDay = totalDays > 1 || segment.continuesBefore || segment.continuesAfter
        const startsVisibleBar = !segment.continuesBefore || day.getDay() === 0
        if (!startsVisibleBar) return null

        const renderedEndMs = Math.min(interval.end.getTime(), rowEndExclusive.getTime())
        const renderedEndInclusive = new Date(renderedEndMs - 1)
        const renderedEndDay = startOfDayLocal(renderedEndInclusive)
        const spanDays = Math.max(1, Math.round((renderedEndDay.getTime() - dayStart.getTime()) / 86400000) + 1)
        const continuesToNextRow = interval.end.getTime() > rowEndExclusive.getTime()
        const labelText = !segment.continuesBefore || day.getDay() === 0 ? ev.title : ''

        const leftRounded = !segment.continuesBefore
        const rightRounded = !continuesToNextRow
        let chipRadius = '8px'
        if (leftRounded && !rightRounded) chipRadius = '9999px 6px 6px 9999px'
        else if (!leftRounded && rightRounded) chipRadius = '6px 9999px 9999px 6px'
        else if (!leftRounded && !rightRounded) chipRadius = '6px'

        return {
          segment,
          chipRadius,
          labelText,
          spanDays,
          isMultiDay,
        }
      })
      .filter((entry): entry is NonNullable<typeof entry> => entry !== null)

    const multiDaySegmentsForDay = daySegments
      .filter((segment) => {
        const interval = resolveEventInterval(segment.event)
        if (!interval) return false
        const eventStartDay = startOfDayLocal(interval.start)
        const eventEndDayExclusive = startOfDayLocal(interval.end)
        const totalDays = Math.max(1, Math.round((eventEndDayExclusive.getTime() - eventStartDay.getTime()) / 86400000))
        return totalDays > 1 || segment.continuesBefore || segment.continuesAfter
      })
      .sort((a, b) => {
        const aStart = new Date(a.event.start_time).getTime()
        const bStart = new Date(b.event.start_time).getTime()
        if (aStart !== bStart) return aStart - bStart
        return a.event.id - b.event.id
      })

    const visibleMultiCoverage = multiDaySegmentsForDay.slice(0, maxItems)
    const visibleMultiEventIds = new Set(visibleMultiCoverage.map((segment) => segment.event.id))
    const shownMultiEntries = segmentsWithMeta.filter((entry) => entry.isMultiDay && visibleMultiEventIds.has(entry.segment.event.id))

    const remainingSlots = Math.max(0, maxItems - visibleMultiCoverage.length)
    const regularEntries = segmentsWithMeta.filter((entry) => !entry.isMultiDay)
    const shownRegularEntries = regularEntries.slice(0, remainingSlots)

    const totalRenderableSegments = multiDaySegmentsForDay.length + regularEntries.length
    const shownCount = visibleMultiCoverage.length + shownRegularEntries.length
    const hiddenCount = Math.max(0, totalRenderableSegments - shownCount)
    const shownMultiLaneByEventId = new Map<number, number>()
    visibleMultiCoverage.forEach((segment, idx) => {
      shownMultiLaneByEventId.set(segment.event.id, idx)
    })

    return (
      <div className="space-y-0.5" style={{ position: 'relative', zIndex: 1 }}>
        {visibleMultiCoverage.length > 0 && (
          <div
            style={{
              position: 'relative',
              height: `${visibleMultiCoverage.length * laneHeightPx}px`,
            }}
          >
            {shownMultiEntries.map(({ segment, chipRadius, labelText, spanDays }) => {
              const ev = segment.event
              const lane = shownMultiLaneByEventId.get(ev.id) ?? 0
              const eventColor = getEventColorHex(ev.color)
              const indicatorColor = darkenHex(eventColor, 0.22)

              return (
                <button
                  key={`preview-${ev.id}-${dayKey}`}
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setActiveEventId(ev.id)
                    selectDay(day)
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
                    position: 'absolute',
                    top: `${lane * laneHeightPx}px`,
                    left: 0,
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.625rem',
                    color: '#465642',
                    background: activeEventId === ev.id ? hexToRgba(eventColor, 0.28) : hexToRgba(eventColor, 0.22),
                    borderRadius: chipRadius,
                    padding: '0 6px',
                    height: '16px',
                    lineHeight: '16px',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    width: `calc(${spanDays * 100}% + ${Math.max(0, spanDays - 1)}px)`,
                    textAlign: 'left',
                    transition: 'all 180ms ease',
                    opacity: draggingEventId === ev.id ? 0.55 : 1,
                    zIndex: 2,
                  }}
                  title={ev.title}
                >
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      width: '100%',
                      minWidth: 0,
                    }}
                  >
                    <span
                      aria-hidden="true"
                      style={{
                        width: '5px',
                        height: '5px',
                        borderRadius: '9999px',
                        background: indicatorColor,
                        flexShrink: 0,
                      }}
                    />
                    <span
                      style={{
                        minWidth: 0,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {labelText || '\u00A0'}
                    </span>
                  </span>
                </button>
              )
            })}
          </div>
        )}

        {shownRegularEntries.map(({ segment, chipRadius, labelText, spanDays }) => {
          const ev = segment.event
          const indicatorColor = getEventColorHex(ev.color)

          return (
            <button
              key={`preview-${ev.id}-${dayKey}`}
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                setActiveEventId(ev.id)
                selectDay(day)
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
                color: '#465642',
                background: activeEventId === ev.id ? hexToRgba(indicatorColor, 0.14) : 'transparent',
                borderRadius: chipRadius,
                border: '1px solid transparent',
                boxSizing: 'border-box',
                padding: '0 6px',
                height: '16px',
                lineHeight: '16px',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                width: `calc(${spanDays * 100}% + ${Math.max(0, spanDays - 1)}px)`,
                textAlign: 'left',
                transition: 'all 180ms ease',
                opacity: draggingEventId === ev.id ? 0.55 : 1,
                position: 'relative',
                zIndex: 1,
              }}
              title={ev.title}
            >
              <span
                aria-hidden="true"
                style={{
                  width: '5px',
                  height: '5px',
                  borderRadius: '9999px',
                  background: indicatorColor,
                  flexShrink: 0,
                }}
              />
              <span
                style={{
                  minWidth: 0,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {labelText || '\u00A0'}
              </span>
            </button>
          )
        })}

        {hiddenCount > 0 && (
          <div
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.625rem',
              color: '#767d72',
              paddingLeft: '2px',
            }}
          >
            +{hiddenCount} more
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
    const isWeekend = day.getDay() === 0 || day.getDay() === 6
    const dayHeaderHeight = 22
    const stackTopGap = compact ? 4 : 6
    const verticalPadding = compact ? 12 : 16
    const eventRowHeight = 16
    const eventRowGap = 2
    const moreLabelHeight = 12
    const moreLabelGap = 2
    const reservedStackHeight = eventRowHeight * 3 + eventRowGap * 2 + moreLabelGap + moreLabelHeight
    const minCellHeight = verticalPadding + dayHeaderHeight + stackTopGap + reservedStackHeight

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
          minHeight: `${minCellHeight}px`,
          border: 'none',
          cursor: 'pointer',
          borderRadius: 0,
          background: isCurrentMonth ? '#ffffff' : '#f7f9f5',
          padding: compact ? '6px 7px' : '8px',
          boxShadow: isDragTarget ? '0 0 0 2px rgba(75, 102, 70, 0.35) inset' : 'none',
          opacity: isCurrentMonth || viewMode !== 'month' ? 1 : 0.82,
        }}
      >
        <div
          className="flex items-center justify-between"
          style={{
            position: 'relative',
            zIndex: 3,
            minHeight: '22px',
          }}
        >
          <span
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontWeight: isToday ? 700 : 600,
              fontSize: '0.81rem',
              color: isToday ? '#3f5a3a' : isCurrentMonth ? (isWeekend ? '#6e7a68' : '#465642') : '#8a9486',
              border: isToday ? '1.5px solid #4b6646' : 'none',
              borderRadius: '9999px',
              minWidth: '22px',
              height: '22px',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: isToday ? '0 7px' : '0 4px',
              lineHeight: 1,
            }}
          >
            {day.getDate()}
          </span>
        </div>

        <div style={{ marginTop: compact ? '4px' : '6px' }}>{renderEventsPreview(day, 3)}</div>
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
          <div className="flex items-center justify-center gap-2">
            {(['day', 'week', 'month', 'year'] as ViewMode[]).map((mode) => (
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

          <div className="flex items-start justify-between gap-3">
            <h2
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: viewMode === 'year' ? '1.68rem' : '1.25rem',
                fontWeight: viewMode === 'year' ? 700 : 500,
                color: '#4b6646',
                letterSpacing: '-0.03em',
                lineHeight: 1,
              }}
            >
              {rangeLabel}
            </h2>

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
          </div>
        </div>

        {viewMode !== 'day' && viewMode !== 'year' && (
          <div
            className="grid grid-cols-7 gap-px mb-2 rounded-lg overflow-hidden"
            style={{ background: '#dfe6da' }}
          >
            {weekdayLabels.map((label) => (
              <div
                key={label}
                className="text-center"
                style={{
                  ...microLabel,
                  fontSize: '0.625rem',
                  padding: '8px 0',
                  background: '#f7f9f5',
                }}
              >
                {label}
              </div>
            ))}
          </div>
        )}

        {viewMode === 'year' && (
          <div
            className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-x-10 gap-y-8"
            style={{ padding: '4px 2px' }}
          >
            {yearMonths.map((monthStart) => renderYearMiniMonth(monthStart))}
          </div>
        )}

        {viewMode === 'month' && (
          <div className="rounded-lg overflow-hidden" style={{ background: '#dfe6da' }}>
            <div className="grid grid-cols-7 gap-px">{monthCells.map((day) => renderDayCell(day, true))}</div>
          </div>
        )}

        {viewMode === 'week' && (
          <div className="rounded-lg overflow-hidden" style={{ background: '#dfe6da' }}>
            <div className="grid grid-cols-7 gap-px">{weekCells.map((day) => renderDayCell(day, false))}</div>
          </div>
        )}

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
              {selectedDate.toLocaleDateString(calendarLocale, { weekday: 'long', month: 'short', day: 'numeric' })}
            </h3>

            {selectedDayAllDaySegments.length > 0 && (
              <div className="mb-3 space-y-1.5">
                <p style={{ ...microLabel, marginBottom: '4px' }}>{t.allDay}</p>
                <div className="flex flex-wrap gap-1.5">
                  {selectedDayAllDaySegments.map((segment) => {
                    const ev = segment.event
                    const eventColor = getEventColorHex(ev.color)
                    const labelText = segment.continuesBefore ? '' : ev.title
                    const isMultiDay = segment.continuesBefore || segment.continuesAfter

                    let chipRadius = '9999px'
                    if (isMultiDay && !segment.continuesBefore && segment.continuesAfter) {
                      chipRadius = '9999px 6px 6px 9999px'
                    } else if (isMultiDay && segment.continuesBefore && !segment.continuesAfter) {
                      chipRadius = '6px 9999px 9999px 6px'
                    } else if (isMultiDay && segment.continuesBefore && segment.continuesAfter) {
                      chipRadius = '6px'
                    }

                    return (
                      <button
                        key={`day-all-day-${ev.id}-${selectedKey}`}
                        type="button"
                        onClick={() => setActiveEventId(ev.id)}
                        onDoubleClick={(e) => openEditModal(ev, e.currentTarget)}
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
                        style={{
                          border: 'none',
                          borderRadius: chipRadius,
                          background: activeEventId === ev.id ? hexToRgba(eventColor, 0.28) : hexToRgba(eventColor, 0.22),
                          color: '#465642',
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontSize: '0.75rem',
                          padding: '4px 10px',
                          minWidth: labelText ? undefined : '26px',
                          cursor: 'pointer',
                          opacity: draggingEventId === ev.id ? 0.55 : 1,
                        }}
                        title={ev.title}
                      >
                        {labelText || '\u00A0'}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            <div
              style={{
                borderRadius: '0 12px 12px 12px',
                background: '#ffffff',
                boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
                overflow: 'hidden',
              }}
            >
              <div className="grid" style={{ gridTemplateColumns: '56px 1fr' }}>
                <div style={{ background: '#f7f9f5' }}>
                  {Array.from({ length: 24 }, (_, hour) => (
                    <div
                      key={`hour-label-${hour}`}
                      style={{
                        height: '56px',
                        padding: '6px 8px 0',
                        fontFamily: 'var(--font-manrope), sans-serif',
                        fontSize: '0.625rem',
                        color: '#767d72',
                        borderTop: hour === 0 ? 'none' : '1px solid rgba(173, 180, 168, 0.16)',
                      }}
                    >
                      {formatHourLabel24(hour)}
                    </div>
                  ))}
                </div>

                <div
                  className="relative"
                  style={{
                    height: `${24 * 56}px`,
                    background: '#ffffff',
                  }}
                >
                  {Array.from({ length: 24 }, (_, hour) => (
                    <div
                      key={`hour-line-${hour}`}
                      style={{
                        position: 'absolute',
                        top: `${hour * 56}px`,
                        left: 0,
                        right: 0,
                        borderTop: hour === 0 ? 'none' : '1px solid rgba(173, 180, 168, 0.16)',
                      }}
                    />
                  ))}

                  {selectedDayTimelineBlocks.map((block) => {
                    const eventColor = getEventColorHex(block.event.color)
                    const duration = block.endMinute - block.startMinute
                    const topPx = (block.startMinute / 60) * 56
                    const heightPx = Math.max((duration / 60) * 56, 24)
                    const laneGap = 4
                    const widthExpr = `calc((100% - ${(block.columnCount + 1) * laneGap}px) / ${block.columnCount})`
                    const leftExpr = `calc(${laneGap}px + ${block.column} * (${widthExpr} + ${laneGap}px))`
                    const labelPrefix = block.startsBeforeDay ? '... ' : ''
                    const labelSuffix = block.endsAfterDay ? ' ...' : ''

                    return (
                      <button
                        key={`timeline-${block.event.id}-${block.startMinute}`}
                        type="button"
                        onClick={() => setActiveEventId(block.event.id)}
                        onDoubleClick={(e) => openEditModal(block.event, e.currentTarget)}
                        style={{
                          position: 'absolute',
                          top: `${topPx}px`,
                          left: leftExpr,
                          width: widthExpr,
                          minHeight: `${heightPx}px`,
                          border: `1px solid ${hexToRgba(eventColor, 0.35)}`,
                          borderRadius: '8px',
                          background: activeEventId === block.event.id ? hexToRgba(eventColor, 0.26) : hexToRgba(eventColor, 0.20),
                          color: '#2e342b',
                          padding: '5px 6px',
                          textAlign: 'left',
                          cursor: 'pointer',
                          overflow: 'hidden',
                        }}
                        title={block.event.title}
                      >
                        <span
                          style={{
                            display: 'block',
                            fontFamily: 'var(--font-manrope), sans-serif',
                            fontSize: '0.6875rem',
                            fontWeight: 700,
                            lineHeight: 1.25,
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                        >
                          {`${labelPrefix}${block.event.title}${labelSuffix}`}
                        </span>
                      </button>
                    )
                  })}

                  {selectedDayTimelineBlocks.length === 0 && selectedDayAllDaySegments.length === 0 && (
                    <p
                      style={{
                        position: 'absolute',
                        top: '10px',
                        left: '12px',
                        fontSize: '0.8125rem',
                        color: '#767d72',
                      }}
                    >
                      {t.noEvents}
                    </p>
                  )}
                </div>
              </div>
            </div>
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
                <div className="flex items-center gap-2">
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

                  <label
                    htmlFor="event-color"
                    style={{
                      width: 20,
                      height: 20,
                      borderRadius: '9999px',
                      overflow: 'hidden',
                      border: '1px solid rgba(173, 180, 168, 0.28)',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                    }}
                    title="Event color"
                  >
                    <input
                      id="event-color"
                      type="color"
                      value={formColor}
                      onChange={(e) => {
                        markInteracted()
                        setFormColor(e.target.value)
                      }}
                      aria-label="Event color"
                      style={{
                        width: 24,
                        height: 24,
                        border: 'none',
                        padding: 0,
                        background: 'transparent',
                        cursor: 'pointer',
                      }}
                    />
                  </label>
                </div>
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
