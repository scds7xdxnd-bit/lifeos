'use client'

import { useState, useRef, useEffect } from 'react'

interface InfoTooltipProps {
  content: React.ReactNode
  /** Where the popover appears relative to the icon. Default: 'top' */
  placement?: 'top' | 'bottom'
  maxWidth?: number
}

export default function InfoTooltip({ content, placement = 'top', maxWidth = 260 }: InfoTooltipProps) {
  const [visible, setVisible] = useState(false)
  const ref = useRef<HTMLSpanElement>(null)

  // Close on outside click / Escape
  useEffect(() => {
    if (!visible) return
    function onKey(e: KeyboardEvent) { if (e.key === 'Escape') setVisible(false) }
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setVisible(false)
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('mousedown', onClickOutside)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.removeEventListener('mousedown', onClickOutside)
    }
  }, [visible])

  const popoverOffset = placement === 'top' ? { bottom: 'calc(100% + 8px)', top: 'auto' } : { top: 'calc(100% + 8px)', bottom: 'auto' }

  return (
    <span
      ref={ref}
      style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', verticalAlign: 'middle' }}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {/* Icon */}
      <button
        type="button"
        aria-label="More information"
        aria-expanded={visible}
        tabIndex={0}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '16px',
          height: '16px',
          borderRadius: '100px',
          borderWidth: '1.5px',
          borderStyle: 'solid',
          borderColor: visible ? '#4b6646' : '#adb4a8',
          background: 'transparent',
          cursor: 'help',
          fontFamily: 'Manrope, sans-serif',
          fontSize: '0.6rem',
          fontWeight: 700,
          color: visible ? '#4b6646' : '#767d72',
          lineHeight: 1,
          padding: 0,
          flexShrink: 0,
          marginLeft: '5px',
          transition: 'border-color 0.15s, color 0.15s',
        }}
        onClick={() => setVisible(v => !v)}
      >
        ?
      </button>

      {/* Popover */}
      {visible && (
        <span
          role="tooltip"
          style={{
            position: 'absolute',
            ...popoverOffset,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 200,
            width: `${maxWidth}px`,
            background: '#ffffff',
            borderRadius: '0 12px 12px 12px',
            boxShadow: '0 4px 20px rgba(46,52,43,0.12)',
            padding: '12px 14px',
            pointerEvents: 'none',
          }}
        >
          {/* Caret */}
          <span
            style={{
              position: 'absolute',
              ...(placement === 'top'
                ? { bottom: '-5px', top: 'auto', borderTop: '5px solid #ffffff', borderBottom: 'none' }
                : { top: '-5px', bottom: 'auto', borderBottom: '5px solid #ffffff', borderTop: 'none' }),
              left: '50%',
              transform: 'translateX(-50%)',
              width: 0,
              height: 0,
              borderLeft: '5px solid transparent',
              borderRight: '5px solid transparent',
            }}
          />
          <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.75rem', color: '#5a6157', lineHeight: 1.55, display: 'block' }}>
            {content}
          </span>
        </span>
      )}
    </span>
  )
}
