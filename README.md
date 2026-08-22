# Knowledge Base — kingsleydaprime

> My personal engineering knowledge base. Concepts, implementations, patterns, and practices — built and updated continuously.

This is not a copy of documentation. It's my understanding of how things work — the why, the how, and what I've figured out the hard way.

---

## How to Use This as a Course

The domains that are actually built out — **networking, DSA, backend, architecture (incl. distributed systems), devops, java, AI/ML, using-ai, cybersecurity, hardware, research, and `concepts/`** — are meant to be readable start-to-finish, not just looked up. (Still scaffold, and labelled as such below: `ai-automation/`, `frontend/01-react`+`02-next`, and parts of `backend/`. **`engineering/` and `robotics/` are written but marked `[reference]`** — courses on paper, with no build behind them yet, and each says so on its own front page. **Note on the frontend two:** the scaffold is the *course*, not the knowledge — ~44,000 words on React/Next.js live in [[projects/README|projects/]], indexed by topic in [[frontend/README|frontend/README]].)

**This is not a software-engineering vault.** It covers software, infrastructure, security, and hardware — see [[PRIMETECHIE|the path]] for how those four fit together rather than sitting in separate silos. Each has its own `README.md` acting as the entry point, with notes tagged **[Beginner]**, **[Intermediate]**, or **[Advanced]** in the order they're meant to be read — a tag marks how much prior context a note assumes *within that folder*, not an absolute difficulty across the whole vault.

**Two cross-cutting entry points, added August 2026:**
- 🕶️ **[[PRIMETECHIE|The Primetechie Path]]** — a tiered progression through the whole vault (Builder → Diagnostician → Systems Thinker → Distributed Mind → Specialist → Force Multiplier), where every gate is something you can *demonstrate*, not something you've read. Start here if you want an order to do all this in.
- 🔨 **[[build-your-own-x/README|Build Your Own X]]** — language-agnostic build guides with numbered, independently-testable milestones. Where the rest of the vault stops being reading. All nine written: HTTP server, git, redis, language, OS, database, shell, container, regex engine.
- 🧭 **[[BUILD-PLAN|Build Plan]]** — the working queue for what gets written next, ordered and sized: the systems languages (Rust/C/C++), `build-your-own-x/`, `engineering/`, and the CS-curriculum gaps found by auditing a standard syllabus against this vault.
- 🧠 **[[learning/README|How I Learn]]** — the method behind everything else here: the learning loop (board → notebook → laptop), the "make a course" system, the one-active-course rule, and AI as sparring partner rather than answer machine. Personal, and deliberately unpublished.
- 🎯 **[[INTERVIEW|Interview Prep Index]]** — every domain now has an `interview/` folder: the question, what a strong answer covers, and the detail that separates memorised from understood.

