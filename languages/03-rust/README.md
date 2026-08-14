# Rust

A language built on a single bet: that "manual memory management *or* a garbage collector" was a false choice. Rust gets memory safety at compile time, with no GC and no runtime cost, by making ownership part of the type system.

**~22,000 words across 18 notes.** Built August 2026, cross-referenced against [roadmap.sh Rust](https://roadmap.sh/rust).

**Source: `[reference]`.** No Rust project in this vault yet, and nothing here has been argued with under real constraints. The first Rust build belongs in [[project-ideas|Project Ideas]] before these notes claim to be knowledge — [[PRIMETECHIE|reading is not a rank]].

> **The thing worth understanding above everything else:** ownership was designed to manage memory, and it turned out to eliminate **data races** for free. The borrow rule — one mutable reference *or* many immutable ones — makes a data race unrepresentable. Java and Go are memory-safe and will still let two threads corrupt a field. That accident is the most interesting result in the language's design, and it's why note 13 is called what it is.

## Reading order

Notes 3, 4 and 5 are the hard part and everything after assumes them. Don't skip ahead; do expect them to take longer than the rest combined.

**Getting oriented**

1. [[languages/03-rust/01-why-rust-and-the-toolchain|Why Rust, and the Toolchain]] — **[Beginner]** — the problem no mainstream language had solved, what it costs, `cargo`, and the compiler as a teaching tool
2. [[languages/03-rust/02-language-fundamentals|Language Fundamentals]] — **[Beginner]** — bindings, immutability by default, shadowing, expressions-as-values, and the two string types

**The hard part — read slowly**

3. [[languages/03-rust/03-ownership|Ownership]] — **[Beginner → Intermediate]** — three rules, move semantics, `Copy`, and `Drop`. The foundation for all of it
4. [[languages/03-rust/04-borrowing-and-references|Borrowing and References]] — **[Beginner → Intermediate]** — the one rule, non-lexical lifetimes, slices, and **the four patterns that get you unstuck**
5. [[languages/03-rust/05-lifetimes|Lifetimes]] — **[Intermediate]** — the scariest syntax, which only *describes* relationships rather than changing them. Elision means you rarely write them

**Modelling data**

6. [[languages/03-rust/06-structs-enums-and-pattern-matching|Structs, Enums and Pattern Matching]] — **[Beginner → Intermediate]** — sum types, exhaustive `match`, and making invalid states unrepresentable
7. [[languages/03-rust/07-option-and-result|Option and Result]] — **[Beginner → Intermediate]** — no null, no exceptions, and the `?` operator
8. [[languages/03-rust/08-error-handling-in-practice|Error Handling in Practice]] — **[Intermediate]** — `thiserror` for libraries, `anyhow` for applications, and errors as HTTP responses

**Abstraction**

9. [[languages/03-rust/09-traits|Traits]] — **[Intermediate]** — shared behaviour without inheritance, the orphan rule, static vs dynamic dispatch
10. [[languages/03-rust/10-generics-and-trait-bounds|Generics and Trait Bounds]] — **[Intermediate]** — monomorphisation, closure traits, const generics
11. [[languages/03-rust/11-collections-and-iterators|Collections and Iterators]] — **[Intermediate]** — the best-designed trait in the library, and why chains are as fast as loops

**When the compiler can't prove it**

12. [[languages/03-rust/12-smart-pointers-and-interior-mutability|Smart Pointers and Interior Mutability]] — **[Intermediate → Advanced]** — `Box`, `Rc`, `RefCell`, `Weak`, and moving the borrow check to runtime

**Concurrency**

13. [[languages/03-rust/13-concurrency|Concurrency]] — **[Intermediate → Advanced]** — `Send`/`Sync`, `Arc<Mutex<T>>`, channels, `rayon`, and what "fearless" does and doesn't mean
14. [[languages/03-rust/14-async-and-tokio|Async and Tokio]] — **[Advanced]** — futures, why the runtime isn't in the language, and the three mistakes that make async slower than blocking

**The deep end**

15. [[languages/03-rust/15-unsafe-and-ffi|Unsafe and FFI]] — **[Advanced]** — the five things `unsafe` actually permits, safe abstractions, and calling C
16. [[languages/03-rust/16-modules-cargo-and-testing|Modules, Cargo and Testing]] — **[Intermediate]** — visibility, workspaces, feature flags, and testing that's mostly built in
17. [[languages/03-rust/17-macros|Macros]] — **[Advanced]** — `macro_rules!`, derive macros, hygiene, and when a function would do
18. [[languages/03-rust/18-performance-and-zero-cost|Performance and Zero-Cost Abstractions]] — **[Advanced]** — what's genuinely free, what isn't, and measuring instead of guessing

## Where the frameworks are

Per [[languages/README|the vault rule]] — `languages/` teaches the language, `backend/frameworks/` teaches the frameworks:

### → **[[backend/frameworks/rust/README|backend/frameworks/rust/]]** — Axum, Actix Web, `tower`

## Rust vs Go, since both now live here

They're often presented as competitors and mostly aren't.

| | [[languages/02-go/README\|Go]] | Rust |
|---|---|---|
| Memory safety | GC | compile-time ownership |
| Learning curve | days | weeks to months |
| Compile speed | very fast | slow |
| Concurrency | goroutines, blocking style, no colouring | async/await + threads, colouring |
| Errors | `if err != nil` | `Result` + `?` |
| Best for | services, infra tooling, team throughput | systems, latency-critical, embedded |

**Go optimises for the team; Rust optimises for the machine and the compiler's ability to prove things.** Pick Go when the deadline and the headcount matter more than the last 10%. Pick Rust when a pause, a crash, or a memory bug is genuinely unacceptable.

## Known gaps

- **No project.** The largest gap, and the one that matters
- **Embedded / `no_std`** — a major Rust use case, entirely absent. Would connect to [[hardware/README|hardware/]]
- **WebAssembly** — one of Rust's strongest niches, not covered
- **Advanced type-level programming** — GATs, HRTBs beyond a mention, typestate patterns
- **`serde` in depth** — the most-used crate in the ecosystem gets only passing coverage

---

## Related
- [[backend/frameworks/rust/README|Rust Backends]] — Axum and Actix
- [[languages/README|Languages]] — the language/framework split rule
- [[languages/02-go/README|Go]] · [[languages/01-java/README|Java]] — the other language courses
- [[BUILD-PLAN|Build Plan]] — what's queued next
- [[project-ideas|Project Ideas]] — where the first Rust build should be logged
