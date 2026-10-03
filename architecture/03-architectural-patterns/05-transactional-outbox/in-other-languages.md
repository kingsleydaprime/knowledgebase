# Transactional Outbox in Other Languages

> **[Intermediate]** · A companion to [[architecture/03-architectural-patterns/05-transactional-outbox/index|transactional outbox]], which crashes a dual write at its worst moments, then shows the outbox writing the event in the same database transaction as the order, and the relay delivering it at least once. This page does the same in Python, Go, Java, Rust and C#, each against a real SQLite database, with the same five scenarios. The pattern is the same everywhere. What differs is how each language opens, commits and, above all, rolls back a transaction. Most of the outbox's safety comes from "if anything fails, nothing is saved", and each language makes that the default in a different way.

## Before you start

You can already:

- Explain the two failures of a dual write, the outbox, and why the relay delivers at least once → [[architecture/03-architectural-patterns/05-transactional-outbox/index|the main lesson]].
- Run SQL against a database from at least one of the languages here.

After this lesson you will be able to:

1. Write a transaction in your language so that any error rolls it back, without a hand-written `catch`.
2. Avoid the in-memory SQLite trap in a connection pool.
3. Name the outbox library or change-data-capture tool people use in your language instead of a hand-written relay.

## The kid version

Five shops each write a sale in a book and ring a bell for the warehouse, and the rule is "both or neither". In one shop, the page is torn out automatically if the shopkeeper walks away mid-sale. In another, it's torn out only if the shopkeeper remembers to tear it. The outbox makes the bell part of the page, so the two can't disagree. What's left is making sure a half-written page never stays.

**Where the analogy stops working.** A shopkeeper might forget. A program forgets too, and in exactly the cases that matter: an error thrown halfway, or an early return. That's why the best transaction APIs roll back unless told to commit, rather than committing unless told to roll back.

## 1. The tools, by ecosystem

| Language | SQLite driver | A transaction | Rolled back when… | Outbox in production |
|---|---|---|---|---|
| JavaScript | `node:sqlite` (built in) | `BEGIN` … `COMMIT`, by hand | your `catch` runs `ROLLBACK` | hand-written; Debezium |
| Python | `sqlite3` (built in) | `with conn:` | the block raises | hand-written; Debezium |
| Go | `modernc.org/sqlite` (pure Go) or `mattn/go-sqlite3` (cgo) | `tx, _ := db.Begin()` | **`defer tx.Rollback()`** runs | Watermill's forwarder |
| Java | `sqlite-jdbc` | `setAutoCommit(false)` … `commit()` | your `catch` calls `rollback()` | Spring Modulith's event registry; Debezium |
| Rust | `rusqlite` (bundles SQLite) | `let tx = conn.transaction()?` | **`tx` is dropped without `commit()`** | hand-written |
| C# | `Microsoft.Data.Sqlite` | `using var tx = conn.BeginTransaction()` | **`tx` is disposed without `Commit()`** | MassTransit, NServiceBus, Wolverine |

**Debezium** reads the database's change log and publishes outbox rows itself. That's the change-data-capture option from the main lesson, and it works the same whatever language wrote the rows. C and C++ use SQLite's C interface directly, but services are rarely written that way, so they have no lab here.

## 2. What changes between languages

### Rollback as the default

The outbox is only safe if a failure part-way through, such as the order's `CHECK` constraint failing, also removes the outbox row. Three of the languages make rollback what happens unless you commit:

- **Rust:** `conn.transaction()` returns a value that rolls back when it's dropped. An error returned early with `?` drops it, so it rolls back.
- **C#:** `using var tx = conn.BeginTransaction()` rolls back when it's disposed at the end of the method, unless `Commit()` ran.
- **Go:** `defer tx.Rollback()` runs on every way out of the function. After `Commit()` it does nothing, so you can always write it.

**Python**'s `with conn:` commits if the block finishes and rolls back if it raises, which is also safe. **Java** and the JavaScript lab write the `try`/`catch`/`rollback` out by hand, which works until someone adds a `return` in the middle or catches the wrong exception type.

### The in-memory database and the connection pool

Each connection to SQLite's `:memory:` gets its own, separate, empty database. Python, Java, Rust and C# hold one connection, so that doesn't matter. **Go's** `database/sql` keeps a pool, and a second connection would see no tables at all. The lab calls `db.SetMaxOpenConns(1)`. That has a second effect: with one connection, the relay's `rows` must be closed before the `UPDATE` runs, or the update waits forever for a connection that's still reading. With a real database server, every connection sees the same database, so neither issue appears; it's the in-memory test setup that bites.

### Python's transaction modes

Since Python 3.12, `sqlite3.connect(..., autocommit=False)` behaves as the database standard expects: every statement is inside a transaction, and nothing is saved until `commit()`. Before that, the default (`isolation_level=""`) opened transactions implicitly before some statements and not others, and forgetting `commit()` silently lost writes when the connection closed. The lab uses `autocommit=False`, commits the dual write explicitly, and uses `with conn:` for the outbox.

### Drivers and native code

**Go's** `modernc.org/sqlite` is SQLite translated to pure Go, so it builds without a C compiler; `mattn/go-sqlite3` wraps the C library and needs cgo. **Rust's** `rusqlite` with the `bundled` feature compiles SQLite's C source into your program on the first build. **Java's** `sqlite-jdbc` carries native libraries inside the jar and loads one at start-up. Recent JDKs warn about that unless the program is started with `--enable-native-access`, which the lab's `check.sh` passes. **C#'s** `Microsoft.Data.Sqlite` gets SQLite through its native-library package.

### Telling "the order was invalid" from "something broke"

Each test checks that a negative total fails with SQLite's `CHECK constraint failed`, and each language reports it differently: Python raises `sqlite3.IntegrityError`, Go returns an `error` whose text contains it, Java throws `SQLException`, Rust returns `rusqlite::Error`, and C# throws `SqliteException`. Real code should check the error code (SQLite's 19, "constraint") rather than the message, so it doesn't break when a driver rewords it.

