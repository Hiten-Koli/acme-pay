import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import App from './App'
import { renderWithQuery } from './test/render'

describe('App', () => {
  it('opens on Pay Pulse with the main navigation', async () => {
    vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise(() => {}))

    renderWithQuery(<App />)

    expect(await screen.findByRole('heading', { level: 1, name: 'Pay Pulse' })).toBeInTheDocument()
    const nav = screen.getByRole('navigation', { name: 'Main' })
    expect(nav).toHaveTextContent('People')
    expect(nav).toHaveTextContent('Benchmarks')
  })
})
