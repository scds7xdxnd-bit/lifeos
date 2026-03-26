/**
 * Phase 13a — Deterministic Daily Planning Engine
 *
 * Pure functions that score habits and skills against the user's calendar
 * to produce read-only daily suggestions. No React, no side effects.
 */

import type { CalendarEvent } from '@/lib/api/calendar'
import type { Habit } from '@/lib/api/habits'
import type { Skill } from '@/lib/api/skills'
import { resolveEventInterval, startOfDayLocal, addDaysLocal, toDateKey } from '../calendar-utils'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type CalendarLoadLevel = 'light' | 'moderate' | 'heavy'

export interface CalendarLoad {
  totalEventMinutes: number
  eventCount: number
  allDayCount: number
  loadLevel: CalendarLoadLevel
}

export interface HabitSuggestion {
  habitId: number
  habitName: string
  score: number
  reason: string
  currentStreak: number
  scheduledTime: string | null
}

export interface SkillSuggestion {
  skillId: number
  skillName: string
  score: number
  reason: string
  daysSinceLastPractice: number | null
  totalMinutes: number
}

export interface DailyPlan {
  date: string
  calendarLoad: CalendarLoad
  habitSuggestions: HabitSuggestion[]
  skillSuggestion: SkillSuggestion | null
}

// ---------------------------------------------------------------------------
// Calendar load
// ---------------------------------------------------------------------------

export function computeCalendarLoad(events: CalendarEvent[], date: Date): CalendarLoad {
  const dayStart = startOfDayLocal(date)
  const dayEnd = addDaysLocal(dayStart, 1)
  const dayStartMs = dayStart.getTime()
  const dayEndMs = dayEnd.getTime()

  let totalEventMinutes = 0
  let eventCount = 0
  let allDayCount = 0

  for (const event of events) {
    const interval = resolveEventInterval(event)
    if (!interval) continue

    if (event.all_day) {
      const evStartDay = startOfDayLocal(interval.start)
      const evEndDay = startOfDayLocal(interval.end)
      if (evStartDay.getTime() <= dayStartMs && evEndDay.getTime() > dayStartMs) {
        allDayCount += 1
      }
      continue
    }

    if (interval.end.getTime() <= dayStartMs || interval.start.getTime() >= dayEndMs) continue

    const clippedStartMs = Math.max(interval.start.getTime(), dayStartMs)
    const clippedEndMs = Math.min(interval.end.getTime(), dayEndMs)
    const minutes = Math.round((clippedEndMs - clippedStartMs) / 60000)

    totalEventMinutes += minutes
    eventCount += 1
  }

  let loadLevel: CalendarLoadLevel = 'light'
  if (totalEventMinutes >= 360) loadLevel = 'heavy'
  else if (totalEventMinutes >= 180) loadLevel = 'moderate'

  return { totalEventMinutes, eventCount, allDayCount, loadLevel }
}

// ---------------------------------------------------------------------------
// Habit scoring
// ---------------------------------------------------------------------------

function recentCompletionCount(habit: Habit): number {
  return habit.last_7_days.filter((d) => d.logged).length
}

export function scoreHabits(
  habits: Habit[],
  calendarLoad: CalendarLoad,
  date: Date,
): HabitSuggestion[] {
  const dateKey = toDateKey(date)

  const candidates = habits.filter((h) => {
    if (!h.is_active) return false
    if (h.completed_today) return false

    // For weekly habits, skip if already completed this week
    if (h.schedule_type === 'weekly') {
      const completedThisWeek = h.last_7_days.some((d) => d.logged)
      if (completedThisWeek) return false
    }

    return true
  })

  const scored: HabitSuggestion[] = candidates.map((habit) => {
    let score = 0

    // Streak at risk
    if (habit.current_streak > 0) {
      score += 40
      if (habit.current_streak >= 30) score += 10
      if (habit.current_streak >= 7) score += 20
    }

    // Scheduled time awareness
    if (habit.scheduled_time) {
      const now = new Date()
      if (toDateKey(now) === dateKey) {
        const [h, m] = habit.scheduled_time.split(':').map(Number)
        if (!Number.isNaN(h) && !Number.isNaN(m)) {
          const scheduledMs = date.getTime()
          const scheduledDate = new Date(date)
          scheduledDate.setHours(h, m, 0, 0)
          const diffMinutes = (scheduledDate.getTime() - now.getTime()) / 60000

          if (diffMinutes < 0) score += 10 // overdue
          else if (diffMinutes <= 180) score += 15 // within 3 hours
        }
      }
    }

    // Low recent completion
    const recentCount = recentCompletionCount(habit)
    if (recentCount < 4) score += 5

    // Build reason
    const reason = buildHabitReason(habit, recentCount, calendarLoad)

    return {
      habitId: habit.id,
      habitName: habit.name,
      score,
      reason,
      currentStreak: habit.current_streak,
      scheduledTime: habit.scheduled_time,
    }
  })

  scored.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score
    return b.currentStreak - a.currentStreak
  })

  // Load shedding
  const maxSuggestions = calendarLoad.loadLevel === 'heavy' ? 1 : calendarLoad.loadLevel === 'moderate' ? 2 : 3
  return scored.slice(0, maxSuggestions)
}

