# Web Frameworks

**Source:** **[reference / landscape]** — the payment sandbox used Spring Boot (covered in depth in [[languages/01-java/05-web-and-api/01-spring-boot|Spring Boot]]); this file maps the alternatives from [roadmap.sh Java](https://roadmap.sh/java) so the Spring choice sits in context rather than as the only option known.

## The landscape

| Framework | Optimizes for | Character |
|---|---|---|
| **Spring / Spring Boot** | ecosystem breadth, convention-over-configuration | The default. Enormous ecosystem (Data, Security, Cloud), huge hiring pool, "batteries included." Heavier startup and memory. What the sandbox used. |
| **Quarkus** | cloud-native, fast startup, low memory | Built for containers/serverless. Ahead-of-time compilation and first-class **GraalVM native image** support → millisecond startup and tiny memory footprint, at the cost of some runtime dynamism. |
| **Micronaut** | compile-time DI, fast startup | Does dependency injection and AOP at **compile time** (no runtime reflection), so startup is fast and it's GraalVM-friendly — a direct reaction to Spring's reflection-heavy startup. |
| **Javalin** | simplicity, minimalism | A thin, unopinionated layer over Jetty. Explicit route handlers, no annotation magic — reach for it when Spring is overkill. |
| **Play** | reactive, stateless, JVM-polyglot | Reactive and non-blocking by design, Scala roots, popular for high-concurrency real-time apps. |
| **Helidon / Vert.x** | reactive, low-level control | Vert.x is an event-loop toolkit (Node-like) for maximum-throughput non-blocking services. |

## What actually drives the choice

- **Startup time & memory** — the axis most alternatives compete on. Spring Boot's reflection-based startup costs seconds and hundreds of MB; Quarkus/Micronaut do work at compile time to slash both, which matters enormously for serverless (cold starts) and dense container deployments. **GraalVM native image** compiles a JVM app to a standalone native binary with near-instant startup and low memory — the headline reason Quarkus/Micronaut exist.
- **Blocking vs reactive** — Spring MVC is thread-per-request and blocking (simple to reason about); Spring WebFlux, Play, and Vert.x are reactive/non-blocking (scale to high concurrency on few threads, harder to write and debug). **Virtual threads ([[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|Virtual Threads]]) change this calculus** — they give blocking-style code reactive-style scaling, which undercuts much of the reason to adopt a reactive framework purely for IO concurrency.
- **Ecosystem vs footprint** — Spring's gravity is its ecosystem and hiring pool; you trade startup/memory for that. For most business backends, Spring Boot remains the pragmatic default precisely because everything integrates and everyone knows it.

## Why Spring Boot was right for the sandbox

The payment sandbox needed validation, JSON binding, DI, scheduling, and auto-generated OpenAPI docs — all things Spring Boot provides out of the box with one starter dependency each. Startup time and native-image footprint were irrelevant for a sandbox service. The alternatives above win on *deployment density and cold-start latency*, which a long-running internal sandbox doesn't optimize for — so the "heavy but complete" framework was the correct call, the same kind of fit-the-tool-to-the-workload reasoning as the [[languages/01-java/04-persistence/02-orm-jpa-hibernate|JDBC-over-ORM]] decision.

## Related
- [[languages/01-java/05-web-and-api/01-spring-boot|Spring Boot]] — the framework the projects used, in depth
- [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads|Virtual Threads]] — why the blocking-vs-reactive tradeoff is shifting
- [[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]] — startup/JIT warmup, what native-image compilation sidesteps
