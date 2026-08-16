---
title: Kingsley's Knowledge Base
---

> **software · infrastructure · security · hardware · ML · engineering · CS theory**
>
> 1,150 notes. Not a mirror of documentation — my understanding of how things actually work, the why and the how, and what I figured out the hard way.

Docs already exist. This is the layer underneath them: the mental models, the failure modes, and the things that only make sense once you've broken them yourself.

---

## Start here

🕶️ **[[PRIMETECHIE|The Primetechie Path]]** — the spine of this whole vault. A tiered progression from *"it works on my machine, and I know why"* to the engineer everyone escalates to, with gates in all four disciplines. **Every gate is something you can demonstrate, not something you've read.** If you want an order to do all this in, start here.

🎯 **[[INTERVIEW|Interview Prep]]** — every domain has a bank: the question, what a strong answer covers, and the detail that separates memorised from understood.

🛠️ **[[project-ideas|Project Ideas]]** — notes are a map; this is the territory. Tiered builds across every column, tied to the notes each one exercises.

---

## The five columns

| | | |
|---|---|---|
| 💻 **Software** | [[backend/README\|Backend]] · [[foundations/dsa/README\|DSA]] · [[architecture/README\|Architecture]] · [[languages/01-java/README\|Java]] · [[ai-ml/03-ai-engineer/README\|AI Engineering]] | backends, systems, algorithms, building on pre-trained models |
| ☁️ **Infrastructure** | [[devops/README\|DevOps]] · [[foundations/networking/README\|Networking]] · [[databases/database-design-reference\|Databases]] | Linux → containers → orchestration → CI/CD → observability |
| 🔐 **Security** | [[cybersecurity/README\|Cybersecurity]] | offence *and* defence — you can't do one well without the other |
| 🔌 **Hardware** | [[hardware/README\|Hardware & Embedded]] | electricity → embedded → RF → a board that physically exists |
| 🧠 **ML & Data** | [[ai-ml/README\|AI & ML]] · [[ai-ml/00-foundations/03-mathematics/README\|the maths]] | training models and reasoning from data — a different bedrock |

**AI sits in two columns on purpose.** *Using* a model is software engineering — APIs, retries, schemas, evals, cost. *Training* one isn't: its foundation is linear algebra, calculus and probability, and its failure modes are leakage, overfitting and drift rather than bugs. [[ai-ml/README|The AI/ML course]] splits the same way.

Most engineering vaults are column one with a bit of column two. The point of this one is the boundaries — being the person who follows a problem from a web request down to a voltage rail, or from a dashboard back to a leaked feature, instead of handing it off at the edge of a job title.

---

## New to any of this?

- **Never used an LLM seriously?** → [[using-ai/README|Using AI]] — eight notes, no code, for people who want to *use* these tools well rather than build with them.
- **Want the wire-level foundation?** → [[foundations/networking/README|Networking]] — the layer under devops, security and distributed systems.
- **Preparing for something?** → [[INTERVIEW|the interview index]].

---

## How the notes are written

Each course folder has a `README.md` entry point and notes numbered in reading order. Course notes follow one shape:

**The kid version first** — plain-language intuition before any depth · **the actual content** — tables, worked examples, real failure modes · **key insight** — the one thing to keep if you forget the rest · **related** — wikilinks out, always.

Notes are tagged **[Beginner]** / **[Intermediate]** / **[Advanced]**, marking how much prior context a note assumes *within its folder* — not absolute difficulty. A [Beginner] tag doesn't mean skip it if you're experienced.

---

## What's actually built, and what isn't

This vault labels its own gaps rather than implying uniform coverage.

**Built out and readable start-to-finish:** networking · DSA · backend · architecture (incl. distributed systems) · devops · java · AI/ML · using-ai · cybersecurity · hardware · research · concepts · operating systems · compilers · databases

**Written, but `[reference]` — read and assembled, not validated by building:** [[engineering/README|engineering]] (continuum mechanics · control theory) · [[robotics/README|robotics]] · [[databases/README|databases]] (the internals course) · the CS-theory spine ([[foundations/discrete-math/README|discrete maths]] · [[foundations/theory-of-computation/README|theory of computation]] · [[foundations/computer-architecture/README|computer architecture]] · [[foundations/numerical-methods/README|numerical methods]] · [[foundations/information-theory/README|information theory]] · [[foundations/gpu-and-parallel-computing/README|GPU & parallel]] · [[foundations/computer-graphics/README|graphics]] · [[foundations/programming-language-theory/README|PL theory]]). Each says so on its own front page, and says what would close the gap.

**Honest scaffold — a stated direction, not knowledge yet:** [[ai-automation/README|ai-automation]] · parts of [[frontend/README|frontend]]

Where a folder is a plan rather than a course, it says so in its first paragraph. Where a topic has been read but not practised, the notes say that too — because *"reading is not a rank"* is the rule the whole vault is organised around.

---

*Personal knowledge base of **Kingsley Ihemelandu** — Systems Engineer · Builder · Founder [@Spectroniq](https://linkedin.com/company/spectroniq). Started properly during SIWES 2026, IT Consortium, Accra. Source on [GitHub](https://github.com/kingsleydaprime/knowledgebase).*
