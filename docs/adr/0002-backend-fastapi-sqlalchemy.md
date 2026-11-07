# 2. Backend: FastAPI, SQLAlchemy 2.0 and a feature-sliced, hexagonal-lite structure

- **Status:** Accepted
- **Date:** 2026-11-07

## Context
We need a Python HTTP API serving a React SPA. It handles CRUD on 10k employees, analytics aggregates, and a streaming AI endpoint. Correctness of money and validation matters more than raw throughput.

## Decision
- **FastAPI** (async) on **Python 3.13**, with **Pydantic v2** for request and response schemas. Type hints are the validation and generate the OpenAPI 3.1 contract.
- **SQLAlchemy 2.0** (typed, async) for data access and **Alembic** for versioned migrations.
- **Structure:** feature slices (`employees`, `compensation`, `insights`, `assistant`), each with its own `router → service → repository` layers, plus a pure `domain` package (`Money`, percentile, compa-ratio) with no I/O.
- Dependencies point inward: routers depend on services, and services depend on domain and repositories. The dashboard, the REST API, and the AI analyst all reuse the same services.

## Alternatives considered
| Option | Why not |
|---|---|
| Django + DRF | Admin, templates, and sessions go unused. Serializers duplicate what Pydantic gives for free. Heavier for an API-only service. |
| Flask | No native typing or validation, so we would rebuild FastAPI's features with extensions. |
| Litestar | Technically strong, but a smaller ecosystem and less familiar to reviewers. |
| SQLModel | Convenient for CRUD, but limited for analytics queries, and it lags SQLAlchemy releases. |
| Generic repository/unit-of-work frameworks | Too much abstraction for three feature slices. Plain repository classes are enough. |

## Consequences
- Business rules are unit-testable without HTTP or a database.
- The OpenAPI schema becomes the source for the generated frontend client (see ADR 0005).
- Async adds some complexity to the test setup, which is accepted in exchange for streaming AI responses and efficient I/O on serverless.
