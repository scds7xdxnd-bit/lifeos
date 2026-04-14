'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Wallet, Plus, BookOpen, ChevronRight, UserPlus } from 'lucide-react'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import { financesApi, Account, Transaction } from '@/lib/api/finances'
import { FinanceSummaryCard } from './_components/FinanceSummaryCard'
import { TransactionList } from './_components/TransactionList'
import { TransactionInputForm } from './_components/TransactionInputForm'
import { AccountList } from './_components/AccountList'
import { AccountDrawer } from './_components/AccountDrawer'
import { TransactionDetail } from './_components/TransactionDetail'
import { JournalEntryList } from './_components/JournalEntryViewer'

type ActivePanel = 'overview' | 'add-transaction' | 'accounts' | 'journal'

const PILL: React.CSSProperties = {
  borderRadius: '9999px',
  border: 'none',
  cursor: 'pointer',
  fontFamily: 'var(--font-manrope), sans-serif',
  fontWeight: 600,
  fontSize: '0.8125rem',
  padding: '0.375rem 0.875rem',
  display: 'inline-flex',
  alignItems: 'center',
  gap: '0.3rem',
}

const CARD: React.CSSProperties = {
  background: '#ffffff',
  borderRadius: '0 16px 16px 16px',
  boxShadow: '0 4px 16px rgba(46, 52, 43, 0.06)',
  padding: '1.5rem',
}

