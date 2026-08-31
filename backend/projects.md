# Backend — Projects

*The domain where you have the most real code already (arete, nextvibe, gees-arise — see [[projects/README|projects/]]) — so the highest-signal reps here are **deepening what exists**, not starting fresh. Sections 01–07 hold in any language; every project below does too.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

**Every entry has a *done when*.** If you can't state when a project is finished, you'll either stop early or never stop.

## The ladder

- 🟢 **Add idempotency to an endpoint you already wrote** — an `Idempotency-Key` header, a store of key→response, and correct behaviour on retry. **Done when:** the same request sent twice creates one record and returns the same response body both times. Exercises: [[backend/02-api-design/README|API design]], [[backend/06-cross-cutting/README|cross-cutting]].

- 🟢 **Instrument one service properly** — structured logs with a request ID propagated through every layer, RED metrics (rate/errors/duration), and one distributed trace end to end. **Done when:** you can take a slow request's ID from a log line and see its full span breakdown. Exercises: [[devops/10-observability/README|observability]].

- 🟢 **Write the failure tests you skipped** — what happens on a DB timeout, a duplicate key, a malformed payload, a 500 from an upstream. **Done when:** every error path in one module has a test that asserts the status code *and* the response shape. Exercises: [[backend/07-practices/README|practices]].

- 🟡 ⭐ **Rate limiter + circuit breaker, from scratch** — token bucket in Redis (not a library), then a circuit breaker around one upstream call with half-open recovery. **Done when:** you can demonstrate the breaker opening under induced failure and recovering, with metrics showing both. Exercises: [[backend/06-cross-cutting/README|cross-cutting]], [[architecture/02-building-blocks/README|building blocks]].

- 🟡 **A job queue with real delivery semantics** — outbox pattern, at-least-once delivery, dead-letter queue, and an idempotent consumer. **Done when:** you can `kill -9` the worker mid-job and no message is lost or double-applied. Exercises: [[backend/04-data-and-persistence/README|data and persistence]], [[architecture/02-building-blocks/README|queues]].

- 🟡 **Auth, implemented not imported** — sessions *and* JWT, refresh-token rotation, and a working logout that actually revokes. **Done when:** you can explain why your refresh tokens rotate, and demonstrate that a stolen one is detectable. Exercises: [[backend/05-auth/README|auth]], [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]].

- 🟡 **Migrate a monolith module to a service** — pick one bounded context in a real project, extract it behind an API, and keep both running. **Done when:** the monolith calls it over the network and you've written up what got harder. Exercises: [[backend/03-structuring-a-backend/README|structuring]], [[architecture/03-architectural-patterns/README|patterns]].

- 🔴 **Load-test and fix your own p99** — pick a real endpoint, load it with k6 until p99 degrades, find the actual cause (N+1? pool exhaustion? GC? lock contention?), fix it, prove it with a before/after graph. **Done when:** you have both graphs and a written diagnosis. **This is the single most interview-relevant backend rep** — [[backend/interview/README|the backend bank]] is built from exactly this conversation.

- 🔴 ⭐ **Rebuild one service in a second language** — take something small you wrote in Node and rewrite it in Go or Rust. **Done when:** both pass the same test suite and you can articulate what each language made easy and hard. Exercises: [[backend/frameworks/README|frameworks]].

## If you only do one

**The p99 investigation.** It's the shortest path from "I built a backend" to "I can reason about a running system under load" — and it's the conversation every backend interview eventually becomes.

## Related
- [[backend/README|the backend course]] · [[backend/interview/README|interview bank]]
- [[build-your-own-shit/01-http-server|build your own HTTP server]] — the foundation under all of this
- [[project-ideas|Project Ideas]] — the vault-wide index
