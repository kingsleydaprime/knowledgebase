# Messaging & Async in Other Languages

> **[Intermediate]** · A companion to [[architecture/02-building-blocks/04-messaging-and-async/index|messaging and async]], which builds a small broker with redelivery and a dead-letter queue, an idempotent consumer, a partitioned log, the load-levelling arithmetic, and a bounded queue that pushes back. This page does the same in Python, Go, Java, Rust and C#, with the same numbers in every language. The broker itself is bookkeeping and translates directly. The bounded queue is where languages differ, because every language has its own, with its own way to wait and its own way to say "full". So each lab uses the language's own primitive instead of a hand-written one, and tests a blocked producer without relying on timing.

## Before you start

You can already:

- Trace a message through receive, acknowledgement, redelivery and the dead-letter queue, and explain back-pressure → [[architecture/02-building-blocks/04-messaging-and-async/index|the main lesson]].
- Start concurrent work in your language: tasks, goroutines or threads.

After this lesson you will be able to:

1. Name your language's bounded queue, its "try" operation that refuses when full, and its operation that waits.
2. Test that a producer is blocked by a full queue, without a sleep that makes the test flaky.
3. Say why two producers in different languages can send the same Kafka key to different partitions, and how to stop it.

## The kid version

Five schools each have a tray for homework with room for three books. In one, a child who finds the tray full is told "no" and keeps the book. In another, the child waits by the tray until a teacher takes a book out. In a third, the oldest book in the tray is pushed out onto the floor to make room. The trays look the same, but what happens when they're full is the whole difference.

**Where the analogy stops working.** You can see a child waiting by a tray. A program can't easily see that another thread is waiting, which is why testing "the producer is blocked" takes a different trick in each language.

## 1. The tools, by ecosystem

| Language | Bounded in-process queue | Refuses when full | Waits when full | RabbitMQ / Kafka / SQS clients |
|---|---|---|---|---|
| TypeScript | written by hand (the main lesson) | `tryPut` | `await put` | amqplib, kafkajs, AWS SDK |
| Python | `asyncio.Queue(maxsize)`; `queue.Queue` for threads | `put_nowait` raises `QueueFull` | `await put` | pika, aio-pika, confluent-kafka, boto3 |
| Go | a **buffered channel** | `select` with `default` | `q <- item` | amqp091-go, franz-go, confluent-kafka-go, AWS SDK |
| Java | `ArrayBlockingQueue` | `offer` returns `false` | `put` | RabbitMQ client, Spring AMQP, kafka-clients (official), AWS SDK |
| Rust | `std::sync::mpsc::sync_channel`; tokio `mpsc::channel` | `try_send` returns `Err(Full)` | `send` | lapin, rdkafka, aws-sdk-sqs |
| C# | `Channel.CreateBounded` | `TryWrite` returns `false` | `await WriteAsync` | RabbitMQ.Client, Confluent.Kafka, AWS SDK |

C# is the only one with the main lesson's third choice built in: `BoundedChannelFullMode` can be `Wait`, `DropOldest`, `DropNewest` or `DropWrite`. C and C++ have no standard bounded queue (you'd build one from a mutex and condition variables, as the [[architecture/03-architectural-patterns/02-resilience-patterns/in-other-languages|resilience companion]] does) and are rarely where message consumers are written, so they have no lab here.

## 2. What changes between languages

### The broker translates directly

`Broker`, `PartitionedLog` and `levelLoad` are maps, lists and counters, and look much the same in every language. The differences are small and typical:

- **Absence.** `receive` returns `undefined` in TypeScript, `None` in Python, `(Delivery, bool)` in Go, `Optional<Delivery>` in Java, `Option<Delivery>` in Rust and `Delivery?` in C#.
- **Removing while iterating.** Java uses the iterator's `remove`, Go `slices.Delete`, Rust `Vec::remove`, and C# `RemoveAt(i--)`.
- **The injected clock.** Rust needs `Rc<Cell<u64>>`, because the broker owns a closure that reads the time while the test also changes it, and Rust allows that shared mutation only through a `Cell`. Go passes a pointer, and Java an `AtomicLong`'s method reference.

### Changing a count from inside a function value

The idempotency test counts charges from inside a callback. JavaScript and Python closures can change outside variables freely (Python with a list or `nonlocal`). Java lambdas can only capture variables that never change, so the count is an `AtomicInteger`. Rust's `idempotent` takes `&mut HashSet` for as long as the returned closure lives, so the borrow checker makes sure nothing else touches `seen` meanwhile, and the charge count is a `Cell`.

### Testing a producer that's blocked

The main lesson's test checks that a producer of five items into a queue of three stops after three, and gets exactly one more in per item taken. Each language proves "it stopped" differently:

- **Python's** asyncio is single-threaded: a few `await asyncio.sleep(0)` steps let the producer run until it's waiting on `put`.
- **Go's** `testing/synctest` has `synctest.Wait()`, which returns once every goroutine in the test's "bubble" is blocked. One catch, found while writing this lab: **the channel must be made inside the bubble.** A goroutine blocked on a channel made outside it doesn't count as durably blocked, so `Wait` never returns and the test hangs.
- **Java** waits until the put count is 3 *and* the producer thread's state is `WAITING`.
- **Rust** and **C#** wait until the put count reaches 3. That's not a timing gamble: the count can't pass 3 until something is taken, so "it reached 3" is exactly "it's stopped at the limit".

### Partition keys and the Kafka client you use

The labs pick a partition with the same stable hash in every language, so a key always lands in the same partition. Real Kafka clients pick it themselves, and **they don't all agree**. The Java client hashes the key with murmur2. librdkafka, which sits underneath the Python `confluent-kafka`, Go `confluent-kafka-go`, Rust `rdkafka` and C# `Confluent.Kafka` clients, defaults to a CRC32-based partitioner. A Java service and a Python service producing the same key can send it to different partitions, which silently breaks per-key ordering. Set `partitioner=murmur2_random` in the librdkafka clients when they share a topic with Java producers.

## 3. The same numbers, in every language

| Check | Expected in every language |
|---|---|
| a queue, two messages, two receives | order 1 then order 2, then nothing; analytics gets both too |
| a topic with no subscribers | nothing stored |
| unacknowledged, timeout 30 s, three tries | attempts 1, 2, 3 at 0, 30 and 60 s; dead-lettered at 90 s |
| a crash after charging, before the ack | 2 charges, or 1 with the idempotent handler |
| 10 s at 300/s then 20/s, capacity 100 | 2,000 rejected synchronously; peak 2,000, clear by 35 s, longest wait 20 s |
| the same with capacity 200 | peak 1,000, clear by 16 s, longest wait 5 s |
| "paid" fails once | queue: created, shipped, paid; partition: created, paid, shipped |
| 10,000 keys over 4 partitions | within 200 of 2,500 each |
| bounded queue of 3, five puts | the fourth try refused; producer stops at 3, then 4 after one take |

## Terms used in this lesson

1. **Bounded channel**: This is a queue between parts of one program with a fixed capacity, through which one side sends and the other receives.
2. **Non-blocking send**: This is a send that returns at once with "no" when the queue is full, instead of waiting for space.
3. **Partitioner**: In a Kafka client, this is the code that picks which partition a message goes to, usually by hashing its key.
4. **Durably blocked**: In Go's `synctest`, this describes a goroutine waiting on something only another goroutine in the same test can provide, such as a channel made inside the test.
5. **Borrow**: In Rust, this is a reference to a value that the compiler tracks, so that while something has a mutable borrow, nothing else can use the value.

## 4. Python

The broker uses dataclasses, and `level_load` keeps its queue of `[second, count]` pairs as lists so the count can change in place. `partition_for` writes the hash out because Python's built-in `hash()` of a string changes every run. The bounded queue is `asyncio.Queue(maxsize=3)`: `put_nowait` raises `QueueFull`, and `await put` waits.

