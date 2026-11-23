---
id: 475d7d74-dc61-4bd4-a459-6db006ec1d15
---

# Transactional Outbox

The transactional outbox is a way of saving a change to the database and the message announcing that change together, so you never get one without the other.

## Before you start
<!-- bite: 1da294af-1365-4acc-9cdf-990af132ae65 -->

You can already:

- Explain what a database transaction guarantees → [[databases/08-transactions-and-acid/index|transactions and ACID]].
- Publish and consume events, and explain why a broker's at-least-once delivery requires idempotent consumers → [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|modular monolith to services]].

After this lesson you will be able to:

1. Show the two ways a dual write fails: a **lost event** and a **phantom event**.
2. Implement an outbox table written in the same transaction as the business change, and a relay that publishes from it.
3. Explain why the relay delivers at least once, and make the consumer safe against it.
4. Choose between a polling relay and change data capture.

**Study route.** The kid version and §1–4, then the worked example. The prediction before running it is the point. §6 (trade-offs) matters for interviews.

## What the transactional outbox is
<!-- bite: 0d8587b4-e441-45f9-86e6-81f4c6f8a148 -->

The transactional outbox saves a change and its message together, so you never get one without the other.

Think of a shop app that saves your order but fails to send the "order placed" message to the warehouse. This lesson shows how the outbox stops that from happening.

## The kid version
<!-- bite: d7142210-eea8-46e2-bef2-b95ab499d1ab -->

You've done your homework and you need to tell your teacher it's done. If you message "done!" first and then your laptop dies before you save, the teacher thinks it's done and it isn't. If you save first and your laptop dies before you message, it's done and nobody knows.

The trick: **write "tell the teacher" on a sticky note and stick it on the homework itself, in the same go.** Now the homework and the note are saved together, or not at all. Later, whoever is passing by reads the note, tells the teacher, and crosses it out. If they get interrupted before crossing it out, the teacher might be told twice — annoying, but nothing is lost and nothing is invented.

**Where the analogy stops working.** A teacher told twice just shrugs. A program told twice might ship two parcels or charge twice — so the receiver has to be built to recognise the repeat, which is the last part of this lesson.

## 1. Why this exists
<!-- bite: a86a979e-5752-4880-b927-d65806fa3e8b -->

Checkout saves an order to Postgres, then publishes `OrderPlaced` to a queue so the warehouse ships it and the email service sends a receipt. One night a deploy restarts the process between those two lines. The order is in the database, paid for, and **no one ever ships it**. A week later someone reorders the lines to publish first — and now, when the insert fails a validation check, the warehouse ships an order that doesn't exist.

This is the **dual write** problem: two separate systems, and no transaction that covers both. Retrying doesn't fix it — the crash can happen during the retry too.

## Terms used in this lesson
<!-- bite: 737bc0f0-5333-4fc2-ae9d-ebc9ddbd50c4 -->

1. **Dual write**: This is updating two separate systems — such as a database and a message broker — one after the other, with nothing guaranteeing both happen.
2. **Lost event**: This is a change that was saved but never announced, because the process stopped before publishing.
3. **Phantom event**: This is an announcement of a change that was never saved, because publishing happened first and the save then failed.
4. **Outbox table**: This is a table in the service's own database where events are written, in the same transaction as the business change, waiting to be published.

## More terms: the relay and delivery
<!-- bite: 035fb6fb-8853-4b9e-94a1-7aab5e691b07 -->

These terms describe the process that sends the saved messages, and how receivers cope with repeats.

5. **Relay**: This is also known as a **message relay** or **outbox publisher**. It is a separate process that reads unpublished rows from the outbox, sends them to the broker, and marks them as sent.
6. **CDC (change data capture)**: The letters stand for those three words. It is reading a database's change log — such as Postgres's write-ahead log — to see every committed insert, instead of polling a table. Debezium is a common CDC tool.
7. **At-least-once delivery**: This is a guarantee that every event is delivered, possibly more than once.
8. **Idempotent consumer**: This is a receiver that produces the same result whether it gets an event once or several times, usually by remembering the IDs of events it has already handled.

## 2. The two failures of a dual write
<!-- bite: 774ef870-5e7b-40ac-bca1-05c4c60882ea -->

There are only two orders to do the writes in, and each has its own failure.

In each panel, time runs down. The green arrow is the write that worked, and the red mark is where it went wrong.

![Two panels. Save, then publish: the service's INSERT order commits, the service crashes, and the publish never happens, so the order is LOST to everyone else. Publish, then save: OrderPlaced is published, then INSERT order fails, so everyone hears about a PHANTOM order that doesn't exist.](../../images/sd-dual-write.svg)

Wrapping both in a database transaction doesn't help. The broker isn't in the transaction, so a publish can't be rolled back, and a commit can still fail after the publish.

