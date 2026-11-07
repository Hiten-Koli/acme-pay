import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { BandBadge } from './BandBadge'

describe('BandBadge', () => {
  it.each([
    ['below', 'Below band'],
    ['within', 'Within band'],
    ['above', 'Above band'],
  ] as const)('labels the %s state in words, not color alone', (band, label) => {
    render(<BandBadge band={band} />)

    expect(screen.getByText(label)).toBeInTheDocument()
  })
})
