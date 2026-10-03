# Transactions and ACID in Other Languages

**[Intermediate → Advanced]** — A companion to [[databases/08-transactions-and-acid/index|transactions and ACID]], which makes the anomalies happen on a real PostgreSQL with two sessions stepped one statement at a time, and fixes them. This page does the same in TypeScript, Go, Java, Rust and C#: the lost update, Repeatable Read's refusal, `FOR UPDATE`'s wait, and write skew under Serializable with a retry that keeps the rule. The SQL is identical everywhere. What changes is the code around it: how each driver tells you *which* failure happened, and how you write the retry loop that Repeatable Read and Serializable require.

## Before you start

You can already:

- Name the anomalies and fix a lost update four ways, and say why a serialization failure means "run it again" → [[databases/08-transactions-and-acid/index|the main lesson]].
- Connect your language's PostgreSQL driver to the throwaway database → [[databases/04-b-trees-and-indexes/in-other-languages|B-trees and indexes in other languages]].

After this lesson you will be able to:

1. Tell a serialization failure, a deadlock and a lock timeout apart in your language, by their SQLSTATE codes.
2. Write a retry loop that reruns the *whole* transaction, only for errors where that's the right response.
3. Pass values as query parameters in your driver, with the right placeholder.

## The kid version

A school has three different "try again" slips. One means "someone changed this while you were working: start the task again". One means "you and another pupil were each waiting for the other: one of you start again". One means "you waited too long for a turn". Teachers in five schools all use the same three slips, but each school files them differently: by number, by colour, by name. You have to know where your school keeps the number.

**Where the analogy stops working.** A pupil reads the slip. A program has to dig the code out of an error object, and each driver puts it somewhere different. Retrying on the wrong error, such as a constraint violation, repeats the same mistake forever.

## 1. The tools, by ecosystem

| Language | Where the SQLSTATE is | Placeholder | Transaction API (besides SQL `BEGIN`) |
|---|---|---|---|
| Python (psycopg) | an exception **class** per code: `errors.SerializationFailure` | `%s` | `with conn.transaction():` |
| TypeScript (node-postgres) | **`err.code`**, a string | `$1` | none: send `BEGIN`/`COMMIT` |
| Go (pgx) | **`*pgconn.PgError`**'s `Code`, found with `errors.As` | `$1` | `conn.Begin(ctx)` → `tx.Commit` / `tx.Rollback` |
| Java (JDBC) | **`SQLException.getSQLState()`** | `?` | `setAutoCommit(false)` + `commit()` / `rollback()` |
| Rust (`postgres`) | **`err.code()`**, an `Option<&SqlState>` with named constants | `$1` | `client.transaction()?` → `commit()`; dropped = rolled back |
| C# (Npgsql) | **`PostgresException.SqlState`**, with constants in `PostgresErrorCodes` | `$1` (positional) or `@name` | `BeginTransactionAsync()` |

The three codes every lab checks:

| SQLSTATE | Meaning | Retry the transaction? |
|---|---|---|
| `40001` | serialization failure | **yes** |
| `40P01` | deadlock detected (you were the victim) | **yes** |
| `55P03` | lock not available (`lock_timeout` passed) | sometimes: it's a policy choice |

The labs send `BEGIN` and `COMMIT` as SQL, so each step is exactly what you'd type into `psql`. In application code, use the driver's transaction API from the table: it can't forget the `ROLLBACK` on an error path. C and C++ (libpq) read the code with `PQresultErrorField(result, PG_DIAG_SQLSTATE)`; they have no lab here.

## 2. What changes between languages

### Finding out which failure happened

- **Python** maps each SQLSTATE to its own exception class, so `except errors.SerializationFailure:` reads like the lesson.
- **TypeScript** gives a plain error with a `code` string; compare with `"40001"`.
- **Go** wraps errors, so `err.(*pgconn.PgError)` fails on a wrapped one. `errors.As` searches the whole chain, and the labs' `Code(err)` helper returns `""` for anything that isn't from PostgreSQL.
- **Java** puts the code on every `SQLException` as `getSQLState()`.
- **Rust** gives `Option<&SqlState>`, compared with constants like `SqlState::T_R_SERIALIZATION_FAILURE`. The `T_R_` prefix comes from the SQL standard's class name, "transaction rollback".
- **C#** throws `PostgresException`, whose `SqlState` compares with `PostgresErrorCodes.SerializationFailure`. An exception filter (`catch … when (…)`) retries only those, letting everything else propagate.

### The retry loop

Every lab's retry loop has the same shape, and the same three rules:

1. **Rerun the whole transaction**, from `BEGIN`, so its reads see the new state. Retrying only the failed statement inside a dead transaction can't work.
2. **Retry only `40001` and `40P01`.** A constraint violation or a syntax error will fail the same way every time.
3. **Back off and stop.** Wait a little longer each time, and give up after a few attempts.

The labs pass the transaction as a function: a closure in TypeScript, Go, Rust and C#, and a functional interface in Java. On failure inside it, they `ROLLBACK` before rethrowing, so the connection is clean for the next attempt.

