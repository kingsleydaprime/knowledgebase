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
4. [[languages/04-c/README|04-c/]] — **[Beginner → Advanced]** — 13 notes: the compilation model, **headers and the translation unit**, the preprocessor, integer promotion, pointers, array decay and strings, manual memory, struct layout, the (small) standard library, **undefined behaviour**, modular C, build systems, and the tooling that substitutes for a safety net. **[reference]**
5. [[languages/05-cpp/README|05-cpp/]] — **[Beginner → Advanced]** — 15 notes: RAII (the central idea), references and `const`, the Rule of Zero/Five, smart pointers, virtual dispatch and vtables, operator overloading, templates and concepts, the STL and ranges, exception safety, `constexpr`, the memory model, the modern subset to write, and CMake. **[reference]**

Other languages (Kotlin, Zig) would slot in as further numbered tracks if notes get written for them.
6. [[languages/06-python/README|06-python/]] — **[Beginner → Advanced]** — 14 notes: the toolchain and virtual environments, **the data model** (names bind to objects — the source of most Python surprises), collections and their costs, scope and closures, dunder protocols and dataclasses, generators and laziness, decorators and context managers, gradual typing, EAFP, the import system, the standard library, **the GIL and the three concurrency models**, pytest and ruff, and why CPython is slow. Deliberately excludes the web frameworks ([[backend/frameworks/python/README|backend/frameworks/python/]]) and the numeric stack ([[ai-ml/00-foundations/04-python-and-data-tools/README|ai-ml]]). **[reference]**
7. [[languages/07-csharp/README|07-csharp/]] — **[Beginner → Advanced]** — 13 notes: the .NET naming mess untangled, **value vs reference types and nullable reference types**, records/structs/classes, **LINQ and the `IQueryable` trap**, reified generics and variance, delegates and events-as-leaks, **the async model everyone copied**, GC and `Span<T>`, exception filters, pattern matching, DI as a platform feature, xUnit and Roslyn analyzers, tiered JIT and Native AOT. **Written because it's [[game-development/engines/unity|Unity's language]]** and the vault had none. **[reference]**

## Related
- [[backend/frameworks/README|backend/frameworks/]] — the frameworks these languages host
- [[backend/README|backend course]] — the framework-agnostic concepts those frameworks implement
- [[foundations/dsa/README|foundations/dsa]] — the CS underneath all of them
- [[projects/record-id-generator-java/learning/01-java-fundamentals|record-id-generator]] and [[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|direct-debit-sandbox]] — the project notes the Java track was distilled from