Start here, depending on what you want:
- [[foundations/programming-fundamentals/README|Programming Fundamentals]] — **start here if you have never written code.** Twelve language-agnostic notes: what a program is → syntax → variables → control flow → collections → functions → recursion → debugging → planning → what to build. Written Aug 2026, because 900 notes assumed this and none of them taught it
- [[foundations/networking/README|Networking]] — the wire up to the web: link layer → IP → TCP/congestion control → DNS/TLS/HTTP → QUIC → debugging. The foundation under devops, security, and distributed systems
- [[foundations/software-engineering/README|Software Engineering — orientation]] — **three short notes on what the profession actually is**: programming vs engineering, the SDLC and what breaks when each phase is skipped, and the eleven roles. Written Aug 2026 to fill a gap the rest of the vault assumed
- [[foundations/dsa/README|Data Structures & Algorithms]] → then [[foundations/dsa/06-patterns/README|LeetCode Patterns]]
- [[using-ai/README|Using AI]] — **start here if you're new to AI and don't write code.** Eight notes on using LLMs well: what they are, how to brief them, how to check them, what not to paste. The on-ramp to everything below
- [[ai-ml/README|AI & ML]] — split into three career paths (data scientist, ML engineer, AI engineer) over a shared foundation
- [[cybersecurity/README|Cybersecurity]] — fundamentals → ethical hacking → network/web security → cryptography → attacks taxonomy → security operations (blue team) → GRC → cloud
- [[backend/README|Backend]] — a full course: foundations → API design → **structuring a backend** (layers, DI, hexagonal, modular monolith) → data → auth, plus `frameworks/` for Node/Nest/Spring/FastAPI/Axum
- [[concepts/02-frontend/README|Frontend]], [[concepts/03-design-patterns/README|Design Patterns]], [[concepts/04-best-practices/README|Best Practices]] — engineering ideas that belong to no single domain
- [[languages/01-java/README|Java]] — the JVM, concurrency, and the Spring Boot/build-tools ecosystem
- [[devops/README|DevOps]] — **the physical layer** (servers, hypervisors, data centres, leaf-spine) → Linux → containers → orchestration → CI/CD → IaC → observability → **the disciplines** (SRE, platform engineering, DevSecOps)
- [[architecture/README|Architecture]] — system design (scaling, caching, patterns) + distributed systems (consensus, consistency, partitioning)
- [[hardware/README|Hardware & Embedded]] — the layer below all the software: electricity → digital/analog → embedded → microcontrollers → I2C/SPI/UART → RF → IoT architecture, plus KiCad and a real fabricated PCB
- [[databases/README|Databases]] — a course on the **internals** (pages → B-trees → LSM → query planning → MVCC → WAL → replication → operations) plus four deep syntax/design references. Read the course to understand `EXPLAIN`; use the references to look things up
- [[foundations/discrete-math/README|Discrete Maths]] → [[foundations/theory-of-computation/README|Theory of Computation]] → [[foundations/computer-architecture/README|Computer Architecture]] — the CS-theory spine, added Aug 2026 after auditing a standard syllabus against this vault. Logic and proof → what's computable and what's NP-hard → why one $O(n)$ loop is thirty times slower than another
- [[foundations/numerical-methods/README|Numerical Methods]] — **the gap three domains asked for by name.** Floating point and conditioning → linear systems → quadrature → ODEs → PDEs → optimisation. What FEM, control discretisation and ML optimisation all sit on
- [[foundations/gpu-and-parallel-computing/README|GPU & Parallel Computing]] — the hardware under 98 notes of ML. Warps, coalescing, the roofline, FSDP. **Why "thousands of cores" is misleading**
- [[foundations/information-theory/README|Information Theory]] — entropy, and **the note explaining the cross-entropy loss the ML track uses everywhere**. Plus compression, channel capacity, error-correcting codes
- [[foundations/computer-graphics/README|Computer Graphics]] · [[foundations/programming-language-theory/README|PL Theory]] — rasterisation, shading and ray tracing; lambda calculus, Curry–Howard and where Rust's borrow checker came from
- [[engineering/README|Engineering]] — the physical half: [[engineering/01-continuum-mechanics/README|continuum mechanics]] (how solids and fluids deform) and [[engineering/02-control-theory/README|control theory]] (making a system behave despite a wrong model). The control track is more portable than it sounds — autoscalers and congestion control are feedback loops with all the classical pathologies
- [[research/README|Research & Paper Writing]] — a meta-skill for every field: doing research (reading papers, finding a gap, methodology) + writing/publishing (structure, style, venues, peer review)

A [Beginner] tag doesn't mean "skip if you're experienced" — it just means the note doesn't lean on anything else in the folder yet. Read a folder's notes in order at least once even if a topic sounds familiar; later notes assume earlier ones without re-explaining them.

## → Ready to build?

Notes are a map, not reps. **[[project-ideas|Project Ideas]]** is the companion build-list — concrete projects across every domain (Java/systems, DevOps, AI engineering, ML engineering, data science), tiered by difficulty and tied to the notes each one exercises. Pick one and finish it.

---

## Structure

Course domains use numbered folders/files (`01-`, `02-`...) so the reading order shows up directly in the file tree, not just inside a README. Everything else is unordered reference material.

