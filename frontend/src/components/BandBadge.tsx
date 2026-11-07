import { ArrowDown, ArrowUp, Check } from 'lucide-react'
import type { Schemas } from '@/lib/api'
import { cn } from '@/lib/utils'

type Band = Schemas['BandPosition']

const BANDS: Record<Band, { label: string; icon: typeof Check; className: string }> = {
  below: { label: 'Below band', icon: ArrowDown, className: 'text-status-warning' },
  within: { label: 'Within band', icon: Check, className: 'text-status-good' },
  above: { label: 'Above band', icon: ArrowUp, className: 'text-status-serious' },
}

/** Pay band state: always icon + label, never color alone. */
export function BandBadge({ band, className }: { band: Band; className?: string }) {
  const { label, icon: Icon, className: tone } = BANDS[band]
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 whitespace-nowrap rounded-full border px-2 py-0.5 text-xs font-medium text-foreground',
        className,
      )}
    >
      <Icon aria-hidden className={cn('size-3.5', tone)} />
      {label}
    </span>
  )
}
