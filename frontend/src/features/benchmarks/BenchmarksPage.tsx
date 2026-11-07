import { getRouteApi } from '@tanstack/react-router'
import { PageHeader } from '@/components/PageHeader'
import { EmptyState, ErrorState, LoadingBlock } from '@/components/QueryStates'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useOptions } from '@/features/meta/useOptions'
import { useBenchmarks } from './api'
import { CountryRanges } from './CountryRanges'
import { DistributionChart } from './DistributionChart'
import { OutliersTable } from './OutliersTable'

const route = getRouteApi('/benchmarks')
const DEFAULT_ROLE = 'Software Engineer'
const ALL = '__all__'

/** Compare what one role is paid across countries, and who sits outside the band. */
export function BenchmarksPage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const options = useOptions()
  const jobTitle =
    search.job_title ??
    (options.data?.job_titles.includes(DEFAULT_ROLE) ? DEFAULT_ROLE : options.data?.job_titles[0])
  const benchmarks = useBenchmarks(jobTitle)

  return (
    <>
      <PageHeader
        title="Benchmarks"
        description="What a role is paid in each country, normalized to USD."
        actions={
          <>
            <Select
              value={jobTitle}
              onValueChange={(job_title) =>
                navigate({ search: { job_title, country: search.country }, replace: true })
              }
            >
              <SelectTrigger aria-label="Job title" className="w-56">
                <SelectValue placeholder="Choose a role" />
              </SelectTrigger>
              <SelectContent>
                {options.data?.job_titles.map((title) => (
                  <SelectItem key={title} value={title}>
                    {title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={search.country ?? ALL}
              onValueChange={(country) =>
                navigate({
                  search: { job_title: jobTitle, country: country === ALL ? undefined : country },
                  replace: true,
                })
              }
            >
              <SelectTrigger aria-label="Country" className="w-44">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ALL}>All countries</SelectItem>
                {options.data?.countries.map((country) => (
                  <SelectItem key={country.code} value={country.code}>
                    {country.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </>
        }
      />
      {benchmarks.isPending && <LoadingBlock className="h-96" />}
      {benchmarks.isError && (
        <ErrorState error={benchmarks.error} onRetry={() => benchmarks.refetch()} />
      )}
      {benchmarks.data &&
        (benchmarks.data.countries.length === 0 ? (
          <EmptyState title={`No active ${jobTitle}s`} />
        ) : (
          <>
            <CountryRanges benchmarks={benchmarks.data} highlight={search.country} />
            <div className="grid gap-6 lg:grid-cols-2">
              <DistributionChart jobTitle={jobTitle} country={search.country} />
              <OutliersTable jobTitle={jobTitle} country={search.country} />
            </div>
          </>
        ))}
    </>
  )
}
