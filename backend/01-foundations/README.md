# 01 — Foundations

What a backend is, how a request physically arrives and is handled, and the concurrency model your framework sits on. Everything in the rest of the course assumes these four notes.

1. [[backend/01-foundations/01-what-a-backend-is|What a Backend Actually Is]] — **[Beginner]** — the four responsibilities, the "never trust the client" rule everything follows from, and where the frontend boundary sits
2. [[backend/01-foundations/02-http-servers|HTTP Servers]] — **[Beginner]** — how requests physically arrive and get dispatched
3. [[backend/01-foundations/03-the-request-lifecycle|The Request Lifecycle]] — **[Beginner→Intermediate]** — the nine stages every framework implements, the middleware onion, and a symptom→stage debugging table
4. [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — **[Intermediate]** — ⭐ thread-per-request vs event loop vs green threads, and **why backend frameworks differ at all**

⭐ Note 4 is the highest-leverage note in the course. It's what turns [[backend/frameworks/README|frameworks/]] from twenty things to memorise into three ideas and twenty vocabularies.

## Related
- [[backend/README|Backend course]] · [[backend/03-structuring-a-backend/README|03 — Structuring a Backend]]
- [[foundations/networking/README|Networking]] — TCP, HTTP, and TLS underneath this
