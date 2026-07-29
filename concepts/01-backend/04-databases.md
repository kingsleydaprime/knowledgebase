# Databases — ORMs, Migrations, Transactions, Indexing

This note is the application-development side of working with a database — how backend code actually talks to one day to day. For the database engines themselves (SQL/NoSQL specifics), see `databases/` in this vault; for scaling a database across a distributed system (replication, sharding, CAP theorem), see `architecture/system-design-reference.md`, which already covers that ground in depth.

## ORMs — trading some control for a lot of convenience

An ORM (Object-Relational Mapper — Prisma, TypeORM, Sequelize, Django's ORM) lets you interact with a database using your programming language's objects/methods instead of writing raw SQL directly.

```javascript
// ORM (Prisma-style)
const user = await prisma.user.findUnique({ where: { id: 42 }, include: { posts: true } });

// equivalent raw SQL
// SELECT * FROM users WHERE id = 42;
// SELECT * FROM posts WHERE author_id = 42;
```

The ORM generates the SQL for you, handles connection pooling, and often provides protection against SQL injection by default (parameterizing queries automatically — see [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]]) — a meaningful security benefit, not just convenience. The tradeoff: an ORM's generated SQL isn't always the most efficient query for a given case, and complex queries can be awkward or inefficient to express through an ORM's abstraction compared to hand-written SQL — most real projects end up dropping to raw SQL for the specific handful of queries where the ORM's abstraction gets in the way, rather than using purely one approach everywhere.

## Migrations — versioning your schema like you version your code

A migration is a versioned, incremental change to the database schema (add a column, create a table, add an index), checked into source control alongside the application code that depends on it — so the schema's history is tracked explicitly and reproducibly, the same way Git tracks code changes, instead of manually running ad-hoc `ALTER TABLE` statements against a database and hoping every environment stays in sync.

```javascript
// example migration (Prisma-style shape)
exports.up = async (db) => {
  await db.schema.alterTable("users", (table) => {
    table.string("phone_number").nullable();
  });
};
exports.down = async (db) => {
  await db.schema.alterTable("users", (table) => {
    table.dropColumn("phone_number");
  });
};
```

The `down` function (reversing a migration) matters as much as `up` — it's what lets a bad migration be rolled back cleanly in production rather than requiring manual, error-prone cleanup.

## Transactions — all-or-nothing groups of operations

A transaction groups multiple database operations so they either **all** succeed together or **all** roll back together — critical whenever an operation involves more than one write that has to stay consistent (transferring money: debit one account, credit another — either both happen or neither does).

```javascript
await db.transaction(async (trx) => {
  await trx("accounts").where({ id: fromId }).decrement("balance", amount);
  await trx("accounts").where({ id: toId }).increment("balance", amount);
  // if either line throws, BOTH changes are rolled back automatically
});
```

Without a transaction, a crash or error between the two operations above leaves the database in an inconsistent state — money debited from one account but never credited to the other. This is the practical, everyday manifestation of the **ACID** properties (Atomicity, Consistency, Isolation, Durability) that traditional relational databases are built around.

## Indexing — the difference between a fast query and a slow one at scale

Without an index, finding rows matching a condition means scanning every row in a table (a **full table scan**) — fine on a table with a hundred rows, ruinous on one with a hundred million. An index is a separate, ordered data structure (commonly a B-tree) that lets the database jump directly to matching rows instead of scanning everything — conceptually the same win [[05-searching|binary search]] provides over linear search, applied to database rows instead of an in-memory array.

```sql
CREATE INDEX idx_users_email ON users(email);
-- a query like `SELECT * FROM users WHERE email = 'x@example.com'`
-- goes from an O(n) full table scan to something close to O(log n)
```

Indexes aren't free — they speed up reads on the indexed column(s) but slow down writes slightly (the index itself has to be updated on every insert/update) and consume additional storage. The practical skill is indexing the columns that are actually queried/filtered/joined on frequently, not indexing everything defensively.

## Gotchas

- The **N+1 query problem** — fetching a list of items, then looping over them to fetch each one's related data with a separate query per item, instead of one batched query — is one of the most common ORM-related performance bugs, since ORMs make it easy to accidentally write this pattern without realizing each `.posts` access behind a loop is triggering its own database round-trip.
- Migrations that aren't reversible (no working `down`) or that aren't tested against production-like data before deploying are a common source of real incidents — a migration that works instantly on a development database with 10 rows can lock a production table for minutes on one with 10 million.
- An index doesn't help a query that doesn't use it — mismatched query patterns (searching on a computed/transformed version of a column that isn't itself indexed, for instance) silently fall back to a full scan despite an index technically existing on the underlying column.

## Related
- [[03-apis|apis]]
- [[02-backend-best-practices|backend-best-practices]]
- [[05-searching|searching]] — why indexing provides the speedup it does
