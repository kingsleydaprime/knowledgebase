# 03 — Structuring a Backend

**The section that makes this a course rather than a framework tutorial.** Every backend, in every language, faces the same structural questions — and the answers are the same whether you're writing NestJS, Spring, FastAPI, or Axum. Frameworks disagree about syntax and agree almost entirely about shape.

Read in order; each note assumes the previous.

1. [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|Layers — Controllers, Services, Repositories]] — **[Beginner→Intermediate]** — the three jobs every backend separates, the rule that tells you when you've broken it, and the honest caveats (anaemic pass-through services, the "swappable database" myth)
2. [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature|Organising by Layer vs by Feature]] — **[Beginner→Intermediate]** — the folder argument that isn't bikeshedding: change locality, deletability, and how `shared/` rots
3. [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency Injection & Wiring]] — **[Intermediate]** — being handed your tools instead of making them; constructor injection, when interfaces earn their keep, and the scope bugs
4. [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture|Hexagonal & Clean Architecture]] — **[Intermediate→Advanced]** — inverting the dependency so business rules depend on nothing; four names for one idea, and an honest account of what it costs
5. [[backend/03-structuring-a-backend/05-modular-monolith-to-services|Modular Monolith → Services]] — **[Intermediate→Advanced]** — where boundaries actually belong, why to discover them in the cheap medium first, and what changes the moment a call crosses a network

## The through-line

All five notes are one question at different scales:

> **What depends on what, and can you change one thing without changing everything else?**

- Note 1: within a request — the controller depends on the service, not the reverse.
- Note 2: within a codebase — a feature's files depend on each other, not on every other feature.
- Note 3: within a class — declare what you need instead of constructing it.
- Note 4: within an application — the domain depends on nothing.
- Note 5: within a system — a module's boundary is a function call or a network call.

Get the direction of dependency right and most structural questions answer themselves.

## The pragmatic summary

If you read nothing else: **default to layered + by-feature + constructor injection.** Add hexagonal only where the business rules are genuinely complex. Stay a modular monolith until you have a named reason to split — and enforce your module boundaries with a linter, because boundaries maintained by discipline don't survive a deadline.

## Related
- [[backend/README|Backend course]] · [[backend/01-foundations/README|01 — Foundations]]
- [[backend/frameworks/README|frameworks/]] — how Nest, Spring, FastAPI and others implement all of this
- [[architecture/README|Architecture]] — the same questions at system scale
- [[concepts/03-design-patterns/README|Design Patterns]] — repository, adapter, facade
