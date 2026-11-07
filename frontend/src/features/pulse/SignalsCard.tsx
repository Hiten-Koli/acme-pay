import { Link } from '@tanstack/react-router'
import { ArrowDown, ChevronRight } from 'lucide-react'
import { EmptyState } from '@/components/QueryStates'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { Schemas } from '@/lib/api'
import { formatMoney } from '@/lib/format'

/** Peer groups with the largest share of people paid below band. */
export function SignalsCard({
  signals,
  className,
}: {
  signals: Schemas['Signal'][]
  className?: string
}) {
  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Where to look</CardTitle>
        <CardDescription>Roles where people are paid well below their peers.</CardDescription>
      </CardHeader>
      <CardContent>
        {signals.length === 0 ? (
          <EmptyState title="No one is paid below band" />
        ) : (
          <ul className="flex flex-col divide-y">
            {signals.map((signal) => (
              <li key={`${signal.country_code}-${signal.job_title}`}>
                <Link
                  to="/benchmarks"
                  search={{ job_title: signal.job_title, country: signal.country_code }}
                  className="group flex items-center gap-3 py-3 text-sm"
                >
                  <ArrowDown aria-hidden className="size-4 shrink-0 text-status-warning" />
                  <span className="flex-1">
                    <span className="font-medium">
                      {signal.below_band} of {signal.headcount}
                    </span>{' '}
                    {signal.job_title}s in {signal.country_code} are below band
                    <span className="block text-xs text-muted-foreground">
                      Peer median {formatMoney(signal.median_salary, signal.currency)}
                    </span>
                  </span>
                  <ChevronRight
                    aria-hidden
                    className="size-4 text-muted-foreground group-hover:text-foreground"
                  />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}
