import { ErrorState, LoadingBlock } from '@/components/QueryStates'
import { Badge } from '@/components/ui/badge'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { formatDate } from '@/lib/format'
import { useEmployee } from './api'
import { ChangeSalaryForm } from './ChangeSalaryForm'
import { EditProfileDialog } from './EditProfileDialog'
import { PayPositionCard } from './PayPositionCard'
import { SalaryHistory } from './SalaryHistory'
import { TerminateDialog } from './TerminateDialog'

/** One employee: pay position, a previewed raise, history and lifecycle actions. */
export function ProfileSheet({ employeeId, onClose }: { employeeId: string; onClose: () => void }) {
  const employee = useEmployee(employeeId)
  const person = employee.data
  const active = person?.status === 'active'

  return (
    <Sheet open onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full gap-0 overflow-y-auto data-[side=right]:sm:max-w-2xl">
        <SheetHeader className="border-b">
          <SheetTitle className="text-xl">
            {person ? `${person.first_name} ${person.last_name}` : 'Employee'}
          </SheetTitle>
          <SheetDescription>
            {person && `${person.job_title} · ${person.department} · ${person.country_code}`}
          </SheetDescription>
          {person && (
            <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <Badge variant="outline">{person.employee_code}</Badge>
              <span>Hired {formatDate(person.hire_date)}</span>
              {person.terminated_on && (
                <Badge variant="secondary">Left {formatDate(person.terminated_on)}</Badge>
              )}
              <span className="flex-1" />
              {active && <EditProfileDialog employee={person} />}
              {active && <TerminateDialog employee={person} />}
            </div>
          )}
        </SheetHeader>
        <div className="flex flex-col gap-6 p-4">
          {employee.isPending && <LoadingBlock />}
          {employee.isError && <ErrorState error={employee.error} />}
          {person && (
            <>
              <PayPositionCard employee={person} />
              {active && <ChangeSalaryForm employee={person} />}
              <SalaryHistory employee={person} />
            </>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}