```python
"""A small in-memory message broker: queues, topics, redelivery, a dead-letter queue, a partitioned log, and
load levelling. The same numbers as the TypeScript lab. The bounded queue is asyncio's own."""
from dataclasses import dataclass
from typing import Callable

MASK = 0xFFFFFFFF


@dataclass
class Delivery:
    id: str
    body: str
    key: str | None
    attempt: int


@dataclass
class _Stored:
    id: str
    body: str
    key: str | None
    attempts: int = 0
    visible_at: float = 0


class Broker:
    """Subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery."""

    def __init__(self, now: Callable[[], float], visibility_ms: float, max_attempts: int):
        self._now, self._visibility_ms, self._max_attempts = now, visibility_ms, max_attempts
        self._subscribers: dict[str, list[str]] = {}
        self._queues: dict[str, list[_Stored]] = {}
        self._dead: dict[str, list[_Stored]] = {}
        self._next_id = 1

    def subscribe(self, topic: str, subscription: str) -> None:
        self._subscribers.setdefault(topic, []).append(subscription)
        self._queues[subscription], self._dead[subscription] = [], []

    def publish(self, topic: str, body: str, key: str | None = None) -> str:
        id_ = f"m{self._next_id}"
        self._next_id += 1
        for s in self._subscribers.get(topic, []):  # no subscribers: nobody keeps it
            self._queues[s].append(_Stored(id_, body, key))
        return id_

    def receive(self, subscription: str) -> Delivery | None:
        queue = self._queues[subscription]
        i = 0
        while i < len(queue):
            m = queue[i]
            if m.visible_at > self._now():
                i += 1  # a consumer has it
            elif m.attempts >= self._max_attempts:
                self._dead[subscription].append(queue.pop(i))  # poison: stop retrying it
            else:
                m.attempts += 1
                m.visible_at = self._now() + self._visibility_ms
                return Delivery(m.id, m.body, m.key, m.attempts)
        return None

    def ack(self, subscription: str, id_: str) -> None:
        self._queues[subscription] = [m for m in self._queues[subscription] if m.id != id_]

    def depth(self, subscription: str) -> int:
        return len(self._queues[subscription])

    def dead_letters(self, subscription: str) -> list[str]:
        return [m.body for m in self._dead[subscription]]


def idempotent(handle: Callable[[str], None], seen: set[str]) -> Callable[[Delivery], str]:
    def run(d: Delivery) -> str:
        if d.id in seen:
            return "duplicate"
        handle(d.body)
        seen.add(d.id)
        return "processed"

    return run


def partition_for(key: str, partitions: int) -> int:
    """The same stable hash as the TypeScript lab. Python's hash() changes every run, so it can't choose partitions."""
    h = 0x811C9DC5
    for ch in key:
        h = ((h ^ ord(ch)) * 0x01000193) & MASK
    h = ((h ^ (h >> 16)) * 0x85EBCA6B) & MASK
    h = ((h ^ (h >> 13)) * 0xC2B2AE35) & MASK
    return (h ^ (h >> 16)) % partitions


class PartitionedLog:
    """Kafka-like: messages are kept; each consumer group has its own offset per partition."""

    def __init__(self, partitions: int):
        self._partitions: list[list[str]] = [[] for _ in range(partitions)]
        self._offsets: dict[str, list[int]] = {}

    def append(self, key: str, body: str) -> int:
        p = partition_for(key, len(self._partitions))
        self._partitions[p].append(body)
        return p

    def poll(self, group: str, partition: int) -> str | None:
        offset = self._offsets_for(group)[partition]
        messages = self._partitions[partition]
        return messages[offset] if offset < len(messages) else None

    def commit(self, group: str, partition: int) -> None:
        self._offsets_for(group)[partition] += 1

    def _offsets_for(self, group: str) -> list[int]:
        return self._offsets.setdefault(group, [0] * len(self._partitions))  # a new group starts at the beginning


def level_load(arrivals: list[int], per_second: int) -> dict:
    served = sum(min(a, per_second) for a in arrivals)
    rejected = sum(max(0, a - per_second) for a in arrivals)
    waiting: list[list[int]] = []  # [arrival second, count], oldest first
    depth = peak_depth = max_wait = cleared_after = 0
    second = 0
    while second < len(arrivals) or depth > 0:
        a = arrivals[second] if second < len(arrivals) else 0
        if a > 0:
            waiting.append([second, a])
        depth += a
        capacity = per_second
        while capacity > 0 and waiting:
            oldest = waiting[0]
            n = min(capacity, oldest[1])
            oldest[1] -= n
            capacity -= n
            depth -= n
            max_wait = max(max_wait, second - oldest[0])
            if oldest[1] == 0:
                waiting.pop(0)
        peak_depth = max(peak_depth, depth)
        if depth > 0:
            cleared_after = second + 2
        second += 1
    return {"sync": {"served": served, "rejected": rejected},
            "queued": {"peak_depth": peak_depth, "cleared_after_seconds": cleared_after, "max_wait_seconds": max_wait}}
```

```python
import asyncio
import unittest

from broker import Broker, PartitionedLog, idempotent, level_load, partition_for


class Clock:
    def __init__(self):
        self.now = 0

    def __call__(self):
        return self.now


def broker(clock=None):
    return Broker(clock or Clock(), visibility_ms=30_000, max_attempts=3)


class Messaging(unittest.IsolatedAsyncioTestCase):
    def test_queue_gives_each_message_to_one_consumer_topic_copies_it(self):
        b = broker()
        b.subscribe("orders", "invoices")
        b.subscribe("orders", "analytics")
        b.publish("orders", "order 1")
        b.publish("orders", "order 2")
        self.assertEqual([b.receive("invoices").body, b.receive("invoices").body], ["order 1", "order 2"])
        self.assertIsNone(b.receive("invoices"))
        self.assertEqual([b.receive("analytics").body, b.receive("analytics").body], ["order 1", "order 2"])
        b.publish("refunds", "refund 1")
        self.assertEqual(b.depth("invoices") + b.depth("analytics"), 4)

    def test_unacknowledged_comes_back_then_goes_to_the_dead_letter_queue(self):
        clock = Clock()
        b = broker(clock)
        b.subscribe("orders", "invoices")
        b.publish("orders", "order 1")
        self.assertEqual(b.receive("invoices").attempt, 1)
        self.assertIsNone(b.receive("invoices"))
        for now, attempt in [(30_000, 2), (60_000, 3)]:
            clock.now = now
            self.assertEqual(b.receive("invoices").attempt, attempt)
        clock.now = 90_000
        self.assertIsNone(b.receive("invoices"))
        self.assertEqual(b.dead_letters("invoices"), ["order 1"])
        self.assertEqual(b.depth("invoices"), 0)

    def test_crash_before_ack_charges_twice_unless_idempotent(self):
        for safe in [False, True]:
            clock = Clock()
            b = broker(clock)
            b.subscribe("orders", "payments")
            b.publish("orders", "charge £40 for order 1")
            charges = []
            charge = lambda body: charges.append(body)
            handle = idempotent(charge, set()) if safe else (lambda d: charge(d.body))
            handle(b.receive("payments"))  # charged, then the consumer crashes before acknowledging
            clock.now = 30_000
            again = b.receive("payments")
            handle(again)
            b.ack("payments", again.id)
            self.assertEqual(len(charges), 1 if safe else 2)

    def test_a_queue_absorbs_a_sale_spike(self):
        spike = [300] * 10 + [20] * 50
        two = level_load(spike, 100)
        self.assertEqual(two["sync"], {"served": 2_000, "rejected": 2_000})
        self.assertEqual(two["queued"], {"peak_depth": 2_000, "cleared_after_seconds": 35, "max_wait_seconds": 20})
        self.assertEqual(level_load(spike, 200)["queued"], {"peak_depth": 1_000, "cleared_after_seconds": 16, "max_wait_seconds": 5})

    def test_redelivery_reorders_a_partition_keeps_order_a_new_group_replays(self):
        clock = Clock()
        b = broker(clock)
        b.subscribe("orders", "shipping")
        for e in ["created", "paid", "shipped"]:
            b.publish("orders", f"order 7 {e}", "order-7")
        seen = []
        for fail in [False, True, False]:
            d = b.receive("shipping")
            if not fail:
                seen.append(d.body)
                b.ack("shipping", d.id)
        clock.now = 30_000
        seen.append(b.receive("shipping").body)
        self.assertEqual(seen, ["order 7 created", "order 7 shipped", "order 7 paid"])

        log = PartitionedLog(4)
        for e in ["created", "paid", "shipped"]:
            log.append("order-7", f"order 7 {e}")
        p, in_order, failed_once = partition_for("order-7", 4), [], False
        while (m := log.poll("shipping", p)) is not None:
            if m.endswith("paid") and not failed_once:
                failed_once = True  # no commit: the same message comes back
                continue
            in_order.append(m)
            log.commit("shipping", p)
        self.assertEqual(in_order, ["order 7 created", "order 7 paid", "order 7 shipped"])
        self.assertEqual(log.poll("analytics", p), "order 7 created")

    def test_a_key_always_lands_in_the_same_partition(self):
        self.assertEqual(partition_for("order-7", 4), partition_for("order-7", 4))
        counts = [0] * 4
        for i in range(10_000):
            counts[partition_for(f"order-{i}", 4)] += 1
        self.assertTrue(all(abs(n - 2_500) < 200 for n in counts), counts)

    async def test_asyncio_queue_pushes_back(self):
        q: asyncio.Queue[int] = asyncio.Queue(maxsize=3)
        accepted = []
        for n in [1, 2, 3, 4]:
            try:
                q.put_nowait(n)
                accepted.append(True)
            except asyncio.QueueFull:  # full: refused at once
                accepted.append(False)
        self.assertEqual(accepted, [True, True, True, False])
        self.assertEqual([q.get_nowait() for _ in range(3)], [1, 2, 3])

        events = []

        async def producer():
            for n in range(1, 6):
                await q.put(n)  # waits while the queue is full
                events.append(f"put {n}")

        task = asyncio.create_task(producer())
        for _ in range(5):
            await asyncio.sleep(0)  # let the producer run until it's blocked
        self.assertEqual(events, ["put 1", "put 2", "put 3"])
        events.append(f"took {await q.get()}")
        for _ in range(5):
            await asyncio.sleep(0)
        self.assertEqual(events[3:], ["took 1", "put 4"])
        for _ in range(4):
            await q.get()
        await task
        self.assertEqual(sum(e.startswith("put") for e in events), 5)
        self.assertTrue(q.empty())


if __name__ == "__main__":
    unittest.main()
```

