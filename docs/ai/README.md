# How AI is used on this project

ACME Pay is built with an AI pair-programmer (**Claude Code**, Anthropic) as the brief requires. This folder documents *how* it was used, so the reviewer can judge the engineering, not just the output.

## Operating model

| Role | Responsibility |
|---|---|
| **Engineer (Hiten)** | Owns the problem framing, product decisions, approval of every plan, review of every change, and what gets pushed |
| **AI pair-programmer** | Proposes plans with alternatives, drafts code, tests, and docs, runs checks, and explains trade-offs |

### Rules of engagement
1. **Plan before code.** For any non-trivial change, the AI proposes a plan and waits for approval. The plan for this project ([PLAN.md](../PLAN.md)) went through a rejected first draft before approval (see the log).
2. **Rules are written down, not repeated.** The AI follows a versioned rules file: [global-engineering-rules.md](global-engineering-rules.md) for general standards, and the project [CLAUDE.md](../../CLAUDE.md) for stack conventions and commands.
3. **Tests are the arbiter.** AI-written code is accepted only when the tests, type checks, and linters pass. For core logic the tests are written first.
4. **The engineer publishes.** The AI commits locally, and the engineer reviews and pushes, so nothing reaches the remote without human sign-off. Every AI-assisted commit carries a `Co-Authored-By` trailer for transparency.
5. **Rejected AI output is logged.** Where AI output was wrong or redirected during review, it goes in [corrections-log.md](corrections-log.md).

## Files
| File | Contents |
|---|---|
| [global-engineering-rules.md](global-engineering-rules.md) | General coding standards the AI must follow on every project |
| [prompts.md](prompts.md) | The key prompts that shaped the project, in order |
| [corrections-log.md](corrections-log.md) | Where the AI got it wrong and how it was caught |
