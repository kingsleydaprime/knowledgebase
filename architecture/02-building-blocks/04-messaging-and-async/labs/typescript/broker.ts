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
