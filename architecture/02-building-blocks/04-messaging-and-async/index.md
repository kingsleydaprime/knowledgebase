# Messaging & Async

> **[Intermediate]** · From the roadmap.sh system-design roadmap. How systems decouple and absorb load by *not* doing everything in the request path. This lesson covers what to keep synchronous and what to hand off, how a queue delivers a message at least once and what that does to your consumers, how a queue turns a traffic spike into a backlog instead of errors, the difference between a queue, a topic and a partitioned log, and back-pressure. The worked example moves the shop's order pipeline off the checkout request. The lab is a small in-memory broker, and it checks every number. Grounded in the real [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|RabbitMQ pipeline]].

## Before you start

You can already:

- Explain utilisation and why a server's queue grows without limit as it nears full → [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|scalability and performance]].
- Explain what makes an operation idempotent: doing it twice has the same effect as doing it once → [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID generation and idempotency]] (a skim is enough).
- Write async TypeScript with `await`, and run a test file with Node 26 (`node --test`).

After this lesson you will be able to:

1. Decide which work belongs in the request path and which should go to a queue, and say what the caller is told.
2. Trace a message through receive, acknowledgement, redelivery and the dead-letter queue, and explain why at-least-once delivery forces idempotent consumers.
3. Work out how deep a queue gets during a spike, how long the backlog lasts, and how long the unluckiest message waits.
4. Choose between a queue, a topic and a partitioned log, and explain why per-key order needs partitions.

**Study route:** sections 1–5 build the model. Stop at the predictions in sections 4, 6 and 8 and try them before reading on. Section 11 is the worked example and section 12 the lab. This week's design task is a **notification system**: do it before reading the worked example, which is deliberately about something else.

## The kid version

In a busy restaurant, the waiter doesn't stand in the kitchen while each meal is cooked. They pin the order ticket on a rail and go back to the tables. Cooks take tickets from the rail when they're free. In a rush, the rail fills up, but nobody is turned away at the door; the food just takes longer. If a cook drops a ticket half-made, it goes back on the rail for someone else. And the receipt printer gets its own copy of every ticket, so the till and the kitchen each see every order.

**Where the analogy stops working.** A cook who drops a ticket usually knows whether they already started the dish. A computer that crashes doesn't: the queue only knows that nobody said "done", so it hands the message out again, and the work may happen twice. Also, a real rail has room for maybe twenty tickets. A software queue can grow to millions, which is a problem of its own (section 9).

## 1. Why this exists

At checkout, the shop does five things: take the payment, reserve the stock, render a PDF invoice (about 200 ms), update the sales dashboards, and tell the warehouse. Done one after another inside the request, checkout takes as long as all five together, fails if any one of them fails, and during a sale is limited by the slowest. If the PDF service can do 100 invoices a second and 300 orders a second arrive, two in every three customers get an error, even though their payment would have gone through. The customer doesn't need the invoice before seeing "order confirmed". They need it in their inbox within a minute. That gap, between "needed now" and "needed soon", is what messaging uses.

## Terms used in messaging

1. **Synchronous**: A call is synchronous when the caller waits for the work to finish before carrying on.
2. **Asynchronous**: A call is asynchronous when the caller hands the work off and carries on at once; the work is done later, by someone else.
3. **Message**: This is a small, self-contained piece of data sent from one part of a system to another, such as "order 7 was placed".
4. **Producer**: This is also called a **publisher**. It's the code that sends messages.
5. **Consumer**: This is also called a **subscriber** or **worker**. It's the code that receives messages and does the work.
6. **Broker**: This is the service that stores messages between producers and consumers, such as RabbitMQ, Amazon SQS or Kafka.
7. **Queue**: This is a list of messages in which each message is given to one consumer.
8. **Topic**: This is a named channel that copies each message to every **subscription**. Each subscription is its own queue.
9. **Acknowledgement**: This is also called an **ack**. It's the consumer telling the broker "done, delete it".
10. **Visibility timeout**: This is how long a received message stays hidden from other consumers. If it isn't acknowledged in that time, the broker assumes the consumer died and delivers it again.
11. **At-least-once delivery**: This means every message is delivered, but some may be delivered more than once.
12. **Idempotent consumer**: This is a consumer that gets the same result whether it processes a message once or several times.
13. **DLQ (dead-letter queue)**: The letters stand for those words. It's where a message goes after failing too many times, so it stops blocking or wasting work and a person can look at it.
14. **Competing consumers**: This means several consumers reading the same queue, so they share the work and drain it faster.
15. **Load levelling**: This means using a queue to turn a burst of requests into a steady flow the workers can keep up with.
16. **Partition**: In a log such as Kafka, this is one of several ordered lists a topic is split into. Messages with the same key always go to the same partition.
17. **Offset**: This is a consumer group's position in a partition: the number of the next message it will read.
18. **Back-pressure**: This is a full queue slowing its producers down, by making them wait or refusing their messages, instead of growing without limit.

