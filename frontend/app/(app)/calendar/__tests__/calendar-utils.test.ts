import { describe, it, expect } from 'vitest'
import {
  toDateKey,
  startOfDayLocal,
  addDaysLocal,
  resolveEventInterval,
  buildMonthGrid,
  buildWeekGrid,
  buildYearMonths,
  getEventColorHex,
  darkenHex,
  hexToRgba,
  combineDateAndTimeToIso,
  parseIsoToDateParts,
  formatSummaryRange,
  parseTypedTime,
  shiftIsoByDays,
  formatHourLabel24,
  DEFAULT_EVENT_COLOR,
} from '../calendar-utils'
import type { CalendarEvent } from '@/lib/api/calendar'

function makeEvent(overrides: Partial<CalendarEvent> & { start_time: string }): CalendarEvent {
  return {
    id: 1,
    title: 'Test',
    description: null,
    end_time: null,
    all_day: false,
    location: null,
    source: 'local',
    color: null,
    is_private: false,
    tags: [],
    duration_minutes: null,
    created_at: new Date().toISOString(),
    ...overrides,
  } as CalendarEvent
}

// ---------------------------------------------------------------------------
// Date key & day helpers
// ---------------------------------------------------------------------------

describe('toDateKey', () => {
  it('formats a local date as YYYY-MM-DD', () => {
    const d = new Date(2025, 0, 5) // Jan 5 2025 local
    expect(toDateKey(d)).toBe('2025-01-05')
  })

  it('pads single-digit month and day', () => {
    const d = new Date(2025, 2, 9) // Mar 9
    expect(toDateKey(d)).toBe('2025-03-09')
  })

  it('uses local date parts, not UTC', () => {
    // Construct a date at 11pm local — in UTC-offset zones this could be the next UTC day
    const d = new Date(2025, 5, 15, 23, 30, 0)
    expect(toDateKey(d)).toBe('2025-06-15')
  })
})

describe('startOfDayLocal', () => {
  it('zeroes hours, minutes, seconds, milliseconds', () => {
    const d = new Date(2025, 3, 10, 14, 35, 22, 999)
    const sod = startOfDayLocal(d)
    expect(sod.getHours()).toBe(0)
    expect(sod.getMinutes()).toBe(0)
    expect(sod.getSeconds()).toBe(0)
    expect(sod.getMilliseconds()).toBe(0)
    expect(sod.getDate()).toBe(10)
  })

  it('does not mutate the original date', () => {
    const d = new Date(2025, 3, 10, 14, 35)
    startOfDayLocal(d)
    expect(d.getHours()).toBe(14)
  })
})

describe('addDaysLocal', () => {
  it('adds positive days', () => {
    const d = new Date(2025, 0, 30)
    const result = addDaysLocal(d, 3)
    expect(result.getDate()).toBe(2)
    expect(result.getMonth()).toBe(1) // Feb
  })

  it('subtracts days with negative values', () => {
    const d = new Date(2025, 1, 1) // Feb 1
    const result = addDaysLocal(d, -1)
    expect(result.getMonth()).toBe(0) // Jan
    expect(result.getDate()).toBe(31)
  })

  it('does not mutate the original date', () => {
    const d = new Date(2025, 0, 15)
    addDaysLocal(d, 5)
    expect(d.getDate()).toBe(15)
  })
})

// ---------------------------------------------------------------------------
// resolveEventInterval
// ---------------------------------------------------------------------------

describe('resolveEventInterval', () => {
  it('returns start and end for a normal event', () => {
    const ev = makeEvent({
      start_time: '2025-06-15T10:00:00Z',
      end_time: '2025-06-15T11:00:00Z',
    })
    const interval = resolveEventInterval(ev)!
    expect(interval).not.toBeNull()
    expect(interval.end.getTime()).toBeGreaterThan(interval.start.getTime())
  })

  it('returns null for an invalid start_time', () => {
    const ev = makeEvent({ start_time: 'not-a-date' })
    expect(resolveEventInterval(ev)).toBeNull()
  })

  it('defaults end to start + 60min when end <= start for non-all-day', () => {
    const ev = makeEvent({
      start_time: '2025-06-15T10:00:00Z',
      end_time: '2025-06-15T09:00:00Z', // before start
    })
    const interval = resolveEventInterval(ev)!
    expect(interval.end.getTime() - interval.start.getTime()).toBe(60 * 60000)
  })

  it('defaults end to next day for all-day event without end', () => {
    const ev = makeEvent({
      start_time: '2025-06-15T00:00:00Z',
      all_day: true,
    })
    const interval = resolveEventInterval(ev)!
    const diffMs = interval.end.getTime() - startOfDayLocal(interval.start).getTime()
    // Should span exactly 1 day
    expect(diffMs).toBe(24 * 60 * 60000)
  })

  it('handles multi-day events with valid end', () => {
    const ev = makeEvent({
      start_time: '2025-06-15T10:00:00Z',
      end_time: '2025-06-17T10:00:00Z',
    })
    const interval = resolveEventInterval(ev)!
    const diffDays = (interval.end.getTime() - interval.start.getTime()) / (24 * 60 * 60000)
    expect(diffDays).toBe(2)
  })
})