### Parameters, not string building

Every statement with a value uses a parameter: `$1` in node-postgres, pgx, the Rust crate and Npgsql, and `?` in JDBC. The value travels separately from the SQL text, so it can't change the statement's meaning. The first draft of the Java lab concatenated a doctor's name into the SQL; that's the SQL-injection pattern, and it was rewritten with `PreparedStatement`.

### Types are stricter in some drivers

Rust's crate won't read an `int` column as `i64`: `get` panics on the wrong type, and `try_get` returns an error. So the Rust helper tries `bigint` and falls back to `int`. node-postgres hands `count(*)`, a `bigint`, back as a string, so the TypeScript lab casts it in SQL (`count(*)::int`). Java's `getLong` and C#'s `Convert.ToInt64` widen without complaint.

## 3. The same results, in every language

| Scenario | Expected in every language |
|---|---|
| two Read Committed read-modify-writes | final balance 80 (a lost update) |
| the same at Repeatable Read | the second `UPDATE` fails with `40001`; balance 90 |
| a second `SELECT … FOR UPDATE` with a 100 ms `lock_timeout` | fails with `55P03` |
| both doctors go off call at Serializable | the second `COMMIT` fails with `40001` |
| the second doctor's transaction, retried | sees 1 on call and changes nothing: bob stays |

## Terms used in this lesson

1. **SQLSTATE**: This is a five-character error code from the SQL standard, which PostgreSQL attaches to every error. The first two characters are the class: `40` means "transaction rollback".
2. **Exception filter**: In C#, this is a `when` clause on a `catch` that decides whether that `catch` handles an exception at all.
3. **Error chain**: In Go, this is an error wrapped inside other errors with `%w`, which `errors.As` and `errors.Is` search.
4. **Query parameter**: This is a value sent separately from the SQL text, referred to in the statement by a placeholder such as `$1` or `?`.

## 4. TypeScript

`withRetry` is a generic async function. `err.code` is compared with the SQLSTATE strings. After a failed `COMMIT` the transaction is already over, so the lab's `ROLLBACK` there ignores errors. Tests run one at a time (`--test-concurrency=1`), because each recreates the tables.

```ts
// The anomalies and their fixes, through node-postgres. Two clients are stepped one statement at a time.
// Run through ../shared/with-postgres.sh.
import { afterEach, beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import pg from "pg";

// PostgreSQL's error codes (SQLSTATE) for the outcomes concurrency makes normal. node-postgres puts it on err.code.
const SERIALIZATION_FAILURE = "40001";
const DEADLOCK_DETECTED = "40P01";
const LOCK_NOT_AVAILABLE = "55P03";

let a: pg.Client;
let b: pg.Client;

async function value(client: pg.Client, sql: string, params: unknown[] = []): Promise<any> {
  const { rows } = await client.query(sql, params);
  return Object.values(rows[0])[0];
}

/** Runs `work` again while PostgreSQL says the transaction should be retried, backing off a little more each time. */
export async function withRetry<T>(work: () => Promise<T>, attempts = 5): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    try {
      return await work();
    } catch (err: any) {
      if (attempt === attempts || ![SERIALIZATION_FAILURE, DEADLOCK_DETECTED].includes(err.code)) throw err;
      await new Promise((resolve) => setTimeout(resolve, 10 * 2 ** attempt));
    }
  }
}

beforeEach(async () => {
  [a, b] = [new pg.Client(), new pg.Client()];
  await Promise.all([a.connect(), b.connect()]);
  await a.query(`
    DROP TABLE IF EXISTS accounts, doctors;
    CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0), version int NOT NULL DEFAULT 1);
    INSERT INTO accounts (id, balance) VALUES (1, 100), (2, 50);
    CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
    INSERT INTO doctors VALUES ('alice', true), ('bob', true);
  `); // no VACUUM here, so one multi-statement call is fine
});

afterEach(() => Promise.all([a.end(), b.end()]));

const balance = () => value(a, "SELECT balance FROM accounts WHERE id = 1");

test("a lost update at Read Committed", async () => {
  await a.query("BEGIN");
  await b.query("BEGIN");
  const [seenA, seenB] = [await balance(), await value(b, "SELECT balance FROM accounts WHERE id = 1")];
  await a.query("UPDATE accounts SET balance = $1 WHERE id = 1", [seenA - 10]);
  await a.query("COMMIT");
  await b.query("UPDATE accounts SET balance = $1 WHERE id = 1", [seenB - 20]);
  await b.query("COMMIT");
  assert.equal(await balance(), 80);
});

test("Repeatable Read refuses the second write with SQLSTATE 40001", async () => {
  await a.query("BEGIN ISOLATION LEVEL REPEATABLE READ");
  await b.query("BEGIN ISOLATION LEVEL REPEATABLE READ");
  const seenB = await value(b, "SELECT balance FROM accounts WHERE id = 1");
  await a.query("UPDATE accounts SET balance = balance - 10 WHERE id = 1");
  await a.query("COMMIT");
  await assert.rejects(b.query("UPDATE accounts SET balance = $1 WHERE id = 1", [seenB - 20]), (err: any) => err.code === SERIALIZATION_FAILURE);
  await b.query("ROLLBACK");
  assert.equal(await balance(), 90);
});

test("FOR UPDATE makes the second reader wait: 55P03 under a short lock_timeout", async () => {
  await a.query("BEGIN");
  await a.query("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE");
  await b.query("BEGIN");
  await b.query("SET LOCAL lock_timeout = '100ms'");
  await assert.rejects(b.query("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE"), (err: any) => err.code === LOCK_NOT_AVAILABLE);
  await b.query("ROLLBACK");
  await a.query("COMMIT");
});

test("write skew: Serializable aborts one, and the retried transaction keeps the rule", async () => {
  const goOffCall = async (client: pg.Client, name: string) => {
    await client.query("BEGIN ISOLATION LEVEL SERIALIZABLE");
    if ((await value(client, "SELECT count(*)::int FROM doctors WHERE on_call")) >= 2) {
      await client.query("UPDATE doctors SET on_call = false WHERE name = $1", [name]);
    }
  };
  await goOffCall(a, "alice");
  await goOffCall(b, "bob");
  await a.query("COMMIT");
  await assert.rejects(b.query("COMMIT"), (err: any) => err.code === SERIALIZATION_FAILURE);
  await b.query("ROLLBACK").catch(() => {}); // after a failed COMMIT the transaction is already over
  await withRetry(async () => {
    try {
      await goOffCall(b, "bob");
      await b.query("COMMIT");
    } catch (err) {
      await b.query("ROLLBACK");
      throw err;
    }
  });
  assert.equal(await value(a, "SELECT string_agg(name, ',') FROM doctors WHERE on_call"), "bob");
});
```