function buildHabitReason(habit: Habit, recentCount: number, load: CalendarLoad): string {
  let reason: string

  if (habit.current_streak >= 30) {
    reason = `streakKeepGoing:${habit.current_streak}`
  } else if (habit.current_streak >= 7) {
    reason = `streakKeepGoing:${habit.current_streak}`
  } else if (habit.current_streak > 0) {
    reason = `streakAtRisk:${habit.current_streak}`
  } else if (habit.scheduled_time) {
    reason = `scheduledPending:${habit.scheduled_time}`
  } else if (recentCount < 4) {
    reason = `completedNOf7:${recentCount}`
  } else {
    reason = 'dueToday'
  }

  // Calendar-aware suffix
  if (load.loadLevel === 'light') {
    reason += '|lightDayEncourage'
  } else if (load.loadLevel === 'heavy') {
    reason += '|busyDayEncourage'
  }

  return reason
}

// ---------------------------------------------------------------------------
// Skill scoring
// ---------------------------------------------------------------------------

export function scoreSkill(
  skills: Skill[],
  calendarLoad: CalendarLoad,
  date: Date,
): SkillSuggestion | null {
  if (skills.length === 0) return null

  const now = date.getTime()

  // Filter out brand-new skills with no practice history
  const practiced = skills.filter((s) => s.session_count > 0)
  if (practiced.length === 0) return null

  const scored = practiced.map((skill) => {
    let score = 0

    // Days since last practice
    let daysSince: number | null = null
    if (skill.last_practiced_at) {
      const lastMs = new Date(skill.last_practiced_at).getTime()
      if (!Number.isNaN(lastMs)) {
        daysSince = Math.floor((now - lastMs) / (24 * 60 * 60000))
        score += Math.min(30, daysSince * 3)
      }
    }

    // Was practicing, stopped (streak broken)
    if (skill.streak_days === 0 && skill.session_count > 0) {
      score += 40
    }

    // Zero sessions this week
    if (skill.sessions_last_7 === 0) {
      score += 15
    }

    // Calendar has free time
    if (calendarLoad.loadLevel === 'light') {
      score += 10
    }

    // Sessions exist but completely stalled (none in 30 days)
    if (skill.session_count > 0 && skill.sessions_last_30 === 0) {
      score += 5
    }

    return { skill, score, daysSince }
  })

  scored.sort((a, b) => b.score - a.score)

  const top = scored[0]
  if (top.score === 0) return null

  const reason = buildSkillReason(top.skill, top.daysSince, calendarLoad)

  return {
    skillId: top.skill.id,
    skillName: top.skill.name,
    score: top.score,
    reason,
    daysSinceLastPractice: top.daysSince,
    totalMinutes: top.skill.total_minutes,
  }
}

function buildSkillReason(skill: Skill, daysSince: number | null, load: CalendarLoad): string {
  let reason: string

  if (daysSince !== null && daysSince >= 7) {
    reason = `noPracticeInDays:${daysSince}`
  } else if (daysSince !== null && daysSince >= 3) {
    reason = `daysSincePractice:${daysSince}`
  } else if (skill.streak_days === 0 && skill.session_count > 0) {
    reason = 'streakRecover'
  } else if (skill.sessions_last_7 === 0) {
    reason = 'noSessionsThisWeek'
  } else {
    reason = 'keepMomentum'
  }

  if (load.loadLevel === 'light') {
    reason += '|lightDayPractice'
  } else if (load.loadLevel === 'heavy') {
    reason += '|busyDayPractice'
  }

  return reason
}

// ---------------------------------------------------------------------------
// Public: generate the full daily plan
// ---------------------------------------------------------------------------

export function generateDailyPlan(
  events: CalendarEvent[],
  habits: Habit[],
  skills: Skill[],
  date: Date,
): DailyPlan {
  const calendarLoad = computeCalendarLoad(events, date)
  const habitSuggestions = scoreHabits(habits, calendarLoad, date)
  const skillSuggestion = scoreSkill(skills, calendarLoad, date)

  return {
    date: toDateKey(date),
    calendarLoad,
    habitSuggestions,
    skillSuggestion,
  }
}

// ---------------------------------------------------------------------------
// Reason text resolver
// ---------------------------------------------------------------------------

export function resolveReasonText(
  encoded: string,
  t: Record<string, string>,
): string {
  const parts = encoded.split('|')
  const segments: string[] = []

  for (const part of parts) {
    const colonIdx = part.indexOf(':')
    if (colonIdx === -1) {
      segments.push(t[part] ?? part)
    } else {
      const key = part.slice(0, colonIdx)
      const value = part.slice(colonIdx + 1)
      const template = t[key] ?? part
      segments.push(
        template
          .replace('{streak}', value)
          .replace('{n}', value)
          .replace('{time}', value),
      )
    }
  }

  return segments.join(' · ')
}
