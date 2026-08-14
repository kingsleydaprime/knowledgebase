# 01 — Node Runtime

The platform underneath every JS backend framework. Notes here are runtime-level, not framework-level.

1. [[backend/frameworks/javascript/01-node-runtime/01-env-validation|Environment Validation]] — failing fast on bad config at boot
2. [[backend/frameworks/javascript/01-node-runtime/02-error-handling|Error Handling]] — the four error channels and why `uncaughtException` isn't recovery

## The runtime facts that matter most
- **The event loop is single-threaded.** Any sync work blocks every pending request → the signature p99 spike with flat p50. → [[backend/interview/01-production-debugging|p99 debugging]]
- **libuv's thread pool defaults to 4** (`UV_THREADPOOL_SIZE`) and serves `fs`, DNS, and some crypto — network I/O does *not* use it.
- **`worker_threads` for CPU, `cluster`/replicas for cores.** They solve different problems.
- **`Buffer.alloc` not `new Buffer`** — the deprecated form returned uninitialised memory and was a type-confusion trap. → [[backend/interview/02-node-runtime-and-api|Q2]]

→ Full depth in [[backend/interview/02-node-runtime-and-api|the Node runtime interview bank]], which was written from a real interview.

## Related
- [[backend/frameworks/javascript/README|JavaScript backends]] · [[foundations/networking/09-sockets-and-the-network-api|Sockets & epoll]]
