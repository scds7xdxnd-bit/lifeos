'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { inquiriesApi } from '@/lib/api/inquiries'
import { domainLabel, pairLabel, fmtDate } from '../inquiry/_components/helpers'

const PAGE_SIZE = 50

export default function HistoryPage() {
  const [page, setPage] = useState(0)

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['inquiries-history', page],
    queryFn: () => inquiriesApi.list(PAGE_SIZE, page * PAGE_SIZE),
    staleTime: 1000 * 30,
  })

  const items = data?.items ?? []

  return (
    <div className="space-y-8">

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Inquiry History</h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            Revisit prior questions and reopen grounded results.
          </p>
        </div>
        <Link
          href="/insights/inquiry"
          className="shrink-0 inline-flex items-center px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/85 transition-all shadow-sm"
        >
          New Inquiry
        </Link>
      </div>

      {/* List card */}
      <div className="glass rounded-2xl p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-foreground">History</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Read-first list of prior inquiries. Open any item to inspect full results.
            </p>
          </div>
          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching}
            className="text-sm px-4 py-2 rounded-full bg-white/50 backdrop-blur-sm border border-white/40 text-foreground hover:bg-white/70 disabled:opacity-50 transition-all"
          >
            {isFetching ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>

        {isLoading && (
          <div className="space-y-2.5">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 bg-white/30 rounded-xl animate-pulse" />
            ))}
          </div>
        )}

        {!isLoading && items.length === 0 && (
          <p className="text-sm text-muted-foreground py-6">No inquiry history yet.</p>
        )}

        {!isLoading && items.length > 0 && (
          <ul className="space-y-2">
            {items.map((inq) => {
              const domainDisplay =
                (inq.domains?.length ?? 0) > 1
                  ? pairLabel(inq.domains)
                  : domainLabel(inq.domain)

              return (
                <li key={inq.id} className="rounded-xl bg-white/30 hover:bg-white/50 transition-all px-5 py-4 flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-foreground">{inq.question || 'Untitled inquiry'}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {domainDisplay}
                      {' · '}
                      {inq.timeframe?.start || '—'} → {inq.timeframe?.end || '—'}
                      {' · '}
                      v{inq.last_version_number ?? 1}
                      {' · '}
                      {fmtDate(inq.created_at)}
                    </p>
                  </div>
                  <Link
                    href={`/insights/inquiry?inquiry_id=${inq.id}`}
                    className="shrink-0 text-xs px-3.5 py-1.5 rounded-full bg-white/50 text-foreground hover:bg-white/70 border border-white/40 transition-all"
                  >
                    Open
                  </Link>
                </li>
              )
            })}
          </ul>
        )}

        {/* Pagination */}
        {(items.length === PAGE_SIZE || page > 0) && (
          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0 || isFetching}
              className="text-sm px-4 py-2 rounded-full bg-white/50 border border-white/40 text-foreground hover:bg-white/70 disabled:opacity-40 transition-all"
            >
              Previous
            </button>
            <span className="text-xs text-muted-foreground">Page {page + 1}</span>
            <button
              type="button"
              onClick={() => setPage((p) => p + 1)}
              disabled={items.length < PAGE_SIZE || isFetching}
              className="text-sm px-4 py-2 rounded-full bg-white/50 border border-white/40 text-foreground hover:bg-white/70 disabled:opacity-40 transition-all"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
