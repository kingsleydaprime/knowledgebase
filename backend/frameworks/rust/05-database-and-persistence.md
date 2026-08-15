# Database and Persistence

**[Intermediate → Advanced]** — `sqlx` checking your SQL against a real schema at compile time, and the options when that isn't what you want.

## `sqlx` — compile-time checked SQL

The headline feature, and it's genuinely unusual:

```rust
let user = sqlx::query_as!(
    User,
    "SELECT id, email, created_at FROM users WHERE id = $1",
    id
)
.fetch_one(&pool)
.await?;
```

The `!` macro **connects to your development database at compile time**, asks Postgres to describe the query, and verifies:

- the SQL parses and the tables and columns exist
- the parameter types match what you passed
- the returned columns map onto `User`'s fields, including nullability

A typo'd column name is a **compile error**. A column that's `NULL`-able mapped to a non-`Option` field is a compile error. Nobody else does this — [[backend/frameworks/go/05-database-access|Go's sqlc]] achieves it by codegen, and most ORMs don't achieve it at all.

```bash
export DATABASE_URL=postgres://localhost/myapp_dev
cargo sqlx prepare              # caches query metadata into .sqlx/ — COMMIT THIS
```

`cargo sqlx prepare` is what makes CI and Docker builds work without a live database. Forgetting to re-run it after changing a query is the standard sqlx annoyance: your build fails in CI with "no cached data for this query".

The non-macro API skips the checking and works with a runtime-determined schema:

```rust
let users = sqlx::query_as::<_, User>("SELECT * FROM users WHERE active = $1")
    .bind(true)
    .fetch_all(&pool)
    .await?;
```

`query_as::<_, User>` needs `User: FromRow`, usually derived.

### Fetch methods

```rust
.fetch_one(&pool).await?         // exactly one; Err(RowNotFound) if none
.fetch_optional(&pool).await?    // Option<T> — use this for lookups
.fetch_all(&pool).await?         // Vec<T> — the whole result in memory
.fetch(&pool)                    // a Stream — for large results
.execute(&pool).await?           // no rows; returns rows_affected()
```

```rust
let mut rows = sqlx::query_as!(Event, "SELECT * FROM events").fetch(&pool);
while let Some(event) = rows.try_next().await? {
    process(event).await?;                    // constant memory over a huge table
}
```

`fetch_optional` over `fetch_one` for anything that might legitimately be absent — otherwise "not found" arrives as an error you have to pattern-match out of `sqlx::Error`.

## Transactions

```rust
let mut tx = pool.begin().await?;

sqlx::query!("UPDATE accounts SET balance = balance - $1 WHERE id = $2", amount, from)
    .execute(&mut *tx).await?;                 // note &mut *tx

sqlx::query!("UPDATE accounts SET balance = balance + $1 WHERE id = $2", amount, to)
    .execute(&mut *tx).await?;

tx.commit().await?;
```

**Dropping a `Transaction` without committing rolls it back.** That's [[languages/03-rust/03-ownership|RAII]] applied to transactions — an early `?` return rolls back automatically, with no `defer tx.Rollback()` and no `finally`. It's the cleanest transaction handling of any language here.

The `&mut *tx` is a deref-coercion wart you'll type a lot. It's required because `Transaction` derefs to a connection and the executor wants `&mut Connection`.

**Never hold a transaction across an HTTP call.** It holds a pool connection for the duration; a slow external service becomes pool exhaustion.

## The pool

```rust
let pool = PgPoolOptions::new()
    .max_connections(25)
    .min_connections(5)
    .acquire_timeout(Duration::from_secs(3))
    .idle_timeout(Duration::from_secs(600))
    .max_lifetime(Duration::from_secs(1800))
    .connect(&database_url)
    .await?;
```

Same sizing logic as [[backend/frameworks/go/05-database-access|Go]]: `max_connections × replicas` under the database's limit, with headroom.

The async-specific hazard is worth repeating from [[backend/frameworks/rust/04-async-pitfalls|Async Pitfalls]] — **tasks are cheap enough to spawn ten thousand instantly**, and they'll all queue on `acquire()`. `acquire_timeout` turns that from an unbounded hang into a fast error, which is what you want: a request that fails in 3 seconds is better than one that hangs for 300.

`PgPool` is internally `Arc`; clone it freely, create exactly one.

## Migrations

```bash
sqlx migrate add create_users        # creates migrations/<timestamp>_create_users.sql
sqlx migrate run
sqlx migrate revert
```

```rust
sqlx::migrate!("./migrations").run(&pool).await?;    // embedded in the binary
```

`sqlx::migrate!` compiles the migration files **into the binary**, so deployment is one artefact with no separate migration files to ship. Convenient, and it interacts badly with multiple replicas starting at once — sqlx takes an advisory lock, so it's safe, but a failed migration inside app startup is harder to diagnose than a failed deploy step.

**Prefer running migrations as a separate step** in your pipeline. → [[devops/06-ci-cd/09-cd-and-deployment|CD and Deployment]]

## The alternatives

| | Approach | When |
|---|---|---|
| **sqlx** | raw SQL, compile-time checked | the default. You write SQL and get type safety |
| **SeaORM** | full async ORM | you want an ORM: entities, relations, a query builder |
| **Diesel** | sync ORM + DSL | mature, excellent type safety, **synchronous** — needs `spawn_blocking` |
| **tokio-postgres** | low-level Postgres driver | maximum control, `COPY`, LISTEN/NOTIFY |
| **cornucopia** | codegen from SQL | like Go's sqlc; generates typed functions |

**Diesel's sync-ness is the practical problem.** In an async service every query needs `spawn_blocking` or `deadpool-diesel`, which adds a thread hop per query and undercuts the reason you chose async. Diesel's type safety is arguably better than sqlx's; the integration cost is real.

**SeaORM** is the closest thing to a conventional ORM and it's fine. The usual reservations apply: generated SQL you didn't write, easy N+1 queries, and a query builder that's more verbose than the SQL it produces.

The Rust community leans the same way [[languages/02-go/README|Go's]] does — **SQL is already a good query language, and sqlx gives you type safety without an abstraction layer.** That combination is hard to argue with.

## Mapping errors

```rust
impl From<sqlx::Error> for AppError {
    fn from(e: sqlx::Error) -> Self {
        match e {
            sqlx::Error::RowNotFound => AppError::NotFound,
            sqlx::Error::Database(ref db) if db.code().as_deref() == Some("23505") =>
                AppError::Conflict("already exists".into()),      // unique violation
            other => AppError::Internal(other.into()),
        }
    }
}
```

Postgres SQLSTATE codes are how you distinguish a unique-constraint violation from a real failure — `23505` unique, `23503` foreign key, `40001` serialisation failure (retry this one), `40P01` deadlock.

Catching `23505` and returning 409 instead of 500 is the difference between "the user sees a sensible message" and "you get paged". → [[backend/frameworks/rust/02-extractors-and-responses|Extractors and Responses]] for how `AppError` becomes a response.

## Redis and caching

```rust
let client = redis::Client::open("redis://127.0.0.1/")?;
let mut conn = client.get_multiplexed_async_connection().await?;

let _: () = conn.set_ex("user:1", json, 3600).await?;
let cached: Option<String> = conn.get("user:1").await?;
```

`get_multiplexed_async_connection` pipelines many logical requests over one TCP connection — the right default for a server. `deadpool-redis` if you want a pool.

Cache-aside, with the usual caveat:

```rust
async fn get_user(&self, id: u64) -> Result<User> {
    if let Some(u) = self.cache.get(id).await? { return Ok(u); }
    let user = self.db_get(id).await?;
    self.cache.set(id, &user).await.ok();       // cache failure must NOT fail the request
    Ok(user)
}
```

**A cache write failure should never fail the request.** `.ok()` discards it deliberately — the cache is an optimisation, not a source of truth. → [[architecture/02-building-blocks/02-caching|Caching]]

## Testing

```rust
#[sqlx::test]
async fn creates_user(pool: PgPool) {
    let store = UserStore::new(pool);
    let user = store.create("k@example.com").await.unwrap();
    assert_eq!(user.email, "k@example.com");
}
```

`#[sqlx::test]` gives each test **its own database**, runs migrations, and drops it afterwards. Tests are isolated and can run in parallel with no cross-contamination — the best database-testing ergonomics of the four stacks here.

Combined with `testcontainers` for the Postgres instance itself, integration tests need no local setup at all.

---

## Related
- [[backend/frameworks/rust/03-state-and-shared-data|State and Shared Data]] — the pool as state
- [[backend/frameworks/rust/04-async-pitfalls|Async Pitfalls]] — pool exhaustion and unbounded spawning
- [[backend/04-data-and-persistence/README|Data and Persistence]] — the concepts
- [[databases/sql-reference|SQL Reference]]
- [[backend/frameworks/rust/README|Rust backends]]
