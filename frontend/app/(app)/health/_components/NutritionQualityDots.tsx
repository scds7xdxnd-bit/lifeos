'use client'

interface NutritionQualityDotsProps {
  days: Array<{ date: string; avgQuality: number | null }>
}

const DAY_ABBR = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

export default function NutritionQualityDots({ days }: NutritionQualityDotsProps) {
  return (
    <div className="flex gap-3" role="img" aria-label="7-day nutrition quality">
      {days.map(({ avgQuality }, i) => {
        const opacity = avgQuality != null ? 0.2 + (avgQuality / 5) * 0.8 : 0
        return (
          <div key={i} className="flex flex-col items-center gap-1">
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: '50%',
                background: avgQuality != null ? `rgba(75, 102, 70, ${opacity})` : '#dee5d7',
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
