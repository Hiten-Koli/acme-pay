import { type FormEvent, useState } from 'react'
import { toast } from 'sonner'
import { BandBadge } from '@/components/BandBadge'
import { FormField, fieldErrors } from '@/components/FormField'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { Schemas } from '@/lib/api'
import { formatChange, formatMoney, todayIso } from '@/lib/format'
import { useDebounced } from '@/lib/useDebounced'
import { useChangeSalary, useSalaryPreview } from './api'

const REASONS: { value: Schemas['CompensationReason']; label: string }[] = [
  { value: 'merit', label: 'Merit increase' },
  { value: 'promotion', label: 'Promotion' },
  { value: 'market_adjustment', label: 'Market adjustment' },
  { value: 'correction', label: 'Correction' },
]
const AMOUNT = /^\d+(\.\d{1,2})?$/

/** Propose a new salary, see its effect before saving, then record it. */
export function ChangeSalaryForm({ employee }: { employee: Schemas['EmployeeRead'] }) {
  const [amount, setAmount] = useState('')
  const [reason, setReason] = useState<Schemas['CompensationReason']>('merit')
  const debounced = useDebounced(amount.trim())
  const valid = AMOUNT.test(debounced) && Number(debounced) > 0
  const preview = useSalaryPreview(employee.id, valid ? debounced : undefined)
  const change = useChangeSalary(employee.id)
  const errors = fieldErrors(change.error)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    try {
      await change.mutateAsync({
        new_salary: amount.trim(),
        effective_date: String(form.get('effective_date')),
        reason,
      })
      toast.success('Salary updated and added to the history')
      setAmount('')
      change.reset()
    } catch {
      // Shown inline from change.error.
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change salary</CardTitle>
        <CardDescription>See the effect before you save it.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={submit} className="grid gap-3 sm:grid-cols-3">
          <FormField
            id="new-salary"
            label={`New salary (${employee.currency})`}
            error={errors.new_salary}
          >
            <Input
              id="new-salary"
              inputMode="decimal"
              placeholder={employee.salary}
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              required
            />
          </FormField>
          <FormField id="effective-date" label="Effective" error={errors.effective_date}>
            <Input
              id="effective-date"
              name="effective_date"
              type="date"
              defaultValue={todayIso()}
              required
            />
          </FormField>
          <FormField id="reason" label="Reason">
            <Select
              value={reason}
              onValueChange={(value) => setReason(value as Schemas['CompensationReason'])}
            >
              <SelectTrigger id="reason" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {REASONS.map((r) => (
                  <SelectItem key={r.value} value={r.value}>
                    {r.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>

          {preview.data && (
            <output
              aria-live="polite"
              className="grid gap-2 rounded-lg bg-muted p-3 text-sm sm:col-span-3 sm:grid-cols-[1fr_1fr_auto]"
            >
              <span>
                <span className="block text-xs text-muted-foreground">Change</span>
                <span className="font-medium tabular-nums">
                  {formatChange(preview.data.change_percent)} (
                  {formatMoney(preview.data.change_amount, employee.currency)})
                </span>
              </span>
              <span>
                <span className="block text-xs text-muted-foreground">Annual cost</span>
                <span className="font-medium tabular-nums">
                  {preview.data.annual_cost_change_usd
                    ? formatMoney(preview.data.annual_cost_change_usd, 'USD')
                    : '—'}
                </span>
              </span>
              <span>
                <span className="block text-xs text-muted-foreground">
                  New position ({preview.data.proposed.compa_ratio} × median)
                </span>
                {preview.data.proposed.band && <BandBadge band={preview.data.proposed.band} />}
              </span>
            </output>
          )}
          {change.error && !Object.keys(errors).length && (
            <p role="alert" className="text-sm text-destructive sm:col-span-3">
              {change.error.message}
            </p>
          )}
          <div className="sm:col-span-3">
            <Button type="submit" disabled={!valid || change.isPending}>
              {change.isPending ? 'Saving…' : 'Save salary change'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
