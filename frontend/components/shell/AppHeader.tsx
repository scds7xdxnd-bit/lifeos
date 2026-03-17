'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'
import { Button } from '@/components/ui/button'

const NAV_LINKS = [
  { href: '/insights/inquiry', label: 'Inquiry' },
  { href: '/insights/history', label: 'History' },
  { href: '/insights/data', label: 'Data' },
  { href: '/insights/account-help', label: 'Account / Help' },
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
    <header className="sticky top-0 z-50 px-4 py-3"
      style={{ background: 'linear-gradient(180deg, rgba(248,250,252,0.96) 0%, rgba(238,242,248,0.9) 100%)', backdropFilter: 'blur(14px)', borderBottom: '1px solid var(--border)' }}>
      <div className="max-w-5xl mx-auto bg-white/90 border border-border rounded-2xl shadow-sm px-5 py-3 flex flex-col gap-2">
        {/* Top row: brand + actions */}
        <div className="flex items-center justify-between">
          <div>
            <Link href="/insights/inquiry" className="text-base font-semibold text-primary leading-none">
              LifeOS
            </Link>
            <p className="text-xs text-muted-foreground mt-0.5">Calm accountability OS</p>
          </div>
          <div className="flex items-center gap-2">
            {user && (
              <span className="text-xs text-muted-foreground hidden sm:block">{user.email}</span>
            )}
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </div>

        {/* Nav row */}
        <nav aria-label="Primary" className="flex flex-wrap gap-1">
          {NAV_LINKS.map(({ href, label }) => {
            const active = pathname === href || pathname.startsWith(href + '/')
            return (
              <Link
                key={href}
                href={href}
                className={[
                  'px-3 py-1.5 rounded-lg text-sm transition-colors',
                  active
                    ? 'bg-primary text-white font-medium'
                    : 'text-foreground hover:bg-secondary',
                ].join(' ')}
              >
                {label}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
