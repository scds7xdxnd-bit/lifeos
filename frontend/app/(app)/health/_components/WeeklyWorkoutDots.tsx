'use client'

interface WeeklyWorkoutDotsProps {
  days: Array<{ date: string; hasWorkout: boolean }>
}

const DAY_ABBR = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

export default function WeeklyWorkoutDots({ days }: WeeklyWorkoutDotsProps) {
  const today = new Date().toISOString().split('T')[0]

  return (
    <div className="flex gap-3" role="img" aria-label="7-day workout pattern">
      <style>{`
        @keyframes dot-pulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(75, 102, 70, 0.4); }
          50% { box-shadow: 0 0 0 4px rgba(75, 102, 70, 0); }
        }
      `}</style>
      {days.map(({ date, hasWorkout }, i) => {
        const isToday = date === today
        return (
          <div key={i} className="flex flex-col items-center gap-1">
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: hasWorkout ? '#4b6646' : '#dee5d7',
                animation: isToday && !hasWorkout ? 'dot-pulse 2s infinite' : undefined,
              }}
            />
            <span
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.5rem',
                fontWeight: 500,
                color: '#767d72',
              }}
            >
              {DAY_ABBR[i]}
            </span>
          </div>
        )
      })}
    </div>
  )
}
