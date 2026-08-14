# 04 — Data & Persistence

Where state actually lives, and the correctness problems that appear the moment two requests touch the same row.

1. [[backend/04-data-and-persistence/01-databases-in-the-backend|Databases in the Backend]] — **[Intermediate]** — modelling, querying, and the ORM tradeoff from the application's side

## Go deeper elsewhere
This section is deliberately thin because the depth already exists:
- [[databases/database-design-reference|Database design]] · [[databases/sql-reference|SQL]] · [[databases/nosql-reference|NoSQL]] · [[databases/mysql-reference|MySQL]] — the reference layer
- [[databases/interview/01-sql-modelling-and-internals|Databases interview]] — **the sharpest material**: index internals, isolation levels and write skew, `EXPLAIN`, connection pool sizing, and safely migrating a 500M-row table
- [[architecture/04-distributed-systems/10-distributed-transactions|Distributed transactions]] — isolation and MVCC in depth

## The backend-specific parts
- **Transaction boundaries belong in the service layer**, not the repository — the service knows what must succeed together. → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories|layers]]
- **Concurrent writes are a correctness problem**: optimistic locking (`@Version`), pessimistic (`SELECT … FOR UPDATE`), or an atomic conditional `UPDATE … WHERE qty > 0`. Know which your isolation level requires.
- **The connection pool is usually your real concurrency limit** — and smaller is often faster. Time spent waiting for a connection is invisible unless you instrument it.
- **N+1 queries** are the most common performance regression, and they exhaust the pool, which makes them a *service-wide* incident. → [[backend/interview/01-production-debugging|production debugging]]
- **Migrations must be backwards-compatible** with the currently-running code — expand, migrate, contract.

## Related
- [[backend/README|Backend course]]
