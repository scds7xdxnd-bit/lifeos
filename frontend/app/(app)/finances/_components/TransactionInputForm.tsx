'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Plus, Minus } from 'lucide-react'
import { financesApi, Account, CreateTransactionInput, CreateSplitTransactionInput } from '@/lib/api/finances'

type Mode = 'simple' | 'split' | 'transfer'

interface SplitLine {
  account_id: number | null
  accountName: string
  amount: string
  memo: string
}

interface TransactionInputFormProps {
  accounts: Account[]
  onSuccess?: () => void
  onCancel?: () => void
  defaultCurrency?: string
  labelTitle?: string
  labelSubmit?: string
  labelCancel?: string
}

const PILL_STYLE = {
  borderRadius: '9999px',
  border: 'none',
  cursor: 'pointer',
  fontFamily: 'var(--font-manrope), sans-serif',
  fontWeight: 600,
  fontSize: '0.8125rem',
  padding: '0.375rem 0.875rem',
}

export function TransactionInputForm({
  accounts,
  onSuccess,
  onCancel,
  defaultCurrency,
  labelTitle = 'Record transaction',
  labelSubmit = 'Save',
  labelCancel = 'Cancel',
}: TransactionInputFormProps) {
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<Mode>('simple')
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  const [debitId, setDebitId] = useState<number | null>(null)
  const [creditId, setCreditId] = useState<number | null>(null)
  const [splitLines, setSplitLines] = useState<SplitLine[]>([
    { account_id: null, accountName: '', amount: '', memo: '' },
    { account_id: null, accountName: '', amount: '', memo: '' },
  ])
  const [error, setError] = useState<string | null>(null)

  const incomeExpenseAccounts = accounts.filter((a) =>
    ['income', 'expense'].includes(a.account_type)
  )
  const balanceSheetAccounts = accounts.filter((a) =>
    ['asset', 'liability'].includes(a.account_type)
  )

  const simpleCreate = useMutation({
    mutationFn: (data: CreateTransactionInput) => financesApi.createTransaction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'transactions'] })
      onSuccess?.()
    },
    onError: () => setError('Failed to save. Please try again.'),
  })

  const splitCreate = useMutation({
    mutationFn: (data: CreateSplitTransactionInput) => financesApi.createSplitTransaction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'transactions'] })
      onSuccess?.()
    },
    onError: () => setError('Failed to save. Please try again.'),
  })

  const isPending = simpleCreate.isPending || splitCreate.isPending

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (mode === 'simple') {
      if (!debitId || !creditId || !amount) {
        setError('Please fill all required fields.')
        return
      }
      simpleCreate.mutate({
        debit_account_id: debitId,
        credit_account_id: creditId,
        amount: parseFloat(amount),
        currency_code: defaultCurrency ?? null,
        description: description || null,
      })
    } else if (mode === 'split') {
      if (!creditId || !amount) {
        setError('Please fill all required fields.')
        return
      }
      const lines = splitLines.filter((l) => l.account_id && l.amount)
      if (lines.length < 2) {
        setError('A split transaction requires at least 2 lines.')
        return
      }
      splitCreate.mutate({
        credit_account_id: creditId,
        total_amount: parseFloat(amount),
        currency_code: defaultCurrency ?? null,
        description: description || null,
        split_lines: lines.map((l) => ({
          account_id: l.account_id!,
          amount: parseFloat(l.amount),
          memo: l.memo || null,
        })),
      })
    }
  }

  const inputStyle: React.CSSProperties = {
    fontFamily: 'var(--font-manrope), sans-serif',
    fontSize: '0.875rem',
    color: '#2e342b',
    background: '#f1f5eb',
    border: 'none',
    borderRadius: '8px',
    padding: '0.5rem 0.75rem',
    width: '100%',
    outline: 'none',
  }

  const labelStyle: React.CSSProperties = {
    fontFamily: 'var(--font-manrope), sans-serif',
    fontSize: '0.6875rem',
    fontWeight: 700,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
    color: '#767d72',
    display: 'block',
    marginBottom: '0.25rem',
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="flex items-center justify-between mb-4">
        <p
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '1.125rem',
            fontWeight: 300,
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          {labelTitle}
        </p>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#767d72' }}
          >
            <X size={16} />
          </button>
        )}
      </div>

      {/* Mode tabs */}
      <div className="flex gap-2 mb-4">
        {(['simple', 'split', 'transfer'] as Mode[]).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => { setMode(m); setError(null) }}
            style={{
              ...PILL_STYLE,
              background: mode === m ? '#3a5c35' : '#e8f0e3',
              color: mode === m ? '#ffffff' : '#3a5c35',
            }}
          >
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {/* Amount */}
        <div>
          <label style={labelStyle}>Amount {defaultCurrency ? `(${defaultCurrency})` : ''}</label>
          <input
            type="number"
            min="0.01"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            style={inputStyle}
            required
          />
        </div>

        {/* Description */}
        <div>
          <label style={labelStyle}>Description</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g. Lunch at café"
            style={inputStyle}
          />
        </div>

        {mode === 'simple' && (
          <>
            <div>
              <label style={labelStyle}>Debit account (what was used)</label>
              <select
                value={debitId ?? ''}
                onChange={(e) => setDebitId(Number(e.target.value))}
                style={inputStyle}
                required
              >
                <option value="">Select account…</option>
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>{a.name} ({a.account_type})</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Credit account (source of funds)</label>
              <select
                value={creditId ?? ''}
                onChange={(e) => setCreditId(Number(e.target.value))}
                style={inputStyle}
                required
              >
                <option value="">Select account…</option>
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>{a.name} ({a.account_type})</option>
                ))}
              </select>
            </div>
          </>
        )}

        {mode === 'split' && (
          <>
            <div>
              <label style={labelStyle}>Source account (credit)</label>
              <select
                value={creditId ?? ''}
                onChange={(e) => setCreditId(Number(e.target.value))}
                style={inputStyle}
                required
              >
                <option value="">Select account…</option>
                {balanceSheetAccounts.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Split lines</label>
              {splitLines.map((line, i) => (
                <div key={i} className="flex gap-2 mb-2">
                  <select
                    value={line.account_id ?? ''}
                    onChange={(e) => {
                      const updated = [...splitLines]
                      updated[i] = { ...updated[i], account_id: Number(e.target.value) }
                      setSplitLines(updated)
                    }}
                    style={{ ...inputStyle, flex: 2 }}
                  >
                    <option value="">Account…</option>
                    {incomeExpenseAccounts.map((a) => (
                      <option key={a.id} value={a.id}>{a.name}</option>
                    ))}
                  </select>
                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    placeholder="0.00"
                    value={line.amount}
                    onChange={(e) => {
                      const updated = [...splitLines]
                      updated[i] = { ...updated[i], amount: e.target.value }
                      setSplitLines(updated)
                    }}
                    style={{ ...inputStyle, flex: 1 }}
                  />
                  {splitLines.length > 2 && (
                    <button
                      type="button"
                      onClick={() => setSplitLines(splitLines.filter((_, j) => j !== i))}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#e8735c' }}
                    >
                      <Minus size={14} />
                    </button>
                  )}
                </div>
              ))}
              <button
                type="button"
                onClick={() => setSplitLines([...splitLines, { account_id: null, accountName: '', amount: '', memo: '' }])}
                style={{
                  ...PILL_STYLE,
                  background: '#e8f0e3',
                  color: '#3a5c35',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem',
                }}
              >
                <Plus size={12} /> Add line
              </button>
            </div>
          </>
        )}

        {mode === 'transfer' && (
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              color: '#5a6157',
            }}
          >
            Use the full journal entry form to record transfers between accounts.
          </p>
        )}
      </div>

      {error && (
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.8125rem',
            color: '#e8735c',
            marginTop: '0.75rem',
          }}
        >
          {error}
        </p>
      )}

      <div className="flex gap-2 mt-5">
        <button
          type="submit"
          disabled={isPending || mode === 'transfer'}
          style={{
            ...PILL_STYLE,
            background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
            color: '#ffffff',
            opacity: isPending || mode === 'transfer' ? 0.6 : 1,
          }}
        >
          {isPending ? 'Saving…' : labelSubmit}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            style={{ ...PILL_STYLE, background: '#e8f0e3', color: '#3a5c35' }}
          >
            {labelCancel}
          </button>
        )}
      </div>
    </form>
  )
}
