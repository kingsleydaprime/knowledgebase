# Express (JavaScript Backend)

## What Express is

**Express is a small web framework for Node.js. It gives you a router and a chain of middleware, and nothing else.** Everything else (structure, validation, how the code is wired together) you choose and build yourself. That is freedom when you know what you're building, and a mess when you don't. This subject shows you how to build it well.

## What you'll build

The whole subject builds **one** app, a step at a time: **Mama Put API**, the backend for a roadside food seller whose customers now order on their phones.

It starts in lesson 1 as a server that answers "Mama Put is open!". By lesson 27 it's a production system:

1. A main API with a menu, orders, customer accounts and kitchen-staff roles, stored in PostgreSQL.
2. A well-designed API: one response shape everywhere, pagination, filtering, searching, sorting and field selection, two versions running side by side, and OpenAPI docs.
3. Payments through Paystack, webhooks in and out, idempotency so nothing happens twice, background jobs, Redis caching, and a kitchen screen that shows new orders live.
4. The same data offered over **GraphQL**, and a **second service** for notifications that the main API talks to over events and **gRPC**, so you learn how microservices talk and how they fail.
5. Tests at every level, logs, metrics and tracing across both services, Docker for the whole system, and automatic deployment when you push.

Every lesson ends with **your project so far** (the folder tree and what each file holds) and explains **the TypeScript it used**, so you don't need to know the language well before you start.

## Lessons

**Part 1: the core backend**

1. [[backend/frameworks/express/01-what-express-is-and-a-first-app|What Express Is, and Your First App]]: setting up the project and following one request from start to finish.
2. [[backend/frameworks/express/02-routing|Routing]]: REST resources, methods, path parameters, query parameters, bodies, status codes and `express.Router()`.
3. [[backend/frameworks/express/03-middleware|Middleware]]: the chain, `next()`, why order is behaviour, and the 404 and error handlers.
4. [[backend/frameworks/express/04-structuring-an-express-app|Structuring an Express App]]: feature folders, routes, services and repositories, and `app.ts` versus `server.ts`.
5. [[backend/frameworks/express/05-wiring-dependencies|Wiring Dependencies]]: factory functions, a composition root, and a first test with a fake.
6. [[backend/frameworks/express/06-validation|Input Validation]]: checking body, path parameters and query parameters with zod at the door, and the line between validation and business rules.
7. [[backend/frameworks/express/07-errors|Errors and Structured Responses]]: the `{ data, meta }` envelope, problem details for errors, request IDs, and one central error handler.
8. [[backend/frameworks/express/08-data-with-postgres|Data with PostgreSQL]]: `pg`, a connection pool, migrations, SQL injection, and a transaction so the last plate goes to one customer.

**Part 2: designing the API properly**

9. [[backend/frameworks/express/09-listing|Pagination, Filtering, Searching, Sorting and Field Selection]]: offset and cursor pagination, allow-lists, and turning query parameters into safe SQL.
10. [[backend/frameworks/express/10-versioning|Versioning]]: breaking changes, the path, header, media-type and query styles, v1 and v2 side by side, and deprecating a version.
11. [[backend/frameworks/express/11-api-docs|API Docs with OpenAPI]]: generating the spec from the zod schemas, interactive docs for both versions, and keeping it honest.

**Part 3: who can do what**

12. [[backend/frameworks/express/12-authentication|Authentication]]: sign-up, password hashing, sessions versus JWTs, refresh tokens, and typing `req.user`. *(in progress: has the `req.user` typing note)*
13. **Authorization**: roles, owning your own orders, and permission checks that can't be forgotten. *(to write)*
14. **Security**: `helmet`, CORS, rate limiting, body limits, and dish photo uploads with `multer`. *(to write)*
15. **Idempotency**: the `Idempotency-Key` header, so a retried "place order" never charges twice. *(to write)*
16. **Testing**: unit tests with fakes, `supertest` against the app, and integration tests on a real database. *(to write)*

**Part 4: what real products need**

17. **Payments and Webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks to a delivery partner. *(to write)*
18. **Background Jobs and Queues**: BullMQ on Redis for work that shouldn't make the customer wait. *(to write)*
19. **Caching with Redis**: caching the menu, and keeping the cache honest when it changes. *(to write)*
20. **Real-time Updates**: a live kitchen screen with server-sent events. *(to write)*

**Part 5: other ways to talk**

21. **GraphQL**: the same menu and orders as a GraphQL API, and when it beats REST. *(to write)*
22. **gRPC**: Protocol Buffers, a gRPC service in Node, and why services use it to talk to each other. *(to write)*

**Part 6: more than one service**

23. **Splitting Out a Microservice**: a separate notifications service, events like `order.placed`, and the outbox pattern. *(to write)*
24. **Calling Other Services Safely**: gRPC calls with timeouts, retries, circuit breakers, and service-to-service auth. *(to write)*

**Part 7: production**

25. **Observability**: structured logs with pino, request IDs across services, metrics and tracing. *(to write)*
26. **Production Config and Docker**: validated config, health checks, graceful shutdown, a Dockerfile, and Docker Compose for the whole system. *(to write)*
27. **CI and Deployment**: GitHub Actions running the tests, migrations on deploy, deploying to a real server, and rolling back. *(to write)*

## What to know

- **Middleware is the whole model.** `(req, res, next)`, order matters, and the error handler takes four arguments (`err, req, res, next`) or it silently isn't one.
- **Use Express 5.** It passes errors from async handlers to your error handler. Express 4 didn't, so an async handler that rejected just hung the request.
- **It gives you no structure.** Impose [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|feature folders]] and [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|a composition root]] yourself, early.
- **It runs on Node**, so every [[backend/frameworks/node/index|runtime]] rule still applies.

## Related

- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/node/index|Node.js]] — what Express runs on
- [[backend/frameworks/nestjs/index|NestJS]] — the same platform, with the structure decided for you
- [[backend/frameworks/flask/index|Flask]] — the same minimalist trade in Python
- [[backend/index|The backend course]] — the ideas these lessons put into practice

## About this subject

Written for Express 5 and Node.js 23.6 or later, which runs TypeScript directly with no build step. Lessons 1–11 were written in November 2026; the rest follow in order. Until November 2026 Express shared a subject with Node.js and NestJS, and it had only one note.
