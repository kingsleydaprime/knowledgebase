# Node.js (JavaScript Backends)

## What Node.js is

**Node.js is the program that runs JavaScript outside the browser, and it can be a web server on its own, with no framework.** It comes with a built-in `http` module, so you can take a request and send a response with nothing else installed. Express and NestJS are both built on top of it, so what you learn here is true in both of them.

**Concurrency model: [[backend/01-foundations/04-runtime-and-concurrency-models/index|event loop]].** One thread runs your JavaScript. Waiting on the network or disk is handed to libuv, and the results come back as callbacks. Almost everything particular to backend JavaScript follows from that one fact: async APIs everywhere, "never block the event loop", `cluster` for more cores, and `worker_threads` for heavy CPU work.

## Lessons so far

1. [[backend/frameworks/node/01-env-validation|Validating .env in nodejs]]
2. [[backend/frameworks/node/02-error-handling|Ways to handle errors in Node.js]]

## The runtime facts that matter most
- **The event loop is single-threaded.** Any sync work blocks every pending request → the signature p99 spike with flat p50. → [[backend/interview/01-production-debugging|p99 debugging]]
- **libuv's thread pool defaults to 4** (`UV_THREADPOOL_SIZE`) and serves `fs`, DNS, and some crypto — network I/O does *not* use it.
- **`worker_threads` for CPU, `cluster`/replicas for cores.** They solve different problems.
- **`Buffer.alloc` not `new Buffer`** — the deprecated form returned uninitialised memory and was a type-confusion trap. → [[backend/interview/02-node-runtime-and-api|Q2]]

→ Full depth in [[backend/interview/02-node-runtime-and-api|the Node runtime interview bank]], which was written from a real interview.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Node.js way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Node.js is and a first server**: `node:http`, `createServer`, one thread and the event loop
2. **Routing by hand**: parsing `req.url` with `URL`, matching method and path, a tiny route table
3. **Reading and writing**: streaming the body, parsing JSON safely, body size limits, status and headers
4. **Middleware without a framework**: a `compose()` function, why order matters, and why Express exists
5. **Structuring a Node service**: feature folders, ES modules, one composition root
6. **Validation**: zod at the boundary, so what comes in is typed
7. **Errors**: the four error channels, why `uncaughtException` isn't recovery, errors to status codes — written in part: [[backend/frameworks/node/02-error-handling|Ways to handle errors in Node.js]]
8. **Data**: `pg` and a connection pool, parameterised queries, transactions, migrations
9. **Auth**: password hashing, sessions versus JWTs, checking permissions
10. **Security and cross-cutting**: CORS and security headers by hand, rate limiting, uploads as streams
11. **Testing**: `node:test`, testing a server without opening a port, fakes
12. **Production**: validating env at boot, structured logging, graceful shutdown, `cluster` versus `worker_threads`, never blocking the loop — written in part: [[backend/frameworks/node/01-env-validation|Validating .env in nodejs]]

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/express/index|Express]] · [[backend/frameworks/nestjs/index|NestJS]] — the two frameworks built on Node
- [[networking/09-sockets-and-the-network-api|Sockets & epoll]]

## About this subject

Built from real Node and Nest work in [[projects/index|projects/]]. Until November 2026 Node, Express and NestJS shared one subject, "JavaScript Backends". They were split so each one can teach the whole backend course in its own way.
