'use client'

import { useEffect, useState } from 'react'
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
  const [isMobile, setIsMobile] = useState(false)
  const menuId = 'language-options-menu'

  useEffect(() => {
    const media = window.matchMedia('(max-width: 768px)')
    const apply = () => setIsMobile(media.matches)
    apply()
    media.addEventListener('change', apply)
    return () => media.removeEventListener('change', apply)
  }, [])

  const useMobileSheet = iconOnly && isMobile

  const triggerStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: iconOnly ? '6px' : '6px',
    height: iconOnly ? '44px' : '36px',
    minHeight: iconOnly ? '44px' : undefined,
    padding: iconOnly ? '0 12px' : '0 12px',
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
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={iconOnly ? `Language options, current ${lang}` : 'Language options'}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-controls={open ? menuId : undefined}
        style={triggerStyle}
      >
        <Globe size={14} />
        <span>{lang}</span>
        {!useMobileSheet && <ChevronDown size={13} />}
      </button>

      {open && !useMobileSheet && (
        <div
          id={menuId}
          role="menu"
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
              role="menuitemradio"
              aria-checked={lang === option.value}
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
              {lang === option.value && <span aria-hidden="true">✓</span>}
            </button>
          ))}
        </div>
      )}

      {open && useMobileSheet && (
        <>
          <button
            type="button"
            aria-label="Close language options"
            onClick={() => setOpen(false)}
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 80,
              border: 'none',
              background: 'rgba(46, 52, 43, 0.28)',
              backdropFilter: 'blur(3px)',
              WebkitBackdropFilter: 'blur(3px)',
              cursor: 'pointer',
            }}
          />
          <div
            id={menuId}
            role="menu"
            aria-label="Language options"
            style={{
              position: 'fixed',
              left: '16px',
              right: '16px',
              bottom: '16px',
              zIndex: 81,
              padding: '14px',
              borderRadius: '0 16px 16px 16px',
              background: '#ffffff',
              boxShadow: '0 16px 36px rgba(46, 52, 43, 0.2)',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}
          >
            {OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                role="menuitemradio"
                aria-checked={lang === option.value}
                onClick={() => {
                  setLang(option.value)
                  setOpen(false)
                }}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  minHeight: '44px',
                  padding: '10px 12px',
                  borderRadius: '100px',
                  border: 'none',
                  background: lang === option.value ? '#e5eade' : '#f8faf2',
                  color: lang === option.value ? '#2e342b' : '#5a6157',
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.875rem',
                  fontWeight: lang === option.value ? 700 : 600,
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <span>{option.label}</span>
                {lang === option.value && <span aria-hidden="true">✓</span>}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
