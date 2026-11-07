import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { vi } from 'vitest'
import { TooltipProvider } from '@/components/ui/tooltip'

/** Render with the app's providers and a fresh, non-retrying query client (isolated, fast). */
export function renderWithQuery(ui: ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <TooltipProvider>{ui}</TooltipProvider>
    </QueryClientProvider>,
  )
}

/**
 * Answer API calls from a table of path → JSON body (anything else is a 404),
 * so components are tested against realistic responses without a server.
 */
export function mockApi(responses: Record<string, unknown>) {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    // Duck-typed: jsdom and Node each have their own Request class, so instanceof is unreliable.
    const raw = typeof input === 'object' && 'url' in input ? input.url : String(input)
    const url = new URL(raw, 'http://localhost')
    const body = responses[url.pathname]
    return body === undefined
      ? Response.json({ title: 'Not Found', status: 404 }, { status: 404 })
      : Response.json(body)
  })
}
