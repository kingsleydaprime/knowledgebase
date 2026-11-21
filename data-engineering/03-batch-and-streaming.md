---
id: 4c892b72-322d-4130-8571-cb85d37addd8
---

# Batch and Streaming

**[Intermediate]** — the two ways data moves, the real trade-off between them, and why the industry stopped maintaining both.

## The kid version first
<!-- bite: 987dca30-614e-40d3-9e1d-5ce70672b59a -->

**Batch:** collect data into a pile, then process the whole pile at once, on a schedule. *"Every night at 2am, process yesterday's orders."* Simple, cheap, and the answer is a few hours old.

**Streaming:** process each record the moment it arrives, forever. *"The instant an order is placed, update the dashboard."* Complex, more expensive, and the answer is seconds old.

**The question is never "which is better" — it's "how fresh does the answer need to be, and what will you pay for freshness."**

## The distinction that actually matters: bounded vs unbounded
<!-- bite: c8a38f4e-60b0-4db1-b760-988fa6592c35 -->

Beneath the two words is one real difference:

- **Batch data is bounded** — a finite dataset with a beginning and an end. "Yesterday's orders" is a complete, fixed set. You can sort it, count it, and know when you're done
- **Streaming data is unbounded** — an infinite sequence with no end. Orders never stop arriving. **You can never see "all" of it**, so questions like "the average" or "the top 10" require a *window* — "the average over the last 5 minutes"

**This is the whole conceptual difficulty of streaming.** Every operation you take for granted in batch — sort, count, join, dedupe — becomes subtle when the dataset is infinite and you only ever see part of it.

## The trade-off
<!-- bite: d74f0b09-152d-4871-a597-fc4dd009c86f -->

| | Batch | Streaming |
|---|---|---|
| Latency | Hours (scheduled) | Seconds |
| Throughput | **Very high** (bulk-optimised) | High, but per-record overhead |
| Complexity | **Low** | High |
| Cost | Lower (run and stop) | Higher (always on) |
| Reprocessing | **Trivial** — just re-run | Hard — replay the stream |
| Correctness | Easy — complete data | Subtle — late/out-of-order data |
| Use for | Reports, ML training, most things | Fraud detection, live dashboards, alerting |

**The honest default: use batch unless you have a specific reason not to.** Streaming is genuinely harder to build, run and debug, and **most "we need real-time" requirements dissolve into "we need it within a few minutes,"** which micro-batch handles at a fraction of the complexity. Reach for true streaming when the *value of the data decays in seconds* — fraud, trading, operational alerting, live personalisation.

## The hard problems in streaming
<!-- bite: d966a851-1379-4c06-b5d7-bee76366b5d0 -->

These are what make streaming a specialty:

**Windowing.** Since you can't aggregate an infinite stream, you aggregate over windows:
- **Tumbling** — fixed, non-overlapping ("each 5-minute block")
- **Sliding** — overlapping ("the last 5 minutes, updated every minute")
- **Session** — grouped by activity gaps ("a user's browsing session")

**Event time vs processing time — the classic streaming trap.** An event *happened* at one time (event time) but *arrives* at your system at another (processing time), possibly much later — a phone was offline in a tunnel and uploads an hour of events at once. **"How many orders in the 2–3pm window" must use event time**, or a delayed event lands in the wrong bucket and your numbers are wrong.

**Late and out-of-order data.** Events arrive late and out of sequence. A **watermark** is the system's estimate of "event time has progressed to here, so I'll assume no earlier events are still coming" — it decides when to close a window. Set it too tight and you drop late data; too loose and you wait forever. **This is the central tuning problem in streaming.**

**Exactly-once processing.** A record must be processed exactly once despite failures and retries — not zero times (data loss), not twice (double-counting). Genuinely hard in a distributed system, and the headline feature of modern streaming engines → [[data-engineering/05-kafka-and-event-streaming|Kafka]], [[architecture/04-distributed-systems/10-distributed-transactions|distributed transactions]].

## Lambda and Kappa — a piece of history worth knowing
<!-- bite: c32e303f-516c-40e4-b705-66ee8e10629b -->

**Lambda architecture** (~2011) ran *both*: a batch layer for correct, complete results and a streaming layer for fast, approximate ones, merged at query time. It worked, but **you maintained two codebases computing the same thing in two paradigms** — a notorious maintenance burden, and the two would drift and disagree.

**Kappa architecture** was the reaction: **just use streaming, and reprocess by replaying the stream from the start.** One codebase, one paradigm. It became viable once streaming engines could handle both real-time and replay well.

**Why this matters even though you won't build Lambda:** it explains the industry's direction — toward *unifying* batch and streaming under one model, so you write logic once and run it either way. **Apache Beam**, **Spark Structured Streaming** and **Flink** all pursue this "batch is just streaming over bounded data" unification, and it's the modern consensus.

## The engines
<!-- bite: 0d8c119a-219e-48c1-b2ca-aeeb0f1ab86b -->

| | For |
|---|---|
| **Apache Flink** | **The streaming-first engine** — true per-event processing, sophisticated windowing and state, exactly-once. The serious choice for real streaming |
| **Spark Structured Streaming** | Micro-batch (tiny frequent batches) with a streaming API. Easier if you already run Spark; higher latency than Flink → [[data-engineering/06-distributed-processing\|Spark]] |
| **Kafka Streams** | A library, not a cluster — stream processing embedded in your app, over Kafka |
| **Materialize / RisingWave** | Streaming SQL — incrementally maintained materialised views over streams. The rising, approachable option |

## Key insight
<!-- bite: 1efd58b4-8bec-457a-9dd5-27d62c912ac1 -->

**The batch/streaming choice is really the bounded/unbounded distinction, and freshness-versus-complexity is the trade you're making.** Batch is bounded and easy; streaming is unbounded, which turns every ordinary operation into a windowing, event-time and late-data problem. Default to batch — most "real-time" needs are actually "few-minute" needs — and the industry's clear direction is to *unify* the two so you write the logic once, which is why "batch is streaming over bounded data" is the framing worth carrying.

## Related
<!-- bite: b5f6b8c5-4d01-4abf-a236-5d12af50f18a -->
- [[data-engineering/05-kafka-and-event-streaming|Kafka and event streaming]] — the backbone of streaming
- [[data-engineering/06-distributed-processing|distributed processing]] — Spark for both
- [[architecture/04-distributed-systems/12-the-log-and-state-machines|the log and state machines]] — the theory under replay
- [[data-engineering/04-ingestion-and-change-data-capture|ingestion]] — where streams come from

*Source: [reference] — Aug 2026.*
