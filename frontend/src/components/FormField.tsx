import type { ReactNode } from 'react'
import { Label } from '@/components/ui/label'

/** A labelled form control with an optional field error from the API. */
export function FormField({
  id,
  label,
  error,
  children,
}: {
  id: string
  label: string
  error?: string
  children: ReactNode
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      {children}
      {error && (
        <p id={`${id}-error`} className="text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}

/** Map API field errors (from RFC 9457 problem details) by field name. */
export function fieldErrors(error: unknown): Record<string, string> {
  const problem = (error as { problem?: { errors?: { field: string; message: string }[] } })
    ?.problem
  return Object.fromEntries((problem?.errors ?? []).map((e) => [e.field, e.message]))
}
