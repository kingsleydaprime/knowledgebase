---
title: Kingsley's Knowledge Base
---

> **software · infrastructure · security · hardware · ML · engineering · CS theory**
>
> ~1,500 course notes, ~1.7 million words, across 45 domains.

**This started as my notes. It has become something closer to a course library** — 45 domains, most of them written as sequenced courses with prerequisites, worked derivations, runnable labs and practice with hidden answers, rather than as a pile of things I looked up.

It is still mine, and it still says so. The honest labels stayed: where a topic was read rather than built, the folder says so on its own front page. Where a number is a guess rather than a measurement, it is marked. What changed is that the material is now written to be **worked through by someone who is not me**.

Docs already exist. This is the layer underneath them: the mental models, the failure modes, and the things that only make sense once you have broken them yourself.

---

## Start here

🕶️ **[[PRIMETECHIE|The Primetechie Path]]** — the spine of the whole vault. A tiered progression from _"it works on my machine, and I know why"_ to the engineer everyone escalates to, with gates in all four disciplines. **Every gate is something you can demonstrate, not something you have read.** If you want an order to do all this in, start here.

🎯 **[[INTERVIEW|Interview Prep]]** — every domain has a bank: the question, what a strong answer covers, and the detail that separates memorised from understood.

🛠️ **[[project-ideas|Project Ideas]]** — notes are a map; this is the territory. Tiered builds across every column, tied to the notes each one exercises.

📐 **[[COURSE-STANDARD|The Course Standard]]** — what a lesson here is supposed to do, and how the newer courses are held to it.

---

## The seven columns

|  |  |  |
| --- | --- | --- |
| 📱 **Mobile** | [[mobile/index\|Mobile]] · [[languages/08-swift/index\|Swift]] · [[languages/09-kotlin/index\|Kotlin]] | the OS can kill your process — everything else follows from that |
| 💻 **Software** | [[backend/index\|Backend]] · [[dsa/index\|DSA]] · [[architecture/index\|Architecture]] · [[languages/01-java/index\|Java]] · [[ai-ml/03-ai-engineer/index\|AI Engineering]] | backends, systems, algorithms, building on pre-trained models |
| ☁️ **Infrastructure** | [[devops/index\|DevOps]] · [[networking/index\|Networking]] · [[databases/index\|Databases]] · [[data-engineering/index\|Data Engineering]] | Linux → containers → orchestration → CI/CD → observability → pipelines |
| 🔐 **Security** | [[cybersecurity/index\|Cybersecurity]] | offence _and_ defence — you cannot do one well without the other |
| ⛓️ **Web3** | [[web3/index\|Web3 & Blockchain]] | the chain, the EVM, Solidity, security — **and an honest assessment of where it does not apply** |
| 🔌 **Hardware** | [[hardware/index\|Hardware & Embedded]] · [[control-theory/index\|Control Theory]] · [[continuum-mechanics/index\|Continuum Mechanics]] | electricity → embedded → RF → a board that physically exists, and the physical systems around it |
| 🧠 **ML & Data** | [[ai-ml/index\|AI & ML]] · [[data-analysis/index\|Data Analysis]] · [[data-engineering/index\|Data Engineering]] | training models, and turning data into decisions and pipelines |

**AI sits in two columns on purpose.** _Using_ a model is software engineering — APIs, retries, schemas, evals, cost. _Training_ one is not: its foundation is linear algebra, calculus and probability, and its failure modes are leakage, overfitting and drift rather than bugs. [[ai-ml/index|The AI/ML course]] splits the same way.

Most engineering vaults are column one with a bit of column two. The point of this one is the boundaries — being the person who follows a problem from a web request down to a voltage rail, or from a dashboard back to a leaked feature, instead of handing it off at the edge of a job title.

---

## The foundations — the CS spine

**The largest section, and the one everything else assumes.**

**If you are new to programming:** [[programming-fundamentals/index|programming-fundamentals/]]. It assumes nothing, and everything else here assumed it.
**If you can already program:** [[dsa/index|dsa/]] and [[networking/index|networking/]] have the most immediate return.
**If you want the deepest single course:** [[compilers/index|compilers/]], then [[build-your-own-shit/04-your-own-language|build your own language]].

### The on-ramp

- [[programming-fundamentals/index|programming-fundamentals/]] — **[Beginner]** · 18 notes — what a program is → languages and translation → tooling → syntax → variables and types → control flow → collections → functions → recursion and the call stack → errors and debugging → planning → what to build next. Language-agnostic, assumes nothing
- [[software-engineering/index|software-engineering/]] — **[Beginner]** · 4 notes — what the *profession* is, as opposed to the craft. **Written because the rest of the vault assumed it and never said it**, and it is week 1 of [[learning/swe-101/index|SWE 101]]

