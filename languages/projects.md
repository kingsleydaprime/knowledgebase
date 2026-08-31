# Languages — Projects

*Seven language courses, ~138,000 words, and the honest problem: **reading a language course teaches you its syntax, not its grain.** Every project here is chosen because it forces you into the thing that language is *for* — and is awkward in the others.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

**The meta-rep:** build **the same small program in three languages** — a concurrent web scraper, or a line-oriented log parser. Nothing teaches you what a language *is* like watching the same problem get easy in one and painful in another.

## Java — see the dedicated ladder

Java has the deepest project list in the vault, aimed at the low-latency target: the order-book matching engine, a lock-free ring buffer, JMH + GC tuning. **Those live in [[project-ideas|project-ideas]] under Java / JVM & Systems** — start there, not here.

## Go

- 🟢 **A CLI with real ergonomics** — flags, subcommands, `context` cancellation on Ctrl-C, and useful `--help`. **Done when:** Ctrl-C during work exits cleanly, mid-operation. Exercises: [[languages/02-go/README|Go]].
- 🟡 ⭐ **A concurrent worker pool with backpressure** — bounded channels, `errgroup`, graceful shutdown, and a rate limit. **Done when:** you can kill it mid-flight and no goroutine leaks (verify with `goleak`). **This is Go's whole thesis** — CSP concurrency as a first-class tool.
- 🟡 **A load-testing tool** — concurrent HTTP requests, latency histogram, p50/p95/p99 output. **Done when:** your numbers agree with `hey` or `k6` on the same target.
- 🔴 **Build your own container** — [[build-your-own-shit/08-your-own-container|the guide]] in Go. Namespaces, cgroups, pivot_root.

## Rust

- 🟢 **Fight the borrow checker on purpose** — implement a doubly-linked list. **Done when:** you've hit the wall, then done it properly with `Rc<RefCell<>>` and understood *why* the naive version can't compile. Exercises: [[languages/03-rust/03-ownership|ownership]], [[languages/03-rust/12-smart-pointers-and-interior-mutability|smart pointers]].
- 🟡 ⭐ **A parser, with real error messages** — JSON or a config format, with `Result` all the way and errors that point at the line and column. **Done when:** the errors are ones you'd want to receive. **Rust's `Result`/`?` is at its best here.**
- 🟡 **An async TCP service on Tokio** — a small protocol server with graceful shutdown. **Done when:** you understand why one `.await` in a lock guard deadlocks everything. Exercises: [[languages/03-rust/14-async-and-tokio|async]].
- 🔴 **Build your own memory allocator** — [[build-your-own-shit/11-your-own-memory-allocator|the guide]] in Rust with `unsafe`. **Rust fights you productively here**, and it's the fastest way to internalise what ownership is preventing.

## C

- 🟢 ⭐ **Build your own shell** — [[build-your-own-shit/07-your-own-shell|the guide]]. `fork`/`exec`/`dup2`/pipes, in the language where the syscall *is* the lesson. **The best C project there is.**
- 🟡 **A memory allocator** — [[build-your-own-shit/11-your-own-memory-allocator|the guide]]. **Done when:** `LD_PRELOAD=./myalloc.so ls` works.
- 🟡 **Find your own UB** — write something with a deliberate off-by-one, then find it with ASan, Valgrind and UBSan. **Done when:** you've seen the same bug reported three different ways. Exercises: [[languages/04-c/README|C]].

## C++

- 🟡 **RAII everything** — take a C program that leaks and rewrite it with smart pointers and containers. **Done when:** Valgrind is clean and you deleted every `free`.
- 🟡 ⭐ **Build your own physics engine** — [[build-your-own-shit/12-your-own-physics-engine|the guide]]. C++'s natural home: performance plus abstraction, and **bugs that report themselves visually**.
- 🔴 **A template-heavy container** — implement a `small_vector` with move semantics, allocator awareness, and correct exception safety. **Done when:** it passes a test suite that throws at every allocation point.

## Python

- 🟢 **Solve the exercises you have** — [[languages/06-python/18-practice-exercises|18-practice-exercises]] is already written. Do it.
- 🟢 ⭐ **Break the data model on purpose** — mutable default arguments, late-binding closures in loops, `is` vs `==`, shared class attributes. **Done when:** you can predict each gotcha's output before running it. Exercises: [[languages/06-python/README|the data model]].
- 🟡 **Prove the GIL to yourself** — the same CPU-bound work with threads, `multiprocessing`, and `asyncio`. **Done when:** you can explain from your own timings why threads didn't help. Exercises: [[languages/06-python/README|the GIL]].
- 🟡 **A decorator library** — retry with backoff, caching, and timing, all preserving signatures with `functools.wraps`. **Done when:** `help()` on a decorated function still shows the right signature.

## C#

- 🟡 **An async pipeline with `IAsyncEnumerable`** — stream, transform, cancel. **Done when:** cancellation propagates end to end. Exercises: [[languages/07-csharp/README|C#]].
- 🟡 ⭐ **A Unity game jam entry** — the reason [[languages/07-csharp/README|C#]] is in this vault. Ship something in 48 hours → [[game-development/README|game development]].
- 🟡 **Zero-allocation parsing with `Span<T>`** — parse a large file with no heap allocations on the hot path. **Done when:** a profiler shows zero Gen0 collections during parsing.

## If you only do one

**The same program in three languages.** It's a weekend, and it converts seven separate courses into one comparative understanding — which is the thing that actually makes you good at picking tools.

## Related
- [[languages/README|the languages index]]
- [[build-your-own-shit/README|build-your-own-shit]] — most guides name the right language for the lesson
- [[project-ideas|Project Ideas]] — the vault-wide index
