import { BandBadge } from '@/components/BandBadge'
import { LoadingBlock } from '@/components/QueryStates'
import { RangeBar } from '@/components/RangeBar'
import type { Schemas } from '@/lib/api'
import { formatMoney } from '@/lib/format'
import { usePayPosition } from './api'

const PADDING = 0.05

/** The salary, its band state, and where it sits among peers (p10–p90 scale). */
export function PayPositionCard({ employee }: { employee: Schemas['EmployeeRead'] }) {
  const position = usePayPosition(employee.id)
  const money = (amount: string) => formatMoney(amount, employee.currency)

  if (position.isPending) return <LoadingBlock className="h-32" />
  const peers = position.data?.peers
  const salary = Number(employee.salary)

  return (
    <section aria-labelledby="pay-position" className="flex flex-col gap-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h2 id="pay-position" className="text-sm text-muted-foreground">
            Annual salary
          </h2>
          <p className="text-3xl font-semibold tabular-nums">{money(employee.salary)}</p>
        </div>
        {position.data?.band && (
          <div className="flex flex-col items-end gap-1">
            <BandBadge band={position.data.band} />
            <span className="text-xs text-muted-foreground tabular-nums">
              {position.data.compa_ratio} × peer median
            </span>
          </div>
        )}
      </div>
      {peers?.p10 && peers.p25 && peers.median && peers.p75 && peers.p90 ? (
        <div>
          <RangeBar
            domain={[
              Math.min(Number(peers.p10), salary) * (1 - PADDING),
              Math.max(Number(peers.p90), salary) * (1 + PADDING),
            ]}
            p25={Number(peers.p25)}
            median={Number(peers.median)}
            p75={Number(peers.p75)}
            marker={salary}
            label={`Salary ${money(employee.salary)} against a peer median of ${money(peers.median)}`}
          />
          <div className="mt-1 flex justify-between text-xs text-muted-foreground tabular-nums">
            <span>10th pct {money(peers.p10)}</span>
            <span className="text-foreground">Median {money(peers.median)}</span>
            <span>90th pct {money(peers.p90)}</span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Compared with {peers.headcount} active {employee.job_title}s in {employee.country_code}.
            Shaded: middle 50% of peers.
          </p>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">Not enough active peers to compare.</p>
      )}
    </section>
  )
}
