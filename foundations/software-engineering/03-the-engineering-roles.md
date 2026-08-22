# The Engineering Roles

> **[Beginner]** · What each role actually does day to day, and what genuinely differs between them.

Titles are inconsistent across companies — the same work is "backend engineer" at one and "platform engineer" at another. What's stable is **the layer of the stack you're responsible for, and what you get paged about.**

| Role | Owns | The daily reality | In this vault |
|---|---|---|---|
| **Frontend** | What the user touches | Rendering, state, accessibility, bundle size, "why is it slow on a mid-range Android" | [[frontend/README\|frontend]] |
| **Backend** | Everything behind the API | Data modelling, APIs, auth, queues, "why is p99 latency 4 seconds" | [[backend/README\|backend]] |
| **Full-stack** | Both, end to end | Owning a feature from database to button. Common at startups | both |
| **Mobile** | iOS/Android apps | Platform APIs, offline state, app-store release cycles, device fragmentation | [[projects/arete/learning/backend/01-fundamentals-and-nestjs\|arete]] |
| **Embedded** | Software on hardware | C, constrained memory, interrupts, no OS or a small one, hardware that lies | [[hardware/README\|hardware]] |
| **Systems** | The layer everything runs on | OS internals, compilers, databases, performance measured in microseconds | [[foundations/os/README\|OS]] · [[foundations/compilers/README\|compilers]] |
| **DevOps / SRE** | Delivery and uptime | Pipelines, infrastructure, monitoring, incidents, being on call | [[devops/README\|devops]] |
| **Security** | Making attacks expensive | Threat modelling, reviews, testing, incident response | [[cybersecurity/README\|cybersecurity]] |
| **Data** | Data other people depend on | Pipelines, warehouses, the correctness of numbers people make decisions on | [[ai-ml/01-data-scientist/README\|data scientist]] |
| **ML** | Models in production | Training, evaluation, drift, serving | [[ai-ml/02-ml-engineer/README\|ML engineer]] |
| **AI engineer** | Products built on models | RAG, agents, prompts, **evals**, cost and latency. Mostly application engineering | [[ai-ml/03-ai-engineer/README\|AI engineer]] |

## What actually differs

Less than the table suggests. Every role above runs the same six [[foundations/software-engineering/02-the-software-development-lifecycle|SDLC]] phases and uses the same three habits. What changes:

**The failure you fear.** Frontend fears a broken layout on a device you don't own. Backend fears data loss. SRE fears the pager. Security fears the breach nobody detects. Embedded fears the bug that needs a physical recall. **This is the most honest way to tell roles apart** — it shapes every trade-off the role makes.

**The feedback loop.** Frontend sees the result in a second. Backend in a test run. Embedded in a flash cycle. ML in a training run measured in hours. Slower loops force more care upfront, which is why embedded and ML cultures feel more conservative than web ones.

**How much of the stack you're allowed to ignore.** Nobody holds all of it. The difference is *which* abstractions you may treat as solid — and every role eventually meets the day theirs leaks, which is when the layer underneath stops being optional.

## Seniority, which matters more than specialism

Roughly, and independent of which row you're in:

- **Junior** — given a well-defined task, completes it, asks when stuck
- **Mid** — given a problem, decomposes and solves it, spots the edge cases
- **Senior** — given an ambiguous goal, works out what should be built, and is trusted on the trade-offs
- **Staff+** — works on which problems are worth solving at all

**The jump from junior to mid is mostly about tolerance for ambiguity, not volume of knowledge.** Worth knowing when reading job ads: "3 years experience" is usually a proxy for "has been on the hook for something in production."

## Related
- [[foundations/software-engineering/01-what-software-engineering-is|what software engineering is]]
- [[PRIMETECHIE|the Primetechie path]] — how these layers connect rather than sitting in silos
- [[INTERVIEW|the interview banks]] — organised by these same domains

*Source: [reference]*
