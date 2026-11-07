import {
  createMemoryHistory,
  createRootRoute,
  createRouter,
  RouterProvider,
} from '@tanstack/react-router'
import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { Schemas } from '@/lib/api'
import { mockApi, renderWithQuery } from '@/test/render'
import { PulsePage } from './PulsePage'

const PULSE: Schemas['Pulse'] = {
  rate_date: '2026-10-01',
  headcount: 9524,
  payroll_usd: '752897479.98',
  median_salary_usd: '74393.50',
  below_band: 419,
  above_band: 726,
  countries: [
    {
      country_code: 'US',
      currency: 'USD',
      headcount: 2400,
      payroll_usd: '300000000.00',
      median_salary_usd: '120000.00',
    },
  ],
  departments: [
    {
      department: 'Engineering',
      headcount: 5000,
      payroll_usd: '500000000.00',
      median_salary_usd: '100000.00',
    },
  ],
  signals: [
    {
      country_code: 'IN',
      job_title: 'Data Scientist',
      currency: 'INR',
      headcount: 77,
      below_band: 25,
      median_salary: '2497800.00',
    },
  ],
}

function renderPage() {
  const router = createRouter({
    routeTree: createRootRoute({ component: PulsePage }),
    history: createMemoryHistory(),
  })
  renderWithQuery(<RouterProvider router={router} />)
}

describe('PulsePage', () => {
  it('shows the headline figures', async () => {
    mockApi({ '/api/insights/pulse': PULSE })

    renderPage()

    expect(await screen.findByText('9,524')).toBeInTheDocument()
    expect(screen.getByText('$752.9M')).toBeInTheDocument()
    expect(screen.getByText('1,145')).toBeInTheDocument()
    expect(screen.getByText('419 below · 726 above')).toBeInTheDocument()
  })

  it('points HR to the groups paid below band', async () => {
    mockApi({ '/api/insights/pulse': PULSE })

    renderPage()

    const signal = await screen.findByRole('link', { name: /25 of 77 Data Scientists/ })
    expect(signal).toHaveAttribute('href', expect.stringContaining('/benchmarks'))
  })

  it('explains the failure when the API is unavailable', async () => {
    mockApi({})

    renderPage()

    expect(await screen.findByText('Something went wrong')).toBeInTheDocument()
  })
})
