'use client'

import { useQuery } from '@tanstack/react-query'
import { Landmark, CreditCard, TrendingUp, DollarSign, ShoppingBag } from 'lucide-react'
import { financesApi, Account } from '@/lib/api/finances'

const TYPE_ICONS: Record<string, React.ComponentType<{ size: number; style?: React.CSSProperties }>> = {
  asset: Landmark,
  liability: CreditCard,
  equity: TrendingUp,
  income: DollarSign,
  expense: ShoppingBag,
}

const TYPE_COLORS: Record<string, string> = {
  asset: '#3a5c35',
  liability: '#e8735c',
  equity: '#4b6646',
  income: '#3a5c35',
  expense: '#767d72',
}

interface AccountListProps {
  onSelect?: (account: Account) => void
  filterType?: string
  labelEmpty?: string
  labelLoading?: string
}

function AccountRow({ account, onSelect }: { account: Account; onSelect?: (a: Account) => void }) {
  const Icon = TYPE_ICONS[account.account_type] ?? DollarSign
  const color = TYPE_COLORS[account.account_type] ?? '#5a6157'

  return (
    <div
      className="flex items-center justify-between py-3"
      style={{
        borderBottom: '1px solid rgba(173, 180, 168, 0.2)',
        cursor: onSelect ? 'pointer' : 'default',
      }}
      onClick={() => onSelect?.(account)}
    >
      <div className="flex items-center gap-3">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
          style={{ background: '#e8f0e3' }}
        >
          <Icon size={14} style={{ color }} />
        </div>
        <div>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: account.is_active ? '#2e342b' : '#adb4a8',
            }}
          >
            {account.name}
          </p>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.75rem',
              color: '#767d72',
            }}
          >
            {account.account_subtype ?? account.account_type}
            {account.code && ` · ${account.code}`}
          </p>
        </div>
      </div>
      {!account.is_active && (
        <span
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#adb4a8',
            background: '#f1f5eb',
            borderRadius: '9999px',
            padding: '0.125rem 0.5rem',
          }}
        >
          Inactive
        </span>
      )}
    </div>
  )
}

export function AccountList({
  onSelect,
  filterType,
  labelEmpty = 'No accounts found.',
  labelLoading = 'Loading…',
}: AccountListProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['finance', 'accounts', { account_type: filterType }],
    queryFn: () =>
      financesApi.listAccounts(filterType ? { account_type: filterType, per_page: 200 } : { per_page: 200 }),
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

  const accounts = data?.accounts ?? []

  if (accounts.length === 0) {
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

  // Group by account_type for display
  const groups: Record<string, Account[]> = {}
  for (const a of accounts) {
    if (!groups[a.account_type]) groups[a.account_type] = []
    groups[a.account_type].push(a)
  }

  const ORDER = ['asset', 'liability', 'equity', 'income', 'expense']

  return (
    <div>
      {ORDER.filter((t) => groups[t]).map((type) => (
        <div key={type} className="mb-4">
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.6875rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: TYPE_COLORS[type] ?? '#767d72',
              marginBottom: '0.25rem',
            }}
          >
            {type}
          </p>
          {groups[type].map((a) => (
            <AccountRow key={a.id} account={a} onSelect={onSelect} />
          ))}
        </div>
      ))}
    </div>
  )
}