## 3. The same scenarios, in every language

| Scenario | Expected in every language |
|---|---|
| dual write, save then publish, crash in between | 1 order saved, 0 events sent: the event is lost |
| dual write, publish then save, the save fails the `CHECK` | 0 orders, 1 event sent: a phantom |
| outbox, then the relay runs twice | 1 event sent the first time, 0 the second |
| outbox, the order fails the `CHECK` | 0 orders and 0 outbox rows: rolled back together |
| the relay crashes after publishing, before marking | sent twice; the idempotent consumer applies it once |

## Terms used in this lesson

1. **Auto-commit**: This is a mode in which each statement is saved as soon as it runs, as its own transaction. JDBC and most drivers start in it.
2. **Drop**: In Rust, this is what happens when a value goes out of scope: its clean-up code runs automatically. A transaction's clean-up is to roll back.
3. **Dispose**: In C#, this is the clean-up a `using` declaration runs at the end of its scope. For a transaction, it rolls back if `Commit` hasn't run.
4. **Connection pool**: This is a set of open database connections that a program reuses, handing one out for each piece of work.
5. **cgo**: This is Go's way of calling C code. Packages that use it need a C compiler to build.

## 4. Python

`open_db` uses `autocommit=False`. `place_order_with_outbox` is a `with db:` block holding both inserts: either both are committed or neither is. The relay commits each "mark as sent" separately, so a crash after publishing leaves the row unmarked, and it's sent again.

```python
"""The dual-write problem, and the transactional outbox that fixes it. The same scenarios as the JavaScript lab."""
import json
import sqlite3

SCHEMA = """
CREATE TABLE orders (id TEXT PRIMARY KEY, total_kobo INTEGER NOT NULL CHECK (total_kobo > 0));
CREATE TABLE outbox (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  type TEXT NOT NULL,
  payload TEXT NOT NULL,
  published_at TEXT
);
"""


def open_db() -> sqlite3.Connection:
    # autocommit=False (Python 3.12+): every statement runs inside a transaction that only commit() makes permanent.
    db = sqlite3.connect(":memory:", autocommit=False)
    db.executescript(SCHEMA)
    db.commit()
    return db


class FakeBroker:
    """Stands in for RabbitMQ, Kafka or SQS: it records what it was sent."""

    def __init__(self):
        self.sent: list[dict] = []

    def publish(self, event: dict) -> None:
        self.sent.append(event)


class Crash(Exception):
    pass


def count_orders(db: sqlite3.Connection) -> int:
    return db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]


# ---- The dual write: two systems, no shared transaction ----

def place_order_save_then_publish(db, broker, order_id: str, total_kobo: int, crash_between=False) -> None:
    db.execute("INSERT INTO orders (id, total_kobo) VALUES (?, ?)", (order_id, total_kobo))
    db.commit()
    if crash_between:
        raise Crash("process died after the commit")
    broker.publish({"eventId": f"evt-{order_id}", "type": "OrderPlaced", "orderId": order_id})


def place_order_publish_then_save(db, broker, order_id: str, total_kobo: int) -> None:
    broker.publish({"eventId": f"evt-{order_id}", "type": "OrderPlaced", "orderId": order_id})
    with db:  # commits if the block succeeds, rolls back if it raises
        db.execute("INSERT INTO orders (id, total_kobo) VALUES (?, ?)", (order_id, total_kobo))


# ---- The outbox: the event is written in the SAME transaction as the order ----

def place_order_with_outbox(db, order_id: str, total_kobo: int) -> None:
    with db:
        db.execute("INSERT INTO orders (id, total_kobo) VALUES (?, ?)", (order_id, total_kobo))
        db.execute("INSERT INTO outbox (event_id, type, payload) VALUES (?, ?, ?)",
                   (f"evt-{order_id}", "OrderPlaced", json.dumps({"orderId": order_id})))


def relay(db, broker, crash_before_mark=False) -> int:
    """Publish first, then mark as sent. A crash in between means the event is sent again: at least once."""
    pending = db.execute("SELECT seq, event_id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY seq").fetchall()
    for seq, event_id, type_, payload in pending:
        broker.publish({"eventId": event_id, "type": type_, **json.loads(payload)})
        if crash_before_mark:
            raise Crash("relay died after publishing, before marking")
        with db:
            db.execute("UPDATE outbox SET published_at = datetime('now') WHERE seq = ?", (seq,))
    return len(pending)


class IdempotentConsumer:
    def __init__(self):
        self.seen: set[str] = set()
        self.applied: list[str] = []

    def handle(self, event: dict) -> str:
        if event["eventId"] in self.seen:
            return "duplicate"
        self.seen.add(event["eventId"])
        self.applied.append(event["orderId"])
        return "applied"
```

