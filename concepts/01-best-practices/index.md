# Best Practices

General engineering practices that apply regardless of language or framework — the habits that separate code that merely runs from code a team can actually maintain.

## Reading order
1. [[concepts/01-best-practices/01-clean-code/index|clean-code]] — **[Beginner]** — naming, function scope, DRY and its limits, comments (why not what), avoiding deep nesting
2. [[concepts/01-best-practices/02-habits-that-make-change-easier|habits-that-make-change-easier]] — **[Beginner → Intermediate]** — seven at-the-keyboard habits (guard clauses, intent-revealing names, anti-corruption boundaries, unrepresentable invalid states, decisions-vs-actions, useful errors, focused changes) under one idea: **make the next change easier**
3. [[concepts/01-best-practices/03-testing-fundamentals/index|testing-fundamentals]] — **[Beginner → Intermediate]** — unit, integration and E2E and what each can't catch · **stub, fake, spy, mock** and which to reach for · flaky tests from the clock and from test order · TDD · running it all in CI. With a lab reproducing a month-end bug
4. [[04-pr-structure|pr-structure]] — **[Beginner]** — keeping pull requests focused, writing them for the reviewer, what to include
5. [[05-documentation-practices|documentation-practices]] — **[Intermediate]** — READMEs, inline comments, API docs, ADRs, and keeping documentation from rotting
6. [[concepts/01-best-practices/06-coupling-and-cohesion/index|coupling-and-cohesion]] — **[Beginner → Intermediate]** — the kinds of coupling and cohesion, worst to best; **fan-in, fan-out and instability**, with a lab that measures them and finds import cycles in your own code
7. [[concepts/01-best-practices/07-solid-principles/index|solid-principles]] — **[Intermediate]** — the five principles, what each one actually buys you, and when applying them is over-engineering
8. [[concepts/01-best-practices/08-data-migrations|data-migrations]] — **[Intermediate → Advanced]** — the five phases, **idempotency as a property of (ID scheme, write verb)**, replace vs. patch, dry runs where the safe name is the short one, count reconciliation, and why repair scripts are planned for rather than apologised for

## Related
- [[backend/index|backend concepts]]
- [[frontend/index|frontend concepts]]
- [[git/index|the git course]]
