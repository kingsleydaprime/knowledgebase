# Languages

Language-specific deep dives. Where [[backend/README|backend/]] and [[frontend/README|frontend/]] are organised by *framework*, this domain is organised by *language* — the parts of a language and its core ecosystem that aren't specific to any one framework built on top of it.

## The rule

> **`languages/` teaches the language. `backend/frameworks/` teaches the frameworks built on it.**

So the JVM, goroutines, the borrow checker, generics, testing and tooling live here. Spring Boot, Gin, Axum, Express and NestJS live in [[backend/frameworks/README|backend/frameworks/]], where they can be compared against each other instead of being filed under the language they happen to be written in.

That comparison is the whole point of the split. Spring's `@RestController`/`@Service` and Nest's `@Controller`/`@Injectable` are the same idea in different spelling — obvious when they share a folder, invisible when they don't.

Applied in August 2026 by **moving** (not copying) Java's Spring Boot material out of `languages/01-java/05-web-and-api/` into [[backend/frameworks/java/README|backend/frameworks/java/]]. Go and Rust follow the same shape from the start.

## Tracks

1. [[languages/01-java/README|01-java/]] — **[Beginner → Advanced]** — a full course in six themed sections: the **language** (fundamentals, OOP, generics, collections, functional, exceptions, modern Java, core APIs) → **JVM & concurrency** (internals, GC, the memory model, virtual threads) → **tooling** (build/DI/testing/logging) → **persistence** → *web & API ([[backend/frameworks/java/README|now in backend/]])* → **applied systems**. Cross-referenced against [roadmap.sh Java](https://roadmap.sh/java); the applied-systems material is distilled from two real SIWES projects.
2. [[languages/02-go/README|02-go/]] — **[Beginner → Advanced]** — 13 notes: the toolchain, the type system, slices and maps properly, interfaces and implicit satisfaction, errors as values, goroutines and channels, concurrency patterns, `context`, generics, the standard library, testing, modules, and the runtime. **[reference]**
3. [[languages/03-rust/README|03-rust/]] — **[Beginner → Advanced]** — 18 notes: ownership, borrowing and lifetimes (the hard part), sum types and exhaustive matching, `Result` and `?`, traits and monomorphised generics, iterators, smart pointers, `Send`/`Sync` concurrency, async and Tokio, `unsafe` and FFI, macros, and what "zero-cost" actually claims. **[reference]**

Other languages (Python at depth, Kotlin, Zig) would slot in as further numbered tracks if notes get written for them.

## Related
- [[backend/frameworks/README|backend/frameworks/]] — the frameworks these languages host
- [[backend/README|backend course]] — the framework-agnostic concepts those frameworks implement
- [[foundations/dsa/README|foundations/dsa]] — the CS underneath all of them
- [[projects/record-id-generator-java/learning/01-java-fundamentals|record-id-generator]] and [[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|direct-debit-sandbox]] — the project notes the Java track was distilled from
