# Resilience Patterns

**[reference]** — from the roadmap.sh system-design roadmap. The design patterns that keep a partial failure *partial* instead of cascading into a total outage. These overlap the [[devops/11-delivery-and-advanced/04-cloud-design-patterns|cloud design patterns]] I covered from the ops angle — here from the architecture angle, applied especially to [[architecture/03-architectural-patterns/04-microservices-patterns|service-to-service]] calls.

## The premise: dependencies fail

In any distributed system ([[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|and they all are]]), the services and databases you call *will* be slow or down sometimes. Without protection, one slow dependency ties up your threads waiting on it, those threads pile up, and your service becomes unavailable too — a **cascading failure** that spreads outward until the whole system is down. Resilience patterns contain that.

## Timeout

The most basic and most important: **never wait indefinitely.** Every remote call gets a bounded timeout, so a hung dependency fails fast instead of holding your resources forever. Sounds obvious; the default in many libraries is *no timeout*, which is how one slow database takes down an entire fleet. Set aggressive, deliberate timeouts on every network call.

## Retry (with backoff + jitter)

Transient failures (a blip, a throttle, a brief unavailability) often succeed on a second attempt, so retry — but carefully:

- **Exponential backoff** — wait longer between each retry (1s, 2s, 4s…) instead of hammering a struggling service.
- **Jitter** — randomize the wait so a swarm of clients doesn't retry in perfect lockstep and create a synchronized thundering herd.
- **Cap the retries** — retrying forever, or retrying a *permanent* failure, creates a **retry storm** that turns a small problem into a self-inflicted DDoS. Only retry idempotent operations ([[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|idempotency]]), and only transient failures.

The [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|message-queue consumer]] does exactly this: transient failures retry, permanent ones go to a dead-letter queue rather than looping forever.

## Circuit breaker

The key pattern for stopping cascades. Like an electrical breaker, it monitors calls to a dependency and, after enough failures, **trips** — subsequent calls fail *instantly* (or return a fallback) without even attempting the dead dependency:

```
CLOSED (normal) --too many failures--> OPEN (fail fast, don't call)
   ^                                      |
   |                                 after a timeout
   +----- success ----- HALF-OPEN <-------+  (try a probe request)
```

This gives the failing service room to recover (it's not being hammered), and keeps *your* service responsive (returning a fast error/fallback beats piling up doomed requests). The trip → probe → recover cycle is the standard implementation. Essential for any service with critical dependencies.

## Bulkhead

Named after a ship's watertight compartments: **isolate resources so one overloaded dependency can't sink the whole ship.** Give each dependency (or class of work) its own connection/thread pool, so a slow downstream exhausts only *its* pool — other functionality keeps working with its own resources. Without bulkheads, one slow dependency drains the *shared* thread pool and everything stalls (the failure mode timeouts alone don't fully prevent).

## Throttling / rate limiting

Protect a service from being overwhelmed (by traffic spikes, abusive clients, or a retry storm) by **rejecting or queuing** excess requests beyond a set rate — controlled shedding of load to stay up for everyone else. (Building a rate limiter is a [[languages/01-java/02-jvm-and-concurrency/exercises/README|concurrency exercise]].) Related: **load shedding** (drop low-priority work under stress) and **back-pressure** (signal upstream to slow down — [[architecture/02-building-blocks/04-messaging-and-async|messaging]]).

## Graceful degradation & fallbacks

When a non-critical dependency fails, return a *reduced* result instead of an error: a stale [[architecture/02-building-blocks/02-caching|cache]] value, a default, a "recommendations unavailable" placeholder. The core service stays up with less functionality rather than going down entirely — the [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability]] payoff.

## The unifying idea

Every pattern here answers one principle: **assume dependencies fail, and contain the blast radius** — timeout so you don't wait forever, circuit-break so you stop calling the dead, bulkhead so failure stays isolated, retry (carefully) for the transient, degrade so users see *something*. Combined, they turn "one service died" from an outage into a shrug.

## Related
- [[devops/11-delivery-and-advanced/04-cloud-design-patterns|Cloud Design Patterns (devops)]] — the same patterns, ops angle, with more
- [[architecture/03-architectural-patterns/04-microservices-patterns|Microservices Patterns]] — where these are most needed
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|Availability & Reliability]] — what these protect