**Lab:** [`labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/08-transactions-and-acid/labs/typescript). `python3 labs/run.py transactions-and-acid/typescript`.

## 5. Go

`Code` uses `errors.As`, and `WithRetry` takes a `context.Context`, so a cancelled request stops retrying. The tests wrap each connection in a small `session` type with `exec`, `must` and `int`, which keeps the stepped scenarios readable.

```go
// Package isolation: the retry loop every Repeatable Read or Serializable transaction needs, written with pgx.
package isolation

import (
	"context"
	"errors"
	"time"

	"github.com/jackc/pgx/v5/pgconn"
)

// PostgreSQL's error codes (SQLSTATE) for the outcomes concurrency makes normal.
const (
	SerializationFailure = "40001"
	DeadlockDetected     = "40P01"
	LockNotAvailable     = "55P03"
)

// Code returns the SQLSTATE of a PostgreSQL error, however deeply it's wrapped, or "" for any other error.
func Code(err error) string {
	var pgErr *pgconn.PgError
	if errors.As(err, &pgErr) {
		return pgErr.Code
	}
	return ""
}

// WithRetry runs work again while PostgreSQL says the transaction should be retried, backing off each time.
// work must run the whole transaction, from BEGIN to COMMIT, and roll back if it fails.
func WithRetry(ctx context.Context, attempts int, work func() error) error {
	for attempt := 1; ; attempt++ {
		err := work()
		if err == nil || attempt == attempts || (Code(err) != SerializationFailure && Code(err) != DeadlockDetected) {
			return err
		}
		select {
		case <-time.After(time.Duration(10<<attempt) * time.Millisecond):
		case <-ctx.Done():
			return ctx.Err()
		}
	}
}
```

```go
package isolation

// The anomalies and their fixes through pgx, with two connections stepped one statement at a time.
// Run through ../shared/with-postgres.sh; without PGHOST these tests skip.

import (
	"context"
	"os"
	"testing"

	"github.com/jackc/pgx/v5"
)

type session struct {
	t    *testing.T
	ctx  context.Context
	conn *pgx.Conn
}

func (s session) exec(sql string, args ...any) error {
	_, err := s.conn.Exec(s.ctx, sql, args...)
	return err
}

func (s session) must(sql string, args ...any) {
	s.t.Helper()
	if err := s.exec(sql, args...); err != nil {
		s.t.Fatal(sql, err)
	}
}

func (s session) int(sql string, args ...any) int {
	s.t.Helper()
	var n int
	if err := s.conn.QueryRow(s.ctx, sql, args...).Scan(&n); err != nil {
		s.t.Fatal(sql, err)
	}
	return n
}

func sessions(t *testing.T) (session, session) {
	t.Helper()
	if os.Getenv("PGHOST") == "" {
		t.Skip("no PostgreSQL: run through ../shared/with-postgres.sh")
	}
	ctx := context.Background()
	open := func() session {
		conn, err := pgx.Connect(ctx, "")
		if err != nil {
			t.Fatal(err)
		}
		t.Cleanup(func() { conn.Close(ctx) })
		return session{t, ctx, conn}
	}
	a, b := open(), open()
	a.must(`DROP TABLE IF EXISTS accounts, doctors;
		CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0));
		INSERT INTO accounts VALUES (1, 100), (2, 50);
		CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
		INSERT INTO doctors VALUES ('alice', true), ('bob', true)`)
	return a, b
}

const balance = "SELECT balance FROM accounts WHERE id = 1"

func TestALostUpdateAtReadCommitted(t *testing.T) {
	a, b := sessions(t)
	a.must("BEGIN")
	b.must("BEGIN")
	seenA, seenB := a.int(balance), b.int(balance)
	a.must("UPDATE accounts SET balance = $1 WHERE id = 1", seenA-10)
	a.must("COMMIT")
	b.must("UPDATE accounts SET balance = $1 WHERE id = 1", seenB-20)
	b.must("COMMIT")
	if got := a.int(balance); got != 80 {
		t.Fatal(got)
	}
}

func TestRepeatableReadRefusesTheSecondWrite(t *testing.T) {
	a, b := sessions(t)
	a.must("BEGIN ISOLATION LEVEL REPEATABLE READ")
	b.must("BEGIN ISOLATION LEVEL REPEATABLE READ")
	seenB := b.int(balance)
	a.must("UPDATE accounts SET balance = balance - 10 WHERE id = 1")
	a.must("COMMIT")
	if err := b.exec("UPDATE accounts SET balance = $1 WHERE id = 1", seenB-20); Code(err) != SerializationFailure {
		t.Fatal(err)
	}
	b.must("ROLLBACK")
}

func TestForUpdateMakesTheSecondReaderWait(t *testing.T) {
	a, b := sessions(t)
	a.must("BEGIN")
	a.must("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")
	b.must("BEGIN")
	b.must("SET LOCAL lock_timeout = '100ms'")
	if err := b.exec("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE"); Code(err) != LockNotAvailable {
		t.Fatal(err)
	}
	b.must("ROLLBACK")
	a.must("COMMIT")
}

func TestWriteSkewSerializableAndRetry(t *testing.T) {
	a, b := sessions(t)
	goOffCall := func(s session, name string) error {
		if err := s.exec("BEGIN ISOLATION LEVEL SERIALIZABLE"); err != nil {
			return err
		}
		if s.int("SELECT count(*) FROM doctors WHERE on_call") >= 2 {
			return s.exec("UPDATE doctors SET on_call = false WHERE name = $1", name)
		}
		return nil
	}
	goOffCall(a, "alice")
	goOffCall(b, "bob")
	a.must("COMMIT")
	if err := b.exec("COMMIT"); Code(err) != SerializationFailure {
		t.Fatal(err)
	}
	err := WithRetry(b.ctx, 5, func() error {
		if err := goOffCall(b, "bob"); err != nil {
			b.exec("ROLLBACK")
			return err
		}
		if err := b.exec("COMMIT"); err != nil {
			b.exec("ROLLBACK")
			return err
		}
		return nil
	})
	var name string
	a.conn.QueryRow(a.ctx, "SELECT string_agg(name, ',') FROM doctors WHERE on_call").Scan(&name)
	if err != nil || name != "bob" {
		t.Fatal(err, name)
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/08-transactions-and-acid/labs/go). `python3 labs/run.py transactions-and-acid/go`.

## 6. Java

`failure` runs an action and returns its SQLSTATE or `null`. `withRetry` takes an `Action`, a functional interface whose `run` may throw `SQLException`, which `Runnable` can't. Statements with values use the `run(c, sql, params…)` overload, which binds them with `PreparedStatement.setObject`.

```java
package isolation;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Set;

/** A session stepped one statement at a time, and the retry loop, over JDBC. */
public final class Isolation {
    private Isolation() {}

    // PostgreSQL's error codes (SQLSTATE) for the outcomes concurrency makes normal. JDBC exposes them as getSQLState().
    public static final String SERIALIZATION_FAILURE = "40001";
    public static final String DEADLOCK_DETECTED = "40P01";
    public static final String LOCK_NOT_AVAILABLE = "55P03";
    private static final Set<String> RETRYABLE = Set.of(SERIALIZATION_FAILURE, DEADLOCK_DETECTED);

    public static Connection connect() throws SQLException {
        // Auto-commit is JDBC's default: with it on, the explicit BEGIN and COMMIT in the checks are the only ones.
        return DriverManager.getConnection("jdbc:postgresql://127.0.0.1:" + System.getenv("PGPORT") + "/postgres?user=postgres");
    }

    public static void run(Connection c, String sql) throws SQLException {
        try (Statement s = c.createStatement()) {
            s.execute(sql);
        }
    }

    /** A statement with parameters: values travel separately from the SQL, so they can't change its meaning. */
    public static void run(Connection c, String sql, Object... params) throws SQLException {
        try (var s = c.prepareStatement(sql)) {
            for (int i = 0; i < params.length; i++) s.setObject(i + 1, params[i]);
            s.execute();
        }
    }

    public static long number(Connection c, String sql) throws SQLException {
        try (Statement s = c.createStatement(); ResultSet r = s.executeQuery(sql)) {
            r.next();
            return r.getLong(1);
        }
    }

    /** The SQLSTATE an action fails with, or null if it succeeds. */
    public static String failure(Action action) {
        try {
            action.run();
            return null;
        } catch (SQLException e) {
            return e.getSQLState();
        }
    }

    @FunctionalInterface
    public interface Action {
        void run() throws SQLException;
    }

    /** Runs work again while PostgreSQL says the transaction should be retried, backing off each time. */
    public static void withRetry(int attempts, Action work) throws SQLException, InterruptedException {
        for (int attempt = 1; ; attempt++) {
            try {
                work.run();
                return;
            } catch (SQLException e) {
                if (attempt == attempts || !RETRYABLE.contains(e.getSQLState())) throw e;
                Thread.sleep(10L << attempt);
            }
        }
    }
}
```

```java
package isolation;

import static isolation.Isolation.LOCK_NOT_AVAILABLE;
import static isolation.Isolation.SERIALIZATION_FAILURE;
import static isolation.Isolation.failure;
import static isolation.Isolation.number;
import static isolation.Isolation.run;

import java.sql.Connection;
import java.sql.SQLException;

/** The anomalies and their fixes through JDBC. Run through ../shared/with-postgres.sh, with -ea. */
public final class IsolationCheck {
    private IsolationCheck() {}

    private static final String BALANCE = "SELECT balance FROM accounts WHERE id = 1";

    private static void reset(Connection a) throws SQLException {
        run(a, """
            DROP TABLE IF EXISTS accounts, doctors;
            CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0));
            INSERT INTO accounts VALUES (1, 100), (2, 50);
            CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
            INSERT INTO doctors VALUES ('alice', true), ('bob', true)""");
    }

    private static void goOffCall(Connection c, String name) throws SQLException {
        run(c, "BEGIN ISOLATION LEVEL SERIALIZABLE");
        if (number(c, "SELECT count(*) FROM doctors WHERE on_call") >= 2) run(c, "UPDATE doctors SET on_call = false WHERE name = ?", name);
    }

    public static void main(String[] args) throws Exception {
        try (Connection a = Isolation.connect(); Connection b = Isolation.connect()) {
            reset(a); // a lost update at Read Committed
            run(a, "BEGIN");
            run(b, "BEGIN");
            long seenA = number(a, BALANCE);
            long seenB = number(b, BALANCE);
            run(a, "UPDATE accounts SET balance = ? WHERE id = 1", seenA - 10);
            run(a, "COMMIT");
            run(b, "UPDATE accounts SET balance = ? WHERE id = 1", seenB - 20);
            run(b, "COMMIT");
            assert number(a, BALANCE) == 80;

            reset(a); // Repeatable Read refuses the second write
            run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
            run(b, "BEGIN ISOLATION LEVEL REPEATABLE READ");
            long seen = number(b, BALANCE);
            run(a, "UPDATE accounts SET balance = balance - 10 WHERE id = 1");
            run(a, "COMMIT");
            assert SERIALIZATION_FAILURE.equals(failure(() -> run(b, "UPDATE accounts SET balance = ? WHERE id = 1", seen - 20)));
            run(b, "ROLLBACK");

            reset(a); // FOR UPDATE makes the second reader wait
            run(a, "BEGIN");
            run(a, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE");
            run(b, "BEGIN");
            run(b, "SET LOCAL lock_timeout = '100ms'");
            assert LOCK_NOT_AVAILABLE.equals(failure(() -> run(b, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")));
            run(b, "ROLLBACK");
            run(a, "COMMIT");

            reset(a); // write skew: Serializable aborts one, and the retry keeps the rule
            goOffCall(a, "alice");
            goOffCall(b, "bob");
            run(a, "COMMIT");
            assert SERIALIZATION_FAILURE.equals(failure(() -> run(b, "COMMIT")));
            Isolation.withRetry(5, () -> {
                try {
                    goOffCall(b, "bob");
                    run(b, "COMMIT");
                } catch (SQLException e) {
                    run(b, "ROLLBACK");
                    throw e;
                }
            });
            assert number(a, "SELECT count(*) FROM doctors WHERE on_call AND name = 'bob'") == 1;
            assert number(a, "SELECT count(*) FROM doctors WHERE on_call") == 1;
        }
        System.out.println("all isolation checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/08-transactions-and-acid/labs/java). `python3 labs/run.py transactions-and-acid/java`.

## 7. Rust

`code` works on any `Result` whose error is a `postgres::Error`. `with_retry` takes an `FnMut` closure that borrows the client mutably on each attempt, and uses `matches!` with a guard to test the code. `?` inside `go_off_call` returns the first database error straight to the retry loop.

```rust
//! Connecting to the throwaway database, and the retry loop every Repeatable Read or Serializable transaction needs.
use postgres::error::SqlState;
use postgres::{Client, Config, NoTls};
use std::time::Duration;

/// The crate doesn't read PG* variables itself, so the settings are passed in. A host starting with "/" is a socket.
pub fn connect() -> Client {
    let host = std::env::var("PGHOST").expect("run through ../shared/with-postgres.sh");
    let port = std::env::var("PGPORT")
        .expect("PGPORT")
        .parse()
        .expect("a port number");
    Config::new()
        .host(&host)
        .port(port)
        .user("postgres")
        .dbname("postgres")
        .connect(NoTls)
        .expect("connect")
}

/// The SQLSTATE a PostgreSQL error carries, if any: `SqlState` has a named constant for every code.
pub fn code(result: &Result<impl Sized, postgres::Error>) -> Option<&SqlState> {
    result.as_ref().err().and_then(postgres::Error::code)
}

/// Runs `work` again while PostgreSQL says the transaction should be retried, backing off each time.
pub fn with_retry<T>(
    attempts: u32,
    mut work: impl FnMut() -> Result<T, postgres::Error>,
) -> Result<T, postgres::Error> {
    for attempt in 1.. {
        let result = work();
        let retry = matches!(code(&result), Some(c) if *c == SqlState::T_R_SERIALIZATION_FAILURE || *c == SqlState::T_R_DEADLOCK_DETECTED);
        if !retry || attempt == attempts {
            return result;
        }
        std::thread::sleep(Duration::from_millis(10 << attempt));
    }
    unreachable!("the loop returns")
}
```

```rust
//! The anomalies and their fixes through the `postgres` crate, two clients stepped one statement at a time.
//! Run through ../shared/with-postgres.sh; without PGHOST, it does nothing.
use isolation::{code, connect, with_retry};
use postgres::Client;
use postgres::error::SqlState;

const BALANCE: &str = "SELECT balance FROM accounts WHERE id = 1";

fn int(c: &mut Client, sql: &str) -> i64 {
    let row = c.query_one(sql, &[]).unwrap();
    row.try_get::<_, i64>(0)
        .unwrap_or_else(|_| i64::from(row.get::<_, i32>(0))) // count(*) is bigint; balance is int
}

fn reset(a: &mut Client) {
    a.batch_execute(
        "DROP TABLE IF EXISTS accounts, doctors;
         CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0));
         INSERT INTO accounts VALUES (1, 100), (2, 50);
         CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
         INSERT INTO doctors VALUES ('alice', true), ('bob', true);",
    )
    .unwrap();
}

