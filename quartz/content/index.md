# Knowledge Base — kingsleydaprime

> My personal engineering knowledge base. Concepts, implementations, patterns, and practices — built and updated continuously.

This is not a copy of documentation. It's my understanding of how things work — the why, the how, and what I've figured out the hard way.

---

## How to Use This as a Course

The domains below that are actually built out (DSA, AI/ML, cybersecurity, and the `concepts/` folders) are meant to be readable start-to-finish, not just looked up. Each has its own `README.md` acting as the entry point, with notes tagged **[Beginner]**, **[Intermediate]**, or **[Advanced]** in the order they're meant to be read — a tag marks how much prior context a note assumes *within that folder*, not an absolute difficulty across the whole vault.

Start here, depending on what you want:
- [[foundations/dsa/README|Data Structures & Algorithms]] → then [[foundations/dsa/06-patterns/README|LeetCode Patterns]]
- [[ai-ml/README|AI & ML]] — orientation → maths → building with code → building your own models
- [[cybersecurity/README|Cybersecurity]] — fundamentals → ethical hacking → network/web security → cryptography
- [[concepts/01-backend/README|Backend]], [[concepts/02-frontend/README|Frontend]], [[concepts/03-design-patterns/README|Design Patterns]], [[concepts/04-best-practices/README|Best Practices]] — framework-agnostic engineering concepts

A [Beginner] tag doesn't mean "skip if you're experienced" — it just means the note doesn't lean on anything else in the folder yet. Read a folder's notes in order at least once even if a topic sounds familiar; later notes assume earlier ones without re-explaining them.

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
├── ai-ml/                        # numbered course, 5 phases: 01-fundamentals →
│   ├── 01-fundamentals/          # 02-maths (linear-algebra/calculus/probability) →
│   ├── 02-maths/                 # 03-ml-engineering (data/training/fine-tuning) →
│   ├── 03-ml-engineering/        # 04-computer-vision → 05-building-your-own-models
│   ├── 04-computer-vision/
│   └── 05-building-your-own-models/
│
├── ai-automation/                # scaffold only — n8n-focused, no content written yet
│
├── cybersecurity/                # numbered course, 5 stages: 01-fundamentals →
│   ├── 01-fundamentals/          # 02-ethical-hacking → 03-network-security →
│   ├── 02-ethical-hacking/       # 04-web-security → 05-cryptography
│   ├── 03-network-security/      # (ethical-hacking includes practice-exercises +
│   ├── 04-web-security/          #  a worked-solutions companion file)
│   └── 05-cryptography/
│
├── concepts/                     # numbered course: framework-agnostic engineering ideas
│   ├── 01-backend/
│   ├── 02-frontend/
│   ├── 03-design-patterns/
│   └── 04-best-practices/
│
├── devops/                       # numbered course: 01-linux → 02-docker →
│   ├── 01-linux/                 # 03-cloud → 04-vps. 01-linux/15-rhcsa/ is the
│   │   └── 15-rhcsa/             # RHCSA cert track (own practice-exercises +
│   ├── 02-docker/                # solutions), built on top of 01-linux fundamentals
│   ├── 03-cloud/
│   └── 04-vps/
│
├── backend/                      # scaffold — shared nodejs/ core, then pick a track
│   ├── 01-nodejs/
│   ├── 02-express/
│   └── 03-nest/
│
├── frontend/                     # scaffold — react/ has 1 note, next/ is empty so far
│   ├── 01-react/
│   ├── 02-next/
│   └── vue/                      # untouched, empty
│
├── databases/, architecture/, git/, hardware/, tools/, references/
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
