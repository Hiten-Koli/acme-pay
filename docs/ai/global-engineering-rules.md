# Global Working Rules

These rules apply to every project. Project-level CLAUDE.md files may add to them or override them.
Primary stack: **Python** (backend) and **React** (frontend).

## 1. Workflow: discuss before building
- For any non-trivial task (new feature, new module, schema change, refactor, dependency addition), **do not implement immediately**.
  1. Restate the goal in one or two lines.
  2. Ask clarifying questions only about things that change the outcome.
  3. Propose a short plan: approach, files affected, trade-offs. Give a recommendation, not a survey of options.
  4. **Wait for my approval** before writing code.
- Trivial, clearly specified changes (typo, rename, small bug fix) can be done directly.
- Suggest better alternatives when I propose something questionable, briefly and with reasons. I make the final call.
- Work in small, reviewable steps. After each step, summarize what changed and what is next.
- Never delete, overwrite, or restructure existing files without telling me first.
- Never commit, push, or install global tools unless I ask.

## 2. Code principles
- **Simple first (KISS).** Choose the most straightforward solution that works.
- **No overengineering (YAGNI).** Build only what was asked. No speculative features, premature abstractions, unused config options, or extra layers.
- **DRY.** Reuse existing code and utilities. Search the codebase before writing something new. Extract duplication only once it appears a second or third time.
- **SOLID, applied pragmatically.** Single responsibility per function, class, and component. Prefer composition over inheritance.
- **Readable over clever.** Clear names, small functions, shallow nesting, early returns. No magic numbers or strings; use named constants or enums.
- **Maintainable.** Loose coupling, explicit dependencies, no hidden global state. Code should be easy to change and delete.
- Prefer boring, well-established libraries over custom solutions. Ask before adding a new dependency.

## 3. Folder structure and organization
- Follow a clear, conventional layout and keep it consistent. Do not dump files in the root.
- Separate concerns by layer. Backend: routes/API, services (business logic), repositories/data access, models/schemas, core/config. Frontend: pages, components, hooks, services/api, utils, types.
- Group by feature/domain when the project grows, rather than by file type alone.
- Keep files focused and small. Split a file when it handles more than one responsibility.
- Configuration and secrets live in environment variables (`.env`, never committed). Provide a `.env.example`.
- Keep a proper `.gitignore`, a pinned dependency file, and a README with setup and run instructions.

## 4. Python standards
- Python 3.11+ idioms. Follow PEP 8 and PEP 257. Format with Ruff/Black, lint with Ruff.
- **Type hints on all function signatures**; keep code mypy-friendly.
- Use Pydantic (or dataclasses) for data validation and structured data. Use `pathlib`, f-strings, context managers, and comprehensions where they stay readable.
- Use virtual environments. Manage dependencies with `pyproject.toml` or `requirements.txt`, pinned.
- Handle errors with specific exceptions. Never use bare `except:` and never swallow errors silently. Use the `logging` module, not `print`.
- Use Pytest for tests.
- For web APIs prefer FastAPI (or the framework already in the project): thin route handlers, logic in services, validated schemas in and out.

## 5. React standards
- Functional components and hooks only. Prefer TypeScript; ask if a project uses plain JavaScript.
- One component per file, small and focused. Extract reusable logic into custom hooks.
- Keep API calls in a dedicated service layer, not inside UI components.
- Keep state as local as possible; lift or use context/state libraries only when needed.
- Handle loading, error, and empty states for every data-driven view.
- Accessibility basics: semantic HTML, labels, keyboard support, alt text.
- Avoid unnecessary re-renders and premature memoization. Use stable keys in lists.
- Lint and format with ESLint and Prettier. Test with Vitest/Jest and React Testing Library.

## 6. Documentation
- Every module, class, and public function gets a concise docstring (Python: Google style) or JSDoc/TSDoc (React/TS) covering purpose, parameters, return value, and raised errors where relevant.
- Comments explain **why**, not what. Do not add noise comments.
- Keep README and API docs current whenever behavior, setup, or endpoints change.
- Record significant design decisions briefly (in README or a `docs/` folder).

## 7. Testing and quality
- Write tests alongside new logic: happy path, edge cases, and failure cases. Business-critical logic (e.g. money and salary calculations) must be tested thoroughly.
- Run the tests, linter, and type checker after changes and report real results. Never claim something works without verifying it.
- Do not weaken or delete tests to make them pass. Fix the cause.
- Prefer fixing root causes over workarounds.

## 8. Security and data handling
- Never hardcode secrets, keys, or credentials. Never log sensitive data.
- Validate and sanitize all external input. Use parameterized queries or an ORM; never build SQL by string concatenation.
- Apply authentication and authorization checks on every protected endpoint. Use least privilege.
- Hash passwords with a modern algorithm (argon2/bcrypt). Use HTTPS and sensible CORS settings.
- **Money and payroll data:** use `Decimal` (never floats) for currency, store amounts in a consistent precision, and treat personal and salary data as confidential.

## 9. Communication style
- Be concise and direct. Lead with the answer or the decision needed.
- Reference files with clickable paths and line numbers.
- Flag assumptions, risks, and anything I skipped or could not verify.
- If something is ambiguous or you disagree with my approach, say so before proceeding.
- Make no unrequested changes: no drive-by refactors, formatting churn, or extra files. Mention such opportunities instead.
- Report outcomes faithfully, including failures.
