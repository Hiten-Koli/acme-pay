# 8. No authentication in v1, with a seam for it

- **Status:** Accepted
- **Date:** 2026-11-07

## Context
Salary data is sensitive and a real deployment requires authentication and authorization. This deployment, however, has one persona (the HR manager), uses **synthetic data only**, and must be easy for reviewers to evaluate in a few minutes.

## Decision
- Ship v1 **without login**.
- All protected routes depend on a single FastAPI dependency, `get_current_actor()`, which currently returns a fixed "HR Manager" actor. Compensation changes record this actor, so the audit trail already has an author field.
- Adding real auth later means replacing that one dependency with an OIDC/JWT verifier. Routes and services don't change.

## Alternatives considered
| Option | Why not |
|---|---|
| Demo login with shared credentials | Gives a false sense of security and adds friction for reviewers. |
| Full OIDC (Auth0, Clerk, Entra ID) | Significant setup for a single-persona demo, and reviewers would need accounts. |

## Consequences
- The public deployment exposes synthetic data only. Real data must never be loaded into it, and the README says so prominently.
- Authorization (roles such as HR manager or HR viewer) remains future work, listed in the requirements as deliberately left out.
