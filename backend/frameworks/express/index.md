# Express (JavaScript Backends)

## What Express is

**Express is a small web framework for Node.js. It gives you a router and a chain of middleware, and nothing else.** Everything else (structure, validation, how the code is wired together) you choose and build yourself. That is freedom when you know what you're building, and a mess when you don't.

## Lessons so far

1. [[backend/frameworks/express/01-extending-express-types|Extending express types]]

## What to know
- **Middleware is the whole model** — `(req, res, next)`, order matters, and the error handler takes four arguments (`err, req, res, next`) or it silently isn't one.
- **Async errors are not caught automatically** in Express 4 — an async handler that rejects hangs the request unless you wrap it or use Express 5.
- **It gives you no structure.** Impose [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|feature folders]] and [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|a composition root]] yourself, early.
- **It runs on Node**, so every [[backend/frameworks/node/index|runtime]] rule still applies.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Express way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Express is and a first app**: `express()`, `app.listen`, and how a request travels through it
2. **Routing**: `app.get`, `express.Router`, params, query, `res.status().json()`
3. **Middleware**: `(req, res, next)`, why order matters, `express.json()`, the four-argument error handler
4. **Structuring an Express app**: a router per feature, thin handlers, services underneath
5. **Wiring dependencies**: no container, so a composition root and factory functions
6. **Validation**: zod middleware for body, params and query
7. **Errors**: async errors in Express 4 versus 5, one central error handler, errors to status codes
8. **Data**: Prisma or `pg` behind a repository, transactions, migrations
9. **Auth**: JWT or session middleware, typing `req.user`, role checks — written in part: [[backend/frameworks/express/01-extending-express-types|Extending express types]]
10. **Security and cross-cutting**: `helmet`, `cors`, `express-rate-limit`, `multer` for uploads
11. **Testing**: supertest against `app`, no port needed
12. **Production**: config, logging with pino, graceful shutdown, `trust proxy` behind a load balancer

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/node/index|Node.js]] — what Express runs on
- [[backend/frameworks/flask/index|Flask]] — the same minimalist trade in Python
- [[backend/01-foundations/03-the-request-lifecycle/index|The Request Lifecycle]]

## About this subject

Until November 2026 Express shared a subject with Node.js and NestJS. It has its own subject now so it can teach the whole backend course the Express way.
