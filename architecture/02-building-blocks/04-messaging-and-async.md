# Messaging & Async

**[reference]** — from the roadmap.sh system-design roadmap. How systems decouple and absorb load by *not* doing everything synchronously in the request path. Grounded in the real [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|RabbitMQ pipeline]].

## Synchronous vs asynchronous

- **Synchronous** — the caller waits for the work to finish before getting a response. Simple, immediate, but the caller is blocked and coupled to the callee's speed and availability.
- **Asynchronous** — the caller hands off the work and returns immediately; the work happens later. Decouples the caller from the worker's pace.

The system-design instinct: **anything slow or non-essential to the immediate response should be async.** A user uploads a video → return "processing" instantly, transcode in the background. Sending email, generating thumbnails, updating analytics, ML inference — none should block the user's request. This keeps the request path fast and the user experience snappy.

## Message queues — the async backbone

A **message queue** (RabbitMQ, SQS, Redis) sits between producers and consumers: producers push messages, consumers pull and process them at their own pace. What this buys:

- **Decoupling** — producer and consumer don't know about each other, can be deployed/scaled/fail independently.
- **Load leveling (buffering)** — a traffic spike fills the queue; consumers drain it steadily instead of being overwhelmed. The **queue-based load leveling** pattern — the queue absorbs bursts so downstream systems see smooth load. (Exactly what the [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|record pipeline]] does.)
- **Reliability** — if a consumer crashes, messages stay in the queue and get reprocessed; nothing is lost.
- **Scalability** — add more consumers (competing consumers) to drain faster.

Delivery guarantees matter: **at-least-once** (a message may be delivered more than once — so consumers must be [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotent]]) is the common default; **exactly-once** is expensive and often approximated. And **back-pressure** (the queue depth signaling producers to slow down) prevents unbounded growth when consumers fall behind.

## Pub/Sub — one event, many consumers

A **publish-subscribe** system broadcasts each message to *all* interested subscribers (vs a queue, where each message goes to *one* consumer). One "order placed" event → the inventory service, the email service, and the analytics service all react independently.

- **Point-to-point (queue)** — one message, one consumer (work distribution).
- **Pub/Sub (topic)** — one message, many consumers (event notification).

Kafka blends both (durable, replayable log that multiple consumer groups read independently) and is the backbone of many large event systems.

## Event-driven architecture

Taken to its conclusion: services communicate primarily by **emitting and reacting to events** rather than calling each other directly. A service publishes "something happened"; others subscribe and react. This maximally decouples services (a new consumer just subscribes — no change to the producer) and scales well, but the cost is **harder reasoning**: the flow is implicit and distributed, debugging spans many services ([[architecture/03-architectural-patterns/04-microservices-patterns|observability]] is essential), and you inherit [[architecture/01-system-design-fundamentals/04-cap-and-consistency|eventual consistency]]. Related patterns — **event sourcing** and **CQRS** — are in [[architecture/03-architectural-patterns/03-data-and-integration-patterns|data & integration patterns]].

## The tradeoff to name

Async isn't free: you trade *immediacy and simplicity* for *decoupling, resilience, and scale*. The system becomes eventually consistent, harder to trace, and needs infrastructure (the queue itself, which must be reliable). Use it where the decoupling/buffering genuinely pays — not for everything, or you've made a simple request into a distributed debugging problem.

## Related
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ (Java)]] — this built in real code (DLQs, backpressure, competing consumers)
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data & Integration Patterns]] — event sourcing, CQRS, saga
- [[architecture/01-system-design-fundamentals/02-scalability-and-performance|Scalability]] — async as a scaling lever
