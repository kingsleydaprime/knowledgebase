# MVCC and Concurrency Control in Other Languages

**[Advanced]** — A companion to [[databases/09-mvcc-and-concurrency-control/index|MVCC and concurrency control]], which looks at row versions directly and makes snapshots, blocked vacuum and a deadlock happen on a real PostgreSQL. This page does the same in TypeScript, Go, Java, Rust and C#: a reader keeping its snapshot while a writer carries on, writers blocking writers, an open snapshot keeping 1,000 dead rows, and a deadlock with exactly one victim. The deadlock is the interesting part, because to make one, two sessions must be waiting *at the same time*, and each language has its own way to have one call blocked while another runs.

## Before you start

You can already:

- Explain snapshots, dead tuples, what blocks vacuum, and how PostgreSQL resolves a deadlock → [[databases/09-mvcc-and-concurrency-control/index|the main lesson]].
- Read your driver's SQLSTATE codes → [[databases/08-transactions-and-acid/in-other-languages|transactions in other languages]].

After this lesson you will be able to:

1. Keep one database call blocked while another runs, in your language: a pending promise, a goroutine, a thread, a scoped thread, or an un-awaited task.
2. Wait until PostgreSQL reports a session as waiting for a lock, instead of sleeping and hoping.
3. Find a session's backend process ID from your driver, to look it up in `pg_stat_activity`.

## The kid version

Two children each hold one end of a skipping rope and want the other end. Neither lets go, so neither gets anywhere, until a teacher notices and makes one of them let go. To *show* this happening, you need both children pulling at once. One child can't stand there pulling while also walking to the other end. Every language has its own way to have one "child" stand and wait while the other walks over.

**Where the analogy stops working.** The teacher in PostgreSQL only looks after a set time (`deadlock_timeout`), and picks the victim by its own rule, so the lab checks that *exactly one* was chosen, not which one.

## 1. The tools, by ecosystem

| Language | Keeping one call waiting while another runs | The session's backend process ID | A blocked session in the lab |
|---|---|---|---|
| Python | a thread | `conn.info.backend_pid` | `threading.Thread` |
| TypeScript | **nothing extra**: a query that's waiting is a promise that hasn't settled | `client.processID` | start the query, don't `await` it yet |
| Go | a goroutine, with the result sent on a channel | `conn.PgConn().PID()` | `go func() { done <- … }()` |
| Java | a thread (virtual threads make this cheap) | `SELECT pg_backend_pid()` | `Executors.newVirtualThreadPerTaskExecutor()` |
| Rust | a **scoped** thread, which may borrow the client | `SELECT pg_backend_pid()` | `std::thread::scope` |
| C# | a task that isn't awaited yet | `connection.ProcessID` | `var pending = Failure(…);` then `await pending` later |

One rule holds in every language: **a connection runs one statement at a time.** The blocked call and the next call must be on *different* connections, which is why the labs use `a`, `b` and a third `watcher` that polls `pg_stat_activity`. C and C++ would use libpq's asynchronous calls (`PQsendQuery`) or threads; they have no lab here.

## 2. What changes between languages

### Having two calls in flight

The deadlock needs session A blocked on row 2 *while* session B asks for row 1:

- **TypeScript** needs nothing special. `a.query(…)` returns a promise immediately; the database call proceeds in the background, and the event loop is free to send B's query. `Promise.allSettled` then collects both outcomes, one rejected with `40P01`.
- **C#** is the same idea with tasks: calling an `async` method without `await` starts it and hands back a `Task` to await later.
- **Go** runs A's call in a goroutine that sends its error on a buffered channel. A `pgx.Conn` isn't safe for concurrent use, so each goroutine uses only its own connection.
- **Java** submits A's call to a virtual-thread executor and reads the `Future` afterwards. The `try`-with-resources on the executor waits for it to finish.
- **Rust** uses `std::thread::scope`, so the thread can borrow `a` mutably. The borrow checker accepts it because the scope ends, and the thread is joined, before `a` is used again. A plain `std::thread::spawn` would need the client moved in, or wrapped in `Arc<Mutex<…>>`.
- **Python** uses a thread, because psycopg's ordinary connection blocks the calling thread. (Its async connection would work like TypeScript's.)

### Waiting for the right moment

