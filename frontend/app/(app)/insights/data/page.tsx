'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { inquiriesApi, type ReadinessResult } from '@/lib/api/inquiries'
import { Button } from '@/components/ui/button'

const DOMAIN_LABELS: Record<string, string> = {
  calendar: 'Calendar',
  habits: 'Habits',
  projects: 'Projects',
  skills: 'Skills',
  finance: 'Finance',
  health: 'Health',
  journal: 'Journal',
  relationships: 'Relationships',
}

const PAIR_LABELS: Record<string, string> = {
  projects_calendar_v1: 'Projects + Calendar',
  projects_skills_v1: 'Projects + Skills',
}

function domainLabel(d: string) {
  return DOMAIN_LABELS[d.toLowerCase()] ?? d
}

function pairLabel(p: string) {
  return PAIR_LABELS[p.toLowerCase()] ?? p
}

export default function DataReadinessPage() {
  const { data, isLoading, isError, refetch, isFetching } = useQuery<ReadinessResult>({
    queryKey: ['readiness'],
    queryFn: inquiriesApi.readiness,
  })

  const readiness = data?.readiness
  const alpha = data?.alpha

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Data Readiness</h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Check whether your visible alpha domains have enough recent records for inquiry.
          </p>
        </div>
        <Link
          href="/insights/inquiry"
          className="shrink-0 inline-flex items-center px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/85 transition-all shadow-sm"
        >
          Go to Inquiry
        </Link>
      </div>

      {/* Readiness status */}
      <div className="glass rounded-2xl p-6 space-y-5">
        <div>
          <h2 className="font-semibold text-foreground">Readiness Status</h2>
          <p className="text-sm text-muted-foreground mt-1">
            This view is setup-focused only. It does not expose broad domain management.
          </p>
        </div>

        {isLoading && (
          <p className="text-sm text-muted-foreground">Checking readiness…</p>
        )}

        {isError && (
          <p className="text-sm text-destructive">Unable to load readiness.</p>
        )}

        {readiness && (
          <div className="space-y-3">
            <div className="space-y-1.5">
              <p className={`text-sm font-medium ${readiness.ready ? 'text-green-700' : 'text-muted-foreground'}`}>
                {readiness.ready
                  ? `Ready — data found in: ${readiness.ready_domains.map(domainLabel).join(', ') || 'configured domains'}.`
                  : 'Not ready yet for full inquiry generation.'}
              </p>
              {readiness.next_step && (
                <p className="text-sm text-muted-foreground">{readiness.next_step}</p>
              )}
            </div>

            {Object.keys(readiness.domain_event_counts).length > 0 && (
              <ul className="space-y-1.5">
                {Object.entries(readiness.domain_event_counts)
                  .sort(([a], [b]) => a.localeCompare(b))
                  .map(([domain, count]) => (
                    <li key={domain} className="text-sm text-muted-foreground flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-ring/40 shrink-0" />
                      {domainLabel(domain)}: {count} recent records
                    </li>
                  ))}
              </ul>
            )}
          </div>
        )}

        <p className="text-xs text-muted-foreground">
          Need help with readiness or setup?{' '}
          <Link href="/insights/account-help" className="font-medium text-foreground hover:underline underline-offset-2">
            View Account / Help
          </Link>
          .
        </p>

        <Button
          variant="glass"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
        >
          {isFetching ? 'Refreshing…' : 'Refresh readiness'}
        </Button>
      </div>

      {/* Alpha scope */}
      {alpha && (
        <div className="glass rounded-2xl p-6 space-y-5">
          <div>
            <h2 className="font-semibold text-foreground">Alpha Scope</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Only approved alpha domains and pair profiles are shown in this phase.
            </p>
          </div>

          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Visible domains
            </p>
            {alpha.visible_domains.length === 0 ? (
              <p className="text-sm text-muted-foreground">No visible alpha domains configured.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {alpha.visible_domains.map((d) => (
                  <span key={d} className="text-sm bg-white/40 px-3 py-1 rounded-full">{domainLabel(d)}</span>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Visible cross-domain pairs
            </p>
            {alpha.enabled_pair_profiles.length === 0 ? (
              <p className="text-sm text-muted-foreground">No visible cross-domain pair profiles configured.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {alpha.enabled_pair_profiles.map((p) => (
                  <span key={p} className="text-sm bg-white/40 px-3 py-1 rounded-full">{pairLabel(p)}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