**Lab:** [`labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/04-messaging-and-async/labs/python). `python3 labs/run.py messaging-and-async/python`.

## 5. Go

`Receive` returns `(Delivery, bool)`, the comma-ok idiom. `TryPut` is a generic non-blocking send, using `select` with a `default` case. The bounded-queue test runs inside `synctest.Test` and makes its channel there, so `synctest.Wait()` can see the producer block. The lab runs with `-race`.

```go
// Package messaging: a small in-memory message broker with queues, topics, redelivery, a dead-letter queue, a
// partitioned log and load levelling. The same numbers as the TypeScript lab. The bounded queue is a channel.
package messaging

import (
	"fmt"
	"slices"
)

type Delivery struct {
	ID, Body, Key string
	Attempt       int
}

type stored struct {
	id, body, key string
	attempts      int
	visibleAt     int64
}

// Broker: subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery.
type Broker struct {
	now          func() int64 // milliseconds
	visibilityMs int64
	maxAttempts  int
	subscribers  map[string][]string
	queues, dead map[string][]*stored
	nextID       int
}

func NewBroker(now func() int64, visibilityMs int64, maxAttempts int) *Broker {
	return &Broker{now: now, visibilityMs: visibilityMs, maxAttempts: maxAttempts,
		subscribers: map[string][]string{}, queues: map[string][]*stored{}, dead: map[string][]*stored{}, nextID: 1}
}

func (b *Broker) Subscribe(topic, subscription string) {
	b.subscribers[topic] = append(b.subscribers[topic], subscription)
	b.queues[subscription], b.dead[subscription] = nil, nil
}

// Publish copies the message into every subscription. With no subscribers, nobody keeps it.
func (b *Broker) Publish(topic, body, key string) string {
	id := fmt.Sprintf("m%d", b.nextID)
	b.nextID++
	for _, s := range b.subscribers[topic] {
		b.queues[s] = append(b.queues[s], &stored{id: id, body: body, key: key})
	}
	return id
}

// Receive returns the oldest message no consumer is working on, and hides it for the visibility timeout.
func (b *Broker) Receive(subscription string) (Delivery, bool) {
	queue := b.queues[subscription]
	for i := 0; i < len(queue); i++ {
		m := queue[i]
		if m.visibleAt > b.now() {
			continue // a consumer has it
		}
		if m.attempts >= b.maxAttempts {
			b.dead[subscription] = append(b.dead[subscription], m) // poison: stop retrying it
			queue = slices.Delete(queue, i, i+1)
			b.queues[subscription] = queue
			i--
			continue
		}
		m.attempts++
		m.visibleAt = b.now() + b.visibilityMs
		return Delivery{m.id, m.body, m.key, m.attempts}, true
	}
	return Delivery{}, false
}

func (b *Broker) Ack(subscription, id string) {
	b.queues[subscription] = slices.DeleteFunc(b.queues[subscription], func(m *stored) bool { return m.id == id })
}

func (b *Broker) Depth(subscription string) int { return len(b.queues[subscription]) }

func (b *Broker) DeadLetters(subscription string) []string {
	var bodies []string
	for _, m := range b.dead[subscription] {
		bodies = append(bodies, m.body)
	}
	return bodies
}

// Idempotent remembers which message IDs it has processed and skips them the second time.
func Idempotent(handle func(body string), seen map[string]bool) func(Delivery) string {
	return func(d Delivery) string {
		if seen[d.ID] {
			return "duplicate"
		}
		handle(d.Body)
		seen[d.ID] = true
		return "processed"
	}
}

// PartitionFor is the same stable hash as the TypeScript lab.
func PartitionFor(key string, partitions int) int {
	h := uint32(0x811c9dc5)
	for i := 0; i < len(key); i++ {
		h = (h ^ uint32(key[i])) * 0x01000193
	}
	h = (h ^ h>>16) * 0x85ebca6b
	h = (h ^ h>>13) * 0xc2b2ae35
	return int((h ^ h>>16) % uint32(partitions))
}

// PartitionedLog is Kafka-like: messages are kept; each consumer group has its own offset per partition.
type PartitionedLog struct {
	partitions [][]string
	offsets    map[string][]int
}

func NewPartitionedLog(partitions int) *PartitionedLog {
	return &PartitionedLog{partitions: make([][]string, partitions), offsets: map[string][]int{}}
}

func (l *PartitionedLog) Append(key, body string) int {
	p := PartitionFor(key, len(l.partitions))
	l.partitions[p] = append(l.partitions[p], body)
	return p
}

func (l *PartitionedLog) Poll(group string, partition int) (string, bool) {
	offset := l.offsetsFor(group)[partition]
	if offset >= len(l.partitions[partition]) {
		return "", false
	}
	return l.partitions[partition][offset], true
}

func (l *PartitionedLog) Commit(group string, partition int) { l.offsetsFor(group)[partition]++ }

func (l *PartitionedLog) offsetsFor(group string) []int {
	if _, ok := l.offsets[group]; !ok {
		l.offsets[group] = make([]int, len(l.partitions)) // a new group starts at the beginning
	}
	return l.offsets[group]
}

type Levelled struct{ Served, Rejected, PeakDepth, ClearedAfterSeconds, MaxWaitSeconds int }

// LevelLoad compares turning away what doesn't fit each second with queueing it and working through it in order.
func LevelLoad(arrivals []int, perSecond int) Levelled {
	var r Levelled
	for _, a := range arrivals {
		r.Served += min(a, perSecond)
		r.Rejected += max(0, a-perSecond)
	}
	type batch struct{ second, count int }
	var waiting []batch
	depth := 0
	for second := 0; second < len(arrivals) || depth > 0; second++ {
		a := 0
		if second < len(arrivals) {
			a = arrivals[second]
		}
		if a > 0 {
			waiting = append(waiting, batch{second, a})
		}
		depth += a
		for capacity := perSecond; capacity > 0 && len(waiting) > 0; {
			n := min(capacity, waiting[0].count)
			waiting[0].count -= n
			capacity -= n
			depth -= n
			r.MaxWaitSeconds = max(r.MaxWaitSeconds, second-waiting[0].second)
			if waiting[0].count == 0 {
				waiting = waiting[1:]
			}
		}
		r.PeakDepth = max(r.PeakDepth, depth)
		if depth > 0 {
			r.ClearedAfterSeconds = second + 2
		}
	}
	return r
}

// TryPut is a non-blocking send on a buffered channel: false if it's full.
func TryPut[T any](q chan<- T, item T) bool {
	select {
	case q <- item:
		return true
	default:
		return false
	}
}
```

```go
package messaging

import (
	"slices"
	"strconv"
	"strings"
	"sync/atomic"
	"testing"
	"testing/synctest"
)

func broker(now *int64) *Broker {
	return NewBroker(func() int64 { return *now }, 30_000, 3)
}

func TestQueueGivesEachMessageToOneConsumerTopicCopiesIt(t *testing.T) {
	var now int64
	b := broker(&now)
	b.Subscribe("orders", "invoices")
	b.Subscribe("orders", "analytics")
	b.Publish("orders", "order 1", "")
	b.Publish("orders", "order 2", "")
	first, _ := b.Receive("invoices")
	second, _ := b.Receive("invoices")
	_, more := b.Receive("invoices")
	if first.Body != "order 1" || second.Body != "order 2" || more {
		t.Fatal(first, second, more)
	}
	a1, _ := b.Receive("analytics")
	a2, _ := b.Receive("analytics")
	b.Publish("refunds", "refund 1", "")
	if a1.Body != "order 1" || a2.Body != "order 2" || b.Depth("invoices")+b.Depth("analytics") != 4 {
		t.Fatal(a1, a2)
	}
}

func TestUnacknowledgedComesBackThenGoesToTheDeadLetterQueue(t *testing.T) {
	var now int64
	b := broker(&now)
	b.Subscribe("orders", "invoices")
	b.Publish("orders", "order 1", "")
	if d, _ := b.Receive("invoices"); d.Attempt != 1 {
		t.Fatal(d)
	}
	if _, ok := b.Receive("invoices"); ok {
		t.Fatal("delivered while hidden")
	}
	for _, c := range []struct {
		now     int64
		attempt int
	}{{30_000, 2}, {60_000, 3}} {
		now = c.now
		if d, _ := b.Receive("invoices"); d.Attempt != c.attempt {
			t.Fatal(d)
		}
	}
	now = 90_000
	if _, ok := b.Receive("invoices"); ok || !slices.Equal(b.DeadLetters("invoices"), []string{"order 1"}) || b.Depth("invoices") != 0 {
		t.Fatal(b.DeadLetters("invoices"))
	}
}

func TestCrashBeforeAckChargesTwiceUnlessIdempotent(t *testing.T) {
	for _, safe := range []bool{false, true} {
		var now int64
		b := broker(&now)
		b.Subscribe("orders", "payments")
		b.Publish("orders", "charge £40 for order 1", "")
		charges := 0
		charge := func(string) { charges++ }
		handle := func(d Delivery) { charge(d.Body) }
		if safe {
			once := Idempotent(charge, map[string]bool{})
			handle = func(d Delivery) { once(d) }
		}
		d, _ := b.Receive("payments")
		handle(d) // charged, then the consumer crashes before acknowledging
		now = 30_000
		again, _ := b.Receive("payments")
		handle(again)
		b.Ack("payments", again.ID)
		if want := map[bool]int{false: 2, true: 1}[safe]; charges != want {
			t.Fatalf("safe=%v: %d charges", safe, charges)
		}
	}
}

func TestAQueueAbsorbsASaleSpike(t *testing.T) {
	spike := append(slices.Repeat([]int{300}, 10), slices.Repeat([]int{20}, 50)...)
	if got := LevelLoad(spike, 100); got != (Levelled{2_000, 2_000, 2_000, 35, 20}) {
		t.Fatal(got)
	}
	if got := LevelLoad(spike, 200); got.PeakDepth != 1_000 || got.ClearedAfterSeconds != 16 || got.MaxWaitSeconds != 5 {
		t.Fatal(got)
	}
}

func TestRedeliveryReordersAPartitionKeepsOrderANewGroupReplays(t *testing.T) {
	var now int64
	b := broker(&now)
	b.Subscribe("orders", "shipping")
	for _, e := range []string{"created", "paid", "shipped"} {
		b.Publish("orders", "order 7 "+e, "order-7")
	}
	var seen []string
	for _, fail := range []bool{false, true, false} {
		d, _ := b.Receive("shipping")
		if !fail {
			seen = append(seen, d.Body)
			b.Ack("shipping", d.ID)
		}
	}
	now = 30_000
	paid, _ := b.Receive("shipping")
	seen = append(seen, paid.Body)
	if !slices.Equal(seen, []string{"order 7 created", "order 7 shipped", "order 7 paid"}) {
		t.Fatal(seen)
	}

	log := NewPartitionedLog(4)
	for _, e := range []string{"created", "paid", "shipped"} {
		log.Append("order-7", "order 7 "+e)
	}
	p := PartitionFor("order-7", 4)
	var inOrder []string
	failedOnce := false
	for m, ok := log.Poll("shipping", p); ok; m, ok = log.Poll("shipping", p) {
		if strings.HasSuffix(m, "paid") && !failedOnce {
			failedOnce = true // no commit: the same message comes back
			continue
		}
		inOrder = append(inOrder, m)
		log.Commit("shipping", p)
	}
	first, _ := log.Poll("analytics", p)
	if !slices.Equal(inOrder, []string{"order 7 created", "order 7 paid", "order 7 shipped"}) || first != "order 7 created" {
		t.Fatal(inOrder, first)
	}
}

func TestAKeyAlwaysLandsInTheSamePartition(t *testing.T) {
	counts := make([]int, 4)
	for i := range 10_000 {
		counts[PartitionFor("order-"+strconv.Itoa(i), 4)]++
	}
	for _, n := range counts {
		if n < 2_300 || n > 2_700 {
			t.Fatal(counts)
		}
	}
}

func TestABufferedChannelPushesBack(t *testing.T) {
	q := make(chan int, 3)
	var got []bool
	for n := 1; n <= 4; n++ {
		got = append(got, TryPut(q, n))
	}
	if !slices.Equal(got, []bool{true, true, true, false}) || <-q != 1 || <-q != 2 || <-q != 3 {
		t.Fatal(got)
	}
	synctest.Test(t, func(t *testing.T) {
		q := make(chan int, 3) // made inside the bubble, so synctest can tell when a send on it is blocked
		var puts atomic.Int32
		done := make(chan struct{})
		go func() {
			for n := 1; n <= 5; n++ {
				q <- n // blocks while the channel is full
				puts.Add(1)
			}
			close(done)
		}()
		synctest.Wait() // the producer is blocked
		if puts.Load() != 3 {
			t.Fatal("puts before any take:", puts.Load())
		}
		<-q
		synctest.Wait()
		if puts.Load() != 4 {
			t.Fatal("puts after one take:", puts.Load())
		}
		for range 4 {
			<-q
		}
		<-done
	})
}
```

**Lab:** [`labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/04-messaging-and-async/labs/go). `python3 labs/run.py messaging-and-async/go`.