## 3. The outbox
<!-- bite: ceef736c-1d54-415a-8923-a4e0c23af1c2 -->

Make it **one write to one system**. Insert the order and an `outbox` row describing the event **in the same database transaction**. Either both are committed or neither is, so there is no moment where one exists without the other.

```text
BEGIN
  INSERT INTO orders  (...)                                         -- one transaction:
  INSERT INTO outbox  (event_id, type, payload, published_at=NULL)  -- both or neither
COMMIT

relay, separately and repeatedly:
  SELECT * FROM outbox WHERE published_at IS NULL ORDER BY seq
  for each row:  publish to broker  →  UPDATE outbox SET published_at = now()
```

The service never talks to the broker during the request. The relay does it afterwards. If the relay is down, events wait in the table — delayed, never lost.

## Seeing the outbox flow
<!-- bite: 4f0f7af8-9eb7-4303-aac6-a7765ceaef35 -->

The green band is the request: two inserts and one commit, all in the database. The blue band happens later, in the relay: find the unpublished row, publish it, then mark it sent.

![The outbox as messages: in one transaction the service inserts the order and an outbox row and commits; later the relay selects unpublished rows, gets OrderPlaced o5, publishes it to the broker, and then updates published_at; the request never talks to the broker.](../../images/sd-outbox-flow.svg)

## 4. The relay delivers at least once — on purpose
<!-- bite: 518ddf95-72ee-408f-9f53-a4ca108d4ffe -->

The relay has its own dual write: publish, then mark as sent. It's always done in that order, because the other order would lose events. So if the relay crashes after publishing and before marking, it publishes the same row again on restart.

That's **at-least-once delivery**. It's the right trade, because a duplicate can be detected and a lost event can't. The other half of the pattern is that **consumers must be idempotent**: each event carries a unique `event_id`, and the consumer records the IDs it has handled and skips repeats.

## Seeing the relay crash and the duplicate
<!-- bite: 9445205d-a962-4687-acc0-3a7211083998 -->

Follow the relay crash in the picture: the broker gets the event twice, and the consumer's check of the event ID turns the second copy into a skip.

![The relay publishes OrderPlaced evt-o5 and the consumer applies it; the relay crashes before marking it sent; on restart it finds the row still unpublished and publishes it again; the consumer skips the second copy as a duplicate; then the relay marks the row published.](../../images/sd-outbox-relay-duplicate.svg)

## Worked example — crash it at the worst moments
<!-- bite: 12cfd98a-0804-42fd-81f8-eb9a79387282 -->

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

## Worked example: predict before running
<!-- bite: f71fa58a-6afb-4fdb-9998-05478e8e1102 -->

Before running the tests, predict what each crash leaves behind.

**Predict before running.** For each of these, say what's in the `orders` table and what the broker has received:

1. Save-then-publish, crashing between the two.
2. Publish-then-save, with an order total of −1 (which the `CHECK` constraint rejects).
3. The outbox version with the same −1 total.
4. The outbox, with the relay crashing after publishing but before marking — then restarting.

## Worked example: the tests
<!-- bite: 21ff4698-fbac-4d3a-8b8e-f2c9c336ae43 -->

This file crashes the code at each bad moment and checks what survived.

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

## Worked example: run it, and the answers
<!-- bite: 2c18153c-49c0-4a32-8888-465d67c2ea67 -->

Here is what a passing run looks like, and the answers to the prediction.

