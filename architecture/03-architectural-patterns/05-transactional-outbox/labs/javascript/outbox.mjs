// outbox.mjs — the dual-write problem, and the transactional outbox that fixes it.
import { DatabaseSync } from "node:sqlite";

export function openDb() {
  const db = new DatabaseSync(":memory:");
  db.exec(`
    CREATE TABLE orders (id TEXT PRIMARY KEY, total_kobo INTEGER NOT NULL CHECK (total_kobo > 0));
    CREATE TABLE outbox (
      seq INTEGER PRIMARY KEY AUTOINCREMENT,      -- publish order
      event_id TEXT NOT NULL UNIQUE,              -- what consumers deduplicate on
      type TEXT NOT NULL,
      payload TEXT NOT NULL,
      published_at TEXT                           -- NULL until the relay has sent it
    );
  `);
  return db;
}

// Stands in for RabbitMQ/Kafka/SQS: it just records what it was sent.
export function fakeBroker() {
  const sent = [];
  return { sent, publish: async (event) => { sent.push(event); } };
}

export class Crash extends Error {}

const transaction = (db, work) => {
  db.exec("BEGIN");
  try { work(); db.exec("COMMIT"); } catch (err) { db.exec("ROLLBACK"); throw err; }
};

// ---- The dual write: two systems, no shared transaction ----

export async function placeOrderSaveThenPublish(db, broker, order, { crashBetween = false } = {}) {
  db.prepare("INSERT INTO orders (id, total_kobo) VALUES (?, ?)").run(order.id, order.totalKobo);
  if (crashBetween) throw new Crash("process died after the commit"); // deploy, OOM, network blip
  await broker.publish({ eventId: `evt-${order.id}`, type: "OrderPlaced", orderId: order.id });
}

export async function placeOrderPublishThenSave(db, broker, order) {
  await broker.publish({ eventId: `evt-${order.id}`, type: "OrderPlaced", orderId: order.id });
  db.prepare("INSERT INTO orders (id, total_kobo) VALUES (?, ?)").run(order.id, order.totalKobo);
}

// ---- The outbox: the event is written in the SAME transaction as the order ----

export function placeOrderWithOutbox(db, order) {
  transaction(db, () => {
    db.prepare("INSERT INTO orders (id, total_kobo) VALUES (?, ?)").run(order.id, order.totalKobo);
    db.prepare("INSERT INTO outbox (event_id, type, payload) VALUES (?, ?, ?)")
      .run(`evt-${order.id}`, "OrderPlaced", JSON.stringify({ orderId: order.id }));
  });
}

// The relay runs separately (a loop, a cron job, or CDC). Publish first, then mark as sent.
export async function relay(db, broker, { crashBeforeMark = false } = {}) {
  const pending = db.prepare("SELECT seq, event_id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY seq").all();
  for (const row of pending) {
    await broker.publish({ eventId: row.event_id, type: row.type, ...JSON.parse(row.payload) });
    if (crashBeforeMark) throw new Crash("relay died after publishing, before marking");
    db.prepare("UPDATE outbox SET published_at = datetime('now') WHERE seq = ?").run(row.seq);
  }
  return pending.length;
}

// ---- A consumer that tolerates the relay's at-least-once delivery ----

export function idempotentConsumer() {
  const seen = new Set();
  const applied = [];
  return {
    applied,
    handle(event) {
      if (seen.has(event.eventId)) return "duplicate";
      seen.add(event.eventId);
      applied.push(event.orderId);
      return "applied";
    },
  };
}
