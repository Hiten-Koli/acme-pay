import { cn } from '@/lib/utils'

export interface RangeBarProps {
  /** Lower and upper ends of the visible scale. */
  domain: [number, number]
  /** Interquartile range (p25–p75), drawn as the band. */
  p25: number
  p75: number
  median: number
  /** Optional individual value, e.g. one employee's salary. */
  marker?: number
  /** Accessible description of the whole bar. */
  label: string
  className?: string
}

/** Position of `value` on the scale, as a clamped percentage. */
export function toPercent(value: number, [low, high]: [number, number]): number {
  if (high <= low) return 50
  return Math.min(100, Math.max(0, ((value - low) / (high - low)) * 100))
}

/**
 * A horizontal pay range: the p25–p75 band, a median tick and an optional marker.
 * Used for one employee against peers and for one role across countries.
 */
export function RangeBar({ domain, p25, p75, median, marker, label, className }: RangeBarProps) {
  const start = toPercent(p25, domain)
  const end = toPercent(p75, domain)
  return (
    <div role="img" aria-label={label} className={cn('relative h-6', className)}>
      <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-border" />
      <div
        className="absolute top-1/2 h-3 -translate-y-1/2 rounded-sm bg-chart-band"
        style={{ left: `${start}%`, width: `${Math.max(end - start, 0.5)}%` }}
      />
      <div
        className="absolute top-1/2 h-5 w-0.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-foreground"
        style={{ left: `${toPercent(median, domain)}%` }}
      />
      {marker !== undefined && (
        <div
          data-testid="range-marker"
          className="absolute top-1/2 size-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-chart-1 ring-2 ring-background"
          style={{ left: `${toPercent(marker, domain)}%` }}
        />
      )}
    </div>
  )
}