## 2. What stays in the request path

The rule: **work the caller needs before it can carry on stays synchronous; everything else can be a message.** For checkout:

- **Synchronous:** taking the payment and reserving the stock. The customer must know whether the order succeeded, and two customers mustn't buy the last kettle.
- **Asynchronous:** the invoice, the dashboards, the warehouse, the confirmation email. None of them changes what the customer is told right now.

The caller is then told what has actually happened: "order confirmed, invoice to follow", not "invoice sent". A video upload returns "processing"; a bulk import returns a job ID that can be checked later. This keeps the request fast, and it keeps it working when the invoice service is slow or down: the messages wait for it.

## 3. A queue, step by step

The broker in the lab works like Amazon SQS or a RabbitMQ queue with manual acknowledgements. Follow one message, with a visibility timeout of 30 seconds and a limit of three deliveries:

1. **Publish.** The producer sends "order 7". The broker stores it. The producer is done.
2. **Receive.** A consumer asks for a message and gets "order 7", delivery 1. The broker hides it for 30 seconds, so no other consumer takes it too.
3. **Ack.** The consumer renders the invoice and acknowledges. The broker deletes the message. That's the normal path.

If the consumer crashes after step 2, nobody acknowledges. After 30 seconds the message becomes visible again and the next consumer gets it as delivery 2. A message that fails every time, a **poison message** such as an order with a corrupt address, would be retried forever, so after the third delivery the broker moves it to the dead-letter queue instead. Someone then looks at it, fixes the cause, and sends it back.

The visibility timeout must be longer than the work normally takes. If invoices take 40 seconds and the timeout is 30, every invoice is delivered twice while the first consumer is still working on it.

## 4. At least once means sometimes twice

The broker can't tell a consumer that crashed *before* doing the work from one that crashed *after* doing it but *before* acknowledging. Both look like "no ack". So it redelivers, and in the second case the work happens twice.

**Predict before reading on.** A payment consumer charges a card, then crashes before acknowledging. What happens next, and how would you stop the customer paying twice?

<details>
<summary>After your prediction</summary>

The message reappears after the visibility timeout, the next consumer charges the card again, and the customer pays twice. The lab's test `at least once means sometimes twice` shows exactly this: two charges.

The fix is an **idempotent consumer**: it records the message ID of everything it has processed, and skips any ID it has seen. For this to be safe, the record and the effect must be saved together, in one database transaction, or with the payment provider's own idempotency key. Otherwise a crash between "charged" and "recorded" brings the duplicate back. With the record in place, the lab's second delivery returns "duplicate" and the card is charged once.

</details>

Why not just deliver exactly once? Because between a broker and a consumer that can crash at any instant, it can't be guaranteed: some message is always either possibly lost or possibly repeated. Systems advertised as "exactly once", such as Kafka transactions, achieve it only within their own system, by making the processing and the record of it one atomic step. The practical answer everywhere is **at-least-once delivery plus idempotent consumers**: effectively once.

## 5. Load levelling: a spike becomes a backlog

In words: while messages arrive faster than the consumers can handle them, the queue grows by the difference each second. Once arrivals drop below capacity, it shrinks by the difference. The longest wait is roughly how long the backlog takes to work through.

With $\lambda$ for arrivals a second, $\mu$ for the consumers' total capacity a second, and a spike lasting $T$ seconds:

$$\text{peak depth} = (\lambda_{\text{spike}} - \mu)\,T \qquad \text{time to clear after the spike} = \frac{\text{peak depth}}{\mu - \lambda_{\text{after}}}$$

**Predict before reading on.** The shop gets 300 orders a second for 10 seconds, then 20 a second. Two invoice workers do 50 a second each. A synchronous invoice service would turn away anything over 100 a second. How many customers would get an error? Through a queue, how deep does it get, when is the backlog cleared, and how long does the unluckiest order wait for its invoice?

<details>
<summary>After your prediction</summary>

Synchronously, 200 a second are turned away for 10 seconds: **2,000 errors**, half the spike. Through the queue, nobody is turned away. It grows by 300 − 100 = 200 a second to a **peak of 2,000**, then shrinks by 100 − 20 = 80 a second, so it takes 25 more seconds to clear: the backlog is gone **35 seconds in**. The last order of the spike waits behind everything before it, about **20 seconds**. With four workers (competing consumers), the peak halves to 1,000, the backlog is gone 16 seconds in, and the longest wait is 5 seconds. The lab's `levelLoad` checks all of these second by second.

</details>

This is week 1's queueing lesson again: a queue doesn't create capacity. It trades errors for waiting. If arrivals stay above capacity, the backlog grows forever, so watch the **queue depth** and the **age of the oldest message**, and add consumers when either keeps rising.

## 6. Queues, topics and fan-out

