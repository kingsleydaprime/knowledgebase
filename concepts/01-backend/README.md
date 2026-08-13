# Backend Engineering — Concepts

Framework-agnostic backend concepts — the ideas that stay true whether you're writing Express, NestJS, Django, or Spring. For the framework-specific implementations of these same ideas, see `backend/express/`, `backend/nest/`, and `backend/nodejs/` in this vault.

## Reading order
1. [[01-http-servers|http-servers]] — **[Beginner]** — the request lifecycle, routing, middleware chains, and why Node's event loop shapes how backend code is written
2. [[02-backend-best-practices|backend-best-practices]] — **[Beginner]** — error handling, logging, validation, and the security basics every backend needs
3. [[03-apis|apis]] — **[Intermediate]** — REST, GraphQL, gRPC, WebSockets, and when each is the right fit
4. [[04-databases|databases]] — **[Intermediate]** — ORMs, migrations, transactions, indexing (the app-dev side of working with a database)
5. [[05-authentication-flows|authentication-flows]] — **[Intermediate]** — session-based vs token-based auth, OAuth 2.0 flows, API keys, SSO
6. [[06-oauth-provider-integrations|oauth-provider-integrations]] — **[Advanced]** — the practical cut: where real providers deviate from the spec, derived tokens, async publishing, and app-review realities
6. [[06-authorization|authorization]] — **[Advanced]** — RBAC vs ABAC, guards/policies, and object-level authorization (the most commonly missed check)

## Related
- [[backend/README|backend/]] — the framework-specific implementations of these same ideas (Node.js core, then Express or Nest)
- [[concepts/02-frontend/README|frontend concepts]]
- [[cybersecurity/README|cybersecurity curriculum map]] — the security mechanics underneath authentication-flows and backend-best-practices
- [[architecture/system-design-reference|system-design-reference]] — scaling these same concepts across a distributed system
