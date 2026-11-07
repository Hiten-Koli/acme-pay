import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiStatus } from './ApiStatus'

function renderWithQueryClient() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <ApiStatus />
    </QueryClientProvider>,
  )
}

function mockHealthResponse(body: unknown, status: number) {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(Response.json(body, { status }))
}

describe('ApiStatus', () => {
  it('reports all systems operational when the API and database are healthy', async () => {
    mockHealthResponse({ status: 'ok', database: 'ok' }, 200)

    renderWithQueryClient()

    expect(await screen.findByText('All systems operational')).toBeInTheDocument()
  })

  it('reports the database as unavailable when the API is degraded', async () => {
    mockHealthResponse({ status: 'degraded', database: 'unavailable' }, 503)

    renderWithQueryClient()

    expect(await screen.findByText('Database unavailable')).toBeInTheDocument()
  })

  it('reports the API as unreachable when the request fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'))

    renderWithQueryClient()

    expect(await screen.findByText('API unreachable')).toBeInTheDocument()
  })
})