export default function FinancesPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).finances
  const qc = useQueryClient()
  const [panel, setPanel] = useState<ActivePanel>('overview')

  // Drawer state
  const [drawerAccount, setDrawerAccount] = useState<Account | null | undefined>(undefined)
  // undefined = closed, null = new account, Account = edit

  // Transaction detail state
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)

  const { data: accountsData } = useQuery({
    queryKey: ['finance', 'accounts'],
    queryFn: () => financesApi.listAccounts({ per_page: 200 }),
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })
  const accounts = accountsData?.accounts ?? []

  const { data: trialData } = useQuery({
    queryKey: ['finance', 'trial-balance'],
    queryFn: () => financesApi.getTrialBalance(),
    staleTime: 5 * 60 * 1000,
    retry: 1,
    enabled: accounts.length > 0,
  })

  const seedMutation = useMutation({
    mutationFn: financesApi.seedAccounts,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['finance'] }),
  })

  const hasAccounts = accounts.length > 0

  const totalAssets =
    trialData?.accounts
      ?.filter((a) => accounts.find((acc) => acc.id === a.account_id)?.account_type === 'asset')
      .reduce((s, a) => s + (a.balance ?? 0), 0) ?? null

  const totalLiabilities =
    trialData?.accounts
      ?.filter((a) => accounts.find((acc) => acc.id === a.account_id)?.account_type === 'liability')
      .reduce((s, a) => s + Math.abs(a.balance ?? 0), 0) ?? null

  const netWorth =
    totalAssets !== null && totalLiabilities !== null
      ? totalAssets - totalLiabilities
      : null

  const isDrawerOpen = drawerAccount !== undefined

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#3a5c35',
            marginBottom: '0.5rem',
          }}
        >
          {t.eyebrow}
        </p>
        <h1
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '2rem',
            fontWeight: 300,
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          {t.title}
        </h1>
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.9375rem',
            color: '#5a6157',
            lineHeight: 1.65,
            marginTop: '0.25rem',
          }}
        >
          {t.primaryQuestion}
        </p>
      </div>

      {/* Onboarding: seed if no accounts */}
      {!hasAccounts && (
        <div style={{ ...CARD, textAlign: 'center', padding: '2.5rem' }}>
          <div
            className="w-14 h-14 rounded-full mx-auto mb-4 flex items-center justify-center"
            style={{ background: '#e8f0e3' }}
          >
            <Wallet size={24} style={{ color: '#3a5c35' }} />
          </div>
          <p
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontSize: '1.125rem',
              fontWeight: 300,
              color: '#4b6646',
              letterSpacing: '-0.03em',
              marginBottom: '0.5rem',
            }}
          >
            {t.setupTitle}
          </p>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              color: '#767d72',
              lineHeight: 1.65,
              maxWidth: '24rem',
              margin: '0 auto 1.5rem',
            }}
          >
            {t.setupBody}
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => seedMutation.mutate()}
              disabled={seedMutation.isPending}
              style={{
                ...PILL,
                background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
                color: '#ffffff',
                opacity: seedMutation.isPending ? 0.65 : 1,
              }}
            >
              {seedMutation.isPending ? t.settingUp : t.setupCta}
            </button>
            <button
              onClick={() => setDrawerAccount(null)}
              style={{ ...PILL, background: '#e8f0e3', color: '#3a5c35' }}
            >
              <UserPlus size={13} />
              {t.addAccountManually ?? 'Add manually'}
            </button>
          </div>
        </div>
      )}

      {hasAccounts && (
        <>
          {/* Summary cards */}
          {netWorth !== null && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <FinanceSummaryCard label={t.netWorth} amount={netWorth} />
              {totalAssets !== null && (
                <FinanceSummaryCard label={t.totalAssets} amount={totalAssets} trend="up" />
              )}
              {totalLiabilities !== null && (
                <FinanceSummaryCard
                  label={t.totalLiabilities}
                  amount={totalLiabilities}
                  trend={totalLiabilities > 0 ? 'down' : 'neutral'}
                />
              )}
            </div>
          )}

          {/* Action bar */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setPanel(panel === 'add-transaction' ? 'overview' : 'add-transaction')}
              style={{
                ...PILL,
                background:
                  panel === 'add-transaction'
                    ? 'linear-gradient(135deg, #4b6646, #3f5a3a)'
                    : '#e8f0e3',
                color: panel === 'add-transaction' ? '#ffffff' : '#3a5c35',
              }}
            >
              <Plus size={14} />
              {t.addTransaction}
            </button>
            <button
              onClick={() => setPanel(panel === 'accounts' ? 'overview' : 'accounts')}
              style={{
                ...PILL,
                background: panel === 'accounts' ? '#e8f0e3' : 'transparent',
                color: '#3a5c35',
              }}
            >
              {t.accounts}
              <ChevronRight
                size={13}
                style={{
                  transform: panel === 'accounts' ? 'rotate(90deg)' : 'none',
                  transition: 'transform 0.15s',
                }}
              />
            </button>
            <button
              onClick={() => setPanel(panel === 'journal' ? 'overview' : 'journal')}
              style={{
                ...PILL,
                background: panel === 'journal' ? '#e8f0e3' : 'transparent',
                color: '#3a5c35',
              }}
            >
              <BookOpen size={13} />
              {t.journal}
            </button>
          </div>

          {/* Add transaction panel */}
          {panel === 'add-transaction' && (
            <div style={CARD}>
              <TransactionInputForm
                accounts={accounts}
                onSuccess={() => setPanel('overview')}
                onCancel={() => setPanel('overview')}
                labelTitle={t.addTransaction}
                labelSubmit={t.save}
                labelCancel={t.cancel}
              />
            </div>
          )}

          {/* Accounts panel */}
          {panel === 'accounts' && (
            <div style={CARD}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <p
                  style={{
                    fontFamily: 'var(--font-serif), Georgia, serif',
                    fontSize: '1.125rem',
                    fontWeight: 300,
                    color: '#4b6646',
                    letterSpacing: '-0.03em',
                  }}
                >
                  {t.accounts}
                </p>
                <button
                  onClick={() => setDrawerAccount(null)}
                  style={{ ...PILL, background: '#e8f0e3', color: '#3a5c35', fontSize: '0.8125rem' }}
                >
                  <Plus size={13} />
                  {t.addAccount ?? 'Add Account'}
                </button>
              </div>
              <AccountList
                labelEmpty={t.noAccounts}
                onSelect={(account) => setDrawerAccount(account)}
              />
            </div>
          )}

          {/* Journal panel */}
          {panel === 'journal' && (
            <div style={CARD}>
              <p
                style={{
                  fontFamily: 'var(--font-serif), Georgia, serif',
                  fontSize: '1.125rem',
                  fontWeight: 300,
                  color: '#4b6646',
                  letterSpacing: '-0.03em',
                  marginBottom: '1rem',
                }}
              >
                {t.journal}
              </p>
              <JournalEntryList />
            </div>
          )}

          {/* Overview: recent transactions */}
          {panel === 'overview' && (
            <div style={CARD}>
              <p
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  color: '#767d72',
                  marginBottom: '0.75rem',
                }}
              >
                {t.recentTransactions}
              </p>
              <TransactionList
                limit={10}
                labelEmpty={t.noTransactions}
                labelLoading={t.loading}
                labelViewAll={t.viewAll}
                onSelect={(tx) => setSelectedTransaction(tx)}
              />
            </div>
          )}
        </>
      )}

      {/* Account drawer (create / edit) */}
      {isDrawerOpen && (
        <AccountDrawer
          account={drawerAccount ?? undefined}
          onClose={() => setDrawerAccount(undefined)}
          onSuccess={() => {
            setDrawerAccount(undefined)
            qc.invalidateQueries({ queryKey: ['finance', 'accounts'] })
          }}
        />
      )}

      {/* Transaction detail drawer */}
      {selectedTransaction && (
        <TransactionDetail
          transaction={selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
        />
      )}
    </div>
  )
}
