import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { LoadingBlock } from '@/components/QueryStates'
import type { Schemas } from '@/lib/api'
import { formatChange, formatDate, formatMoney } from '@/lib/format'
import { useSalaryHistory } from './api'

const REASON_LABELS: Record<Schemas['CompensationReason'], string> = {
  hire: 'Starting salary',
  merit: 'Merit increase',
  promotion: 'Promotion',
  market_adjustment: 'Market adjustment',
  correction: 'Correction',
}

/** Salary over time (step chart, one series) and the append-only list of changes. */
export function SalaryHistory({ employee }: { employee: Schemas['EmployeeRead'] }) {
  const history = useSalaryHistory(employee.id)
  if (history.isPending) return <LoadingBlock className="h-48" />
  const entries = history.data ?? []
  const points = [...entries]
    .reverse()
    .map((entry) => ({ date: entry.effective_date, salary: Number(entry.new_salary) }))

  return (
    <section aria-labelledby="salary-history" className="flex flex-col gap-3">
      <h2 id="salary-history" className="font-medium">
        Salary history
      </h2>
      {points.length > 1 && (
        <ResponsiveContainer width="100%" height={140}>
          <LineChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
            <XAxis
              dataKey="date"
              tickFormatter={(date: string) => date.slice(0, 4)}
              tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis hide domain={['dataMin', 'dataMax']} />
            <Tooltip
              content={({ active, payload }) => {
                const point = payload?.[0]?.payload as (typeof points)[number] | undefined
                if (!active || !point) return null
                return (
                  <div className="rounded-md border bg-popover px-3 py-2 text-xs shadow-md">
                    <p className="font-medium">{formatMoney(point.salary, employee.currency)}</p>
                    <p className="text-muted-foreground">from {formatDate(point.date)}</p>
                  </div>
                )
              }}
            />
            <Line
              type="stepAfter"
              dataKey="salary"
              stroke="var(--chart-1)"
              strokeWidth={2}
              dot={{ r: 4, fill: 'var(--chart-1)', stroke: 'var(--background)', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
      <ol className="flex flex-col divide-y rounded-lg border text-sm">
        {entries.map((entry) => {
          const previous = entry.previous_salary ? Number(entry.previous_salary) : undefined
          const change = previous
            ? ((Number(entry.new_salary) - previous) / previous) * 100
            : undefined
          return (
            <li key={entry.id} className="flex items-center gap-3 px-3 py-2">
              <span className="w-24 shrink-0 text-muted-foreground tabular-nums">
                {formatDate(entry.effective_date)}
              </span>
              <span className="flex-1">
                {REASON_LABELS[entry.reason]}
                <span className="block text-xs text-muted-foreground">by {entry.changed_by}</span>
              </span>
              <span className="text-right tabular-nums">
                {formatMoney(entry.new_salary, entry.currency)}
                {change !== undefined && (
                  <span className="block text-xs text-muted-foreground">
                    {formatChange(change)}
                  </span>
                )}
              </span>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
