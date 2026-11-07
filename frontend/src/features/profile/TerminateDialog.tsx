import { UserMinus } from 'lucide-react'
import { type FormEvent, useState } from 'react'
import { toast } from 'sonner'
import { FormField } from '@/components/FormField'
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
import { todayIso } from '@/lib/format'
import { useTerminateEmployee } from './api'

/** Record a leaver. Their record and pay history are kept. */
export function TerminateDialog({ employee }: { employee: Schemas['EmployeeRead'] }) {
  const [open, setOpen] = useState(false)
  const terminate = useTerminateEmployee(employee.id)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    try {
      await terminate.mutateAsync({ terminated_on: String(form.get('terminated_on')) })
      toast.success(`${employee.first_name} ${employee.last_name} marked as left`)
      setOpen(false)
    } catch {
      // Shown inline from terminate.error.
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <UserMinus />
          Mark as left
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Mark {employee.first_name} {employee.last_name} as left?
          </DialogTitle>
          <DialogDescription>
            They will no longer count in pay insights. Their record and salary history are kept.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={submit} className="flex flex-col gap-3">
          <FormField id="terminated-on" label="Last day">
            <Input
              id="terminated-on"
              name="terminated_on"
              type="date"
              defaultValue={todayIso()}
              required
            />
          </FormField>
          {terminate.error && (
            <p role="alert" className="text-sm text-destructive">
              {terminate.error.message}
            </p>
          )}
          <DialogFooter>
            <Button type="submit" variant="destructive" disabled={terminate.isPending}>
              {terminate.isPending ? 'Saving…' : 'Mark as left'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