```python
import sqlite3
import unittest

from outbox import (Crash, FakeBroker, IdempotentConsumer, count_orders, open_db, place_order_publish_then_save,
                    place_order_save_then_publish, place_order_with_outbox, relay)


class Outbox(unittest.TestCase):
    def test_save_then_publish_loses_the_event(self):
        db, broker = open_db(), FakeBroker()
        with self.assertRaises(Crash):
            place_order_save_then_publish(db, broker, "o1", 500_000, crash_between=True)
        self.assertEqual((count_orders(db), len(broker.sent)), (1, 0))

    def test_publish_then_save_leaves_a_phantom(self):
        db, broker = open_db(), FakeBroker()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "CHECK constraint failed"):
            place_order_publish_then_save(db, broker, "o2", -1)
        self.assertEqual((count_orders(db), len(broker.sent)), (0, 1))

    def test_outbox_a_crash_before_the_relay_loses_nothing(self):
        db, broker = open_db(), FakeBroker()
        place_order_with_outbox(db, "o3", 500_000)
        self.assertEqual(relay(db, broker), 1)
        self.assertEqual(broker.sent, [{"eventId": "evt-o3", "type": "OrderPlaced", "orderId": "o3"}])
        self.assertEqual(relay(db, broker), 0)

    def test_outbox_a_failed_order_rolls_back_its_event(self):
        db, broker = open_db(), FakeBroker()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "CHECK constraint failed"):
            place_order_with_outbox(db, "o4", -1)
        self.assertEqual((count_orders(db), relay(db, broker)), (0, 0))

    def test_relay_crash_sends_twice_consumer_applies_once(self):
        db, broker = open_db(), FakeBroker()
        place_order_with_outbox(db, "o5", 500_000)
        with self.assertRaises(Crash):
            relay(db, broker, crash_before_mark=True)
        relay(db, broker)
        self.assertEqual(len(broker.sent), 2)
        consumer = IdempotentConsumer()
        self.assertEqual([consumer.handle(e) for e in broker.sent], ["applied", "duplicate"])
        self.assertEqual(consumer.applied, ["o5"])


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/05-transactional-outbox/labs/python). `python3 labs/run.py transactional-outbox/python`.

## 5. Go

`OpenDB` limits the pool to one connection. `PlaceOrderWithOutbox` runs `defer tx.Rollback()` right after `Begin`, so every early `return err` rolls back. The crash is an error wrapping `ErrCrash`, checked with `errors.Is`. `go.mod` pins `modernc.org/sqlite`, so the first run downloads it.

```go
// Package outbox: the dual-write problem, and the transactional outbox that fixes it, on a real SQLite database.
// The same scenarios as the JavaScript lab.
package outbox

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"

	_ "modernc.org/sqlite" // a SQLite driver written in pure Go: no C compiler needed
)

const schema = `
CREATE TABLE orders (id TEXT PRIMARY KEY, total_kobo INTEGER NOT NULL CHECK (total_kobo > 0));
CREATE TABLE outbox (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  type TEXT NOT NULL,
  payload TEXT NOT NULL,
  published_at TEXT
);`

func OpenDB() (*sql.DB, error) {
	db, err := sql.Open("sqlite", ":memory:")
	if err != nil {
		return nil, err
	}
	// database/sql keeps a pool of connections, and each connection to :memory: is its own empty database.
	// One connection means one database.
	db.SetMaxOpenConns(1)
	if _, err := db.Exec(schema); err != nil {
		return nil, err
	}
	return db, nil
}

type Event struct {
	EventID, Type, OrderID string
}

// FakeBroker stands in for RabbitMQ, Kafka or SQS: it records what it was sent.
type FakeBroker struct{ Sent []Event }

func (b *FakeBroker) Publish(e Event) { b.Sent = append(b.Sent, e) }

var ErrCrash = errors.New("crash")

func CountOrders(db *sql.DB) (n int, err error) {
	err = db.QueryRow("SELECT COUNT(*) FROM orders").Scan(&n)
	return n, err
}

// ---- The dual write: two systems, no shared transaction ----

func PlaceOrderSaveThenPublish(db *sql.DB, b *FakeBroker, id string, totalKobo int, crashBetween bool) error {
	if _, err := db.Exec("INSERT INTO orders (id, total_kobo) VALUES (?, ?)", id, totalKobo); err != nil {
		return err
	}
	if crashBetween {
		return fmt.Errorf("process died after the commit: %w", ErrCrash)
	}
	b.Publish(Event{"evt-" + id, "OrderPlaced", id})
	return nil
}

func PlaceOrderPublishThenSave(db *sql.DB, b *FakeBroker, id string, totalKobo int) error {
	b.Publish(Event{"evt-" + id, "OrderPlaced", id})
	_, err := db.Exec("INSERT INTO orders (id, total_kobo) VALUES (?, ?)", id, totalKobo)
	return err
}

// ---- The outbox: the event is written in the SAME transaction as the order ----

func PlaceOrderWithOutbox(db *sql.DB, id string, totalKobo int) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback() // undoes everything unless Commit ran first; after Commit it does nothing
	if _, err := tx.Exec("INSERT INTO orders (id, total_kobo) VALUES (?, ?)", id, totalKobo); err != nil {
		return err
	}
	payload, _ := json.Marshal(map[string]string{"orderId": id})
	if _, err := tx.Exec("INSERT INTO outbox (event_id, type, payload) VALUES (?, ?, ?)", "evt-"+id, "OrderPlaced", string(payload)); err != nil {
		return err
	}
	return tx.Commit()
}

// Relay publishes first, then marks as sent. A crash in between means the event is sent again: at least once.
func Relay(db *sql.DB, b *FakeBroker, crashBeforeMark bool) (int, error) {
	type row struct {
		seq                   int64
		eventID, typ, payload string
	}
	rows, err := db.Query("SELECT seq, event_id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY seq")
	if err != nil {
		return 0, err
	}
	var pending []row
	for rows.Next() {
		var r row
		if err := rows.Scan(&r.seq, &r.eventID, &r.typ, &r.payload); err != nil {
			rows.Close()
			return 0, err
		}
		pending = append(pending, r)
	}
	rows.Close() // with one connection, it must be free before the UPDATE below can run
	for _, r := range pending {
		var p struct {
			OrderID string `json:"orderId"`
		}
		if err := json.Unmarshal([]byte(r.payload), &p); err != nil {
			return 0, err
		}
		b.Publish(Event{r.eventID, r.typ, p.OrderID})
		if crashBeforeMark {
			return 0, fmt.Errorf("relay died after publishing, before marking: %w", ErrCrash)
		}
		if _, err := db.Exec("UPDATE outbox SET published_at = datetime('now') WHERE seq = ?", r.seq); err != nil {
			return 0, err
		}
	}
	return len(pending), nil
}

type IdempotentConsumer struct {
	seen    map[string]bool
	Applied []string
}

func (c *IdempotentConsumer) Handle(e Event) string {
	if c.seen == nil {
		c.seen = map[string]bool{}
	}
	if c.seen[e.EventID] {
		return "duplicate"
	}
	c.seen[e.EventID] = true
	c.Applied = append(c.Applied, e.OrderID)
	return "applied"
}
```

```go
package outbox

import (
	"errors"
	"slices"
	"strings"
	"testing"
)

