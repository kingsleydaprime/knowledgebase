# Foundations

**The CS spine.** Fifteen courses, ~371 notes, ~312,000 words — the largest section of the vault, and the one everything else assumes.

> **This README existed nowhere until Aug 2026.** Every sub-course had one; the parent didn't, so the vault's biggest section had no entry point. Found while linking [[foundations/projects|projects.md]] into every domain.

## Where to start

**If you're new to programming:** [[foundations/programming-fundamentals/README|programming-fundamentals/]]. It assumes nothing, and everything else here assumed it.

**If you can already program:** [[foundations/dsa/README|dsa/]] and [[foundations/networking/README|networking/]] are the two with the most immediate return.

**If you want the deepest single lesson:** [[foundations/compilers/README|compilers/]], then [[build-your-own-shit/04-your-own-language|build your own language]].

## The on-ramp

- [[foundations/programming-fundamentals/README|programming-fundamentals/]] — **[Beginner]** · 18 notes — **the entry point to the whole vault.** What a program is → languages and translation → tooling → syntax → variables and types → control flow → collections → functions → recursion and the call stack → errors and debugging → planning → what to build next. Language-agnostic, assumes nothing
- [[foundations/software-engineering/README|software-engineering/]] — **[Beginner]** · 4 notes — what the *profession* is, as opposed to the craft: the lifecycle, the roles, and the kinds of engineering. **Written because the rest of the vault assumed it and never said it**, and it's week 1 of [[learning/swe-101/README|SWE 101]]

## The core

- [[foundations/dsa/README|dsa/]] — **[Beginner → Advanced]** · **197 notes, ~91,000 words — by far the largest course here.** Iterations and what they cost → data types → data structures → algorithms → [[foundations/dsa/06-patterns/README|15 LeetCode patterns]] → a [[foundations/dsa/neetcode-150/README|NeetCode 150]] bank and an [[foundations/dsa/interview/README|interview]] folder. The `pdfs/` are the original Codility-style course material, kept untouched
- [[foundations/networking/README|networking/]] — **[Intermediate]** · 22 notes — the model and the link layer → IP and routing → UDP, TCP, congestion, sockets → DNS, HTTP, TLS, QUIC → middleboxes, performance, debugging. From Kurose & Ross, Stevens, the RFCs, and Grigorik
- [[foundations/os/README|os/]] — **[Intermediate → Advanced]** · 16 notes — the kernel/user split → processes and threads → scheduling → virtual memory → allocation → concurrency primitives → filesystems → I/O models (epoll, io_uring) → syscalls and the ABI → signals and IPC → **isolation and containers** → boot and init
- [[foundations/computer-architecture/README|computer-architecture/]] — **[Intermediate → Advanced]** · 15 notes — the ISA as a contract → data representation → instruction sets → assembly → the datapath → pipelining → branch prediction and Spectre → the memory hierarchy → caches → out-of-order → memory models → performance method. **Where the vault's performance constants come from**

## The theory spine

Written to explain *why* the practical courses are shaped as they are.

- [[foundations/discrete-math/README|discrete-math/]] — **[Intermediate]** · 11 notes — logic → proof → sets, relations, functions → induction and recurrences → combinatorics → graphs → **number theory, with RSA derived in eight lines**
- [[foundations/theory-of-computation/README|theory-of-computation/]] — **[Advanced]** · 11 notes — the Chomsky hierarchy → finite automata → regular and context-free languages → Turing machines → decidability and Rice's theorem → P vs NP → quantum. **Explains why [[foundations/compilers/README|compilers/]] is structured as it is**
- [[foundations/programming-language-theory/README|programming-language-theory/]] — **[Advanced]** · 10 notes — lambda calculus → semantics → type systems → inference → Curry–Howard → effects and substructural types. **Where Rust's borrow checker comes from**
- [[foundations/information-theory/README|information-theory/]] — **[Intermediate]** · 10 notes — entropy → mutual information → compression → **cross-entropy and KL divergence** (the note [[ai-ml/README|ai-ml]] needed) → channel capacity → error-correcting codes

## Building and computing

- [[foundations/compilers/README|compilers/]] — **[Advanced]** · 12 notes — lexing → parsing (recursive descent and Pratt) → ASTs and scopes → type systems → SSA and IR → optimisation → codegen → bytecode VMs → GC → JIT. **Built specifically to unblock [[build-your-own-shit/04-your-own-language|build-your-own-language]]**
- [[foundations/numerical-methods/README|numerical-methods/]] — **[Intermediate → Advanced]** · 13 notes — floating point and error → root finding → linear systems → eigenvalues → interpolation → quadrature → ODEs → PDEs → optimisation. **[[engineering/README|engineering/]] asked for this by name**
- [[foundations/gpu-and-parallel-computing/README|gpu-and-parallel-computing/]] — **[Advanced]** · 10 notes — parallelism → GPU architecture and warps → the CUDA model → patterns → coalescing → the roofline model → FSDP and multi-GPU. **The hardware under [[ai-ml/README|ai-ml/]]**
- [[foundations/computer-graphics/README|computer-graphics/]] — **[Intermediate → Advanced]** · 12 notes — the rendering equation → transforms → rasterisation → shading and PBR → textures → the GPU pipeline → ray tracing → meshes → animation. **Most of [[game-development/README|game-development/]]'s graphics half lives here**
- [[foundations/systems-engineering/README|systems-engineering/]] — **[Intermediate]** · 9 notes — what systems engineering is (emergence, the cost curve) → requirements → the lifecycle and V-model → architecture and interfaces (ICDs, N², margin, Conway) → trade studies → V&V → MBSE/SysML → FMEA and fault trees. **The degree-shaped gap**

## Build it

[[foundations/projects|projects.md]] — the reps, graded 🟢🟡🔴 with a *done when* for each, plus the nine sub-courses that ship **practice exercises with solutions**.

**The single best rep here is [[build-your-own-shit/09-your-own-regex-engine|the regex engine]]** — one evening, ~200 lines, and it turns the most abstract folder in the vault into running code. Most of the other deep foundations reps are full guides in [[build-your-own-shit/README|build-your-own-shit/]]: the shell and container for [[foundations/os/README|OS]], the HTTP server for [[foundations/networking/README|networking]], the language for [[foundations/compilers/README|compilers]], the allocator for memory.

## The honest labelling

**The practical courses are grounded; the theory spine is `[reference]`.** `discrete-math`, `theory-of-computation`, `computer-architecture`, `numerical-methods`, `information-theory`, `gpu-and-parallel-computing`, `computer-graphics` and `programming-language-theory` were read and assembled, not validated by building. Each says so on its own front page, and each names what would close its gap.

**That's also why they're the cheapest reps in the vault** — most are a single script and an afternoon, and [[foundations/projects|projects.md]] lists them.

## Related
- [[foundations/projects|Projects]] — **the reps for this domain**
- [[build-your-own-shit/README|build-your-own-shit]] — the deep systems reps, as full guides
- [[README|the vault README]] · [[PRIMETECHIE|the Primetechie path]] — where these sit as rank gates
- [[INTERVIEW|Interview Prep Index]] — `dsa/`, `os/` and `networking/` all have banks
