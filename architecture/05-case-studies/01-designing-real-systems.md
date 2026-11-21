---
id: e014c85d-7405-498e-9828-de7198599b0d
---

# Designing Real Systems

## How to use these
<!-- bite: d6fdbba9-1af5-4968-9361-c442c71f50a5 -->

For each problem, run the framework: **clarify requirements → estimate → high-level design → deep-dive the hard part → name the tradeoffs.** Do it on paper/whiteboard before reading any solution. The classic problems each stress a different building block:

## URL shortener (e.g. bit.ly)
<!-- bite: 2e1778a6-43b2-4b9c-a830-7679ff66db8e -->

- **The core** — generate a short unique key for a long URL; redirect on lookup.
- **What it teaches** — key generation ([[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID strategies]]: hash vs counter vs random, collision handling), read-heavy [[architecture/02-building-blocks/02-caching/index|caching]] (redirects vastly outnumber creates), and simple [[architecture/02-building-blocks/03-databases-at-scale|key-value storage]] at scale. The gentle starter.

## A social feed / Twitter timeline
<!-- bite: 62c125e2-8ebc-4667-bcdc-6794a994d474 -->

- **The core** — users post; followers see a timeline.
- **What it teaches** — the **fan-out** decision: *fan-out-on-write* (push each post to all followers' precomputed timelines — fast reads, expensive for celebrities with millions of followers) vs *fan-out-on-read* (assemble the timeline at read time — cheap writes, slow reads). The real answer is *hybrid* (push for most, pull for celebrities) — a perfect example of "it depends on the [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|requirements]]." Also [[architecture/02-building-blocks/02-caching/index|caching]], [[architecture/02-building-blocks/03-databases-at-scale|sharding]] by user, and [[architecture/01-system-design-fundamentals/04-cap-and-consistency|eventual consistency]] (a slightly stale feed is fine).

## A rate limiter
<!-- bite: 2901910b-3028-45bd-b294-1c9c2432941e -->

- **The core** — allow N requests per user per window; reject the rest.
- **What it teaches** — algorithms (token bucket, sliding window), where the counter lives ([[architecture/02-building-blocks/02-caching/index|Redis]] for shared state across servers), and the [[languages/01-java/02-jvm-and-concurrency/exercises/index|concurrency]] of atomic increments. You've already got a [[languages/01-java/02-jvm-and-concurrency/exercises/index|single-machine version to build]] — the distributed version adds shared state.

## A chat system (e.g. WhatsApp)
<!-- bite: 02df8786-56b9-4b3e-a28a-8ee5c7f3ff30 -->

- **The core** — real-time messaging, delivery, presence.
- **What it teaches** — [[architecture/02-building-blocks/05-communication/index|WebSockets]] for real-time push, message [[architecture/02-building-blocks/04-messaging-and-async/index|queues]], delivery guarantees + [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotency]] (exactly-once display), and connection state at scale.

## Others worth working
<!-- bite: afd7fd0a-d709-49ea-9199-64487f04f8c8 -->

A **news feed / notification system** (fan-out again), a **web crawler** (queues, dedup, politeness), a **typeahead/autocomplete** (tries, caching), a **distributed cache** (consistent hashing), a **payment system** (strong consistency, idempotency, sagas — the [[languages/01-java/06-applied-systems/index|domain you've built in Java]]).

## The evaluation criteria (what "good" looks like)
<!-- bite: 37ea8ac3-eda4-431b-984f-9c42ec150f92 -->

Whether interviewing or designing for real, a strong design shows:

1. **Requirements first** — you asked what you're optimizing for before designing.
2. **Justified choices** — every component has a *why* tied to a requirement, not "because it's what people use."
3. **Named tradeoffs** — you said what you're giving up (consistency for availability, storage for read speed) *deliberately*.
4. **Bottleneck awareness** — you found the single points of failure and hot paths and addressed them.
5. **Knowing when to stop** — you didn't add Kafka and microservices to a problem a monolith and a database solve.

## Then: build one
<!-- bite: 81982cd0-cf00-4e3d-80ec-9b5df55a0cb1 -->

Reading and whiteboarding get you far, but the deepest understanding comes from **building** — which is why the flagship [[project-ideas|projects]] are systems you implement yourself. Design a system on paper, then go build a piece of it for real.

## Related
<!-- bite: 18c4d56e-9ac8-4146-8f81-4f6e2bb6268b -->
- [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|How to Approach System Design]] — the framework these apply
- [[architecture/system-design-reference|System Design Reference]] — the dense cheat-sheet for quick lookup
- [[project-ideas|Project Ideas]] — build-your-own Redis / DB / git / Raft

## About this lesson
<!-- bite: 681bb825-6430-46b1-85d6-4ceb09e60d67 -->

**Level:** reference / practice. **Covers:** applying the [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|framework]] to the classic design problems. The point isn't to memorize "the answer" (there isn't one) — it's to practice the *reasoning*, since that's what the skill and the interview reward.
