# 6. Money and currency representation

- **Status:** Accepted
- **Date:** 2026-11-07

## Context
Employees are paid in their local currency in many countries. HR must compare pay across countries, and every figure must reconcile exactly. Floating-point arithmetic cannot represent most decimal amounts (`0.1 + 0.2 != 0.3`), and mixing currencies silently produces meaningless numbers.

## Decision
- A domain **value object** `Money(amount: Decimal, currency: CurrencyCode)`. It is immutable and holds an ISO 4217 code. Adding or comparing two different currencies **raises an error** instead of producing a number.
- Stored as `NUMERIC(14,2)` plus a `CHAR(3)` currency code. Sent over the API as a **decimal string** plus currency, so precision is never lost in JSON numbers.
- Cross-currency figures convert through an `fx_rates` table keyed by **(currency, effective date)**. Every converted figure carries the rate date, and the UI displays it.
- Rounding happens only at presentation and storage boundaries, using banker's rounding (`ROUND_HALF_EVEN`).
- Salaries are **annual base** amounts.

## Alternatives considered
| Option | Why not |
|---|---|
| `float` | Inexact, so totals don't reconcile. |
| Integer minor units (cents) | Exact, but currencies differ in minor units (JPY has 0 decimal places, KWD has 3), and every display and API boundary needs conversion. `Decimal` + `NUMERIC` is equally exact and clearer. |
| Live FX API | Numbers would change between page loads and be impossible to audit. Adds an external dependency. |
| Store a USD copy per employee | Duplicates data, which goes stale when rates change. |

## Consequences
- Currency bugs become type errors and failing tests instead of wrong reports.
- Property-based tests (Hypothesis) prove the invariants: addition is exact, conversion round-trips, and different currencies never mix.
- FX rates are static seed data for this assessment. Updating them is a data change, not a code change.