```
knowledgebase/
│
├── PRIMETECHIE.md                # the tiered progression through everything below
├── INTERVIEW.md                  # index of every domain's interview/ folder
├── BUILD-PLAN.md                 # the ordered queue of what gets written next
│
├── foundations/
│   ├── programming-fundamentals/ # numbered course (12 notes, Aug 2026): THE ON-RAMP.
│   │                             # what a program is → languages/translation → tooling →
│   │                             # syntax → variables/types → control flow → collections →
│   │                             # functions → recursion/the call stack → errors/debugging
│   │                             # → planning → what to build next. Language-agnostic;
│   │                             # assumes nothing. Everything else here assumed it.
│   ├── dsa/                      # numbered course: iterations → data types → data
│   │   │                         # structures → algorithms → patterns/ (15 LeetCode patterns)
│   │   └── pdfs/                 # original Codility-style course material, untouched
│   ├── networking/               # numbered course (16 notes, built Aug 2026): the model
│   │                             # & link layer → IP/routing → UDP/TCP/congestion/sockets
│   │                             # → DNS/HTTP/TLS/QUIC → middleboxes/performance/debugging.
│   │                             # From Kurose & Ross, Stevens, RFCs, Grigorik.
│   ├── os/                       # numbered course (12 notes, Aug 2026): kernel/user split →
│   │                             # processes/threads → scheduling → virtual memory →
│   │                             # allocation → futexes → filesystems → epoll/io_uring →
│   │                             # syscalls/ABI → signals/IPC → namespaces+cgroups → boot.
│   │                             # Built against the plan its own README proposed.
│   ├── discrete-math/            # numbered course (8 notes, Aug 2026): logic → proof →
│   │                             # sets/relations/functions → induction/recurrences →
│   │                             # combinatorics → graphs → number theory (RSA in 8 lines).
│   ├── theory-of-computation/    # numbered course (8 notes, Aug 2026): the Chomsky hierarchy
│   │                             # → finite automata → regular → context-free → Turing
│   │                             # machines → decidability/Rice → P vs NP → quantum.
│   │                             # Explains WHY compilers/ is structured as it is.
│   ├── numerical-methods/        # numbered course (10 notes, Aug 2026): floating point/error
│   │                             # → root finding → linear systems → eigenvalues →
│   │                             # interpolation → quadrature → ODEs → PDEs → optimisation.
│   │                             # engineering/ asked for this by name.
│   ├── information-theory/       # numbered course (7 notes, Aug 2026): entropy → mutual info
│   │                             # → compression → CROSS-ENTROPY & KL (the note ai-ml needed)
│   │                             # → channel capacity → ECC → where it shows up.
│   ├── gpu-and-parallel-computing/ # numbered course (7 notes, Aug 2026): parallelism → GPU
│   │                             # architecture/warps → CUDA model → patterns → coalescing
│   │                             # → roofline → FSDP/multi-GPU. The hardware under ai-ml/.
│   ├── computer-graphics/        # numbered course (9 notes, Aug 2026): rendering equation →
│   │                             # transforms → rasterisation → shading/PBR → textures →
│   │                             # GPU pipeline → ray tracing → meshes → animation.
│   ├── programming-language-theory/ # numbered course (7 notes, Aug 2026): lambda calculus →
│   │                             # semantics → type systems → inference → Curry-Howard →
│   │                             # effects & substructural (where Rust's borrow checker is from).
│   ├── computer-architecture/    # numbered course (12 notes, Aug 2026): ISA as contract →
│   │                             # data representation → instruction sets → assembly →
│   │                             # datapath → pipelining → branch prediction/Spectre →
│   │                             # memory hierarchy → caches → OOO → memory models →
│   │                             # performance method. Where the vault's constants come from.
│   └── compilers/                # numbered course (11 notes, Aug 2026): lexing → parsing
│                                 # (recursive descent + Pratt) → ASTs/scopes → type systems
│                                 # → SSA/IR → optimisation → codegen → bytecode VMs → GC
│                                 # → JIT. Built to unblock build-your-own-language.
│
├── using-ai/                     # 8-note course for NON-programmers new to AI (Aug 2026):
│                                 # what an LLM is → how it works plainly → choosing a tool
│                                 # → prompting as briefing → context/long chats →
│                                 # verifying output → privacy → living with it.
│                                 # The on-ramp *into* ai-ml/; a technical-user track is planned.
│
├── ai-ml/                        # split (roadmap.sh-cross-referenced) into 3 career
│   ├── 00-foundations/           # paths over a shared foundation: 00-foundations
│   ├── 01-data-scientist/        # (concepts + maths) → 01-data-scientist (skeleton) →
│   ├── 02-ml-engineer/           # 02-ml-engineer (ML workflow/CV/build-your-own, +algo
│   └── 03-ai-engineer/           # zoo/RL/MLOps to come) → 03-ai-engineer (deep-built:
│                                  # LLMs/prompting/RAG/tools+MCP/agents/multimodal/safety)
│
├── ai-automation/                # scaffold only — n8n-focused, no content written yet
│
├── cybersecurity/                # numbered course, roadmap.sh-cross-referenced.
│   ├── 01-fundamentals/          # Original: 01-fundamentals → 02-ethical-hacking →
│   ├── 02-ethical-hacking/       # 03-network-security → 04-web-security →
│   ├── 03-network-security/      # 05-cryptography. Then the roadmap gaps:
│   ├── 04-web-security/          # 06-attacks-and-threats (taxonomy) →
│   ├── 05-cryptography/          # 07-security-operations (SIEM/IR/hunting/forensics,
│   ├── 06-attacks-and-threats/   # the blue-team half) → 08-governance-risk-and-
│   ├── 07-security-operations/   # compliance → 09-cloud-security.
│   ├── 08-governance-risk-and-compliance/
│   └── 09-cloud-security/
│
├── concepts/                     # engineering ideas that belong to NO domain.
│   ├── 02-frontend/              # (01-backend moved into backend/ — Aug 2026, so that
│   ├── 03-design-patterns/       #  everything about backends is findable in one place)
│   └── 04-best-practices/
│
├── devops/                       # numbered course, roadmap.sh-cross-referenced.
│   ├── 00-the-physical-layer/    # NEW Aug 2026: the layer under Linux — servers,
│   │                             # virtualisation/hypervisors, data centres (hot aisle,
│   │                             # PUE, Uptime tiers, what an AZ physically is), and the
│   │                             # leaf-spine DC network. 4 notes.
│   ├── 01-linux/                 # Foundation: 01-linux (+15-rhcsa/ cert track) →
│   │   └── 15-rhcsa/             # 02-docker → 03-cloud → 04-vps. Then the DevOps
│   ├── 02-docker/                # pillars: 05-orchestration (k8s) → 06-ci-cd →
│   ├── 03-cloud/                 # 07-infrastructure-as-code (terraform/ansible) →
│   ├── 04-vps/                   # 08-networking-and-web → 09-secret-management →
│   ├── 05-orchestration/         # 10-observability → 11-delivery-and-advanced
│   ├── 06-ci-cd/                 # (gitops/artifacts/service-mesh/patterns).
│   ├── 07-infrastructure-as-code/  # 05-11 are mostly reference, not yet hands-on.
│   ├── 08-networking-and-web/
│   ├── 09-secret-management/
│   ├── 10-observability/
│   ├── 11-delivery-and-advanced/
│   └── 12-sre-and-platform-engineering/  # NEW Aug 2026: the DISCIPLINES, not the tools.
│                                 # How delivery practice evolved (waterfall→agile→devops→
│                                 # SRE→platform→devsecops, each fixing the last one's
│                                 # bottleneck) · toil/on-call/incident command/postmortems
│                                 # · IDPs and golden paths · security as a pipeline stage.
│
├── languages/                     # numbered course, organized by language rather than framework
│   └── 01-java/                  # 6 themed sections: language (fundamentals→OOP→generics→
│                                  # collections→functional→exceptions→modern-java→core-apis),
│                                  # jvm-and-concurrency (internals/GC/memory-model/loom),
│                                  # tooling, persistence, web-and-api, applied-systems.
│                                  # roadmap.sh-cross-referenced; applied section from 2 real projects
│
├── backend/                      # numbered COURSE (restructured Aug 2026) + implementations.
│   ├── 01-foundations/           # 01-foundations (what a backend is, request lifecycle,
│   ├── 02-api-design/            #  runtime/concurrency models) → 02-api-design →
│   ├── 03-structuring-a-backend/ #  03-structuring (layers, by-feature, DI, hexagonal,
│   ├── 04-data-and-persistence/  #  modular monolith→services) → 04-data → 05-auth →
│   ├── 05-auth/                  #  06-cross-cutting → 07-practices.
│   ├── 06-cross-cutting/         # Sections 01-07 hold true in ANY language;
│   ├── 07-practices/             # frameworks/ is "how this stack does it".
│   ├── frameworks/               #   javascript/{node,express,nest}, java/ (pointer to
│   │                             #   languages/01-java), python/, go/, rust/
│   └── interview/                # built from a real interview, not guessed
│
├── frontend/                     # mixed — react/ and next/ are still scaffold, but
│   ├── 01-react/                 # gsap/, framer-motion/, and threejs/ are full written
│   ├── 02-next/                  # courses (tweens/timelines, gestures/variants,
│   ├── 03-gsap/                  # scene/materials/R3F, each with performance notes)
│   ├── 04-framer-motion/
│   ├── 05-threejs/
│
├── architecture/                 # numbered course: system design (fundamentals →
│   ├── 01-system-design-fundamentals/  # building-blocks → patterns) + distributed
│   ├── 02-building-blocks/       # systems (04 — consensus/clocks/consistency/2PC).
│   ├── 03-architectural-patterns/  # roadmap.sh-cross-referenced; DDIA for dist-sys.
│   ├── 04-distributed-systems/   # Keeps system-design-reference.md as a cheat-sheet.
│   └── 05-case-studies/
│
├── engineering/                  # the PHYSICAL half, two tracks (26 notes, ~41k words, Aug 2026).
│                                 # 01-continuum-mechanics: continuum hypothesis → tensors →
│                                 # kinematics → strain → stress → conservation laws →
│                                 # constitutive models → elasticity → beams → finite deformation
│                                 # → Navier-Stokes → failure → FEM.
│                                 # 02-control-theory: open/closed loop → transfer functions →
│                                 # time response → PID (and tuning one) → root locus → Bode →
│                                 # Nyquist → state space → observers/Kalman → LQR/MPC → digital
│                                 # → nonlinear. [reference], and honest that these validate
│                                 # against an experiment, not a compiler.
│
├── hardware/                     # NOT reference material — a real course (~11k words) plus the
│                                 # vault's largest applied project. electricity → digital/analog
│                                 # → embedded/RTOS → microcontrollers → UART/I2C/SPI → RF →
│                                 # IoT architecture, + kicad-basics. Reps live in
│                                 # projects/iot-bridge-pcb/ (19k words, a board that exists).
│                                 # Filed under "reference" until Aug 2026, which undersold it.
│
├── robotics/                     # a course (14 notes, ~22k words, Aug 2026) but [reference] —
│                                 # sense/plan/act → sensors → actuators → transforms → forward/
│                                 # inverse kinematics → Jacobians → dynamics → control →
│                                 # motion planning → state estimation → SLAM → ROS 2 → safety.
│                                 # The control THEORY lives in engineering/02-control-theory/;
│                                 # note 09 here is the robot-specific part. Its README is blunt
│                                 # that nothing here has been validated on hardware.
│
├── git/                          # a course (~17k words, 17 notes) + a command reference and a
│                                 # recovery guide. internals → three trees → branching →
│                                 # merge/rebase → history → undoing → team workflow → gh CLI → hooks.
│                                 # Split out of one 3,168-line reference in Aug 2026.
│
├── tools/                        # the software used to do the work. quartz/ (6 notes) documents
│                                 # the SSG publishing this vault — pipeline, config, theming,
│                                 # layout, graph view, deploy. plus neovim-setup.
│
├── databases/                    # a course (12 notes, ~18k words, Aug 2026) + 4 big reference
│                                 # files kept in place. Course = INTERNALS: pages/buffer pool →
│                                 # B-trees → LSM → query pipeline → join algorithms/optimiser →
│                                 # ACID/isolation → MVCC/vacuum → WAL/ARIES → replication →
│                                 # operations. References = SYNTAX: sql-, database-design-,
│                                 # mysql-, nosql-reference (11k lines, ~40 inbound links).
│
│   NOTE: quartz/content/index.md is the PUBLISHED SITE'S landing page and is
│   its own file — it used to symlink here, but a README and a landing page
│   want different things. Edit both when the vault's shape changes.
│
├── learning/                     # HOW I LEARN, not what — the loop, the course system,
│                                 # the one-active-course rule, catalogue + course template.
│                                 # Personal; not symlinked into quartz/content.
│
├── problem-solving/, blog-drafts/  # blog-drafts + blog-ideas.md are gitignored —
│                                 # local drafts, deliberately not published
│
├── sources/                      # RAW MATERIAL, NOT NOTES — video transcripts and course
│                                 # PDFs the courses were distilled from. Excluded from the
│                                 # Quartz build so they don't dominate search/graph.
│
└── projects/                     # per-project learning logs + interview/ banks.
                                  # 42% of the vault by word count. See projects/README.md
                                  # for the map of which project exercises which domain.
```

