# Build Plan

The working queue for the vault, agreed 2026-08-14. Ordered, sized, and honest about what each batch costs. Tick things off as they land.

**Current state:** 1,086 notes, ~1,247,000 words (Phase 5k, 2026-08-24). This plan adds roughly **110 notes** on the core path, plus **~48** if the CS-theory gaps are folded in.

> **The standing caveat:** almost everything below will be marked `[reference]` — written from sources, not from having built the thing. That's the vault's convention and it should stay visible. [[PRIMETECHIE|Reading is not a rank.]] The `build-your-own-shit/` phase exists specifically to convert some of it into the other kind.

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
- [x] `build-your-own-shit/` batch 1 — http-server, git, shell + README, ~6,800 words
- [x] `build-your-own-shit/` batch 2 — redis, language, database, ~6,300 words
- [x] `build-your-own-shit/` batch 3 — os, container, ~4,400 words. **All 8 guides written; Phase 2 complete**
- [x] `engineering/` created (umbrella) + `01-continuum-mechanics/` — 13 notes, ~19,600 words

---

## Phase 1 — the systems languages

The order is deliberate: Rust first (already queued), then C, then C++. C before C++ because C++ is only comprehensible as a reaction to C, and both before `build-your-own-shit/`, because every build guide there assumes you can read a systems language.

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

## Phase 2 — `build-your-own-shit/`

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

Once this folder exists, [[project-ideas|project-ideas.md]]'s "build your own shit" tier should link into it rather than duplicating it.

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
- [x] **`databases/` → a course** — ✅ **DONE** — 12 notes, ~17,900 words, plus a README. **Additive**: all four reference files kept (≈40 inbound links) and positioned as the syntax layer; the course is the *internals* layer they lacked — pages, B-trees, LSM, the query pipeline, MVCC, WAL, replication, operations

~~Deferred, honestly: computer graphics, information theory, PL theory.~~ **Un-deferred 2026-08-16** — and a re-audit of every README's stated-gaps section found two *more* load-bearing than any of the three:

## Phase 4 — the gaps the vault itself flagged

Ordered by dependency. Chosen 2026-08-16 after grepping every README for its own "known gaps" section.

- [x] **`foundations/numerical-methods/`** — ✅ **DONE** — 10 notes, ~14,500 words. **Was the biggest structural hole.** `engineering/README` says "not yet written; FEM and CFD both need it"; continuum mechanics lists quadrature/linear solvers/stability as genuine gaps; control theory needs discretisation; ML optimisation leans on conditioning. Floating point → root finding → linear systems → eigenvalues → interpolation → quadrature → ODEs → PDEs → optimisation
- [x] **`foundations/information-theory/`** — ✅ **DONE** — 7 notes, ~10,600 words. **Connective tissue, not a new silo.** Cross-entropy and KL divergence are used throughout `ai-ml/` and never explained; key entropy is referenced in discrete-math 06; Shannon capacity belongs under networking; ECC under number theory
- [x] **`foundations/gpu-and-parallel-computing/`** — ✅ **DONE** — 7 notes, ~10,800 words. Closes the gap flagged in `computer-architecture/README` ("a genuine gap given the ML material in this vault"). **`ai-ml/` is 98 notes with nothing explaining the hardware underneath.** SIMT/warps → coalescing → occupancy → the CUDA model → why matmul maps well → tensor cores → transfer cost
- [x] **`foundations/computer-graphics/`** — ✅ **DONE** — 9 notes, ~13,000 words. Needed numerical methods and GPU first. The transform pipeline (reuses `robotics/04`), rasterisation, shading, ray tracing, shaders
- [x] **`foundations/programming-language-theory/`** — ✅ **DONE** — 7 notes, ~10,200 words. Lambda calculus, formal type systems, operational semantics, Curry–Howard (already name-dropped in `discrete-math/02`). Stands on the compilers course

---

## Phase 5 — the gaps two source courses found

Added 2026-08-22. Both from freeCodeCamp transcripts in `sources/`, gap-analysed against the vault before anything was written — **most of what the IT-fundamentals course covers (IP addressing, subnetting, TCP/IP, DNS, firewalls, NAT, Linux, VPC/security groups, CI/CD) was already here and was deliberately not duplicated.** Three folders survived the filter.

