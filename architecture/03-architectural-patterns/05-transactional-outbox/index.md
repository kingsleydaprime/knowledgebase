# Transactional Outbox

> **[Intermediate→Advanced]** · How to save something to your database **and** tell other systems about it, without ever doing one and not the other. The fix for the "dual write" problem, with a lab that crashes at the worst moment on purpose.

## Before you start

You can already:

- Explain what a database transaction guarantees → [[databases/08-transactions-and-acid|transactions and ACID]].
- Publish and consume events, and explain why a broker's at-least-once delivery requires idempotent consumers → [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|modular monolith to services]].

After this lesson you will be able to:

1. Show the two ways a dual write fails: a **lost event** and a **phantom event**.
2. Implement an outbox table written in the same transaction as the business change, and a relay that publishes from it.
3. Explain why the relay delivers at least once, and make the consumer safe against it.
4. Choose between a polling relay and change data capture.

**Study route.** The kid version and §1–4, then the worked example. The prediction before running it is the point. §6 (trade-offs) matters for interviews.

## The kid version

You've done your homework and you need to tell your teacher it's done. If you message "done!" first and then your laptop dies before you save, the teacher thinks it's done and it isn't. If you save first and your laptop dies before you message, it's done and nobody knows.

The trick: **write "tell the teacher" on a sticky note and stick it on the homework itself, in the same go.** Now the homework and the note are saved together, or not at all. Later, whoever is passing by reads the note, tells the teacher, and crosses it out. If they get interrupted before crossing it out, the teacher might be told twice — annoying, but nothing is lost and nothing is invented.

**Where the analogy stops working.** A teacher told twice just shrugs. A program told twice might ship two parcels or charge twice — so the receiver has to be built to recognise the repeat, which is the last part of this lesson.

## 1. Why this exists

Checkout saves an order to Postgres, then publishes `OrderPlaced` to a queue so the warehouse ships it and the email service sends a receipt. One night a deploy restarts the process between those two lines. The order is in the database, paid for, and **no one ever ships it**. A week later someone reorders the lines to publish first — and now, when the insert fails a validation check, the warehouse ships an order that doesn't exist.

This is the **dual write** problem: two separate systems, and no transaction that covers both. Retrying doesn't fix it — the crash can happen during the retry too.

## Terms used in this lesson

1. **Dual write**: This is updating two separate systems — such as a database and a message broker — one after the other, with nothing guaranteeing both happen.
2. **Lost event**: This is a change that was saved but never announced, because the process stopped before publishing.
3. **Phantom event**: This is an announcement of a change that was never saved, because publishing happened first and the save then failed.
4. **Outbox table**: This is a table in the service's own database where events are written, in the same transaction as the business change, waiting to be published.
5. **Relay**: This is also known as a **message relay** or **outbox publisher**. It is a separate process that reads unpublished rows from the outbox, sends them to the broker, and marks them as sent.
6. **CDC (change data capture)**: The letters stand for those three words. It is reading a database's change log — such as Postgres's write-ahead log — to see every committed insert, instead of polling a table. Debezium is a common CDC tool.
7. **At-least-once delivery**: This is a guarantee that every event is delivered, possibly more than once.
8. **Idempotent consumer**: This is a receiver that produces the same result whether it gets an event once or several times, usually by remembering the IDs of events it has already handled.

## 2. The two failures of a dual write

There are only two orders to do the writes in, and each has its own failure.

```
Save, then publish                    Publish, then save
──────────────────                    ──────────────────
INSERT order   ✓ committed            publish OrderPlaced  ✓ sent
   ✗ crash                            INSERT order         ✗ fails (validation, deadlock, crash)
publish        never happens
                                      → PHANTOM: everyone hears about
→ LOST: the order exists, nobody        an order that doesn't exist
  is ever told
```

Wrapping both in a database transaction doesn't help. The broker isn't in the transaction, so a publish can't be rolled back, and a commit can still fail after the publish.

## 3. The outbox

Make it **one write to one system**. Insert the order and an `outbox` row describing the event **in the same database transaction**. Either both are committed or neither is, so there is no moment where one exists without the other.

```
BEGIN
  INSERT INTO orders  (...)                                  ┐ one transaction:
  INSERT INTO outbox  (event_id, type, payload, published_at=NULL) ┘ both or neither
COMMIT

relay, separately and repeatedly:
  SELECT * FROM outbox WHERE published_at IS NULL ORDER BY seq
  for each row:  publish to broker  →  UPDATE outbox SET published_at = now()
```

The service never talks to the broker during the request. The relay does it afterwards. If the relay is down, events wait in the table — delayed, never lost.

## 4. The relay delivers at least once — on purpose

