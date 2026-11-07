import { RangeBar } from '@/components/RangeBar'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { Schemas } from '@/lib/api'
import { formatMoney } from '@/lib/format'
import { cn } from '@/lib/utils'

/** Middle-50% pay range and median per country, on one shared USD scale. */
export function CountryRanges({
  benchmarks,
  highlight,
}: {
  benchmarks: Schemas['Benchmarks']
  highlight?: string
}) {
  const highest = Math.max(...benchmarks.countries.map((c) => Number(c.p75_usd)))
  const domain: [number, number] = [0, highest * 1.05]

  return (
    <Card>
      <CardHeader>
        <CardTitle>{benchmarks.job_title}: pay by country</CardTitle>
        <CardDescription>
          Bar: middle 50% of salaries (25th–75th percentile) · tick: median · USD
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-1">
          {benchmarks.countries.map((country) => (
            <li
              key={country.country_code}
              className={cn(
                'grid grid-cols-[4.5rem_1fr_7rem] items-center gap-3 rounded-md px-2 py-1 text-sm sm:grid-cols-[4.5rem_1fr_7rem_10rem]',
                highlight === country.country_code && 'bg-muted',
              )}
            >
              <span className="tabular-nums">{country.country_code}</span>
              <RangeBar
                domain={domain}
                p25={Number(country.p25_usd)}
                median={Number(country.median_usd)}
                p75={Number(country.p75_usd)}
                label={`${country.country_code}: median ${formatMoney(country.median_usd, 'USD')}, middle 50% ${formatMoney(country.p25_usd, 'USD')} to ${formatMoney(country.p75_usd, 'USD')}`}
              />
              <span className="text-right font-medium tabular-nums">
                {formatMoney(country.median_usd, 'USD')}
              </span>
              <span className="hidden text-right text-xs text-muted-foreground tabular-nums sm:block">
                {formatMoney(country.median, country.currency)} · {country.headcount} people
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}
