'use client'

import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

interface WorkoutSummaryCardProps {
  sessionsThisWeek: number
  totalDurationMinutes: number
  workoutTypes: Record<string, number>
}

export default function WorkoutSummaryCard({
  sessionsThisWeek,
  totalDurationMinutes,
  workoutTypes,
}: WorkoutSummaryCardProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health

  const typeEntries = Object.entries(workoutTypes)

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '0 16px 16px 16px',
        boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
        padding: '32px',
      }}
    >
      <p
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.6875rem',
          fontWeight: 700,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: '#8b4a3a',
          marginBottom: '12px',
        }}
      >
        {t.training}
      </p>

      <p
        style={{
          fontFamily: 'var(--font-serif), Georgia, serif',
          fontSize: '1.5rem',
          fontWeight: 400,
          color: '#2e342b',
          marginBottom: '4px',
        }}
      >
        {sessionsThisWeek} {t.sessions}
      </p>

      {totalDurationMinutes > 0 && (
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.8125rem',
            color: '#5a6157',
            marginBottom: '12px',
          }}
        >
          {totalDurationMinutes} {t.minUnit}
        </p>
      )}

      {typeEntries.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {typeEntries.map(([type, count]) => (
            <span
              key={type}
              style={{
                background: '#f1f5eb',
                color: '#5a6157',
                borderRadius: '100px',
                padding: '2px 10px',
                fontSize: '0.6875rem',
                fontFamily: 'var(--font-manrope), sans-serif',
              }}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)} ({count})
            </span>
          ))}
        </div>
      )}

      {sessionsThisWeek === 0 && (
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.875rem',
            color: '#767d72',
            marginTop: '8px',
          }}
        >
          {t.noData}
        </p>
      )}
    </div>
  )
}
