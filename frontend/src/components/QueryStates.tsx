import { AlertCircle, Inbox } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

/** Placeholder blocks while data loads. */
export function LoadingBlock({ className }: { className?: string }) {
  return <Skeleton className={cn('h-40 w-full', className)} />
}

/** A failed request, with a retry. */
export function ErrorState({ error, onRetry }: { error: Error; onRetry?: () => void }) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center gap-2 rounded-lg border border-dashed p-8 text-center"
    >
      <AlertCircle aria-hidden className="size-5 text-destructive" />
      <p className="text-sm font-medium">Something went wrong</p>
      <p className="text-sm text-muted-foreground">{error.message}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  )
}

/** Nothing to show yet. */
export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed p-8 text-center">
      <Inbox aria-hidden className="size-5 text-muted-foreground" />
      <p className="text-sm font-medium">{title}</p>
      {hint && <p className="text-sm text-muted-foreground">{hint}</p>}
    </div>
  )
}
