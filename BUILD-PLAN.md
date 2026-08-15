# Build Plan

The working queue for the vault, agreed 2026-08-14. Ordered, sized, and honest about what each batch costs. Tick things off as they land.

**Current state:** 912 notes, ~1,080,000 words. This plan adds roughly **110 notes** on the core path, plus **~48** if the CS-theory gaps are folded in.

> **The standing caveat:** almost everything below will be marked `[reference]` — written from sources, not from having built the thing. That's the vault's convention and it should stay visible. [[PRIMETECHIE|Reading is not a rank.]] The `build-your-own-x/` phase exists specifically to convert some of it into the other kind.

---

## Phase 0 — done

- [x] `languages/02-go/` — README + 13 notes, ~14,400 words
- [x] Spring Boot moved to `backend/frameworks/java/`; the `languages/` vs `backend/frameworks/` rule stated
- [x] `languages/03-rust/` — README + 18 notes, ~22,000 words
- [x] `languages/04-c/` — README + 13 notes, ~19,000 words
- [x] `languages/05-cpp/` — README + 15 notes, ~24,000 words
- [x] `backend/frameworks/` — go (6), rust (6), c (4), cpp (5) + READMEs, ~31,000 words
- [x] `foundations/os/` — 12 notes, ~17,000 words
- [x] `foundations/compilers/` — 11 notes, ~16,500 words
- [x] `build-your-own-x/` batch 1 — http-server, git, shell + README, ~6,800 words
- [x] `build-your-own-x/` batch 2 — redis, language, database, ~6,300 words
- [x] `build-your-own-x/` batch 3 — os, container, ~4,400 words. **All 8 guides written; Phase 2 complete**
- [x] `engineering/` created (umbrella) + `01-continuum-mechanics/` — 13 notes, ~19,600 words

---

## Phase 1 — the systems languages

The order is deliberate: Rust first (already queued), then C, then C++. C before C++ because C++ is only comprehensible as a reaction to C, and both before `build-your-own-x/`, because every build guide there assumes you can read a systems language.

### 1.1 `languages/03-rust/` — ✅ **DONE** — README + 18 notes, ~22,000 words
Ownership and borrowing · lifetimes · traits and generics · `Result`/`Option` and the `?` operator · pattern matching · smart pointers (`Box`/`Rc`/`Arc`/`RefCell`) · interior mutability · `unsafe` and what it actually permits · async/await and the runtime split · cargo, crates, workspaces · macros · testing · error-handling crates (`thiserror`/`anyhow`) · performance and zero-cost abstractions

### 1.2 `languages/04-c/` — ✅ **DONE** — README + 13 notes, ~19,000 words
**Explicitly requested: headers.** The translation unit model is the thing nobody explains properly.

Compilation model (preprocess → compile → assemble → link) · **headers, include guards, and why `.h`/`.c` split the way they do** · the preprocessor and macros · types, integer promotion, and `size_t` · pointers and pointer arithmetic · arrays vs pointers (the decay rule) · manual memory: `malloc`/`free`, the heap, and every way to get it wrong · structs, unions, bitfields, padding · strings as `char*` and why that's a security story · the standard library · **undefined behaviour** as its own note · build systems: `make`, `CMake` · debugging: `gdb`, `valgrind`, sanitizers

### 1.3 `languages/05-cpp/` — ✅ **DONE** — README + 15 notes, ~24,000 words
RAII (the central idea) · classes, constructors, the rule of 0/3/5 · references vs pointers · templates and generic programming · the STL: containers, iterators, algorithms · smart pointers and ownership · move semantics and rvalue references · operator overloading · inheritance, virtual dispatch, and the vtable · exceptions and exception safety · `constexpr` and compile-time computation · modern C++ (11→23): what actually changed practice · **modules**, and why headers are still everywhere · concurrency: `std::thread`, `atomic`, the memory model · build and tooling: CMake, package managers

### 1.4 `backend/frameworks/` — ✅ **DONE** — 21 notes + 4 rewritten READMEs, ~31,000 words
Following the [[languages/README|rule]]: frameworks live here, languages live there.

