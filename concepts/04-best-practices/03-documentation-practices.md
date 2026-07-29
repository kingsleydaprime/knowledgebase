# Documentation Practices

Documentation exists to transfer context from someone who has it (right now, while building something) to someone who doesn't (later — a teammate, a future contributor, or future-you after enough time has passed to forget the details). Writing it well is mostly about being honest with yourself about what that future reader will actually need and won't already know.

## The layers of documentation, and what each is actually for

- **README** — the entry point: what this project/module is, how to get it running, where to look next. Should answer "what is this and how do I start" in under a minute of reading, not require reading the entire codebase first.
- **Inline code comments** — for the *why*, not the *what* (see [[01-clean-code|clean-code]]) — a non-obvious constraint, a workaround, a reason behind a surprising decision at that specific spot in the code.
- **API documentation** — the contract for how to call something: parameters, return values, error cases, example usage. This is what a *consumer* of a function/endpoint needs, independent of how it's implemented internally.
- **Architecture Decision Records (ADRs)** — a short, dated record of a significant technical decision: what was decided, what alternatives were considered, and why. The value is almost entirely in the "why" and "what else was considered" — six months later, the decision itself is often visible in the code, but the reasoning behind it (and why the alternatives were rejected) is otherwise lost entirely.

```markdown
# ADR 004: Use PostgreSQL instead of MongoDB for the orders service

## Context
Orders have a fixed, well-understood relational shape and require strong
transactional guarantees across order + inventory + payment records.

## Decision
Use PostgreSQL.

## Alternatives considered
- MongoDB — rejected: schema flexibility isn't needed here, and multi-document
  transactions were less mature/more awkward at the time of this decision.

## Consequences
Requires a formal migration process for schema changes (see concepts/backend/databases.md).
```

## Writing for the reader who has less context than you do right now

The person writing documentation always has more context than the reader will — this is the central, easy-to-forget trap. Explicitly naming assumptions ("this assumes you've already run the setup script in the main README") and avoiding unexplained internal jargon/abbreviations is what actually closes that gap, rather than assuming shared context that only exists in the writer's head at the moment of writing.

## Keeping documentation from rotting

Documentation that describes outdated behavior is often worse than no documentation at all — it actively misleads a reader who trusts it. Practices that help:
- Keep documentation as close as possible to the code it describes (in the same repository, ideally the same file/folder) so it's more likely to be updated alongside a code change rather than forgotten in a separate system.
- Treat significant documentation updates as part of the same PR as the code change they describe (see [[02-pr-structure|pr-structure]]), not a separate, easily-deprioritized follow-up task.
- Periodically audit and prune documentation for things that no longer reflect current behavior — stale docs accumulate silently unless someone deliberately checks.

## Gotchas

- Documenting *what* code does at a level a reader could get just as easily from reading well-named code itself is low-value effort — spend that effort on the *why* instead (see [[01-clean-code|clean-code]]'s comments section for the same principle applied to inline comments specifically).
- Comprehensive documentation written once and never revisited tends to decay into actively misleading territory faster than teams expect — a living document that's checked periodically beats an exhaustive one written once and abandoned.
- Over-documenting a rapidly-changing, early-stage part of a system can create more maintenance burden (keeping docs in sync) than value delivered — matching documentation depth to how stable a given piece of the system actually is is a reasonable, deliberate tradeoff, not a nice-to-have.

## Related
- [[01-clean-code|clean-code]]
- [[02-pr-structure|pr-structure]]
- [[04-testing-fundamentals|testing-fundamentals]]
