'use client'

import { useQuery } from '@tanstack/react-query'
import { ArrowUpRight, ArrowDownLeft, RefreshCw, Ban } from 'lucide-react'
import { financesApi, Transaction } from '@/lib/api/finances'

interface TransactionListProps {
  limit?: number
  onViewAll?: () => void
  onSelect?: (txn: Transaction) => void
  labelViewAll?: string
  labelEmpty?: string
  labelLoading?: string
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function formatAmount(amount: number, currency?: string | null): string {
  const symbol = currency === 'KRW' ? '₩' : currency === 'EUR' ? '€' : '$'
  const decimals = currency === 'KRW' || currency === 'JPY' ? 0 : 2
  return `${symbol}${amount.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`
}

function TransactionRow({ txn, onSelect }: { txn: Transaction; onSelect?: (txn: Transaction) => void }) {
  const isVoid = txn.is_void
  return (
    <div
      className="flex items-center justify-between py-3"
      style={{
        borderBottom: '1px solid rgba(173, 180, 168, 0.2)',
        opacity: isVoid ? 0.45 : 1,
        cursor: onSelect ? 'pointer' : 'default',
      }}
      onClick={() => onSelect?.(txn)}
    >
      <div className="flex items-center gap-3 min-w-0">
        <div
          className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
          style={{ background: '#f1f5eb' }}
        >
          {isVoid ? (
            <Ban size={14} style={{ color: '#e8735c' }} />
          ) : txn.source === 'calendar_inferred' ? (
            <RefreshCw size={14} style={{ color: '#767d72' }} />
          ) : txn.void_of_id ? (
            <ArrowUpRight size={14} style={{ color: '#3a5c35' }} />
          ) : (
            <ArrowDownLeft size={14} style={{ color: '#5a6157' }} />
          )}
        </div>
        <div className="min-w-0">
          <p
            className="truncate"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              color: '#2e342b',
              fontWeight: 500,
            }}
          >
            {txn.description || txn.counterparty || 'Transaction'}
          </p>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.75rem',
              color: '#767d72',
            }}
          >
            {formatDate(txn.occurred_at)}
            {txn.category && ` · ${txn.category}`}
          </p>
        </div>
      </div>
      <p
        className="flex-shrink-0 ml-4"
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.9375rem',
          fontWeight: 600,
          color: isVoid ? '#767d72' : '#2e342b',
          textDecoration: isVoid ? 'line-through' : 'none',
        }}
      >
        {formatAmount(txn.amount, txn.currency_code)}
      </p>
    </div>
  )
}

export function TransactionList({
  limit = 10,
  onViewAll,
  onSelect,
  labelViewAll = 'View all transactions',
  labelEmpty = 'No transactions yet.',
  labelLoading = 'Loading…',
}: TransactionListProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['finance', 'transactions', { per_page: limit }],
    queryFn: () => financesApi.listTransactions({ per_page: limit }),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })

  if (isLoading) {
    return (
      <p
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.875rem',
          color: '#767d72',
          padding: '1rem 0',
        }}
      >
        {labelLoading}
      </p>
    )
  }

  const transactions = data?.transactions ?? []

  if (transactions.length === 0) {
    return (
      <p
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.875rem',
          color: '#767d72',
          padding: '1rem 0',
        }}
      >
        {labelEmpty}
      </p>
    )
  }

  return (
    <div>
      {transactions.map((txn) => (
        <TransactionRow key={txn.id} txn={txn} onSelect={onSelect} />
      ))}
      {onViewAll && data && data.total > limit && (
        <button
          onClick={onViewAll}
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.8125rem',
            color: '#3a5c35',
            fontWeight: 600,
            marginTop: '0.75rem',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 0,
          }}
        >
          {labelViewAll} ({data.total})
        </button>
      )}
    </div>
  )
}
