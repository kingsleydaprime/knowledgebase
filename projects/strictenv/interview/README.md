# strictenv — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from what's
actually in [`../learning.md`](../learning.md). Every question has a real answer somewhere in the
ten-milestone build log.

## How to use this

- **Answer out loud, from memory, before reading the hint.** If you can't, that's the gap.
- Each question has a **Strong answer covers** line — a checklist of the points a good answer
  hits, not a script.
- **[Beginner] / [Intermediate] / [Advanced]** describe how much project context the question
  assumes, not absolute difficulty.
- 🔥 marks the questions most likely to come up, because they're where this project is unusual.

## Files

| File | Covers |
|---|---|
| [01-typescript-type-system.md](01-typescript-type-system.md) | `InferEnv`, mapped types, conditional optionality, `Simplify`, narrowing, the one honest `as` |
| [02-runtime-parsing-and-cli.md](02-runtime-parsing-and-cli.md) | Coercion rules, the `.env` parser, precedence, `ENOENT`, ANSI colour, table alignment |
| [03-testing-packaging-and-story.md](03-testing-packaging-and-story.md) | Testing `process.exit`, PRD-traceable tests, dual-format smoke test, trade-offs, behavioural |

---

## Before anything else: the 60-second pitch

> A zero-dependency, Node-only TypeScript library that turns `process.env` into a typed, validated,
> auto-coerced object checked once at boot. You declare a schema — types, required flags,
> defaults — and it gives you back an object where required keys are non-optional *in the type*
> and optional ones aren't, with numbers already numbers and booleans already booleans. On failure
> it prints a colour-coded table of every problem at once and exits, so a misconfigured deploy dies
> at startup rather than at 2am inside a request handler. Two interesting parts: the type-level
> work — required-vs-optional is computed per key from the schema, which needs two mapped types
> intersected because TS can't make `?:` conditional inside one — and the deliberate design of the
> coercion edge cases, because `Boolean("false")` is `true` in JavaScript and that class of bug is
> the entire reason the library exists.

The `Boolean("false")` line is the one to keep. It turns an abstract library into a concrete bug
you've prevented.
