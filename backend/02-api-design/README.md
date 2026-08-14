# 02 — API Design

The contract between your backend and everything that calls it. Design decisions here are the hardest to reverse — you can refactor internals freely, but a published API shape is load-bearing for every client you don't control.

1. [[backend/02-api-design/01-apis-and-rest|APIs & REST]] — **[Intermediate]** — resources, methods, status codes, and which parts of REST actually pay off

## Not yet written
Planned, and honestly absent — the questions this section should answer:
- **Versioning, pagination, filtering** — URL vs header versioning; **cursor over offset** pagination (offset breaks when rows are inserted and gets slower with depth)
- **Errors and status codes** — a consistent error envelope (RFC 9457 `application/problem+json`), 400 vs 422, 401 vs 403, and never leaking a stack trace
- **Beyond REST** — GraphQL (and its [[backend/interview/01-production-debugging|N+1 problem]]), gRPC, tRPC, webhooks
- **Contracts and documentation** — OpenAPI generated from code rather than maintained beside it

Meanwhile, the material exists in interview form: [[concepts/interview/01-apis-auth-and-practices|APIs, Auth & Practices]] covers REST semantics, idempotency, and safe/idempotent methods with worked answers.

## Related
- [[backend/README|Backend course]] · [[foundations/networking/11-http-evolution|HTTP evolution]] — what your API rides on
- [[languages/01-java/05-web-and-api/03-api-design-and-documentation|API design & docs (Java)]]
