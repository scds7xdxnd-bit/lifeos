'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/auth/context'

export default function AccountHelpPage() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">

        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Account / Help</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Private alpha account access and product usage guidance.
            </p>
          </div>
          <Link
            href="/users/profile"
            className="shrink-0 inline-flex items-center px-3 py-1.5 rounded-md border border-border text-sm text-foreground hover:bg-muted/50 transition-colors"
          >
            Profile
          </Link>
        </div>

        {/* Account Access */}
        <div className="bg-card rounded-xl border border-border p-5 space-y-3">
          <div>
            <h2 className="font-semibold text-foreground">Account Access</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Session-cookie access only. Invite-based registration remains enforced in private alpha.
            </p>
          </div>
          <div className="rounded-lg bg-muted/30 px-4 py-3 text-sm text-foreground">
            {user
              ? `${user.email} · timezone ${user.timezone ?? 'UTC'}`
              : 'Account details unavailable.'}
          </div>
          {user && (
            <p className="text-xs text-green-700 bg-green-50 px-3 py-1.5 rounded-md inline-block">
              Account active
            </p>
          )}
        </div>

        {/* Support Path */}
        <div className="bg-card rounded-xl border border-border p-5 space-y-4">
          <div>
            <h2 className="font-semibold text-foreground">Support Path</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Use this path for invite, onboarding, readiness, login, or inquiry-surface issues.
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Primary support contact</p>
            <p className="text-sm text-foreground">
              Contact your invite administrator for private alpha support.
            </p>
          </div>
          <div className="space-y-1.5">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">When to use support</p>
            <ul className="space-y-1 text-sm text-foreground list-disc list-inside">
              <li>Invite token or registration problems</li>
              <li>Readiness blocked and setup confusion</li>
              <li>Login / access issues</li>
              <li>Inquiry result concerns to escalate beyond in-page feedback</li>
            </ul>
          </div>
        </div>

        {/* How to Use */}
        <div className="bg-card rounded-xl border border-border p-5 space-y-4">
          <div>
            <h2 className="font-semibold text-foreground">How to Use LifeOS Alpha</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              LifeOS is a structured inquiry product, not a chatbot or recommendation assistant.
            </p>
          </div>
          <div className="space-y-1.5">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Primary loop</p>
            <ol className="space-y-1 text-sm text-foreground list-decimal list-inside">
              <li>Check data readiness</li>
              <li>Ask one scoped inquiry question</li>
              <li>Read the humanized brief first</li>
              <li>Open the technical brief when needed</li>
              <li>Refine or return later</li>
            </ol>
          </div>
          <div className="space-y-1.5">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Scope boundaries</p>
            <ul className="space-y-1 text-sm text-foreground list-disc list-inside">
              <li>No assistant chat mode</li>
              <li>No recommendations or predictive advice</li>
              <li>No broad domain management as primary UX</li>
            </ul>
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            <Link
              href="/insights/inquiry"
              className="inline-flex items-center px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              Go to Inquiry
            </Link>
            <Link
              href="/insights/data"
              className="inline-flex items-center px-3 py-2 rounded-md border border-border text-sm text-foreground hover:bg-muted/50 transition-colors"
            >
              Data Readiness
            </Link>
            <Link
              href="/insights/history"
              className="inline-flex items-center px-3 py-2 rounded-md border border-border text-sm text-foreground hover:bg-muted/50 transition-colors"
            >
              View History
            </Link>
          </div>
        </div>

      </div>
    </div>
  )
}
