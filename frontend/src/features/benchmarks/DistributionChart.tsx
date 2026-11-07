import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { EmptyState, LoadingBlock } from '@/components/QueryStates'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatMoney } from '@/lib/format'
import { useDistribution } from './api'

/** Histogram of salaries for the role (local currency within a country, otherwise USD). */
export function DistributionChart({
  jobTitle,
  country,
}: {
  jobTitle: string | undefined
  country: string | undefined
}) {
  const distribution = useDistribution(jobTitle, country)
  const currency = distribution.data?.currency ?? 'USD'
  const data = (distribution.data?.buckets ?? []).map((bucket) => ({
    ...bucket,
    label: formatMoney(bucket.lower, currency, { compact: true }),
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Salary distribution</CardTitle>
        <CardDescription>
          {country ? `${country}, ${currency}` : 'All countries, USD'} · number of people
        </CardDescription>
      </CardHeader>
      <CardContent>
        {distribution.isPending && <LoadingBlock className="h-56" />}
        {distribution.data && data.length === 0 && <EmptyState title="No salaries to show" />}
        {data.length > 0 && (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data} barCategoryGap={2}>
              <CartesianGrid vertical={false} stroke="var(--border)" />
              <XAxis
                dataKey="label"
                tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                allowDecimals={false}
                width={32}
                tick={{ fill: 'var(--muted-foreground)', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: 'var(--muted)' }}
                content={({ active, payload }) => {
                  const bucket = payload?.[0]?.payload as (typeof data)[number] | undefined
                  if (!active || !bucket) return null
                  return (
                    <div className="rounded-md border bg-popover px-3 py-2 text-xs shadow-md">
                      <p className="font-medium">{bucket.count} people</p>
                      <p className="text-muted-foreground">
                        {formatMoney(bucket.lower, currency)} –{' '}
                        {formatMoney(bucket.upper, currency)}
                      </p>
                    </div>
                  )
                }}
              />
              <Bar dataKey="count" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
