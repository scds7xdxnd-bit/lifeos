'use client'

import type { HabitHistoryEntry } from '@/lib/api/habits'

interface HabitStreakChartProps {
  entries: HabitHistoryEntry[]
}

/**
 * 30-day bar chart showing daily completion.
 * Filled bar = logged, empty bar = missed. Sage palette.
 */
export function HabitStreakChart({ entries }: HabitStreakChartProps) {
  if (entries.length === 0) return null

  const barHeight = 48

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {/* Bar chart */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: '2px',
          height: `${barHeight + 16}px`,
        }}
      >
        {entries.map((entry) => {
          const dayNum = new Date(entry.date).getDate()
          return (
            <div
              key={entry.date}
              title={`${entry.date}${entry.logged ? ' \u2713' : ''}`}
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <div
                style={{
                  width: '100%',
                  maxWidth: '12px',
                  height: entry.logged ? `${barHeight}px` : '6px',
                  borderRadius: '3px 3px 1px 1px',
                  background: entry.logged
                    ? '#3a5272'
                    : '#e4e8de',
                  transition: 'height 300ms ease',
                }}
              />
              {/* Show day number for 1st, 10th, 20th, 30th only to avoid clutter */}
              {(dayNum === 1 || dayNum === 10 || dayNum === 20 || dayNum === 30) && (
                <span
                  style={{
                    fontSize: '0.5rem',
                    fontFamily: 'var(--font-manrope), sans-serif',
                    color: '#767d72',
                    lineHeight: 1,
                  }}
                >
                  {dayNum}
                </span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
