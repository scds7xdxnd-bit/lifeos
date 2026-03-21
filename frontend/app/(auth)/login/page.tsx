'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth/context'
import { LeafCluster } from '@/components/landing/assets/Botanicals'

type View = 'login' | 'register'

export default function LoginPage() {
  const router = useRouter()
  const { login, register } = useAuth()

  const [view, setView] = useState<View>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [inviteToken, setInviteToken] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      if (view === 'login') {
        await login(email, password)
      } else {
        await register({ email, password, invite_token: inviteToken || undefined })
      }
      router.push('/calendar')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div style={{ width: '100%', maxWidth: '420px', position: 'relative', padding: '0 4px' }}>
      <style>{`
        .auth-back-link { color: #5a6157; text-decoration: none; transition: color 0.2s; }
        .auth-back-link:hover, .auth-back-link:focus-visible { color: #4b6646; }
        .auth-submit { transition: all 0.25s ease; }
        .auth-submit:hover:not(:disabled), .auth-submit:focus-visible:not(:disabled) {
          background: linear-gradient(135deg, #3f5a3a, #365234) !important;
          box-shadow: 0 10px 34px rgba(46, 52, 43, 0.24) !important;
          transform: translateY(-1px);
        }
        .auth-submit:focus-visible { outline: 2px solid #4b6646; outline-offset: 2px; }
        .auth-input {
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.875rem;
          color: #2e342b;
          background: #ffffff;
          border: 1px solid rgba(173, 180, 168, 0.20);
          border-radius: 4px;
          padding: 12px 14px;
          outline: none;
          width: 100%;
          transition: border-color 0.2s;
        }
        .auth-input::placeholder { color: #adb4a8; }
        .auth-input:focus { border-color: #4b6646; box-shadow: 0 0 0 2px rgba(75, 102, 70, 0.12); }
        @media (max-width: 480px) {
          .auth-card-inner { padding: 32px 24px 28px !important; }
        }
      `}</style>

      {/* Back to home */}
      <Link
        href="/"
        className="auth-back-link"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
          fontSize: '0.78rem',
          fontWeight: 500,
          marginBottom: '32px',
        }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable={false}>
          <path d="M19 12H5" /><path d="M12 19l-7-7 7-7" />
        </svg>
        Back to home
      </Link>

      {/* Card */}
      <div
        className="auth-card-inner"
        style={{
          background: 'rgba(255, 255, 255, 0.82)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.4)',
          borderRadius: '0 24px 24px 24px',
          padding: '44px 36px 40px',
          boxShadow: '0 20px 50px rgba(46, 52, 43, 0.06)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Botanical corner accent */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            bottom: '-20px',
            right: '-20px',
            width: '160px',
            height: '160px',
            opacity: 0.06,
            pointerEvents: 'none',
          }}
        >
          <LeafCluster color="#4b6646" />
        </div>

        {/* Mobile brand (hidden on desktop where left panel shows it) */}
        <div className="lg:hidden" style={{ textAlign: 'center', marginBottom: '28px' }}>
          <h1
            style={{
              fontFamily: "var(--font-serif), 'Newsreader', Georgia, serif",
              fontSize: '2.2rem',
              fontWeight: 300,
              letterSpacing: '-0.03em',
              color: '#2e342b',
              marginBottom: '4px',
            }}
          >
            LifeOS
          </h1>
        </div>

        {/* Heading */}
        <div style={{ marginBottom: '28px' }}>
          <h2
            style={{
              fontFamily: "var(--font-serif), 'Newsreader', Georgia, serif",
              fontSize: '1.5rem',
              fontWeight: 400,
              letterSpacing: '-0.02em',
              color: '#2e342b',
              marginBottom: '8px',
            }}
          >
            {view === 'login' ? 'Welcome back' : 'Join the alpha'}
          </h2>
          <p
            style={{
              fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
              fontSize: '0.85rem',
              color: '#5a6157',
              lineHeight: 1.5,
            }}
          >
            {view === 'login'
              ? 'Sign in to your archive.'
              : 'Private alpha \u2014 invite token required.'}
          </p>
        </div>

        {/* Register mode badge */}
        {view === 'register' && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              borderRadius: '100px',
              background: 'rgba(75, 102, 70, 0.08)',
              marginBottom: '20px',
            }}
          >
            <div
              style={{
                width: '5px',
                height: '5px',
                borderRadius: '50%',
                background: '#4b6646',
              }}
            />
            <span
              style={{
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.65rem',
                fontWeight: 700,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                color: '#4b6646',
              }}
            >
              Limited spots
            </span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label
              htmlFor="email"
              style={{
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.6875rem',
                fontWeight: 700,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
                color: '#767d72',
              }}
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="auth-input"
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label
              htmlFor="password"
              style={{
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.6875rem',
                fontWeight: 700,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
                color: '#767d72',
              }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete={view === 'login' ? 'current-password' : 'new-password'}
              required
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="auth-input"
            />
          </div>

          {view === 'register' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label
                htmlFor="invite_token"
                style={{
                  fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                  fontSize: '0.6875rem',
                  fontWeight: 700,
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  color: '#767d72',
                }}
              >
                Invite token
              </label>
              <input
                id="invite_token"
                type="text"
                placeholder="Paste your invite token"
                value={inviteToken}
                onChange={(e) => setInviteToken(e.target.value)}
                className="auth-input"
                style={{ borderColor: 'rgba(232, 115, 92, 0.25)' }}
              />
            </div>
          )}

          {error && (
            <p
              style={{
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.82rem',
                color: '#e8735c',
                textAlign: 'center',
                margin: 0,
              }}
            >
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="auth-submit"
            style={{
              width: '100%',
              padding: '14px 24px',
              borderRadius: '100px',
              border: 'none',
              background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
              color: '#ffffff',
              fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
              fontSize: '0.875rem',
              fontWeight: 700,
              letterSpacing: '0.01em',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              opacity: isSubmitting ? 0.6 : 1,
              boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
              marginTop: '6px',
            }}
          >
            {isSubmitting
              ? 'Please wait\u2026'
              : view === 'login'
              ? 'Continue'
              : 'Create Account'}
          </button>
        </form>

        {/* Toggle */}
        <p
          style={{
            fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
            fontSize: '0.82rem',
            color: '#5a6157',
            textAlign: 'center',
            marginTop: '24px',
            marginBottom: 0,
          }}
        >
          {view === 'login' ? (
            <>
              No account?{' '}
              <button
                type="button"
                onClick={() => { setView('register'); setError(null) }}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  fontFamily: 'inherit',
                  fontSize: 'inherit',
                  fontWeight: 600,
                  color: '#4b6646',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                  textUnderlineOffset: '3px',
                }}
              >
                Register
              </button>
            </>
          ) : (
            <>
              Have an account?{' '}
              <button
                type="button"
                onClick={() => { setView('login'); setError(null) }}
                style={{
                  background: 'none',
                  border: 'none',
                  padding: 0,
                  fontFamily: 'inherit',
                  fontSize: 'inherit',
                  fontWeight: 600,
                  color: '#4b6646',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                  textUnderlineOffset: '3px',
                }}
              >
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  )
}