## 6. Java

`receive` returns `Optional<Delivery>` and removes poison messages with the iterator's `remove`. `partitionFor` uses `Integer.remainderUnsigned`, because Java's `int` has no unsigned form. The bounded queue is `ArrayBlockingQueue`: `offer` refuses and `put` waits. The producer is a virtual thread, and the check waits for its state to be `WAITING`.

```java
package messaging;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.LongSupplier;

/** A small in-memory message broker. The same numbers as the TypeScript lab. The bounded queue is java.util.concurrent's. */
public final class Messaging {
    private Messaging() {}

    public record Delivery(String id, String body, String key, int attempt) {}

    private static final class Stored {
        final String id;
        final String body;
        final String key;
        int attempts;
        long visibleAt;

        Stored(String id, String body, String key) {
            this.id = id;
            this.body = body;
            this.key = key;
        }
    }

    /** Subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery. */
    public static final class Broker {
        private final LongSupplier now;
        private final long visibilityMs;
        private final int maxAttempts;
        private final Map<String, List<String>> subscribers = new HashMap<>();
        private final Map<String, List<Stored>> queues = new HashMap<>();
        private final Map<String, List<Stored>> dead = new HashMap<>();
        private int nextId = 1;

        public Broker(LongSupplier now, long visibilityMs, int maxAttempts) {
            this.now = now;
            this.visibilityMs = visibilityMs;
            this.maxAttempts = maxAttempts;
        }

        public void subscribe(String topic, String subscription) {
            subscribers.computeIfAbsent(topic, t -> new ArrayList<>()).add(subscription);
            queues.put(subscription, new ArrayList<>());
            dead.put(subscription, new ArrayList<>());
        }

        /** With no subscribers, nobody keeps the message. */
        public String publish(String topic, String body, String key) {
            String id = "m" + nextId++;
            for (String s : subscribers.getOrDefault(topic, List.of())) queues.get(s).add(new Stored(id, body, key));
            return id;
        }

        public Optional<Delivery> receive(String subscription) {
            var queue = queues.get(subscription);
            for (var it = queue.iterator(); it.hasNext();) {
                Stored m = it.next();
                if (m.visibleAt > now.getAsLong()) continue; // a consumer has it
                if (m.attempts >= maxAttempts) {
                    it.remove(); // poison: stop retrying it
                    dead.get(subscription).add(m);
                    continue;
                }
                m.attempts++;
                m.visibleAt = now.getAsLong() + visibilityMs;
                return Optional.of(new Delivery(m.id, m.body, m.key, m.attempts));
            }
            return Optional.empty();
        }

        public void ack(String subscription, String id) {
            queues.get(subscription).removeIf(m -> m.id.equals(id));
        }

        public int depth(String subscription) {
            return queues.get(subscription).size();
        }

        public List<String> deadLetters(String subscription) {
            return dead.get(subscription).stream().map(m -> m.body).toList();
        }
    }

    /** Skips a message ID it has already processed. */
    public static Function<Delivery, String> idempotent(Consumer<String> handle, Set<String> seen) {
        return d -> {
            if (seen.contains(d.id())) return "duplicate";
            handle.accept(d.body());
            seen.add(d.id());
            return "processed";
        };
    }

    /** The same stable hash as the TypeScript lab. String.hashCode is stable too, but clusters similar keys. */
    public static int partitionFor(String key, int partitions) {
        int h = 0x811c9dc5;
        for (int i = 0; i < key.length(); i++) h = (h ^ key.charAt(i)) * 0x01000193;
        h = (h ^ (h >>> 16)) * 0x85ebca6b;
        h = (h ^ (h >>> 13)) * 0xc2b2ae35;
        return Integer.remainderUnsigned(h ^ (h >>> 16), partitions);
    }

    /** Kafka-like: messages are kept; each consumer group has its own offset per partition. */
    public static final class PartitionedLog {
        private final List<List<String>> partitions = new ArrayList<>();
        private final Map<String, int[]> offsets = new HashMap<>();

        public PartitionedLog(int count) {
            for (int i = 0; i < count; i++) partitions.add(new ArrayList<>());
        }

        public int append(String key, String body) {
            int p = partitionFor(key, partitions.size());
            partitions.get(p).add(body);
            return p;
        }

        public Optional<String> poll(String group, int partition) {
            int offset = offsetsFor(group)[partition];
            var messages = partitions.get(partition);
            return offset < messages.size() ? Optional.of(messages.get(offset)) : Optional.empty();
        }

        public void commit(String group, int partition) {
            offsetsFor(group)[partition]++;
        }

        private int[] offsetsFor(String group) {
            return offsets.computeIfAbsent(group, g -> new int[partitions.size()]); // a new group starts at 0
        }
    }

    public record Levelled(int served, int rejected, int peakDepth, int clearedAfterSeconds, int maxWaitSeconds) {}

    public static Levelled levelLoad(int[] arrivals, int perSecond) {
        int served = 0;
        int rejected = 0;
        for (int a : arrivals) {
            served += Math.min(a, perSecond);
            rejected += Math.max(0, a - perSecond);
        }
        var waiting = new ArrayDeque<int[]>(); // {arrival second, count}, oldest first
        int depth = 0;
        int peakDepth = 0;
        int maxWait = 0;
        int cleared = 0;
        for (int second = 0; second < arrivals.length || depth > 0; second++) {
            int a = second < arrivals.length ? arrivals[second] : 0;
            if (a > 0) waiting.add(new int[] {second, a});
            depth += a;
            for (int capacity = perSecond; capacity > 0 && !waiting.isEmpty();) {
                int[] oldest = waiting.peek();
                int n = Math.min(capacity, oldest[1]);
                oldest[1] -= n;
                capacity -= n;
                depth -= n;
                maxWait = Math.max(maxWait, second - oldest[0]);
                if (oldest[1] == 0) waiting.poll();
            }
            peakDepth = Math.max(peakDepth, depth);
            if (depth > 0) cleared = second + 2;
        }
        return new Levelled(served, rejected, peakDepth, cleared, maxWait);
    }
}
```

