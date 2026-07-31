# Designing Real Systems

**[reference / practice]** — applying the [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|framework]] to the classic design problems. The point isn't to memorize "the answer" (there isn't one) — it's to practice the *reasoning*, since that's what the skill and the interview reward.

## How to use these

For each problem, run the framework: **clarify requirements → estimate → high-level design → deep-dive the hard part → name the tradeoffs.** Do it on paper/whiteboard before reading any solution. The classic problems each stress a different building block:

## URL shortener (e.g. bit.ly)

- **The core** — generate a short unique key for a long URL; redirect on lookup.
- **What it teaches** — key generation ([[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID strategies]]: hash vs counter vs random, collision handling), read-heavy [[architecture/02-building-blocks/02-caching|caching]] (redirects vastly outnumber creates), and simple [[architecture/02-building-blocks/03-databases-at-scale|key-value storage]] at scale. The gentle starter.

## A social feed / Twitter timeline

- **The core** — users post; followers see a timeline.
- **What it teaches** — the **fan-out** decision: *fan-out-on-write* (push each post to all followers' precomputed timelines — fast reads, expensive for celebrities with millions of followers) vs *fan-out-on-read* (assemble the timeline at read time — cheap writes, slow reads). The real answer is *hybrid* (push for most, pull for celebrities) — a perfect example of "it depends on the [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|requirements]]." Also [[architecture/02-building-blocks/02-caching|caching]], [[architecture/02-building-blocks/03-databases-at-scale|sharding]] by user, and [[architecture/01-system-design-fundamentals/04-cap-and-consistency|eventual consistency]] (a slightly stale feed is fine).

## A rate limiter

- **The core** — allow N requests per user per window; reject the rest.
- **What it teaches** — algorithms (token bucket, sliding window), where the counter lives ([[architecture/02-building-blocks/02-caching|Redis]] for shared state across servers), and the [[languages/01-java/02-jvm-and-concurrency/exercises/README|concurrency]] of atomic increments. You've already got a [[languages/01-java/02-jvm-and-concurrency/exercises/README|single-machine version to build]] — the distributed version adds shared state.

## A chat system (e.g. WhatsApp)

- **The core** — real-time messaging, delivery, presence.
- **What it teaches** — [[architecture/02-building-blocks/05-communication|WebSockets]] for real-time push, message [[architecture/02-building-blocks/04-messaging-and-async|queues]], delivery guarantees + [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotency]] (exactly-once display), and connection state at scale.

## Others worth working

A **news feed / notification system** (fan-out again), a **web crawler** (queues, dedup, politeness), a **typeahead/autocomplete** (tries, caching), a **distributed cache** (consistent hashing), a **payment system** (strong consistency, idempotency, sagas — the [[languages/01-java/06-applied-systems/README|domain you've built in Java]]).

## The evaluation criteria (what "good" looks like)

Whether interviewing or designing for real, a strong design shows:

1. **Requirements first** — you asked what you're optimizing for before designing.
2. **Justified choices** — every component has a *why* tied to a requirement, not "because it's what people use."
3. **Named tradeoffs** — you said what you're giving up (consistency for availability, storage for read speed) *deliberately*.
4. **Bottleneck awareness** — you found the single points of failure and hot paths and addressed them.
5. **Knowing when to stop** — you didn't add Kafka and microservices to a problem a monolith and a database solve.

## Then: build one

Reading and whiteboarding get you far, but the deepest understanding comes from **building** — which is why the flagship [[project-ideas|projects]] are systems you implement yourself. Design a system on paper, then go build a piece of it for real.

## Related
- [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|How to Approach System Design]] — the framework these apply
- [[architecture/system-design-reference|System Design Reference]] — the dense cheat-sheet for quick lookup
- [[project-ideas|Project Ideas]] — build-your-own Redis / DB / git / Raft