fn go_off_call(c: &mut Client, name: &str) -> Result<(), postgres::Error> {
    c.batch_execute("BEGIN ISOLATION LEVEL SERIALIZABLE")?;
    let on_call: i64 = c
        .query_one("SELECT count(*) FROM doctors WHERE on_call", &[])?
        .get(0);
    if on_call >= 2 {
        c.execute(
            "UPDATE doctors SET on_call = false WHERE name = $1",
            &[&name],
        )?;
    }
    Ok(())
}

#[test]
fn isolation() {
    if std::env::var("PGHOST").is_err() {
        return;
    }
    let (mut a, mut b) = (connect(), connect());

    reset(&mut a); // a lost update at Read Committed
    a.batch_execute("BEGIN").unwrap();
    b.batch_execute("BEGIN").unwrap();
    let (seen_a, seen_b) = (int(&mut a, BALANCE) as i32, int(&mut b, BALANCE) as i32);
    a.execute(
        "UPDATE accounts SET balance = $1 WHERE id = 1",
        &[&(seen_a - 10)],
    )
    .unwrap();
    a.batch_execute("COMMIT").unwrap();
    b.execute(
        "UPDATE accounts SET balance = $1 WHERE id = 1",
        &[&(seen_b - 20)],
    )
    .unwrap();
    b.batch_execute("COMMIT").unwrap();
    assert_eq!(int(&mut a, BALANCE), 80);

    reset(&mut a); // Repeatable Read refuses the second write
    a.batch_execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        .unwrap();
    b.batch_execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        .unwrap();
    let seen = int(&mut b, BALANCE) as i32;
    a.batch_execute("UPDATE accounts SET balance = balance - 10 WHERE id = 1; COMMIT")
        .unwrap();
    let refused = b.execute(
        "UPDATE accounts SET balance = $1 WHERE id = 1",
        &[&(seen - 20)],
    );
    assert_eq!(code(&refused), Some(&SqlState::T_R_SERIALIZATION_FAILURE));
    b.batch_execute("ROLLBACK").unwrap();

    reset(&mut a); // FOR UPDATE makes the second reader wait
    a.batch_execute("BEGIN; SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")
        .unwrap();
    b.batch_execute("BEGIN; SET LOCAL lock_timeout = '100ms'")
        .unwrap();
    let waited = b.batch_execute("SELECT balance FROM accounts WHERE id = 1 FOR UPDATE");
    assert_eq!(code(&waited), Some(&SqlState::LOCK_NOT_AVAILABLE));
    b.batch_execute("ROLLBACK").unwrap();
    a.batch_execute("COMMIT").unwrap();

    reset(&mut a); // write skew: Serializable aborts one, and the retry keeps the rule
    go_off_call(&mut a, "alice").unwrap();
    go_off_call(&mut b, "bob").unwrap();
    a.batch_execute("COMMIT").unwrap();
    assert_eq!(
        code(&b.batch_execute("COMMIT")),
        Some(&SqlState::T_R_SERIALIZATION_FAILURE)
    );
    with_retry(5, || {
        let result = go_off_call(&mut b, "bob").and_then(|()| b.batch_execute("COMMIT"));
        if result.is_err() {
            b.batch_execute("ROLLBACK")?;
        }
        result
    })
    .unwrap();
    let on_call: String = a
        .query_one(
            "SELECT string_agg(name, ',') FROM doctors WHERE on_call",
            &[],
        )
        .unwrap()
        .get(0);
    assert_eq!(on_call, "bob");
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/08-transactions-and-acid/labs/rust). `python3 labs/run.py transactions-and-acid/rust`.

