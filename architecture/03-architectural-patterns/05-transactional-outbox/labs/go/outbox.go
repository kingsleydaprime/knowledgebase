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
