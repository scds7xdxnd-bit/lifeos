'use client'

export function AppFooter() {
  return (
    <footer
      className="mt-16 py-6 sm:py-8 px-4 sm:px-6"
      style={{
        background: '#1a1f1a',
      }}
    >
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-4 sm:gap-6">
          {/* Brand */}
          <span
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontStyle: 'italic',
              fontSize: '1rem',
              color: '#6b8f65',
              letterSpacing: '-0.03em',
            }}
          >
            LifeOS
          </span>
          <span
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.6875rem',
              color: '#5a6857',
            }}
          >
            Your life, clearly.
          </span>
        </div>

        <span
          className="hidden sm:inline"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.6875rem',
            color: '#5a6857',
          }}
        >
          Deterministic intelligence · No ML autonomy
        </span>
      </div>
    </footer>
  )
}
