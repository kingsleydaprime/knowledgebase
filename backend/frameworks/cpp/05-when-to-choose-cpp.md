# When to Choose C++

**[Intermediate]** — The decision, argued honestly against Rust and Go, and the cases where C++ is genuinely the right answer for a service.

## The position, up front

**C++ on the server is defensible far more often than [[backend/frameworks/c/04-when-not-to-use-c|C]].** RAII removes the leak-and-double-free class, containers remove the buffer-overrun class, and `std::string` removes the NUL-termination class — while keeping identical performance.

It is still **not memory-safe**. Use-after-free through a dangling reference, iterator invalidation, object slicing, and data races are all reachable in ordinary modern C++, and nothing checks you. The ~70% memory-safety CVE figure from Microsoft and Google covers C **and** C++.

So the question isn't "is C++ safe enough" — it's "what does C++ give me that a memory-safe language doesn't, and is that worth the exposure?"

## What C++ actually gives you

**An enormous existing ecosystem.** Not web libraries — domain libraries. Eigen, OpenCV, PyTorch's C++ API, CGAL, Boost, every vendor SDK, every physics engine, every codec. If your problem lives in one of these, C++ isn't a preference, it's where the code is.

**Interop with existing C++.** A game engine, a trading system, a simulation, a CAD kernel. Adding HTTP to that process beats adding a second process, an IPC layer, and a serialisation boundary.

**Predictable latency with no GC**, and total control over memory layout. Same as Rust.

**A mature toolchain** — debuggers, profilers, sanitizers, and decades of institutional knowledge about all three.

## What it costs versus Rust

This is the comparison that matters, because they occupy nearly the same niche.

| | C++ | Rust |
|---|---|---|
| Performance | same | same |
| RAII | ✅ | ✅ |
| Memory safety | **by discipline** | **guaranteed** |
| Data races | possible | **impossible** |
| Serialisation | hand-written / macros | `#[derive(Serialize)]` |
| Package management | vcpkg/Conan, awkward | cargo |
| Compile-time query checking | no | sqlx |
| Async story | no shared vocabulary | one `Future` trait |
| Domain libraries | **vast** | growing |
| Existing code | **vast** | growing |

**Rust wins on every axis except the last two — and those two are often decisive.**

The serialisation gap deserves emphasis because it's felt on every endpoint: [[backend/frameworks/cpp/03-json-and-serialisation|C++ has no reflection]], so every struct-to-JSON mapping is written by hand or generated. In Rust it's one derive. For a CRUD-shaped service that's the difference between an afternoon and a week.

**The honest summary: for a *new* service with no existing C++ and no C++-only libraries, Rust is the better choice.** It gives you the same performance with guarantees instead of discipline, and a genuinely better web ecosystem.

## What it costs versus Go

| | C++ | Go |
|---|---|---|
| Raw performance | faster | fast enough, usually |
| GC pauses | none | sub-millisecond |
| Memory footprint | smallest | small |
| Development speed | **slowest here** | **fastest here** |
| Compile time | minutes | seconds |
| Onboarding | months | days |
| Deployment | ~100MB image, dynamic libs | ~10MB static binary |
| Web ecosystem | thin | large |

**Go wins decisively on everything except raw performance and memory footprint**, and Go's GC pauses are irrelevant for the overwhelming majority of services.

If your reason for C++ is "it'll be faster", measure first. Your bottleneck is the database, the network, or your algorithm — both languages spend 95% of a request waiting on I/O.

## The cases where C++ is right

**1. The process is already C++.**

The strongest case by far, and it's about the *process*, not about HTTP. A game server needs an admin API; a trading system needs a control endpoint; a simulation engine needs to expose results. Adding Drogon beats adding a second runtime, a second deployment unit, and a serialisation boundary between them.

**2. The domain libraries are C++.**

Computer vision, numerical computing, physics, geometry, media codecs, hardware SDKs. Calling OpenCV from Go via cgo is a worse boundary than writing the service in C++.

