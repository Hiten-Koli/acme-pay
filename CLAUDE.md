# ACME Pay: project rules for the AI pair-programmer

These rules extend the global engineering rules ([docs/ai/global-engineering-rules.md](docs/ai/global-engineering-rules.md)). Where they conflict, this file wins.

## Context
- **What:** salary management and pay insights for an HR manager at a 10,000-employee, multi-country organization. This is a job assessment for a "software craftsperson" role, where **how** it's built is graded as much as what.
- **Source of truth for scope:** [docs/PLAN.md](docs/PLAN.md) (roadmap, section 10), [docs/requirements.md](docs/requirements.md), and [docs/adr/](docs/adr/). Don't build anything outside them without asking.
- **Persona:** non-technical HR manager. UX is insight-first, not table-first.

## Workflow
- Follow the roadmap milestones in order. Propose the plan for each milestone and wait for approval before starting it.
- **TDD for domain and service logic:** commit the failing test, then the implementation, then any refactor. The red → green → refactor cycle should be visible in the history.
- **Commits:** Conventional Commits (`feat`, `fix`, `test`, `refactor`, `docs`, `build`, `ci`, `chore`), with optional scope `(backend)` or `(frontend)`. One logical change per commit, with a body explaining *why*. Every commit must pass all checks.
- **Pushing:** commit locally only. The engineer reviews and runs `git push`, so nothing is published without human sign-off.
- **Significant decisions** get a new ADR in `docs/adr/` (and a row in its README). Never edit an accepted ADR; supersede it instead.
- **When AI output is rejected, redirected, or found wrong in review**, add an entry to [docs/ai/corrections-log.md](docs/ai/corrections-log.md). Add direction-changing prompts to [docs/ai/prompts.md](docs/ai/prompts.md). Keep the logs factual and concise, and log only entries with engineering substance. Leave out routine environment or tooling hiccups.
- Add a runtime dependency only in the commit that first uses it.

## Stack
- **Backend:** Python 3.13, FastAPI (async), Pydantic v2, SQLAlchemy 2.0 (async) + Alembic, PostgreSQL 17. Managed with **uv**.
- **Frontend:** React 19, TypeScript 7 (strict), Vite 8, TanStack Router/Query/Table/Virtual, shadcn/ui + Tailwind v4, Recharts. Linted and formatted with **Biome**.
- **Infra:** Neon (Postgres), Vercel (SPA + Python Functions), GitHub Actions (CI/CD).

## Commands
| Task | Backend (`backend/`) | Frontend (`frontend/`) |
|---|---|---|
| Install | `uv sync` | `npm install` |
| Lint | `uv run ruff check .` | `npm run lint` |
| Format | `uv run ruff format .` | `npm run lint:fix` |
| Type check | `uv run mypy` | `npm run typecheck` |
| Test | `uv run pytest` | `npm test` |
| Build | — | `npm run build` |

Local DB: `docker compose up -d` from the repo root (copy `.env.example` to `.env` first).

## Code conventions
- **Backend layout:** feature slices in `backend/acme_pay/<feature>/` with `router.py → service.py → repository.py`, plus `models.py` and `schemas.py`. Pure rules live in `backend/acme_pay/domain/` and must not do I/O. Routers hold no business logic.
- **Money:** always the `Money` value object (`Decimal` + ISO 4217 code). Never `float`. Sent over the API as a decimal string. FX conversion only through dated rates (ADR 0006).
- **Errors:** RFC 9457 Problem Details responses.
- **Analytics:** aggregate in SQL (`percentile_cont`), not in Python loops.
- **Frontend layout:** `src/features/<feature>/` holds that feature's components, hooks, and api usage. Shared primitives go in `src/components/ui/`. `src/api/` is **generated**, so never edit it by hand.
- **Tests:** deterministic (fixed seeds, frozen time, no network in unit tests). Name each test after the behavior it checks.
- **AI analyst:** tool calling over existing services only. Never text-to-SQL, and never send personal data to the LLM (ADR 0007).
- **Data:** synthetic only. Never load real personal data.
