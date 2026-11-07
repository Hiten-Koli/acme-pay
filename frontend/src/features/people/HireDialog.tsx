import { UserPlus } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { toast } from 'sonner'
import { FormField, fieldErrors } from '@/components/FormField'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useOptions } from '@/features/meta/useOptions'
import { todayIso } from '@/lib/format'
import { useHireEmployee } from './api'

const TEXT_FIELDS = [
  ['first_name', 'First name'],
  ['last_name', 'Last name'],
  ['email', 'Work email'],
  ['job_title', 'Job title'],
  ['department', 'Department'],
] as const

/** Add a new employee with their starting salary. */
export function HireDialog({ onHired }: { onHired: (employeeId: string) => void }) {
  const [open, setOpen] = useState(false)
  const [country, setCountry] = useState('')
  const options = useOptions()
  const hire = useHireEmployee()
  const errors = fieldErrors(hire.error)
  const currency = options.data?.countries.find((c) => c.code === country)?.currency

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const value = (name: string) => String(form.get(name) ?? '')
    try {
      const employee = await hire.mutateAsync({
        first_name: value('first_name'),
        last_name: value('last_name'),
        email: value('email'),
        job_title: value('job_title'),
        department: value('department'),
        country_code: country,
        salary: value('salary'),
        hire_date: value('hire_date'),
      })
      toast.success(
        `${employee.first_name} ${employee.last_name} added as ${employee.employee_code}`,
      )
      setOpen(false)
      hire.reset()
      onHired(employee.id)
    } catch {
      // Field and rule errors are shown inline from hire.error.
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <UserPlus />
          Add employee
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add employee</DialogTitle>
          <DialogDescription>
            Their starting salary becomes the first entry in their pay history.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={submit} className="grid gap-3 sm:grid-cols-2">
          {TEXT_FIELDS.map(([name, label]) => (
            <FormField key={name} id={`hire-${name}`} label={label} error={errors[name]}>
              <Input
                id={`hire-${name}`}
                name={name}
                type={name === 'email' ? 'email' : 'text'}
                list={
                  name === 'job_title' || name === 'department' ? `hire-${name}-list` : undefined
                }
                required
              />
            </FormField>
          ))}
          <datalist id="hire-job_title-list">
            {options.data?.job_titles.map((title) => (
              <option key={title} value={title} />
            ))}
          </datalist>
          <datalist id="hire-department-list">
            {options.data?.departments.map((name) => (
              <option key={name} value={name} />
            ))}
          </datalist>
          <FormField id="hire-country" label="Country" error={errors.country_code}>
            <Select value={country} onValueChange={setCountry} required>
              <SelectTrigger id="hire-country" className="w-full">
                <SelectValue placeholder="Choose a country" />
              </SelectTrigger>
              <SelectContent>
                {options.data?.countries.map((c) => (
                  <SelectItem key={c.code} value={c.code}>
                    {c.name} ({c.currency})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>
          <FormField
            id="hire-salary"
            label={`Annual salary${currency ? ` (${currency})` : ''}`}
            error={errors.salary}
          >
            <Input
              id="hire-salary"
              name="salary"
              inputMode="decimal"
              placeholder="85000.00"
              pattern="\d+(\.\d{1,2})?"
              required
            />
          </FormField>
          <FormField id="hire-hire_date" label="Start date" error={errors.hire_date}>
            <Input
              id="hire-hire_date"
              name="hire_date"
              type="date"
              defaultValue={todayIso()}
              required
            />
          </FormField>
          {hire.error && !Object.keys(errors).length && (
            <p role="alert" className="text-sm text-destructive sm:col-span-2">
              {hire.error.message}
            </p>
          )}
          <DialogFooter className="sm:col-span-2">
            <Button type="submit" disabled={hire.isPending || !country}>
              {hire.isPending ? 'Adding…' : 'Add employee'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
