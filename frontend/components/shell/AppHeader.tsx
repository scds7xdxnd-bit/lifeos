'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'

const NAV_LINKS = [
  { href: '/insights/inquiry', label: 'Inquiry' },
  { href: '/calendar', label: 'Calendar' },
  { href: '/habits', label: 'Habits' },
  { href: '/skills', label: 'Skills' },
  { href: '/projects', label: 'Projects' },
  { href: '/insights/data', label: 'Data' },
  { href: '/insights/account-help', label: 'Account' },
]

export function AppHeader() {
  const pathname = usePathname()
  const router = useRouter()
  const { logout, user } = useAuth()

  async function handleLogout() {
    await logout()
    router.push('/login')
  }

  return (
    <header
      className="sticky top-0 z-50 px-4 py-3"
      style={{
        background: 'rgba(248,247,245,0.90)',
        backdropFilter: 'blur(14px)',
        WebkitBackdropFilter: 'blur(14px)',
        borderBottom: '1px solid rgba(0,0,0,0.06)',
      }}
    >
      <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
        {/* Brand */}
        <Link
          href="/insights/inquiry"
          className="shrink-0"
          style={{
            fontFamily: 'Georgia, "Times New Roman", serif',
            fontSize: '1.2rem',
            fontWeight: 700,
            color: '#1A1A1A',
            letterSpacing: '-0.01em',
            textDecoration: 'none',
          }}
        >
          LifeOS
        </Link>

        {/* Nav */}
        <nav aria-label="Primary" className="flex items-center gap-1">
          {NAV_LINKS.map(({ href, label }) => {
            const active = pathname === href || pathname.startsWith(href + '/')
            return (
              <Link
                key={href}
                href={href}
                style={{
                  padding: '6px 16px',
                  borderRadius: '100px',
                  fontSize: '0.875rem',
                  fontWeight: active ? 600 : 400,
                  color: active ? '#ffffff' : '#555555',
                  background: active ? '#1A1A1A' : 'transparent',
                  textDecoration: 'none',
                  transition: 'background 0.18s ease, color 0.18s ease',
                  whiteSpace: 'nowrap',
                }}
              >
                {label}
              </Link>
            )
          })}
        </nav>

        {/* User + logout */}
        <div className="flex items-center gap-3 shrink-0">
          {user && (
            <span
              className="hidden sm:block"
              style={{ fontSize: '0.8rem', color: '#999' }}
            >
              {user.email}
            </span>
          )}
          <button
            onClick={handleLogout}
            style={{
              padding: '6px 16px',
              borderRadius: '100px',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: '#555',
              background: 'transparent',
              border: '1px solid rgba(0,0,0,0.12)',
              cursor: 'pointer',
              transition: 'background 0.18s ease, border-color 0.18s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#EDEAE4'
              e.currentTarget.style.borderColor = 'rgba(0,0,0,0.18)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.borderColor = 'rgba(0,0,0,0.12)'
            }}
          >
            Sign out
          </button>
        </div>
      </div>
    </header>
  )
}
