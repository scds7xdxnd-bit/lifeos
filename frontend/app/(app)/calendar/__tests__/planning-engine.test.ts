import { describe, it, expect } from 'vitest'
import {
  computeCalendarLoad,
  scoreHabits,
  scoreSkill,
  generateDailyPlan,
  resolveReasonText,
} from '../_planning/planning-engine'
import type { CalendarEvent } from '@/lib/api/calendar'
import type { Habit } from '@/lib/api/habits'
import type { Skill } from '@/lib/api/skills'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeEvent(overrides: Partial<CalendarEvent> & { start_time: string }): CalendarEvent {
  return {
    id: 1,
    title: 'Meeting',
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

function makeHabit(overrides: Partial<Habit> = {}): Habit {
  return {
    id: 1,
    name: 'Meditate',
    description: null,
    schedule_type: 'daily',
    target_count: null,
    time_of_day: null,
    scheduled_time: null,
    difficulty: null,
    is_active: true,
    count: 10,
    last_logged_date: null,
    completed_today: false,
    current_streak: 5,
    completion_rate_30d: 0.8,
    today_log_id: null,
    last_7_days: [
      { date: '2025-06-09', logged: true },
      { date: '2025-06-10', logged: true },
      { date: '2025-06-11', logged: true },
      { date: '2025-06-12', logged: true },
      { date: '2025-06-13', logged: true },
      { date: '2025-06-14', logged: false },
      { date: '2025-06-15', logged: false },
    ],
    ...overrides,
  }
}

function makeSkill(overrides: Partial<Skill> = {}): Skill {
  return {
    id: 1,
    name: 'Piano',
    category: 'Music',
    difficulty: null,
    target_level: null,
    current_level: null,
    description: null,
    tags: [],
    total_minutes: 600,
    session_count: 20,
    last_practiced_at: '2025-06-10T10:00:00Z',
    streak_days: 0,
    sessions_last_7: 0,
    sessions_last_30: 3,
    recent_sessions: [],
    ...overrides,
  }
}

const SELECTED_DATE = new Date(2025, 5, 15) // June 15, 2025

// ---------------------------------------------------------------------------
// computeCalendarLoad
// ---------------------------------------------------------------------------

describe('computeCalendarLoad', () => {
  it('returns light for an empty calendar', () => {
    const load = computeCalendarLoad([], SELECTED_DATE)
    expect(load.loadLevel).toBe('light')
    expect(load.totalEventMinutes).toBe(0)
    expect(load.eventCount).toBe(0)
    expect(load.allDayCount).toBe(0)
  })

  it('classifies < 3 hours as light', () => {
    const events = [
      makeEvent({
        id: 1,
        start_time: '2025-06-15T09:00:00',
        end_time: '2025-06-15T11:00:00',
      }),
    ]
    const load = computeCalendarLoad(events, SELECTED_DATE)
    expect(load.loadLevel).toBe('light')
    expect(load.totalEventMinutes).toBe(120)
    expect(load.eventCount).toBe(1)
  })

  it('classifies 3-6 hours as moderate', () => {
    const events = [
      makeEvent({ id: 1, start_time: '2025-06-15T08:00:00', end_time: '2025-06-15T12:00:00' }),
    ]
    const load = computeCalendarLoad(events, SELECTED_DATE)
    expect(load.loadLevel).toBe('moderate')
    expect(load.totalEventMinutes).toBe(240)
  })

  it('classifies 6+ hours as heavy', () => {
    const events = [
      makeEvent({ id: 1, start_time: '2025-06-15T08:00:00', end_time: '2025-06-15T12:00:00' }),
      makeEvent({ id: 2, start_time: '2025-06-15T13:00:00', end_time: '2025-06-15T17:00:00' }),
    ]
    const load = computeCalendarLoad(events, SELECTED_DATE)
    expect(load.loadLevel).toBe('heavy')
    expect(load.totalEventMinutes).toBe(480)
  })

  it('counts all-day events separately', () => {
    const events = [
      makeEvent({ id: 1, start_time: '2025-06-15T00:00:00', all_day: true }),
    ]
    const load = computeCalendarLoad(events, SELECTED_DATE)
    expect(load.allDayCount).toBe(1)
    expect(load.eventCount).toBe(0)
    expect(load.totalEventMinutes).toBe(0) // all-day doesn't count towards load minutes
  })

  it('clips multi-day events to the selected day', () => {
    const events = [
      makeEvent({
        id: 1,
        start_time: '2025-06-14T20:00:00',
        end_time: '2025-06-15T04:00:00',
      }),
    ]
    const load = computeCalendarLoad(events, SELECTED_DATE)
    // Only 00:00 to 04:00 counts = 240 minutes
    expect(load.totalEventMinutes).toBe(240)
  })

  it('ignores events on other days', () => {
    const events = [
      makeEvent({ id: 1, start_time: '2025-06-14T09:00:00', end_time: '2025-06-14T17:00:00' }),
    ]
    const load = computeCalendarLoad(events, SELECTED_DATE)
    expect(load.eventCount).toBe(0)
    expect(load.totalEventMinutes).toBe(0)
  })
})

// ---------------------------------------------------------------------------
// scoreHabits
// ---------------------------------------------------------------------------

describe('scoreHabits', () => {
  const lightLoad = computeCalendarLoad([], SELECTED_DATE)

  it('excludes completed habits', () => {
    const habits = [makeHabit({ completed_today: true })]
    const suggestions = scoreHabits(habits, lightLoad, SELECTED_DATE)
    expect(suggestions).toHaveLength(0)
  })

  it('excludes inactive habits', () => {
    const habits = [makeHabit({ is_active: false })]
    const suggestions = scoreHabits(habits, lightLoad, SELECTED_DATE)
    expect(suggestions).toHaveLength(0)
  })

  it('scores habits with active streaks higher', () => {
    const habits = [
      makeHabit({ id: 1, name: 'No streak', current_streak: 0 }),
      makeHabit({ id: 2, name: 'Long streak', current_streak: 10 }),
    ]
    const suggestions = scoreHabits(habits, lightLoad, SELECTED_DATE)
    expect(suggestions[0].habitName).toBe('Long streak')
    expect(suggestions[0].score).toBeGreaterThan(suggestions[1].score)
  })

  it('caps at 3 suggestions on light days', () => {
    const habits = Array.from({ length: 5 }, (_, i) =>
      makeHabit({ id: i + 1, name: `Habit ${i + 1}`, current_streak: 5 - i }),
    )
    const suggestions = scoreHabits(habits, lightLoad, SELECTED_DATE)
    expect(suggestions).toHaveLength(3)
  })

  it('caps at 2 suggestions on moderate days', () => {
    const moderateLoad = {
      totalEventMinutes: 200,
      eventCount: 2,
      allDayCount: 0,
      loadLevel: 'moderate' as const,
    }
    const habits = Array.from({ length: 5 }, (_, i) =>
      makeHabit({ id: i + 1, name: `Habit ${i + 1}`, current_streak: 5 - i }),
    )
    const suggestions = scoreHabits(habits, moderateLoad, SELECTED_DATE)
    expect(suggestions).toHaveLength(2)
  })

  it('caps at 1 suggestion on heavy days', () => {
    const heavyLoad = {
      totalEventMinutes: 400,
      eventCount: 4,
      allDayCount: 0,
      loadLevel: 'heavy' as const,
    }
    const habits = Array.from({ length: 5 }, (_, i) =>
      makeHabit({ id: i + 1, name: `Habit ${i + 1}`, current_streak: 5 - i }),
    )
    const suggestions = scoreHabits(habits, heavyLoad, SELECTED_DATE)
    expect(suggestions).toHaveLength(1)
  })

  it('skips weekly habits already completed this week', () => {
    const habits = [
      makeHabit({
        schedule_type: 'weekly',
        last_7_days: [
          { date: '2025-06-12', logged: true },
          { date: '2025-06-13', logged: false },
          { date: '2025-06-14', logged: false },
          { date: '2025-06-15', logged: false },
          { date: '2025-06-16', logged: false },
          { date: '2025-06-17', logged: false },
          { date: '2025-06-18', logged: false },
        ],
      }),
    ]
    const suggestions = scoreHabits(habits, lightLoad, SELECTED_DATE)
    expect(suggestions).toHaveLength(0)
  })

  it('includes weekly habits not yet completed this week', () => {
    const habits = [
      makeHabit({
        schedule_type: 'weekly',
        current_streak: 0,
        last_7_days: Array.from({ length: 7 }, (_, i) => ({
          date: `2025-06-${9 + i}`,
          logged: false,
        })),
      }),
    ]
    const suggestions = scoreHabits(habits, lightLoad, SELECTED_DATE)
    expect(suggestions).toHaveLength(1)
  })

  it('returns empty array for no eligible habits', () => {
    const suggestions = scoreHabits([], lightLoad, SELECTED_DATE)
    expect(suggestions).toHaveLength(0)
  })

  it('includes calendar load context in reason', () => {
    const habits = [makeHabit()]
    const lightSuggestions = scoreHabits(habits, lightLoad, SELECTED_DATE)
    expect(lightSuggestions[0].reason).toContain('lightDayEncourage')

    const heavyLoad = {
      totalEventMinutes: 400,
      eventCount: 4,
      allDayCount: 0,
      loadLevel: 'heavy' as const,
    }
    const heavySuggestions = scoreHabits(habits, heavyLoad, SELECTED_DATE)
    expect(heavySuggestions[0].reason).toContain('busyDayEncourage')
  })
})

// ---------------------------------------------------------------------------
// scoreSkill
// ---------------------------------------------------------------------------

describe('scoreSkill', () => {
  const lightLoad = computeCalendarLoad([], SELECTED_DATE)

  it('returns null for empty skills array', () => {
    expect(scoreSkill([], lightLoad, SELECTED_DATE)).toBeNull()
  })

  it('returns null when all skills score 0 (brand new, no sessions)', () => {
    const skills = [
      makeSkill({
        session_count: 0,
        streak_days: 0,
        sessions_last_7: 0,
        sessions_last_30: 0,
        last_practiced_at: null,
      }),
    ]
    expect(scoreSkill(skills, lightLoad, SELECTED_DATE)).toBeNull()
  })

  it('picks the skill with highest score', () => {
    const skills = [
      makeSkill({ id: 1, name: 'Piano', streak_days: 0, session_count: 10, sessions_last_7: 0 }),
      makeSkill({ id: 2, name: 'Drawing', streak_days: 3, session_count: 5, sessions_last_7: 2 }),
    ]
    const suggestion = scoreSkill(skills, lightLoad, SELECTED_DATE)!
    expect(suggestion).not.toBeNull()
    expect(suggestion.skillName).toBe('Piano') // broken streak + no sessions this week
  })

  it('awards +15 for zero sessions this week', () => {
    const skill = makeSkill({ sessions_last_7: 0, streak_days: 1, session_count: 5, last_practiced_at: null })
    const suggestion = scoreSkill([skill], lightLoad, SELECTED_DATE)!
    // Should include the 15 points for no sessions this week
    expect(suggestion.score).toBeGreaterThanOrEqual(15)
  })

  it('awards +40 for broken streak with existing sessions', () => {
    const skill = makeSkill({ streak_days: 0, session_count: 10, sessions_last_7: 2, last_practiced_at: '2025-06-14T10:00:00Z' })
    const suggestion = scoreSkill([skill], lightLoad, SELECTED_DATE)!
    expect(suggestion.score).toBeGreaterThanOrEqual(40)
  })

  it('includes calendar load context in reason', () => {
    const skill = makeSkill()
    const heavyLoad = {
      totalEventMinutes: 400,
      eventCount: 4,
      allDayCount: 0,
      loadLevel: 'heavy' as const,
    }
    const suggestion = scoreSkill([skill], heavyLoad, SELECTED_DATE)!
    expect(suggestion.reason).toContain('busyDayPractice')
  })

  it('calculates days since last practice', () => {
    // Last practiced June 10 00:00 local, selected date is June 15 00:00 local = 5 days
    const skill = makeSkill({ last_practiced_at: new Date(2025, 5, 10, 0, 0, 0).toISOString() })
    const suggestion = scoreSkill([skill], lightLoad, SELECTED_DATE)!
    expect(suggestion.daysSinceLastPractice).toBe(5)
  })
})

// ---------------------------------------------------------------------------
// generateDailyPlan
// ---------------------------------------------------------------------------

describe('generateDailyPlan', () => {
  it('produces a complete plan with all sections', () => {
    const events = [
      makeEvent({ id: 1, start_time: '2025-06-15T09:00:00', end_time: '2025-06-15T10:00:00' }),
    ]
    const habits = [makeHabit()]
    const skills = [makeSkill()]

    const plan = generateDailyPlan(events, habits, skills, SELECTED_DATE)

    expect(plan.date).toBe('2025-06-15')
    expect(plan.calendarLoad.loadLevel).toBe('light')
    expect(plan.habitSuggestions.length).toBeGreaterThan(0)
    expect(plan.skillSuggestion).not.toBeNull()
  })

  it('produces an empty plan when all habits complete and no skills', () => {
    const plan = generateDailyPlan(
      [],
      [makeHabit({ completed_today: true })],
      [],
      SELECTED_DATE,
    )
    expect(plan.habitSuggestions).toHaveLength(0)
    expect(plan.skillSuggestion).toBeNull()
  })

  it('is deterministic — same inputs produce same outputs', () => {
    const events = [makeEvent({ id: 1, start_time: '2025-06-15T09:00:00', end_time: '2025-06-15T11:00:00' })]
    const habits = [
      makeHabit({ id: 1, name: 'A', current_streak: 10 }),
      makeHabit({ id: 2, name: 'B', current_streak: 3 }),
    ]
    const skills = [makeSkill()]

    const plan1 = generateDailyPlan(events, habits, skills, SELECTED_DATE)
    const plan2 = generateDailyPlan(events, habits, skills, SELECTED_DATE)

    expect(plan1).toEqual(plan2)
  })
})

// ---------------------------------------------------------------------------
// resolveReasonText
// ---------------------------------------------------------------------------

describe('resolveReasonText', () => {
  const t = {
    streakAtRisk: '{streak}-day streak — keep it alive',
    streakKeepGoing: '{streak}-day streak — you\'re on a roll',
    lightDayEncourage: 'Your calendar is open — great day for this',
    busyDayEncourage: 'Busy day — even a small win counts',
    dueToday: 'Ready when you are',
    noPracticeInDays: 'It\'s been {n} days — your future self will thank you',
    keepMomentum: 'Keep the momentum going',
    completedNOf7: '{n} of 7 days this week — one more today?',
  }

  it('resolves a simple key', () => {
    expect(resolveReasonText('dueToday', t)).toBe('Ready when you are')
  })

  it('resolves a key with {streak} interpolation', () => {
    expect(resolveReasonText('streakAtRisk:12', t)).toBe('12-day streak — keep it alive')
  })

  it('resolves a key with {n} interpolation', () => {
    expect(resolveReasonText('completedNOf7:3', t)).toBe('3 of 7 days this week — one more today?')
  })

  it('joins multiple parts with " · "', () => {
    const result = resolveReasonText('streakAtRisk:5|lightDayEncourage', t)
    expect(result).toBe('5-day streak — keep it alive · Your calendar is open — great day for this')
  })

  it('falls back to raw key if not found in translations', () => {
    expect(resolveReasonText('unknownKey', t)).toBe('unknownKey')
  })
})
