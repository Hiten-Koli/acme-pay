import {
  createRootRoute,
  createRoute,
  createRouter,
  lazyRouteComponent,
} from '@tanstack/react-router'
import { AppShell } from '@/app/AppShell'
import { PeoplePage } from '@/features/people/PeoplePage'
import { PulsePage } from '@/features/pulse/PulsePage'

/** Filters, sort, paging and the open profile all live in the URL, so every view is shareable. */
export interface PeopleSearch {
  search?: string
  country?: string
  department?: string
  job_title?: string
  status?: 'active' | 'terminated'
  sort?: 'name' | '-name' | 'salary' | '-salary' | 'hire_date' | '-hire_date'
  page?: number
  employee?: string
}

export interface BenchmarksSearch {
  job_title?: string
  country?: string
}

const text = (value: unknown): string | undefined =>
  typeof value === 'string' && value !== '' ? value : undefined

const SORTS = new Set(['name', '-name', 'salary', '-salary', 'hire_date', '-hire_date'])

const rootRoute = createRootRoute({ component: AppShell })

const pulseRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', component: PulsePage })

const peopleRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/people',
  component: PeoplePage,
  validateSearch: (search: Record<string, unknown>): PeopleSearch => ({
    search: text(search.search),
    country: text(search.country),
    department: text(search.department),
    job_title: text(search.job_title),
    status: search.status === 'terminated' ? 'terminated' : undefined,
    sort: SORTS.has(String(search.sort)) ? (search.sort as PeopleSearch['sort']) : undefined,
    page: Number(search.page) > 1 ? Number(search.page) : undefined,
    employee: text(search.employee),
  }),
})

const benchmarksRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/benchmarks',
  // Loaded on first visit: keeps the charting library out of the initial download.
  component: lazyRouteComponent(
    () => import('@/features/benchmarks/BenchmarksPage'),
    'BenchmarksPage',
  ),
  validateSearch: (search: Record<string, unknown>): BenchmarksSearch => ({
    job_title: text(search.job_title),
    country: text(search.country),
  }),
})

export const router = createRouter({
  routeTree: rootRoute.addChildren([pulseRoute, peopleRoute, benchmarksRoute]),
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