func TestSaveThenPublishLosesTheEvent(t *testing.T) {
	db, err := OpenDB()
	if err != nil {
		t.Fatal(err)
	}
	b := &FakeBroker{}
	if err := PlaceOrderSaveThenPublish(db, b, "o1", 500_000, true); !errors.Is(err, ErrCrash) {
		t.Fatal(err)
	}
	if n, _ := CountOrders(db); n != 1 || len(b.Sent) != 0 {
		t.Fatal(n, b.Sent)
	}
}

func TestPublishThenSaveLeavesAPhantom(t *testing.T) {
	db, _ := OpenDB()
	b := &FakeBroker{}
	if err := PlaceOrderPublishThenSave(db, b, "o2", -1); err == nil || !strings.Contains(err.Error(), "CHECK constraint failed") {
		t.Fatal(err)
	}
	if n, _ := CountOrders(db); n != 0 || len(b.Sent) != 1 {
		t.Fatal(n, b.Sent)
	}
}

func TestOutboxACrashBeforeTheRelayLosesNothing(t *testing.T) {
	db, _ := OpenDB()
	b := &FakeBroker{}
	if err := PlaceOrderWithOutbox(db, "o3", 500_000); err != nil {
		t.Fatal(err)
	}
	first, _ := Relay(db, b, false)
	second, _ := Relay(db, b, false)
	if first != 1 || second != 0 || !slices.Equal(b.Sent, []Event{{"evt-o3", "OrderPlaced", "o3"}}) {
		t.Fatal(first, second, b.Sent)
	}
}

func TestOutboxAFailedOrderRollsBackItsEvent(t *testing.T) {
	db, _ := OpenDB()
	if err := PlaceOrderWithOutbox(db, "o4", -1); err == nil || !strings.Contains(err.Error(), "CHECK constraint failed") {
		t.Fatal(err)
	}
	n, _ := CountOrders(db)
	sent, _ := Relay(db, &FakeBroker{}, false)
	if n != 0 || sent != 0 {
		t.Fatal(n, sent)
	}
}

func TestRelayCrashSendsTwiceConsumerAppliesOnce(t *testing.T) {
	db, _ := OpenDB()
	b := &FakeBroker{}
	PlaceOrderWithOutbox(db, "o5", 500_000)
	if _, err := Relay(db, b, true); !errors.Is(err, ErrCrash) {
		t.Fatal(err)
	}
	Relay(db, b, false)
	var c IdempotentConsumer
	var results []string
	for _, e := range b.Sent {
		results = append(results, c.Handle(e))
	}
	if len(b.Sent) != 2 || !slices.Equal(results, []string{"applied", "duplicate"}) || !slices.Equal(c.Applied, []string{"o5"}) {
		t.Fatal(b.Sent, results, c.Applied)
	}
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/05-transactional-outbox/labs/go). `python3 labs/run.py transactional-outbox/go`.

## 6. Java

Plain JDBC: `setAutoCommit(false)` starts the transaction, and a `try`/`catch` rolls back on any `SQLException` or runtime exception before rethrowing. The `finally` turns auto-commit back on. `relay` collects the pending rows into a local record, then publishes and updates each. `check.sh` downloads the `sqlite-jdbc` jar once into the shared jar cache, as the other Java labs with libraries do.

```java
package outbox;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** The dual-write problem, and the transactional outbox that fixes it, over JDBC and SQLite. */
public final class Outbox {
    private Outbox() {}

    public static Connection openDb() throws SQLException {
        Connection db = DriverManager.getConnection("jdbc:sqlite::memory:"); // the sqlite-jdbc driver registers itself
        try (Statement s = db.createStatement()) {
            s.executeUpdate("CREATE TABLE orders (id TEXT PRIMARY KEY, total_kobo INTEGER NOT NULL CHECK (total_kobo > 0))");
            s.executeUpdate("""
                CREATE TABLE outbox (
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  event_id TEXT NOT NULL UNIQUE,
                  type TEXT NOT NULL,
                  payload TEXT NOT NULL,
                  published_at TEXT
                )""");
        }
        return db;
    }

    public record Event(String eventId, String type, String orderId) {}

    /** Stands in for RabbitMQ, Kafka or SQS: it records what it was sent. */
    public static final class FakeBroker {
        public final List<Event> sent = new ArrayList<>();

        public void publish(Event e) {
            sent.add(e);
        }
    }

    public static final class Crash extends RuntimeException {
        private static final long serialVersionUID = 1L;

        public Crash(String message) {
            super(message);
        }
    }

    public static int countOrders(Connection db) throws SQLException {
        try (Statement s = db.createStatement(); ResultSet r = s.executeQuery("SELECT COUNT(*) FROM orders")) {
            return r.getInt(1);
        }
    }

    private static void insertOrder(Connection db, String id, int totalKobo) throws SQLException {
        try (PreparedStatement p = db.prepareStatement("INSERT INTO orders (id, total_kobo) VALUES (?, ?)")) {
            p.setString(1, id);
            p.setInt(2, totalKobo);
            p.executeUpdate();
        }
    }

    // ---- The dual write: two systems, no shared transaction ----

    public static void placeOrderSaveThenPublish(Connection db, FakeBroker b, String id, int totalKobo, boolean crashBetween) throws SQLException {
        insertOrder(db, id, totalKobo); // auto-commit is on by default: this is saved at once
        if (crashBetween) throw new Crash("process died after the commit");
        b.publish(new Event("evt-" + id, "OrderPlaced", id));
    }

    public static void placeOrderPublishThenSave(Connection db, FakeBroker b, String id, int totalKobo) throws SQLException {
        b.publish(new Event("evt-" + id, "OrderPlaced", id));
        insertOrder(db, id, totalKobo);
    }

    // ---- The outbox: the event is written in the SAME transaction as the order ----

    public static void placeOrderWithOutbox(Connection db, String id, int totalKobo) throws SQLException {
        db.setAutoCommit(false); // JDBC's way to start a transaction
        try {
            insertOrder(db, id, totalKobo);
            try (PreparedStatement p = db.prepareStatement("INSERT INTO outbox (event_id, type, payload) VALUES (?, ?, ?)")) {
                p.setString(1, "evt-" + id);
                p.setString(2, "OrderPlaced");
                p.setString(3, "{\"orderId\":\"" + id + "\"}"); // the IDs are plain letters and digits; real code uses a JSON library
                p.executeUpdate();
            }
            db.commit();
        } catch (SQLException | RuntimeException e) {
            db.rollback();
            throw e;
        } finally {
            db.setAutoCommit(true);
        }
    }

    /** Publish first, then mark as sent. A crash in between means the event is sent again: at least once. */
    public static int relay(Connection db, FakeBroker b, boolean crashBeforeMark) throws SQLException {
        record Row(long seq, String eventId, String type, String payload) {}
        List<Row> pending = new ArrayList<>();
        try (Statement s = db.createStatement();
                ResultSet r = s.executeQuery("SELECT seq, event_id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY seq")) {
            while (r.next()) pending.add(new Row(r.getLong(1), r.getString(2), r.getString(3), r.getString(4)));
        }
        for (Row row : pending) {
            String orderId = row.payload().replaceAll(".*\"orderId\":\"([^\"]*)\".*", "$1");
            b.publish(new Event(row.eventId(), row.type(), orderId));
            if (crashBeforeMark) throw new Crash("relay died after publishing, before marking");
            try (PreparedStatement p = db.prepareStatement("UPDATE outbox SET published_at = datetime('now') WHERE seq = ?")) {
                p.setLong(1, row.seq());
                p.executeUpdate();
            }
        }
        return pending.size();
    }

    public static final class IdempotentConsumer {
        private final Set<String> seen = new HashSet<>();
        public final List<String> applied = new ArrayList<>();

        public String handle(Event e) {
            if (!seen.add(e.eventId())) return "duplicate"; // add returns false if it was already there
            applied.add(e.orderId());
            return "applied";
        }
    }
}
```

