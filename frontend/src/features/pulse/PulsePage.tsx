import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '@/components/PageHeader'
import { ErrorState, LoadingBlock } from '@/components/QueryStates'
import { api, unwrap } from '@/lib/api'
import { formatDate } from '@/lib/format'
import { CountryPayrollChart } from './CountryPayrollChart'
import { DepartmentTable } from './DepartmentTable'
import { KpiRow } from './KpiRow'
import { SignalsCard } from './SignalsCard'

/** Home: how ACME pays its people, at a glance. */
export function PulsePage() {
  const pulse = useQuery({
    queryKey: ['pulse'],
    queryFn: () => unwrap(api.GET('/api/insights/pulse')),
  })

  return (
    <>
      <PageHeader
        title="Pay Pulse"
        description="How ACME pays its active workforce, and where to look first."
      />
      {pulse.isPending && <LoadingBlock className="h-96" />}
      {pulse.isError && <ErrorState error={pulse.error} onRetry={() => pulse.refetch()} />}
      {pulse.data && (
        <>
          <KpiRow pulse={pulse.data} />
          <div className="grid gap-6 lg:grid-cols-5">
            <SignalsCard signals={pulse.data.signals} className="lg:col-span-2" />
            <CountryPayrollChart countries={pulse.data.countries} className="lg:col-span-3" />
          </div>
          <DepartmentTable departments={pulse.data.departments} />
          {pulse.data.rate_date && (
            <p className="text-xs text-muted-foreground">
              USD figures use FX rates as of {formatDate(pulse.data.rate_date)}. Pay band: within
              20% of the median for the same role in the same country.
            </p>
          )}
        </>
      )}
    </>
  )
}
