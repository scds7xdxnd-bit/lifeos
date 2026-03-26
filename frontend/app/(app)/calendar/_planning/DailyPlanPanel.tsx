'use client'

import { useDailyPlan } from './useDailyPlan'
import { resolveReasonText } from './planning-engine'
import type { HabitSuggestion, SkillSuggestion, CalendarLoad } from './planning-engine'
import type { CalendarPageTranslations } from '@/lib/translations/app'

interface DailyPlanPanelProps {
  selectedDate: Date
  t: CalendarPageTranslations
}

// ---------------------------------------------------------------------------
// Micro-components
// ---------------------------------------------------------------------------

function CalendarLoadChip({ load, t }: { load: CalendarLoad; t: CalendarPageTranslations }) {
  const labels: Record<string, string> = {
    light: t.calendarLoadLight,
    moderate: t.calendarLoadModerate,
    heavy: t.calendarLoadHeavy,
  }

  const colors: Record<string, { bg: string; text: string }> = {
    light: { bg: '#d6e8ce', text: '#465642' },
    moderate: { bg: '#dee5d7', text: '#5a6157' },
    heavy: { bg: '#fce8e4', text: '#8b4a3a' },
  }

  const style = colors[load.loadLevel] ?? colors.light

  return (
    <span
      style={{
        display: 'inline-block',
        fontFamily: 'var(--font-manrope), sans-serif',
        fontSize: '0.6875rem',
        fontWeight: 600,
        letterSpacing: '0.03em',
        color: style.text,
        background: style.bg,
        borderRadius: '9999px',
        padding: '3px 10px',
      }}
    >
      {labels[load.loadLevel]}
    </span>
  )
}

function HabitSuggestionCard({
  suggestion,
  t,
}: {
  suggestion: HabitSuggestion
  t: CalendarPageTranslations
}) {
  const reasonText = resolveReasonText(suggestion.reason, t as unknown as Record<string, string>)

  return (
    <article
      style={{
        background: '#ffffff',
        borderRadius: '0 12px 12px 12px',
        padding: '12px 14px',
        boxShadow: '0 2px 12px rgba(46, 52, 43, 0.05)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '10px',
        transition: 'transform 220ms ease, box-shadow 220ms ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)'
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(46, 52, 43, 0.10)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = '0 2px 12px rgba(46, 52, 43, 0.05)'
      }}
    >
      {/* Left accent bar */}
      <div
        style={{
          width: 3,
          minHeight: 32,
          borderRadius: 2,
          background: '#3a5272',
          flexShrink: 0,
          alignSelf: 'stretch',
        }}
      />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontWeight: 700,
            fontSize: '0.8125rem',
            color: '#2e342b',
            lineHeight: 1.3,
          }}
        >
          {suggestion.habitName}
          {suggestion.currentStreak > 0 && (
            <span
              style={{
                marginLeft: 6,
                fontSize: '0.6875rem',
                fontWeight: 600,
                color: '#4b6646',
              }}
            >
              {suggestion.currentStreak}d
            </span>
          )}
        </div>
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontWeight: 400,
            fontSize: '0.75rem',
            color: '#5a6157',
            marginTop: 2,
            lineHeight: 1.4,
          }}
        >
          {reasonText}
        </p>
      </div>
    </article>
  )
}

function SkillSuggestionCard({
  suggestion,
  t,
}: {
  suggestion: SkillSuggestion
  t: CalendarPageTranslations
}) {
  const reasonText = resolveReasonText(suggestion.reason, t as unknown as Record<string, string>)
  const hours = Math.floor(suggestion.totalMinutes / 60)
  const mins = suggestion.totalMinutes % 60

  return (
    <article
      style={{
        background: '#ffffff',
        borderRadius: '0 12px 12px 12px',
        padding: '12px 14px',
        boxShadow: '0 2px 12px rgba(46, 52, 43, 0.05)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '10px',
        transition: 'transform 220ms ease, box-shadow 220ms ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)'
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(46, 52, 43, 0.10)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)'
        e.currentTarget.style.boxShadow = '0 2px 12px rgba(46, 52, 43, 0.05)'
      }}
    >
      {/* Left accent bar — parchment domain */}
      <div
        style={{
          width: 3,
          minHeight: 32,
          borderRadius: 2,
          background: '#6b5a35',
          flexShrink: 0,
          alignSelf: 'stretch',
        }}
      />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontWeight: 700,
            fontSize: '0.8125rem',
            color: '#2e342b',
            lineHeight: 1.3,
          }}
        >
          {suggestion.skillName}
          {suggestion.totalMinutes > 0 && (
            <span
              style={{
                marginLeft: 6,
                fontSize: '0.6875rem',
                fontWeight: 600,
                color: '#5a6157',
              }}
            >
              {hours > 0 ? `${hours}h${mins > 0 ? ` ${mins}m` : ''}` : `${mins}m`}
            </span>
          )}
        </div>
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontWeight: 400,
            fontSize: '0.75rem',
            color: '#5a6157',
            marginTop: 2,
            lineHeight: 1.4,
          }}
        >
          {reasonText}
        </p>
      </div>
    </article>
  )
}

// ---------------------------------------------------------------------------
// Main panel
// ---------------------------------------------------------------------------

export default function DailyPlanPanel({ selectedDate, t }: DailyPlanPanelProps) {
  const { plan, isLoading } = useDailyPlan(selectedDate)

  if (isLoading || !plan) return null

  const hasHabits = plan.habitSuggestions.length > 0
  const hasSkill = plan.skillSuggestion !== null
  const isEmpty = !hasHabits && !hasSkill

  return (
    <section
      style={{
        background: '#f1f5eb',
        borderRadius: '0 12px 12px 12px',
        padding: '20px 20px 16px',
        marginTop: 16,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          marginBottom: isEmpty ? 0 : 14,
        }}
      >
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#4b6646',
            margin: 0,
          }}
        >
          {t.dailyPlan}
        </p>
        <CalendarLoadChip load={plan.calendarLoad} t={t} />
      </div>

      {/* Empty state */}
      {isEmpty && (
        <p
          style={{
            fontFamily: 'var(--font-newsreader, "Newsreader"), serif',
            fontStyle: 'italic',
            fontSize: '0.9375rem',
            color: '#4b6646',
            marginTop: 10,
            lineHeight: 1.5,
          }}
        >
          {t.nothingPressing}
        </p>
      )}

      {/* Habits section */}
      {hasHabits && (
        <div style={{ marginBottom: hasSkill ? 14 : 0 }}>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.625rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: '#767d72',
              marginBottom: 6,
            }}
          >
            {t.habitsDue}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {plan.habitSuggestions.map((s, idx) => (
              <div
                key={s.habitId}
                style={{
                  animation: `fadeSlideIn 300ms ease-out ${idx * 50}ms both`,
                }}
              >
                <HabitSuggestionCard suggestion={s} t={t} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Skill section */}
      {hasSkill && plan.skillSuggestion && (
        <div>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.625rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: '#767d72',
              marginBottom: 6,
            }}
          >
            {t.skillPractice}
          </p>
          <SkillSuggestionCard suggestion={plan.skillSuggestion} t={t} />
        </div>
      )}

      {/* Stagger animation keyframes */}
      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(6px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </section>
  )
}
