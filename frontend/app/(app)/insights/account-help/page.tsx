'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/auth/context'

export default function AccountHelpPage() {
  const { user } = useAuth()

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Account / Help</h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Private alpha account access and product usage guidance.
          </p>
        </div>
        <Link
          href="/insights/inquiry"
          className="shrink-0 inline-flex items-center px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/85 transition-all shadow-sm"
        >
          Go to Inquiry
        </Link>
      </div>

      {/* Account Access */}
      <div className="glass rounded-2xl p-6 space-y-4">
        <div>
          <h2 className="font-semibold text-foreground">Account Access</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Session-cookie access only. Invite-based registration remains enforced in private alpha.
          </p>
        </div>
        <div className="rounded-xl bg-white/40 px-5 py-3.5 text-sm text-foreground">
          {user
            ? `${user.email} · timezone ${user.timezone ?? 'UTC'}`
            : 'Account details unavailable.'}
        </div>
        {user && (
          <span className="inline-block text-xs text-green-700 bg-green-50/80 px-3 py-1.5 rounded-full">
            Account active
          </span>
        )}
      </div>

      {/* Support Path */}
      <div className="glass rounded-2xl p-6 space-y-5">
        <div>
          <h2 className="font-semibold text-foreground">Support Path</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Use this path for invite, onboarding, readiness, login, or inquiry-surface issues.
          </p>
        </div>
        <div className="space-y-1.5">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Primary support contact</p>
          <p className="text-sm text-foreground">
            Contact your invite administrator for private alpha support.
          </p>
        </div>
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">When to use support</p>
          <ul className="space-y-1.5 text-sm text-foreground list-disc list-inside">
            <li>Invite token or registration problems</li>
            <li>Readiness blocked and setup confusion</li>
            <li>Login / access issues</li>
            <li>Inquiry result concerns to escalate beyond in-page feedback</li>
          </ul>
        </div>
      </div>

      {/* How to Use */}
      <div className="glass rounded-2xl p-6 space-y-5">
        <div>
          <h2 className="font-semibold text-foreground">How to Use LifeOS Alpha</h2>
          <p className="text-sm text-muted-foreground mt-1">
            LifeOS is a structured inquiry product, not a chatbot or recommendation assistant.
          </p>
        </div>
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Primary loop</p>
          <ol className="space-y-1.5 text-sm text-foreground list-decimal list-inside">
            <li>Check data readiness</li>
            <li>Ask one scoped inquiry question</li>
            <li>Read the humanized brief first</li>
            <li>Open the technical brief when needed</li>
            <li>Refine or return later</li>
          </ol>
        </div>
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Scope boundaries</p>
          <ul className="space-y-1.5 text-sm text-foreground list-disc list-inside">
            <li>No assistant chat mode</li>
            <li>No recommendations or predictive advice</li>
            <li>No broad domain management as primary UX</li>
          </ul>
        </div>
        <div className="flex flex-wrap gap-2.5 pt-2">
          <Link
            href="/insights/inquiry"
            className="inline-flex items-center px-5 py-2.5 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/85 transition-all shadow-sm"
          >
            Go to Inquiry
          </Link>
          <Link
            href="/insights/data"
            className="inline-flex items-center px-4 py-2.5 rounded-full bg-white/50 backdrop-blur-sm border border-white/40 text-sm text-foreground hover:bg-white/70 transition-all"
          >
            Data Readiness
          </Link>
          <Link
            href="/insights/history"
            className="inline-flex items-center px-4 py-2.5 rounded-full bg-white/50 backdrop-blur-sm border border-white/40 text-sm text-foreground hover:bg-white/70 transition-all"
          >
            View History
          </Link>
        </div>
      </div>

    </div>
  )
}