```java
package outbox;

import java.sql.SQLException;
import java.util.List;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class OutboxCheck {
    private OutboxCheck() {}

    interface Body {
        void run() throws Exception;
    }

    private static Exception thrown(Body body) {
        try {
            body.run();
        } catch (Exception e) {
            return e;
        }
        throw new AssertionError("expected an exception");
    }

    public static void main(String[] args) throws Exception {
        try (var db = Outbox.openDb()) {
            var b = new Outbox.FakeBroker();
            assert thrown(() -> Outbox.placeOrderSaveThenPublish(db, b, "o1", 500_000, true)) instanceof Outbox.Crash;
            assert Outbox.countOrders(db) == 1 && b.sent.isEmpty(); // the order exists, and nobody will hear of it
        }
        try (var db = Outbox.openDb()) {
            var b = new Outbox.FakeBroker();
            var e = thrown(() -> Outbox.placeOrderPublishThenSave(db, b, "o2", -1));
            assert e instanceof SQLException && e.getMessage().contains("CHECK constraint failed") : e;
            assert Outbox.countOrders(db) == 0 && b.sent.size() == 1; // a phantom event
        }
        try (var db = Outbox.openDb()) {
            var b = new Outbox.FakeBroker();
            Outbox.placeOrderWithOutbox(db, "o3", 500_000);
            assert Outbox.relay(db, b, false) == 1 && Outbox.relay(db, b, false) == 0;
            assert b.sent.equals(List.of(new Outbox.Event("evt-o3", "OrderPlaced", "o3"))) : b.sent;
        }
        try (var db = Outbox.openDb()) {
            var e = thrown(() -> Outbox.placeOrderWithOutbox(db, "o4", -1));
            assert e.getMessage().contains("CHECK constraint failed") : e;
            assert Outbox.countOrders(db) == 0 && Outbox.relay(db, new Outbox.FakeBroker(), false) == 0;
        }
        try (var db = Outbox.openDb()) {
            var b = new Outbox.FakeBroker();
            Outbox.placeOrderWithOutbox(db, "o5", 500_000);
            assert thrown(() -> Outbox.relay(db, b, true)) instanceof Outbox.Crash;
            Outbox.relay(db, b, false);
            var consumer = new Outbox.IdempotentConsumer();
            assert b.sent.size() == 2 && b.sent.stream().map(consumer::handle).toList().equals(List.of("applied", "duplicate"));
            assert consumer.applied.equals(List.of("o5"));
        }
        System.out.println("all outbox checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/05-transactional-outbox/labs/java). `python3 labs/run.py transactional-outbox/java`.

## 7. Rust

`place_order_with_outbox` takes `&mut Connection`, because `transaction()` needs exclusive use of the connection, so nothing else can run a statement mid-transaction. Each `?` returns early and drops the transaction, which rolls it back. `Error` is a small enum of a crash or a database error, with a `From` conversion so `?` works on both. The payload goes through `serde_json`.

```rust
//! The dual-write problem, and the transactional outbox that fixes it, on a real SQLite database.
//! The same scenarios as the JavaScript lab.
use rusqlite::{Connection, params};
use std::collections::HashSet;

pub fn open_db() -> rusqlite::Result<Connection> {
    let db = Connection::open_in_memory()?;
    db.execute_batch(
        "CREATE TABLE orders (id TEXT PRIMARY KEY, total_kobo INTEGER NOT NULL CHECK (total_kobo > 0));
         CREATE TABLE outbox (
           seq INTEGER PRIMARY KEY AUTOINCREMENT,
           event_id TEXT NOT NULL UNIQUE,
           type TEXT NOT NULL,
           payload TEXT NOT NULL,
           published_at TEXT
         );",
    )?;
    Ok(db)
}

#[derive(Debug, Clone, PartialEq)]
pub struct Event {
    pub event_id: String,
    pub kind: String,
    pub order_id: String,
}

fn order_placed(id: &str) -> Event {
    Event {
        event_id: format!("evt-{id}"),
        kind: "OrderPlaced".into(),
        order_id: id.into(),
    }
}

