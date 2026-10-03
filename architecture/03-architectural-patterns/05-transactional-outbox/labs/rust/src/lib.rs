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
