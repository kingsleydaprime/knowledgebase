# Knowledge Base — kingsleydaprime

> My personal engineering knowledge base. Concepts, implementations, patterns, and practices — built and updated continuously.

This is not a copy of documentation. It's my understanding of how things work — the why, the how, and what I've figured out the hard way.

---

## Structure

```
knowledgebase/
│
├── foundations/                  # Universal CS concepts — language agnostic
│   ├── networking/               # OSI model, HTTP/HTTPS, TCP/UDP, DNS, sockets
│   ├── os/                       # Operating systems, Linux internals, processes, memory
│   ├── data-structures/          # Arrays, linked lists, trees, graphs, heaps
│   ├── algorithms/               # Sorting, searching, complexity, recursion
│   └── computer-science/         # General CS — compilers, memory, concurrency
│
├── concepts/                     # Engineering concepts — framework/language agnostic
│   ├── backend/
│   │   ├── README.md             # What backend engineering actually is
│   │   ├── http-servers.md       # Request lifecycle, routing, middleware, parsing
│   │   ├── authentication.md     # JWT, sessions, OAuth, API keys
│   │   ├── authorization.md      # RBAC, ABAC, guards, policies
│   │   ├── apis.md               # REST, GraphQL, gRPC, WebSockets
│   │   ├── databases.md          # ORMs, migrations, transactions, indexing
│   │   └── best-practices.md     # Error handling, logging, validation, security
│   │
│   ├── frontend/
│   │   ├── README.md
│   │   ├── rendering.md          # CSR, SSR, SSG, ISR, hydration
│   │   ├── state-management.md   # Local, global, server state
│   │   └── best-practices.md     # Accessibility, performance, component design
│   │
│   ├── design-patterns/
│   │   ├── README.md
│   │   ├── creational.md         # Singleton, Factory, Builder, Prototype
│   │   ├── structural.md         # Adapter, Decorator, Proxy, Facade
│   │   ├── behavioral.md         # Observer, Strategy, Command, Iterator
│   │   └── architectural.md      # MVC, CQRS, Event-driven, Microservices, Monolith
│   │
│   ├── system-design/
│   │   ├── README.md
│   │   ├── scalability.md        # Horizontal vs vertical, load balancing
│   │   ├── caching.md            # Cache strategies, Redis, CDN
│   │   └── distributed-systems.md # CAP theorem, consistency, availability
│   │
│   └── best-practices/           # General engineering practices
│       ├── clean-code.md
│       ├── git-practices.md       # PR structure, branching, commit messages
│       ├── documentation.md
│       └── testing.md             # Unit, integration, e2e, TDD
│
├── problem-solving/               # How to think, not just what to know
│   ├── README.md
│   ├── frameworks.md              # How to approach any problem from scratch
│   ├── debugging.md               # Systematic debugging methodology
│   ├── system-thinking.md         # Breaking big problems into small ones
│   └── life-tech-parallels.md     # Applying engineering thinking beyond tech
│
├── languages/                     # The language itself — syntax, idioms, internals
│   ├── javascript/
│   ├── typescript/
│   ├── python/
│   ├── go/
│   ├── java/
│   └── rust/
│
├── backend/                       # Framework-specific implementation
│   ├── nodejs/
│   ├── nestjs/
│   ├── express/
│   ├── django/
│   ├── fastapi/
│   └── spring/
│
├── frontend/                      # Framework-specific implementation
│   ├── react/
│   ├── nextjs/
│   └── tailwind/
│
├── devops/                        # Infrastructure, deployment, automation
│   ├── linux/
│   ├── docker/
│   ├── kubernetes/
│   ├── ci-cd/
│   ├── terraform/
│   └── aws/
│
├── ai-ml/                         # Machine learning and AI systems
│   ├── fundamentals/
│   ├── pytorch/
│   ├── mlops/
│   └── llms/
│
├── cybersecurity/                 # Security concepts and ethical hacking
│   ├── networking-security/
│   ├── web-security/
│   └── ethical-hacking/
│
├── embedded/                      # Hardware and embedded systems
│   ├── arduino/
│   ├── esp32/
│   └── ros2/
│
├── mobile/
│   ├── react-native/
│   └── java-android/
│
├── databases/
│   ├── postgresql/
│   ├── mongodb/
│   └── redis/
│
└── tools/                         # Dev tools and environment setup
    ├── neovim/
    ├── vscode/
    └── terminal/
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
