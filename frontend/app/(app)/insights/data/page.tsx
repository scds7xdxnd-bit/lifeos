'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { inquiriesApi, type ReadinessResult } from '@/lib/api/inquiries'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

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
    <div className="space-y-4">
      {/* Header card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle>Data Readiness</CardTitle>
              <CardDescription className="mt-1">
                Check whether your visible alpha domains have enough recent records for inquiry.
              </CardDescription>
            </div>
            <Link
              href="/insights/inquiry"
              className="inline-flex items-center justify-center rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Go to Inquiry
            </Link>
          </div>
        </CardHeader>
      </Card>

      {/* Readiness status */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Readiness Status</CardTitle>
          <CardDescription>
            This view is setup-focused only. It does not expose broad domain management.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading && (
            <p className="text-sm text-muted-foreground">Checking readiness…</p>
          )}

          {isError && (
            <p className="text-sm text-destructive">Unable to load readiness.</p>
          )}

          {readiness && (
            <>
              <div className="space-y-1">
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
                <ul className="space-y-1">
                  {Object.entries(readiness.domain_event_counts)
                    .sort(([a], [b]) => a.localeCompare(b))
                    .map(([domain, count]) => (
                      <li key={domain} className="text-sm text-muted-foreground">
                        {domainLabel(domain)}: {count} recent records
                      </li>
                    ))}
                </ul>
              )}
            </>
          )}

          <p className="text-xs text-muted-foreground">
            Need help with readiness or setup?{' '}
            <Link href="/insights/account-help" className="text-primary hover:underline">
              View Account / Help
            </Link>
            .
          </p>

          <Button
            variant="secondary"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
          >
            {isFetching ? 'Refreshing…' : 'Refresh readiness'}
          </Button>
        </CardContent>
      </Card>

      {/* Alpha scope */}
      {alpha && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Alpha Scope</CardTitle>
            <CardDescription>
              Only approved alpha domains and pair profiles are shown in this phase.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Visible domains
              </p>
              {alpha.visible_domains.length === 0 ? (
                <p className="text-sm text-muted-foreground">No visible alpha domains configured.</p>
              ) : (
                <ul className="space-y-0.5">
                  {alpha.visible_domains.map((d) => (
                    <li key={d} className="text-sm">{domainLabel(d)}</li>
                  ))}
                </ul>
              )}
            </div>

            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Visible cross-domain pairs
              </p>
              {alpha.enabled_pair_profiles.length === 0 ? (
                <p className="text-sm text-muted-foreground">No visible cross-domain pair profiles configured.</p>
              ) : (
                <ul className="space-y-0.5">
                  {alpha.enabled_pair_profiles.map((p) => (
                    <li key={p} className="text-sm">{pairLabel(p)}</li>
                  ))}
                </ul>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
