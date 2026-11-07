import { getRouteApi } from '@tanstack/react-router'
import { Download } from 'lucide-react'
import { lazy, Suspense } from 'react'
import type { PeopleSearch } from '@/app/router'
import { PageHeader } from '@/components/PageHeader'
import { EmptyState, ErrorState, LoadingBlock } from '@/components/QueryStates'
import { Button } from '@/components/ui/button'
import { exportUrl, useEmployees } from './api'
import { HireDialog } from './HireDialog'
import { Pagination } from './Pagination'
import { PeopleFilters } from './PeopleFilters'
import { PeopleTable } from './PeopleTable'

// Loaded when a profile is first opened (it brings the salary-history chart with it).
const ProfileSheet = lazy(() =>
  import('@/features/profile/ProfileSheet').then((module) => ({ default: module.ProfileSheet })),
)

const PAGE_SIZE = 25
const route = getRouteApi('/people')

/** The searchable employee directory. */
export function PeoplePage() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const filters = {
    search: search.search,
    country: search.country,
    department: search.department,
    job_title: search.job_title,
    status: search.status ?? 'active',
    sort: search.sort ?? 'name',
    page: search.page ?? 1,
    page_size: PAGE_SIZE,
  } as const
  const employees = useEmployees(filters)

  /** Change the URL; any filter change returns to the first page. */
  const update = (changes: Partial<PeopleSearch>) =>
    navigate({ search: (prev) => ({ ...prev, page: undefined, ...changes }), replace: true })

  return (
    <>
      <PageHeader
        title="People"
        description="Everyone at ACME, their role and what they are paid."
        actions={
          <>
            <Button variant="outline" asChild>
              <a href={exportUrl(filters)} download>
                <Download />
                Export CSV
              </a>
            </Button>
            <HireDialog onHired={(id) => update({ employee: id })} />
          </>
        }
      />
      <PeopleFilters search={search} onChange={update} />
      {employees.isPending && <LoadingBlock className="h-[480px]" />}
      {employees.isError && (
        <ErrorState error={employees.error} onRetry={() => employees.refetch()} />
      )}
      {employees.data &&
        (employees.data.total === 0 ? (
          <EmptyState title="No one matches these filters" hint="Try a broader search." />
        ) : (
          <>
            <PeopleTable
              employees={employees.data.items}
              sort={filters.sort}
              onSort={(sort) => update({ sort })}
              onOpen={(id) => navigate({ search: (prev) => ({ ...prev, employee: id }) })}
            />
            <Pagination
              page={filters.page}
              pageSize={PAGE_SIZE}
              total={employees.data.total}
              onPage={(page) => navigate({ search: (prev) => ({ ...prev, page }) })}
            />
          </>
        ))}
      {search.employee && (
        <Suspense>
          <ProfileSheet
            employeeId={search.employee}
            onClose={() => navigate({ search: (prev) => ({ ...prev, employee: undefined }) })}
          />
        </Suspense>
      )}
    </>
  )
}
