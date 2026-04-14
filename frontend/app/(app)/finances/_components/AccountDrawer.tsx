'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { X, ChevronDown } from 'lucide-react'
import { financesApi, Account, UpdateAccountInput } from '@/lib/api/finances'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type AccountType = 'asset' | 'liability' | 'equity' | 'income' | 'expense'

interface AccountDrawerProps {
  /** When set, the drawer opens in edit mode for this account. */
  account?: Account | null
  /** Called after a successful create or update. */
  onSuccess?: (account: Account) => void
  /** Called when the drawer should close. */
  onClose: () => void
}

const ACCOUNT_TYPES: AccountType[] = ['asset', 'liability', 'equity', 'income', 'expense']

const TYPE_LABELS: Record<AccountType, string> = {
  asset: 'Asset',
  liability: 'Liability',
  equity: 'Equity',
  income: 'Income',
  expense: 'Expense',
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function FieldLabel({ children }: { children: React.ReactNode }) {
  return (
    <label
      style={{
        fontFamily: 'var(--font-manrope), sans-serif',
        fontSize: '0.6875rem',
        fontWeight: 700,
        textTransform: 'uppercase' as const,
        letterSpacing: '0.06em',
        color: '#5a6157',
        display: 'block',
        marginBottom: '0.375rem',
      }}
    >
      {children}
    </label>
  )
}

function Input({
  value,
  onChange,
  placeholder,
  disabled,
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  disabled?: boolean
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      disabled={disabled}
      style={{
        width: '100%',
        padding: '0.625rem 0.875rem',
        borderRadius: '0.5rem',
        border: 'none',
        background: '#f4f7f0',
        fontFamily: 'var(--font-manrope), sans-serif',
        fontSize: '0.9375rem',
        color: '#2e342b',
        outline: 'none',
        opacity: disabled ? 0.5 : 1,
      }}
    />
  )
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function AccountDrawer({ account, onSuccess, onClose }: AccountDrawerProps) {
  const isEdit = !!account
  const qc = useQueryClient()

  const [name, setName] = useState(account?.name ?? '')
  const [accountType, setAccountType] = useState<AccountType>(
    (account?.account_type as AccountType) ?? 'expense'
  )
  const [subtype, setSubtype] = useState(account?.account_subtype ?? '')
  const [description, setDescription] = useState(account?.description ?? '')
  const [categoryNameNew, setCategoryNameNew] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Reset form when account prop changes
  useEffect(() => {
    setName(account?.name ?? '')
    setAccountType((account?.account_type as AccountType) ?? 'expense')
    setSubtype(account?.account_subtype ?? '')
    setDescription(account?.description ?? '')
    setError(null)
  }, [account])

  // Fetch subtypes for selected account type
  const { data: subtypesData } = useQuery({
    queryKey: ['finance', 'subtypes', accountType],
    queryFn: () => financesApi.getAccountSubtypes(accountType),
    staleTime: 60 * 60 * 1000,
    retry: 1,
  })
  const subtypes = subtypesData?.subtypes ?? []

  const createMutation = useMutation({
    mutationFn: () =>
      financesApi.createAccount({
        name,
        account_type: accountType,
        account_subtype: subtype || null,
        description: description || null,
        category_name_new: categoryNameNew || null,
      }),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['finance', 'accounts'] })
      onSuccess?.(res.account)
      onClose()
    },
    onError: (err: Error) => {
      setError(err.message ?? 'Something went wrong')
    },
  })

  const updateMutation = useMutation({
    mutationFn: () => {
      const payload: UpdateAccountInput = {}
      if (name !== account?.name) payload.name = name
      if (description !== (account?.description ?? '')) payload.description = description || null
      if (subtype !== (account?.account_subtype ?? '')) payload.account_subtype = subtype || null
      if (categoryNameNew) payload.category_name_new = categoryNameNew
      return financesApi.updateAccount(account!.id, payload)
    },
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['finance', 'accounts'] })
      onSuccess?.(res.account)
      onClose()
    },
    onError: (err: Error) => {
      setError(err.message ?? 'Something went wrong')
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: () => financesApi.deactivateAccount(account!.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['finance', 'accounts'] })
      onClose()
    },
    onError: (err: Error) => {
      setError(err.message ?? 'Something went wrong')
    },
  })

  const isPending =
    createMutation.isPending || updateMutation.isPending || deactivateMutation.isPending

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!name.trim()) {
      setError('Account name is required')
      return
    }
    if (isEdit) {
      updateMutation.mutate()
    } else {
      createMutation.mutate()
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(46,52,43,0.35)',
          zIndex: 40,
        }}
      />

      {/* Drawer panel */}
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
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '1.25rem 1.5rem',
            borderBottom: '1px solid rgba(173,180,168,0.2)',
          }}
        >
          <h2
            style={{
              fontFamily: 'var(--font-newsreader), serif',
              fontSize: '1.25rem',
              fontWeight: 600,
              color: '#2e342b',
              letterSpacing: '-0.02em',
            }}
          >
            {isEdit ? 'Edit Account' : 'New Account'}
          </h2>
          <button
            onClick={onClose}
            style={{
              width: '2rem',
              height: '2rem',
              borderRadius: '9999px',
              border: 'none',
              background: '#e8f0e3',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              color: '#3a5c35',
            }}
          >
            <X size={14} />
          </button>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Name */}
            <div>
              <FieldLabel>Account Name *</FieldLabel>
              <Input
                value={name}
                onChange={setName}
                placeholder="e.g. Savings Account"
              />
            </div>

            {/* Account type (disabled in edit mode) */}
            <div>
              <FieldLabel>Type</FieldLabel>
              <div style={{ position: 'relative' }}>
                <select
                  value={accountType}
                  onChange={(e) => {
                    setAccountType(e.target.value as AccountType)
                    setSubtype('')
                  }}
                  disabled={isEdit}
                  style={{
                    width: '100%',
                    padding: '0.625rem 2.25rem 0.625rem 0.875rem',
                    borderRadius: '0.5rem',
                    border: 'none',
                    background: '#f4f7f0',
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.9375rem',
                    color: '#2e342b',
                    appearance: 'none',
                    cursor: isEdit ? 'not-allowed' : 'pointer',
                    opacity: isEdit ? 0.5 : 1,
                  }}
                >
                  {ACCOUNT_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {TYPE_LABELS[t]}
                    </option>
                  ))}
                </select>
                <ChevronDown
                  size={14}
                  style={{
                    position: 'absolute',
                    right: '0.875rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: '#767d72',
                    pointerEvents: 'none',
                  }}
                />
              </div>
            </div>

            {/* Subtype */}
            {subtypes.length > 0 && (
              <div>
                <FieldLabel>Subtype</FieldLabel>
                <div style={{ position: 'relative' }}>
                  <select
                    value={subtype}
                    onChange={(e) => setSubtype(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.625rem 2.25rem 0.625rem 0.875rem',
                      borderRadius: '0.5rem',
                      border: 'none',
                      background: '#f4f7f0',
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.9375rem',
                      color: '#2e342b',
                      appearance: 'none',
                      cursor: 'pointer',
                    }}
                  >
                    <option value="">No subtype</option>
                    {subtypes.map((s) => (
                      <option key={s} value={s}>
                        {s.replace(/_/g, ' ')}
                      </option>
                    ))}
                  </select>
                  <ChevronDown
                    size={14}
                    style={{
                      position: 'absolute',
                      right: '0.875rem',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      color: '#767d72',
                      pointerEvents: 'none',
                    }}
                  />
                </div>
              </div>
            )}

            {/* Category */}
            <div>
              <FieldLabel>New Category Name</FieldLabel>
              <Input
                value={categoryNameNew}
                onChange={setCategoryNameNew}
                placeholder="Leave blank to use default"
              />
            </div>

            {/* Description */}
            <div>
              <FieldLabel>Description</FieldLabel>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional notes"
                rows={3}
                style={{
                  width: '100%',
                  padding: '0.625rem 0.875rem',
                  borderRadius: '0.5rem',
                  border: 'none',
                  background: '#f4f7f0',
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.9375rem',
                  color: '#2e342b',
                  outline: 'none',
                  resize: 'vertical',
                }}
              />
            </div>

            {/* Error */}
            {error && (
              <p
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.875rem',
                  color: '#c0392b',
                  background: 'rgba(192,57,43,0.08)',
                  borderRadius: '0.5rem',
                  padding: '0.625rem 0.875rem',
                }}
              >
                {error}
              </p>
            )}
          </div>
        </form>

        {/* Footer actions */}
        <div
          style={{
            padding: '1.25rem 1.5rem',
            borderTop: '1px solid rgba(173,180,168,0.2)',
            display: 'flex',
            gap: '0.75rem',
            alignItems: 'center',
          }}
        >
          {/* Deactivate (edit only) */}
          {isEdit && account?.is_active && (
            <button
              type="button"
              onClick={() => deactivateMutation.mutate()}
              disabled={isPending}
              style={{
                padding: '0.5625rem 1rem',
                borderRadius: '9999px',
                border: '1px solid rgba(192,57,43,0.3)',
                background: 'transparent',
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#c0392b',
                cursor: 'pointer',
                opacity: isPending ? 0.5 : 1,
              }}
            >
              Deactivate
            </button>
          )}

          <div style={{ flex: 1 }} />

          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '0.5625rem 1.25rem',
              borderRadius: '9999px',
              border: 'none',
              background: '#e8f0e3',
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#3a5c35',
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>

          <button
            type="submit"
            form=""
            onClick={handleSubmit}
            disabled={isPending}
            style={{
              padding: '0.5625rem 1.5rem',
              borderRadius: '9999px',
              border: 'none',
              background: '#3a5c35',
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#fff',
              cursor: 'pointer',
              opacity: isPending ? 0.6 : 1,
            }}
          >
            {isPending ? 'Saving…' : isEdit ? 'Save Changes' : 'Create Account'}
          </button>
        </div>
      </div>
    </>
  )
}
