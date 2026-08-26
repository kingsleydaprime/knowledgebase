# Build Your Own Shit

Language-agnostic build guides. Each file is *"here is everything you'll meet building this, and the order to build it in"* — not a tutorial in one language.

**This folder is where the rest of the vault stops being reading.** Every other domain here is `[reference]` — written from sources, not from having built the thing. These guides exist to convert some of it into the other kind. [[PRIMETECHIE|Reading is not a rank.]]

## The shape every guide follows

1. **What you're building** — and what you're deliberately not
2. **What you need first** — with links into the vault, and honest notes on what's missing
3. **The build order** — numbered milestones, each independently testable, **each producing something that runs**
4. **Per-language toolkit** — what the stdlib gives you and what a library would, across C/C++/Rust/Go/Python/JS
5. **The parts that will bite you** — stated in advance, so they cost you an hour rather than an evening
6. **How to know it works** — test strategy, and a reference implementation to compare against
7. **Where to stop** — the line between a learning artefact and a real one

The milestone ordering is the load-bearing part. **You should always have something working**, so each guide is sequenced to keep a runnable artefact at every step rather than a half-built system that only works at the end.

## The guides

**Built:**

1. [[build-your-own-shit/01-http-server|HTTP Server]] — **[Intermediate]** — accept loop → request-line parser → headers → responses → routing → static files → keep-alive → concurrency → chunked encoding. **The best first project**: a weekend, immediate visual feedback, and a real browser as the test
2. [[build-your-own-shit/02-your-own-git|Your Own Git]] — **[Intermediate]** — content-addressable store → blobs → trees → commits → refs → log → index → branches → diff → merge. **Real Git can read your repository**
3. [[build-your-own-shit/03-your-own-redis|Your Own Redis]] — **[Intermediate]** — RESP parser → store → expiry → event loop → data types → RDB/AOF persistence → replication. **The real `redis-cli` connects to it**
4. [[build-your-own-shit/04-your-own-language|Your Own Language]] — **[Intermediate → Advanced]** — lexer → parser → tree-walking interpreter → closures → then a bytecode VM, a type checker, or GC. **The deepest single lesson here**
5. [[build-your-own-shit/05-your-own-os|Your Own OS]] — **[Advanced]** — bootloader → descriptor tables → interrupts → physical memory → paging → user mode → syscalls → processes → filesystem. **Weeks, not a weekend** — and it boots from a USB stick on real hardware
6. [[build-your-own-shit/06-your-own-database|Your Own Database]] — **[Advanced]** — pager → row format → B-tree → SQL parser → execution → **transactions and a WAL**. `kill -9` mid-write and the data survives
7. [[build-your-own-shit/07-your-own-shell|Your Own Shell]] — **[Intermediate]** — read-eval loop → tokenise → `fork`/`exec` → exit status → redirection → builtins → pipelines → jobs. **The best small one**: a few hundred lines, and you can use it
8. [[build-your-own-shit/08-your-own-container|Your Own Container]] — **[Intermediate]** — namespaces → pivot_root → cgroups → user namespaces → overlayfs. **The best effort-to-insight ratio here**: ~200 lines, one evening
9. [[build-your-own-shit/09-your-own-regex-engine|Your Own Regex Engine]] — **[Intermediate]** — parse → Thompson's construction → NFA simulation → subset construction → captures. **One evening, and yours beats Python's `re` by minutes on adversarial input**

10. [[build-your-own-shit/10-your-own-neural-network|Your Own Neural Network]] — **[Intermediate]** — forward pass → loss → backprop by hand → gradient checking → mini-batches → Adam → a tiny autodiff engine. **`loss.backward()` stops being magic**, and it's the guide [[ai-ml/README|ai-ml's]] 98 notes never had
11. [[build-your-own-shit/11-your-own-memory-allocator|Your Own Memory Allocator]] — **[Intermediate]** — `sbrk` → bump allocator → headers → free list → splitting → **coalescing** → alignment → `LD_PRELOAD`. **A weekend, and `ls` runs on your `malloc`**
12. [[build-your-own-shit/12-your-own-physics-engine|Your Own Physics Engine]] — **[Intermediate → Advanced]** — fixed timestep → **semi-implicit Euler** → collision → impulses → rotation → friction → iterative solver → broad phase. **The one where the bug reports itself visually**

13. [[build-your-own-shit/13-your-own-react|Your Own React]] — **[Intermediate]** — `createElement` → render → a work loop → **fibers** → render/commit split → reconciliation and keys → function components → **`useState` via an array and a cursor**. ~500 lines, and **the hook rules stop being rules and become consequences**

**All thirteen are written.**

**Three added Aug 2026**, chosen against this folder's own criterion — build a toy version of something you rely on, and the real thing stops being opaque:

- **Neural network** — the largest domain in the vault (`ai-ml/`, ~98 notes) had no build guide at all. The most conspicuous gap
- **Memory allocator** — best effort-to-insight ratio after the container guide, and it makes [[foundations/os/05-memory-allocation|OS memory]] and [[languages/04-c/README|C]] concrete
- **Physics engine** — completes the [[game-development/README|game development track]], and it's the rare project where a wrong integrator is *visible*
- **React** *(added later)* — the frontend equivalent of the language guide, and it explains the hook rules by making you implement the array they depend on

**Considered and not written:** a text editor (overlaps the shell guide's terminal handling), a BitTorrent client (more protocol plumbing than insight per hour), and a browser engine (too large to finish, which breaks rule 7).

## Which to start with

| If you want | Build |
|---|---|
| The fastest satisfying result | **HTTP server** |
| To stop autodiff being magic | **neural network** |
| The best weekend systems project | **memory allocator** |
| Something where bugs are *visible* | **physics engine** |
| To stop `useState` being magic | **your own React** |
| To understand a tool you use daily | **git** |
| The smallest project that teaches the most | **shell** |
| Theory to become concrete fastest | **regex engine** |
| To stop finding Docker magical | **container** (~200 lines, once you've read os/11) |
| The deepest single lesson | **language** |
| To never fear a database again | **database** |

**Start with the shell or the HTTP server.** Both are a weekend, both produce something you can show, and both make several vault domains concrete at once.

## The advice that applies to all of them

**Compare against the real thing at every milestone.** `git cat-file -p` on objects you created, `curl -v` against your server, `bash` against your shell. A tight feedback loop against a reference implementation is worth more than any amount of planning.

**Write the test before the next milestone.** Each milestone in these guides has a concrete "you'll know it works when" — use it.

**Pick a language that doesn't hide the lesson.** Go's `os/exec` and Rust's `Command` both wrap `fork`/`exec`/`dup2` behind a builder — you'll finish faster and learn less. Where the syscall *is* the lesson, use C, or Python's raw `os.*` calls.

**Stop where the guide says.** The gap between a learning artefact and production software is decades of edge cases, and crossing it teaches you much less per hour than starting the next project.

**Then write down what surprised you.** The point of these is the gap between having read [[git/01-how-git-works|How Git Actually Works]] and having implemented it — and that gap is only visible right after you close it.

## Related
- [[BUILD-PLAN|Build Plan]] — the queue these come from
- [[project-ideas|Project Ideas]] — the wider tiered build list
- [[PRIMETECHIE|The Primetechie Path]] — where these sit as rank gates
- [[foundations/os/README|Operating Systems]] · [[foundations/compilers/README|Compilers]] — the two prerequisites written specifically to unblock this folder