The relay has its own dual write: publish, then mark as sent. It's always done in that order, because the other order would lose events. So if the relay crashes after publishing and before marking, it publishes the same row again on restart.

That's **at-least-once delivery**. It's the right trade, because a duplicate can be detected and a lost event can't. The other half of the pattern is that **consumers must be idempotent**: each event carries a unique `event_id`, and the consumer records the IDs it has handled and skips repeats.

## Worked example — crash it at the worst moments

The lab uses Node's built-in SQLite for a real transaction, and a fake broker that records what it's sent.

```js
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
```

**Predict before running.** For each of these, say what's in the `orders` table and what the broker has received:

1. Save-then-publish, crashing between the two.
2. Publish-then-save, with an order total of −1 (which the `CHECK` constraint rejects).
3. The outbox version with the same −1 total.
4. The outbox, with the relay crashing after publishing but before marking — then restarting.

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  Crash, fakeBroker, idempotentConsumer, openDb,
  placeOrderPublishThenSave, placeOrderSaveThenPublish, placeOrderWithOutbox, relay,
} from "./outbox.mjs";

const countOrders = (db) => db.prepare("SELECT COUNT(*) AS n FROM orders").get().n;

test("dual write, save then publish: a crash in between LOSES the event", async () => {
  const db = openDb(), broker = fakeBroker();
  await assert.rejects(placeOrderSaveThenPublish(db, broker, { id: "o1", totalKobo: 500_000 }, { crashBetween: true }), Crash);
  assert.equal(countOrders(db), 1);      // the order exists...
  assert.equal(broker.sent.length, 0);   // ...but nobody will ever hear about it
});

test("dual write, publish then save: a failed save leaves a PHANTOM event", async () => {
  const db = openDb(), broker = fakeBroker();
  await assert.rejects(placeOrderPublishThenSave(db, broker, { id: "o2", totalKobo: -1 }), /CHECK constraint failed/);
  assert.equal(countOrders(db), 0);      // no order...
  assert.equal(broker.sent.length, 1);   // ...but the warehouse was told to ship it
});

test("outbox: a crash before the relay runs loses nothing — the relay sends it later", async () => {
  const db = openDb(), broker = fakeBroker();
  placeOrderWithOutbox(db, { id: "o3", totalKobo: 500_000 });
  // the process dies here; on restart the relay picks up where it left off
  assert.equal(await relay(db, broker), 1);
  assert.deepEqual(broker.sent, [{ eventId: "evt-o3", type: "OrderPlaced", orderId: "o3" }]);
  assert.equal(await relay(db, broker), 0); // already marked: not sent again
});

test("outbox: a failed order rolls back its event too — no phantom", async () => {
  const db = openDb(), broker = fakeBroker();
  assert.throws(() => placeOrderWithOutbox(db, { id: "o4", totalKobo: -1 }), /CHECK constraint failed/);
  assert.equal(countOrders(db), 0);
  assert.equal(await relay(db, broker), 0);
});

test("relay crash after publish: the event is sent twice, the idempotent consumer applies it once", async () => {
  const db = openDb(), broker = fakeBroker();
  placeOrderWithOutbox(db, { id: "o5", totalKobo: 500_000 });
  await assert.rejects(relay(db, broker, { crashBeforeMark: true }), Crash);
  await relay(db, broker); // restart: the row was never marked, so it goes again
  assert.equal(broker.sent.length, 2);

  const consumer = idempotentConsumer();
  assert.deepEqual(broker.sent.map((e) => consumer.handle(e)), ["applied", "duplicate"]);
  assert.deepEqual(consumer.applied, ["o5"]);
});
```

**Lab:** these files are in [`architecture/03-architectural-patterns/05-transactional-outbox/labs/javascript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/05-transactional-outbox/labs/javascript). From the vault root, `python3 labs/run.py transactional-outbox/javascript` runs them and checks this page still shows the same code.

