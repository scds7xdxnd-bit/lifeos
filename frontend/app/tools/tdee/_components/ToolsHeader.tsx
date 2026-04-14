'use client'

// Minimal sticky header: "LifeOS Tools" brand mark linking to portfolio.
// Glassmorphism per DESIGN.md §5.

export default function ToolsHeader() {
  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 50,
        background: 'rgba(248, 250, 242, 0.75)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        height: '56px',
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          maxWidth: '960px',
          width: '100%',
          margin: '0 auto',
          padding: '0 20px',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <a
          href="https://taeyangcv.vercel.app/"
          target="_blank"
          rel="noopener noreferrer"
          style={{ textDecoration: 'none', display: 'flex', alignItems: 'baseline', gap: '6px' }}
        >
          <span
            style={{
              fontFamily: 'var(--font-serif), Newsreader, serif',
              fontStyle: 'italic',
              color: '#4b6646',
              letterSpacing: '-0.03em',
              fontSize: '1.125rem',
            }}
          >
            LifeOS
          </span>
          <span
            style={{
              fontFamily: 'var(--font-manrope), Manrope, sans-serif',
              fontWeight: 700,
              color: '#5a6157',
              fontSize: '0.875rem',
            }}
          >
            Tools
          </span>
        </a>
      </div>
    </header>
  )
}