---

## The Rule

**Concept or implementation?**

- *Does it belong to a **domain**?* → that domain's folder (`backend/`, `devops/`, `architecture/`…), in a numbered section if it's true regardless of language
- *Is this how a specific tool/framework does it?* → that domain's implementation folder — e.g. `backend/frameworks/<language>/<framework>/`
- *Is it true of engineering generally, belonging to **no** domain* (clean code, design patterns, PR structure)? → `concepts/`
- *Is this how to think about a problem?* → `problem-solving/`
- *Is this a dev environment or tooling thing?* → `tools/`

Notes capture **understanding** — the why and how. Not a copy of docs. Docs already exist.

---

## Note Format

There are two shapes here, and this section describes what's **actually used** rather than an aspiration — the previously documented format (`## What it is / ## Why it exists / ## References`) was followed by almost nothing.

**Course notes** (the numbered folders — networking, distributed systems, java, cybersecurity…):

```markdown
# Topic Name
**[Beginner|Intermediate|Advanced]** — one line on what this is and what it assumes

## The kid version first     ← plain-language intuition before any depth
## <the actual content>      ← tables, worked examples, real failure modes
## Key insight               ← the one thing to keep if you forget the rest
## Related                   ← wikilinks out, always
## Seen in the wild          ← where this shows up in projects/ (where applicable)
```

**Reference notes** (`*-reference.md`, the unordered folders) are dense lookup documents, not pedagogy — no reading order, no difficulty marker.

**Difficulty markers** are inline `**[Beginner]**` / `**[Intermediate]**` / `**[Advanced]**` in READMEs and note headers (91 files), *not* Obsidian frontmatter tags. A marker says how much prior context a note assumes **within its folder**, not absolute difficulty.

**Interview banks** (`<domain>/interview/`) use a third shape: the question, **what a strong answer covers**, and **the detail worth adding**. 🔥 marks frequently-asked. See [[INTERVIEW|the index]].

---

## About

Personal knowledge base of **Kingsley Ihemelandu** ([@kingsleydaprime](https://github.com/kingsleydaprime)).

Systems Engineer · Builder · Founder [@Spectroniq](https://linkedin.com/company/spectroniq)

*Started building this properly during SIWES 2026 — IT Consortium, Accra, Ghana.*
