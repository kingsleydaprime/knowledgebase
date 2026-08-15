# Database Access

**[Intermediate]** — `database/sql`, why Go's ORM story is deliberately weak, and the connection-pool settings that decide whether your service survives load.

## `database/sql`

Go ships a database-agnostic interface; you add a driver.

```go
import (
    "database/sql"
    _ "github.com/jackc/pgx/v5/stdlib"      // blank import — registers the driver
)

db, err := sql.Open("pgx", dsn)
if err != nil { return fmt.Errorf("open: %w", err) }
defer db.Close()

if err := db.PingContext(ctx); err != nil {   // Open does NOT connect
    return fmt.Errorf("ping: %w", err)
}
```

**`sql.Open` doesn't connect.** It validates the DSN and returns a pool. The first real connection happens on first use, so without an explicit `Ping` a misconfigured database URL surfaces as a failed request rather than a failed startup.

**`*sql.DB` is a pool, not a connection.** It's safe for concurrent use, and you create exactly one for the process lifetime. Creating one per request is a real and common mistake — it defeats pooling entirely.

## The pool settings

The most operationally important five lines in a Go service:

```go
db.SetMaxOpenConns(25)                      // total connections; 0 = unlimited (DANGEROUS)
db.SetMaxIdleConns(25)                      // keep idle; default 2
db.SetConnMaxLifetime(5 * time.Minute)      // recycle — respects DB-side timeouts and failover
db.SetConnMaxIdleTime(1 * time.Minute)
```

Why each matters:

**`MaxOpenConns` defaults to unlimited.** Under load, Go's cheap goroutines will happily open ten thousand connections and take the database down. Postgres's default `max_connections` is 100 *total*, so a few unbounded replicas exhaust it. **Always set this.**

The sizing rule: `MaxOpenConns × replicas` must stay under the database's limit, with headroom. More connections than the database has cores rarely helps — queueing in your app is cheaper than thrashing in the database, and a pgbouncer in front changes the arithmetic entirely.

**`MaxIdleConns` defaults to 2.** If it's below `MaxOpenConns`, connections are closed and reopened constantly under bursty load. Set them equal.

**`ConnMaxLifetime`** matters for failover and for databases that close idle connections server-side. Without it you'll see "unexpected EOF" after a failover, because the pool hands out connections to a database that's gone.

When the pool is exhausted, `QueryContext` **blocks** until a connection frees or the context is cancelled — which is why passing a request-scoped context matters. → [[languages/02-go/08-context|Context]]

## Querying

```go
var u User
err := db.QueryRowContext(ctx,
    `SELECT id, email, created_at FROM users WHERE id = $1`, id,
).Scan(&u.ID, &u.Email, &u.CreatedAt)

if errors.Is(err, sql.ErrNoRows) {
    return nil, ErrNotFound                     // not an error condition; map it
}
if err != nil {
    return nil, fmt.Errorf("query user: %w", err)
}
```

```go
rows, err := db.QueryContext(ctx, `SELECT id, email FROM users WHERE active = $1`, true)
if err != nil { return nil, fmt.Errorf("query users: %w", err) }
defer rows.Close()                              // MANDATORY — leaks a connection otherwise

var users []User
for rows.Next() {
    var u User
    if err := rows.Scan(&u.ID, &u.Email); err != nil {
        return nil, fmt.Errorf("scan: %w", err)
    }
    users = append(users, u)
}
if err := rows.Err(); err != nil {              // CHECK THIS — the loop hides errors
    return nil, fmt.Errorf("iterate: %w", err)
}
```

Three things that leak or lie:

**`defer rows.Close()`** — an unclosed `Rows` holds its connection until GC, and the pool starves.

**`rows.Err()`** — `rows.Next()` returns `false` both for "done" and for "an error occurred". Without checking `Err()` you silently truncate a result set on a network blip.

**`sql.ErrNoRows`** — always `errors.Is`, never `==`, since callers wrap.

**`ExecContext` for writes:**

```go
res, err := db.ExecContext(ctx, `UPDATE users SET email = $1 WHERE id = $2`, email, id)
n, _ := res.RowsAffected()
if n == 0 { return ErrNotFound }
```

`RowsAffected` is how you distinguish "updated" from "no such row" — the update itself doesn't error.

## Parameters, always

```go
db.QueryContext(ctx, "SELECT * FROM users WHERE email = $1", email)          // safe
db.QueryContext(ctx, "SELECT * FROM users WHERE email = '"+email+"'")        // SQL INJECTION
```

Placeholders are driver-specific: `$1` for Postgres, `?` for MySQL and SQLite. They are sent separately from the query text, so the value can never be parsed as SQL.