### The core

- [[dsa/index|dsa/]] — **[Beginner → Advanced]** — **the largest course here.** Iterations and what they cost → data types → [[dsa/02-data-structures/index|data structures]] → algorithms → [[dsa/04-patterns/index|15 LeetCode patterns]] → a [[dsa/neetcode-150/index|NeetCode 150]] bank and an [[dsa/interview/index|interview]] folder
- [[how-computers-work/index|how-computers-work/]] — **[Beginner → Advanced]** · 34 modules — **electricity → semiconductors → logic gates → arithmetic → memory → a CPU you build yourself.** Every lab verified; ends in a working 16-bit machine with an assembler, an emulator and a language
- [[networking/index|networking/]] — **[Intermediate]** · 22 notes — the model and the link layer → IP and routing → UDP, TCP, congestion, sockets → DNS, HTTP, TLS, QUIC → middleboxes, performance, debugging
- [[os/index|os/]] — **[Intermediate → Advanced]** · 16 notes — the kernel/user split → processes and threads → scheduling → virtual memory → allocation → concurrency → filesystems → I/O models → syscalls and the ABI → isolation and containers → boot and init
- [[computer-architecture/index|computer-architecture/]] — **[Intermediate → Advanced]** · 15 notes — the ISA as a contract → data representation → assembly → the datapath → pipelining → branch prediction and Spectre → caches → out-of-order → memory models. **Where the vault's performance constants come from**

### The theory spine

Written to explain *why* the practical courses are shaped as they are.