/// Stands in for RabbitMQ, Kafka or SQS: it records what it was sent.
#[derive(Default)]
pub struct FakeBroker {
    pub sent: Vec<Event>,
}

#[derive(Debug)]
pub enum Error {
    Crash(&'static str),
    Db(rusqlite::Error),
}

impl From<rusqlite::Error> for Error {
    fn from(e: rusqlite::Error) -> Self {
        Error::Db(e)
    }
}

pub fn count_orders(db: &Connection) -> rusqlite::Result<i64> {
    db.query_row("SELECT COUNT(*) FROM orders", [], |r| r.get(0))
}

// ---- The dual write: two systems, no shared transaction ----

pub fn place_order_save_then_publish(
    db: &Connection,
    b: &mut FakeBroker,
    id: &str,
    total_kobo: i64,
    crash_between: bool,
) -> Result<(), Error> {
    db.execute(
        "INSERT INTO orders (id, total_kobo) VALUES (?1, ?2)",
        params![id, total_kobo],
    )?;
    if crash_between {
        return Err(Error::Crash("process died after the commit"));
    }
    b.sent.push(order_placed(id));
    Ok(())
}

pub fn place_order_publish_then_save(
    db: &Connection,
    b: &mut FakeBroker,
    id: &str,
    total_kobo: i64,
) -> Result<(), Error> {
    b.sent.push(order_placed(id));
    db.execute(
        "INSERT INTO orders (id, total_kobo) VALUES (?1, ?2)",
        params![id, total_kobo],
    )?;
    Ok(())
}

// ---- The outbox: the event is written in the SAME transaction as the order ----

/// `transaction()` needs `&mut Connection`, so nothing else can use the connection mid-transaction. If this function
/// returns early with `?`, the transaction is dropped without `commit()`, and dropping it rolls back.
pub fn place_order_with_outbox(
    db: &mut Connection,
    id: &str,
    total_kobo: i64,
) -> Result<(), Error> {
    let tx = db.transaction()?;
    tx.execute(
        "INSERT INTO orders (id, total_kobo) VALUES (?1, ?2)",
        params![id, total_kobo],
    )?;
    let payload = serde_json::json!({ "orderId": id }).to_string();
    tx.execute(
        "INSERT INTO outbox (event_id, type, payload) VALUES (?1, ?2, ?3)",
        params![format!("evt-{id}"), "OrderPlaced", payload],
    )?;
    tx.commit()?;
    Ok(())
}

/// Publish first, then mark as sent. A crash in between means the event is sent again: at least once.
pub fn relay(db: &Connection, b: &mut FakeBroker, crash_before_mark: bool) -> Result<usize, Error> {
    let pending: Vec<(i64, String, String, String)> = db
        .prepare("SELECT seq, event_id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY seq")?
        .query_map([], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?)))?
        .collect::<rusqlite::Result<_>>()?;
    for (seq, event_id, kind, payload) in &pending {
        let payload: serde_json::Value = serde_json::from_str(payload).unwrap_or_default();
        let order_id = payload["orderId"].as_str().unwrap_or_default().to_string();
        b.sent.push(Event {
            event_id: event_id.clone(),
            kind: kind.clone(),
            order_id,
        });
        if crash_before_mark {
            return Err(Error::Crash("relay died after publishing, before marking"));
        }
        db.execute(
            "UPDATE outbox SET published_at = datetime('now') WHERE seq = ?1",
            params![seq],
        )?;
    }
    Ok(pending.len())
}

#[derive(Default)]
pub struct IdempotentConsumer {
    seen: HashSet<String>,
    pub applied: Vec<String>,
}

impl IdempotentConsumer {
    pub fn handle(&mut self, e: &Event) -> &'static str {
        if !self.seen.insert(e.event_id.clone()) {
            return "duplicate"; // insert returns false if it was already there
        }
        self.applied.push(e.order_id.clone());
        "applied"
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn is_check_failure(e: &Error) -> bool {
        matches!(e, Error::Db(db) if db.to_string().contains("CHECK constraint failed"))
    }

    #[test]
    fn save_then_publish_loses_the_event() {
        let (db, mut b) = (open_db().unwrap(), FakeBroker::default());
        assert!(matches!(
            place_order_save_then_publish(&db, &mut b, "o1", 500_000, true),
            Err(Error::Crash(_))
        ));
        assert_eq!((count_orders(&db).unwrap(), b.sent.len()), (1, 0));
    }

    #[test]
    fn publish_then_save_leaves_a_phantom() {
        let (db, mut b) = (open_db().unwrap(), FakeBroker::default());
        assert!(is_check_failure(
            &place_order_publish_then_save(&db, &mut b, "o2", -1).unwrap_err()
        ));
        assert_eq!((count_orders(&db).unwrap(), b.sent.len()), (0, 1));
    }

    #[test]
    fn outbox_a_crash_before_the_relay_loses_nothing() {
        let (mut db, mut b) = (open_db().unwrap(), FakeBroker::default());
        place_order_with_outbox(&mut db, "o3", 500_000).unwrap();
        assert_eq!(relay(&db, &mut b, false).unwrap(), 1);
        assert_eq!(b.sent, [order_placed("o3")]);
        assert_eq!(relay(&db, &mut b, false).unwrap(), 0);
    }

    #[test]
    fn outbox_a_failed_order_rolls_back_its_event() {
        let mut db = open_db().unwrap();
        assert!(is_check_failure(
            &place_order_with_outbox(&mut db, "o4", -1).unwrap_err()
        ));
        assert_eq!(count_orders(&db).unwrap(), 0);
        assert_eq!(relay(&db, &mut FakeBroker::default(), false).unwrap(), 0);
    }

