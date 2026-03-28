'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

interface BiometricTrendCardProps {
  latestWeight: number | null
  weightDelta: number | null
  trendDirection: 'up' | 'down' | 'stable'
  energyLevel: number | null
  stressLevel: number | null
}

function DotRating({ value, label }: { value: number | null; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.75rem',
          color: '#767d72',
        }}
      >
        {label}
      </span>
      <div className="flex gap-1" role="img" aria-label={`${label}: ${value ?? 0} of 5`}>
        {Array.from({ length: 5 }, (_, i) => (
          <div
            key={i}
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: value != null && i < value ? '#4b6646' : '#dee5d7',
            }}
          />
        ))}
      </div>
    </div>
  )
}

export default function BiometricTrendCard({
  latestWeight,
  weightDelta,
  trendDirection,
  energyLevel,
  stressLevel,
}: BiometricTrendCardProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health

  const TrendIcon = trendDirection === 'up' ? TrendingUp : trendDirection === 'down' ? TrendingDown : Minus
  const deltaColor = '#767d72'

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
        {t.biometrics}
      </p>

      {latestWeight != null ? (
        <>
          <div className="flex items-baseline gap-3 mb-3">
            <span
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: '1.5rem',
                fontWeight: 400,
                color: '#2e342b',
              }}
            >
              {latestWeight} kg
            </span>
            {weightDelta != null && (
              <span
                className="flex items-center gap-1"
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  color: deltaColor,
                }}
              >
                <TrendIcon size={14} />
                {weightDelta > 0 ? '+' : ''}{weightDelta.toFixed(1)} kg
              </span>
            )}
          </div>
        </>
      ) : (
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.875rem',
            color: '#767d72',
            marginBottom: '12px',
          }}
        >
          {t.noData}
        </p>
      )}

      <div className="flex flex-col gap-2 mt-3">
        <DotRating value={energyLevel} label={t.energy} />
        <DotRating value={stressLevel} label={t.stress} />
      </div>
    </div>
  )
}
