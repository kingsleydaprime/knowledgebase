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
