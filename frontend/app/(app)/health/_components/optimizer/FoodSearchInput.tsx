'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { Loader2 } from 'lucide-react'
import { searchFoodDatabase, type FoodSearchResult } from '@/lib/api/foodSearch'

interface Props {
  value: string
  onChange: (name: string) => void
  onSelect: (result: FoodSearchResult) => void
  disabled?: boolean
  placeholder?: string
  lang?: string
}

const INPUT_STYLE: React.CSSProperties = {
  width: '100%',
  padding: '9px 36px 9px 12px',
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.875rem',
  color: '#2e342b',
  background: '#f7f8f5',
  border: '1.5px solid rgba(173,180,168,0.4)',
  borderRadius: 4,
  outline: 'none',
  boxSizing: 'border-box' as const,
}

export function FoodSearchInput({ value, onChange, onSelect, disabled, placeholder, lang }: Props) {
  const [results, setResults] = useState<FoodSearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const [noResults, setNoResults] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const runSearch = useCallback(async (q: string) => {
    if (q.length < 3) {
      setResults([])
      setOpen(false)
      setNoResults(false)
      setLoading(false)
      return
    }
    setLoading(true)
    setNoResults(false)
    const found = await searchFoodDatabase(q, lang ?? 'en')
    setLoading(false)
    setResults(found)
    setNoResults(found.length === 0)
    setOpen(true)
    setActiveIndex(-1)
  }, [lang])

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => runSearch(value), 300)
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current) }
  }, [value, runSearch])

  // Close on outside click
  useEffect(() => {
    function onOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onOutside)
    return () => document.removeEventListener('mousedown', onOutside)
  }, [])

  function handleSelect(result: FoodSearchResult) {
    onSelect(result)
    setOpen(false)
    setResults([])
    setNoResults(false)
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (!open) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveIndex((i) => Math.min(i + 1, results.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveIndex((i) => Math.max(i - 1, -1))
    } else if (e.key === 'Enter' && activeIndex >= 0 && results[activeIndex]) {
      e.preventDefault()
      handleSelect(results[activeIndex])
    } else if (e.key === 'Escape') {
      setOpen(false)
    }
  }

  const showDropdown = open && (results.length > 0 || noResults)

  return (
    <div ref={containerRef} style={{ position: 'relative' }}>
      <div style={{ position: 'relative' }}>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => { if (results.length > 0 || noResults) setOpen(true) }}
          disabled={disabled}
          placeholder={placeholder ?? 'Search for a food…'}
          style={INPUT_STYLE}
          role="combobox"
          aria-expanded={showDropdown}
          aria-label="Search for food"
          aria-autocomplete="list"
          autoComplete="off"
        />
        {loading && (
          <div
            style={{
              position: 'absolute',
              right: 10,
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#8b4a3a',
              display: 'flex',
            }}
          >
            <Loader2 size={15} style={{ animation: 'spin 0.8s linear infinite' }} />
          </div>
        )}
      </div>

      {showDropdown && (
        <div
          role="listbox"
          style={{
            position: 'absolute',
            top: 'calc(100% + 4px)',
            left: 0,
            right: 0,
            zIndex: 80,
            background: '#ffffff',
            borderRadius: '0 12px 12px 12px',
            boxShadow: '0 8px 24px rgba(46,52,43,0.08)',
            maxHeight: 320,
            overflowY: 'auto',
          }}
        >
          {noResults ? (
            <div
              style={{
                padding: '12px 16px',
                fontFamily: 'Manrope, sans-serif',
                fontSize: '0.8rem',
                color: '#767d72',
                fontStyle: 'italic',
              }}
            >
              No matches found — enter values manually.
            </div>
          ) : (
            results.map((r, i) => (
              <div
                key={`${r.product_name}-${i}`}
                role="option"
                aria-selected={i === activeIndex}
                onMouseDown={() => handleSelect(r)}
                onMouseEnter={() => setActiveIndex(i)}
                style={{
                  padding: '10px 16px',
                  minHeight: 44,
                  cursor: 'pointer',
                  background: i === activeIndex ? '#f8faf2' : 'transparent',
                  borderBottom: i < results.length - 1 ? '1px solid #f0f2ec' : 'none',
                }}
              >
                <div
                  style={{
                    fontFamily: 'Manrope, sans-serif',
                    fontSize: '0.8125rem',
                    fontWeight: 500,
                    color: '#2e342b',
                    marginBottom: 2,
                  }}
                >
                  {r.product_name}
                  {r.brands && (
                    <span style={{ fontWeight: 400, color: '#767d72' }}> — {r.brands}</span>
                  )}
                </div>
                <div
                  style={{
                    fontFamily: 'Manrope, sans-serif',
                    fontSize: '0.6875rem',
                    color: '#5a6157',
                  }}
                >
                  {Math.round(r.calories_per_100g)} cal · {r.protein_per_100g.toFixed(1)}g P ·{' '}
                  {r.carbohydrate_per_100g.toFixed(1)}g C · {r.fat_per_100g.toFixed(1)}g F
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