- [x] **`foundations/programming-fundamentals/`** — ✅ **DONE** — README + 12 notes, ~13,700 words. **The vault had no way in.** 900+ notes assumed you could already read code; `using-ai/` was written as the on-ramp for non-programmers into *AI*, and there was no equivalent into *programming*. Language-agnostic: what a program is → translation → tooling → syntax → variables/types → control flow → collections → functions → recursion/the call stack → errors/debugging → planning → what to build next
- [x] **`devops/00-the-physical-layer/`** — ✅ **DONE** — README + 4 notes, ~5,100 words. The gap was exactly one layer wide: `hardware/` covers boards, `devops/03-cloud` opens with "someone else's computers" and never mentions the computers. Servers → virtualisation/hypervisors → data centres → the leaf-spine network. **`hot aisle` had 0 hits vault-wide**
- [x] **`devops/12-sre-and-platform-engineering/`** — ✅ **DONE** — README + 4 notes, ~5,400 words. `devops/` had eleven sections of *tools* and two paragraphs of *disciplines*. **`toil` had 0 hits**; IDPs appeared once; DevSecOps had no note. The evolution spine (waterfall → agile → DevOps → SRE → platform → DevSecOps, each fixing the last one's bottleneck) → SRE practices → platform engineering → DevSecOps. Deliberately does **not** restate SLO/error-budget material already in `10-observability/`

**Total so far: 3 READMEs + 20 notes, ~27,400 words.**

### Phase 5b — the follow-on gaps (2026-08-22)

Found in the same session, from a third source (`sources/100 CS concepts explained.md` — **mostly redundant**; 95% of it was already covered at greater depth) and from a direct audit of `languages/` and `backend/frameworks/`.

- [x] **`foundations/programming-fundamentals/` notes 13–14** — ✅ **DONE** — ~2,200 words. **Closes the gap this course's own README declared.** The original call — "OOP belongs in `languages/`" — was wrong: OOP is language-*flavoured*, not language-specific, and omitting it stopped the course one concept short of where every real codebase starts. Objects and classes; programming paradigms (with expression-vs-statement, which was absent vault-wide outside `compilers/`)
- [x] **`languages/06-python/`** — ✅ **DONE** — README + 14 notes, ~12,600 words. **`languages/README` had listed "Python at depth" as a track that would slot in if notes got written.** They hadn't been — despite the entire `ai-ml/` domain being written in Python and `devops/` assuming it for automation. **The vault taught Python-the-tool everywhere and Python-the-language nowhere.** Deliberately excludes the web frameworks (below) and the numeric stack (`ai-ml/00-foundations/04-python-and-data-tools/`), per the `languages/` rule
- [x] **`backend/frameworks/python/`** — ✅ **DONE** — rewritten README + 3 notes, ~2,650 words. Was scaffold-only. Took the **folder shape** its own index predicted it would, since FastAPI, Django and Flask are genuinely co-equal subjects
- [x] **`devops/01-linux/12-bash-scripting`** — extended with repo-wide scripting technique (`fold`, assertion-guarded rewrites, verification passes). **Not a new note** — the heredoc and `python3 -` material was already there, so this extends rather than restates
- [x] **`.obsidian/app.json`** — `userIgnoreFilters` for `quartz/` and `sources/`. **487 stray `.md` files in `quartz/node_modules/`** were polluting the graph and search. Not committed — `.obsidian/` is gitignored

**Phase 5 total: 5 READMEs + 39 notes, ~47,000 words**, plus ~1,200 words extending `12-bash-scripting`.

### Phase 5c — the curiosity batch (2026-08-23)

Prompted by a single message naming six directions at once, plus "is the Python course complete" and "borrow from roadmap.sh". **All six became maps, none became an active course** — logged in [[learning/catalogue|the parking lot]], per [[learning/04-one-active-course|the one-active-course rule]].

- [x] **Python roadmap audit** — ✅ notes 15–17 (~2,700 words): files & I/O, regular expressions, asyncio in depth. **All three were named as gaps by the course's own honest note before [roadmap.sh](https://roadmap.sh/python) confirmed them.** README now carries a full three-way roadmap mapping: covered here / covered elsewhere in the vault / deliberately skipped
- [x] **`foundations/systems-engineering/`** — ✅ README + 8 notes, ~8,200 words. **Zero prior hits for INCOSE, MBSE, SysML, requirements engineering or trade studies** — in a vault kept by a systems engineering student. Cuts both ways: it connects the degree to the software, and imports FMEA/fault trees/ICDs/traceability, which software genuinely underuses. **No roadmap.sh roadmap exists** for this; the standards are the syllabus
- [x] **`game-development/`** — ✅ README + 8 notes, ~7,600 words, cross-referenced against [roadmap.sh game-developer](https://roadmap.sh/game-developer). **Deliberately thin** — the roadmap's maths, graphics, physics-integration, spatial-structure and ML topics were already written under `computer-graphics/`, `robotics/`, `numerical-methods/`, `dsa/` and `ai-ml/`. The folder points at them rather than restating
- [x] **`foundations/software-engineering/04`** — ✅ ~1,300 words. The field cut by constraint rather than product area, with **embedded at depth** (the stated interest) and an honest account of which switches are hard
- [x] **`desktop/`** — ✅ README + 1 note + frameworks index + 5 scaffolds, ~2,750 words. Copies the `backend/frameworks/` convention exactly, as requested. No roadmap.sh coverage exists
- [x] **`devops/00-the-physical-layer/05`** — ✅ ~1,100 words. The infrastructure career path on top of the physical-layer notes: the roles, **hands-on-metal vs infrastructure-as-software**, where certs actually help
- [x] **Parking lot + thinking-patterns** — six interests dated and captured; the recurrence of the bundled-asks pattern recorded with evidence

**Deferred, deliberately:** finance / tax / entrepreneurship (deferred by him in the same message — and it isn't a tech domain, so it needs its own shape rather than a course folder) and manufacturing as a business (under-specified; a business question, not a learning one).

**Phase 5c total: 31 files (4 READMEs + 27 notes/scaffolds), ~26,500 words.**

### Phase 5d — exercises (2026-08-23)

**The gap nine separate domain READMEs named independently**, and the only one that genuinely required generation rather than reading. Two courses closed; seven still open.

- [x] **`foundations/programming-fundamentals/` 15–16** — ✅ ~3,550 words. Sixteen exercises, language-agnostic, ~8–12 hours. **The course's own honest note said "this is a reading course with no problems in it" — that no longer applies to it**
- [x] **`languages/06-python/` 18–19** — ✅ ~3,500 words. Eighteen exercises that *reproduce* the gotchas. **Every figure in the solutions was measured on Python 3.14**, not estimated — including one exercise that had to be rewritten because 3.14's constant folding defeated the original demonstration

**Measured while writing, and worth recording:** 4 threads on CPU-bound work ran **2× slower than serial** (5.76 s vs 2.81 s) — stronger than note 12's "no speedup" claim; catastrophic backtracking hit **23 s at n=28**, doubling per character; a generator vs list of 5M items differed by **211,287×** in `getsizeof`.

**Still open — the same gap, in seven other domains:** discrete-math, theory-of-computation, computer-architecture, numerical-methods, GPU/parallel, PL-theory, computer-graphics, information-theory, databases. Each names "exercises" in its own `What's missing` line.

**Phase 5d total: 4 notes, ~7,050 words.**

### Phase 5e — the remaining nine domains (2026-08-23)

**Every domain that named `exercises` in its own `What's missing` line now has them.** Nine pairs, built from each README's own "what would close the gap" list rather than invented.

| Domain | Notes | Shape |
|---|---|---|
| `foundations/computer-architecture` | 13–14 | Measured: cache sizes from timing, matmul, false sharing |
| `foundations/numerical-methods` | 11–12 | Measured: the U-curve, cancellation, Hilbert, Runge |
| `foundations/discrete-math` | 09–10 | Proofs on paper; RSA and counterexamples verified |
| `foundations/theory-of-computation` | 09–10 | Three proofs from scratch + regex engine + SAT solver |
| `foundations/information-theory` | 08–09 | Measured: entropy vs gzip, Huffman on skewed sources |
| `databases` | 13–14 | Measured: 9,327× index speedup, N+1, MVCC, WAL |
| `foundations/gpu-and-parallel-computing` | 08–09 | **Honest no-GPU path**; figures marked as borrowed |
| `foundations/computer-graphics` | 10–11 | Shadertoy + a CPU ray tracer |
| `foundations/programming-language-theory` | 08–09 | Implementations: Algorithm W, progress/preservation |

**Measured while writing, and it changed the material:**

- **The sorted-array branch-prediction result does not reproduce at `-O2`** — 4.0× at `-O0`, ~nothing at `-O2`, because GCC emits branchless code. The exercise now asks you to find the instruction that explains it, which teaches more than the original
- **Matrix multiply: 6.5× at N=1024, only 2.4× at N=512** — the effect appears when the working set exceeds L3, so benchmarking on small inputs misleads
- **gzip beat the order-0 entropy "floor" by ~2×** on a real file, which forced the correct statement: entropy is the floor *for a given source model*
- **A SQLite index gave 9,327×** on 200 lookups over 500k rows
- **`foundations/information-theory/README` claimed Huffman loses "~7× at $p=0.9$" — measured, that's 2.1×; 7.1× is $p=0.98$.** Corrected in place

**Phase 5e total: 18 notes, ~21,900 words.**

### Phase 5f — the public-resource pass (2026-08-23)

**Reframed by him mid-session:** the vault is published, so it serves readers on paths that aren't his. That changes what "missing" means — a stub that's a fine personal placeholder is a dead end for a stranger.

- [x] **Interview banks, where the reference material was deepest and the bank thinnest** — ✅ 4 notes + a new bank, ~5,000 words. **Java (parked) had 3 interview notes; frontend (his actual target) had 1.** Now: `frontend/interview` 1→**3** (the JS/TS language round; state/data/a11y/RSC), `concepts/interview` 1→**2** (patterns, code review, testing theatre, when duplication beats abstraction), and a new **`languages/06-python/interview`**
- [x] **`ai-automation/`** — ✅ README + 6 notes, ~5,500 words. **The only genuinely empty domain in the vault** — a 219-word stub carrying a 6-note plan since July. The plan was good; these are that plan, written

**Deliberately not done:** interview banks for `game-development`, `desktop`, `systems-engineering` and the CS-theory spine. [[INTERVIEW|INTERVIEW.md]]'s own stated principle is that **"an interview bank for a subject you haven't practised would be memorisation, not preparation"** — that reasoning still holds, and silently violating it to make a table look complete would be the wrong kind of completeness.

**Phase 5f total: 12 files, ~12,200 words.**

### Phase 5g — depth on request (2026-08-23)

**Two asks: make game development a real track rather than a map, and add astronomy for someone else.** The first exposed a dependency the vault didn't have.

- [x] **`game-development/` → a full track** — ✅ engines/ (4), interview/ (2), a project-ideas tier, README rewritten. **Honest audit first: it had no projects, no interview bank, no per-engine structure — it was a map, and I'd said so.** Now ~12,550 words
- [x] **`languages/07-csharp/`** — ✅ README + 13 notes, ~9,600 words. **C# was absent from the vault entirely**, so the game track pointed at nothing for Unity, and `languages/` had a Java-shaped hole where a reader would compare. Value/reference types, nullable refs, records, LINQ, reified generics, async, GC and `Span<T>`, pattern matching, DI, tiered JIT/AOT
- [x] **`astronomy/`** — ✅ README + 10 notes, ~9,300 words. Written for a reader with no physics and no other domain in this vault. **Note 09 handles astrology honestly** — the two-millennia shared history (Ptolemy and Kepler practised both), what a natal chart actually contains, the Carlson and Dean–Kelly studies, and **the six psychological mechanisms that explain why it feels precise anyway.** Those mechanisms — Barnum, confirmation bias, subjective validation, cold reading — are useful well beyond astrology

**A note on note 09's framing**, since it's the one editorial judgement here worth recording: the vault is rigorous everywhere else, so presenting astrology as a working predictive system would have been dishonest, and refusing to cover it would have been useless to the person who asked. **The treatment is accurate about the evidence, generous about the culture and history, and clear about where the line sits.**

**Phase 5g total: 32 new files, ~25,800 words** (plus a rewritten game-development README and a project-ideas tier).

### Phase 5h — the two dependencies (2026-08-23)

Both asked for directly, and both were things the vault had already flagged against itself.

- [x] **`backend/frameworks/csharp/`** — ✅ README + 4 notes, ~3,500 words. **Named in `languages/07-csharp/README`'s own "what's missing"**, and the frameworks map listed seven languages with C# conspicuously absent right after the language course landed. **Flat notes by concern**, per the folder's own folder-vs-flat test: ASP.NET Core is *the* choice, and Minimal APIs vs MVC are two styles within it. Also updated the cross-stack concept table to seven columns
- [x] **`build-your-own-shit/` 10–12** — ✅ ~2,900 words. Chosen against the folder's stated criterion rather than to pad the list:
  - **Neural network** — **`ai-ml/` is ~98 notes, the largest domain in the vault, and had no build guide.** The most conspicuous absence
  - **Memory allocator** — best effort-to-insight after the container guide; makes `foundations/os/05` and `languages/04-c` concrete
  - **Physics engine** — completes the game-dev track, and it's the rare project where a wrong integrator is *visually* wrong

**Considered and rejected, recorded so it isn't re-litigated:** a text editor (overlaps the shell guide's raw-terminal material), a BitTorrent client (protocol plumbing over insight per hour), a browser engine (too large to finish, which violates the folder's own rule 7 about stopping).

**Phase 5h total: 8 files, ~6,400 words.**

### Phase 5i — the backend depth pass (2026-08-23)

Asked to "fill in the scaffolds — go, rust, c, cpp". **They weren't scaffolds.** The audit is the finding.

- [x] **Corrected a stale index** — ✅ `go/`, `rust/`, `c/` and `cpp/` were labelled `scaffold` in two places while containing **21 notes and ~28,000 words**, written back in Phase 1.4. **The table was never updated, and I edited it twice (for `python/` and `csharp/`) without noticing.** An index that lies about its own contents is worse than one that's incomplete
- [x] **`backend/06-cross-cutting/`** — ✅ README + 7 notes, ~5,400 words. **This was the actual scaffold** — a README that mapped elsewhere, including a row reading *"file uploads — not covered anywhere yet — a genuine gap."* Validation & DTOs · config & secrets · error handling · rate limiting · idempotency & retries · security headers & CORS · file uploads. **Caching, observability and background jobs deliberately still point elsewhere** rather than being duplicated
- [x] **`backend/frameworks/cross-language-recipes`** — ✅ ~1,500 words. The stated ask: *"a full backend in all the languages — rate limiting, headers, auth."* Middleware, rate limiting, JWT verification (**with algorithm pinning**), CORS, **graceful shutdown**, structured logging, and a what-you-get-free matrix — **side by side in Node, Go, Rust, Python, C# and Java**

**Phase 5i total: 9 files, ~7,400 words**, plus three corrected indexes.

### Phase 5j — the frontend restructure (2026-08-23)

**`frontend/` is now a course + `frameworks/`, mirroring `backend/`.** Both moves were already prescribed by the vault: `concepts/README` said *"02-frontend arguably belongs in frontend/. Not moved yet"*, and `frontend/README` said *"distil the recurring material and leave the war stories in projects/, cross-linked — the same split backend uses."*

- [x] **Structure** — ✅ `concepts/02-frontend/` moved in (3 notes → sections 02, 04, 07); `03-gsap`/`04-framer-motion`/`05-threejs`/`01-react`/`02-next` moved under `frameworks/`. **~57 inbound links repointed across 39 files**
- [x] **Course sections `01`–`07`** — ✅ 7 new notes, ~7,000 words: what a frontend is · the browser and the DOM · **hydration and the server boundary** · components and composition · **data fetching and server state** · CSS architecture · **accessibility** · performance
- [x] **`frameworks/react`, `next`, `css`** — ✅ the React model, error boundaries, and **`css/` with Tailwind and Sass** — which appeared nowhere in the vault except one socioboom note
- [x] **`projects/` material left in place, deliberately** — ~44,000 words of React/Next taught against real code. Moving it would strip the project logs of material that reads as a whole, against the [[learning/README|dev-workflow]] principle that both copies are meant to exist. **Indexed from `frameworks/react/` and `frameworks/next/` instead** — the problem was findability, not location

**Two bugs I made and caught, worth recording:** a blunt string replacement rewrote `projects/socioboom/learning/frontend/02-nextjs-app-router` into a `frameworks/` path (it matched inside a *project* path — replacements should have been anchored to `[[`); and sibling short-form links like `[[02-state-management]]` silently began resolving to a **project note** rather than the moved course note. **The link checker reported "all resolve" for the second one** — a link can resolve and still be wrong, which is the limitation of checking existence rather than intent.

- [x] **Testing** — ✅ 2 notes, ~2,200 words. `@testing-library` appeared **nowhere** in the vault outside my own "what's missing" line, and Playwright had no note despite being a stated learning goal. `03-testing-a-frontend` (query priority, waiting properly, **MSW over module mocks**) and `04-end-to-end-with-playwright` — written to explain **why** the structure is what it is, not to list APIs

**Backend testing was already covered** and did not need adding: [[backend/07-practices/02-testing-a-backend|testing a backend]] (1,600 words — Testcontainers, test-data isolation, time, per-layer, auth, flakiness), [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]] for the pyramid and TDD, plus per-language notes in Go, Rust, Java, Python and C#.

**Phase 5j total: 18 files, ~11,600 words**

### Phase 5k — React guide, and two renames (2026-08-24)

- [x] **`build-your-own-shit/13-your-own-react`** — ✅ ~1,300 words. `createElement` → render → a work loop → **fibers** → the render/commit split → reconciliation and keys → function components → **`useState` via an array and a cursor**. **The payoff is step 8:** put a hook inside an `if` and watch state attach to the wrong slot — the hook rules stop being style and become the only thing keeping that array aligned. Optional step 10 rebuilds it with signals, which makes the React-vs-Solid comparison in `frontend/frameworks/README` something you've felt
- [x] **`build-your-own-x/` → `build-your-own-shit/`** — ✅ his call, taken with the trade named: the folder is a **public Quartz URL** (`kingsleydaprime.github.io/knowledgebase/build-your-own-shit/`) on a site the hire track plans to link from a CV. **107 paths and 7 display names across 41 files.** Checked first that the string never appears as a substring of anything else and isn't in any config
- [x] **"Software Engineering — Orientation" → "Introduction to Software Engineering"** — ✅ the domain README title, the root README entry, and **SWE 101's week 1** in the scheme of work. *"Orientation"* described the note's role in the vault; *"Introduction to Software Engineering"* describes what it teaches, which is the right name for the **first topic of the course**

**Phase 5k total: 1 new guide + 2 renames across 45 files.**

- [x] **A table of contents for the scheme of work** — ✅ his observation, and the justification turned out to be structural rather than cosmetic: the file summarised **153 topics with a 12-row block table** and nothing in between, so "where is X taught / when do I hit it" meant scrolling 624 lines. **And the file's own header says "week number = notebook section number" and "index on pages 1–4"** — so the notebook needs an index the source document never produced. **Generated by \** between HTML markers, so it is regenerated rather than hand-maintained and cannot drift from the weeks below it., plus 39 files repointed and 3 indexes rewritten.

**Still open:**  — a course (`01`–`07`) plus `frontend/frameworks/{react,next,css}`, mirroring `backend/`. **The bigger half of that is a *move*, not new writing**: ~44,000 words of React/Next material currently sit in `projects/`, indexed only by `frontend/README`. That's a findability problem, and it's the next batch. Combined 5d+5e: **22 notes, ~29,000 words**, and **no domain README now names exercises as missing.** The standing caveat applies harder than usual to the last one — three of its four notes are organisational disciplines, and a solo project has no dev/ops wall, no ticket queue and no on-call rotation to validate them against.

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
| ~~7~~ | ~~`build-your-own-shit/` — 01, 02, 07~~ ✅ | 3 |
| ~~8~~ | ~~`build-your-own-shit/` — 03, 04, 06~~ ✅ | 3 |
| ~~9~~ | ~~`build-your-own-shit/` — 05, 08~~ ✅ | 2 |
| ~~10~~ | ~~`engineering/01-continuum-mechanics/`~~ ✅ | 13 |
| ~~11~~ | ~~`engineering/02-control-theory/`~~ ✅ | 13 |
| ~~12~~ | ~~`robotics/` buildout~~ ✅ | 14 |
| ~~13~~ | ~~*optional* — theory of computation, computer architecture, discrete math~~ ✅ | 28 |

Batches 5 and 6 are inserted before `build-your-own-shit/` because the OS and compilers guides are blocked without them. Everything else follows the order requested.

**PHASES 0–4 COMPLETE (2026-08-16); Phase 5 added and completed 2026-08-22.** Phase 4 was added from a re-audit of every README's own stated-gaps section — the three long-deferred subjects, plus numerical methods and GPU/parallel computing, which turned out to be more load-bearing than any of them. **All five were built in dependency order in one session: 40 notes, ~59,000 words.**

**Phase 5 (2026-08-22) added three more**, found by gap-analysing two source courses rather than a syllabus — see above. **Nothing is queued.** The remaining gaps each README names are now *within* domains rather than whole missing subjects — and **the vault-wide debt is reps, not notes.** Fourteen domains are `[reference]`; every one names its own remedy, and [[project-ideas|project-ideas]] carries the consolidated list.

**The standing debt is reps, not notes.** `engineering/`, `robotics/` and all three CS-theory domains are `[reference]`: read and assembled, never validated by building. Each one's README names what would close its own gap, and [[project-ideas|project-ideas]] carries the list.

---

## Related
- [[project-ideas|Project Ideas]] — the tiered build list this plan's Phase 2 goes deep on
- [[PRIMETECHIE|The Primetechie Path]] — the ranks these are meant to serve
- [[README|Vault README]] — the current map
