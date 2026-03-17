'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

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
    <Card className="w-full max-w-sm shadow-lg">
      <CardHeader className="space-y-1">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl font-semibold text-primary">LifeOS</span>
        </div>
        <CardTitle className="text-xl">
          {view === 'login' ? 'Sign in' : 'Create account'}
        </CardTitle>
        <CardDescription>
          {view === 'login'
            ? 'Enter your email and password to continue.'
            : 'Private alpha — invite token required.'}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete={view === 'login' ? 'current-password' : 'new-password'}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {view === 'register' && (
            <div className="space-y-1.5">
              <Label htmlFor="invite_token">Invite token</Label>
              <Input
                id="invite_token"
                type="text"
                value={inviteToken}
                onChange={(e) => setInviteToken(e.target.value)}
              />
            </div>
          )}

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting
              ? 'Please wait…'
              : view === 'login'
              ? 'Sign in'
              : 'Create account'}
          </Button>
        </form>

        <div className="mt-4 text-center text-sm text-muted-foreground">
          {view === 'login' ? (
            <>
              No account?{' '}
              <button
                type="button"
                onClick={() => { setView('register'); setError(null) }}
                className="text-primary hover:underline"
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
                className="text-primary hover:underline"
              >
                Sign in
              </button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
