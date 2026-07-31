# Languages

Language-specific deep dives that sit alongside [[../backend/README|backend/]] and [[../frontend/README|frontend/]]. Where those two are organized by *framework* (Express, Nest, React, GSAP...), this domain is organized by *language* — the parts of a language and its core ecosystem that aren't specific to any one framework built on top of it.

## Structure

1. [[languages/01-java/README|01-java/]] — **[Beginner → Advanced]** — a full course organized into six themed sections: the **language** (fundamentals, OOP, generics, collections, functional, exceptions, modern Java, core APIs) → **JVM & concurrency** (internals, GC, the memory model, virtual threads) → **tooling** (build/DI/testing/logging) → **persistence** → **web & API** → **applied systems**. Topic coverage cross-referenced against [roadmap.sh Java](https://roadmap.sh/java); the applied-systems material is distilled from two real SIWES projects (a Spring Boot payment sandbox and a high-throughput CSV→MySQL pipeline over RabbitMQ).

Other languages (Go, Python at depth, Kotlin, etc.) would slot in as further numbered tracks if/when notes get written for them.

## Related
- [[backend/README|backend]] — Node.js/Express/Nest, the JS-ecosystem counterpart to this domain
- [[concepts/01-backend/README|backend concepts]] — framework-agnostic ideas these tracks implement
- [[projects/record-id-generator-java/learning/01-java-fundamentals|record-id-generator-java learning notes]] and [[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|direct-debit-sandbox-java learning notes]] — the original project-embedded notes the applied-systems section was built from. Kept in place as the full narrative/debugging-log version; this domain is the distilled reference version.
