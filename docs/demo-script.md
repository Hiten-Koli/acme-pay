# Demo script (about 3 minutes)

A walkthrough for the video, told from the HR manager's point of view. Use the live app (or a local one seeded with `python -m acme_pay.seed`, which gives identical numbers).

## 1. The problem (15 s)
> "ACME's HR team manages pay for 10,000 people in 10 countries in Excel. Answering 'are we paying people fairly?' takes hours of pivot tables. ACME Pay starts from the questions, not the spreadsheet."

## 2. Pay Pulse: where to look (40 s)
- Headline figures: **9,524 active people, $752.9M payroll, $74,394 median**, **1,145 outside their pay band**.
- *Where to look*: **"25 of 77 Data Scientists in IN are below band."** Explain the band: within 20% of the median for the same role in the same country.
- Payroll by country and by department; click a department to open the directory filtered to it.

## 3. Follow the signal into Benchmarks (35 s)
- Click the Data Scientist signal. The role across countries in USD: the US median is $142k, India's $33k.
- India's histogram shows a separate cluster on the left: the underpaid group.
- *Outside the band* lists the people furthest from the median. Click **Rahul Costa (0.64 × median)**.

## 4. Decide a raise (45 s)
- The profile: salary ₹1,746,700, **Below band**, and the dot on the peer range sits left of the shaded middle 50%.
- Type **2400000**. Before anything is saved, the preview shows **+37.4%**, **$7,840 a year**, and the new position **0.88 × median, Within band**.
- Save. The history now shows the change with its reason and author, and every pay view refreshes.
- Try saving the same amount again: *"Salary is already this amount"*. HR rules are enforced by the API, not just the form.

## 5. Find anyone, keep data clean (20 s)
- `Ctrl K`, type a name, and jump straight to the profile.
- People: search, filters and sort live in the URL (share a view by copying the link). **Export CSV** opens in Excel.
- Add an employee with a lowercase country code (`gb`): it's normalized, paid in GBP, and the starting salary becomes the first history entry.

## 6. Ask ACME Pay (25 s, if a Gemini key is configured)
- Ask: *"Where do we pay Data Scientists the most, and the least?"*
- The answer is short. Below it is **the exact data it used**, shown with the same range chart as Benchmarks. The model can only call tested, aggregate-only queries; it never sees individuals.

## 7. How it's built (20 s)
- The README and docs: requirements, ADRs (including what changed during delivery), measured performance.
- The commit history: failing test first, then the code, for every rule. CI checks, migrates, deploys and smoke-tests on every push to `main`.
