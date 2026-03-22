'use client'

import type { HabitHeatmapEntry } from '@/lib/api/habits'

interface HabitHeatmapProps {
  entries: HabitHeatmapEntry[]
  year: number
}

/**
 * GitHub-style yearly heatmap for habit completion.
 * 52 columns (weeks) x 7 rows (days), sage-green fills.
 */
export function HabitHeatmap({ entries, year }: HabitHeatmapProps) {
  // Build a Set for O(1) lookup
  const loggedDates = new Set(entries.filter((e) => e.logged).map((e) => e.date))

  // Build grid: find the first day of the year, pad to start on Sunday
  const jan1 = new Date(year, 0, 1)
  const startOffset = jan1.getDay() // 0=Sun, 6=Sat
  const startDate = new Date(jan1)
  startDate.setDate(startDate.getDate() - startOffset)

  // Generate 53 weeks x 7 days
  const weeks: Array<Array<{ date: string; logged: boolean; inYear: boolean }>> = []
  const cursor = new Date(startDate)
  for (let w = 0; w < 53; w++) {
    const week: Array<{ date: string; logged: boolean; inYear: boolean }> = []
    for (let d = 0; d < 7; d++) {
      const iso = cursor.toISOString().slice(0, 10)
      const inYear = cursor.getFullYear() === year
      week.push({ date: iso, logged: loggedDates.has(iso), inYear })
      cursor.setDate(cursor.getDate() + 1)
    }
    weeks.push(week)
  }

  const dayLabels = ['', 'M', '', 'W', '', 'F', '']

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div style={{ display: 'flex', gap: '2px' }}>
        {/* Day labels column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', marginRight: '4px' }}>
          {dayLabels.map((label, i) => (
            <div
              key={i}
              style={{
                width: '12px',
                height: '10px',
                fontSize: '0.5rem',
                fontFamily: 'var(--font-manrope), sans-serif',
                color: '#767d72',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
              }}
            >
              {label}
            </div>
          ))}
        </div>
        {/* Week columns */}
        {weeks.map((week, wi) => (
          <div key={wi} style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            {week.map((day) => (
              <div
                key={day.date}
                title={day.inYear ? `${day.date}${day.logged ? ' \u2713' : ''}` : ''}
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '2px',
                  background: !day.inYear
                    ? 'transparent'
                    : day.logged
                    ? '#4b6646'
                    : '#eef2e8',
                  opacity: !day.inYear ? 0 : day.logged ? 1 : 0.7,
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
