'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Pencil, Trash2, AlertTriangle } from 'lucide-react'
import { financesApi, Transaction } from '@/lib/api/finances'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatAmount(amount: number, currencyCode: string | null): string {
  const code = currencyCode ?? 'USD'
  const noDecimals = ['KRW', 'JPY', 'VND', 'IDR', 'HUF', 'CLP']
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: code,
    minimumFractionDigits: noDecimals.includes(code) ? 0 : 2,
    maximumFractionDigits: noDecimals.includes(code) ? 0 : 2,
  }).format(amount)
}

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(iso))
}

function isWithin24h(iso: string): boolean {
  return Date.now() - new Date(iso).getTime() < 24 * 60 * 60 * 1000
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '0.5rem 0', borderBottom: '1px solid rgba(173,180,168,0.15)' }}>
      <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
        {label}
      </span>
      <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.9375rem', fontWeight: 500, color: '#2e342b', textAlign: 'right', maxWidth: '60%' }}>
        {value}
      </span>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Edit form (metadata only — within 24h grace period)
// ---------------------------------------------------------------------------

function EditForm({
  transaction,
  onSaved,
  onCancel,
}: {
  transaction: Transaction
  onSaved: () => void
  onCancel: () => void
}) {
  const qc = useQueryClient()
  const [description, setDescription] = useState(transaction.description ?? '')
  const [counterparty, setCounterparty] = useState(transaction.counterparty ?? '')
  const [category, setCategory] = useState(transaction.category ?? '')
  const [occurredAt, setOccurredAt] = useState(
    transaction.occurred_at ? transaction.occurred_at.slice(0, 16) : ''
  )
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () =>
      financesApi.updateTransaction(transaction.id, {
        description: description || null,
        counterparty: counterparty || null,
        category: category || null,
        occurred_at: occurredAt ? new Date(occurredAt).toISOString() : null,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['finance', 'transactions'] })
      onSaved()
    },
    onError: (err: Error) => setError(err.message),
  })

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '0.5rem 0.75rem',
    borderRadius: '0.5rem',
    border: 'none',
    background: '#f4f7f0',
    fontFamily: 'var(--font-manrope), sans-serif',
    fontSize: '0.9375rem',
    color: '#2e342b',
    outline: 'none',
  }

  const labelStyle: React.CSSProperties = {
    fontFamily: 'var(--font-manrope), sans-serif',
    fontSize: '0.6875rem',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    color: '#5a6157',
    display: 'block',
    marginBottom: '0.25rem',
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', background: '#f4f7f0', borderRadius: '0.5rem', padding: '0.5rem 0.75rem' }}>
        Within the 24-hour window — you can edit metadata. Amount and account changes require voiding this transaction.
      </p>

      <div><label style={labelStyle}>Description</label><input style={inputStyle} value={description} onChange={(e) => setDescription(e.target.value)} /></div>
      <div><label style={labelStyle}>Counterparty</label><input style={inputStyle} value={counterparty} onChange={(e) => setCounterparty(e.target.value)} /></div>
      <div><label style={labelStyle}>Category</label><input style={inputStyle} value={category} onChange={(e) => setCategory(e.target.value)} /></div>
      <div>
        <label style={labelStyle}>Occurred At</label>
        <input type="datetime-local" style={inputStyle} value={occurredAt} onChange={(e) => setOccurredAt(e.target.value)} />
      </div>

      {error && (
        <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#c0392b' }}>{error}</p>
      )}

      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
        <button onClick={onCancel} style={{ padding: '0.5rem 1rem', borderRadius: '9999px', border: 'none', background: '#e8f0e3', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#3a5c35', cursor: 'pointer' }}>
          Cancel
        </button>
        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          style={{ padding: '0.5rem 1.25rem', borderRadius: '9999px', border: 'none', background: '#3a5c35', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#fff', cursor: 'pointer', opacity: mutation.isPending ? 0.6 : 1 }}
        >
          {mutation.isPending ? 'Saving…' : 'Save'}
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Void confirmation
// ---------------------------------------------------------------------------

function VoidConfirm({
  transaction,
  onVoided,
  onCancel,
}: {
  transaction: Transaction
  onVoided: () => void
  onCancel: () => void
}) {
  const qc = useQueryClient()
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => financesApi.voidTransaction(transaction.id, { reason: reason || null }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['finance', 'transactions'] })
      onVoided()
    },
    onError: (err: Error) => setError(err.message),
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', gap: '0.625rem', alignItems: 'flex-start', background: 'rgba(192,57,43,0.07)', borderRadius: '0.625rem', padding: '0.75rem 1rem' }}>
        <AlertTriangle size={16} style={{ color: '#c0392b', flexShrink: 0, marginTop: '0.125rem' }} />
        <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#c0392b', lineHeight: 1.5 }}>
          This will create a reversal journal entry. The original transaction is preserved for audit.
        </p>
      </div>

      <div>
        <label style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase' as const, letterSpacing: '0.06em', color: '#5a6157', display: 'block', marginBottom: '0.25rem' }}>
          Reason (optional)
        </label>
        <input
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="e.g. Entered wrong amount"
          style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', border: 'none', background: '#f4f7f0', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.9375rem', color: '#2e342b', outline: 'none' }}
        />
      </div>

      {error && (
        <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#c0392b' }}>{error}</p>
      )}

      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
        <button onClick={onCancel} style={{ padding: '0.5rem 1rem', borderRadius: '9999px', border: 'none', background: '#e8f0e3', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#3a5c35', cursor: 'pointer' }}>
          Cancel
        </button>
        <button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          style={{ padding: '0.5rem 1.25rem', borderRadius: '9999px', border: 'none', background: '#c0392b', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#fff', cursor: 'pointer', opacity: mutation.isPending ? 0.6 : 1 }}
        >
          {mutation.isPending ? 'Voiding…' : 'Void Transaction'}
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

type Panel = 'detail' | 'edit' | 'void'

interface TransactionDetailProps {
  transaction: Transaction
  onClose: () => void
}

export function TransactionDetail({ transaction, onClose }: TransactionDetailProps) {
  const [panel, setPanel] = useState<Panel>('detail')

  const canEdit = !transaction.is_void && isWithin24h(transaction.occurred_at)
  const canVoid = !transaction.is_void

  return (
    <>
      {/* Backdrop */}
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(46,52,43,0.35)', zIndex: 40 }} />

      {/* Panel */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: '100%',
          maxWidth: '440px',
          background: '#fafbf7',
          zIndex: 50,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '-8px 0 32px rgba(46,52,43,0.12)',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1.25rem 1.5rem', borderBottom: '1px solid rgba(173,180,168,0.2)' }}>
          <div>
            <h2 style={{ fontFamily: 'var(--font-newsreader), serif', fontSize: '1.25rem', fontWeight: 600, color: transaction.is_void ? '#adb4a8' : '#2e342b', letterSpacing: '-0.02em', textDecoration: transaction.is_void ? 'line-through' : 'none' }}>
              {formatAmount(transaction.amount, transaction.currency_code)}
            </h2>
            {transaction.is_void && (
              <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#c0392b' }}>
                Void
              </span>
            )}
          </div>
          <button onClick={onClose} style={{ width: '2rem', height: '2rem', borderRadius: '9999px', border: 'none', background: '#e8f0e3', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#3a5c35' }}>
            <X size={14} />
          </button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
          {panel === 'detail' && (
            <div>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <Row label="Date" value={formatDate(transaction.occurred_at)} />
                {transaction.description && <Row label="Description" value={transaction.description} />}
                {transaction.counterparty && <Row label="Counterparty" value={transaction.counterparty} />}
                {transaction.category && <Row label="Category" value={transaction.category} />}
                <Row label="Source" value={transaction.source} />
                {transaction.currency_code && <Row label="Currency" value={transaction.currency_code} />}
                {transaction.edited_at && <Row label="Last Edited" value={formatDate(transaction.edited_at)} />}
                {transaction.void_of_id && <Row label="Reversal Of" value={`#${transaction.void_of_id}`} />}
              </div>

              {/* Actions */}
              {!transaction.is_void && (
                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
                  {canEdit && (
                    <button
                      onClick={() => setPanel('edit')}
                      style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.375rem', padding: '0.625rem', borderRadius: '9999px', border: 'none', background: '#e8f0e3', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#3a5c35', cursor: 'pointer' }}
                    >
                      <Pencil size={13} /> Edit
                    </button>
                  )}
                  {canVoid && (
                    <button
                      onClick={() => setPanel('void')}
                      style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.375rem', padding: '0.625rem', borderRadius: '9999px', border: '1px solid rgba(192,57,43,0.3)', background: 'transparent', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#c0392b', cursor: 'pointer' }}
                    >
                      <Trash2 size={13} /> Void
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          {panel === 'edit' && (
            <EditForm
              transaction={transaction}
              onSaved={() => setPanel('detail')}
              onCancel={() => setPanel('detail')}
            />
          )}

          {panel === 'void' && (
            <VoidConfirm
              transaction={transaction}
              onVoided={onClose}
              onCancel={() => setPanel('detail')}
            />
          )}
        </div>
      </div>
    </>
  )
}
