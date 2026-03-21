'use client'

import { useState } from 'react'
import { Globe, ChevronDown } from 'lucide-react'
import type { Lang } from '@/components/landing/translations'

interface LanguageMenuProps {
  lang: Lang
  setLang: (lang: Lang) => void
  iconOnly?: boolean
}

const OPTIONS: Array<{ value: Lang; label: string }> = [
  { value: 'en', label: 'English' },
  { value: 'zh', label: '中文' },
  { value: 'ko', label: '한국어' },
]

export function LanguageMenu({ lang, setLang, iconOnly = false }: LanguageMenuProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Language options"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: iconOnly ? '0' : '6px',
          height: '36px',
          padding: iconOnly ? '0 10px' : '0 12px',
          borderRadius: '100px',
          border: '1px solid rgba(173, 180, 168, 0.20)',
          background: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          color: '#5a6157',
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.75rem',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          cursor: 'pointer',
        }}
      >
        <Globe size={14} />
        {!iconOnly && <span>{lang}</span>}
        {!iconOnly && <ChevronDown size={13} />}
      </button>

      {open && (
        <div
          style={{
            position: 'absolute',
            top: '42px',
            right: 0,
            zIndex: 60,
            minWidth: '160px',
            padding: '8px',
            borderRadius: '0 12px 12px 12px',
            background: '#ffffff',
            boxShadow: '0 8px 24px rgba(46, 52, 43, 0.12)',
          }}
        >
          {OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => {
                setLang(option.value)
                setOpen(false)
              }}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '8px 10px',
                borderRadius: '100px',
                border: 'none',
                background: lang === option.value ? '#e5eade' : 'transparent',
                color: lang === option.value ? '#2e342b' : '#5a6157',
                fontFamily: 'var(--font-manrope), sans-serif',
                fontSize: '0.8125rem',
                fontWeight: lang === option.value ? 700 : 500,
                cursor: 'pointer',
                textAlign: 'left',
              }}
            >
              <span>{option.label}</span>
              {lang === option.value && (
                <span style={{ fontSize: '0.625rem', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                  Active
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
