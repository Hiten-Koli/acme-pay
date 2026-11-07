# 1. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-07

## Context
This project will be read by people who were not present when decisions were made: reviewers, future maintainers, and the author months from now. Code shows *what* was built, not *why*, or which alternatives were rejected.

## Decision
Record every significant decision as a short Architecture Decision Record (ADR) in `docs/adr/`, numbered sequentially, using this format: **Context → Decision → Alternatives considered → Consequences**.

A decision is significant when it is hard to reverse, affects more than one part of the system, or a reasonable engineer could have chosen differently.

ADRs are immutable once accepted. A changed decision gets a new ADR that supersedes the old one, and the old one's status is updated to say so.

## Alternatives considered
- **Decisions only in the plan document.** The plan is a point-in-time snapshot and mixes many concerns. Individual decisions get lost.
- **A wiki.** It lives outside the repository and drifts away from the code.

## Consequences
- Every reviewer can trace why the system looks the way it does.
- Writing a few paragraphs per decision forces the alternatives to be considered explicitly.
