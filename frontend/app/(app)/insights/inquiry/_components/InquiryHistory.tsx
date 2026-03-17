'use client'

import type { Inquiry } from '@/lib/api/inquiries'
import { domainLabel, pairLabel, fmtDate } from './helpers'

interface InquiryHistoryProps {
  items: Inquiry[]
  isLoading: boolean
  selectedId: number | null
  onView: (inquiry: Inquiry) => void
  onRefine: (inquiry: Inquiry) => void
}

export function InquiryHistory({
  items,
  isLoading,
  selectedId,
  onView,
  onRefine,
}: InquiryHistoryProps) {
  if (isLoading) {
    return (
      <div className="bg-card rounded-xl border border-border p-5">
        <h3 className="font-semibold text-foreground mb-3">Recent Inquiries</h3>
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-muted/40 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (!items.length) {
    return (
      <div className="bg-card rounded-xl border border-border p-5">
        <h3 className="font-semibold text-foreground mb-1">Recent Inquiries</h3>
        <p className="text-sm text-muted-foreground">No inquiries yet. Generate your first brief above.</p>
      </div>
    )
  }

  return (
    <div className="bg-card rounded-xl border border-border p-5 space-y-3">
      <h3 className="font-semibold text-foreground">Recent Inquiries</h3>
      <ul className="space-y-2">
        {items.map((inq) => {
          const isSelected = inq.id === selectedId
          const domainDisplay =
            (inq.domains?.length ?? 0) > 1
              ? pairLabel(inq.domains)
              : domainLabel(inq.domain)

          return (
            <li
              key={inq.id}
              className={`rounded-lg border px-4 py-3 transition-colors ${
                isSelected
                  ? 'border-primary/40 bg-primary/5'
                  : 'border-border bg-background hover:bg-muted/30'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground truncate">{inq.question}</p>
                  <div className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-muted-foreground">
                    <span>{domainDisplay}</span>
                    <span>·</span>
                    <span>{inq.timeframe?.start} → {inq.timeframe?.end}</span>
                    {inq.last_version_number > 1 && (
                      <>
                        <span>·</span>
                        <span>v{inq.last_version_number}</span>
                      </>
                    )}
                    <span>·</span>
                    <span>{fmtDate(inq.created_at)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => onView(inq)}
                    className={`text-xs px-2.5 py-1 rounded-md border transition-colors ${
                      isSelected
                        ? 'border-primary text-primary bg-primary/10'
                        : 'border-border text-foreground hover:bg-muted/50'
                    }`}
                  >
                    View
                  </button>
                  <button
                    type="button"
                    onClick={() => onRefine(inq)}
                    className="text-xs px-2.5 py-1 rounded-md border border-border text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
                  >
                    Refine
                  </button>
                </div>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
