import { useQuery } from '@tanstack/react-query'
import { api, unwrap } from '@/lib/api'

/** One role's pay statistics per country. */
export function useBenchmarks(jobTitle: string | undefined) {
  return useQuery({
    queryKey: ['benchmarks', jobTitle],
    queryFn: () =>
      unwrap(
        api.GET('/api/insights/benchmarks', { params: { query: { job_title: jobTitle ?? '' } } }),
      ),
    enabled: Boolean(jobTitle),
  })
}

/** Salary histogram for a role, optionally within one country (local currency). */
export function useDistribution(jobTitle: string | undefined, country: string | undefined) {
  return useQuery({
    queryKey: ['distribution', jobTitle, country],
    queryFn: () =>
      unwrap(
        api.GET('/api/insights/distribution', {
          params: { query: { job_title: jobTitle, country } },
        }),
      ),
    enabled: Boolean(jobTitle),
  })
}

/** People in this role paid outside band, most extreme first. */
export function useOutliers(jobTitle: string | undefined, country: string | undefined) {
  return useQuery({
    queryKey: ['outliers', jobTitle, country],
    queryFn: () =>
      unwrap(
        api.GET('/api/insights/outliers', { params: { query: { job_title: jobTitle, country } } }),
      ),
    enabled: Boolean(jobTitle),
  })
}