Two shapes of delivery:

- **Point-to-point (a queue):** each message goes to **one** consumer. That's how work is shared out: two invoice workers on one queue split the invoices between them.
- **Publish–subscribe (a topic):** each message is copied to **every** subscription. One "order placed" event reaches invoices, analytics and the warehouse, and each handles it independently. A new team that wants the event adds a subscription; the producer doesn't change.

Most brokers combine them: a topic fans out to subscriptions, and each subscription is a queue that its own consumers compete on. That's SNS feeding SQS queues, or a RabbitMQ fanout exchange bound to several queues.

**Predict before reading on.** The refunds team creates its subscription an hour after the first refund events were published. What do they get?

<details>
<summary>After your prediction</summary>

Nothing from before their subscription existed. A topic copies messages into the subscriptions that exist *at publish time*; with none, the message is kept nowhere. The lab's test publishes to `refunds` with no subscribers and checks that nothing was stored. If you need to read history, you need a log that keeps messages (next section), not a queue that deletes them.

</details>

## 7. Order, and the partitioned log

A queue roughly keeps the order messages arrived in, until something goes wrong. In the lab, order 7's "created", "paid" and "shipped" events go into one queue. The consumer handles "created", then fails on "paid". While "paid" is hidden, waiting to be redelivered, "shipped" is free, so it's processed next. The result: **shipped before paid**. With several competing consumers, order isn't kept even without failures, because a fast consumer can finish a later message first.

**Kafka's** model fixes this differently. A topic is a **log** split into **partitions**. A message's key, such as the order ID, decides its partition, so all of order 7's events go into the same one, in the order sent. Each partition is read by one consumer in a group at a time, in order, and the consumer's position is an **offset** it commits after each message. A message that fails isn't committed, so the next poll returns it again: the partition waits for it, and "shipped" can't overtake "paid".

Two more consequences:

- **Messages are kept, not deleted when read.** Each consumer group has its own offsets, so analytics and shipping read the same log independently, and a new group can start at offset 0 and replay everything. That fixes section 6's refunds problem.
- **Order costs throughput and blocks on poison messages.** One partition is one consumer at a time, so a topic can only be read as fast as its partitions allow; you choose the partition count up front. A message that always fails blocks its whole partition, so you still need a retry limit and a dead-letter topic.

## 8. Back-pressure: what a full queue should do

A queue that can grow forever hides a problem until the broker runs out of memory or disk. A **bounded** queue has three choices when it's full:

1. **Make the producer wait.** The producer slows to the consumer's pace. That's right inside a program, such as a file reader feeding a slow database writer.
2. **Refuse the message.** The producer gets an error at once and can tell its caller "busy, try later" with HTTP 503 or 429. That's right at the edge of a system, where waiting would only move the problem.
3. **Drop the oldest.** That's right for data where only the latest matters, such as live positions or metrics.

The lab's `BoundedQueue` does the first two. With room for 3, the fourth `tryPut` is refused. A producer using `put` stops after three items and continues one item at a time as the consumer takes them, so the queue never holds more than three.

**Predict before reading on.** A producer puts 5 items into a `BoundedQueue(3)` with `put`, and nothing is taken. How many puts finish?

<details>
<summary>After your prediction</summary>

Three. The fourth `put` waits for space, and so does the producer, until something is taken. Each `take` lets exactly one more `put` through. The lab's test checks the events: put 1, put 2, put 3, then took 1, then put 4.

</details>

## 9. Event-driven architecture, and what it costs

Taken further, services stop calling each other and instead **publish what happened** and **react to what others publish**. A new consumer just subscribes, with no change to the producer, so services are decoupled and scale independently. The costs are real:

- **The flow is implicit.** No single piece of code shows what happens when an order is placed; you have to find every subscriber. Tracing across services ([[devops/10-observability/01-observability-fundamentals/index|observability]]) becomes essential.
- **Everything downstream is eventually consistent.** The dashboard lags the orders by seconds, or by minutes during a spike.
- **The broker is now critical infrastructure.** It needs replication and monitoring like a database.
- **Publishing and saving must agree.** If checkout saves the order and then crashes before publishing, the warehouse never hears of it. If it publishes and then the save fails, the warehouse ships an order that doesn't exist. The [[architecture/03-architectural-patterns/05-transactional-outbox/index|transactional outbox]] (next week) solves this by saving the message in the same transaction as the order.

Event sourcing and CQRS take the idea further still; they're in [[architecture/03-architectural-patterns/03-data-and-integration-patterns|data and integration patterns]]. Use asynchrony where the decoupling or buffering pays. Don't use it for everything, or you've turned a simple request into a distributed debugging problem.

## 10. Choosing a broker