- `go/` (~6) — `net/http` in depth, Chi, Gin, middleware as composition, testing handlers, the stdlib-is-enough argument
- `rust/` (~6) — Axum, `tower` layers, extractors, Actix Web, state and `Arc<AppState>`, async pitfalls
- `c/` (~4) — libmicrohttpd, Kore, Ulfius, civetweb; when a C web server is a real answer and when it's a bad idea
- `cpp/` (~5) — Drogon, Crow, Pistache, oat++, Boost.Beast

---

## Phase 2 — `build-your-own-x/`

**The point of this folder:** language-agnostic build guides. Each file is *"here is everything you'll meet building this, and the order to build it in"* — not a tutorial in one language. Where a step needs a library, suggest options **per language**.

### The shape every file follows

1. **What you're actually building** — and what you're deliberately not
2. **What you need to know before starting** — with links into the vault, and honest notes on what's missing
3. **The build order** — numbered milestones, each independently testable, each producing something that *runs*
4. **Per-language toolkit** — for each milestone, what the stdlib gives you and what a library would, across C/C++/Rust/Go/Python/JS
5. **The parts that will actually bite you** — the hard bits, stated in advance
6. **How to know it works** — test strategy and reference implementations to compare against
7. **Where to stop** — the difference between a learning artefact and a real one

### The files — ~8 guides, longer than normal notes (~2,500 words each)

- [x] **`01-http-server.md`** ✅ — the one to write first, since it's the most tractable. Milestones: raw socket accept loop → request-line parser → header parser → response writer → routing → static files → keep-alive → concurrency → chunked encoding. *Requested example: "build the parser first, then a route."*
- [x] **`02-your-own-git.md`** ✅ — content-addressable store → blob/tree/commit objects → refs → index/staging → commit → log → branch → checkout → diff → merge. Pairs with [[git/01-how-git-works|How Git Actually Works]], which is already written
- [x] **`03-your-own-redis.md`** ✅ — RESP protocol parser → in-memory store → GET/SET → event loop → expiry → more data types → persistence (RDB/AOF) → replication
- [x] **`04-your-own-language.md`** ✅ — lexer → parser/AST → tree-walking interpreter → environments and scope → functions and closures → then either a bytecode VM or a compiler. **Blocked on the compilers gap below**
- [x] **`05-your-own-os.md`** ✅ — bootloader → protected/long mode → VGA or serial output → interrupts → memory management → paging → processes → scheduler → syscalls → filesystem. The longest and hardest; **blocked on the OS gap below**
- [x] **`06-your-own-database.md`** ✅ — pager → B-tree or LSM → record format → a SQL subset parser → query execution → transactions and a WAL
- [x] **`07-your-own-shell.md`** ✅ — the best small one. Read-eval loop → tokenising → `fork`/`exec` → redirection → pipes → job control → builtins
- [x] **`08-your-own-container.md`** ✅ — namespaces → cgroups → chroot/pivot_root → a layered filesystem. Ties [[devops/02-docker/README|Docker]] to what the kernel actually does

Once this folder exists, [[project-ideas|project-ideas.md]]'s "build your own X" tier should link into it rather than duplicating it.

---

## Phase 3 — `engineering/`

Chosen structure: one umbrella with numbered tracks, room to grow.

- [x] **`engineering/01-continuum-mechanics/`** — ✅ **DONE** — 13 notes, ~19,600 words
- [x] **`engineering/02-control-theory/`** — ✅ **DONE** — 13 notes, ~21,000 words
- [x] **`robotics/`** — ✅ **DONE** — 14 notes, ~22,000 words. Built against the 9-note plan its README proposed, with kinematics expanded to five notes as this plan called for (transforms, forward, inverse, Jacobians, dynamics). Note 09 is the robotics-specific control note; theory stays in `engineering/02`

> `robotics/README.md` carried the rule that control-theory notes *"should only be written after something has actually been made to move."* **Honoured, not deleted** — it survives in both new tracks' honest notes, sharpened rather than softened: the robotics README now says outright that its "what actually goes wrong" sections are written from other people's experience, and `project-ideas.md` states the debt explicitly. **Phase 3 is complete.**

