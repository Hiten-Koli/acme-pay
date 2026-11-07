# Key prompts

The prompts that set the direction of the project, in order, paraphrased for brevity. Routine instructions are omitted.

## 1. Codifying engineering standards before any code
> Set up rules for yourself globally: modern coding standards, documentation, sound design principles, maintainability, DRY, simplicity without overengineering, a clean folder structure, and planning with me before implementing anything.

**Outcome:** [global-engineering-rules.md](global-engineering-rules.md). Standards are written once and versioned, not repeated in every prompt.

## 2. Framing the assessment
> Plan before building. Make the architectural decisions on modern standards, at zero cost. Justify each decision against the alternatives. Define the folder structure and an automated deployment pipeline. State the problem clearly, what the solution does, how, and why it is the right approach.

**Outcome:** the first draft of [PLAN.md](../PLAN.md).

## 3. Raising the bar on the plan
> The plan is good but not great. It risks looking like legacy HRMS software: tables and rows. Make it modern and world-class, still at zero cost.

**Outcome:** the plan was rebuilt around the persona's jobs to be done. Changes:
- an insight-first UX (Pay Pulse, People Explorer, impact preview, benchmarks)
- a grounded AI pay analyst
- property-based tests and AI evals
- per-PR preview environments
- explicit non-functional budgets, risks, and a fallback order

"Modern" was deliberately applied to the product experience and engineering rigor, not to infrastructure complexity, in line with the brief: *"not the most complex system, but good engineering judgment"*.

## 4. Commit history as a narrative
> Commit with messages that let a reviewer follow how the solution evolved.

**Outcome:** conventional commits with explanatory bodies, one logical change per commit, and `Co-Authored-By` trailers for transparency.