- **RabbitMQ:** a queue broker with flexible routing (exchanges, bindings). Messages are deleted once acknowledged. Good for task distribution and routing.
- **Amazon SQS** (with **SNS** for fan-out): the same model as a managed service, with nothing to run.
- **Kafka** (or Redpanda, or Amazon Kinesis): a partitioned, replicated log. Messages are kept for days or forever; order per key; replay. Good for event streams that many teams read, and for very high volume.
- **Redis Streams** and **Postgres** (`SELECT … FOR UPDATE SKIP LOCKED`) are enough for modest volumes, with no new system to run.

## 11. Worked example: taking the shop's order pipeline off the checkout path

**Step 1: split the work.** Checkout keeps the payment and the stock reservation, in one database transaction with the order. In the same transaction it writes an "order placed" message to an outbox table, which a relay publishes to the `orders` topic. The customer sees "order confirmed" as soon as the transaction commits.

**Step 2: subscriptions.** The `orders` topic has three subscriptions: `invoices`, `analytics` and `warehouse`. Each is its own queue with its own consumers, and a failure in one doesn't hold up the others.

**Step 3: make every consumer idempotent.** The invoice consumer keys each invoice by order ID with a unique constraint, so a duplicate delivery hits the constraint and is skipped. The warehouse consumer sends the order ID to the warehouse's API as an idempotency key. Analytics counts with an upsert keyed by message ID.

**Step 4: size it.** The sale spike is 300 orders a second for 10 seconds. With two invoice workers, section 5 says the backlog peaks at 2,000 and invoices are up to 20 seconds late, and nobody is turned away. That's acceptable for an invoice. The alert fires if the oldest invoice message is over 2 minutes old.

**Step 5: failures and order.** The visibility timeout is 60 seconds, three times the slowest invoice. After 5 deliveries a message goes to the dead-letter queue, which pages someone if it's not empty. The warehouse needs each order's events in order (paid before cancelled), so the `warehouse` subscription reads a log partitioned by order ID rather than a plain queue.

## 12. Runnable example: a broker you can watch

`broker.ts` has the queue-and-topic broker with visibility timeouts and a dead-letter queue, an idempotency wrapper, a partitioned log with consumer-group offsets, the load-levelling simulation from section 5, and a bounded queue. `broker.test.ts` plays out every scenario in this lesson.

```ts
// broker.ts — a small in-memory message broker, to watch what real ones do: queues where each message goes to one
// consumer, topics that copy each message to every subscription, redelivery when a consumer doesn't acknowledge,
// a dead-letter queue, a partitioned log that keeps each key in order, and a bounded queue that pushes back.
// Time is a clock passed in, so tests move it forward instead of waiting.

export interface Delivery {
  id: string;
  body: string;
  key?: string;
  attempt: number; // 1 the first time, 2 after one redelivery, ...
}

interface Stored {
  id: string;
  body: string;
  key?: string;
  attempts: number;
  visibleAt: number; // hidden from other consumers until then, while one consumer works on it
}

/**
 * Queues and topics. A subscription is a queue: consumers of the same subscription compete for its messages.
 * Publishing to a topic copies the message into every subscription, so each one sees every message.
 * Delivery is at least once: a message that isn't acknowledged within `visibilityMs` is delivered again,
 * and after `maxAttempts` deliveries it's moved to the subscription's dead-letter queue.
 */
export class Broker {
  #now: () => number;
  #visibilityMs: number;
  #maxAttempts: number;
  #subscribers = new Map<string, string[]>(); // topic → subscription names
  #queues = new Map<string, Stored[]>(); // subscription → messages, oldest first
  #dead = new Map<string, Stored[]>();
  #nextId = 1;

  constructor(options: { now: () => number; visibilityMs: number; maxAttempts: number }) {
    this.#now = options.now;
    this.#visibilityMs = options.visibilityMs;
    this.#maxAttempts = options.maxAttempts;
  }

  subscribe(topic: string, subscription: string): void {
    this.#subscribers.set(topic, [...(this.#subscribers.get(topic) ?? []), subscription]);
    this.#queues.set(subscription, []);
    this.#dead.set(subscription, []);
  }

  /** Copies the message into every subscription. With no subscribers, nobody keeps it: it's gone. */
  publish(topic: string, body: string, key?: string): string {
    const id = `m${this.#nextId++}`;
    for (const s of this.#subscribers.get(topic) ?? []) {
      this.#queues.get(s)!.push({ id, body, key, attempts: 0, visibleAt: 0 });
    }
    return id;
  }

  /** The oldest message no other consumer is working on, hidden for `visibilityMs` until it's acknowledged. */
  receive(subscription: string): Delivery | undefined {
    const queue = this.#queues.get(subscription)!;
    for (let i = 0; i < queue.length; i++) {
      const m = queue[i];
      if (m.visibleAt > this.#now()) continue; // a consumer has it
      if (m.attempts >= this.#maxAttempts) {
        this.#dead.get(subscription)!.push(...queue.splice(i, 1)); // poison: stop retrying it
        i--;
        continue;
      }
      m.attempts++;
      m.visibleAt = this.#now() + this.#visibilityMs;
      return { id: m.id, body: m.body, key: m.key, attempt: m.attempts };
    }
    return undefined;
  }

  /** Done: remove it for good. A consumer that crashes before this gets the message delivered again. */
  ack(subscription: string, id: string): void {
    const queue = this.#queues.get(subscription)!;
    const i = queue.findIndex((m) => m.id === id);
    if (i >= 0) queue.splice(i, 1);
  }

  depth(subscription: string): number {
    return this.#queues.get(subscription)!.length;
  }

  deadLetters(subscription: string): string[] {
    return this.#dead.get(subscription)!.map((m) => m.body);
  }
}