**Run it.** From [`architecture/03-architectural-patterns/05-transactional-outbox/labs/javascript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/05-transactional-outbox/labs/javascript), run `node --test`. It needs Node 22.5 or later for `node:sqlite`; checked with Node 26, which prints no experimental warning. Expected:

```text
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
<!-- bite: ddbafb36-a6f3-442c-a213-221299324cde -->

**Polling** — the relay runs `SELECT ... WHERE published_at IS NULL` every second or so, as in the lab. Simple, works on any database, easy to debug. Costs: a little latency (up to one poll interval), load from frequent queries, and care when running more than one relay, so two don't send the same rows. In Postgres, `SELECT ... FOR UPDATE SKIP LOCKED` lets several relays share the work safely.

**CDC** — a tool such as Debezium reads the database's write-ahead log and streams each committed outbox insert to the broker. Lower latency and no polling load, but it's another system to run, and it needs database-level permissions and configuration.

**Start with polling.** Move to CDC when the poll interval or the query load actually hurts.

## 6. Trade-offs and limits
<!-- bite: c89722ff-8941-40af-83e9-cf6eb8224a82 -->

- **Eventual, not immediate.** Other systems hear about the change a moment later, not as part of the request. Design the user experience for that gap.
- **The outbox grows.** Delete or archive published rows on a schedule, or the table and its index slow down.
- **Ordering is per producer.** `seq` gives order within one service's outbox. Across services, or with several relays and partitions, there's no global order — consumers must not rely on one.
- **It only fixes the producer side.** Consumers still need idempotency, and if they do two writes themselves, they need an **inbox** table — the mirror image: record the `event_id` and the effect in one transaction.
- **It's a building block, not the whole saga.** In a [[architecture/03-architectural-patterns/03-data-and-integration-patterns|saga]], each step's local transaction uses an outbox to announce the next step reliably.

## Common pitfalls
<!-- bite: c4d25ef2-60d9-45c3-a48d-ac531a88bc3f -->

1. **Publishing inside the transaction "to be safe".** The broker isn't part of the transaction. If the commit fails after the publish, you've made a phantom event.
2. **Marking as sent before publishing.** A crash between the two loses the event for good — the one failure the pattern exists to prevent.
3. **No `event_id`, or one generated at publish time.** Consumers can't deduplicate. The ID must be written into the outbox row, so every retry carries the same one.
4. **Two relays without row locking.** Both read the same pending rows and both publish them. Use `SKIP LOCKED`, or run exactly one relay.
5. **Putting the outbox in a different database** from the business data. Then it's a dual write again.

## Check your understanding
<!-- bite: 3e3ed8ea-359b-42e5-8644-3793940df197 -->

Try each one before you open the answer.

1. <!-- q: open id="17e55320" -->
   A dual write updates two separate systems, such as a database and a message broker, one after the other. Why doesn't retrying fix it?

   <details><summary>Answer</summary>

   There's no transaction covering both systems. A retry is just another attempt at the same two steps, and the process can die between them during the retry too.

   </details>

2. <!-- q: gap id="09fa75c0" answers="lost;phantom" -->
   Fill in the gaps. Save-then-publish, with a crash between the two, gives a ___ event: saved but never announced. Publish-then-save, where the save then fails, gives a ___ event: announced but never saved.

   <details><summary>Answer</summary>

   A lost event and a phantom event. Each write order has its own failure, which is why the outbox makes it one write to one system.

   </details>

3. <!-- q: mcq id="8353b80d" -->
   Why must the outbox table be in the same database as the order?

   - [ ] So the relay can find it faster
   - [x] So one local transaction covers both; in a separate database, writing them is a dual write again
   - [ ] Because brokers can only read from the main database
   - [ ] It doesn't have to be

   <details><summary>Answer</summary>

   The whole pattern rests on the order and its event being committed together or not at all, which only one database's transaction can promise.

   </details>

4. <!-- q: mcq id="3929ceab" -->
   Why does the relay publish an outbox row before marking it as sent, even though that can cause duplicates?

   - [ ] Marking is slower than publishing
   - [x] Mark-then-publish can lose an event forever if the relay crashes between the steps, while publish-then-mark only duplicates, which consumers can detect
   - [ ] The broker requires it
   - [ ] To keep events in order

   <details><summary>Answer</summary>

   A duplicate can be recognised by its `event_id` and skipped. A lost event can't be recovered, so the relay deliberately delivers at least once.

   </details>

5. <!-- q: mcq id="65eea30c" -->
   A consumer charges a customer's card when it receives `OrderPlaced`. What must it do to be safe against repeats?

   - [ ] Nothing, the outbox already prevents duplicates
   - [ ] Generate a new event ID when it receives the event
   - [x] Check the event's `event_id` before charging, and record it in the same transaction as the record of the charge
   - [ ] Ask the relay to resend if unsure

   <details><summary>Answer</summary>

   The relay delivers at least once, so the consumer must be idempotent. Recording the ID and the effect together means a crash can't leave one without the other.

   </details>

6. <!-- q: mcq id="03a87213" -->
   When should you move from a polling relay to change data capture (CDC), which reads the database's change log?

   - [ ] From the start: CDC is always better
   - [x] When the poll interval's delay or the polling query load actually hurts
   - [ ] Never: CDC can't read outbox rows
   - [ ] When you need more than one consumer

   <details><summary>Answer</summary>

   Polling is simple, works on any database and is easy to debug. CDC (such as Debezium) gives lower latency and no polling load, but it's another system to run and needs database-level permissions.

   </details>

## Check your understanding: worked problems
<!-- bite: 162d6eae-8a8e-4d2a-acf5-3737184d17eb -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="cc320608" answers="4;3" -->
   Fill in the gaps. An outbox holds three unpublished events, e1, e2 and e3. The relay publishes then marks each row. It publishes e1 and marks it, then publishes e2 and crashes before marking it. On restart it publishes every row not yet marked. The broker receives ___ messages in total, and an idempotent consumer applies ___ of them.

   <details><summary>Answer</summary>

   4 messages: e1, e2, then e2 again and e3 after the restart. The consumer recognises the second e2 by its `event_id` and applies 3.

   </details>

2. <!-- q: gap id="ee582c09" answers="e2;3" -->
   Fill in the gaps. A buggy relay marks each row as sent before publishing it. The outbox holds e1, e2, e3 and e4. It marks and publishes e1, then marks e2 and crashes before publishing it. On restart it marks and publishes every unmarked row. The event lost for good is ___, and the broker receives ___ messages.

   <details><summary>Answer</summary>

   e2 is lost: it was marked as sent, so the restarted relay skips it, but it was never published. The broker gets e1, e3 and e4: 3 messages.

   </details>

3. <!-- q: gap id="dd9a3e63" answers="5;3" -->
   Fill in the gaps. A service with no outbox saves each order, then publishes its event. Over five orders, the process crashes between the save and the publish on two of them. Afterwards the database holds ___ orders and the broker has received ___ events.

   <details><summary>Answer</summary>

   5 orders and 3 events. The two crashes each leave a lost event: an order saved but never announced, so never shipped.

   </details>

4. <!-- q: gap id="d68d0aee" answers="4;6;2" -->
   Fill in the gaps. A service with no outbox publishes each order's event, then saves the order. Six orders come in, and two of the saves fail a validation check. The database holds ___ orders, the broker has ___ events, and ___ of those events are phantoms.

   <details><summary>Answer</summary>

   4 orders, 6 events, 2 phantoms: events announcing orders that were never saved. With an outbox, the failed check would roll back the outbox row too, so no event would be sent.

   </details>

5. <!-- q: sketch id="ab27643e" -->
   Draw a message sequence diagram on paper with four lifelines: relay, database, broker and consumer. The outbox holds one unpublished row, a `PaymentCaptured` event with event ID `evt-p9`. The relay publishes it, the broker delivers it to the consumer, and then the relay crashes before marking the row as sent. It restarts and carries on as normal. The consumer is idempotent. Draw every message until the row is marked published, and write what the consumer does with each copy.

   <details><summary>Answer</summary>

   ![Answer sketch: the relay publishes PaymentCaptured evt-p9 and the consumer applies it; the relay crashes before marking it sent; on restart it selects unpublished rows, publishes evt-p9 again, and the consumer skips the second copy as a duplicate; finally the relay updates published_at.](../../images/sd-sketch-relay-duplicate.svg)

   What to check:
   - The event reaches the consumer twice, with the same event ID both times.
   - The consumer applies the first copy and skips the second, because it has seen `evt-p9`.
   - After the restart, the relay reads the outbox again before publishing; the row is still unpublished.
   - Marking the row published is the last message.

   </details>

## Practice — independent task
<!-- bite: 57e1a82a-a8d9-42a2-acb1-134978d2fb8e -->

**Extend the lab into a two-service flow.**

1. Add a `payments` consumer that, on `OrderPlaced`, writes a `charges` row **and** an `inbox` row (the `event_id`) in one SQLite transaction, and skips events already in the inbox.
2. Make it write a `PaymentSucceeded` event to its **own** outbox in the same transaction, and add a relay for it.
3. Write a test where every relay crashes once after publishing. Show that each order ends with exactly one charge and exactly one `PaymentSucceeded` applied downstream.

**Done when:** the crash-everywhere test passes, no step publishes to the broker from inside a request, and you can say — without notes — which crash causes a duplicate and which component absorbs it.

## Before moving on
<!-- bite: 59944868-4c23-4097-b9c9-0153fef85e97 -->

You can name both dual-write failures, implement an outbox and relay, and explain why the result is at-least-once delivery with idempotent consumers.

**Recap.** Never write to a database and a broker as two steps. Write the event to an outbox table in the same transaction as the change; a relay publishes it afterwards, then marks it sent. That's at-least-once delivery, so every event carries a stable ID and every consumer deduplicates on it.

**Next.** [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data and integration patterns]] — sagas, which chain these reliable local steps into multi-service workflows.

## Related
<!-- bite: d21e221c-0be0-4829-98fc-3919f1bc686d -->
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data and integration patterns]] — saga, CQRS, event sourcing
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|Modular monolith to services]] — at-least-once delivery and idempotent consumers
- [[concepts/02-design-patterns/03-behavioral-patterns/index|Behavioural patterns]] — the observer pattern this replaces at system scale
- [[databases/08-transactions-and-acid/index|Transactions and ACID]] — the guarantee the pattern is built on

## About this lesson
<!-- bite: 9fa4f595-5caf-400d-8bcf-60287a6df1bb -->

**Level:** Intermediate→Advanced. **Covers:** How to save something to your database **and** tell other systems about it, without ever doing one and not the other. The fix for the "dual write" problem, with a lab that crashes at the worst moment on purpose.

*Source: [reference] — the lab's behaviour was executed; production details (CDC tooling, relay locking) are from documentation, not from operating one.*
