/**
 * Display formatting. The API sends money as exact decimal strings; numbers are only
 * created here, for display, never for arithmetic that is stored.
 */

const LOCALE = 'en-US'
const moneyFormats = new Map<string, Intl.NumberFormat>()

function moneyFormat(currency: string, compact: boolean): Intl.NumberFormat {
  const key = `${currency}:${compact}`
  let format = moneyFormats.get(key)
  if (!format) {
    format = new Intl.NumberFormat(LOCALE, {
      style: 'currency',
      currency,
      notation: compact ? 'compact' : 'standard',
      maximumFractionDigits: compact ? 1 : 0,
    })
    moneyFormats.set(key, format)
  }
  return format
}

/** Format an amount in a currency, e.g. `€85,000` or, compact, `$752.9M`. */
export function formatMoney(
  amount: string | number,
  currency: string,
  { compact = false }: { compact?: boolean } = {},
): string {
  return moneyFormat(currency, compact).format(Number(amount))
}

/** Format a whole number with thousands separators. */
export function formatCount(value: number): string {
  return value.toLocaleString(LOCALE)
}

/** Format an ISO date (`2025-01-15`) as `15 Jan 2025`, independent of the viewer's time zone. */
export function formatDate(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number)
  return new Date(Date.UTC(year ?? 0, (month ?? 1) - 1, day ?? 1)).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  })
}

/** Format a percentage given in percent units, e.g. `"20.00"` → `+20.0%`. */
export function formatChange(percent: string | number): string {
  const value = Number(percent)
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`
}

/** Today's date as an ISO string in the viewer's calendar. */
export function todayIso(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}
