import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react'
import type { PeopleSearch } from '@/app/router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { Schemas } from '@/lib/api'
import { formatDate, formatMoney } from '@/lib/format'
import { cn } from '@/lib/utils'

type Sort = NonNullable<PeopleSearch['sort']>

function SortHeader({
  label,
  field,
  sort,
  onSort,
  align = 'left',
  className,
}: {
  label: string
  field: 'name' | 'salary' | 'hire_date'
  sort: Sort
  onSort: (sort: Sort) => void
  align?: 'left' | 'right'
  className?: string
}) {
  const active = sort.replace('-', '') === field
  const descending = sort.startsWith('-')
  const Icon = !active ? ArrowUpDown : descending ? ArrowDown : ArrowUp
  const next = (active && !descending ? `-${field}` : field) as Sort
  return (
    <TableHead
      className={cn(align === 'right' && 'text-right', className)}
      aria-sort={active ? (descending ? 'descending' : 'ascending') : 'none'}
    >
      <Button variant="ghost" size="sm" className="-mx-2" onClick={() => onSort(next)}>
        {label}
        <Icon aria-hidden className="size-3.5" />
      </Button>
    </TableHead>
  )
}

/** One page of employees. Rows open the profile. */
export function PeopleTable({
  employees,
  sort,
  onSort,
  onOpen,
}: {
  employees: Schemas['EmployeeRead'][]
  sort: Sort
  onSort: (sort: Sort) => void
  onOpen: (employeeId: string) => void
}) {
  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <SortHeader label="Name" field="name" sort={sort} onSort={onSort} />
            <TableHead className="hidden md:table-cell">Role</TableHead>
            <TableHead className="hidden sm:table-cell">Country</TableHead>
            <SortHeader label="Salary" field="salary" sort={sort} onSort={onSort} align="right" />
            <SortHeader
              label="Hired"
              field="hire_date"
              sort={sort}
              onSort={onSort}
              className="hidden lg:table-cell"
            />
          </TableRow>
        </TableHeader>
        <TableBody>
          {employees.map((employee) => (
            <TableRow
              key={employee.id}
              className="cursor-pointer"
              onClick={() => onOpen(employee.id)}
            >
              <TableCell>
                <button
                  type="button"
                  className="text-left font-medium hover:underline"
                  onClick={(event) => {
                    event.stopPropagation()
                    onOpen(employee.id)
                  }}
                >
                  {employee.first_name} {employee.last_name}
                </button>
                <span className="block text-xs text-muted-foreground">
                  {/* Small screens: role and country move under the name to keep salary visible. */}
                  <span className="md:hidden">{employee.job_title} · </span>
                  <span className="sm:hidden">{employee.country_code} · </span>
                  {employee.employee_code}
                  {employee.status === 'terminated' && (
                    <Badge variant="secondary" className="ml-2">
                      Left
                    </Badge>
                  )}
                </span>
              </TableCell>
              <TableCell className="hidden md:table-cell">
                {employee.job_title}
                <span className="block text-xs text-muted-foreground">{employee.department}</span>
              </TableCell>
              <TableCell className="hidden sm:table-cell">{employee.country_code}</TableCell>
              <TableCell className="text-right tabular-nums">
                {formatMoney(employee.salary, employee.currency)}
              </TableCell>
              <TableCell className="hidden tabular-nums lg:table-cell">
                {formatDate(employee.hire_date)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