The one thing parameters **cannot** be is an identifier — table names, column names, `ORDER BY` direction. Those need an allowlist:

```go
var allowedSort = map[string]string{"name": "name", "created": "created_at"}
col, ok := allowedSort[r.URL.Query().Get("sort")]
if !ok { col = "created_at" }
query := fmt.Sprintf("SELECT ... ORDER BY %s", col)      // safe: col came from the map
```

→ [[cybersecurity/04-web-security/README|Web Security]]

## Transactions

```go
func (s *Store) Transfer(ctx context.Context, from, to string, amount int64) error {
    tx, err := s.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelSerializable})
    if err != nil { return fmt.Errorf("begin: %w", err) }
    defer tx.Rollback()                     // no-op after Commit; the safety net

    if _, err := tx.ExecContext(ctx,
        `UPDATE accounts SET balance = balance - $1 WHERE id = $2`, amount, from); err != nil {
        return fmt.Errorf("debit: %w", err)
    }
    if _, err := tx.ExecContext(ctx,
        `UPDATE accounts SET balance = balance + $1 WHERE id = $2`, amount, to); err != nil {
        return fmt.Errorf("credit: %w", err)
    }
    return tx.Commit()
}
```

**`defer tx.Rollback()` immediately after `BeginTx`** is the idiom. Rollback after a successful commit returns `sql.ErrTxDone`, which is harmless — so this one line covers every error path including panics, without a `goto cleanup`-style ladder.

**A transaction holds a connection for its whole life.** Long transactions starve the pool; never do an HTTP call inside one.

## The ORM question

Go's ecosystem is unusually sceptical of ORMs, and the options reflect that:

| | Approach | Character |
|---|---|---|
| **`database/sql`** | raw SQL, manual scan | verbose; zero magic; always available |
| **`sqlx`** | thin extension | adds `StructScan`, named params, `Select`/`Get` into slices |
| **`sqlc`** | **codegen from SQL** | you write SQL, it generates typed Go. No runtime layer |
| **`pgx`** | Postgres-native | skips `database/sql`; faster, `COPY`, LISTEN/NOTIFY, real types |
| **GORM** | full ORM | associations, migrations, hooks — and reflection, and surprising SQL |
| **ent** | schema-as-code | graph-oriented, generates a typed client. Heavier concept |

**`sqlc` is the one worth knowing about**, because it inverts the usual trade:

```sql
-- query.sql
-- name: GetUser :one
SELECT id, email, created_at FROM users WHERE id = $1;
```

```go
// generated — typed, no reflection, no runtime cost
user, err := queries.GetUser(ctx, id)
```

You write real SQL; it generates the structs and the scan code by checking your queries against the actual schema at build time. A typo'd column is a **compile error**, not a runtime one. That's genuinely better than both raw `Scan` and an ORM.

**On GORM:** it works, it's popular, and the reservations are real — it generates SQL you didn't write and can't easily predict, N+1 queries are easy to create and hard to see, and its error handling doesn't fit Go's idioms. If your team wants an ORM it's the default; know what it costs.

The Go position, stated plainly: **SQL is already a good language for querying, and the abstraction usually costs more than it saves.** Prefer `sqlc`, or `sqlx` for a thin layer, and reach for a full ORM only when the team genuinely wants one. → [[databases/sql-reference|SQL reference]]

## Migrations

```bash
migrate create -ext sql -dir db/migrations -seq create_users
migrate -database "$DATABASE_URL" -path db/migrations up
```

`golang-migrate`, `goose`, or `atlas`. All do versioned up/down SQL files.

**Run migrations as a separate step, not at application startup.** Multiple replicas starting simultaneously will race, and a failed migration inside your app's boot path is much harder to reason about than a failed deploy step. → [[devops/06-ci-cd/09-cd-and-deployment|CD and Deployment]]

## Health checks

```go
func (s *Server) handleReady(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
    defer cancel()
    if err := s.db.PingContext(ctx); err != nil {
        http.Error(w, "database unavailable", http.StatusServiceUnavailable)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```

**Liveness must not check dependencies** — if it does, a database blip makes Kubernetes restart every healthy pod, turning a partial outage into a total one. Liveness answers "is this process wedged"; readiness answers "should I get traffic". → [[devops/05-orchestration/README|Orchestration]]

---

## Related
- [[backend/frameworks/go/04-structuring-a-go-service|Structuring a Go Service]] — where the store fits
- [[backend/04-data-and-persistence/README|Data and Persistence]] — the concepts
- [[databases/sql-reference|SQL Reference]] · [[databases/database-design-reference|Database Design]]
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — pooling and connection limits
- [[backend/frameworks/go/README|Go backends]]