```java
package messaging;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class MessagingCheck {
    private MessagingCheck() {}

    private static Messaging.Broker broker(AtomicLong clock) {
        return new Messaging.Broker(clock::get, 30_000, 3);
    }

    private static void until(BooleanSupplier done) throws InterruptedException {
        while (!done.getAsBoolean()) Thread.sleep(1);
    }

    public static void main(String[] args) throws Exception {
        var b = broker(new AtomicLong());
        b.subscribe("orders", "invoices");
        b.subscribe("orders", "analytics");
        b.publish("orders", "order 1", null);
        b.publish("orders", "order 2", null);
        assert b.receive("invoices").orElseThrow().body().equals("order 1");
        assert b.receive("invoices").orElseThrow().body().equals("order 2");
        assert b.receive("invoices").isEmpty();
        assert b.receive("analytics").orElseThrow().body().equals("order 1");
        b.publish("refunds", "refund 1", null);
        assert b.depth("invoices") + b.depth("analytics") == 4;

        var clock = new AtomicLong();
        var r = broker(clock);
        r.subscribe("orders", "invoices");
        r.publish("orders", "order 1", null);
        assert r.receive("invoices").orElseThrow().attempt() == 1 && r.receive("invoices").isEmpty();
        clock.set(30_000);
        assert r.receive("invoices").orElseThrow().attempt() == 2;
        clock.set(60_000);
        assert r.receive("invoices").orElseThrow().attempt() == 3;
        clock.set(90_000);
        assert r.receive("invoices").isEmpty() && r.deadLetters("invoices").equals(List.of("order 1")) && r.depth("invoices") == 0;

        for (boolean safe : new boolean[] {false, true}) {
            var t = new AtomicLong();
            var p = broker(t);
            p.subscribe("orders", "payments");
            p.publish("orders", "charge £40 for order 1", null);
            var charges = new AtomicInteger();
            Consumer<String> charge = body -> charges.incrementAndGet();
            var once = Messaging.idempotent(charge, new HashSet<>());
            Consumer<Messaging.Delivery> handle = safe ? once::apply : d -> charge.accept(d.body());
            handle.accept(p.receive("payments").orElseThrow()); // charged, then a crash before the ack
            t.set(30_000);
            var again = p.receive("payments").orElseThrow();
            handle.accept(again);
            p.ack("payments", again.id());
            assert charges.get() == (safe ? 1 : 2) : safe + ": " + charges.get();
        }

        int[] spike = new int[60];
        for (int i = 0; i < 60; i++) spike[i] = i < 10 ? 300 : 20;
        assert Messaging.levelLoad(spike, 100).equals(new Messaging.Levelled(2_000, 2_000, 2_000, 35, 20));
        var four = Messaging.levelLoad(spike, 200);
        assert four.peakDepth() == 1_000 && four.clearedAfterSeconds() == 16 && four.maxWaitSeconds() == 5 : four;

        var c = new AtomicLong();
        var s = broker(c);
        s.subscribe("orders", "shipping");
        for (String e : List.of("created", "paid", "shipped")) s.publish("orders", "order 7 " + e, "order-7");
        List<String> seen = new ArrayList<>();
        for (boolean fail : new boolean[] {false, true, false}) {
            var d = s.receive("shipping").orElseThrow();
            if (!fail) {
                seen.add(d.body());
                s.ack("shipping", d.id());
            }
        }
        c.set(30_000);
        seen.add(s.receive("shipping").orElseThrow().body());
        assert seen.equals(List.of("order 7 created", "order 7 shipped", "order 7 paid")) : seen;

        var log = new Messaging.PartitionedLog(4);
        for (String e : List.of("created", "paid", "shipped")) log.append("order-7", "order 7 " + e);
        int part = Messaging.partitionFor("order-7", 4);
        List<String> inOrder = new ArrayList<>();
        boolean failedOnce = false;
        for (var m = log.poll("shipping", part); m.isPresent(); m = log.poll("shipping", part)) {
            if (m.get().endsWith("paid") && !failedOnce) {
                failedOnce = true; // no commit: the same message comes back
                continue;
            }
            inOrder.add(m.get());
            log.commit("shipping", part);
        }
        assert inOrder.equals(List.of("order 7 created", "order 7 paid", "order 7 shipped")) : inOrder;
        assert log.poll("analytics", part).orElseThrow().equals("order 7 created");

        int[] counts = new int[4];
        for (int i = 0; i < 10_000; i++) counts[Messaging.partitionFor("order-" + i, 4)]++;
        for (int n : counts) assert Math.abs(n - 2_500) < 200 : java.util.Arrays.toString(counts);

        // A bounded queue pushes back: offer refuses when full, put waits.
        var q = new ArrayBlockingQueue<Integer>(3);
        List<Boolean> accepted = new ArrayList<>();
        for (int n = 1; n <= 4; n++) accepted.add(q.offer(n));
        assert accepted.equals(List.of(true, true, true, false)) : accepted;
        assert q.take() == 1 && q.take() == 2 && q.take() == 3;
        var puts = new AtomicInteger();
        var producer = Thread.ofVirtual().start(() -> {
            try {
                for (int n = 1; n <= 5; n++) {
                    q.put(n); // waits while the queue is full
                    puts.incrementAndGet();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        until(() -> puts.get() == 3 && producer.getState() == Thread.State.WAITING); // stopped at the limit
        q.take();
        until(() -> puts.get() == 4); // one out, one more in; a fifth can't fit until the next take
        for (int i = 0; i < 4; i++) q.take();
        producer.join();
        assert puts.get() == 5 && q.isEmpty();
        System.out.println("all messaging checks passed");
    }
}
```

**Lab:** [`labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/04-messaging-and-async/labs/java). `python3 labs/run.py messaging-and-async/java`.

## 7. Rust

The broker holds its clock as `Box<dyn Fn() -> u64>`, and the tests share the time through `Rc<Cell<u64>>`. `level_load` uses `saturating_sub` for "how many didn't fit", so a quiet second gives 0 instead of an underflow panic. The bounded queue is `sync_channel(3)`: `try_send` returns `Err(Full)` and `send` blocks. The producer runs on a thread, and `rx.iter().take(4)` drains the rest.

```rust
//! A small in-memory message broker: queues, topics, redelivery, a dead-letter queue, a partitioned log and load
//! levelling. The same numbers as the TypeScript lab. The bounded queue is std's `sync_channel`.
use std::collections::{HashMap, HashSet, VecDeque};

#[derive(Debug, Clone, PartialEq)]
pub struct Delivery {
    pub id: String,
    pub body: String,
    pub key: Option<String>,
    pub attempt: u32,
}

struct Stored {
    id: String,
    body: String,
    key: Option<String>,
    attempts: u32,
    visible_at: u64,
}

/// Subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery.
pub struct Broker {
    now: Box<dyn Fn() -> u64>, // milliseconds
    visibility_ms: u64,
    max_attempts: u32,
    subscribers: HashMap<String, Vec<String>>,
    queues: HashMap<String, Vec<Stored>>,
    dead: HashMap<String, Vec<Stored>>,
    next_id: u32,
}

impl Broker {
    pub fn new(now: impl Fn() -> u64 + 'static, visibility_ms: u64, max_attempts: u32) -> Self {
        Broker {
            now: Box::new(now),
            visibility_ms,
            max_attempts,
            subscribers: HashMap::new(),
            queues: HashMap::new(),
            dead: HashMap::new(),
            next_id: 1,
        }
    }

    pub fn subscribe(&mut self, topic: &str, subscription: &str) {
        self.subscribers
            .entry(topic.into())
            .or_default()
            .push(subscription.into());
        self.queues.insert(subscription.into(), Vec::new());
        self.dead.insert(subscription.into(), Vec::new());
    }

    /// With no subscribers, nobody keeps the message.
    pub fn publish(&mut self, topic: &str, body: &str, key: Option<&str>) -> String {
        let id = format!("m{}", self.next_id);
        self.next_id += 1;
        for s in self.subscribers.get(topic).into_iter().flatten() {
            let stored = Stored {
                id: id.clone(),
                body: body.into(),
                key: key.map(Into::into),
                attempts: 0,
                visible_at: 0,
            };
            self.queues.get_mut(s).expect("subscribed").push(stored);
        }
        id
    }

    pub fn receive(&mut self, subscription: &str) -> Option<Delivery> {
        let now = (self.now)();
        let queue = self.queues.get_mut(subscription)?;
        let mut i = 0;
        while i < queue.len() {
            if queue[i].visible_at > now {
                i += 1; // a consumer has it
            } else if queue[i].attempts >= self.max_attempts {
                let poison = queue.remove(i); // stop retrying it
                self.dead
                    .get_mut(subscription)
                    .expect("subscribed")
                    .push(poison);
            } else {
                let m = &mut queue[i];
                m.attempts += 1;
                m.visible_at = now + self.visibility_ms;
                return Some(Delivery {
                    id: m.id.clone(),
                    body: m.body.clone(),
                    key: m.key.clone(),
                    attempt: m.attempts,
                });
            }
        }
        None
    }

    pub fn ack(&mut self, subscription: &str, id: &str) {
        if let Some(queue) = self.queues.get_mut(subscription) {
            queue.retain(|m| m.id != id);
        }
    }

    pub fn depth(&self, subscription: &str) -> usize {
        self.queues[subscription].len()
    }

    pub fn dead_letters(&self, subscription: &str) -> Vec<&str> {
        self.dead[subscription]
            .iter()
            .map(|m| m.body.as_str())
            .collect()
    }
}

/// Skips a message ID it has already processed.
pub fn idempotent<'a>(
    mut handle: impl FnMut(&str) + 'a,
    seen: &'a mut HashSet<String>,
) -> impl FnMut(&Delivery) -> &'static str + 'a {
    move |d| {
        if seen.contains(&d.id) {
            return "duplicate";
        }
        handle(&d.body);
        seen.insert(d.id.clone());
        "processed"
    }
}

