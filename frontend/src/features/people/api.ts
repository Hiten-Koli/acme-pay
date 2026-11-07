import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import type { paths } from '@/api/schema'
import { api, type Schemas, unwrap } from '@/lib/api'

/** Query parameters of GET /api/employees, straight from the API contract. */
export type EmployeeFilters = NonNullable<paths['/api/employees']['get']['parameters']['query']>

/** One page of employees; keeps the previous page on screen while the next loads. */
export function useEmployees(filters: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => unwrap(api.GET('/api/employees', { params: { query: filters } })),
    placeholderData: keepPreviousData,
  })
}

/** URL for downloading the filtered directory as CSV. */
export function exportUrl(filters: EmployeeFilters): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters ?? {})) {
    if (value !== undefined && value !== '' && key !== 'page' && key !== 'page_size') {
      params.set(key, String(value))
    }
  }
  return `/api/employees/export.csv?${params}`
}

/** Hire a new employee. */
export function useHireEmployee() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: Schemas['EmployeeCreate']) => unwrap(api.POST('/api/employees', { body })),
    onSuccess: () => queryClient.invalidateQueries(),
  })
}
