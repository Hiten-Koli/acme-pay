import { Pencil } from 'lucide-react'
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
import type { Schemas } from '@/lib/api'
import { useUpdateEmployee } from './api'

const FIELDS = [
  ['first_name', 'First name'],
  ['last_name', 'Last name'],
  ['email', 'Work email'],
  ['job_title', 'Job title'],
  ['department', 'Department'],
] as const

/** Edit profile details. Salary is changed through the salary form, so it stays in the history. */
export function EditProfileDialog({ employee }: { employee: Schemas['EmployeeRead'] }) {
  const [open, setOpen] = useState(false)
  const update = useUpdateEmployee(employee.id)
  const errors = fieldErrors(update.error)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const changes = Object.fromEntries(
      FIELDS.map(([name]) => [name, String(form.get(name))]).filter(
        ([name, value]) => value !== employee[name as keyof typeof employee],
      ),
    )
    try {
      await update.mutateAsync(changes)
      toast.success('Profile updated')
      setOpen(false)
    } catch {
      // Shown inline from update.error.
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Pencil />
          Edit
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit profile</DialogTitle>
          <DialogDescription>
            Salary changes are made from the profile so they are recorded.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={submit} className="grid gap-3 sm:grid-cols-2">
          {FIELDS.map(([name, label]) => (
            <FormField key={name} id={`edit-${name}`} label={label} error={errors[name]}>
              <Input id={`edit-${name}`} name={name} defaultValue={employee[name]} required />
            </FormField>
          ))}
          {update.error && !Object.keys(errors).length && (
            <p role="alert" className="text-sm text-destructive sm:col-span-2">
              {update.error.message}
            </p>
          )}
          <DialogFooter className="sm:col-span-2">
            <Button type="submit" disabled={update.isPending}>
              {update.isPending ? 'Saving…' : 'Save'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
