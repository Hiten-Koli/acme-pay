import { useQuery } from '@tanstack/react-query'
import { api, type Schemas, unwrap } from '@/lib/api'

/** Countries, departments and job titles for filters and forms (rarely changes). */
export function useOptions() {
  return useQuery({
    queryKey: ['options'],
    queryFn: () => unwrap(api.GET('/api/meta/options')),
    staleTime: Number.POSITIVE_INFINITY,
  })
}

/** Look up a country by code in the loaded options. */
export function findCountry(
  options: Schemas['Options'] | undefined,
  code: string,
): Schemas['Country'] | undefined {
  return options?.countries.find((country) => country.code === code)
}
