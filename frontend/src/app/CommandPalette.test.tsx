import {
  createMemoryHistory,
  createRootRoute,
  createRouter,
  RouterProvider,
} from '@tanstack/react-router'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { mockApi, renderWithQuery } from '@/test/render'
import { CommandPalette } from './CommandPalette'

const PATEL = {
  id: '6f1c0a52-0000-4000-8000-000000000001',
  employee_code: 'EMP-009533',
  first_name: 'Aarav',
  last_name: 'Patel',
  email: 'aarav.patel@acme.example',
  job_title: 'Software Engineer',
  department: 'Engineering',
  country_code: 'DE',
  currency: 'EUR',
  salary: '93500.00',
  hire_date: '2020-04-03',
  status: 'active',
  terminated_on: null,
}

function renderPalette() {
  const router = createRouter({
    routeTree: createRootRoute({ component: CommandPalette }),
    history: createMemoryHistory(),
  })
  renderWithQuery(<RouterProvider router={router} />)
}

describe('CommandPalette', () => {
  it('opens and finds people by name', async () => {
    mockApi({ '/api/employees': { items: [PATEL], total: 1, page: 1, page_size: 6 } })
    renderPalette()

    await userEvent.click(await screen.findByRole('button', { name: /Search/ }))
    await userEvent.type(screen.getByPlaceholderText('Search people or pages…'), 'patel')

    expect(await screen.findByText('Aarav Patel')).toBeInTheDocument()
  })

  it('offers pages that match what was typed', async () => {
    mockApi({})
    renderPalette()

    await userEvent.click(await screen.findByRole('button', { name: /Search/ }))
    await userEvent.type(screen.getByPlaceholderText('Search people or pages…'), 'bench')

    expect(await screen.findByText('Benchmarks')).toBeInTheDocument()
  })
})
