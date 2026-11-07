# 5. Frontend: React, Vite, TanStack, shadcn/ui, and a generated API client

- **Status:** Accepted, partially superseded by [0009](0009-delivery-refinements.md)
- **Date:** 2026-11-07

## Context
The UI is an **analytics product, not a data-entry form**. It needs a polished, modern look, smooth handling of 10k rows, shareable filtered views, and frontend types that stay correct as the API evolves.

## Decision
| Concern | Choice |
|---|---|
| Framework | **React 19 + TypeScript (strict) + Vite**, built as a single-page app |
| Routing | **TanStack Router**, with type-safe routes and **typed URL search params**, so filters and saved views are shareable links |
| Server state | **TanStack Query**: caching, background refresh, optimistic updates |
| UI | **shadcn/ui** (Radix primitives, owned in-repo) + **Tailwind CSS v4** |
| Grid | **TanStack Table + TanStack Virtual** |
| Charts and map | **Recharts** (via shadcn charts) and **d3-geo** with TopoJSON |
| Command palette | **cmdk** |
| API client | **Generated from the backend's OpenAPI** with `@hey-api/openapi-ts`: types, TanStack Query hooks, and Zod schemas |
| Tooling | **Biome** (lint and format), **Vitest**, **Testing Library**, **MSW**, **Playwright + axe** |

## Alternatives considered
| Option | Why not |
|---|---|
| Next.js | SSR and SEO add nothing to an internal tool, and its server layer would become a second backend, blurring where business logic lives. |
| MUI, Ant Design | Recognizable "admin template" look and heavy bundles. MUI's advanced grid features are paid. |
| Mantine | Solid, but less control over the visual identity than owned shadcn components. |
| AG Grid | Heavy, and its best features are paid. |
| Redux | Built for client state, but our state is server state. |
| Hand-written API types | They drift silently from the backend. The generated client turns drift into a compile error. |
| ESLint + Prettier | Two tools to configure where Biome does both, faster. |

## Consequences
- Changing the API breaks the frontend build instead of production. CI checks that the generated client is up to date.
- shadcn components are copied into `components/ui/`. That's more files, but we own the look and accessibility.
- Virtualized rendering keeps scrolling smooth regardless of row count.
