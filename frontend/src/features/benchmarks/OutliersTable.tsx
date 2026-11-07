import { Link } from '@tanstack/react-router'
import { BandBadge } from '@/components/BandBadge'
import { EmptyState, LoadingBlock } from '@/components/QueryStates'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatMoney } from '@/lib/format'
import { useOutliers } from './api'

const SHOWN = 8

/** The people in this role paid furthest from their peer median. */
export function OutliersTable({
  jobTitle,
  country,
}: {
  jobTitle: string | undefined
  country: string | undefined
}) {
  const outliers = useOutliers(jobTitle, country)
  const rows = (outliers.data ?? []).slice(0, SHOWN)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Outside the band</CardTitle>
        <CardDescription>
          Paid more than 20% from the median for the same role in the same country
        </CardDescription>
      </CardHeader>
      <CardContent>
        {outliers.isPending && <LoadingBlock className="h-56" />}
        {outliers.data && rows.length === 0 && <EmptyState title="Everyone is within band" />}
        <ul className="flex flex-col divide-y">
          {rows.map((person) => (
            <li key={person.id}>
              <Link
                to="/people"
                search={{ employee: person.id }}
                className="flex items-center gap-3 py-2 text-sm hover:bg-muted/50"
              >
                <span className="flex-1">
                  <span className="font-medium">
                    {person.first_name} {person.last_name}
                  </span>
                  <span className="block text-xs text-muted-foreground">
                    {person.country_code} · {formatMoney(person.salary, person.currency)} vs median{' '}
                    {formatMoney(person.peer_median, person.currency)}
                  </span>
                </span>
                <span className="text-right text-xs tabular-nums">
                  <BandBadge band={person.band} />
                  <span className="mt-1 block text-muted-foreground">
                    {person.compa_ratio} × median
                  </span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