Sending B's query before A is actually waiting would make B wait instead, with no deadlock. Sleeping "long enough" works until the machine is busy. Every lab instead polls `pg_stat_activity` from the watcher connection until A's `wait_event_type` is `Lock`. To do that, it needs A's backend process ID: node-postgres and Npgsql expose it as a property, pgx through `PgConn().PID()`, and Java and Rust ask the server with `SELECT pg_backend_pid()`.

### Settings that outlive the statement

The lab sets `lock_timeout` on B early, for the "writers block writers" check, and `RESET`s it before the deadlock check: otherwise B would give up on its lock after 100 ms and never become a deadlock victim. Session settings persist for the connection's life, the same caution as `SET work_mem` on a pooled connection in [[databases/07-join-algorithms-and-the-optimiser/in-other-languages|the joins companion]].

### Big numbers again

`pgstattuple`'s `dead_tuple_count` is a `bigint`. node-postgres returns `"1000"`, a string; pgx scans into `int64`; Rust reads `i64`; Java's `getLong` and C#'s `Convert.ToInt64` give 64-bit integers.

## 3. The same results, in every language

| Scenario | Expected in every language |
|---|---|
| A's Repeatable Read snapshot while B updates to 50 | B finishes at once (100 ms `lock_timeout` not hit); A reads 100; after A commits, 50 |
| B updates a row A has updated but not committed | `55P03` after 100 ms |
| A holds an idle snapshot; B updates 1,000 rows and vacuums | `dead_tuple_count` 1,000; after A commits and B vacuums again, 0 |
| A holds row 1 and wants 2; B holds 2 and wants 1 | exactly one of them fails with `40P01` |

## Terms used in this lesson

1. **Backend process ID**: This is the operating-system process ID of the PostgreSQL server process serving one connection. `pg_stat_activity` and `pg_locks` identify sessions by it.
2. **Pending promise**: In JavaScript, this is a promise whose operation has started but not finished. Not awaiting it lets other code run in the meantime.
3. **Scoped thread**: In Rust, this is a thread created inside `std::thread::scope`, guaranteed to finish before the scope ends, so it may borrow local variables.
4. **Virtual thread**: In Java, this is a lightweight thread managed by the JVM rather than the operating system, cheap enough to start one per blocking task.

## 4. TypeScript

The deadlock check starts A's update without awaiting it, waits for `pg_stat_activity` to show A waiting, sends B's update, and settles both with `Promise.allSettled`. `waitUntilBlocked` polls with `setTimeout` between checks.