/// The same stable hash as the TypeScript lab. std's HashMap hasher is seeded randomly, so it can't choose partitions.
pub fn partition_for(key: &str, partitions: usize) -> usize {
    let mut h: u32 = 0x811c9dc5;
    for byte in key.bytes() {
        h = (h ^ u32::from(byte)).wrapping_mul(0x01000193);
    }
    h = (h ^ (h >> 16)).wrapping_mul(0x85ebca6b);
    h = (h ^ (h >> 13)).wrapping_mul(0xc2b2ae35);
    (h ^ (h >> 16)) as usize % partitions
}

/// Kafka-like: messages are kept; each consumer group has its own offset per partition.
pub struct PartitionedLog {
    partitions: Vec<Vec<String>>,
    offsets: HashMap<String, Vec<usize>>,
}

impl PartitionedLog {
    pub fn new(partitions: usize) -> Self {
        PartitionedLog {
            partitions: vec![Vec::new(); partitions],
            offsets: HashMap::new(),
        }
    }

    pub fn append(&mut self, key: &str, body: &str) -> usize {
        let p = partition_for(key, self.partitions.len());
        self.partitions[p].push(body.into());
        p
    }

    pub fn poll(&mut self, group: &str, partition: usize) -> Option<String> {
        let offset = self.offsets_for(group)[partition];
        self.partitions[partition].get(offset).cloned()
    }

    pub fn commit(&mut self, group: &str, partition: usize) {
        self.offsets_for(group)[partition] += 1;
    }

    fn offsets_for(&mut self, group: &str) -> &mut Vec<usize> {
        let count = self.partitions.len();
        self.offsets
            .entry(group.into())
            .or_insert_with(|| vec![0; count]) // a new group starts at the beginning
    }
}

#[derive(Debug, PartialEq)]
pub struct Levelled {
    pub served: u32,
    pub rejected: u32,
    pub peak_depth: u32,
    pub cleared_after_seconds: usize,
    pub max_wait_seconds: usize,
}

pub fn level_load(arrivals: &[u32], per_second: u32) -> Levelled {
    let served = arrivals.iter().map(|&a| a.min(per_second)).sum();
    let rejected = arrivals.iter().map(|&a| a.saturating_sub(per_second)).sum();
    let mut waiting: VecDeque<(usize, u32)> = VecDeque::new(); // (arrival second, count), oldest first
    let (mut depth, mut peak_depth, mut max_wait, mut cleared) = (0, 0, 0, 0);
    let mut second = 0;
    while second < arrivals.len() || depth > 0 {
        let a = arrivals.get(second).copied().unwrap_or(0);
        if a > 0 {
            waiting.push_back((second, a));
        }
        depth += a;
        let mut capacity = per_second;
        while capacity > 0 {
            let Some(oldest) = waiting.front_mut() else {
                break;
            };
            let n = capacity.min(oldest.1);
            oldest.1 -= n;
            capacity -= n;
            depth -= n;
            max_wait = max_wait.max(second - oldest.0);
            if oldest.1 == 0 {
                waiting.pop_front();
            }
        }
        peak_depth = peak_depth.max(depth);
        if depth > 0 {
            cleared = second + 2;
        }
        second += 1;
    }
    Levelled {
        served,
        rejected,
        peak_depth,
        cleared_after_seconds: cleared,
        max_wait_seconds: max_wait,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;
    use std::rc::Rc;
    use std::sync::atomic::{AtomicU32, Ordering};
    use std::sync::{Arc, mpsc};

    fn broker() -> (Rc<Cell<u64>>, Broker) {
        let clock = Rc::new(Cell::new(0));
        let read = clock.clone();
        (clock, Broker::new(move || read.get(), 30_000, 3))
    }

    fn body(d: Option<Delivery>) -> String {
        d.expect("a message").body
    }

    #[test]
    fn a_queue_gives_each_message_to_one_consumer_a_topic_copies_it() {
        let (_, mut b) = broker();
        b.subscribe("orders", "invoices");
        b.subscribe("orders", "analytics");
        b.publish("orders", "order 1", None);
        b.publish("orders", "order 2", None);
        assert_eq!(
            [body(b.receive("invoices")), body(b.receive("invoices"))],
            ["order 1", "order 2"]
        );
        assert_eq!(b.receive("invoices"), None);
        assert_eq!(
            [body(b.receive("analytics")), body(b.receive("analytics"))],
            ["order 1", "order 2"]
        );
        b.publish("refunds", "refund 1", None);
        assert_eq!(b.depth("invoices") + b.depth("analytics"), 4);
    }

    #[test]
    fn unacknowledged_comes_back_then_goes_to_the_dead_letter_queue() {
        let (clock, mut b) = broker();
        b.subscribe("orders", "invoices");
        b.publish("orders", "order 1", None);
        assert_eq!(b.receive("invoices").unwrap().attempt, 1);
        assert_eq!(b.receive("invoices"), None);
        for (now, attempt) in [(30_000, 2), (60_000, 3)] {
            clock.set(now);
            assert_eq!(b.receive("invoices").unwrap().attempt, attempt);
        }
        clock.set(90_000);
        assert_eq!(b.receive("invoices"), None);
        assert_eq!(b.dead_letters("invoices"), ["order 1"]);
        assert_eq!(b.depth("invoices"), 0);
    }

    #[test]
    fn a_crash_before_the_ack_charges_twice_unless_idempotent() {
        for safe in [false, true] {
            let (clock, mut b) = broker();
            b.subscribe("orders", "payments");
            b.publish("orders", "charge £40 for order 1", None);
            let charges = Cell::new(0);
            let mut seen = HashSet::new();
            let mut once = idempotent(|_| charges.set(charges.get() + 1), &mut seen);
            let mut handle = |d: &Delivery| {
                if safe {
                    once(d);
                } else {
                    charges.set(charges.get() + 1)
                }
            };
            handle(&b.receive("payments").unwrap()); // charged, then a crash before the ack
            clock.set(30_000);
            let again = b.receive("payments").unwrap();
            handle(&again);
            b.ack("payments", &again.id);
            assert_eq!(charges.get(), if safe { 1 } else { 2 });
        }
    }

    #[test]
    fn a_queue_absorbs_a_sale_spike() {
        let spike: Vec<u32> = [vec![300; 10], vec![20; 50]].concat();
        let two = level_load(&spike, 100);
        assert_eq!(
            two,
            Levelled {
                served: 2_000,
                rejected: 2_000,
                peak_depth: 2_000,
                cleared_after_seconds: 35,
                max_wait_seconds: 20
            }
        );
        let four = level_load(&spike, 200);
        assert_eq!(
            (
                four.peak_depth,
                four.cleared_after_seconds,
                four.max_wait_seconds
            ),
            (1_000, 16, 5)
        );
    }

    #[test]
    fn redelivery_reorders_a_partition_keeps_order_a_new_group_replays() {
        let (clock, mut b) = broker();
        b.subscribe("orders", "shipping");
        for e in ["created", "paid", "shipped"] {
            b.publish("orders", &format!("order 7 {e}"), Some("order-7"));
        }
        let mut seen = Vec::new();
        for fail in [false, true, false] {
            let d = b.receive("shipping").unwrap();
            if !fail {
                b.ack("shipping", &d.id);
                seen.push(d.body);
            }
        }
        clock.set(30_000);
        seen.push(body(b.receive("shipping")));
        assert_eq!(seen, ["order 7 created", "order 7 shipped", "order 7 paid"]);

        let mut log = PartitionedLog::new(4);
        for e in ["created", "paid", "shipped"] {
            log.append("order-7", &format!("order 7 {e}"));
        }
        let p = partition_for("order-7", 4);
        let (mut in_order, mut failed_once) = (Vec::new(), false);
        while let Some(m) = log.poll("shipping", p) {
            if m.ends_with("paid") && !failed_once {
                failed_once = true; // no commit: the same message comes back
                continue;
            }
            in_order.push(m);
            log.commit("shipping", p);
        }
        assert_eq!(
            in_order,
            ["order 7 created", "order 7 paid", "order 7 shipped"]
        );
        assert_eq!(log.poll("analytics", p).as_deref(), Some("order 7 created"));
    }

    #[test]
    fn a_key_always_lands_in_the_same_partition() {
        let mut counts = [0; 4];
        for i in 0..10_000 {
            counts[partition_for(&format!("order-{i}"), 4)] += 1;
        }
        assert!(
            counts.iter().all(|&n: &i32| (n - 2_500).abs() < 200),
            "{counts:?}"
        );
    }

    #[test]
    fn a_sync_channel_pushes_back() {
        let (tx, rx) = mpsc::sync_channel::<u32>(3);
        let accepted: Vec<bool> = (1..=4).map(|n| tx.try_send(n).is_ok()).collect(); // Err(Full) for the fourth
        assert_eq!(accepted, [true, true, true, false]);
        assert_eq!(rx.try_iter().collect::<Vec<_>>(), [1, 2, 3]);

        let puts = Arc::new(AtomicU32::new(0));
        let counted = puts.clone();
        let producer = std::thread::spawn(move || {
            for n in 1..=5 {
                tx.send(n).unwrap(); // waits while the channel is full
                counted.fetch_add(1, Ordering::SeqCst);
            }
        });
        let wait_for = |n| {
            while puts.load(Ordering::SeqCst) < n {
                std::thread::yield_now()
            }
        };
        wait_for(3); // it can't get past 3 until something is taken
        assert_eq!(rx.recv().unwrap(), 1);
        wait_for(4);
        assert_eq!(puts.load(Ordering::SeqCst), 4); // and not past 4 until the next take
        assert_eq!(rx.iter().take(4).collect::<Vec<_>>(), [2, 3, 4, 5]);
        producer.join().unwrap();
    }
}
```

**Lab:** [`labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/04-messaging-and-async/labs/rust). `python3 labs/run.py messaging-and-async/rust`.

