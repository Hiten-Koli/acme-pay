# 3. Database: PostgreSQL, hosted on Neon

- **Status:** Accepted
- **Date:** 2026-11-07

## Context
The brief allows any relational database "like SQLite". Our core questions are about **distributions**: medians, percentiles, and outliers per role and country. Money must be exact. The deployed app must keep the HR manager's edits, and the hosting must be free.

## Decision
Use **PostgreSQL 17** everywhere: Docker Compose locally, a service container in CI, and **Neon** (serverless Postgres, free tier) in production.

- `percentile_cont` computes medians and percentiles in SQL, next to the data.
- `NUMERIC(14,2)` stores money exactly.
- Neon's **copy-on-write branching** gives each pull request an isolated, seeded database for preview environments.
- Production connects through Neon's pooled endpoint, which suits serverless functions.

## Alternatives considered
| Option | Why not |
|---|---|
| SQLite | No built-in percentile functions, single writer, and free hosts provide only ephemeral disks, so edits would vanish on redeploy. Using SQLite locally and Postgres in production breaks dev/prod parity. |
| Supabase | Free projects pause after 7 days of inactivity, so a reviewer could find the database asleep. It also ships auth, storage, and realtime, none of which we use. |
| Turso (libSQL) | Its SQLAlchemy dialect is less mature, and it still lacks percentile functions. |
| PlanetScale | No free tier, and it's MySQL-based. |

## Consequences
- Local development needs Docker (or a native Postgres). Docker Compose makes this a single command.
- Integration tests run against real Postgres, so SQL behaves the same in tests and production.
- Neon scales to zero, so the first query after idle takes about a second to wake the database. This is acceptable, and the UI covers it with skeleton states.
