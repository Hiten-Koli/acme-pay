import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import type { Schemas } from '@/lib/api'
import { formatCount, formatMoney } from '@/lib/format'

/**
 * Payroll per country in USD. One series, so one hue and no legend (the title names it).
 * Plain HTML bars: lighter than a chart library on the first screen, and readable by
 * assistive technology as a list.
 */
export function CountryPayrollChart({
  countries,
  className,
}: {
  countries: Schemas['CountryPay'][]
  className?: string
}) {
  const largest = Math.max(...countries.map((c) => Number(c.payroll_usd)), 1)

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Payroll by country</CardTitle>
        <CardDescription>Annual base salary, USD</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-1.5">
          {countries.map((country) => {
            const width = (Number(country.payroll_usd) / largest) * 100
            return (
              <li key={country.country_code}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="group grid grid-cols-[3.5rem_1fr_4.5rem] items-center gap-2 rounded-sm text-sm">
                      <span className="tabular-nums">{country.country_code}</span>
                      <span className="h-5 rounded-sm bg-muted/60">
                        <span
                          className="block h-full rounded-r-[4px] bg-chart-1 group-hover:opacity-80"
                          style={{ width: `${Math.max(width, 1)}%` }}
                        />
                      </span>
                      <span className="text-right text-muted-foreground tabular-nums">
                        {formatMoney(country.payroll_usd, 'USD', { compact: true })}
                      </span>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    {formatCount(country.headcount)} people · median{' '}
                    {formatMoney(country.median_salary_usd, 'USD')} · paid in {country.currency}
                  </TooltipContent>
                </Tooltip>
              </li>
            )
          })}
        </ul>
      </CardContent>
    </Card>
  )
}
