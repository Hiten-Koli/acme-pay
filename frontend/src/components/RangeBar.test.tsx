import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { RangeBar, toPercent } from './RangeBar'

describe('toPercent', () => {
  it('places values linearly on the scale', () => {
    expect(toPercent(150, [100, 200])).toBe(50)
  })

  it('clamps values outside the scale to its ends', () => {
    expect(toPercent(50, [100, 200])).toBe(0)
    expect(toPercent(250, [100, 200])).toBe(100)
  })
})

describe('RangeBar', () => {
  it('is described for assistive technology and marks the individual value', () => {
    render(
      <RangeBar
        domain={[0, 200]}
        p25={50}
        median={100}
        p75={150}
        marker={150}
        label="Salary against peers"
      />,
    )

    expect(screen.getByRole('img', { name: 'Salary against peers' })).toBeInTheDocument()
    expect(screen.getByTestId('range-marker')).toHaveStyle({ left: '75%' })
  })
})
