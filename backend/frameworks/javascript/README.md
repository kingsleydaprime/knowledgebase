# JavaScript / TypeScript Backends

**Concurrency model: [[backend/01-foundations/04-runtime-and-concurrency-models|event loop]].** One thread runs your JavaScript; I/O is handed to libuv and completions come back as callbacks. Everything distinctive about backend JS follows from that one fact — async-by-default APIs, "never block the event loop," `cluster` for multi-core, `worker_threads` for CPU work.

## Sections
1. [[backend/frameworks/javascript/01-node-runtime/README|01 — Node Runtime]] — the platform Express and Nest both sit on
2. [[backend/frameworks/javascript/02-express/README|02 — Express]] — minimal: a router and middleware, everything else is yours
3. [[backend/frameworks/javascript/03-nest/README|03 — Nest]] — opinionated: DI container, modules, decorators. Angular's structure for the backend

## Choosing between them
**Express** when the team is small and you want control — you'll assemble your own [[backend/03-structuring-a-backend/README|structure]], which is fine if you know what you're assembling. **Nest** when several people share the codebase and you want the layering, DI, and conventions decided for you. Nest costs more to learn and pays back in consistency; that's a team-size call, not a technical one.

Also worth knowing: **Fastify** (faster, schema-first validation), **Hono** (edge runtimes), and that Nest can run on a Fastify adapter instead of Express.

## Related
- [[backend/frameworks/README|frameworks/]] · [[backend/interview/02-node-runtime-and-api|Node runtime interview]]
