# 9. Refinements made during delivery

- **Status:** Accepted
- **Date:** 2026-11-07
- **Supersedes:** parts of [0004](0004-hosting-vercel-github-actions.md) and [0005](0005-frontend-react-vite-tanstack-shadcn.md); the "outliers" definition in the plan

## Context
The plan was written before any code. Building and measuring the product showed where it could be simpler, or where an assumption was wrong. The engineer's standing direction during delivery was to keep things simple. Each change below makes the system simpler, more correct, or both.

## Decisions

| Area | Planned | Delivered | Why |
|---|---|---|---|
| **"Outside band"** | Outside the 10th–90th percentile of the peer group | Compa-ratio outside **0.80–1.20** of the peer median | By definition, about 20% of every group falls outside its own 10th–90th percentile, so that count carries no information. ±20% of the peer median is standard compensation practice and finds real outliers. |
| **Directory** | Virtualized grid (TanStack Table + Virtual) | Server-paged table (25 rows), sorting and filters in the URL | The server returns 25 rows, so there is nothing to virtualize. Shareable URLs matter more to HR than infinite scroll. |
| **Pagination** | Cursor (keyset) | Offset with total count | Fine at 10k (16 ms). Ordering already has a stable id tiebreaker, so moving to keyset later is a local change ([performance.md](../performance.md)). |
| **Country overview** | World map (d3-geo) | Ranked HTML bars | Ten countries read more precisely as bars than as map areas. Bars also kept the first screen inside the bundle budget. |
| **API client** | `@hey-api/openapi-ts` (types, hooks, Zod) | `openapi-typescript` types + `openapi-fetch` | Same guarantee (the frontend fails to compile on contract drift) with less generated code. CI still blocks drift. |
| **Preview environments** | Neon branch + Vercel preview per PR | Not built | Single developer, trunk-based. CI runs every check against a real PostgreSQL on every push, which covers what previews would. |
| **E2E tests** | Playwright + axe in CI | Component tests (Vitest + Testing Library) plus a scripted browser review of every screen during development | Visual review caught real issues: flag emoji rendering as letters on Windows, a clipped mobile table, a cramped side panel. A CI browser suite is the next step if the UI grows. |
| **Observability** | Sentry | Structured logs only | No production traffic to observe in an assessment. The error handling (problem details, logged provider failures) is where Sentry would plug in. |
| **Alembic** | Runtime dependency | Dev dependency | Migrations run from CI and locally, never inside the deployed function. Keeps the function bundle small. |
| **Frontend lint scope** | Everything | Excludes `src/components/ui` (shadcn) and `src/api` (generated) | Vendored and generated code is not ours to restyle. Our code is linted strictly. |

## Consequences
- Fewer moving parts. Every remaining one is exercised by tests or by CI.
- The plan ([PLAN.md](../PLAN.md)) is kept unchanged as the record of intent. This ADR is the record of what changed and why.
