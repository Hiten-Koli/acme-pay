# Architecture Decision Records

Why ACME Pay is built the way it is. See [ADR 0001](0001-record-architecture-decisions.md) for the format.

| # | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-backend-fastapi-sqlalchemy.md) | Backend: FastAPI, SQLAlchemy 2.0, feature-sliced hexagonal-lite | Accepted |
| [0003](0003-database-postgresql-neon.md) | Database: PostgreSQL on Neon | Accepted |
| [0004](0004-hosting-vercel-github-actions.md) | Hosting and delivery: Vercel, gated by GitHub Actions | Accepted, partly superseded by 0009 |
| [0005](0005-frontend-react-vite-tanstack-shadcn.md) | Frontend: React, Vite, TanStack, shadcn/ui, generated client | Accepted, partly superseded by 0009 |
| [0006](0006-money-and-currency.md) | Money and currency representation | Accepted |
| [0007](0007-grounded-ai-pay-analyst.md) | Grounded, provider-agnostic AI pay analyst | Accepted |
| [0008](0008-no-authentication-in-v1.md) | No authentication in v1, with a seam for it | Accepted |
| [0009](0009-delivery-refinements.md) | Refinements made during delivery (band definition, simplifications) | Accepted |
