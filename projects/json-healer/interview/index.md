# json-healer — Interview Questions

Questions an interviewer could realistically ask **about this project**, drawn from what's
actually in [`../learning.md`](../learning.md). Nothing here is generic trivia — every question
has a real answer sitting somewhere in the build log.

## How to use this

- **Answer out loud, from memory, before reading the hint.** If you can't, that's the gap.
- Each question has a **Strong answer covers** line. It's a checklist of the points a good
  answer hits — not a script to recite.
- **[Beginner] / [Intermediate] / [Advanced]** tags describe how much of the project's context
  the question assumes, not absolute difficulty.
- The questions marked 🔥 are the ones an interviewer is *most* likely to ask, because they're
  where this project is unusual.

## Files

| File | Covers |
|---|---|
| [01-typescript-and-packaging.md](01-typescript-and-packaging.md) | TS config, dual CJS/ESM exports, `extends Error`, tsup, size budget, npm publishing |
| [02-parsing-and-algorithms.md](02-parsing-and-algorithms.md) | Regex vs scanner, fence stripping, block extraction, bracket balancing, the pipeline |
| [03-design-decisions-and-story.md](03-design-decisions-and-story.md) | Scope, trade-offs, benchmarks, "why not just X", behavioural questions |

---

## Before anything else: the 60-second pitch

Interviewers open with *"tell me about json-healer."* Have this ready, out loud, under a minute:

> A zero-dependency TypeScript library that repairs malformed JSON coming out of LLMs — markdown
> fences, chatter around the payload, trailing commas, single quotes, unterminated strings,
> truncated output. It tries `JSON.parse` first and only does work when that fails, so the happy
> path costs nothing. The interesting part is that the naive approach — regex for everything —
> breaks the moment you need to know whether a comma is *inside a string*, so the middle of the
> library is a small character scanner that tracks string/escape state, and every later heal step
> is built on top of it. It ships dual CJS/ESM, has a hard gzip size budget, and does no schema
> validation on purpose — that's Zod's job.

Rehearse the second half. Anyone can describe *what* it does; the scanner insight is what shows
you understood the problem rather than just pattern-matched it.
