# Kafka and Event Streaming

**[Advanced]** — the log as a central abstraction, and why one idea became the backbone of modern data infrastructure.

## The kid version first

Imagine a shared notebook that many programs write into and many others read from. Writers only ever *append* to the end. Readers each keep their own bookmark and read forward at their own pace — a fast reader and a slow reader don't interfere, and a reader that crashes just resumes from its bookmark.

**That append-only shared notebook is Kafka**, and it turns out that almost every data-movement problem — messaging, event streaming, CDC, decoupling services — is solved by putting a log in the middle.

## The log is the idea

Kafka is "just" a distributed, durable, append-only **log**. That sounds unambitious until you see what the log's properties give you → [[architecture/04-distributed-systems/12-the-log-and-state-machines|the log and state machines]]:

- **Append-only** — writes are fast (no random I/O, no updates), and history is immutable
- **Ordered** — records have a fixed position (offset); order is preserved within a partition
- **Durable** — persisted to disk and replicated, so it survives crashes
- **Replayable** — a new consumer can read from the beginning; the data isn't consumed-and-gone like a queue

**That last property is the profound one.** A traditional message queue deletes a message once it's read. A log *keeps* everything, and each consumer tracks its own position. So you can add a new consumer next year that reprocesses two years of history — which is exactly what makes [[data-engineering/03-batch-and-streaming|Kappa architecture]] (reprocess by replay) possible.

## The anatomy

```
   TOPIC "orders"  (a named log, split into partitions for parallelism)
   ┌──────────── partition 0 ────────────┐
   │ [0][1][2][3][4][5] ...  ← offsets    │  ← producers APPEND to the end →
   ├──────────── partition 1 ────────────┤
   │ [0][1][2][3] ...                     │
   └──────────────────────────────────────┘
        ▲                    ▲
   consumer group A     consumer group B    ← each group has its own position
```

- **Topic** — a named stream of records ("orders", "clicks")
- **Partition** — a topic is split into partitions so it can be written and read in parallel across machines. **This is where throughput comes from**, and the source of the main subtlety
- **Offset** — a record's position in a partition. **Consumers commit their offset** — "I've processed up to here" — so a crash resumes cleanly
- **Producer** — appends records, choosing a partition (often by hashing a key)
- **Consumer group** — a set of consumers sharing the work of a topic; each partition goes to exactly one consumer in the group, so adding consumers scales reading

## Ordering — the thing everyone gets wrong

**Kafka guarantees order *within a partition*, not across partitions.**

So if order matters — all events for one user must be processed in sequence — **you must send them to the same partition**, by keying on the user ID:

```
producer.send("orders", key=user_id, value=event)
   → same user_id → same partition → ordered
   → different users → different partitions → parallel, no cross-order guarantee
```

**Getting the partition key wrong is the classic Kafka bug.** Key by user and one user's events stay ordered but a hot user creates a hot partition (skew); key randomly and you get even load but lose per-entity ordering. **The partition key is a design decision with real consequences**, not a default → [[architecture/04-distributed-systems/13-partitioning|partitioning]].

## Delivery guarantees

Kafka can be configured for each, and the choice is a real trade → [[data-engineering/04-ingestion-and-change-data-capture|delivery guarantees]]:

- **At-least-once** (default, common) — a record is never lost but may be redelivered on retry. Pair with idempotent consumers
- **At-most-once** — no duplicates, possible loss. Rarely wanted
- **Exactly-once** (EOS) — Kafka's transactions + idempotent producer give genuine exactly-once *within Kafka-to-Kafka* processing. Real, but adds overhead and doesn't automatically extend to external systems

**"Exactly-once end-to-end" is usually approximated** as at-least-once delivery into an idempotent target — cheaper, and correct in effect → [[data-engineering/08-orchestration|idempotency]].

## What Kafka is actually used for

One tool, several jobs, which is why it's everywhere:

1. **Decoupling services** — service A appends events, services B/C/D consume independently. A doesn't know or care who reads. **The backbone of event-driven architecture** → [[architecture/03-architectural-patterns/README|architectural patterns]]
2. **The streaming ingestion layer** — clicks, IoT, telemetry land in Kafka, then flow to the warehouse and to real-time processors → [[data-engineering/03-batch-and-streaming|streaming]]
3. **CDC transport** — Debezium publishes database changes to Kafka topics → [[data-engineering/04-ingestion-and-change-data-capture|CDC]]
4. **Event sourcing** — the log *is* the source of truth; current state is a projection you rebuild by replaying → [[architecture/04-distributed-systems/12-the-log-and-state-machines|the log]]

## The ecosystem and the alternatives

- **Kafka Connect** — a framework of pre-built source/sink connectors (DB in, S3 out) so you don't write plumbing
- **Schema Registry** — enforces a schema (Avro/Protobuf) on topics, so a producer can't silently break every consumer by changing the data shape. **Essential in practice** — without it, one bad deploy poisons the stream
- **ksqlDB / Kafka Streams** — process streams with SQL or a library, in place

**Alternatives worth knowing:** **AWS Kinesis** and **Google Pub/Sub** (managed, cloud-native, less to operate); **Redpanda** (Kafka-compatible, C++, no JVM/ZooKeeper, faster and simpler to run); **Apache Pulsar** (separates serving and storage). **Kafka is operationally heavy** — a managed option (Confluent Cloud, MSK, Redpanda Cloud) is the sane default for most teams, because running Kafka well is a genuine specialty.

## Key insight

**Kafka is a distributed, durable, replayable log, and that single abstraction solves messaging, streaming, CDC transport and service decoupling all at once** — because keeping every event (rather than consuming-and-deleting) lets any number of consumers read at their own pace and replay history. The one thing to get right is partitioning: order is guaranteed only within a partition, so the partition key is a deliberate design choice trading ordering against even load. And unless you enjoy operations, run it managed.

## Related
- [[architecture/04-distributed-systems/12-the-log-and-state-machines|the log and state machines]] — the theory Kafka embodies
- [[architecture/04-distributed-systems/13-partitioning|partitioning]] — the ordering/skew trade
- [[data-engineering/03-batch-and-streaming|batch and streaming]] — what consumes these streams
- [[data-engineering/04-ingestion-and-change-data-capture|ingestion and CDC]] — a major producer

*Source: [reference] — Aug 2026.*
