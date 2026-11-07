import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { renderWithQuery } from '@/test/render'
import { AskPage } from './AskPage'

function mockAssistant({ enabled }: { enabled: boolean }) {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const url = typeof input === 'object' && 'url' in input ? input.url : String(input)
    if (url.endsWith('/api/assistant/status')) return Response.json({ enabled })
    return Response.json({
      answer: 'The US pays Data Scientists the most; India the least.',
      evidence: [
        {
          tool: 'org_pay_summary',
          arguments: {},
          result: {
            rate_date: '2026-10-01',
            headcount: 9524,
            payroll_usd: '752897479.98',
            median_salary_usd: '74393.50',
            below_band: 419,
            above_band: 726,
            countries: [],
            departments: [],
            signals: [],
          },
        },
      ],
    })
  })
}

describe('AskPage', () => {
  it('explains how to enable the analyst when no model is configured', async () => {
    mockAssistant({ enabled: false })

    renderWithQuery(<AskPage />)

    expect(await screen.findByText('The AI analyst is not configured')).toBeInTheDocument()
  })

  it('shows the answer together with the data it is based on', async () => {
    mockAssistant({ enabled: true })
    renderWithQuery(<AskPage />)

    await userEvent.click(
      await screen.findByRole('button', { name: /How many people are paid below/ }),
    )

    expect(await screen.findByText(/US pays Data Scientists the most/)).toBeInTheDocument()
    expect(screen.getByText('Organization pay summary')).toBeInTheDocument()
    expect(screen.getByText('9,524')).toBeInTheDocument()
  })
})
