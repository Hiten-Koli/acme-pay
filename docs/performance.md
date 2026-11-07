# Performance

Measured, not estimated. Dataset: the deterministic seed (10,000 employees, 9,524 active, 62,207 salary-history rows) on local PostgreSQL 17. API timings are 20 warm requests per endpoint through the full FastAPI stack.

## Budgets and results

| Budget (from the plan) | Result |
|---|---|
| API p95 < 200 ms (warm) | **Met.** Slowest endpoint: pulse at 134 ms p95 |
| Initial JS < 250 KB gzipped | **Met.** 154 KB (was 282 KB before optimization, see below) |
| Seed 10k employees < 10 s | **Met.** 3.3–4.2 s end to end |

## API latency (local, warm)

| Endpoint | p50 | p95 | Notes |
|---|---|---|---|
| `GET /api/insights/pulse` | 115 ms | 134 ms | 4 aggregate queries (totals, by country, by department, signals) over all active rows, each with percentiles |
| `GET /api/insights/outliers?band=below` | 36 ms | 39 ms | Peer medians for every role × country, then filter |
| `GET /api/employees?search=patel` | 45 ms | 47 ms | Sequential scan (see below) |
| `GET /api/insights/benchmarks?job_title=…` | 22 ms | 23 ms | |
| `GET /api/employees?country=IN&department=Engineering` | 16 ms | 21 ms | Index scan |
| `GET /api/meta/options` | 18 ms | 19 ms | |

## Query plans (EXPLAIN ANALYZE)

| Query | Execution | Plan |
|---|---|---|
| Directory: country + department filter, sorted, page 1 | 2.8 ms | Index (`ix_employees_country_job_title`, `ix_employees_department`) |
| Peer statistics for one country + job title | 0.24 ms | Index (`ix_employees_country_job_title`) |
| Salary history for one employee | 1.3 ms | Index (`ix_compensation_changes_employee_id`) |
| Directory search (`ILIKE '%term%'` on name, email, code) | 13.9 ms | Sequential scan |

### Why each index exists
- **`(country_code, job_title)`** is the peer group. It serves the profile's pay position, the raise preview and the country filter (leading column).
- **`department`, `status`** are the directory filters HR uses most; every query filters `status = 'active'`.
- **`compensation_changes.employee_id`** serves the salary history in the profile.
- **Unique `email`, `employee_code`** enforce integrity first; they also make exact lookups fast.

## Design choices that keep it fast
- **Aggregate in SQL, not Python.** Percentiles (`percentile_cont`), sums and counts run in PostgreSQL next to the data. Python never loops over 10k rows.
- **One shared set of CTEs** (latest FX rate → active pay in USD → peer medians → compa-ratios), so every insight is computed the same way.
- **Bulk seeding with `COPY`**: 72k rows load in about a second.
- **Server-side paging, sorting and filtering.** The browser receives 25 rows, never 10,000. That makes a virtualized grid unnecessary.
- **Frontend:** TanStack Query caches responses and keeps the previous page on screen while the next one loads. Benchmarks, the profile panel and the AI page are lazy-loaded.

## Bundle-size optimization
A first build was 282 KB gzipped, over budget. The charting library (Recharts) loaded on the first screen only because of the "payroll by country" chart.
1. That chart became plain HTML bars. They are lighter and read as a list by assistive technology.
2. Benchmarks, the profile panel and Ask ACME Pay are lazy-loaded, so Recharts arrives only when a chart is actually shown.

Result: **154 KB** initial, with chart code in a separate chunk.

## What changes at larger scale

| Scale | First thing to change | Why |
|---|---|---|
| ~100k employees | `pg_trgm` GIN index for search | `ILIKE '%term%'` cannot use B-tree indexes; trigram indexes can |
| ~100k | Cache `/insights/pulse` for a short time (or a materialized view refreshed on write) | It aggregates the whole workforce on every request |
| ~1M | Keyset (cursor) pagination | `OFFSET` cost grows with page depth; the API already sorts with a stable id tiebreaker, so the change is local to the repository |
| ~1M | Pre-computed peer statistics table, updated on salary change | Peer medians are recomputed per request today |

None of these are needed at 10k. Adding them now would be complexity without benefit.

## Production notes
Vercel functions run in `sin1` next to Neon in Singapore, so API-to-database round trips stay inside one region. Neon scales to zero, so the first request after idle wakes the database (about a second); the UI shows loading skeletons meanwhile.