- [[mathematics/index|mathematics/]] — **[Beginner → Advanced]** — foundations and number bases → [[mathematics/02-discrete-math/index|discrete maths]] → [[mathematics/03-geometry-trigonometry/index|geometry and trigonometry]] → [[mathematics/04-linear-algebra/index|linear algebra]] → [[mathematics/06-calculus/index|calculus]] → [[mathematics/07-applied-and-computational/01-numerical-methods/index|numerical methods]]. **Merges a full secondary curriculum with a university one**, so each subject appears once
- [[theory-of-computation/index|theory-of-computation/]] — **[Advanced]** · 11 notes — the Chomsky hierarchy → automata → Turing machines → decidability and Rice's theorem → P vs NP → quantum. **Explains why [[compilers/index|compilers/]] is structured as it is**
- [[programming-language-theory/index|programming-language-theory/]] — **[Advanced]** · 10 notes — lambda calculus → semantics → type systems → inference → Curry–Howard → effects. **Where Rust's borrow checker comes from**
- [[information-theory/index|information-theory/]] — **[Intermediate]** · 10 notes — entropy → mutual information → compression → **cross-entropy and KL divergence** → channel capacity → error-correcting codes
- [[digital-signal-processing/index|digital-signal-processing/]] — **[Beginner → Advanced]** · 9 notes — signals & LTI → sampling & Nyquist → the frequency domain → the FFT → **convolution** (which is also a CNN's core) → filters → modulation & SDR

### Building and computing

- [[compilers/index|compilers/]] — **[Advanced]** · 12 notes — lexing → parsing → ASTs and scopes → type systems → IR → optimisation → codegen → **linking and loading** → bytecode VMs → GC → JIT. **Built to unblock [[build-your-own-shit/04-your-own-language|build-your-own-language]]**
- [[gpu-and-parallel-computing/index|gpu-and-parallel-computing/]] — **[Advanced]** · 10 notes — parallelism → GPU architecture and warps → CUDA → coalescing → the roofline model → multi-GPU. **The hardware under [[ai-ml/index|ai-ml/]]**
- [[computer-graphics/index|computer-graphics/]] — **[Intermediate → Advanced]** · 12 notes — the rendering equation → transforms → rasterisation → shading and PBR → the GPU pipeline → ray tracing → animation
- [[systems-engineering/index|systems-engineering/]] — **[Intermediate]** · 9 notes — emergence and the cost curve → requirements → the V-model → interfaces → trade studies → V&V → MBSE → FMEA. **The degree-shaped gap**

---

## New to any of this?

- **Just want to not get hacked?** → [[cybersecurity/10-protecting-yourself/index|Protecting Yourself]] — eight notes, no code, no jargon. The six things that actually matter, and an ordered checklist for when it has already gone wrong.
- **Never used an LLM seriously?** → [[using-ai/index|Using AI]] — eight notes, no code, for people who want to _use_ these tools well rather than build with them.
- **Want the wire-level foundation?** → [[networking/index|Networking]] — the layer under devops, security and distributed systems.
- **Want to know what a computer actually is?** → [[how-computers-work/index|How Computers Work]] — starts at electricity and ends with a CPU you built.

---

## How the courses are written

Every course folder has an `index.md` entry point and notes numbered in reading order. Notes are tagged **[Beginner]** / **[Intermediate]** / **[Advanced]**, marking how much prior context a note assumes _within its folder_ — not absolute difficulty.

**Older notes** follow one shape: the kid version first — plain-language intuition before any depth · the actual content — tables, worked examples, real failure modes · key insight · related links out.

**Newer courses are held to [[COURSE-STANDARD|the course standard]]**, which asks for more: stated prerequisites, observable outcomes, a terminology table before any jargon, the mechanism built one step at a time, a **runnable lab whose expected output was generated from an actual run**, practice with answers hidden behind a fold, and a demonstrable finish line. `dsa/02-data-structures`, `dsa/04-patterns`, `how-computers-work`, `mathematics` and `compilers` are the ones converted so far.

Where a lab claims an output, that output came from executing the code — not from predicting it. Several labs exist specifically to check a claim the prose makes rather than to illustrate it: that omitting partial pivoting silently returns a wrong answer, that two triangles satisfy the same SSA data, that a hanging chain is not a parabola.

---

## What is actually built, and what is not

This vault labels its own gaps rather than implying uniform coverage.

**Built out and readable start to finish:** networking · DSA · backend · architecture · devops · java · AI/ML · using-ai · cybersecurity · hardware · research · concepts · operating systems · compilers · databases · how-computers-work · mathematics

**Written, but `[reference]` — read and assembled, not validated by building:** [[mobile/index|mobile]] (a full track plus Swift/Kotlin/Dart — nothing here has been shipped to a store by its author) · [[web3/index|web3]] (nothing in it has been deployed or audited by its author; [[build-your-own-shit/16-your-own-token-and-wallet|guide 16]] is the cheapest way to start closing that) · [[control-theory/index|control theory]] · [[continuum-mechanics/index|continuum mechanics]] · [[robotics/index|robotics]] · [[databases/index|databases]] (the internals course) · much of the theory spine ([[theory-of-computation/index|theory of computation]] · [[computer-architecture/index|computer architecture]] · [[information-theory/index|information theory]] · [[gpu-and-parallel-computing/index|GPU & parallel]] · [[computer-graphics/index|graphics]] · [[programming-language-theory/index|PL theory]])

**Honest scaffold — a stated direction, not knowledge yet:** [[ai-automation/index|ai-automation]] · parts of [[frontend/index|frontend]] · the reserved folders in [[mathematics/index|mathematics]], which are listed by name so the shape of the curriculum stays visible

Where a folder is a plan rather than a course, it says so in its first paragraph. Where a topic has been read but not practised, the notes say that too — because _"reading is not a rank"_ is the rule the whole thing is organised around.

**The cheapest way to close a `[reference]` gap is a rep.** [[build-your-own-shit/index|build-your-own-shit/]] has the deep ones as full guides; the single best is [[build-your-own-shit/09-your-own-regex-engine|the regex engine]] — one evening, ~200 lines, and it turns the most abstract folder in the vault into running code.

**Four of the theory-spine folders got their first build guide in Sep 2026** — [[build-your-own-shit/21-your-own-compressor|a compressor]] for information theory, [[build-your-own-shit/22-your-own-ray-tracer|a ray tracer]] for graphics, [[build-your-own-shit/19-your-own-tcp-ip-stack|a TCP/IP stack]] for networking and [[build-your-own-shit/20-your-own-raft-kv-store|a Raft key-value store]] for distributed systems. **The compressor is the cheapest of the four**: a weekend, and `gunzip` decompresses your output.

---

## Related

- [[project-ideas|Project Ideas]] — the reps, graded 🟢🟡🔴 with a *done when* for each
- [[build-your-own-shit/index|build-your-own-shit/]] — the deep systems reps, as full guides
- [[PRIMETECHIE|The Primetechie Path]] — where all of this sits as rank gates
- [[INTERVIEW|Interview Prep]] — `dsa/`, `os/` and `networking/` all have banks
- [[BUILD-PLAN|Build Plan]] — what is being worked on next
- [[COURSE-STANDARD|Course Standard]] — the shape a lesson is held to

---

_Knowledge base of **Kingsley Ihemelandu** — Systems Engineer · Builder · Founder [@Spectroniq](https://linkedin.com/company/spectroniq). Started properly during SIWES 2026, IT Consortium, Accra. Source on [GitHub](https://github.com/kingsleydaprime/knowledgebase)._