    #[test]
    fn relay_crash_sends_twice_consumer_applies_once() {
        let (mut db, mut b) = (open_db().unwrap(), FakeBroker::default());
        place_order_with_outbox(&mut db, "o5", 500_000).unwrap();
        assert!(matches!(relay(&db, &mut b, true), Err(Error::Crash(_))));
        relay(&db, &mut b, false).unwrap();
        let mut consumer = IdempotentConsumer::default();
        assert_eq!(
            b.sent
                .iter()
                .map(|e| consumer.handle(e))
                .collect::<Vec<_>>(),
            ["applied", "duplicate"]
        );
        assert_eq!(consumer.applied, ["o5"]);
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/05-transactional-outbox/labs/rust). `python3 labs/run.py transactional-outbox/rust`. The first build compiles SQLite itself and takes a minute or so.

## 8. C#

`using var tx = db.BeginTransaction()` rolls back at the end of the method unless `Commit()` ran. `Microsoft.Data.Sqlite`'s `CreateCommand()` puts each new command in the connection's open transaction, which the lab's outbox insert relies on. Parameters are named `$id` and `$total`. It runs in the .NET SDK container, and the NuGet package is cached between runs.

```csharp
// The dual-write problem, and the transactional outbox that fixes it, on a real SQLite database.
// The same scenarios as the JavaScript lab.
using System.Text.Json;
using Microsoft.Data.Sqlite;

public record Event(string EventId, string Type, string OrderId);

/// <summary>Stands in for RabbitMQ, Kafka or SQS: it records what it was sent.</summary>
public sealed class FakeBroker
{
    public List<Event> Sent { get; } = [];
    public void Publish(Event e) => Sent.Add(e);
}

public sealed class CrashException(string message) : Exception(message);

public static class Outbox
{
    public static SqliteConnection OpenDb()
    {
        var db = new SqliteConnection("Data Source=:memory:"); // the database lives as long as this connection is open
        db.Open();
        Execute(db, """
            CREATE TABLE orders (id TEXT PRIMARY KEY, total_kobo INTEGER NOT NULL CHECK (total_kobo > 0));
            CREATE TABLE outbox (
              seq INTEGER PRIMARY KEY AUTOINCREMENT,
              event_id TEXT NOT NULL UNIQUE,
              type TEXT NOT NULL,
              payload TEXT NOT NULL,
              published_at TEXT
            );
            """);
        return db;
    }

    private static int Execute(SqliteConnection db, string sql, params (string Name, object Value)[] args)
    {
        using var command = db.CreateCommand(); // joins the connection's current transaction, if there is one
        command.CommandText = sql;
        foreach (var (name, value) in args) command.Parameters.AddWithValue(name, value);
        return command.ExecuteNonQuery();
    }

    public static long CountOrders(SqliteConnection db)
    {
        using var command = db.CreateCommand();
        command.CommandText = "SELECT COUNT(*) FROM orders";
        return (long)command.ExecuteScalar()!;
    }

    private static void InsertOrder(SqliteConnection db, string id, int totalKobo) =>
        Execute(db, "INSERT INTO orders (id, total_kobo) VALUES ($id, $total)", ("$id", id), ("$total", totalKobo));

    // ---- The dual write: two systems, no shared transaction ----

    public static void PlaceOrderSaveThenPublish(SqliteConnection db, FakeBroker b, string id, int totalKobo, bool crashBetween = false)
    {
        InsertOrder(db, id, totalKobo);
        if (crashBetween) throw new CrashException("process died after the commit");
        b.Publish(new($"evt-{id}", "OrderPlaced", id));
    }

    public static void PlaceOrderPublishThenSave(SqliteConnection db, FakeBroker b, string id, int totalKobo)
    {
        b.Publish(new($"evt-{id}", "OrderPlaced", id));
        InsertOrder(db, id, totalKobo);
    }

    // ---- The outbox: the event is written in the SAME transaction as the order ----

    public static void PlaceOrderWithOutbox(SqliteConnection db, string id, int totalKobo)
    {
        using var tx = db.BeginTransaction(); // disposed without Commit, it rolls back
        InsertOrder(db, id, totalKobo);
        Execute(db, "INSERT INTO outbox (event_id, type, payload) VALUES ($id, $type, $payload)",
            ("$id", $"evt-{id}"), ("$type", "OrderPlaced"), ("$payload", JsonSerializer.Serialize(new { orderId = id })));
        tx.Commit();
    }

    /// <summary>Publish first, then mark as sent. A crash in between means the event is sent again: at least once.</summary>
    public static int Relay(SqliteConnection db, FakeBroker b, bool crashBeforeMark = false)
    {
        var pending = new List<(long Seq, string EventId, string Type, string Payload)>();
        using (var command = db.CreateCommand())
        {
            command.CommandText = "SELECT seq, event_id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY seq";
            using var reader = command.ExecuteReader();
            while (reader.Read()) pending.Add((reader.GetInt64(0), reader.GetString(1), reader.GetString(2), reader.GetString(3)));
        }
        foreach (var row in pending)
        {
            var orderId = JsonDocument.Parse(row.Payload).RootElement.GetProperty("orderId").GetString()!;
            b.Publish(new(row.EventId, row.Type, orderId));
            if (crashBeforeMark) throw new CrashException("relay died after publishing, before marking");
            Execute(db, "UPDATE outbox SET published_at = datetime('now') WHERE seq = $seq", ("$seq", row.Seq));
        }
        return pending.Count;
    }
}

public sealed class IdempotentConsumer
{
    private readonly HashSet<string> _seen = [];
    public List<string> Applied { get; } = [];

    public string Handle(Event e)
    {
        if (!_seen.Add(e.EventId)) return "duplicate"; // Add returns false if it was already there
        Applied.Add(e.OrderId);
        return "applied";
    }
}
```

```csharp
// Checks: the same scenarios as every other language.
using Microsoft.Data.Sqlite;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static Exception Thrown(Action body)
{
    try
    {
        body();
    }
    catch (Exception e)
    {
        return e;
    }
    throw new Exception("expected an exception");
}

using (var db = Outbox.OpenDb())
{
    var b = new FakeBroker();
    Check(Thrown(() => Outbox.PlaceOrderSaveThenPublish(db, b, "o1", 500_000, crashBetween: true)) is CrashException, "crash");
    Check(Outbox.CountOrders(db) == 1 && b.Sent.Count == 0, "the event is lost");
}
using (var db = Outbox.OpenDb())
{
    var b = new FakeBroker();
    var e = Thrown(() => Outbox.PlaceOrderPublishThenSave(db, b, "o2", -1));
    Check(e is SqliteException && e.Message.Contains("CHECK constraint failed"), e.Message);
    Check(Outbox.CountOrders(db) == 0 && b.Sent.Count == 1, "a phantom event");
}
using (var db = Outbox.OpenDb())
{
    var b = new FakeBroker();
    Outbox.PlaceOrderWithOutbox(db, "o3", 500_000);
    Check(Outbox.Relay(db, b) == 1 && Outbox.Relay(db, b) == 0, "sent once");
    Check(b.Sent.SequenceEqual([new Event("evt-o3", "OrderPlaced", "o3")]), b.Sent.Count);
}
using (var db = Outbox.OpenDb())
{
    var e = Thrown(() => Outbox.PlaceOrderWithOutbox(db, "o4", -1));
    Check(e.Message.Contains("CHECK constraint failed"), e.Message);
    Check(Outbox.CountOrders(db) == 0 && Outbox.Relay(db, new FakeBroker()) == 0, "rolled back together");
}
using (var db = Outbox.OpenDb())
{
    var b = new FakeBroker();
    Outbox.PlaceOrderWithOutbox(db, "o5", 500_000);
    Check(Thrown(() => Outbox.Relay(db, b, crashBeforeMark: true)) is CrashException, "relay crash");
    Outbox.Relay(db, b);
    var consumer = new IdempotentConsumer();
    Check(b.Sent.Count == 2 && b.Sent.Select(consumer.Handle).SequenceEqual(["applied", "duplicate"]), "applied once");
    Check(consumer.Applied.SequenceEqual(["o5"]), "o5");
}
Console.WriteLine("all outbox checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/05-transactional-outbox/labs/csharp). `python3 labs/run.py transactional-outbox/csharp`.

## Common pitfalls

1. **A hand-written rollback that misses a path.** An early `return` or an unexpected exception type skips it. Prefer `defer tx.Rollback()`, `using`, Rust's drop, or Python's `with`.
2. **`:memory:` behind a connection pool.** Each connection gets its own empty database. Limit the pool to one, or use a temporary file.
3. **Leaving rows open with a single connection.** In Go, an unclosed `rows` holds the only connection, and the next statement waits forever.
4. **Python's old transaction default.** Forgetting `commit()` under the legacy mode loses writes. Use `autocommit=False` and `with conn:`.
5. **Matching error messages.** Check SQLite's constraint error code, not the English text.

## Check your understanding

1. In which three languages does a forgotten `commit()` lead to a rollback rather than a half-saved transaction, and why?
2. Why does the Go lab call `SetMaxOpenConns(1)`, and what second problem does that create?
3. In Rust, why does `place_order_with_outbox` take `&mut Connection` when the relay takes `&Connection`?
4. The Java lab catches `SQLException | RuntimeException` before rolling back. What would go wrong if it caught only `SQLException`?
5. A team's relay is hand-written in Python. Name a tool that would publish the outbox rows without one, and how it gets them.

<details>
<summary>Answers — after your attempt</summary>

1. Rust, C# and Go. Rust's transaction rolls back when dropped; C#'s rolls back when disposed at the end of its `using` scope; Go's `defer tx.Rollback()` runs on every way out of the function. Each only saves when `commit` runs explicitly.
2. `database/sql` opens several connections, and each connection to `:memory:` has its own empty database, so a second connection would find no tables. With only one connection, any statement needs it free, so the relay's open `rows` must be closed before the `UPDATE`, or the update waits forever.
3. `transaction()` needs exclusive access to the connection for as long as the transaction lives, which Rust expresses as `&mut`. The relay runs plain statements, which only need shared access, `&`.
4. A runtime exception, such as a bug's `NullPointerException` between the two inserts, would skip the rollback. Worse, the `finally` then calls `setAutoCommit(true)`, and JDBC specifies that switching auto-commit back on in the middle of a transaction **commits** it. The order would be saved without its outbox row: exactly the lost event the pattern exists to prevent.
5. Debezium, which reads the database's change log (Postgres's write-ahead log, MySQL's binlog) and publishes each new outbox row to Kafka. That's change data capture, with no polling relay.

</details>

## Practice — independent task

**Batch the relay, safely.**

1. In your language's lab, change `relay` to mark sent events in one `UPDATE … WHERE seq IN (…)` after publishing a batch, instead of one `UPDATE` per event.
2. Use your language's safe transaction pattern for the marking.
3. Add a test: with three pending events, crash after publishing two. On restart, which events are sent again? Assert exactly that.

**Done when:** all five original tests and your new one pass, and you can say how many duplicates your batched relay can produce in the worst case, compared with the original.

## Before moving on

You can write a transaction that rolls back by default in your language, avoid the in-memory and connection-pool traps, and name the outbox tools people use in your language.

**Recap.** The outbox works the same in every language: the order and its event in one transaction, a relay that publishes then marks, and idempotent consumers. The language decides how safe the transaction is by default. Rust's drop, C#'s `using`, Go's `defer tx.Rollback()` and Python's `with conn:` roll back unless the work finishes; Java's JDBC and raw SQL need a careful `try`/`catch`. Watch `:memory:` behind Go's connection pool, and check constraint errors by code. In production, MassTransit, NServiceBus, Wolverine, Spring Modulith, Watermill or Debezium do the relaying.

## Related

- [[architecture/03-architectural-patterns/05-transactional-outbox/index|Transactional outbox]]: the main lesson
- [[architecture/02-building-blocks/04-messaging-and-async/in-other-languages|Messaging and async in other languages]]: the brokers the relay publishes to
- [[architecture/03-architectural-patterns/01-monolith-microservices-serverless/in-other-languages|Monolith, microservices, serverless in other languages]]: this week's other companion