## 8. C#

`Failure` catches `PostgresException` and returns its `SqlState`. `WithRetry` uses an exception filter, so only serialization failures and deadlocks are caught and anything else propagates untouched. Parameters are positional `$1`, added in order. It runs in the .NET SDK container on the host's network.

```csharp
// The anomalies and their fixes through Npgsql, two connections stepped one statement at a time.
using Npgsql;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var connectionString = $"Host=127.0.0.1;Port={Environment.GetEnvironmentVariable("PGPORT")};Username=postgres;Database=postgres";
await using var a = new NpgsqlConnection(connectionString);
await using var b = new NpgsqlConnection(connectionString);
await a.OpenAsync();
await b.OpenAsync();

static async Task Run(NpgsqlConnection c, string sql, params object[] values)
{
    await using var command = new NpgsqlCommand(sql, c);
    foreach (var v in values) command.Parameters.Add(new NpgsqlParameter { Value = v }); // $1, $2, … in order
    await command.ExecuteNonQueryAsync();
}

static async Task<long> Number(NpgsqlConnection c, string sql)
{
    await using var command = new NpgsqlCommand(sql, c);
    return Convert.ToInt64(await command.ExecuteScalarAsync());
}

// The SQLSTATE an action fails with, or null. Npgsql names the codes in PostgresErrorCodes.
static async Task<string?> Failure(Func<Task> action)
{
    try
    {
        await action();
        return null;
    }
    catch (PostgresException e)
    {
        return e.SqlState;
    }
}

// Runs work again while PostgreSQL says the transaction should be retried, backing off each time.
static async Task WithRetry(int attempts, Func<Task> work)
{
    for (var attempt = 1; ; attempt++)
    {
        try
        {
            await work();
            return;
        }
        catch (PostgresException e) when (attempt < attempts && e.SqlState is PostgresErrorCodes.SerializationFailure or PostgresErrorCodes.DeadlockDetected)
        {
            await Task.Delay(10 << attempt);
        }
    }
}

const string Balance = "SELECT balance FROM accounts WHERE id = 1";
async Task Reset() => await Run(a, """
    DROP TABLE IF EXISTS accounts, doctors;
    CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0));
    INSERT INTO accounts VALUES (1, 100), (2, 50);
    CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
    INSERT INTO doctors VALUES ('alice', true), ('bob', true)
    """);

await Reset(); // a lost update at Read Committed
await Run(a, "BEGIN");
await Run(b, "BEGIN");
var (seenA, seenB) = (await Number(a, Balance), await Number(b, Balance));
await Run(a, "UPDATE accounts SET balance = $1 WHERE id = 1", (int)seenA - 10);
await Run(a, "COMMIT");
await Run(b, "UPDATE accounts SET balance = $1 WHERE id = 1", (int)seenB - 20);
await Run(b, "COMMIT");
Check(await Number(a, Balance) == 80, "lost update");

await Reset(); // Repeatable Read refuses the second write
await Run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
await Run(b, "BEGIN ISOLATION LEVEL REPEATABLE READ");
var seen = await Number(b, Balance);
await Run(a, "UPDATE accounts SET balance = balance - 10 WHERE id = 1");
await Run(a, "COMMIT");
Check(await Failure(() => Run(b, "UPDATE accounts SET balance = $1 WHERE id = 1", (int)seen - 20)) == PostgresErrorCodes.SerializationFailure, "40001");
await Run(b, "ROLLBACK");

await Reset(); // FOR UPDATE makes the second reader wait
await Run(a, "BEGIN");
await Run(a, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE");
await Run(b, "BEGIN");
await Run(b, "SET LOCAL lock_timeout = '100ms'");
Check(await Failure(() => Run(b, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")) == PostgresErrorCodes.LockNotAvailable, "55P03");
await Run(b, "ROLLBACK");
await Run(a, "COMMIT");

await Reset(); // write skew: Serializable aborts one, and the retry keeps the rule
async Task GoOffCall(NpgsqlConnection c, string name)
{
    await Run(c, "BEGIN ISOLATION LEVEL SERIALIZABLE");
    if (await Number(c, "SELECT count(*) FROM doctors WHERE on_call") >= 2) await Run(c, "UPDATE doctors SET on_call = false WHERE name = $1", name);
}
await GoOffCall(a, "alice");
await GoOffCall(b, "bob");
await Run(a, "COMMIT");
Check(await Failure(() => Run(b, "COMMIT")) == PostgresErrorCodes.SerializationFailure, "commit refused");
await WithRetry(5, async () =>
{
    try
    {
        await GoOffCall(b, "bob");
        await Run(b, "COMMIT");
    }
    catch (PostgresException)
    {
        await Run(b, "ROLLBACK");
        throw;
    }
});
Check(await Number(a, "SELECT count(*) FROM doctors WHERE on_call AND name = 'bob'") == 1 && await Number(a, "SELECT count(*) FROM doctors WHERE on_call") == 1, "bob stays");
Console.WriteLine("all isolation checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/08-transactions-and-acid/labs/csharp). `python3 labs/run.py transactions-and-acid/csharp`.

## Common pitfalls

1. **Retrying every error.** A constraint violation fails identically each time. Retry `40001` and `40P01` only.
2. **Retrying the statement, not the transaction.** After a serialization failure the transaction is dead; start again from `BEGIN`.
3. **Forgetting `ROLLBACK` on the error path** when sending `BEGIN` as SQL. The next statement fails with "current transaction is aborted". The drivers' transaction APIs do it for you.
4. **Type-asserting a wrapped Go error.** Use `errors.As`.
5. **Building SQL from values.** Use the driver's placeholder.
6. **Comparing node-postgres's `bigint` results with numbers.** They're strings.

## Check your understanding

1. Your Go code does `if pgErr, ok := err.(*pgconn.PgError); ok && pgErr.Code == "40001"`, and it never matches, though the database clearly returned `40001`. Why?
2. Why does the C# retry use `catch (PostgresException e) when (…)` rather than catching and rethrowing?
3. Which of `40001`, `40P01`, `23505` (unique violation) and `55P03` should a generic retry loop retry, and why not the others?
4. Why must the retry loop rerun the read that decided whether to update, not just the update?
5. What's the placeholder for the first parameter in JDBC, in node-postgres and in psycopg?

<details>
<summary>Answers — after your attempt</summary>

1. The error was wrapped (for example by `fmt.Errorf("…: %w", err)`) before reaching that line, so its outer type isn't `*pgconn.PgError`. `errors.As` unwraps the chain until it finds one.
2. The filter decides before the stack unwinds: errors that don't match aren't caught at all, so they keep their original stack trace and aren't accidentally swallowed. It also makes the "only these codes" rule visible in one line.
3. `40001` and `40P01`: both mean "this attempt lost a race; a fresh attempt may succeed". `23505` will fail the same way every time, so it needs handling, not retrying. `55P03` depends on the operation: a migration might retry later, while a user request might rather report "busy".
4. The decision was based on data that was out of date, and that's why the transaction failed. A retry must see the current data and decide again; in the write-skew case, the retry sees one doctor on call and correctly does nothing.
5. `?` in JDBC, `$1` in node-postgres, `%s` in psycopg.

</details>

## Practice — independent task

**Rewrite the write-skew retry with your driver's transaction API.**

1. Replace `BEGIN ISOLATION LEVEL SERIALIZABLE` and `COMMIT` with the transaction API from the table, setting the isolation level through it (each driver has an option for it).
2. Make sure a failure anywhere in the body rolls back without an explicit `ROLLBACK` in your code.
3. Keep the test's assertions: the first attempt fails with `40001`, and the retried one leaves bob on call.

**Done when:** the test passes with no `BEGIN`, `COMMIT` or `ROLLBACK` strings left in your transaction code, and you can say how your driver's API guarantees the rollback.

## Before moving on

You can read your driver's SQLSTATE for serialization failures, deadlocks and lock timeouts, write a retry loop that reruns the whole transaction for the right errors only, and pass values as parameters.

**Recap.** The anomalies and fixes are SQL, and identical everywhere. Each driver reports failures differently: exception classes in psycopg, `err.code` in node-postgres, `errors.As` to a `PgError` in pgx, `getSQLState()` in JDBC, `err.code()` with `SqlState` constants in Rust, and `PostgresException.SqlState` with `PostgresErrorCodes` in Npgsql. Retry `40001` and `40P01` by rerunning the whole transaction with backoff and a limit; never retry constraint violations. Use parameters, and in real code the driver's transaction API, which rolls back for you.

## Related

- [[databases/08-transactions-and-acid/index|Transactions and ACID]]: the main lesson
- [[databases/09-mvcc-and-concurrency-control/in-other-languages|MVCC in other languages]]: deadlocks and blocked sessions in the same drivers
- [[architecture/03-architectural-patterns/05-transactional-outbox/in-other-languages|Transactional outbox in other languages]]: rollback-by-default transaction APIs
