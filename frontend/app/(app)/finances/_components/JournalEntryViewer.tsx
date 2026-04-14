'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronDown, ChevronUp, BookOpen } from 'lucide-react'
import { financesApi, JournalEntryDetail } from '@/lib/api/finances'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDecimal(val: number, currencyCode: string | null | undefined): string {
  const code = currencyCode ?? 'USD'
  const noDecimals = ['KRW', 'JPY', 'VND', 'IDR', 'HUF', 'CLP']
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: noDecimals.includes(code) ? 0 : 2,
    maximumFractionDigits: noDecimals.includes(code) ? 0 : 2,
  }).format(val)
}

// ---------------------------------------------------------------------------
// Entry display
// ---------------------------------------------------------------------------

function EntryLines({ entry }: { entry: JournalEntryDetail }) {
  const lines = Array.isArray(entry.lines) ? entry.lines : []
  const debitTotal = lines.length > 0
    ? lines.reduce((sum, line) => sum + line.debit, 0)
    : entry.debit_total
  const creditTotal = lines.length > 0
    ? lines.reduce((sum, line) => sum + line.credit, 0)
    : entry.credit_total

  return (
    <div
      style={{
        borderRadius: '0 0.625rem 0.625rem 0.625rem',
        background: '#f4f7f0',
        overflow: 'hidden',
        marginTop: '0.5rem',
      }}
    >
      {/* Column headers */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 5rem 5rem',
          gap: '0.5rem',
          padding: '0.5rem 0.875rem',
          borderBottom: '1px solid rgba(173,180,168,0.25)',
        }}
      >
        {['Account', 'Debit', 'Credit'].map((h) => (
          <span
            key={h}
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.6875rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: '#767d72',
              textAlign: h === 'Account' ? 'left' : 'right',
            }}
          >
            {h}
          </span>
        ))}
      </div>

      {lines.map((line, i) => (
        <div
          key={i}
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 5rem 5rem',
            gap: '0.5rem',
            padding: '0.5rem 0.875rem',
            borderBottom: i < lines.length - 1 ? '1px solid rgba(173,180,168,0.12)' : 'none',
          }}
        >
          <div>
            <span
              style={{
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.875rem',
                color: '#2e342b',
              }}
            >
              #{line.account_id}
            </span>
            {line.memo && (
              <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72', marginTop: '0.125rem' }}>
                {line.memo}
              </p>
            )}
          </div>
          <span
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              color: line.debit > 0 ? '#2e342b' : '#adb4a8',
              textAlign: 'right',
            }}
          >
            {line.debit > 0 ? formatDecimal(line.debit, line.currency_code) : '—'}
          </span>
          <span
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              color: line.credit > 0 ? '#2e342b' : '#adb4a8',
              textAlign: 'right',
            }}
          >
            {line.credit > 0 ? formatDecimal(line.credit, line.currency_code) : '—'}
          </span>
        </div>
      ))}

      {lines.length === 0 && (
        <div
          style={{
            padding: '0.625rem 0.875rem',
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.8125rem',
            color: '#767d72',
          }}
        >
          No line details available.
        </div>
      )}

      {/* Totals */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 5rem 5rem',
          gap: '0.5rem',
          padding: '0.5rem 0.875rem',
          borderTop: '1px solid rgba(173,180,168,0.25)',
          background: 'rgba(173,180,168,0.08)',
        }}
      >
        <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', fontWeight: 700, color: '#767d72' }}>
          Total
        </span>
        <span
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.875rem',
            fontWeight: 700,
            color: '#3a5c35',
            textAlign: 'right',
          }}
        >
          {formatDecimal(debitTotal, null)}
        </span>
        <span
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.875rem',
            fontWeight: 700,
            color: '#3a5c35',
            textAlign: 'right',
          }}
        >
          {formatDecimal(creditTotal, null)}
        </span>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// JournalEntryViewer — progressive disclosure
// ---------------------------------------------------------------------------

interface JournalEntryViewerProps {
  /** The journal entry ID to fetch and display. */
  journalEntryId: number
  /** Label shown on the toggle button. Defaults to "View Journal Entry". */
  label?: string
}

export function JournalEntryViewer({
  journalEntryId,
  label = 'View Journal Entry',
}: JournalEntryViewerProps) {
  const [expanded, setExpanded] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['finance', 'journal', journalEntryId],
    queryFn: () => financesApi.getJournalEntry(journalEntryId),
    enabled: expanded,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })

  return (
    <div>
      {/* Toggle */}
      <button
        onClick={() => setExpanded((p) => !p)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.375rem',
          padding: '0.375rem 0.875rem',
          borderRadius: '9999px',
          border: 'none',
          background: expanded ? '#e8f0e3' : 'transparent',
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.8125rem',
          fontWeight: 600,
          color: '#3a5c35',
          cursor: 'pointer',
          transition: 'background 0.15s',
        }}
      >
        <BookOpen size={13} />
        {label}
        {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>

      {/* Content */}
      {expanded && (
        <div style={{ marginTop: '0.5rem' }}>
          {isLoading && (
            <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#767d72', padding: '0.5rem 0' }}>
              Loading…
            </p>
          )}
          {error && (
            <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#c0392b', padding: '0.5rem 0' }}>
              Could not load journal entry.
            </p>
          )}
          {data?.entry && <EntryLines entry={data.entry} />}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Inline list variant — shows all journal entries for power users
// ---------------------------------------------------------------------------

export function JournalEntryList() {
  const [expanded, setExpanded] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['finance', 'journal', 'list'],
    queryFn: () => financesApi.listJournalEntries(),
    enabled: expanded,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })

  const entries = data?.entries ?? []

  return (
    <div>
      <button
        onClick={() => setExpanded((p) => !p)}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.375rem',
          padding: '0.5rem 1rem',
          borderRadius: '9999px',
          border: 'none',
          background: expanded ? '#e8f0e3' : '#f4f7f0',
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.875rem',
          fontWeight: 600,
          color: '#3a5c35',
          cursor: 'pointer',
        }}
      >
        <BookOpen size={14} />
        Journal Entries
        {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>

      {expanded && (
        <div style={{ marginTop: '1rem' }}>
          {isLoading && (
            <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#767d72' }}>
              Loading…
            </p>
          )}
          {!isLoading && entries.length === 0 && (
            <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#767d72' }}>
              No journal entries yet.
            </p>
          )}
          {entries.map((entry) => (
            <div key={entry.id} style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', fontWeight: 700, color: '#5a6157' }}>
                  #{entry.entry_number}
                </span>
                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
                  {new Date(entry.posted_at).toLocaleDateString()}
                </span>
                {entry.description && (
                  <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#2e342b' }}>
                    {entry.description}
                  </span>
                )}
              </div>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 5rem 5rem',
                  gap: '0.5rem',
                  padding: '0.5rem 0.875rem',
                  borderRadius: '0 0.625rem 0.625rem 0.625rem',
                  background: '#f4f7f0',
                }}
              >
                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
                  {entry.lines} line{entry.lines === 1 ? '' : 's'}
                </span>
                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#2e342b', textAlign: 'right' }}>
                  {formatDecimal(entry.debit_total, null)}
                </span>
                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#2e342b', textAlign: 'right' }}>
                  {formatDecimal(entry.credit_total, null)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
