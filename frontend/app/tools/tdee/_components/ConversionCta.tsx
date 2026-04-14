'use client'

import type { TdeeResult } from '@/lib/tdee-calculator'

interface ConversionCtaProps {
  hasResult: boolean
  result: TdeeResult | null
}

export default function ConversionCta({ hasResult, result }: ConversionCtaProps) {
  const ctaUrl = result
    ? `https://taeyangcv.vercel.app/?ref=tdee&tdee=${Math.round(result.tdee)}&daily=${Math.round(result.daily_calories)}&goal=${result.goal_type ?? 'maintain'}`
    : 'https://taeyangcv.vercel.app/?ref=tdee'

  return (
    <div
      style={{
        background: 'linear-gradient(135deg, #f1f5eb, #e8f0e3)',
        borderRadius: '0 16px 16px 16px',
        padding: '40px 32px',
        marginTop: '40px',
        textAlign: 'center',
      }}
    >
      <p
        style={{
          fontFamily: 'var(--font-manrope), Manrope, sans-serif',
          fontWeight: 700,
          fontSize: '0.6875rem',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: '#4b6646',
          marginBottom: '12px',
        }}
      >
        LifeOS
      </p>

      <h2
        style={{
          fontFamily: 'var(--font-serif), Newsreader, serif',
          fontWeight: 300,
          fontSize: '1.75rem',
          color: '#4b6646',
          letterSpacing: '-0.03em',
          marginBottom: '12px',
          lineHeight: 1.2,
        }}
      >
        Want to track this over time?
      </h2>

      <p
        style={{
          fontFamily: 'var(--font-manrope), Manrope, sans-serif',
          fontWeight: 400,
          fontSize: '0.9375rem',
          color: '#5a6157',
          lineHeight: 1.65,
          marginBottom: '28px',
          maxWidth: '380px',
          margin: '0 auto 28px',
        }}
      >
        LifeOS helps you observe your body composition trends with clinical precision.
      </p>

      <a
        href={ctaUrl}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: 'inline-block',
          background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
          color: '#ffffff',
          borderRadius: '100px',
          padding: '14px 40px',
          minHeight: '48px',
          fontFamily: 'var(--font-manrope), Manrope, sans-serif',
          fontWeight: 600,
          fontSize: '0.9375rem',
          boxShadow: '0 4px 20px rgba(46,52,43,0.18)',
          textDecoration: 'none',
          transition: 'transform 0.15s, box-shadow 0.15s',
        }}
        onMouseEnter={e => {
          const el = e.currentTarget as HTMLAnchorElement
          el.style.transform = 'translateY(-2px) scale(1.025)'
          el.style.boxShadow = '0 6px 24px rgba(46,52,43,0.24)'
        }}
        onMouseLeave={e => {
          const el = e.currentTarget as HTMLAnchorElement
          el.style.transform = 'none'
          el.style.boxShadow = '0 4px 20px rgba(46,52,43,0.18)'
        }}
      >
        Join LifeOS
      </a>
    </div>
  )
}
