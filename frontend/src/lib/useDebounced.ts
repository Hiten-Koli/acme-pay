import { useEffect, useState } from 'react'

const DEFAULT_DELAY_MS = 300

/** Return `value` once it has stopped changing for `delayMs` (e.g. for search-as-you-type). */
export function useDebounced<T>(value: T, delayMs = DEFAULT_DELAY_MS): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(timer)
  }, [value, delayMs])
  return debounced
}
