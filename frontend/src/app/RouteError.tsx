import type { ErrorComponentProps } from '@tanstack/react-router'
import { ErrorState } from '@/components/QueryStates'

/** Shown instead of a blank or default screen if a page fails to render. */
export function RouteError({ error, reset }: ErrorComponentProps) {
  return (
    <main className="mx-auto max-w-xl p-8">
      <ErrorState
        error={error instanceof Error ? error : new Error(String(error))}
        onRetry={reset}
      />
    </main>
  )
}
