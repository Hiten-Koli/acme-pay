import { describe, expect, it } from 'vitest'
import { formatChange, formatDate, formatMoney } from './format'

describe('formatMoney', () => {
  it('formats exact decimal strings in the given currency without cents', () => {
    expect(formatMoney('85000.00', 'EUR')).toBe('€85,000')
    expect(formatMoney('2400000.00', 'INR')).toBe('₹2,400,000')
  })

  it('formats large figures compactly for headlines', () => {
    expect(formatMoney('752897479.98', 'USD', { compact: true })).toBe('$752.9M')
  })
})

describe('formatDate', () => {
  it('shows ISO dates as day month year regardless of time zone', () => {
    expect(formatDate('2025-01-15')).toBe('15 Jan 2025')
  })
})

describe('formatChange', () => {
  it('signs positive changes', () => {
    expect(formatChange('20.00')).toBe('+20.0%')
    expect(formatChange('-3.5')).toBe('-3.5%')
  })
})
