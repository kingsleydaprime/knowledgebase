# Knowledge Base — kingsleydaprime

> My personal engineering knowledge base. Concepts, implementations, patterns, and practices — built and updated continuously.

This is not a copy of documentation. It's my understanding of how things work — the why, the how, and what I've figured out the hard way.

---

## How to Use This as a Course

The domains that are actually built out — **networking, DSA, backend, architecture (incl. distributed systems), devops, java, AI/ML, using-ai, cybersecurity, research, and `concepts/`** — are meant to be readable start-to-finish, not just looked up. (Still scaffold, and labelled as such below: `ai-automation/`, `frontend/01-react`+`02-next`, `foundations/os`, and parts of `backend/`.) Each has its own `README.md` acting as the entry point, with notes tagged **[Beginner]**, **[Intermediate]**, or **[Advanced]** in the order they're meant to be read — a tag marks how much prior context a note assumes *within that folder*, not an absolute difficulty across the whole vault.

**Two cross-cutting entry points, added August 2026:**
- 🕶️ **[[PRIMETECHIE|The Primetechie Path]]** — a tiered progression through the whole vault (Builder → Diagnostician → Systems Thinker → Distributed Mind → Specialist → Force Multiplier), where every gate is something you can *demonstrate*, not something you've read. Start here if you want an order to do all this in.
- 🎯 **[[INTERVIEW|Interview Prep Index]]** — every domain now has an `interview/` folder: the question, what a strong answer covers, and the detail that separates memorised from understood.

Start here, depending on what you want:
- [[foundations/networking/README|Networking]] — the wire up to the web: link layer → IP → TCP/congestion control → DNS/TLS/HTTP → QUIC → debugging. The foundation under devops, security, and distributed systems
- [[foundations/dsa/README|Data Structures & Algorithms]] → then [[foundations/dsa/06-patterns/README|LeetCode Patterns]]
- [[using-ai/README|Using AI]] — **start here if you're new to AI and don't write code.** Eight notes on using LLMs well: what they are, how to brief them, how to check them, what not to paste. The on-ramp to everything below
- [[ai-ml/README|AI & ML]] — split into three career paths (data scientist, ML engineer, AI engineer) over a shared foundation
- [[cybersecurity/README|Cybersecurity]] — fundamentals → ethical hacking → network/web security → cryptography → attacks taxonomy → security operations (blue team) → GRC → cloud
- [[backend/README|Backend]] — a full course: foundations → API design → **structuring a backend** (layers, DI, hexagonal, modular monolith) → data → auth, plus `frameworks/` for Node/Nest/Spring/FastAPI/Axum
- [[concepts/02-frontend/README|Frontend]], [[concepts/03-design-patterns/README|Design Patterns]], [[concepts/04-best-practices/README|Best Practices]] — engineering ideas that belong to no single domain
- [[languages/01-java/README|Java]] — the JVM, concurrency, and the Spring Boot/build-tools ecosystem
- [[devops/README|DevOps]] — Linux → containers → orchestration → CI/CD → IaC → observability
- [[architecture/README|Architecture]] — system design (scaling, caching, patterns) + distributed systems (consensus, consistency, partitioning)
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
│
├── foundations/
│   ├── dsa/                      # numbered course: iterations → data types → data
│   │   │                         # structures → algorithms → patterns/ (15 LeetCode patterns)
│   │   └── pdfs/                 # original Codility-style course material, untouched
│   ├── networking/               # numbered course (16 notes, built Aug 2026): the model
│   │                             # & link layer → IP/routing → UDP/TCP/congestion/sockets
│   │                             # → DNS/HTTP/TLS/QUIC → middleboxes/performance/debugging.
│   │                             # From Kurose & Ross, Stevens, RFCs, Grigorik.
│   └── os/                       # partially built — fundamentals.md + interview/, with a
│                                 # curriculum plan in its README. Honest scaffold.
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
│   └── 11-delivery-and-advanced/
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
├── databases/, git/, hardware/, tools/
│                                 # unordered reference material, not course-structured
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
