# Best Practices

General engineering practices that apply regardless of language or framework — the habits that separate code that merely runs from code a team can actually maintain.

## Reading order
1. [[01-clean-code|clean-code]] — **[Beginner]** — naming, function scope, DRY and its limits, comments (why not what), avoiding deep nesting
2. [[02-pr-structure|pr-structure]] — **[Beginner]** — keeping pull requests focused, writing them for the reviewer, what to include
3. [[03-documentation-practices|documentation-practices]] — **[Intermediate]** — READMEs, inline comments, API docs, ADRs, and keeping documentation from rotting
4. [[04-testing-fundamentals|testing-fundamentals]] — **[Intermediate]** — the testing pyramid (unit/integration/E2E), TDD, what makes a test actually valuable vs. just contributing to a coverage number
5. [[05-solid-principles|solid-principles]] — **[Intermediate]** — the five principles, what each one actually buys you, and when applying them is over-engineering
6. [[concepts/04-best-practices/06-data-migrations|data-migrations]] — **[Intermediate → Advanced]** — the five phases, **idempotency as a property of (ID scheme, write verb)**, replace vs. patch, dry runs where the safe name is the short one, count reconciliation, and why repair scripts are planned for rather than apologised for
7. [[concepts/04-best-practices/07-habits-that-make-change-easier|habits-that-make-change-easier]] — **[Beginner → Intermediate]** — seven at-the-keyboard habits (guard clauses, intent-revealing names, anti-corruption boundaries, unrepresentable invalid states, decisions-vs-actions, useful errors, focused changes) under one idea: **make the next change easier**

## Related
- [[backend/README|backend concepts]]
- [[frontend/README|frontend concepts]]
- [[git/README|the git course]]