```ts
// MVCC through node-postgres: snapshots, blocked vacuum and a deadlock. Run through ../shared/with-postgres.sh.
import { afterEach, beforeEach, test } from "node:test";
import assert from "node:assert/strict";
import pg from "pg";

const DEADLOCK_DETECTED = "40P01";
const LOCK_NOT_AVAILABLE = "55P03";

let a: pg.Client;
let b: pg.Client;
let watcher: pg.Client;

async function value(client: pg.Client, sql: string, params: unknown[] = []): Promise<any> {
  const { rows } = await client.query(sql, params);
  return Object.values(rows[0])[0];
}

/** Waits until the session with this backend pid is waiting for a lock. */
async function waitUntilBlocked(pid: number): Promise<void> {
  for (let i = 0; i < 500; i++) {
    if ((await value(watcher, "SELECT wait_event_type FROM pg_stat_activity WHERE pid = $1", [pid])) === "Lock") return;
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  throw new Error(`session ${pid} never waited for a lock`);
}

beforeEach(async () => {
  [a, b, watcher] = [new pg.Client(), new pg.Client(), new pg.Client()];
  await Promise.all([a.connect(), b.connect(), watcher.connect()]);
  await a.query(`
    CREATE EXTENSION IF NOT EXISTS pgstattuple;
    DROP TABLE IF EXISTS accounts;
    CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
    INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i;
  `);
  await a.query("VACUUM accounts"); // alone: VACUUM can't run inside a multi-statement call's transaction
});

afterEach(() => Promise.all([a.end(), b.end(), watcher.end()]));

test("readers don't block writers, and keep reading their snapshot", async () => {
  await a.query("BEGIN ISOLATION LEVEL REPEATABLE READ");
  assert.equal(await value(a, "SELECT balance FROM accounts WHERE id = 1"), 100);
  await b.query("SET lock_timeout = '100ms'");
  await b.query("UPDATE accounts SET balance = 50 WHERE id = 1"); // finishes at once
  assert.equal(await value(a, "SELECT balance FROM accounts WHERE id = 1"), 100);
  await a.query("COMMIT");
  assert.equal(await value(a, "SELECT balance FROM accounts WHERE id = 1"), 50);
});

test("writers block writers on the same row", async () => {
  await a.query("BEGIN");
  await a.query("UPDATE accounts SET balance = 90 WHERE id = 1");
  await b.query("SET lock_timeout = '100ms'");
  await assert.rejects(b.query("UPDATE accounts SET balance = 80 WHERE id = 1"), (err: any) => err.code === LOCK_NOT_AVAILABLE);
  await a.query("COMMIT");
});

test("an open snapshot stops vacuum removing anything", async () => {
  await a.query("BEGIN ISOLATION LEVEL REPEATABLE READ");
  await a.query("SELECT 1");
  await b.query("UPDATE accounts SET balance = balance + 1");
  await b.query("VACUUM accounts");
  assert.equal(await value(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')"), "1000"); // a bigint: a string
  await a.query("COMMIT");
  await b.query("VACUUM accounts");
  assert.equal(await value(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')"), "0");
});

test("a deadlock: exactly one victim", async () => {
  for (const client of [a, b]) await client.query("SET deadlock_timeout = '100ms'");
  await a.query("BEGIN");
  await b.query("BEGIN");
  await a.query("UPDATE accounts SET balance = 1 WHERE id = 1");
  await b.query("UPDATE accounts SET balance = 2 WHERE id = 2");
  // No threads needed: a query that's waiting for a lock is just a promise that hasn't settled yet.
  const aWantsRow2 = a.query("UPDATE accounts SET balance = 1 WHERE id = 2");
  await waitUntilBlocked((a as any).processID);
  const bWantsRow1 = b.query("UPDATE accounts SET balance = 2 WHERE id = 1");
  const results = await Promise.allSettled([aWantsRow2, bWantsRow1]);
  const victims = results.filter((r) => r.status === "rejected" && (r.reason as any).code === DEADLOCK_DETECTED);
  assert.equal(victims.length, 1);
  await Promise.all([a.query("ROLLBACK"), b.query("ROLLBACK")]);
});
```

