'use client'

import { useEffect, useState } from 'react'
import { FernFrond } from '@/components/landing/assets/Botanicals'

const testimonials = [
  { quote: 'LifeOS was the first time I could actually see my life as a system \u2014 and see where it was breaking.', name: 'Maya R.', role: 'Product designer' },
  { quote: 'LifeOS showed me the gap between the life I said I wanted and how I was actually spending my time.', name: 'James T.', role: 'Builder' },
  { quote: 'It changed how I think about my days. I stopped reacting and started running my life deliberately.', name: 'Priya N.', role: 'Creative director' },
]

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const [quoteIdx, setQuoteIdx] = useState(0)
  const [fade, setFade] = useState(true)

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout> | null = null
    const timer = setInterval(() => {
      setFade(false)
      timeoutId = setTimeout(() => {
        setQuoteIdx((i) => (i + 1) % testimonials.length)
        setFade(true)
      }, 400)
    }, 6000)
    return () => {
      clearInterval(timer)
      if (timeoutId !== null) clearTimeout(timeoutId)
    }
  }, [])

  const t = testimonials[quoteIdx]

  return (
    <main style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Left panel — dark editorial brand showcase */}
      <div
        style={{
          flex: '0 0 45%',
          background: 'linear-gradient(170deg, #1a1f1a 0%, #2a3228 50%, #1a1f1a 100%)',
          padding: '64px 56px',
          position: 'relative',
          overflow: 'hidden',
        }}
        className="hidden lg:flex lg:flex-col lg:justify-center"
      >
        {/* Botanical accent */}
        <div
          style={{
            position: 'absolute',
            top: '-5%',
            right: '-10%',
            width: '80%',
            height: '90%',
            opacity: 0.04,
            pointerEvents: 'none',
          }}
        >
          <FernFrond color="#a8c4a0" />
        </div>

        {/* Brand */}
        <div style={{ position: 'relative', zIndex: 1 }}>
          <h1
            style={{
              fontFamily: "var(--font-serif), 'Newsreader', Georgia, serif",
              fontSize: '2.8rem',
              fontWeight: 300,
              letterSpacing: '-0.03em',
              color: '#a8c4a0',
              marginBottom: '16px',
            }}
          >
            LifeOS
          </h1>
          <p
            style={{
              fontFamily: "var(--font-serif), 'Newsreader', Georgia, serif",
              fontSize: '1.8rem',
              fontWeight: 300,
              fontStyle: 'italic',
              lineHeight: 1.3,
              color: '#e8ebe4',
              letterSpacing: '-0.02em',
              maxWidth: '380px',
              marginBottom: '48px',
            }}
          >
            Your life,<br />beautifully organized.
          </p>

          {/* Divider line */}
          <div
            style={{
              width: '48px',
              height: '2px',
              background: '#a8c4a0',
              opacity: 0.3,
              marginBottom: '40px',
            }}
          />

          {/* Rotating testimonial */}
          <div
            style={{
              transition: 'opacity 0.4s ease',
              opacity: fade ? 1 : 0,
              minHeight: '120px',
            }}
          >
            <p
              style={{
                fontFamily: "var(--font-serif), 'Newsreader', Georgia, serif",
                fontSize: '1.05rem',
                fontStyle: 'italic',
                lineHeight: 1.65,
                color: 'rgba(232, 235, 228, 0.7)',
                maxWidth: '340px',
                marginBottom: '20px',
              }}
            >
              &ldquo;{t.quote}&rdquo;
            </p>
            <p
              style={{
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#a8c4a0',
                letterSpacing: '0.03em',
              }}
            >
              {t.name}
              <span style={{ fontWeight: 400, color: 'rgba(168, 196, 160, 0.5)', marginLeft: '8px' }}>
                {t.role}
              </span>
            </p>
          </div>

          {/* Bottom badge */}
          <div
            style={{
              marginTop: '64px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              borderRadius: '100px',
              background: 'rgba(168, 196, 160, 0.08)',
              border: '1px solid rgba(168, 196, 160, 0.12)',
            }}
          >
            <div
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: '#a8c4a0',
              }}
            />
            <span
              style={{
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.7rem',
                fontWeight: 700,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                color: 'rgba(168, 196, 160, 0.6)',
              }}
            >
              Private Alpha
            </span>
          </div>
        </div>
      </div>

      {/* Right panel — form area */}
      <div
        className="flex items-center justify-center"
        style={{
          flex: 1,
          padding: '40px 20px',
          background: 'linear-gradient(180deg, #f8faf2 0%, #f1f5eb 60%, #e5eade 100%)',
          position: 'relative',
          overflow: 'hidden',
          minHeight: '100vh',
        }}
      >
        {children}
      </div>
    </main>
  )
}