/**
 * Makes a handler safe to run twice for the same message: it remembers which message IDs it has processed.
 * In a real system the "seen" record and the handler's effect are written in one database transaction.
 */
export function idempotent(handle: (body: string) => void, seen: Set<string>): (d: Delivery) => "processed" | "duplicate" {
  return (d) => {
    if (seen.has(d.id)) return "duplicate";
    handle(d.body);
    seen.add(d.id);
    return "processed";
  };
}

/** FNV-1a with a final mix: the same stable hash as the load-balancing lab, so a key always picks the same partition. */
export function partitionFor(key: string, partitions: number): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < key.length; i++) h = Math.imul(h ^ key.charCodeAt(i), 0x01000193) >>> 0;
  h = Math.imul(h ^ (h >>> 16), 0x85ebca6b) >>> 0;
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35) >>> 0;
  return ((h ^ (h >>> 16)) >>> 0) % partitions;
}

/**
 * A log split into partitions, like Kafka. Messages are kept, not removed when read. Each consumer group has its
 * own position (offset) in each partition, so groups read independently and a new group can replay from the start.
 * A message with a key always goes to the same partition, so one key's messages are read in the order sent.
 */
export class PartitionedLog {
  #partitions: string[][];
  #offsets = new Map<string, number[]>(); // group → next offset to read, per partition

  constructor(partitions: number) {
    this.#partitions = Array.from({ length: partitions }, () => []);
  }

  append(key: string, body: string): number {
    const p = partitionFor(key, this.#partitions.length);
    this.#partitions[p].push(body);
    return p;
  }

  /** The next message for this group in this partition, or undefined at the end. Reading doesn't move the offset. */
  poll(group: string, partition: number): string | undefined {
    return this.#partitions[partition][this.#offsetsFor(group)[partition]];
  }

  /** Moves past the message just processed. Until then, poll keeps returning it: the partition waits for it. */
  commit(group: string, partition: number): void {
    this.#offsetsFor(group)[partition]++;
  }

  #offsetsFor(group: string): number[] {
    if (!this.#offsets.has(group)) this.#offsets.set(group, this.#partitions.map(() => 0)); // a new group starts at the beginning
    return this.#offsets.get(group)!;
  }
}

/**
 * A burst of requests, second by second, against a fixed capacity. Synchronously, whatever doesn't fit in a second
 * is turned away. Through a queue, it waits and is worked through in arrival order. Returns both.
 */
export function levelLoad(arrivals: readonly number[], perSecond: number) {
  let served = 0;
  let rejected = 0;
  for (const a of arrivals) {
    served += Math.min(a, perSecond);
    rejected += Math.max(0, a - perSecond);
  }

  const waiting: { second: number; count: number }[] = []; // the queue, in arrival order
  let depth = 0;
  let peakDepth = 0;
  let maxWaitSeconds = 0;
  let clearedAfterSeconds = 0; // the end of the last second that finished with a backlog
  for (let second = 0; second < arrivals.length || depth > 0; second++) {
    const a = arrivals[second] ?? 0;
    if (a > 0) waiting.push({ second, count: a });
    depth += a;
    let capacity = perSecond;
    while (capacity > 0 && waiting.length > 0) {
      const oldest = waiting[0];
      const n = Math.min(capacity, oldest.count);
      oldest.count -= n;
      capacity -= n;
      depth -= n;
      maxWaitSeconds = Math.max(maxWaitSeconds, second - oldest.second);
      if (oldest.count === 0) waiting.shift();
    }
    peakDepth = Math.max(peakDepth, depth);
    if (depth > 0) clearedAfterSeconds = second + 2; // still waiting at the end of this second, so clear by the next
  }
  return { sync: { served, rejected }, queued: { peakDepth, clearedAfterSeconds, maxWaitSeconds } };
}

/**
 * A queue with a size limit. When it's full, `tryPut` says no at once and `put` waits for space: the producer is
 * slowed to the consumer's pace (back-pressure) instead of the queue growing without limit.
 */
export class BoundedQueue<T> {
  #items: T[] = [];
  #capacity: number;
  #takers: ((item: T) => void)[] = [];
  #putters: (() => void)[] = [];