**Lab:** [`labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/09-mvcc-and-concurrency-control/labs/typescript). `python3 labs/run.py mvcc-and-concurrency-control/typescript`.

## 5. Go

A goroutine runs A's blocked update and sends its error on a buffered channel, so the goroutine never blocks on sending. The lab runs with `-race`, and the race detector is satisfied because each connection is only ever used by one goroutine at a time.

```go
// Package mvcc: reading a PostgreSQL error's SQLSTATE through pgx, for the outcomes MVCC makes normal.
package mvcc

import (
	"errors"

	"github.com/jackc/pgx/v5/pgconn"
)

const (
	DeadlockDetected = "40P01"
	LockNotAvailable = "55P03"
)

// Code returns the SQLSTATE of a PostgreSQL error, however deeply it's wrapped, or "" for any other error.
func Code(err error) string {
	var pgErr *pgconn.PgError
	if errors.As(err, &pgErr) {
		return pgErr.Code
	}
	return ""
}
```

```go
package mvcc

// MVCC through pgx: snapshots, blocked vacuum and a deadlock. Run through ../shared/with-postgres.sh.

import (
	"context"
	"os"
	"testing"
	"time"

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

func (s session) int(sql string, args ...any) int64 {
	s.t.Helper()
	var n int64
	if err := s.conn.QueryRow(s.ctx, sql, args...).Scan(&n); err != nil {
		s.t.Fatal(sql, err)
	}
	return n
}

func sessions(t *testing.T) (session, session, session) {
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
	a, b, watcher := open(), open(), open()
	a.must(`CREATE EXTENSION IF NOT EXISTS pgstattuple;
		DROP TABLE IF EXISTS accounts;
		CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
		INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i`)
	a.must("VACUUM accounts") // alone: VACUUM can't run inside a multi-statement call's transaction
	return a, b, watcher
}

const balance = "SELECT balance FROM accounts WHERE id = 1"

func TestReadersDontBlockWriters(t *testing.T) {
	a, b, _ := sessions(t)
	a.must("BEGIN ISOLATION LEVEL REPEATABLE READ")
	if a.int(balance) != 100 {
		t.Fatal("before")
	}
	b.must("SET lock_timeout = '100ms'")
	b.must("UPDATE accounts SET balance = 50 WHERE id = 1") // finishes at once
	if a.int(balance) != 100 {
		t.Fatal("a's snapshot changed")
	}
	a.must("COMMIT")
	if a.int(balance) != 50 {
		t.Fatal("after")
	}
}

func TestWritersBlockWriters(t *testing.T) {
	a, b, _ := sessions(t)
	a.must("BEGIN")
	a.must("UPDATE accounts SET balance = 90 WHERE id = 1")
	b.must("SET lock_timeout = '100ms'")
	if err := b.exec("UPDATE accounts SET balance = 80 WHERE id = 1"); Code(err) != LockNotAvailable {
		t.Fatal(err)
	}
	a.must("COMMIT")
}

func TestAnOpenSnapshotStopsVacuum(t *testing.T) {
	a, b, _ := sessions(t)
	a.must("BEGIN ISOLATION LEVEL REPEATABLE READ")
	a.must("SELECT 1")
	b.must("UPDATE accounts SET balance = balance + 1")
	b.must("VACUUM accounts")
	if n := b.int("SELECT dead_tuple_count FROM pgstattuple('accounts')"); n != 1000 {
		t.Fatal(n)
	}
	a.must("COMMIT")
	b.must("VACUUM accounts")
	if n := b.int("SELECT dead_tuple_count FROM pgstattuple('accounts')"); n != 0 {
		t.Fatal(n)
	}
}

func TestADeadlockHasExactlyOneVictim(t *testing.T) {
	a, b, watcher := sessions(t)
	a.must("SET deadlock_timeout = '100ms'")
	b.must("SET deadlock_timeout = '100ms'")
	a.must("BEGIN")
	b.must("BEGIN")
	a.must("UPDATE accounts SET balance = 1 WHERE id = 1")
	b.must("UPDATE accounts SET balance = 2 WHERE id = 2")
	aDone := make(chan error, 1)
	go func() { aDone <- a.exec("UPDATE accounts SET balance = 1 WHERE id = 2") }() // a pgx.Conn is used by one goroutine at a time
	for i := 0; ; i++ {
		var event *string
		watcher.conn.QueryRow(watcher.ctx, "SELECT wait_event_type FROM pg_stat_activity WHERE pid = $1", a.conn.PgConn().PID()).Scan(&event)
		if event != nil && *event == "Lock" {
			break
		}
		if i == 500 {
			t.Fatal("a never waited")
		}
		time.Sleep(10 * time.Millisecond)
	}
	bErr := b.exec("UPDATE accounts SET balance = 2 WHERE id = 1")
	aErr := <-aDone
	victims := 0
	for _, err := range []error{aErr, bErr} {
		if Code(err) == DeadlockDetected {
			victims++
		}
	}
	if victims != 1 {
		t.Fatal(aErr, bErr)
	}
	a.exec("ROLLBACK")
	b.exec("ROLLBACK")
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/09-mvcc-and-concurrency-control/labs/go). `python3 labs/run.py mvcc-and-concurrency-control/go`.

## 6. Java

A virtual-thread executor runs A's blocked update; `failure` returns its SQLSTATE through the `Future`. `waitUntilBlocked` uses a `PreparedStatement` with the process ID as a parameter.

```java
package mvcc;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.concurrent.Executors;

/** MVCC through JDBC: snapshots, blocked vacuum and a deadlock. Run through ../shared/with-postgres.sh, with -ea. */
public final class MvccCheck {
    private MvccCheck() {}

    static final String DEADLOCK_DETECTED = "40P01";
    static final String LOCK_NOT_AVAILABLE = "55P03";
    static final String BALANCE = "SELECT balance FROM accounts WHERE id = 1";

    static Connection connect() throws SQLException {
        return DriverManager.getConnection("jdbc:postgresql://127.0.0.1:" + System.getenv("PGPORT") + "/postgres?user=postgres");
    }

    static void run(Connection c, String sql) throws SQLException {
        try (Statement s = c.createStatement()) {
            s.execute(sql);
        }
    }

    static long number(Connection c, String sql) throws SQLException {
        try (Statement s = c.createStatement(); ResultSet r = s.executeQuery(sql)) {
            r.next();
            return r.getLong(1);
        }
    }

    /** The SQLSTATE a statement fails with, or null if it succeeds. */
    static String failure(Connection c, String sql) {
        try {
            run(c, sql);
            return null;
        } catch (SQLException e) {
            return e.getSQLState();
        }
    }

    static int pid(Connection c) throws SQLException {
        return (int) number(c, "SELECT pg_backend_pid()");
    }

    static void waitUntilBlocked(Connection watcher, int pid) throws SQLException, InterruptedException {
        try (PreparedStatement s = watcher.prepareStatement("SELECT wait_event_type FROM pg_stat_activity WHERE pid = ?")) {
            s.setInt(1, pid);
            for (int i = 0; i < 500; i++) {
                try (ResultSet r = s.executeQuery()) {
                    if (r.next() && "Lock".equals(r.getString(1))) return;
                }
                Thread.sleep(10);
            }
        }
        throw new AssertionError("session " + pid + " never waited for a lock");
    }

    static void reset(Connection a) throws SQLException {
        run(a, """
            CREATE EXTENSION IF NOT EXISTS pgstattuple;
            DROP TABLE IF EXISTS accounts;
            CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
            INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i""");
        run(a, "VACUUM accounts"); // alone: VACUUM can't run inside a multi-statement call's transaction
    }

    public static void main(String[] args) throws Exception {
        try (Connection a = connect(); Connection b = connect(); Connection watcher = connect()) {
            reset(a); // readers don't block writers
            run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
            assert number(a, BALANCE) == 100;
            run(b, "SET lock_timeout = '100ms'");
            run(b, "UPDATE accounts SET balance = 50 WHERE id = 1");
            assert number(a, BALANCE) == 100;
            run(a, "COMMIT");
            assert number(a, BALANCE) == 50;

            reset(a); // writers block writers
            run(a, "BEGIN");
            run(a, "UPDATE accounts SET balance = 90 WHERE id = 1");
            assert LOCK_NOT_AVAILABLE.equals(failure(b, "UPDATE accounts SET balance = 80 WHERE id = 1"));
            run(a, "COMMIT");

            reset(a); // an open snapshot stops vacuum
            run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
            run(a, "SELECT 1");
            run(b, "UPDATE accounts SET balance = balance + 1");
            run(b, "VACUUM accounts");
            assert number(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')") == 1000;
            run(a, "COMMIT");
            run(b, "VACUUM accounts");
            assert number(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')") == 0;

            reset(a); // a deadlock: exactly one victim
            run(b, "RESET lock_timeout");
            run(a, "SET deadlock_timeout = '100ms'");
            run(b, "SET deadlock_timeout = '100ms'");
            run(a, "BEGIN");
            run(b, "BEGIN");
            run(a, "UPDATE accounts SET balance = 1 WHERE id = 1");
            run(b, "UPDATE accounts SET balance = 2 WHERE id = 2");
            int aPid = pid(a);
            try (var threads = Executors.newVirtualThreadPerTaskExecutor()) {
                var aWantsRow2 = threads.submit(() -> failure(a, "UPDATE accounts SET balance = 1 WHERE id = 2"));
                waitUntilBlocked(watcher, aPid);
                String bResult = failure(b, "UPDATE accounts SET balance = 2 WHERE id = 1");
                long victims = List.of(String.valueOf(aWantsRow2.get()), String.valueOf(bResult)).stream().filter(DEADLOCK_DETECTED::equals).count();
                assert victims == 1 : aWantsRow2.get() + " " + bResult;
            }
            run(a, "ROLLBACK");
            run(b, "ROLLBACK");
        }
        System.out.println("all mvcc checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/09-mvcc-and-concurrency-control/labs/java). `python3 labs/run.py mvcc-and-concurrency-control/java`.

## 7. Rust

`std::thread::scope` lets the waiting thread borrow `a` mutably, with no `Arc` or `Mutex`, because the scope guarantees the thread is joined before `a` is used again. Several statements go in one `batch_execute` where none of them is `VACUUM`.

```rust
//! Connecting to the throwaway database, and reading an error's SQLSTATE.
use postgres::error::SqlState;
use postgres::{Client, Config, NoTls};

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

pub fn code<T>(result: &Result<T, postgres::Error>) -> Option<&SqlState> {
    result.as_ref().err().and_then(postgres::Error::code)
}
```

```rust
//! MVCC through the `postgres` crate: snapshots, blocked vacuum and a deadlock. Run through
//! ../shared/with-postgres.sh; without PGHOST, it does nothing.
use mvcc::{code, connect};
use postgres::Client;
use postgres::error::SqlState;
use std::time::Duration;

const BALANCE: &str = "SELECT balance FROM accounts WHERE id = 1";

fn balance(c: &mut Client) -> i32 {
    c.query_one(BALANCE, &[]).unwrap().get(0) // an int column reads as i32: the crate won't widen it for you
}

fn dead(c: &mut Client) -> i64 {
    c.query_one("SELECT dead_tuple_count FROM pgstattuple('accounts')", &[])
        .unwrap()
        .get(0)
}

fn reset(a: &mut Client) {
    a.batch_execute(
        "CREATE EXTENSION IF NOT EXISTS pgstattuple;
         DROP TABLE IF EXISTS accounts;
         CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
         INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i;",
    )
    .unwrap();
    a.batch_execute("VACUUM accounts").unwrap(); // alone: VACUUM can't run inside a multi-statement call's transaction
}

#[test]
fn mvcc() {
    if std::env::var("PGHOST").is_err() {
        return;
    }
    let (mut a, mut b, mut watcher) = (connect(), connect(), connect());

    reset(&mut a); // readers don't block writers
    a.batch_execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        .unwrap();
    assert_eq!(balance(&mut a), 100);
    b.batch_execute("SET lock_timeout = '100ms'; UPDATE accounts SET balance = 50 WHERE id = 1")
        .unwrap();
    assert_eq!(balance(&mut a), 100);
    a.batch_execute("COMMIT").unwrap();
    assert_eq!(balance(&mut a), 50);

    reset(&mut a); // writers block writers
    a.batch_execute("BEGIN; UPDATE accounts SET balance = 90 WHERE id = 1")
        .unwrap();
    let blocked = b.batch_execute("UPDATE accounts SET balance = 80 WHERE id = 1");
    assert_eq!(code(&blocked), Some(&SqlState::LOCK_NOT_AVAILABLE));
    a.batch_execute("COMMIT").unwrap();

    reset(&mut a); // an open snapshot stops vacuum
    a.batch_execute("BEGIN ISOLATION LEVEL REPEATABLE READ; SELECT 1")
        .unwrap();
    b.batch_execute("UPDATE accounts SET balance = balance + 1")
        .unwrap();
    b.batch_execute("VACUUM accounts").unwrap();
    assert_eq!(dead(&mut b), 1000);
    a.batch_execute("COMMIT").unwrap();
    b.batch_execute("VACUUM accounts").unwrap();
    assert_eq!(dead(&mut b), 0);

    reset(&mut a); // a deadlock: exactly one victim
    b.batch_execute("RESET lock_timeout").unwrap();
    for c in [&mut a, &mut b] {
        c.batch_execute("SET deadlock_timeout = '100ms'; BEGIN")
            .unwrap();
    }
    a.batch_execute("UPDATE accounts SET balance = 1 WHERE id = 1")
        .unwrap();
    b.batch_execute("UPDATE accounts SET balance = 2 WHERE id = 2")
        .unwrap();
    let a_pid: i32 = a.query_one("SELECT pg_backend_pid()", &[]).unwrap().get(0);
    let (a_result, b_result) = std::thread::scope(|s| {
        // A scoped thread may borrow `a` mutably: the scope ends before `a` is used again.
        let waiting = s.spawn(|| a.batch_execute("UPDATE accounts SET balance = 1 WHERE id = 2"));
        loop {
            let row = watcher
                .query_one(
                    "SELECT wait_event_type FROM pg_stat_activity WHERE pid = $1",
                    &[&a_pid],
                )
                .unwrap();
            if row.get::<_, Option<String>>(0).as_deref() == Some("Lock") {
                break;
            }
            std::thread::sleep(Duration::from_millis(10));
        }
        let b_result = b.batch_execute("UPDATE accounts SET balance = 2 WHERE id = 1");
        (waiting.join().unwrap(), b_result)
    });
    let victims = [code(&a_result), code(&b_result)]
        .iter()
        .filter(|c| **c == Some(&SqlState::T_R_DEADLOCK_DETECTED))
        .count();
    assert_eq!(victims, 1);
    a.batch_execute("ROLLBACK").unwrap();
    b.batch_execute("ROLLBACK").unwrap();
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/09-mvcc-and-concurrency-control/labs/rust). `python3 labs/run.py mvcc-and-concurrency-control/rust`.

## 8. C#

A's blocked update is a task started without `await`; the polling loop runs on another connection; then both results are awaited. `NpgsqlConnection.ProcessID` gives the backend process ID directly.

```csharp
// MVCC through Npgsql: snapshots, blocked vacuum and a deadlock.
using Npgsql;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var connectionString = $"Host=127.0.0.1;Port={Environment.GetEnvironmentVariable("PGPORT")};Username=postgres;Database=postgres";
await using var a = new NpgsqlConnection(connectionString);
await using var b = new NpgsqlConnection(connectionString);
await using var watcher = new NpgsqlConnection(connectionString);
await Task.WhenAll(a.OpenAsync(), b.OpenAsync(), watcher.OpenAsync());

static async Task Run(NpgsqlConnection c, string sql)
{
    await using var command = new NpgsqlCommand(sql, c);
    await command.ExecuteNonQueryAsync();
}

static async Task<long> Number(NpgsqlConnection c, string sql)
{
    await using var command = new NpgsqlCommand(sql, c);
    return Convert.ToInt64(await command.ExecuteScalarAsync());
}

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

const string Balance = "SELECT balance FROM accounts WHERE id = 1";
async Task Reset()
{
    await Run(a, """
        CREATE EXTENSION IF NOT EXISTS pgstattuple;
        DROP TABLE IF EXISTS accounts;
        CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
        INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i
        """);
    await Run(a, "VACUUM accounts"); // alone: VACUUM can't run inside a multi-statement call's transaction
}

await Reset(); // readers don't block writers
await Run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
Check(await Number(a, Balance) == 100, "before");
await Run(b, "SET lock_timeout = '100ms'");
await Run(b, "UPDATE accounts SET balance = 50 WHERE id = 1");
Check(await Number(a, Balance) == 100, "a's snapshot");
await Run(a, "COMMIT");
Check(await Number(a, Balance) == 50, "after");

await Reset(); // writers block writers
await Run(a, "BEGIN");
await Run(a, "UPDATE accounts SET balance = 90 WHERE id = 1");
Check(await Failure(() => Run(b, "UPDATE accounts SET balance = 80 WHERE id = 1")) == PostgresErrorCodes.LockNotAvailable, "55P03");
await Run(a, "COMMIT");

await Reset(); // an open snapshot stops vacuum
await Run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
await Run(a, "SELECT 1");
await Run(b, "UPDATE accounts SET balance = balance + 1");
await Run(b, "VACUUM accounts");
Check(await Number(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')") == 1000, "kept");
await Run(a, "COMMIT");
await Run(b, "VACUUM accounts");
Check(await Number(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')") == 0, "removed");

await Reset(); // a deadlock: exactly one victim
await Run(b, "RESET lock_timeout");
foreach (var c in new[] { a, b }) await Run(c, "SET deadlock_timeout = '100ms'");
await Run(a, "BEGIN");
await Run(b, "BEGIN");
await Run(a, "UPDATE accounts SET balance = 1 WHERE id = 1");
await Run(b, "UPDATE accounts SET balance = 2 WHERE id = 2");
var aWantsRow2 = Failure(() => Run(a, "UPDATE accounts SET balance = 1 WHERE id = 2")); // started, not awaited: it's waiting
for (var i = 0; ; i++)
{
    await using var command = new NpgsqlCommand($"SELECT wait_event_type FROM pg_stat_activity WHERE pid = {a.ProcessID}", watcher);
    if (await command.ExecuteScalarAsync() is "Lock") break;
    Check(i < 500, "a never waited");
    await Task.Delay(10);
}
var bResult = await Failure(() => Run(b, "UPDATE accounts SET balance = 2 WHERE id = 1"));
var aResult = await aWantsRow2;
Check(new[] { aResult, bResult }.Count(code => code == PostgresErrorCodes.DeadlockDetected) == 1, (aResult, bResult));
await Run(a, "ROLLBACK");
await Run(b, "ROLLBACK");
Console.WriteLine("all mvcc checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/databases/09-mvcc-and-concurrency-control/labs/csharp). `python3 labs/run.py mvcc-and-concurrency-control/csharp`.

## Common pitfalls

1. **Two concurrent calls on one connection.** A connection runs one statement at a time; most drivers queue, some fail. Use one connection per concurrent call.
2. **Sleeping instead of waiting for the lock.** Poll `pg_stat_activity` for `wait_event_type = 'Lock'`.
3. **A leftover `lock_timeout`.** It makes the session give up instead of waiting, and hides the behaviour you're testing.
4. **Sharing a pgx connection across goroutines.** It isn't safe for concurrent use; use a pool (`pgxpool`) in real code.
5. **Awaiting a JavaScript or C# query too early.** Awaiting A's update before sending B's means the test waits forever: A can't finish until B's update arrives.

## Check your understanding

1. Why does the TypeScript deadlock test need no threads, when Python's does?
2. What would happen in the C# test if the first update were awaited before the polling loop?
3. Why can Rust's scoped thread borrow `a` mutably when a thread from `std::thread::spawn` can't?
4. Why does the lab poll `pg_stat_activity` from a third connection, rather than from `a` or `b`?
5. Why is the test's assertion "exactly one victim" rather than "b is the victim"?

<details>
<summary>Answers — after your attempt</summary>

1. node-postgres sends queries without blocking the JavaScript thread: `a.query()` returns a promise at once, and the event loop is free to send B's query while A's waits in the database. psycopg's ordinary connection blocks the calling thread for the whole query, so a second thread is needed to keep going.
2. A's update can't finish until the deadlock is resolved, and the deadlock can't exist until B sends its update, which comes after the `await`. The test would hang (until a timeout), with A waiting for a row B holds.
3. A scoped thread is guaranteed to finish before the scope returns, so the compiler knows the borrow of `a` ends before `a` is used again. A spawned thread might outlive the function, so anything it uses must be owned (`'static`), and a mutable borrow of a local isn't.
4. `a` is busy, blocked in its update, and `b` is about to be. A connection runs one statement at a time, so the watcher needs its own.
5. PostgreSQL's choice depends on which session's deadlock check runs first, which depends on timing. The lesson's point is that one transaction is cancelled and the other proceeds; which one is an implementation detail the application shouldn't rely on.

</details>

## Practice — independent task

**Reproduce the migration lock queue in your language.**

1. Port the main lesson's last test: A holds an open transaction that read the table, B runs `ALTER TABLE … ADD COLUMN` (blocked), and C's plain `SELECT` with a 200 ms `lock_timeout` fails with `55P03`.
2. Then show the fix: B with its own `lock_timeout` fails fast, and C's `SELECT` succeeds.
3. Use your language's way of keeping B's call waiting, and wait for B in `pg_stat_activity` before running C.

**Done when:** both halves pass several times in a row, and you can say which object in your code holds B's pending call.

## Before moving on

You can keep one database call waiting while another runs in your language, wait for PostgreSQL to report a lock wait instead of sleeping, and find a session's process ID through your driver.

**Recap.** MVCC behaves identically through every driver. To make two sessions wait at once, each language has its tool: a pending promise in TypeScript, an un-awaited task in C#, a goroutine in Go, a virtual thread in Java, a scoped thread in Rust, a thread in Python. Use one connection per concurrent call, poll `pg_stat_activity` from a third to know when a session is waiting, and clear leftover session settings like `lock_timeout` before testing something that depends on waiting.

## Related

- [[databases/09-mvcc-and-concurrency-control/index|MVCC and concurrency control]]: the main lesson
- [[databases/08-transactions-and-acid/in-other-languages|Transactions in other languages]]: SQLSTATE codes and retry loops in the same drivers
- [[architecture/02-building-blocks/04-messaging-and-async/in-other-languages|Messaging in other languages]]: blocked producers, tested without sleeps
