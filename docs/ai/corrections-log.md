# Corrections log

Where AI output was rejected, redirected, or found to be wrong during review, and what changed as a result. Newest entries at the bottom.

| # | Date | What happened | How it was caught | Resolution |
|---|---|---|---|---|
| 1 | 2026-11-07 | The AI's **first plan was correct but generic**: a CRUD table with summary statistics, the default shape of an "HR system". It didn't reflect how the persona actually works. | Engineer review: the plan was rejected for not meeting a craftsperson standard. | Re-planned from the persona's jobs to be done: insight-first screens, a compensation impact preview, benchmarks, and a grounded AI analyst. Principle adopted: start from the user's questions, not the data model. |
| 2 | 2026-11-07 | Early commits raised **LF/CRLF warnings**. The project is developed on Windows but built and hosted on Linux. | Spotted in git output during review of the first commits. | Added `.gitattributes` to normalize to LF before any code existed, so diffs stay clean and shell scripts stay safe in CI. |
