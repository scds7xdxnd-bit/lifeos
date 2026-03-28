'use client'

import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

interface NutritionSummaryCardProps {
  mealsToday: number
  averageQuality: number | null
  weeklyMealDays: boolean[]
}

export default function NutritionSummaryCard({
  mealsToday,
  averageQuality,
  weeklyMealDays,
}: NutritionSummaryCardProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health

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
        {t.nutrition}
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
        {mealsToday} {t.mealsUnit}
      </p>

      {averageQuality != null && (
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.875rem',
            color: '#5a6157',
            marginBottom: '12px',
          }}
        >
          {t.qualityLabel}: {averageQuality.toFixed(1)} / 5
        </p>
      )}

      <div className="flex gap-1.5 mt-3" role="img" aria-label="7-day meal log">
        {weeklyMealDays.map((logged, i) => (
          <div
            key={i}
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: logged ? '#4b6646' : '#dee5d7',
            }}
          />
        ))}
      </div>
    </div>
  )
}
