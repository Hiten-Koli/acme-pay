# 7. A grounded, provider-agnostic AI pay analyst

- **Status:** Accepted
- **Date:** 2026-11-07

## Context
The problem statement asks for the HR manager to "answer questions about how the org pays people". Dashboards answer the questions we anticipated, and natural language covers the rest. Salary data is sensitive, though, and an LLM that invents a number in a pay discussion is worse than no answer.

## Decision
- The assistant uses **tool calling over our existing, tested insight services**, for example `get_salary_benchmarks(country, job_title)`, `compare_role_across_countries(job_title)`, `find_outliers(country)`, and `get_headcount(group_by)`. The tools return **aggregates only**.
- **No text-to-SQL** and no access to individual records. Names, emails, and individual salaries are never sent to the model.
- Each answer streams back over SSE as **a short explanation plus evidence**: the tool calls and their results, rendered as charts and tables. Every figure on screen comes from the database, not from generated text.
- An `LLMProvider` **port** has one adapter per vendor. The default is a free-tier model (Google Gemini Flash), chosen for cost, and Claude or OpenAI can be swapped in through configuration.
- **Evals:** a golden set of questions with expected tool calls and arguments runs in CI against recorded model responses, so it's deterministic and free. It can also run against the live model on demand.
- With no API key configured, the feature hides itself and the rest of the product works unchanged.

## Alternatives considered
| Option | Why not |
|---|---|
| Text-to-SQL | Prompt-injection and data-exfiltration risk, and unpredictable queries. Hard to test. |
| Sending raw rows as context | Leaks personal data, and 10k rows exceed sensible context and cost budgets. |
| Hard-wiring a single vendor's SDK | Couples the domain to a provider whose free tiers and pricing change. |
| No AI | Leaves the open-ended half of the problem statement unaddressed. |

## Consequences
- The assistant can only be as wrong as our tested services, which keeps correctness bounded and verifiable.
- New questions need new tools. That limits it deliberately, but tools are small and reuse existing services.
- Free-tier rate limits may throttle heavy use. The UI degrades gracefully with a clear message.
