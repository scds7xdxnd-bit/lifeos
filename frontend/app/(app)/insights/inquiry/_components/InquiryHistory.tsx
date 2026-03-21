'use client'

import type { Inquiry } from '@/lib/api/inquiries'
import { domainLabel, pairLabel, fmtDate } from './helpers'

interface InquiryHistoryProps {
  items: Inquiry[]
  isLoading: boolean
  selectedId: number | null
  onView: (inquiry: Inquiry) => void
  onRefine: (inquiry: Inquiry) => void
}

export function InquiryHistory({
  items,
  isLoading,
  selectedId,
  onView,
  onRefine,
}: InquiryHistoryProps) {
  if (isLoading) {
    return (
      <div
        className="p-5 sm:p-7"
        style={{
          background: '#ffffff',
          borderRadius: '0 16px 16px 16px',
          boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
        }}
      >
        <h3
          className="mb-4"
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '1.125rem',
            fontWeight: 400,
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          Recent Inquiries
        </h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-16 rounded-xl animate-pulse"
              style={{ background: '#f1f5eb' }}
            />
          ))}
        </div>
      </div>
    )
  }

  if (!items.length) {
    return (
      <div
        className="p-5 sm:p-7"
        style={{
          background: '#ffffff',
          borderRadius: '0 16px 16px 16px',
          boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
        }}
      >
        <h3
          className="mb-2"
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '1.125rem',
            fontWeight: 400,
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          Recent Inquiries
        </h3>
        <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
          No inquiries yet. Generate your first brief above.
        </p>
      </div>
    )
  }

  return (
    <div
      className="p-5 sm:p-7 space-y-5"
      style={{
        background: '#ffffff',
        borderRadius: '0 16px 16px 16px',
        boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
      }}
    >
      <h3
        style={{
          fontFamily: 'var(--font-serif), Georgia, serif',
          fontSize: '1.125rem',
          fontWeight: 400,
          color: '#4b6646',
          letterSpacing: '-0.03em',
        }}
      >
        Recent Inquiries
      </h3>
      <ul className="space-y-3">
        {items.map((inq) => {
          const isSelected = inq.id === selectedId
          const domainDisplay =
            (inq.domains?.length ?? 0) > 1
              ? pairLabel(inq.domains)
              : domainLabel(inq.domain)

          return (
            <li
              key={inq.id}
              className="px-4 py-3.5 transition-all duration-220"
              style={{
                borderRadius: '0 12px 12px 12px',
                background: isSelected ? '#f1f5eb' : '#f8faf2',
                boxShadow: isSelected ? '0 4px 16px rgba(46, 52, 43, 0.06)' : 'none',
              }}
            >
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <p
                    className="truncate"
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.875rem',
                      fontWeight: 600,
                      color: '#2e342b',
                    }}
                  >
                    {inq.question}
                  </p>
                  <div
                    className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5"
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.6875rem',
                      color: '#767d72',
                    }}
                  >
                    <span>{domainDisplay}</span>
                    <span style={{ color: '#adb4a8' }}>·</span>
                    <span>{inq.timeframe?.start} → {inq.timeframe?.end}</span>
                    {inq.last_version_number > 1 && (
                      <>
                        <span style={{ color: '#adb4a8' }}>·</span>
                        <span>v{inq.last_version_number}</span>
                      </>
                    )}
                    <span style={{ color: '#adb4a8' }}>·</span>
                    <span>{fmtDate(inq.created_at)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => onView(inq)}
                    className="transition-all duration-200"
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      textTransform: 'uppercase' as const,
                      letterSpacing: '0.05em',
                      padding: '6px 14px',
                      borderRadius: '100px',
                      border: 'none',
                      cursor: 'pointer',
                      color: isSelected ? '#ffffff' : '#5a6157',
                      background: isSelected
                        ? 'linear-gradient(135deg, #4b6646, #3f5a3a)'
                        : '#e5eade',
                      boxShadow: isSelected ? '0 4px 12px rgba(46, 52, 43, 0.15)' : 'none',
                    }}
                  >
                    View
                  </button>
                  <button
                    type="button"
                    onClick={() => onRefine(inq)}
                    className="transition-all duration-200"
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      textTransform: 'uppercase' as const,
                      letterSpacing: '0.05em',
                      padding: '6px 14px',
                      borderRadius: '100px',
                      border: 'none',
                      cursor: 'pointer',
                      color: '#767d72',
                      background: '#ebefe4',
                    }}
                  >
                    Refine
                  </button>
                </div>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
