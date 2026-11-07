import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { Schemas } from '@/lib/api'
import { formatCount, formatMoney } from '@/lib/format'

function Kpi({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <Card>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-3xl tabular-nums">{value}</CardTitle>
      </CardHeader>
      <CardContent className="text-xs text-muted-foreground">{hint}</CardContent>
    </Card>
  )
}

/** The four headline numbers. */
export function KpiRow({ pulse }: { pulse: Schemas['Pulse'] }) {
  const outside = pulse.below_band + pulse.above_band
  return (
    <section aria-label="Key figures" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Kpi
        label="Active headcount"
        value={formatCount(pulse.headcount)}
        hint="Across 10 countries"
      />
      <Kpi
        label="Annual payroll"
        value={formatMoney(pulse.payroll_usd, 'USD', { compact: true })}
        hint="Base salary, in USD"
      />
      <Kpi
        label="Median salary"
        value={pulse.median_salary_usd ? formatMoney(pulse.median_salary_usd, 'USD') : '—'}
        hint="Organization-wide, in USD"
      />
      <Kpi
        label="Outside pay band"
        value={formatCount(outside)}
        hint={`${formatCount(pulse.below_band)} below · ${formatCount(pulse.above_band)} above`}
      />
    </section>
  )
}
