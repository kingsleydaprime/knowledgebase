# Build Your Own X

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

1. [[build-your-own-x/01-http-server|HTTP Server]] — **[Intermediate]** — accept loop → request-line parser → headers → responses → routing → static files → keep-alive → concurrency → chunked encoding. **The best first project**: a weekend, immediate visual feedback, and a real browser as the test
2. [[build-your-own-x/02-your-own-git|Your Own Git]] — **[Intermediate]** — content-addressable store → blobs → trees → commits → refs → log → index → branches → diff → merge. **Real Git can read your repository** — that's the test that makes it satisfying
7. [[build-your-own-x/07-your-own-shell|Your Own Shell]] — **[Intermediate]** — read-eval loop → tokenise → `fork`/`exec` → exit status → redirection → builtins → pipelines → jobs. **The best small one**: a few hundred lines, and you can use it

**Planned:**

3. `03-your-own-redis` — RESP parser → in-memory store → event loop → expiry → more types → persistence → replication
4. `04-your-own-language` — lexer → parser → tree-walking interpreter → closures → bytecode VM. → [[foundations/compilers/README|compilers]] is the prerequisite, now written
5. `05-your-own-os` — bootloader → long mode → interrupts → paging → processes → scheduler → syscalls → filesystem. The longest and hardest. → [[foundations/os/README|os]] is the prerequisite, now written
6. `06-your-own-database` — pager → B-tree or LSM → record format → SQL subset → query execution → transactions and a WAL
8. `08-your-own-container` — namespaces → cgroups → pivot_root → layered filesystem. Ties [[devops/02-docker/README|Docker]] to [[foundations/os/11-isolation-and-containers|what the kernel actually does]]

## Which to start with

| If you want | Build |
|---|---|
| The fastest satisfying result | **HTTP server** |
| To understand a tool you use daily | **git** |
| The smallest project that teaches the most | **shell** |
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
