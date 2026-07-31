# Knowledge Base — kingsleydaprime

> My personal engineering knowledge base. Concepts, implementations, patterns, and practices — built and updated continuously.

This is not a copy of documentation. It's my understanding of how things work — the why, the how, and what I've figured out the hard way.

---

## How to Use This as a Course

The domains below that are actually built out (DSA, AI/ML, cybersecurity, and the `concepts/` folders) are meant to be readable start-to-finish, not just looked up. Each has its own `README.md` acting as the entry point, with notes tagged **[Beginner]**, **[Intermediate]**, or **[Advanced]** in the order they're meant to be read — a tag marks how much prior context a note assumes *within that folder*, not an absolute difficulty across the whole vault.

Start here, depending on what you want:
- [[foundations/dsa/README|Data Structures & Algorithms]] → then [[foundations/dsa/06-patterns/README|LeetCode Patterns]]
- [[ai-ml/README|AI & ML]] — split into three career paths (data scientist, ML engineer, AI engineer) over a shared foundation
- [[cybersecurity/README|Cybersecurity]] — fundamentals → ethical hacking → network/web security → cryptography → attacks taxonomy → security operations (blue team) → GRC → cloud
- [[concepts/01-backend/README|Backend]], [[concepts/02-frontend/README|Frontend]], [[concepts/03-design-patterns/README|Design Patterns]], [[concepts/04-best-practices/README|Best Practices]] — framework-agnostic engineering concepts
- [[languages/01-java/README|Java]] — the JVM, concurrency, and the Spring Boot/build-tools ecosystem
- [[devops/README|DevOps]] — Linux → containers → orchestration → CI/CD → IaC → observability
- [[architecture/README|Architecture]] — system design (scaling, caching, patterns) + distributed systems (consensus, consistency, partitioning)

A [Beginner] tag doesn't mean "skip if you're experienced" — it just means the note doesn't lean on anything else in the folder yet. Read a folder's notes in order at least once even if a topic sounds familiar; later notes assume earlier ones without re-explaining them.

## → Ready to build?

Notes are a map, not reps. **[[project-ideas|Project Ideas]]** is the companion build-list — concrete projects across every domain (Java/systems, DevOps, AI engineering, ML engineering, data science), tiered by difficulty and tied to the notes each one exercises. Pick one and finish it.

---

## Structure

Course domains use numbered folders/files (`01-`, `02-`...) so the reading order shows up directly in the file tree, not just inside a README. Everything else is unordered reference material.

```
knowledgebase/
│
├── foundations/
│   ├── dsa/                      # numbered course: iterations → data types → data
│   │   │                         # structures → algorithms → patterns/ (15 LeetCode patterns)
│   │   └── pdfs/                 # original Codility-style course material, untouched
│   ├── os/                       # fundamentals.md
│   └── networking/                # currently empty
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
├── concepts/                     # numbered course: framework-agnostic engineering ideas
│   ├── 01-backend/
│   ├── 02-frontend/
│   ├── 03-design-patterns/
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
├── backend/                      # scaffold — shared nodejs/ core, then pick a track
│   ├── 01-nodejs/
│   ├── 02-express/
│   └── 03-nest/
│
├── frontend/                     # mixed — react/ and next/ are still scaffold, but
│   ├── 01-react/                 # gsap/, framer-motion/, and threejs/ are full written
│   ├── 02-next/                  # courses (tweens/timelines, gestures/variants,
│   ├── 03-gsap/                  # scene/materials/R3F, each with performance notes)
│   ├── 04-framer-motion/
│   ├── 05-threejs/
│   └── vue/                      # untouched, empty
│
├── architecture/                 # numbered course: system design (fundamentals →
│   ├── 01-system-design-fundamentals/  # building-blocks → patterns) + distributed
│   ├── 02-building-blocks/       # systems (04 — consensus/clocks/consistency/2PC).
│   ├── 03-architectural-patterns/  # roadmap.sh-cross-referenced; DDIA for dist-sys.
│   ├── 04-distributed-systems/   # Keeps system-design-reference.md as a cheat-sheet.
│   └── 05-case-studies/
│
├── databases/, git/, hardware/, tools/, references/
│                                 # unordered reference material, not course-structured
│
├── problem-solving/, blog-drafts/
│
└── projects/                     # per-project learning logs, not course material
```

---

## The Rule

**Concept or implementation?**

- *Is this true regardless of language or framework?* → `concepts/` or `foundations/`
- *Is this how a specific tool does it?* → that tool's folder
- *Is this how to think about a problem?* → `problem-solving/`
- *Is this a dev environment or tooling thing?* → `tools/`

Notes capture **understanding** — the why and how. Not a copy of docs. Docs already exist.

---

## Note Format

Each note follows this structure where relevant:

```markdown
# Topic Name
> Framework/Language vX · Last updated Month Year

## What it is
## Why it exists / the problem it solves
## How it works
## Example
## Gotchas / what I learned the hard way
## References
```

---

## About

Personal knowledge base of **Kingsley Ihemelandu** ([@kingsleydaprime](https://github.com/kingsleydaprime)).

Systems Engineer · Builder · Founder [@Spectroniq](https://linkedin.com/company/spectroniq)

*Started building this properly during SIWES 2026 — IT Consortium, Accra, Ghana.*