**Run it.** From [`architecture/03-architectural-patterns/05-transactional-outbox/labs/javascript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/05-transactional-outbox/labs/javascript), run `node --test`. It needs Node 22.5 or later for `node:sqlite`; checked with Node 26, which prints no experimental warning. Expected:

```
ℹ tests 5
ℹ pass 5
ℹ fail 0
```

**The answers.**

1. **Lost.** One order, zero events.
2. **Phantom.** Zero orders, one event — the warehouse was told to ship something that doesn't exist.
3. **Neither.** The `CHECK` failure rolls back the whole transaction, outbox row included, so the relay finds nothing to send.
4. **Duplicated, then deduplicated.** The broker receives the event twice. The consumer applies it once and reports the second as `"duplicate"`.

## 5. Polling relay or change data capture?

**Polling** — the relay runs `SELECT ... WHERE published_at IS NULL` every second or so, as in the lab. Simple, works on any database, easy to debug. Costs: a little latency (up to one poll interval), load from frequent queries, and care when running more than one relay, so two don't send the same rows. In Postgres, `SELECT ... FOR UPDATE SKIP LOCKED` lets several relays share the work safely.

**CDC** — a tool such as Debezium reads the database's write-ahead log and streams each committed outbox insert to the broker. Lower latency and no polling load, but it's another system to run, and it needs database-level permissions and configuration.

**Start with polling.** Move to CDC when the poll interval or the query load actually hurts.

## 6. Trade-offs and limits

- **Eventual, not immediate.** Other systems hear about the change a moment later, not as part of the request. Design the user experience for that gap.
- **The outbox grows.** Delete or archive published rows on a schedule, or the table and its index slow down.
- **Ordering is per producer.** `seq` gives order within one service's outbox. Across services, or with several relays and partitions, there's no global order — consumers must not rely on one.
- **It only fixes the producer side.** Consumers still need idempotency, and if they do two writes themselves, they need an **inbox** table — the mirror image: record the `event_id` and the effect in one transaction.
- **It's a building block, not the whole saga.** In a [[architecture/03-architectural-patterns/03-data-and-integration-patterns|saga]], each step's local transaction uses an outbox to announce the next step reliably.

## Common pitfalls

1. **Publishing inside the transaction "to be safe".** The broker isn't part of the transaction. If the commit fails after the publish, you've made a phantom event.
2. **Marking as sent before publishing.** A crash between the two loses the event for good — the one failure the pattern exists to prevent.
3. **No `event_id`, or one generated at publish time.** Consumers can't deduplicate. The ID must be written into the outbox row, so every retry carries the same one.
4. **Two relays without row locking.** Both read the same pending rows and both publish them. Use `SKIP LOCKED`, or run exactly one relay.
5. **Putting the outbox in a different database** from the business data. Then it's a dual write again.

## Check your understanding

1. What is a dual write, and why doesn't retrying fix it?
2. Name the two failures, and which write order causes each.
3. Why must the outbox row be in the same database as the order?
4. Why does the relay publish *before* marking the row as sent, even though that causes duplicates?
5. A consumer charges a customer's card on `OrderPlaced`. What must it store, and when?

<details>
<summary>Answers — after your attempt</summary>

1. Writing to two systems one after the other with no shared transaction. A retry is just another attempt at the same two steps, and the process can die during it too.
2. A lost event, from save-then-publish when the process stops between them. A phantom event, from publish-then-save when the save fails.
3. So one local transaction covers both. In separate databases, writing them is a dual write again.
4. Mark-then-publish can lose an event forever if the relay crashes between the steps. Publish-then-mark can only duplicate one, and duplicates can be detected and ignored by an idempotent consumer.
5. The event's `event_id`, recorded in the same transaction as the record of the charge — and checked before charging. That way a redelivered event is recognised and skipped, and a crash can't record one without the other.

</details>

## Practice — independent task

**Extend the lab into a two-service flow.**

1. Add a `payments` consumer that, on `OrderPlaced`, writes a `charges` row **and** an `inbox` row (the `event_id`) in one SQLite transaction, and skips events already in the inbox.
2. Make it write a `PaymentSucceeded` event to its **own** outbox in the same transaction, and add a relay for it.
3. Write a test where every relay crashes once after publishing. Show that each order ends with exactly one charge and exactly one `PaymentSucceeded` applied downstream.

**Done when:** the crash-everywhere test passes, no step publishes to the broker from inside a request, and you can say — without notes — which crash causes a duplicate and which component absorbs it.

## Before moving on

You can name both dual-write failures, implement an outbox and relay, and explain why the result is at-least-once delivery with idempotent consumers.

**Recap.** Never write to a database and a broker as two steps. Write the event to an outbox table in the same transaction as the change; a relay publishes it afterwards, then marks it sent. That's at-least-once delivery, so every event carries a stable ID and every consumer deduplicates on it.

**Next.** [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data and integration patterns]] — sagas, which chain these reliable local steps into multi-service workflows.

## Related
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data and integration patterns]] — saga, CQRS, event sourcing
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|Modular monolith to services]] — at-least-once delivery and idempotent consumers
- [[concepts/03-design-patterns/03-behavioral-patterns/index|Behavioural patterns]] — the observer pattern this replaces at system scale
- [[databases/08-transactions-and-acid|Transactions and ACID]] — the guarantee the pattern is built on

*Source: [reference] — the lab's behaviour was executed; production details (CDC tooling, relay locking) are from documentation, not from operating one.*
