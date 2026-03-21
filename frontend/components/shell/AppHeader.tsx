'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'
import {
  Calendar,
  Search,
  Wallet,
  Heart,
  Repeat,
  BookOpen,
  LogOut,
  User,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'

/* ── Navigation structure ──────────────────────────────────────────────────── */

const PRIMARY_LINKS = [
  { href: '/calendar', label: 'Calendar', icon: Calendar },
  { href: '/insights/inquiry', label: 'Inquiry', icon: Search },
]

const DOMAIN_LINKS = [
  { href: '/finances', label: 'Finances', icon: Wallet, accent: '#3a5c35' },
  { href: '/health', label: 'Health', icon: Heart, accent: '#8b4a3a' },
  { href: '/habits', label: 'Habits', icon: Repeat, accent: '#3a5272' },
  { href: '/skills', label: 'Skills', icon: BookOpen, accent: '#6b5a35' },
]

const ALL_LINKS = [
  ...PRIMARY_LINKS.map((l) => ({ ...l, accent: '#4b6646' })),
  ...DOMAIN_LINKS,
]

/* ── Component ─────────────────────────────────────────────────────────────── */

export function AppHeader() {
  const pathname = usePathname()
  const router = useRouter()
  const { logout, user } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  async function handleLogout() {
    await logout()
    router.push('/login')
  }

  function isActive(href: string) {
    return pathname === href || pathname.startsWith(href + '/')
  }

  return (
    <>
      <header
        className="sticky top-0 z-50"
        style={{
          background: 'rgba(248, 250, 242, 0.75)',
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.20)',
          boxShadow: '0 4px 24px rgba(46, 52, 43, 0.04)',
        }}
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between gap-4">
          {/* Brand — Newsreader italic in primary */}
          <Link
            href="/calendar"
            className="shrink-0"
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontSize: '1.35rem',
              fontWeight: 400,
              fontStyle: 'italic',
              color: '#4b6646',
              letterSpacing: '-0.03em',
              textDecoration: 'none',
            }}
          >
            LifeOS
          </Link>

          {/* Desktop navigation — hidden on mobile */}
          <nav aria-label="Primary" className="hidden lg:flex items-center gap-1">
            {PRIMARY_LINKS.map(({ href, label, icon: Icon }) => {
              const active = isActive(href)
              return (
                <Link
                  key={href}
                  href={href}
                  className="flex items-center gap-2 px-4 py-2 rounded-full text-sm transition-all duration-200"
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontWeight: active ? 700 : 500,
                    color: active ? '#ffffff' : '#5a6157',
                    background: active
                      ? 'linear-gradient(135deg, #4b6646, #3f5a3a)'
                      : 'transparent',
                    boxShadow: active
                      ? '0 4px 20px rgba(46, 52, 43, 0.18)'
                      : 'none',
                    whiteSpace: 'nowrap',
                  }}
                >
                  <Icon size={16} strokeWidth={active ? 2.5 : 2} />
                  {label}
                </Link>
              )
            })}

            {/* Separator */}
            <div
              className="mx-2 h-5"
              style={{
                width: '1px',
                background: 'rgba(173, 180, 168, 0.3)',
              }}
            />

            {/* Domain links */}
            {DOMAIN_LINKS.map(({ href, label, icon: Icon, accent }) => {
              const active = isActive(href)
              return (
                <Link
                  key={href}
                  href={href}
                  className="flex items-center gap-2 px-4 py-2 rounded-full text-sm transition-all duration-200"
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontWeight: active ? 700 : 500,
                    color: active ? '#ffffff' : '#5a6157',
                    background: active
                      ? `linear-gradient(135deg, ${accent}, ${accent}dd)`
                      : 'transparent',
                    boxShadow: active
                      ? '0 4px 20px rgba(46, 52, 43, 0.18)'
                      : 'none',
                    whiteSpace: 'nowrap',
                  }}
                >
                  <Icon size={16} strokeWidth={active ? 2.5 : 2} />
                  {label}
                </Link>
              )
            })}
          </nav>

          {/* Right side: user area (desktop) + mobile menu toggle */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Desktop user area */}
            <div className="hidden lg:flex items-center gap-3">
              {user && (
                <div className="flex items-center gap-2">
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center"
                    style={{ background: '#e5eade', color: '#4b6646' }}
                  >
                    <User size={14} strokeWidth={2} />
                  </div>
                  <span
                    className="text-xs hidden xl:block"
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      color: '#767d72',
                      maxWidth: '140px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {user.email}
                  </span>
                </div>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition-all duration-200"
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontWeight: 700,
                  color: '#767d72',
                  background: 'transparent',
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase' as const,
                  cursor: 'pointer',
                  border: 'none',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = '#4b6646'
                  e.currentTarget.style.background = '#e5eade'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#767d72'
                  e.currentTarget.style.background = 'transparent'
                }}
              >
                <LogOut size={13} strokeWidth={2} />
                Sign out
              </button>
            </div>

            {/* Mobile menu toggle */}
            <button
              className="lg:hidden flex items-center justify-center"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '100px',
                border: 'none',
                background: mobileMenuOpen ? '#e5eade' : 'transparent',
                color: '#4b6646',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile dropdown menu */}
        {mobileMenuOpen && (
          <div
            className="lg:hidden"
            style={{
              background: 'rgba(248, 250, 242, 0.95)',
              backdropFilter: 'blur(12px)',
              WebkitBackdropFilter: 'blur(12px)',
              borderTop: '1px solid rgba(255, 255, 255, 0.15)',
              padding: '12px 16px 16px',
              boxShadow: '0 8px 24px rgba(46, 52, 43, 0.08)',
            }}
          >
            {/* Nav links grid — 3 columns for 6 items */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '8px',
                marginBottom: '12px',
              }}
            >
              {ALL_LINKS.map(({ href, label, icon: Icon, accent }) => {
                const active = isActive(href)
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex flex-col items-center gap-1.5 py-3 rounded-2xl transition-all duration-200"
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.6875rem',
                      fontWeight: active ? 700 : 500,
                      color: active ? '#ffffff' : '#5a6157',
                      background: active
                        ? `linear-gradient(135deg, ${accent}, ${accent}dd)`
                        : '#ffffff',
                      boxShadow: active
                        ? '0 4px 16px rgba(46, 52, 43, 0.15)'
                        : '0 1px 4px rgba(46, 52, 43, 0.04)',
                      textDecoration: 'none',
                      borderRadius: '0 12px 12px 12px',
                    }}
                  >
                    <Icon size={18} strokeWidth={active ? 2.2 : 1.8} />
                    {label}
                  </Link>
                )
              })}
            </div>

            {/* User info + logout */}
            <div
              className="flex items-center justify-between pt-3"
              style={{
                borderTop: '1px solid rgba(173, 180, 168, 0.15)',
              }}
            >
              {user && (
                <div className="flex items-center gap-2">
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center"
                    style={{ background: '#e5eade', color: '#4b6646' }}
                  >
                    <User size={14} strokeWidth={2} />
                  </div>
                  <span
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.75rem',
                      color: '#767d72',
                      maxWidth: '180px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {user.email}
                  </span>
                </div>
              )}
              <button
                onClick={() => { setMobileMenuOpen(false); handleLogout() }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-all duration-200"
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontWeight: 700,
                  fontSize: '0.6875rem',
                  color: '#767d72',
                  background: 'transparent',
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase' as const,
                  cursor: 'pointer',
                  border: 'none',
                }}
              >
                <LogOut size={13} strokeWidth={2} />
                Sign out
              </button>
            </div>
          </div>
        )}
      </header>
    </>
  )
}
