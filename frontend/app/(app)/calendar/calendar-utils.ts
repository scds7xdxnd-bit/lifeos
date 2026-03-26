import type { CalendarEvent } from '@/lib/api/calendar'

export type Meridiem = 'AM' | 'PM'

export type DayEventSegment = {
  event: CalendarEvent
  segmentStart: Date
  segmentEnd: Date
  isAllDay: boolean
  continuesBefore: boolean
  continuesAfter: boolean
}

export type DayTimelineBlock = {
  event: CalendarEvent
  startMinute: number
  endMinute: number
  startsBeforeDay: boolean
  endsAfterDay: boolean
  column: number
  columnCount: number
}

export const DEFAULT_EVENT_COLOR = '#4f7fd8'

export function getEventColorHex(color?: string | null) {
  const normalized = (color ?? '').trim()
  if (/^#[0-9a-fA-F]{6}$/.test(normalized)) return normalized
  return DEFAULT_EVENT_COLOR
}

export function hexToRgba(hex: string, alpha: number) {
  const safe = getEventColorHex(hex)
  const r = Number.parseInt(safe.slice(1, 3), 16)
  const g = Number.parseInt(safe.slice(3, 5), 16)
  const b = Number.parseInt(safe.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

export function darkenHex(hex: string, amount = 0.18) {
  const safe = getEventColorHex(hex)
  const r = Number.parseInt(safe.slice(1, 3), 16)
  const g = Number.parseInt(safe.slice(3, 5), 16)
  const b = Number.parseInt(safe.slice(5, 7), 16)
  const factor = Math.max(0, 1 - amount)
  const nr = Math.max(0, Math.min(255, Math.round(r * factor)))
  const ng = Math.max(0, Math.min(255, Math.round(g * factor)))
  const nb = Math.max(0, Math.min(255, Math.round(b * factor)))
  const toHex = (v: number) => v.toString(16).padStart(2, '0')
  return `#${toHex(nr)}${toHex(ng)}${toHex(nb)}`
}

export function fmtDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return iso
  }
}

export function fmtTime(iso: string) {
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

export function getCalendarLocale(lang: string) {
  if (lang === 'zh') return 'zh-CN'
  if (lang === 'ko') return 'ko-KR'
  return 'en-US'
}

export function toDateKey(date: Date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

export function startOfWeek(date: Date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() - d.getDay())
  return d
}

export function buildMonthGrid(date: Date) {
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

export function buildWeekGrid(date: Date) {
  const cursor = startOfWeek(date)
  const cells: Date[] = []
  for (let i = 0; i < 7; i += 1) {
    cells.push(new Date(cursor))
    cursor.setDate(cursor.getDate() + 1)
  }
  return cells
}

export function buildYearMonths(date: Date) {
  const year = date.getFullYear()
  return Array.from({ length: 12 }, (_, idx) => new Date(year, idx, 1))
}

export function formatDateInputValue(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function parseIsoToDateParts(iso?: string | null) {
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

export function combineDateAndTimeToIso(dateValue: string, hour: string, minute: string, meridiem: Meridiem) {
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

export function formatSummaryDate(date: Date, lang: string) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  if (lang === 'ko' || lang === 'zh') {
    return `${y}/${m}/${d}`
  }
  return `${d}/${m}/${y}`
}

export function formatSummaryTime(date: Date) {
  const hour24 = date.getHours()
  const meridiem = hour24 >= 12 ? 'PM' : 'AM'
  const hour12 = hour24 % 12 === 0 ? 12 : hour24 % 12
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${hour12}:${minute} ${meridiem}`
}

export function formatSummaryRange(startIso: string | undefined, endIso: string | undefined, lang: string) {
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
  return `${startDate} ${startTime} - ${endDate} ${endTime}`
}

export function shiftIsoByDays(iso: string, days: number) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  date.setDate(date.getDate() + days)
  return date.toISOString()
}

export function startOfDayLocal(date: Date) {
  const next = new Date(date)
  next.setHours(0, 0, 0, 0)
  return next
}

export function addDaysLocal(date: Date, days: number) {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

export function resolveEventInterval(event: CalendarEvent) {
  const start = new Date(event.start_time)
  if (Number.isNaN(start.getTime())) return null

  let end = event.end_time ? new Date(event.end_time) : new Date(start)
  if (Number.isNaN(end.getTime())) {
    end = new Date(start)
  }

  if (event.all_day) {
    if (!event.end_time || end.getTime() <= start.getTime()) {
      end = addDaysLocal(startOfDayLocal(start), 1)
    }
  } else if (end.getTime() <= start.getTime()) {
    end = new Date(start)
    end.setMinutes(end.getMinutes() + 60)
  }

  return { start, end }
}

export function formatHourLabel24(hour: number) {
  return `${String(hour).padStart(2, '0')}:00`
}

export function clamp(n: number, min: number, max: number) {
  return Math.min(Math.max(n, min), max)
}

export const TIME_SLOT_OPTIONS = Array.from({ length: 48 }, (_, idx) => {
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

export function toSlotIndex(hour: string, minute: string, meridiem: Meridiem) {
  let h = Number.parseInt(hour, 10)
  const m = Number.parseInt(minute, 10)
  if (Number.isNaN(h) || h < 1 || h > 12) h = 12
  const safeMinute = Number.isNaN(m) ? 0 : clamp(Math.round(m / 30) * 30, 0, 30)
  let hour24 = h % 12
  if (meridiem === 'PM') hour24 += 12
  return clamp(hour24 * 2 + (safeMinute >= 30 ? 1 : 0), 0, TIME_SLOT_OPTIONS.length - 1)
}

export function buildNearbySlots(baseIndex: number, startOffset = 0) {
  const start = clamp(baseIndex + startOffset, 0, TIME_SLOT_OPTIONS.length - 1)
  const end = clamp(baseIndex + 6, 0, TIME_SLOT_OPTIONS.length - 1)
  return TIME_SLOT_OPTIONS.slice(start, end + 1)
}

export function parseTypedTime(value: string): { hour: string; minute: string; meridiem: Meridiem } | null {
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