---

## The CS-curriculum gaps

Found 2026-08-14 by grep-testing a standard undergraduate syllabus against the vault. **Absent entirely** (0 hits): complexity theory (P vs NP), automata and formal languages, compilers, computer architecture, discrete mathematics, programming-language theory, computer graphics, information theory. **All but the last three are now closed.** **Thin:** operating systems (one note), databases (references only, no course), numerical methods.

The bias is coherent — everything practitioners use, little of what's proved in a lecture hall — but **two of these gaps block Phase 2**, so they're not optional:

- [x] **`foundations/compilers/`** — ✅ **DONE** — 11 notes, ~16,500 words
- [x] **`foundations/os/` buildout** — ✅ **DONE** — 12 notes, ~17,000 words. `fundamentals.md` kept (13 inbound links); numbered course built around it

Worth doing, not blocking:

- [x] **`foundations/theory-of-computation/`** — ✅ **DONE** — 8 notes, ~11,600 words
- [x] **`foundations/computer-architecture/`** — ✅ **DONE** — 12 notes, ~17,400 words (plan said ~10; data representation and performance-method earned their own)
- [x] **`foundations/discrete-math/`** — ✅ **DONE** — 8 notes, ~11,300 words. Recurrences and the Master Theorem folded into `05-induction-and-recursion` rather than a separate note
- [ ] **`databases/` → a course** — **the last big unstructured domain**, and now the only unticked item in this file. Four reference files (`sql-`, `mysql-`, `nosql-`, `database-design-reference`) plus an `interview/` folder, no numbered course. Note that `foundations/discrete-math/04` now leans on it for the relational-model connection

Deferred, honestly: computer graphics, information theory, PL theory. Real subjects, no current pull.

---

## Suggested order

Each line is roughly one working session.

| # | Batch | Notes |
|---|---|---|
| ~~1~~ | ~~`languages/03-rust/`~~ ✅ | 18 |
| ~~2~~ | ~~`languages/04-c/`~~ ✅ | 13 |
| ~~3~~ | ~~`languages/05-cpp/`~~ ✅ | 15 |
| ~~4~~ | ~~`backend/frameworks/`~~ ✅ | 21 |
| ~~5~~ | ~~`foundations/os/`~~ ✅ | 12 |
| ~~6~~ | ~~`foundations/compilers/`~~ ✅ | 11 |
| ~~7~~ | ~~`build-your-own-x/` — 01, 02, 07~~ ✅ | 3 |
| ~~8~~ | ~~`build-your-own-x/` — 03, 04, 06~~ ✅ | 3 |
| ~~9~~ | ~~`build-your-own-x/` — 05, 08~~ ✅ | 2 |
| ~~10~~ | ~~`engineering/01-continuum-mechanics/`~~ ✅ | 13 |
| ~~11~~ | ~~`engineering/02-control-theory/`~~ ✅ | 13 |
| ~~12~~ | ~~`robotics/` buildout~~ ✅ | 14 |
| ~~13~~ | ~~*optional* — theory of computation, computer architecture, discrete math~~ ✅ | 28 |

Batches 5 and 6 are inserted before `build-your-own-x/` because the OS and compilers guides are blocked without them. Everything else follows the order requested.

**Every batch in this plan is now complete.** What remains is `databases/` → a course (above), and the three deferred subjects (computer graphics, information theory, PL theory) — none of which anyone has asked for.

**The standing debt is reps, not notes.** `engineering/`, `robotics/` and all three CS-theory domains are `[reference]`: read and assembled, never validated by building. Each one's README names what would close its own gap, and [[project-ideas|project-ideas]] carries the list.

---

## Related
- [[project-ideas|Project Ideas]] — the tiered build list this plan's Phase 2 goes deep on
- [[PRIMETECHIE|The Primetechie Path]] — the ranks these are meant to serve
- [[README|Vault README]] — the current map
