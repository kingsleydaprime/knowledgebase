# Design Patterns

The classic Gang-of-Four object-oriented design patterns — reusable, named solutions to recurring problems in how objects are created, composed, and made to communicate. The value of this vocabulary is mostly about recognition and communication: naming a shape lets you say "just use a Strategy here" instead of re-deriving the same structure from scratch, and lets you recognize a pattern already implicitly present in unfamiliar code.

## Reading order
1. [[01-creational-patterns|creational-patterns]] — **[Beginner]** — Factory, Builder, Singleton, Prototype — how objects get created
2. [[02-structural-patterns|structural-patterns]] — **[Intermediate]** — Adapter, Decorator, Proxy, Facade — how objects get composed
3. [[03-behavioral-patterns|behavioral-patterns]] — **[Advanced]** — Observer, Strategy, Command, Iterator — how objects communicate and share responsibility

## A note on architectural patterns

MVC, CQRS, Event-Driven Architecture, Microservices vs. Monolith — the larger, system-level patterns rather than object-level ones — are **not** duplicated here. They're already covered in real depth, with worked examples, in `architecture/system-design-reference.md` (see its sections on Microservices vs Monolith and Key Design Patterns specifically) — start there for that layer.

## Related
- [[concepts/01-backend/README|backend concepts]]
- [[concepts/02-frontend/README|frontend concepts]]
- [[architecture/system-design-reference|system-design-reference]]
