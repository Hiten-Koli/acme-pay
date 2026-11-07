import createClient from 'openapi-fetch'
import type { components, paths } from '@/api/schema'

/** Response and request shapes, generated from the backend's OpenAPI schema. */
export type Schemas = components['schemas']

/**
 * Typed client for the ACME Pay API.
 *
 * Same origin: `/api` is proxied by Vite in development and rewritten by Vercel in production.
 */
export const api = createClient<paths>({
  baseUrl: globalThis.location?.origin ?? 'http://localhost',
  // Look fetch up per call (not once at import), so tests and instrumentation can wrap it.
  fetch: (request) => globalThis.fetch(request),
})

/** RFC 9457 Problem Details, as returned by every API error. */
export interface Problem {
  title?: string
  detail?: string
  errors?: { field: string; message: string }[]
}

/** An API call that failed, carrying the server's explanation. */
export class ApiError extends Error {
  readonly status: number
  readonly problem: Problem

  constructor(status: number, problem: Problem) {
    super(problem.detail ?? problem.title ?? `Request failed (${status})`)
    this.status = status
    this.problem = problem
  }
}

/**
 * Await an openapi-fetch call and return its data.
 *
 * @throws ApiError with the problem details when the response is not successful.
 */
export async function unwrap<T>(
  request: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
  const { data, error, response } = await request
  if (!response.ok || data === undefined) {
    throw new ApiError(response.status, (error ?? {}) as Problem)
  }
  return data
}
