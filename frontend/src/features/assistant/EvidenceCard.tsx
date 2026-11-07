import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CountryRanges } from '@/features/benchmarks/CountryRanges'
import type { Schemas } from '@/lib/api'
import { formatCount, formatMoney } from '@/lib/format'

const TOOL_LABELS: Record<string, string> = {
  org_pay_summary: 'Organization pay summary',
  role_pay_by_country: 'Role pay by country',
  salary_distribution: 'Salary distribution',
  available_filters: 'Available countries, departments and roles',
}

function Figures({ rows }: { rows: [string, string][] }) {
  return (
    <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm sm:grid-cols-3">
      {rows.map(([label, value]) => (
        <div key={label}>
          <dt className="text-xs text-muted-foreground">{label}</dt>
          <dd className="font-medium tabular-nums">{value}</dd>
        </div>
      ))}
    </dl>
  )
}

function Body({ evidence }: { evidence: Schemas['Evidence'] }) {
  const result = evidence.result
  switch (evidence.tool) {
    case 'role_pay_by_country':
      return <CountryRanges benchmarks={result as Schemas['Benchmarks']} />
    case 'org_pay_summary': {
      const pulse = result as Schemas['Pulse']
      return (
        <Figures
          rows={[
            ['Headcount', formatCount(pulse.headcount)],
            ['Payroll (USD)', formatMoney(pulse.payroll_usd, 'USD', { compact: true })],
            [
              'Median (USD)',
              pulse.median_salary_usd ? formatMoney(pulse.median_salary_usd, 'USD') : '—',
            ],
            ['Below band', formatCount(pulse.below_band)],
            ['Above band', formatCount(pulse.above_band)],
          ]}
        />
      )
    }
    case 'salary_distribution': {
      const distribution = result as Schemas['Distribution']
      return (
        <ul className="flex flex-col gap-1 text-sm">
          {distribution.buckets
            .filter((bucket) => bucket.count > 0)
            .map((bucket) => (
              <li key={bucket.lower} className="flex justify-between tabular-nums">
                <span className="text-muted-foreground">
                  {formatMoney(bucket.lower, distribution.currency, { compact: true })} –{' '}
                  {formatMoney(bucket.upper, distribution.currency, { compact: true })}
                </span>
                <span>{formatCount(bucket.count)} people</span>
              </li>
            ))}
        </ul>
      )
    }
    default:
      return null
  }
}

/** The data an answer is based on, shown with the same visuals as the rest of the app. */
export function EvidenceCard({ evidence }: { evidence: Schemas['Evidence'] }) {
  const filters = Object.entries(evidence.arguments)
    .filter(([, value]) => value !== null && value !== '')
    .map(([key, value]) => `${key.replace('_', ' ')}: ${value}`)
    .join(' · ')
  const body = Body({ evidence })
  if (!body) return null
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">{TOOL_LABELS[evidence.tool] ?? evidence.tool}</CardTitle>
        <CardDescription>{filters || 'All active employees'}</CardDescription>
      </CardHeader>
      <CardContent>{body}</CardContent>
    </Card>
  )
}