// ---------------------------------------------------------------------------
// Grid builders
// ---------------------------------------------------------------------------

describe('buildMonthGrid', () => {
  it('always returns 42 cells (6 rows x 7 columns)', () => {
    const grid = buildMonthGrid(new Date(2025, 5, 1)) // June 2025
    expect(grid).toHaveLength(42)
  })

  it('starts on the Sunday of the first week', () => {
    const grid = buildMonthGrid(new Date(2025, 5, 1)) // June 2025 starts on Sunday
    expect(grid[0].getDay()).toBe(0) // Sunday
  })

  it('includes days from previous and next months as padding', () => {
    // March 2025 starts on Saturday
    const grid = buildMonthGrid(new Date(2025, 2, 1))
    // First cell should be a Sunday before March 1
    expect(grid[0].getDay()).toBe(0)
    // Last cell should be in April
    expect(grid[41].getMonth()).toBeGreaterThanOrEqual(3) // April or later
  })
})

describe('buildWeekGrid', () => {
  it('returns exactly 7 days', () => {
    const grid = buildWeekGrid(new Date(2025, 5, 11)) // a Wednesday
    expect(grid).toHaveLength(7)
  })

  it('starts on Sunday', () => {
    const grid = buildWeekGrid(new Date(2025, 5, 11))
    expect(grid[0].getDay()).toBe(0)
  })
})

describe('buildYearMonths', () => {
  it('returns 12 months starting from January', () => {
    const months = buildYearMonths(new Date(2025, 5, 15))
    expect(months).toHaveLength(12)
    expect(months[0].getMonth()).toBe(0)
    expect(months[11].getMonth()).toBe(11)
    expect(months[0].getFullYear()).toBe(2025)
  })
})

// ---------------------------------------------------------------------------
// Color utilities
// ---------------------------------------------------------------------------

describe('getEventColorHex', () => {
  it('returns a valid hex color as-is', () => {
    expect(getEventColorHex('#ff5500')).toBe('#ff5500')
  })

  it('returns default color for null/undefined', () => {
    expect(getEventColorHex(null)).toBe(DEFAULT_EVENT_COLOR)
    expect(getEventColorHex(undefined)).toBe(DEFAULT_EVENT_COLOR)
  })

  it('returns default color for invalid hex', () => {
    expect(getEventColorHex('red')).toBe(DEFAULT_EVENT_COLOR)
    expect(getEventColorHex('#fff')).toBe(DEFAULT_EVENT_COLOR) // 3-char hex not supported
  })

  it('trims whitespace', () => {
    expect(getEventColorHex('  #aabbcc  ')).toBe('#aabbcc')
  })
})

describe('darkenHex', () => {
  it('darkens a color by the given amount', () => {
    const result = darkenHex('#ffffff', 0.5)
    expect(result).toBe('#808080')
  })

  it('returns black for amount=1', () => {
    expect(darkenHex('#ff0000', 1)).toBe('#000000')
  })

  it('returns same color for amount=0', () => {
    expect(darkenHex('#aabbcc', 0)).toBe('#aabbcc')
  })
})

describe('hexToRgba', () => {
  it('converts hex to rgba', () => {
    expect(hexToRgba('#ff0000', 0.5)).toBe('rgba(255, 0, 0, 0.5)')
  })

  it('falls back to default color for invalid hex', () => {
    const result = hexToRgba('invalid', 1)
    expect(result).toMatch(/^rgba\(\d+, \d+, \d+, 1\)$/)
  })
})

// ---------------------------------------------------------------------------
// Time parsing & formatting
// ---------------------------------------------------------------------------

