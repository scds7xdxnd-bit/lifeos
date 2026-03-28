'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { Pencil, Trash2 } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { foodLibraryApi } from '@/lib/api/foodLibrary'
import type { FoodItem } from '@/lib/api/foodLibrary'
import type { HealthPageTranslations } from '@/lib/translations/app'

interface Props {
  t: HealthPageTranslations
  foods: FoodItem[]
  isLoading: boolean
  onAddFood: () => void
  onEditFood: (id: number) => void
  selectedIds: Set<number>
  onToggle: (id: number) => void
  onSelectAll: () => void
  onDeselectAll: () => void
}

interface PendingDelete {
  id: number
  name: string
  timerId: ReturnType<typeof setTimeout>
}

const MICRO: React.CSSProperties = {
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.6875rem',
  fontWeight: 700,
  letterSpacing: '0.05em',
  textTransform: 'uppercase' as const,
  color: '#8b4a3a',
}

export function FoodLibraryManager({ t, foods, isLoading, onAddFood, onEditFood, selectedIds, onToggle, onSelectAll, onDeselectAll }: Props) {
  const allSelected = foods.length > 0 && selectedIds.size === foods.length
  const qc = useQueryClient()
  const [armedId, setArmedId] = useState<number | null>(null)
  const [pending, setPending] = useState<PendingDelete | null>(null)
  const [toastVisible, setToastVisible] = useState(false)
  // ref so timer callbacks always read the latest pending without stale closure
  const pendingRef = useRef<PendingDelete | null>(null)

  const deleteMutation = useMutation({
    mutationFn: (id: number) => foodLibraryApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['health', 'food-library'] }),
  })

  useEffect(() => {
    pendingRef.current = pending
  }, [pending])

  // Immediately commit a pending delete (used when a second delete supersedes it)
  const commitNow = useCallback(
    (p: PendingDelete) => {
      clearTimeout(p.timerId)
      deleteMutation.mutate(p.id)
    },
    [deleteMutation],
  )

  function handleTrashClick(id: number) {
    setArmedId((prev) => (prev === id ? null : id))
  }

  function handleDeleteConfirm(food: FoodItem) {
    // Commit any already-pending delete immediately before starting a new one
    if (pendingRef.current) {
      commitNow(pendingRef.current)
    }

    const timerId = setTimeout(() => {
      deleteMutation.mutate(food.id)
      setPending(null)
      setToastVisible(false)
    }, 4000)

    const next: PendingDelete = { id: food.id, name: food.name, timerId }
    pendingRef.current = next
    setPending(next)
    setArmedId(null)
    setToastVisible(true)
  }

  function handleUndo() {
    if (pendingRef.current) {
      clearTimeout(pendingRef.current.timerId)
    }
    setPending(null)
    setToastVisible(false)
  }

  // Disarm when clicking outside a food row
  useEffect(() => {
    if (!armedId) return
    function onDoc(e: MouseEvent) {
      if (!(e.target as HTMLElement).closest('[data-food-row]')) {
        setArmedId(null)
      }
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [armedId])

  // Clean up timer on unmount
  useEffect(() => {
    return () => {
      if (pendingRef.current) clearTimeout(pendingRef.current.timerId)
    }
  }, [])

  return (
    <>
      <div style={{ background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '20px 20px 16px' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <span style={MICRO}>{t.foodLibrary} {foods.length > 0 && `(${selectedIds.size}/${foods.length})`}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {foods.length > 0 && (
              <button
                type="button"
                onClick={allSelected ? onDeselectAll : onSelectAll}
                style={{ background: 'none', border: 'none', fontFamily: 'Manrope, sans-serif', fontSize: '0.75rem', fontWeight: 600, color: '#5a6157', cursor: 'pointer', padding: '2px 4px' }}
                onMouseEnter={(e) => (e.currentTarget.style.color = '#4b6646')}
                onMouseLeave={(e) => (e.currentTarget.style.color = '#5a6157')}
              >
                {allSelected ? t.deselectAll : t.selectAll}
              </button>
            )}
            <button
              type="button"
              onClick={onAddFood}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                padding: '6px 14px',
                borderRadius: 100,
                border: 'none',
                background: '#f1f5eb',
                fontFamily: 'Manrope, sans-serif',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#2e342b',
                cursor: 'pointer',
              }}
            >
              + {t.addFood}
            </button>
          </div>
        </div>

        {/* Food rows */}
        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {[1, 2, 3].map((i) => (
              <div key={i} style={{ height: 56, background: '#f0f2ec', borderRadius: '0 10px 10px 10px' }} />
            ))}
          </div>
        ) : foods.length === 0 ? (
          <p
            style={{
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.875rem',
              color: '#767d72',
              textAlign: 'center',
              padding: '20px 0',
            }}
          >
            {t.noFoodsYet}
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 320, overflowY: 'auto' }}>
            {foods
              .filter((food) => pending?.id !== food.id)
              .map((food, i) => {
                const isArmed = armedId === food.id
                return (
                  <div
                    key={food.id}
                    data-food-row="true"
                    onClick={() => onToggle(food.id)}
                    style={{
                      background: selectedIds.has(food.id) ? '#fdf0ed' : '#f8faf2',
                      borderRadius: '0 10px 10px 10px',
                      padding: '7px 12px',
                      animation: `fadeSlideIn 260ms ease-out ${i * 35}ms both`,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                      minHeight: 40,
                      cursor: 'pointer',
                      transition: 'background 0.12s',
                    }}
                  >
                      <input
                        type="checkbox"
                        checked={selectedIds.has(food.id)}
                        onChange={() => onToggle(food.id)}
                        onClick={e => e.stopPropagation()}
                        style={{ accentColor: '#4b6646', width: 15, height: 15, flexShrink: 0, cursor: 'pointer' }}
                      />
                      <span
                        style={{
                          fontFamily: 'Manrope, sans-serif',
                          fontSize: '0.8125rem',
                          fontWeight: selectedIds.has(food.id) ? 600 : 500,
                          color: '#2e342b',
                          flex: '1 1 0',
                          minWidth: 0,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {food.name}
                      </span>

                      <div style={{ display: 'flex', alignItems: 'center', gap: 0, flexShrink: 0, fontFamily: 'Manrope, sans-serif', fontSize: '0.7rem', color: '#5a6157', whiteSpace: 'nowrap' }}>
                        <span>{Math.round(Number(food.calories_per_100g))} {t.colKcal}</span>
                        <span style={{ margin: '0 5px', color: '#c8cec4' }}>·</span>
                        <span style={{ fontWeight: 600, color: '#4b6646' }}>${Number(food.cost_per_100g).toFixed(2)}</span>
                      </div>

                      {/* Action buttons */}
                      <div style={{ display: 'flex', gap: 2, flexShrink: 0, alignItems: 'center' }} onClick={e => e.stopPropagation()}>
                        <button
                          type="button"
                          onClick={() => onEditFood(food.id)}
                          aria-label={`Edit ${food.name}`}
                          style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: '#5a6157',
                            padding: '4px 6px',
                            borderRadius: 100,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                          onMouseEnter={(e) => (e.currentTarget.style.color = '#4b6646')}
                          onMouseLeave={(e) => (e.currentTarget.style.color = '#5a6157')}
                        >
                          <Pencil size={13} />
                        </button>

                        {isArmed ? (
                          <button
                            type="button"
                            onClick={() => handleDeleteConfirm(food)}
                            aria-label={`Confirm delete ${food.name}`}
                            style={{
                              padding: '4px 12px',
                              borderRadius: 100,
                              border: 'none',
                              background: '#8b4a3a',
                              fontFamily: 'Manrope, sans-serif',
                              fontSize: '0.75rem',
                              fontWeight: 700,
                              color: '#fff',
                              cursor: 'pointer',
                              whiteSpace: 'nowrap',
                              animation: 'armIn 140ms cubic-bezier(0.34,1.56,0.64,1) both',
                            }}
                          >
                            Delete
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => handleTrashClick(food.id)}
                            aria-label={`Delete ${food.name}`}
                            style={{
                              background: 'none',
                              border: 'none',
                              cursor: 'pointer',
                              color: '#adb4a8',
                              padding: '4px 6px',
                              borderRadius: 100,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                            onMouseEnter={(e) => (e.currentTarget.style.color = '#e8735c')}
                            onMouseLeave={(e) => (e.currentTarget.style.color = '#adb4a8')}
                          >
                            <Trash2 size={13} />
                          </button>
                        )}
                      </div>
                  </div>
                )
              })}
          </div>
        )}
      </div>

      {/* Delete toast — single, non-stacking */}
      {toastVisible && pending && (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: 'fixed',
            bottom: 28,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 100,
            background: '#2e342b',
            borderRadius: '0 12px 12px 12px',
            padding: '12px 8px 12px 18px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            boxShadow: '0 8px 32px rgba(46,52,43,0.22)',
            animation: 'toastIn 220ms cubic-bezier(0.34,1.56,0.64,1) both',
            minWidth: 260,
            maxWidth: 'calc(100vw - 48px)',
            overflow: 'hidden',
          }}
        >
          <span
            style={{
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.875rem',
              color: '#e8f0e4',
              flex: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            <span style={{ color: '#8fa888', marginRight: 5 }}>Deleted</span>
            {pending.name}
          </span>

          <button
            type="button"
            onClick={handleUndo}
            style={{
              padding: '6px 16px',
              borderRadius: 100,
              border: '1.5px solid rgba(255,255,255,0.18)',
              background: 'transparent',
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.8rem',
              fontWeight: 700,
              color: '#fdf0ed',
              cursor: 'pointer',
              minHeight: 36,
              flexShrink: 0,
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.08)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
          >
            Undo
          </button>

          {/* Progress bar */}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: 3,
              background: 'rgba(255,255,255,0.08)',
            }}
          >
            <div
              style={{
                height: '100%',
                background: '#8b4a3a',
                transformOrigin: 'left',
                animation: 'toastProgress 4000ms linear forwards',
              }}
            />
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(-6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes armIn {
          from { opacity: 0; transform: scale(0.82); }
          to   { opacity: 1; transform: scale(1); }
        }
        @keyframes toastIn {
          from { opacity: 0; transform: translateX(-50%) translateY(10px) scale(0.96); }
          to   { opacity: 1; transform: translateX(-50%) translateY(0)    scale(1); }
        }
        @keyframes toastProgress {
          from { transform: scaleX(1); }
          to   { transform: scaleX(0); }
        }
      `}</style>
    </>
  )
}
