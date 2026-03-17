'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

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
      router.push('/insights/data')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-sm space-y-10">
      {/* Brand */}
      <div className="text-center space-y-2">
        <h1
          className="text-4xl font-bold tracking-tight"
          style={{ fontFamily: 'var(--font-serif)', letterSpacing: '-0.03em' }}
        >
          LifeOS
        </h1>
        <p className="text-muted-foreground text-sm">
          {view === 'login'
            ? 'Your life, clearly.'
            : 'Private alpha — invite token required.'}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email" className="text-xs text-muted-foreground">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            required
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="password" className="text-xs text-muted-foreground">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete={view === 'login' ? 'current-password' : 'new-password'}
            required
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {view === 'register' && (
          <div className="space-y-2">
            <Label htmlFor="invite_token" className="text-xs text-muted-foreground">Invite token</Label>
            <Input
              id="invite_token"
              type="text"
              placeholder="Paste your invite token"
              value={inviteToken}
              onChange={(e) => setInviteToken(e.target.value)}
            />
          </div>
        )}

        {error && (
          <p className="text-sm text-destructive text-center">{error}</p>
        )}

        <button type="submit" className="glass-btn" disabled={isSubmitting}>
          {isSubmitting
            ? 'Please wait…'
            : view === 'login'
            ? 'Continue with Email'
            : 'Create Account'}
        </button>
      </form>

      {/* Toggle */}
      <p className="text-center text-sm text-muted-foreground">
        {view === 'login' ? (
          <>
            No account?{' '}
            <button
              type="button"
              onClick={() => { setView('register'); setError(null) }}
              className="font-medium text-foreground hover:underline underline-offset-2"
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
              className="font-medium text-foreground hover:underline underline-offset-2"
            >
              Sign in
            </button>
          </>
        )}
      </p>
    </div>
  )
}