describe('parseTypedTime', () => {
  it('parses "9 AM"', () => {
    expect(parseTypedTime('9 AM')).toEqual({ hour: '9', minute: '00', meridiem: 'AM' })
  })

  it('parses "12:30 PM"', () => {
    expect(parseTypedTime('12:30 PM')).toEqual({ hour: '12', minute: '30', meridiem: 'PM' })
  })

  it('returns null for invalid input', () => {
    expect(parseTypedTime('25:00 AM')).toBeNull()
    expect(parseTypedTime('hello')).toBeNull()
    expect(parseTypedTime('')).toBeNull()
  })

  it('is case-insensitive', () => {
    expect(parseTypedTime('3:15 pm')).toEqual({ hour: '3', minute: '15', meridiem: 'PM' })
  })

  it('rejects hour 0', () => {
    expect(parseTypedTime('0 AM')).toBeNull()
  })

  it('rejects hour > 12', () => {
    expect(parseTypedTime('13 PM')).toBeNull()
  })
})

describe('combineDateAndTimeToIso', () => {
  it('produces a valid ISO string', () => {
    const iso = combineDateAndTimeToIso('2025-06-15', '9', '30', 'AM')
    expect(iso).toBeDefined()
    const d = new Date(iso!)
    expect(d.getHours()).toBe(9)
    expect(d.getMinutes()).toBe(30)
  })

  it('handles PM correctly', () => {
    const iso = combineDateAndTimeToIso('2025-06-15', '2', '00', 'PM')
    const d = new Date(iso!)
    expect(d.getHours()).toBe(14)
  })

  it('handles 12 AM as midnight', () => {
    const iso = combineDateAndTimeToIso('2025-06-15', '12', '00', 'AM')
    const d = new Date(iso!)
    expect(d.getHours()).toBe(0)
  })

  it('handles 12 PM as noon', () => {
    const iso = combineDateAndTimeToIso('2025-06-15', '12', '00', 'PM')
    const d = new Date(iso!)
    expect(d.getHours()).toBe(12)
  })

  it('returns undefined for empty date', () => {
    expect(combineDateAndTimeToIso('', '9', '00', 'AM')).toBeUndefined()
  })

  it('returns undefined for invalid minute', () => {
    expect(combineDateAndTimeToIso('2025-06-15', '9', '99', 'AM')).toBeUndefined()
  })
})

describe('parseIsoToDateParts', () => {
  it('returns defaults for null/undefined', () => {
    const result = parseIsoToDateParts(null)
    expect(result.date).toBe('')
    expect(result.hour).toBe('9')
    expect(result.meridiem).toBe('AM')
  })

  it('parses a valid ISO string', () => {
    const d = new Date(2025, 5, 15, 14, 30) // 2:30 PM local
    const result = parseIsoToDateParts(d.toISOString())
    expect(result.hour).toBe('2')
    expect(result.minute).toBe('30')
    expect(result.meridiem).toBe('PM')
    expect(result.date).toBe('2025-06-15')
  })

  it('returns defaults for invalid ISO string', () => {
    const result = parseIsoToDateParts('not-a-date')
    expect(result.date).toBe('')
  })
})

describe('formatSummaryRange', () => {
  it('returns placeholder for missing start', () => {
    expect(formatSummaryRange(undefined, undefined, 'en')).toBe('Set start date and time')
  })

  it('formats start-only range', () => {
    const start = new Date(2025, 5, 15, 10, 0).toISOString()
    const result = formatSummaryRange(start, undefined, 'en')
    expect(result).toContain('10:00 AM')
  })

  it('formats same-day range with start and end times', () => {
    const start = new Date(2025, 5, 15, 10, 0).toISOString()
    const end = new Date(2025, 5, 15, 14, 0).toISOString()
    const result = formatSummaryRange(start, end, 'en')
    expect(result).toContain('10:00 AM')
    expect(result).toContain('2:00 PM')
    expect(result).toContain(' - ')
  })
})

describe('shiftIsoByDays', () => {
  it('shifts forward by N days', () => {
    const iso = new Date(2025, 0, 30).toISOString()
    const shifted = new Date(shiftIsoByDays(iso, 3))
    expect(shifted.getDate()).toBe(2)
    expect(shifted.getMonth()).toBe(1)
  })

  it('returns original string for invalid ISO', () => {
    expect(shiftIsoByDays('bad', 1)).toBe('bad')
  })
})

describe('formatHourLabel24', () => {
  it('pads single digit hours', () => {
    expect(formatHourLabel24(9)).toBe('09:00')
  })

  it('formats double digit hours', () => {
    expect(formatHourLabel24(14)).toBe('14:00')
  })
})
