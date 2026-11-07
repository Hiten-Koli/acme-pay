# 4. Hosting and delivery: Vercel, with GitHub Actions as the gate

- **Status:** Accepted, partially superseded by [0009](0009-delivery-refinements.md)
- **Date:** 2026-11-07

## Context
The software must be deployed, free, and pleasant for a reviewer opening it cold. It needs an SPA and a Python API. Deploys must never ship code that has not passed its checks.

## Decision
- Host the **SPA on Vercel's CDN** and the **FastAPI app as Vercel Python Functions** (Hobby plan). The web app rewrites `/api/*` to the API, so both are served from **one origin** and no CORS is needed.
- **GitHub Actions** owns the pipeline, deploying with the Vercel CLI only after all checks pass:
  - **Pull request:** lint, type check, and tests, then a Neon branch and a Vercel preview, then Playwright end-to-end tests against the preview.
  - **main:** migrate, then deploy, then a smoke test.
- Seeding production data is a separate manual workflow that is safe to re-run.

## Alternatives considered
| Option | Why not |
|---|---|
| Render (free) | The service sleeps after 15 minutes idle, and the next request waits about 50 seconds. A bad first impression for a reviewer. |
| Fly.io, Railway | No ongoing free tier for new accounts. |
| Google Cloud Run | Requires a billing account and card. |
| Netlify | Python support is weaker than Vercel's. |
| Vercel's own git auto-deploy | Deploys run in parallel with CI rather than after it, so failing code could reach production. |

## Consequences
- Cold starts are about a second, and every PR gets its own preview URL.
- The API stays a standard ASGI app, so moving to any container host later only needs a Dockerfile, with no code changes.
- Vercel Hobby is for non-commercial use, which fits this assessment. A commercial deployment would move to a paid plan or another host.