Worth checking first whether an FFI boundary is actually fine — often the C++ is a *library* you call, and the service around it can be anything. That's frequently the better design.

**3. A latency SLO a GC can't meet, on an existing C++ team.**

If you need Rust-class latency and the team knows C++ and not Rust, C++ is a rational choice. The safety gap is real; the retraining cost is also real.

**4. Very large existing C++ codebases.**

Rewrites fail. Extending what exists is usually correct.

## The cases where it isn't

**A new standalone web service.** Use Go, or Rust if you need no-GC.

**"We need performance."** Not a reason on its own. Measure, and check the bottleneck isn't I/O.

**"The team knows C++."** Knowing C++ is not the same as knowing how to write a secure network service in C++. Those are different skills — and the second requires sanitizers in CI, fuzzing, careful async lifetime management, and a reviewer who catches a captured-by-reference lambda.

**A team without strong conventions.** C++ is [[languages/05-cpp/14-modern-cpp-and-modules|several languages at once]], and without an enforced subset a codebase drifts into containing all of them.

## If you do choose it

The things that most reduce the risk, in order of value:

1. **Modern C++ only** — RAII, `unique_ptr`, containers, no raw `new`/`delete`. Enforce with `clang-tidy` (`modernize-*`, `cppcoreguidelines-*`) in CI → [[languages/05-cpp/14-modern-cpp-and-modules|the subset to write]]
2. **Sanitizers in CI** — ASan+UBSan on every test run, TSan separately, `-D_GLIBCXX_DEBUG`
3. **Coroutines over callbacks** — an entire dangling-capture bug class disappears → [[backend/frameworks/cpp/02-async-models-and-asio|asio]]
4. **A battle-tested HTTP layer** — Drogon or Beast, never your own parser
5. **Fuzz anything parsing untrusted input**
6. **A reverse proxy in front** for TLS and malformed-request rejection
7. **`std::expected` factories** so invalid domain objects can't be constructed → [[backend/frameworks/cpp/03-json-and-serialisation|validation]]
8. **Consider gRPC over JSON** for service-to-service — Protobuf's codegen sidesteps the reflection gap entirely

## The framing worth keeping

> **C++'s remaining niche on the server is *extending*, not *starting*.** When the process is already C++ for good reasons, adding HTTP to it is correct. When you're choosing from scratch, the languages that give you the same performance with guarantees — or 90% of the performance with a tenth of the effort — are usually the better answer.
>
> That's not a criticism of C++. It's the same conclusion the industry reached, and it's why new infrastructure is being written in Rust and Go while the enormous existing C++ estate keeps being extended in C++.

The four-language picture, complete:

| Situation | Choose |
|---|---|
| Existing C++ process needs HTTP | **C++** |
| C++-only domain libraries | **C++** |
| New service, latency SLO a GC can't meet | **[[backend/frameworks/rust/README\|Rust]]** |
| New service, correctness critical | **Rust** |
| New service, ordinary requirements, ship soon | **[[backend/frameworks/go/README\|Go]]** |
| Existing C process needs HTTP | **[[backend/frameworks/c/README\|C]]**, or C++ if it compiles |
| Rich domain logic, big team, mature ecosystem | **[[backend/frameworks/java/README\|Spring Boot]]** |

---

## Related
- [[backend/frameworks/cpp/01-drogon-and-the-landscape|Drogon and the Landscape]] — the options if the answer is yes
- [[backend/frameworks/cpp/03-json-and-serialisation|JSON and Serialisation]] — the ergonomic gap, concretely
- [[backend/frameworks/rust/06-production-and-tradeoffs|Rust: Production and Tradeoffs]] — the same argument from the other side
- [[backend/frameworks/c/04-when-not-to-use-c|C: When Not to Use C]]
- [[backend/frameworks/cpp/README|C++ backends]]
