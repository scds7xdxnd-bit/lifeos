'use client'

import { Heart } from 'lucide-react'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

interface HealthEmptyStateProps {
  onLogBiometric: () => void
  onLogWorkout: () => void
  onLogMeal: () => void
}

export default function HealthEmptyState({ onLogBiometric, onLogWorkout, onLogMeal }: HealthEmptyStateProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health

  return (
    <div
      className="p-12 text-center"
      style={{
        background: '#ffffff',
        borderRadius: '0 16px 16px 16px',
        boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
      }}
    >
      <div
        className="w-16 h-16 rounded-full mx-auto mb-5 flex items-center justify-center"
        style={{ background: '#fce8e4' }}
      >
        <Heart size={28} style={{ color: '#8b4a3a' }} aria-hidden="true" />
      </div>

      <h3
        className="mb-3"
        style={{
          fontFamily: 'var(--font-serif), Georgia, serif',
          fontSize: '1.25rem',
          fontWeight: 400,
          color: '#4b6646',
          letterSpacing: '-0.03em',
        }}
      >
        {t.emptyTitle}
      </h3>

      <p
        className="mx-auto mb-8"
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.875rem',
          color: '#767d72',
          lineHeight: 1.65,
          maxWidth: '360px',
        }}
      >
        {t.emptyBody}
      </p>

      <div className="flex flex-wrap justify-center gap-3">
        {[
          { label: t.logBiometric, handler: onLogBiometric },
          { label: t.logWorkout, handler: onLogWorkout },
          { label: t.logMeal, handler: onLogMeal },
        ].map(({ label, handler }) => (
          <button
            key={label}
            onClick={handler}
            aria-label={label}
            style={{
              background: '#f1f5eb',
              color: '#2e342b',
              borderRadius: '100px',
              padding: '10px 20px',
              minHeight: '44px',
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              fontWeight: 500,
              border: 'none',
              cursor: 'pointer',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease',
            }}
            onMouseEnter={e => {
              ;(e.currentTarget as HTMLElement).style.transform = 'translateY(-1px)'
              ;(e.currentTarget as HTMLElement).style.boxShadow = '0 4px 12px rgba(46,52,43,0.1)'
            }}
            onMouseLeave={e => {
              ;(e.currentTarget as HTMLElement).style.transform = ''
              ;(e.currentTarget as HTMLElement).style.boxShadow = ''
            }}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  )
}