## 8. C#

`Broker` is a class with a primary constructor, and `Receive` returns `Delivery?`. `LevelLoad` queues `int[]` pairs, because a tuple in a `Queue<T>` is a copy and can't be changed in place. The bounded queue is `Channel.CreateBounded` with `FullMode = Wait`: `TryWrite` refuses and `WriteAsync` waits. Changing `FullMode` to `DropOldest` would give the lesson's third choice. It runs in the .NET SDK container.

```csharp
// A small in-memory message broker: queues, topics, redelivery, a dead-letter queue, a partitioned log and load
// levelling. The same numbers as the TypeScript lab. The bounded queue is System.Threading.Channels.

public record Delivery(string Id, string Body, string? Key, int Attempt);

/// <summary>Subscriptions are queues; a topic copies each message into every subscription. At-least-once delivery.</summary>
public sealed class Broker(Func<long> now, long visibilityMs, int maxAttempts)
{
    private sealed class Stored(string id, string body, string? key)
    {
        public string Id { get; } = id;
        public string Body { get; } = body;
        public string? Key { get; } = key;
        public int Attempts { get; set; }
        public long VisibleAt { get; set; }
    }

    private readonly Dictionary<string, List<string>> _subscribers = [];
    private readonly Dictionary<string, List<Stored>> _queues = [];
    private readonly Dictionary<string, List<Stored>> _dead = [];
    private int _nextId = 1;

    public void Subscribe(string topic, string subscription)
    {
        if (!_subscribers.TryGetValue(topic, out var list)) _subscribers[topic] = list = [];
        list.Add(subscription);
        _queues[subscription] = [];
        _dead[subscription] = [];
    }

    /// <summary>With no subscribers, nobody keeps the message.</summary>
    public string Publish(string topic, string body, string? key = null)
    {
        var id = $"m{_nextId++}";
        foreach (var s in _subscribers.GetValueOrDefault(topic) ?? []) _queues[s].Add(new Stored(id, body, key));
        return id;
    }

    public Delivery? Receive(string subscription)
    {
        var queue = _queues[subscription];
        for (var i = 0; i < queue.Count; i++)
        {
            var m = queue[i];
            if (m.VisibleAt > now()) continue; // a consumer has it
            if (m.Attempts >= maxAttempts)
            {
                queue.RemoveAt(i--); // poison: stop retrying it
                _dead[subscription].Add(m);
                continue;
            }
            m.Attempts++;
            m.VisibleAt = now() + visibilityMs;
            return new Delivery(m.Id, m.Body, m.Key, m.Attempts);
        }
        return null;
    }

    public void Ack(string subscription, string id) => _queues[subscription].RemoveAll(m => m.Id == id);

    public int Depth(string subscription) => _queues[subscription].Count;

    public IReadOnlyList<string> DeadLetters(string subscription) => _dead[subscription].Select(m => m.Body).ToList();
}

public static class Messages
{
    /// <summary>Skips a message ID it has already processed.</summary>
    public static Func<Delivery, string> Idempotent(Action<string> handle, ISet<string> seen) => d =>
    {
        if (seen.Contains(d.Id)) return "duplicate";
        handle(d.Body);
        seen.Add(d.Id);
        return "processed";
    };

    /// <summary>The same stable hash as the TypeScript lab; string.GetHashCode() changes every run.</summary>
    public static int PartitionFor(string key, int partitions)
    {
        var h = 0x811c9dc5u;
        foreach (var c in key) h = (h ^ c) * 0x01000193;
        h = (h ^ (h >> 16)) * 0x85ebca6b;
        h = (h ^ (h >> 13)) * 0xc2b2ae35;
        return (int)((h ^ (h >> 16)) % (uint)partitions);
    }

    public record Levelled(int Served, int Rejected, int PeakDepth, int ClearedAfterSeconds, int MaxWaitSeconds);

    public static Levelled LevelLoad(int[] arrivals, int perSecond)
    {
        var served = arrivals.Sum(a => Math.Min(a, perSecond));
        var rejected = arrivals.Sum(a => Math.Max(0, a - perSecond));
        var waiting = new Queue<int[]>(); // {arrival second, count}, oldest first; arrays so the count can change in place
        int depth = 0, peakDepth = 0, maxWait = 0, cleared = 0;
        for (var second = 0; second < arrivals.Length || depth > 0; second++)
        {
            var a = second < arrivals.Length ? arrivals[second] : 0;
            if (a > 0) waiting.Enqueue([second, a]);
            depth += a;
            for (var capacity = perSecond; capacity > 0 && waiting.Count > 0;)
            {
                var oldest = waiting.Peek();
                var n = Math.Min(capacity, oldest[1]);
                oldest[1] -= n;
                capacity -= n;
                depth -= n;
                maxWait = Math.Max(maxWait, second - oldest[0]);
                if (oldest[1] == 0) waiting.Dequeue();
            }
            peakDepth = Math.Max(peakDepth, depth);
            if (depth > 0) cleared = second + 2;
        }
        return new(served, rejected, peakDepth, cleared, maxWait);
    }
}

/// <summary>Kafka-like: messages are kept; each consumer group has its own offset per partition.</summary>
public sealed class PartitionedLog(int count)
{
    private readonly List<string>[] _partitions = Enumerable.Range(0, count).Select(_ => new List<string>()).ToArray();
    private readonly Dictionary<string, int[]> _offsets = [];

    public int Append(string key, string body)
    {
        var p = Messages.PartitionFor(key, _partitions.Length);
        _partitions[p].Add(body);
        return p;
    }

    public string? Poll(string group, int partition)
    {
        var offset = OffsetsFor(group)[partition];
        return offset < _partitions[partition].Count ? _partitions[partition][offset] : null;
    }

    public void Commit(string group, int partition) => OffsetsFor(group)[partition]++;

    private int[] OffsetsFor(string group) =>
        _offsets.TryGetValue(group, out var o) ? o : _offsets[group] = new int[_partitions.Length]; // a new group starts at 0
}
```

