'use client'

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface SummaryCardProps {
  label: string
  amount: number
  currency?: string
  trend?: 'up' | 'down' | 'neutral'
  trendLabel?: string
}

function formatAmount(amount: number, currency?: string): string {
  const symbol = currency === 'KRW' ? '₩' : currency === 'EUR' ? '€' : '$'
  const decimals = currency === 'KRW' || currency === 'JPY' ? 0 : 2
  return `${symbol}${amount.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`
}

export function FinanceSummaryCard({ label, amount, currency, trend, trendLabel }: SummaryCardProps) {
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus
  const trendColor = trend === 'up' ? '#3a5c35' : trend === 'down' ? '#e8735c' : '#767d72'

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '0 16px 16px 16px',
        boxShadow: '0 4px 16px rgba(46, 52, 43, 0.06)',
        padding: '1.25rem 1.5rem',
      }}
    >
      <p
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.6875rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: '#767d72',
          marginBottom: '0.5rem',
        }}
      >
        {label}
      </p>
      <p
        style={{
          fontFamily: 'var(--font-serif), Georgia, serif',
          fontSize: '1.625rem',
          fontWeight: 300,
          color: '#2e342b',
          letterSpacing: '-0.03em',
          lineHeight: 1.2,
        }}
      >
        {formatAmount(amount, currency)}
      </p>
      {trend && trendLabel && (
        <div className="flex items-center gap-1 mt-2">
          <TrendIcon size={13} style={{ color: trendColor }} />
          <span
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.75rem',
              color: trendColor,
            }}
          >
            {trendLabel}
          </span>
        </div>
      )}
    </div>
  )
}
