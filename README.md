# ACME Pay

**Insight-first salary management for HR.** ACME Pay replaces spreadsheet-based pay management for a 10,000-person, multi-country organization. It shows how the company pays people, records every pay change, and answers pay questions in plain English, with the figures shown as evidence.

> **Status:** foundations in place; features in progress. Live demo and video links will appear here.

## Read this first
| Document | What it tells you |
|---|---|
| [Requirements (one page)](docs/requirements.md) | Goal, scope, and what's deliberately left out |
| [Plan](docs/PLAN.md) | Product vision, architecture, quality strategy, roadmap |
| [Architecture decisions](docs/adr/) | Why each technology was chosen over the alternatives |
| [How AI was used](docs/ai/) | Rules, key prompts, and a log of AI corrections |

## Repository layout
```
backend/    FastAPI service (Python 3.13, uv)
frontend/   React 19 + TypeScript + Vite single-page app
docs/       Plan, requirements, ADRs, AI collaboration log
```

## Run locally
Prerequisites: Python 3.13 + [uv](https://docs.astral.sh/uv/), Node.js 24+, Docker.

```bash
cp .env.example .env
docker compose up -d                 # Postgres 17
cd backend && uv sync && uv run pytest
cd ../frontend && npm install && npm run dev
```

The full local setup is completed as the walking skeleton lands (roadmap milestone 1).
