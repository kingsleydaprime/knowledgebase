# Runtime & Concurrency Models

**[Intermediate]** — **the most useful note in this course**, because it explains *why* backend frameworks differ. Once you know which concurrency model a framework sits on, most of its API design, its performance characteristics, and its failure modes follow. This is the note that makes [[backend/frameworks/README|the frameworks folder]] make sense.

## The kid version first

A restaurant with one waiter and many tables.

- **Thread-per-request:** hire one waiter per table. Simple — each waiter follows their table start to finish. But waiters are expensive, and most of the time they're *standing still waiting for the kitchen*.
- **Event loop:** one waiter, moving constantly. Take an order, hand it to the kitchen, immediately go to the next table. Come back when food is ready. Enormously efficient — **until one customer asks the waiter to sit and do their taxes**, and every other table waits.
- **Green threads / coroutines:** it *looks* like one waiter per table (easy to write), but the restaurant secretly reassigns them whenever one is idle. Best of both — you write the simple version, the runtime runs the efficient one.

That's the whole taxonomy. Everything below is detail.

## The three models

| | **Thread-per-request** | **Event loop** | **Green threads / async** |
|---|---|---|---|
| Concurrency unit | OS thread | callback / task on one thread | lightweight task, M:N onto threads |
| Cost per connection | ~1 MB stack + scheduler | a closure (bytes) | a few KB |
| Blocking a unit | fine — others run | **catastrophic** — all stall | fine — runtime parks it |
| Code style | sequential, easy | callbacks / promises | sequential, easy |
| CPU-bound work | fine | must move off-thread | needs care |
| Examples | Java (pre-Loom), Rails, Django (WSGI), PHP | **Node.js**, nginx, Redis | Go, Java 21+ (Loom), Rust (tokio), Python asyncio, Elixir |

### Thread-per-request

Each request gets an OS thread. Blocking is *free* from the programmer's view — `db.query()` just waits and the OS schedules something else.

The cost is per-connection, not per-work: 10,000 connections means 10,000 threads means ~10 GB of stacks plus heavy context switching, when most are idle. That's the **C10K problem**. → [[foundations/networking/09-sockets-and-the-network-api|sockets]]

### Event loop

One thread, an OS readiness API underneath (`epoll`/`kqueue`), and a queue of callbacks. Handles enormous connection counts on one core because idle connections cost almost nothing.

**The defining constraint: any synchronous work blocks everything.** Not "slows" — *blocks*. A 200ms `JSON.parse` doesn't make one request slow; it makes every request that arrives during those 200ms slow. This produces the signature **p99 spike with a flat p50 and low CPU**, and it is the single most important thing to know about operating Node. → [[backend/interview/01-production-debugging|p99 debugging]]

Everything distinctive about Node follows from this one fact: async-by-default APIs, `worker_threads` for CPU work, `cluster` for multi-core, the cultural rule "never block the event loop," and why a `Sync` suffix in a library is a red flag on a server.

### Green threads / coroutines

The runtime multiplexes many lightweight tasks onto few OS threads, parking a task when it blocks on I/O and resuming it later.

**You write blocking-style code and get event-loop efficiency.** Goroutines have always worked this way; Java 21's virtual threads brought it to the JVM; Rust and Python express it as `async`/`await`.

The key realisation: **the programming model (sequential, readable, debuggable) and the execution model (multiplexed onto few threads) never had to match.** We only conflated them because runtimes couldn't separate them. Once one can, thread-per-request comes back — at a million threads.

Two caveats: the "coloured functions" problem in `async`/`await` languages (an async function can only be called from async code, so the ecosystem splits in two — Go and Loom avoid this), and CPU-bound work still needs real parallelism.

## Why this determines framework design

Read a framework's API and you can usually infer its model:

- **Everything returns a promise/future, nothing is synchronous** → event loop or async runtime. (Express, NestJS, FastAPI, Axum)
- **Handlers look synchronous and blocking is fine** → thread-per-request or green threads. (Spring MVC, Django, Rails, Go's `net/http`)
- **There's a separate "reactive" variant** → the framework was built thread-per-request and bolted on an event-loop option. (Spring MVC vs WebFlux — and note that **Loom largely removes the reason to use WebFlux**, which is a live debate worth knowing.)

It also determines **how you scale**: an event-loop runtime is one core per process, so you scale with processes/containers (`cluster`, or N replicas). A thread-per-request or green-thread runtime uses all cores in one process, so you scale up before you scale out.

And **how you tune**: for thread-per-request, thread-pool size is the dial. For an event loop, the dial is *"what's blocking?"* plus process count. For green threads, usually nothing — which is the point.

## The things that bite, per model

- **Event loop:** sync work on the hot path; an unbounded `Promise.all` swamping a downstream; libuv's thread pool defaulting to **4** (so heavy `fs`/`pbkdf2` bottlenecks while the loop looks idle); microtask starvation.
- **Thread-per-request:** pool exhaustion under a slow dependency — every thread parked waiting, so the service is dead while CPU is idle. **The fix is timeouts and bulkheads, not a bigger pool.**
- **Green threads:** unbounded task spawning (cheap tasks make it easy to create millions); pinning (Java's `synchronized` pinned virtual threads before JDK 24); blocking calls that the runtime can't intercept, e.g. a native driver.

**Common to all three:** your **connection pool** is usually the real concurrency limit. A pool of 10 caps you at 10 concurrent queries regardless of how many threads, tasks, or callbacks you have. Time spent waiting for a connection is invisible unless you instrument it — and it's a top cause of mysterious latency.

## Key insight

A backend framework is mostly **a set of ergonomic choices made on top of one concurrency model**, and the model is the part that actually determines behaviour under load. Learn the three models and frameworks stop being twenty things to memorise: they become three things you understand and twenty vocabularies. It also tells you what to worry about on day one — *"what happens here if something blocks?"* has a different answer in Nest than in Spring, and that difference is the whole reason both exist.

## Related
- [[backend/frameworks/README|frameworks/]] — each framework's model, named
- [[foundations/networking/09-sockets-and-the-network-api|Sockets & the Network API]] — C10K, `select`→`epoll`→`io_uring` from the OS side
- [[foundations/os/interview/01-processes-memory-and-io|OS: blocking vs non-blocking vs async I/O]]
- [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|Virtual Threads (Java)]] · [[backend/interview/02-node-runtime-and-api|Node runtime interview]]
