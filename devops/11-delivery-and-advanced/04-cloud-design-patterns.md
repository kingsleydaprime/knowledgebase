---
id: d2f130a4-93cf-4da2-879a-5997b6be1f77
---

# Cloud Design Patterns

Cloud design patterns are tried and tested ways of building systems that keep working when parts of them fail. In the cloud, machines and networks do fail, so you plan for it from the start. Retrying a failed request after a short wait, the way an app tries again when your network drops, is one of these patterns.

## The premise: the cloud fails, by design
<!-- bite: 6dd00a81-5c46-4142-9d62-e2d74dac2ef2 -->

Cloud infrastructure is commodity hardware that *will* fail — instances die, networks partition, dependencies time out. You don't prevent failure; you **design for it**. That reframing is the root of every pattern here: assume any component can vanish mid-request, and build so the system degrades gracefully instead of collapsing.

## Availability & resilience patterns
<!-- bite: 4f3e3413-4959-4272-85ed-751ae36eb062 -->

- **Retry (with backoff + jitter)** — transient failures (a brief network blip, a throttled request) often succeed on a second attempt. Retry — but with *exponential backoff* (wait longer each time) and *jitter* (randomize the wait) so a swarm of clients doesn't retry in lockstep and hammer a recovering service. (The [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|message-queue consumer]] does exactly this: transient failures retry, permanent ones go to a DLQ.)
- **Circuit breaker** — if a dependency is clearly down, stop calling it for a while. Like an electrical breaker, it "trips" after repeated failures and fails fast (returning an error or fallback immediately) instead of piling up doomed requests and threads on a dead service. It periodically tries a probe request to see if the dependency recovered. Prevents one failing service from cascading into total collapse.
- **Bulkhead** — isolate resources so one overloaded component can't sink the whole ship (named after ship compartments). E.g. separate connection/thread pools per dependency, so a slow downstream exhausts only its own pool, not the entire app's threads.
- **Timeout** — never wait forever. Every remote call needs a bounded timeout, or one slow dependency ties up resources until the whole system starves (the thread-pool exhaustion the bulkhead pattern also guards against).
- **Graceful degradation / fallback** — when a non-critical dependency fails, return a reduced-but-working response (a stale cache, a default) instead of an error. The site stays up with less functionality rather than going down.
- **Health checks** — expose liveness/readiness endpoints so load balancers and [[devops/10-orchestration/01-kubernetes|orchestrators]] can route around unhealthy instances automatically.

## Scalability & data patterns
<!-- bite: e88f9777-aedb-411c-a0ae-09a1b7587ee5 -->

- **Horizontal scaling + statelessness** — scale *out* (more instances) not just *up* (bigger instance). This requires services to be **stateless** — no session data held in-process — so any instance can handle any request and instances are disposable. State goes to a shared store (DB, Redis) instead.
- **Cache-aside** — check a cache first; on a miss, load from the database and populate the cache. The workhorse read-scaling pattern (Redis in front of Postgres). Pairs with the [[devops/02-networking-and-web/02-web-servers-and-proxies|caching]] discussion; the hard part is invalidation.
- **Queue-based load leveling** — put a queue between a producer and a slower consumer so traffic spikes are absorbed and the consumer processes at its own steady pace instead of being overwhelmed. This is exactly the [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|RabbitMQ pipeline]] and its backpressure — a design pattern the applied-systems work already demonstrates.
- **CQRS / read replicas** — separate read and write paths so reads scale independently (replicas) of writes.
- **Sharding / partitioning** — split data across nodes by key so no single database is the bottleneck.

## Management & monitoring patterns
<!-- bite: 89691d41-76fe-4dee-9b93-a371917b2515 -->

- **Externalized configuration** — config lives outside the artifact (env vars, config service), so the same image runs in every environment ([[devops/09-infrastructure-as-code/index|IaC]], [[devops/06-secret-management/index|secrets]]).
- **Observability built in** — structured logs, metrics, and traces as a first-class design concern, not bolted on ([[devops/07-observability/index|observability]]).
- **Idempotency** — design operations so retries and duplicate deliveries are safe (the [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotency-key pattern]]) — a hard requirement once you have retries and at-least-once messaging.

## The through-line
<!-- bite: 3bd780bd-429a-440a-842e-003a6521bcbd -->

Almost every pattern here is a specific answer to one principle: **assume failure and partial availability, and contain the blast radius.** Retry/circuit-breaker/timeout/bulkhead contain *dependency* failure; statelessness/queues/caching contain *load*; idempotency contains *duplication*. Notably, several of these aren't abstract — the applied-systems section already implements queue-based load leveling, retry-with-DLQ, and idempotency in a real pipeline, which is the most concrete grounding this otherwise-reference section has.

## Related
<!-- bite: 2f65996f-d2a9-4f75-9c61-604771bb1110 -->
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] — queue-based load leveling + retry/DLQ in real code
- [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — the idempotency pattern implemented
- [[devops/11-delivery-and-advanced/03-service-mesh|Service Mesh]] — infrastructure that implements retry/circuit-breaking for you
- [[devops/08-cloud/01-cloud-fundamentals|Cloud Fundamentals]] — regions/AZs, the substrate for availability

## About this lesson
<!-- bite: 07e9ae01-eb3a-4a3c-947c-5400f76d0c2f -->

**Level:** reference. **Covers:** from roadmap.sh's cloud-design-patterns branch and the standard patterns literature (Azure's catalog is a good canonical reference). These are architectural patterns for building systems that stay up, scale, and recover on inherently unreliable cloud infrastructure.