```csharp
// Checks: the same numbers as every other language.
using System.Threading.Channels;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

long clock = 0;
Broker NewBroker() => new(() => Interlocked.Read(ref clock), 30_000, 3);

var b = NewBroker();
b.Subscribe("orders", "invoices");
b.Subscribe("orders", "analytics");
b.Publish("orders", "order 1");
b.Publish("orders", "order 2");
Check(b.Receive("invoices")?.Body == "order 1" && b.Receive("invoices")?.Body == "order 2" && b.Receive("invoices") is null, "one consumer each");
Check(b.Receive("analytics")?.Body == "order 1" && b.Receive("analytics")?.Body == "order 2", "every subscription");
b.Publish("refunds", "refund 1");
Check(b.Depth("invoices") + b.Depth("analytics") == 4, "nobody keeps refunds");

clock = 0;
var r = NewBroker();
r.Subscribe("orders", "invoices");
r.Publish("orders", "order 1");
Check(r.Receive("invoices")?.Attempt == 1 && r.Receive("invoices") is null, "hidden while worked on");
clock = 30_000;
Check(r.Receive("invoices")?.Attempt == 2, "redelivered");
clock = 60_000;
Check(r.Receive("invoices")?.Attempt == 3, "redelivered again");
clock = 90_000;
Check(r.Receive("invoices") is null && r.DeadLetters("invoices").SequenceEqual(["order 1"]) && r.Depth("invoices") == 0, "dead-lettered");

foreach (var safe in new[] { false, true })
{
    clock = 0;
    var p = NewBroker();
    p.Subscribe("orders", "payments");
    p.Publish("orders", "charge £40 for order 1");
    var charges = 0;
    Action<string> charge = _ => charges++;
    var once = Messages.Idempotent(charge, new HashSet<string>());
    Action<Delivery> handle = safe ? d => once(d) : d => charge(d.Body);
    handle(p.Receive("payments")!); // charged, then a crash before the ack
    clock = 30_000;
    var again = p.Receive("payments")!;
    handle(again);
    p.Ack("payments", again.Id);
    Check(charges == (safe ? 1 : 2), (safe, charges));
}

int[] spike = [.. Enumerable.Repeat(300, 10), .. Enumerable.Repeat(20, 50)];
Check(Messages.LevelLoad(spike, 100) == new Messages.Levelled(2_000, 2_000, 2_000, 35, 20), Messages.LevelLoad(spike, 100));
var four = Messages.LevelLoad(spike, 200);
Check(four.PeakDepth == 1_000 && four.ClearedAfterSeconds == 16 && four.MaxWaitSeconds == 5, four);

clock = 0;
var s = NewBroker();
s.Subscribe("orders", "shipping");
foreach (var e in new[] { "created", "paid", "shipped" }) s.Publish("orders", $"order 7 {e}", "order-7");
var seen = new List<string>();
foreach (var fail in new[] { false, true, false })
{
    var d = s.Receive("shipping")!;
    if (fail) continue;
    seen.Add(d.Body);
    s.Ack("shipping", d.Id);
}
clock = 30_000;
seen.Add(s.Receive("shipping")!.Body);
Check(seen.SequenceEqual(["order 7 created", "order 7 shipped", "order 7 paid"]), string.Join(", ", seen));

var log = new PartitionedLog(4);
foreach (var e in new[] { "created", "paid", "shipped" }) log.Append("order-7", $"order 7 {e}");
var part = Messages.PartitionFor("order-7", 4);
var inOrder = new List<string>();
var failedOnce = false;
for (var m = log.Poll("shipping", part); m is not null; m = log.Poll("shipping", part))
{
    if (m.EndsWith("paid") && !failedOnce)
    {
        failedOnce = true; // no commit: the same message comes back
        continue;
    }
    inOrder.Add(m);
    log.Commit("shipping", part);
}
Check(inOrder.SequenceEqual(["order 7 created", "order 7 paid", "order 7 shipped"]), string.Join(", ", inOrder));
Check(log.Poll("analytics", part) == "order 7 created", "a new group replays");

var counts = new int[4];
for (var i = 0; i < 10_000; i++) counts[Messages.PartitionFor($"order-{i}", 4)]++;
Check(counts.All(n => Math.Abs(n - 2_500) < 200), string.Join(", ", counts));

// A bounded channel pushes back: TryWrite refuses when full, WriteAsync waits.
var q = Channel.CreateBounded<int>(new BoundedChannelOptions(3) { FullMode = BoundedChannelFullMode.Wait });
Check(new[] { 1, 2, 3, 4 }.Select(n => q.Writer.TryWrite(n)).SequenceEqual([true, true, true, false]), "fourth refused");
Check(await q.Reader.ReadAsync() == 1 && await q.Reader.ReadAsync() == 2 && await q.Reader.ReadAsync() == 3, "drained");
var puts = 0;
var producer = Task.Run(async () =>
{
    for (var n = 1; n <= 5; n++)
    {
        await q.Writer.WriteAsync(n); // waits while the channel is full
        Interlocked.Increment(ref puts);
    }
});
while (Volatile.Read(ref puts) < 3) await Task.Delay(1); // it can't get past 3 until something is read
Check(await q.Reader.ReadAsync() == 1, "first out");
while (Volatile.Read(ref puts) < 4) await Task.Delay(1);
Check(Volatile.Read(ref puts) == 4, "one out, one more in");
for (var i = 2; i <= 5; i++) Check(await q.Reader.ReadAsync() == i, i);
await producer;
Console.WriteLine("all messaging checks passed");
```

**Lab:** [`labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/04-messaging-and-async/labs/csharp). `python3 labs/run.py messaging-and-async/csharp`.

## Common pitfalls

1. **An unbounded in-process queue.** `asyncio.Queue()` with no `maxsize`, a Go slice used as a queue, `LinkedBlockingQueue()` with no capacity, `mpsc::channel()` and `Channel.CreateUnbounded` all grow without limit. Give them a size.
2. **Testing a blocked producer with a sleep.** Wait for a count that can't overshoot, or use `synctest`.
3. **Making the channel outside the `synctest` bubble.** `synctest.Wait()` then never returns.
4. **Mixing Kafka clients on one topic without matching partitioners.** Java and librdkafka disagree by default, which breaks per-key order.
5. **Using the language's built-in hash for partitions.** Python's and C#'s string hashes change every run, and Rust's `HashMap` hasher is seeded randomly.

## Check your understanding

1. Which of the six languages has "drop the oldest when full" built into its bounded queue?
2. Why is "wait until the put count reaches 3" a reliable test that the producer is blocked, and not a timing gamble?
3. Why does the Go bounded-queue test hang if `q` is made before `synctest.Test`?
4. A Java producer and a Python `confluent-kafka` producer both send events for order 7 to one topic. What can go wrong, and what's the fix?
5. Why does the Rust test share the clock through `Rc<Cell<u64>>` rather than a plain `u64`?

<details>
<summary>Answers — after your attempt</summary>

1. C#: `Channel.CreateBounded` with `BoundedChannelFullMode.DropOldest`.
2. The count goes up only after a put succeeds, and with capacity 3 and nothing taken, a fourth put can't succeed. So the count can reach 3 and can never reach 4: once it's 3, the producer is necessarily waiting on the fourth put.
3. `synctest.Wait()` waits for every goroutine in the bubble to be durably blocked. A send on a channel made outside the bubble might be completed by something outside the test, so it doesn't count, and `Wait` keeps waiting.
4. The two clients choose partitions with different hash functions by default (murmur2 in Java, CRC32 in librdkafka), so order 7's events can land in two partitions and be read out of order. Configure `partitioner=murmur2_random` in the librdkafka client.
5. The broker's clock closure and the test both need the time: the closure reads it, and the test changes it. Rust allows changing a value shared by two owners only through interior mutability such as `Cell`, and `Rc` lets both own it.

</details>

## Practice — independent task

**Add "drop the oldest" to your language's bounded queue.**

1. Wrap your language's queue (or, in C#, try `DropOldest` first and read what it does) in a type with `putDroppingOldest(item)`: if the queue is full, remove the oldest item, then add the new one, and return what was dropped.
2. Test it: with capacity 3, put 1–5; the queue holds 3, 4, 5, and the drops were 1 and 2.
3. Decide what happens if a consumer takes an item at the same moment as a drop, and make your test cover it, or explain why your language makes it impossible.

**Done when:** your test passes several runs in a row, and you can name one kind of data where dropping the oldest is right and one where it would be a bug.

## Before moving on

You can name your language's bounded queue and its refusing and waiting operations, test a blocked producer without sleeping, and keep Kafka keys on the same partition across languages.

**Recap.** The broker translates line for line. The bounded queue is each language's own: `asyncio.Queue`, a buffered channel, `ArrayBlockingQueue`, `sync_channel`, `Channel.CreateBounded`, each with a refusing "try" form and a waiting form. Only C# can drop the oldest out of the box. Test a blocked producer with a count that can't overshoot, `synctest` (with the channel made inside the bubble) or the thread's state, never a sleep. And when several languages produce to one Kafka topic, make their partitioners agree.

## Related

- [[architecture/02-building-blocks/04-messaging-and-async/index|Messaging and async]]: the main lesson
- [[architecture/02-building-blocks/05-communication/in-other-languages|Communication in other languages]]: the synchronous side, in the same languages
- [[architecture/03-architectural-patterns/02-resilience-patterns/in-other-languages|Resilience patterns in other languages]]: bounded concurrency and fairness
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ (Java)]]: a real broker from Java
