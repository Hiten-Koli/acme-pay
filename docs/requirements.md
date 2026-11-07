# ACME Pay: Requirements (one page)

## Goal
Replace ACME's Excel-based salary management for **10,000 employees across multiple countries** with a web application. The HR manager should be able to **keep salary data correct** and **answer questions about how the organization pays people** quickly and with confidence.

## User
**HR Manager (Priya).** Comfortable with Excel, not technical, accountable to leadership for pay decisions.

| Job to be done | Today (Excel) | With ACME Pay |
|---|---|---|
| Keep pay data correct | Copies of files, overwritten values, typos | One validated source of truth with an append-only change history |
| Answer pay questions | Pivot tables and manual currency conversion | Insights on demand, plus questions in plain English |
| Decide on a pay change | Guesswork | Live preview of band position and cost before saving |

## Scope & features

**F1. Employee lifecycle.** Create, view, edit, and terminate employees. Termination is a soft delete that keeps the history. Data is validated on the server and constrained in the database.

**F2. Compensation changes.** Record a salary change with an effective date and reason. Every change is stored with its previous value and can never be edited afterwards. A **live impact preview** shows the new percentile among peers, the compa-ratio, and the annual cost (local currency and USD) before saving.

**F3. People Explorer.** Search, filter by country, department, role, or band position, sort, and save views across 10k employees with no lag. **CSV export** of any view.

**F4. Insights.**
- **Pay Pulse:** headcount, payroll in USD, median salary, people outside their band, payroll by country, and highlighted signals.
- **Benchmarks:** min, 25th percentile, median, 75th percentile, max, and average per role × country, plus cross-country comparison in USD.
- **Distribution and outliers:** salary histogram, and people outside the 10th-to-90th percentile range of their peer group.

**F5. Ask ACME Pay (AI analyst).** HR asks pay questions in natural language. The answer comes with the underlying figures as evidence. The model can only call tested analytics functions, so it never writes SQL and never sees personal data. The feature is optional and hides itself if not configured.

**F6. Seed data.** A deterministic script generates 10,000 realistic employees across about 10 countries in a few seconds, and is safe to re-run.

**Rules that hold everywhere**
- Money uses exact decimals with an ISO 4217 currency code, never floats.
- Cross-currency figures use a **dated** FX rate, and the rate date is shown.
- Insights cover active employees only. A peer group is the same job title in the same country.

## Quality bar
- API p95 under 200 ms (warm) and Pay Pulse LCP under 2 s.
- Zero accessibility violations (axe) on key pages.
- Fast, deterministic tests at every layer. Deploys only happen when all checks pass.

## Deliberately left out, and why

| Left out | Reasoning |
|---|---|
| Authentication and roles | There is one persona and the data is synthetic, and reviewers should reach the product without a login wall. The API has a single security seam where OIDC can be added later. |
| Payroll processing (tax, payslips, payouts) | A separate, regulated domain. The problem is managing and understanding pay, not paying it out. |
| Live FX rates | They make figures non-reproducible. A dated rate table is explainable and auditable. |
| Excel/CSV import | Done properly (validation, preview, error report), it is a feature in its own right. Export covers the Excel habit today. First item for v2. |
| Bonus, equity, benefits | Base salary answers the core questions. The model can extend to total compensation later. |
| Approvals, notifications, org chart | Useful at enterprise scale, but not needed to solve the stated problem. |
| Gender pay-equity analysis | Highly relevant because the EU Pay Transparency Directive applies from 2026, but it requires sensitive attributes. Stretch goal. |