  constructor(capacity: number) {
    this.#capacity = capacity;
  }

  get size(): number {
    return this.#items.length;
  }

  tryPut(item: T): boolean {
    const taker = this.#takers.shift();
    if (taker) {
      taker(item); // someone is waiting: hand it straight over
      return true;
    }
    if (this.#items.length >= this.#capacity) return false;
    this.#items.push(item);
    return true;
  }

  async put(item: T): Promise<void> {
    while (!this.tryPut(item)) await new Promise<void>((resolve) => this.#putters.push(resolve));
  }

  async take(): Promise<T> {
    if (this.#items.length > 0) {
      const item = this.#items.shift()!;
      this.#putters.shift()?.(); // there's room now: wake one waiting producer
      return item;
    }
    return new Promise<T>((resolve) => this.#takers.push(resolve));
  }
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { BoundedQueue, Broker, idempotent, levelLoad, partitionFor, PartitionedLog } from "./broker.ts";

function broker(clock = { now: 0 }) {
  return new Broker({ now: () => clock.now, visibilityMs: 30_000, maxAttempts: 3 });
}

test("a queue gives each message to one consumer; a topic copies it to every subscription", () => {
  const b = broker();
  b.subscribe("orders", "invoices");
  b.subscribe("orders", "analytics");
  b.publish("orders", "order 1");
  b.publish("orders", "order 2");
  // Two invoice workers share the invoices subscription: they split the messages.
  assert.equal(b.receive("invoices")?.body, "order 1");
  assert.equal(b.receive("invoices")?.body, "order 2");
  assert.equal(b.receive("invoices"), undefined); // both are taken, though not yet acknowledged
  // Analytics has its own copy of everything.
  assert.deepEqual([b.receive("analytics")?.body, b.receive("analytics")?.body], ["order 1", "order 2"]);
  // A topic with no subscribers keeps nothing.
  b.publish("refunds", "refund 1");
  assert.equal(b.depth("invoices") + b.depth("analytics"), 4);
});

test("a message that isn't acknowledged comes back, and after three tries goes to the dead-letter queue", () => {
  const clock = { now: 0 };
  const b = broker(clock);
  b.subscribe("orders", "invoices");
  b.publish("orders", "order 1");
  const first = b.receive("invoices")!;
  assert.equal(first.attempt, 1);
  assert.equal(b.receive("invoices"), undefined); // hidden while a consumer works on it
  clock.now = 30_000; // no ack in time: the consumer is presumed dead
  assert.equal(b.receive("invoices")?.attempt, 2);
  clock.now = 60_000;
  assert.equal(b.receive("invoices")?.attempt, 3);
  clock.now = 90_000;
  assert.equal(b.receive("invoices"), undefined); // three tries are enough
  assert.deepEqual(b.deadLetters("invoices"), ["order 1"]);
  assert.equal(b.depth("invoices"), 0);
});

test("at least once means sometimes twice: a crash before the ack charges twice, unless the handler is idempotent", () => {
  for (const safe of [false, true]) {
    const clock = { now: 0 };
    const b = broker(clock);
    b.subscribe("orders", "payments");
    b.publish("orders", "charge £40 for order 1");
    let charges = 0;
    const charge = () => void charges++;
    const handle = safe ? idempotent(charge, new Set()) : (d: { body: string }) => charge();
    handle(b.receive("payments")!); // charged, then the consumer crashes before acknowledging
    clock.now = 30_000;
    const again = b.receive("payments")!; // so the broker delivers it again
    handle(again);
    b.ack("payments", again.id);
    assert.equal(charges, safe ? 1 : 2);
  }
});

test("a queue absorbs a sale spike that a synchronous service would turn away", () => {
  // 10 seconds at 300 orders a second, then 50 seconds at 20. Two workers at 50 a second each.
  const spike = [...Array(10).fill(300), ...Array(50).fill(20)];
  const two = levelLoad(spike, 100);
  assert.deepEqual(two.sync, { served: 2_000, rejected: 2_000 }); // half the spike gets errors
  assert.deepEqual(two.queued, { peakDepth: 2_000, clearedAfterSeconds: 35, maxWaitSeconds: 20 });
  // Nobody is turned away. The backlog is gone 35 seconds in, but the last spike orders waited 20 seconds.
  const four = levelLoad(spike, 200); // competing consumers: twice the workers
  assert.deepEqual(four.queued, { peakDepth: 1_000, clearedAfterSeconds: 16, maxWaitSeconds: 5 });
});

test("redelivery reorders one key's events; a partition keeps them in order, and a new group replays them", () => {
  const clock = { now: 0 };
  const b = broker(clock);
  b.subscribe("orders", "shipping");
  for (const e of ["created", "paid", "shipped"]) b.publish("orders", `order 7 ${e}`, "order-7");
  const seen: string[] = [];
  const created = b.receive("shipping")!;
  seen.push(created.body);
  b.ack("shipping", created.id);
  b.receive("shipping"); // "paid": the handler fails, so it isn't acknowledged
  const shipped = b.receive("shipping")!; // meanwhile the next message is free to go
  seen.push(shipped.body);
  b.ack("shipping", shipped.id);
  clock.now = 30_000;
  const paid = b.receive("shipping")!;
  seen.push(paid.body);
  assert.deepEqual(seen, ["order 7 created", "order 7 shipped", "order 7 paid"]); // shipped before paid

  const log = new PartitionedLog(4);
  for (const e of ["created", "paid", "shipped"]) log.append("order-7", `order 7 ${e}`);
  const p = partitionFor("order-7", 4);
  const inOrder: string[] = [];
  let failedOnce = false;
  for (let m = log.poll("shipping", p); m !== undefined; m = log.poll("shipping", p)) {
    if (m.endsWith("paid") && !failedOnce) {
      failedOnce = true; // fails once: no commit, so the partition waits and the same message comes back
      continue;
    }
    inOrder.push(m);
    log.commit("shipping", p);
  }
  assert.deepEqual(inOrder, ["order 7 created", "order 7 paid", "order 7 shipped"]);
  assert.equal(log.poll("analytics", p), "order 7 created"); // a group that has never read starts at the beginning
});

test("a key always lands in the same partition", () => {
  assert.equal(partitionFor("order-7", 4), partitionFor("order-7", 4));
  const counts = [0, 0, 0, 0];
  for (let i = 0; i < 10_000; i++) counts[partitionFor(`order-${i}`, 4)]++;
  assert.ok(counts.every((n) => Math.abs(n - 2_500) < 200), `${counts}`); // and keys spread evenly
});

test("a bounded queue pushes back: a fast producer waits for a slow consumer", async () => {
  const q = new BoundedQueue<number>(3);
  assert.deepEqual([1, 2, 3, 4].map((n) => q.tryPut(n)), [true, true, true, false]); // full: the fourth is refused
  assert.deepEqual([await q.take(), await q.take(), await q.take()], [1, 2, 3]);

  const events: string[] = [];
  const producer = (async () => {
    for (let n = 1; n <= 5; n++) {
      await q.put(n);
      events.push(`put ${n}`);
    }
  })();
  await new Promise((resolve) => setImmediate(resolve)); // let the producer run until it's blocked
  assert.deepEqual(events, ["put 1", "put 2", "put 3"]); // it stopped at the limit
  events.push(`took ${await q.take()}`);
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(events.slice(3), ["took 1", "put 4"]); // one out, one more in
  for (let i = 0; i < 4; i++) events.push(`took ${await q.take()}`);
  await producer;
  assert.equal(events.filter((e) => e.startsWith("put")).length, 5); // all five got in, never more than 3 waiting
  assert.equal(q.size, 0);
});
```

**Lab:** the code is in [`architecture/02-building-blocks/04-messaging-and-async/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/04-messaging-and-async/labs/typescript). From the vault root, `python3 labs/run.py messaging-and-async/typescript` runs the tests and checks this page still shows the same code. Inside the folder, `node --test` runs the tests alone. Expect seven passing tests in well under a second.

## Common pitfalls

1. **Assuming exactly once.** Every consumer will one day see a message twice. Make it idempotent from the start.
2. **Recording "processed" separately from the effect.** A crash between them brings the duplicate back. Save both in one transaction.
3. **A visibility timeout shorter than the work.** Every slow message is processed twice, in parallel.
4. **No dead-letter queue.** One poison message is retried forever, wasting a worker, or in a partitioned log, blocking a partition.
5. **Watching only throughput.** A queue hides overload as waiting. Alert on depth and on the age of the oldest message.
6. **Expecting order from competing consumers.** Use one partition per key when order matters, and accept its throughput limit.
7. **Publishing outside the database transaction.** The message and the data disagree after a crash. Use the outbox.
8. **Making everything asynchronous.** A user who needs an answer now should get one now, and a simple flow split over four services is harder to debug.

## Check your understanding

1. Why can't a broker guarantee exactly-once delivery to a consumer that can crash?
2. A consumer takes up to 45 seconds per message, and the visibility timeout is 30. What happens?
3. 500 messages a second arrive for 20 seconds, then 50 a second. Consumers handle 250 a second. What's the peak depth, and when is the backlog gone?
4. When would you use a topic rather than a queue? When a partitioned log rather than a topic?
5. Why does a failing message in a Kafka partition hold up the messages behind it, while in SQS it doesn't?
6. A bounded queue is full. Should the producer wait or get an error? Give one case for each.

<details>
<summary>Answers — after your attempt</summary>

1. When a consumer stops without acknowledging, the broker can't know whether the work was done. It must either redeliver (maybe twice) or not (maybe never). Exactly-once needs the processing and its record to be one atomic step, which a broker alone can't provide.
2. Messages that take over 30 seconds become visible again while still being worked on, and a second consumer starts on them too. Each slow message is processed twice, and under load more consumers are busy with duplicates. Raise the timeout above the slowest normal time, or extend it while working.
3. It grows by 250 a second for 20 seconds: 5,000. Then it shrinks by 200 a second, so 25 more seconds: gone about 45 seconds in.
4. A topic when several independent consumers each need every message, such as invoices and analytics both needing "order placed". A partitioned log when you also need per-key order, replay of history, or many consumer groups reading at their own pace.
5. A Kafka consumer reads a partition in order and only moves on by committing the offset, so an uncommitted message is returned again and everything behind it waits. SQS hides a failed message and hands out the next ones, so others continue, which is why SQS doesn't keep order.
6. Wait inside a program, where the producer can slow down without a user noticing, such as a file reader feeding a slow writer. Error at a system's edge, where a waiting producer is a waiting user, such as an API that should answer 503 so the client can retry later.

</details>

## Practice — independent task

**Add retries with back-off to the broker.**

1. Copy `broker.ts` and `broker.test.ts` to a scratch folder.
2. Add `nack(subscription, id)`: the consumer reports a failure, and the message becomes visible again after a delay that doubles each attempt: 1 second, then 2, then 4.
3. Keep the dead-letter rule: after `maxAttempts` deliveries, the message goes to the dead-letter queue.
4. Test the exact times at which a failing message is redelivered, and that a message that succeeds on its second attempt never reaches the dead-letter queue.

**A smaller step first:** in the load-levelling test, change the workers' capacity from 100 to 150. Predict the peak depth, when the backlog clears, and the longest wait before running it.

**Done when:** your new tests and the seven existing ones pass, and you can say why retrying immediately, with no delay, is a bad idea when a dependency is down.

<details>
<summary>Hints — after your attempt</summary>

- Set `visibleAt = now + 1000 * 2 ** (attempts - 1)` in `nack`. Real systems add random jitter too, so retries from many consumers don't arrive at the same instant.
- The smaller step: the queue grows by 150 a second to a peak of 1,500, then shrinks by 130 a second, which takes about 12 seconds, so it clears about 22 seconds in. The last spike order waits about 10 seconds (3,000 orders at 150 a second).
- Retrying at once against a dependency that's down just adds load to it and burns through the attempts in milliseconds. [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience patterns]] covers back-off.

</details>

## Tradeoffs, limits and extensions

- **The lab's broker lives in memory.** Real brokers write messages to disk and copy them to other machines before acknowledging the producer. That durability, and its cost in latency, is most of what you pay a broker for.
- **Message size.** Brokers limit message size: about 1 MB by default for both SQS and Kafka. Put large payloads in object storage and send a reference.
- **Schema changes.** A message format is an API that many consumers depend on. Add fields, don't rename or remove them, and version the schema.
- **Ordering across keys** is not kept even by a partitioned log, only within a key. Design consumers so that doesn't matter.

## Before moving on

You can decide what stays in the request path, trace a message through acknowledgement, redelivery and the dead-letter queue, make a consumer idempotent, size a queue for a spike, and choose between a queue, a topic and a partitioned log.

**Recap.** Keep in the request path only what the caller needs now; send the rest as messages. Delivery is at least once: an unacknowledged message comes back after the visibility timeout, and a poison message goes to the dead-letter queue, so consumers must be idempotent, with the "seen" record saved alongside the effect. A queue turns a spike into a backlog: it grows by arrivals minus capacity and drains by capacity minus arrivals, so watch its depth and its oldest message. A queue gives each message to one consumer, a topic copies it to every subscription, and a partitioned log keeps per-key order and history at the cost of throughput per partition. Bound your queues and decide whether a full one blocks or refuses.

**Next.** [[architecture/02-building-blocks/05-communication/index|Communication]]: the synchronous side, meaning how services call each other with REST, GraphQL and gRPC, and what each costs.

## Related

- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ (Java)]]: this built in real code (DLQs, back-pressure, competing consumers)
- [[architecture/03-architectural-patterns/05-transactional-outbox/index|Transactional outbox]]: publishing a message and saving data together
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data and integration patterns]]: event sourcing, CQRS, sagas
- [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|Scalability]]: the queueing arithmetic behind load levelling

## Seen in the wild

- [[projects/record-id-generator-java/learning/05-rabbitmq-messaging|record-id-generator]]: the queue running for real
- [[projects/socioboom/interview/02-queues-and-deployment|socioboom]]: background jobs for social publishing
- [[projects/nextvibe/learning/backend/05-realtime|nextvibe]]: real-time delivery, the push-based sibling
