/** Health summary returned by `GET /api/health`. */
export interface Health {
  status: 'ok' | 'degraded'
  database: 'ok' | 'unavailable'
}

/**
 * Fetch the API health summary.
 *
 * A 503 still carries a valid health body (the API is up, the database is not),
 * so only other non-OK statuses are treated as errors.
 *
 * @throws Error when the API is unreachable or responds unexpectedly.
 */
export async function fetchHealth(): Promise<Health> {
  const response = await fetch('/api/health')
  if (!response.ok && response.status !== 503) {
    throw new Error(`Health check failed with HTTP ${response.status}`)
  }
  return (await response.json()) as Health
}
