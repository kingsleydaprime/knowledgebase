# Distributed Processing — Spark and Beyond

**[Advanced]** — processing data too big for one machine, the lineage of the idea, and the honest question of whether you need it.

## The kid version first

Some datasets are too big to process on one computer. The solution: **split the data across many machines, run the same computation on each piece in parallel, then combine the results.** One machine counting a trillion rows takes forever; a hundred machines each counting ten billion takes a hundredth of the time.

The catch is that coordinating a hundred machines — moving data between them, handling the ones that crash — is where all the difficulty lives.

## The heritage: MapReduce

The idea that started modern big data (Google, 2004). Two steps:

```
MAP    — each machine processes its chunk, emitting (key, value) pairs
SHUFFLE — pairs with the same key are moved to the same machine  ← the expensive part
REDUCE — each machine aggregates the values for its keys
```

Counting words across a billion documents: **map** each document to `(word, 1)` pairs, **shuffle** so all `(the, 1)`s land together, **reduce** by summing. **The programming model's power is that it hides the distribution** — you write map and reduce, the framework handles splitting, scheduling, moving data, and re-running failed tasks.

**Hadoop MapReduce** (open-source, 2006) made this mainstream and defined an era. It's now largely historical — too slow (it wrote to disk between every step) and too clunky — but **the mental model is exactly right**, and the shuffle is still the thing that dominates performance.

## Spark — what replaced it

Apache Spark kept the model and fixed the speed by **keeping data in memory between steps** instead of writing to disk each time — 10–100× faster for multi-step jobs. It's the dominant distributed processing engine.

Spark's key ideas:

**The DataFrame** — a distributed table with a SQL-like API. You express *what* you want; Spark's optimiser (Catalyst) plans *how* → [[databases/07-join-algorithms-and-the-optimiser|query optimisers]]:

```python
df = spark.read.parquet("s3://data/orders/")
result = (df.filter(df.status == "completed")
            .groupBy("region")
            .agg(sum("amount").alias("revenue")))
result.write.parquet("s3://out/revenue/")
```

**Lazy evaluation** — nothing runs until an *action* (write, count, collect). Spark builds the whole plan first, then optimises the entire chain — so it can push filters down, combine steps, and avoid materialising intermediate results.

**Lineage and fault tolerance** — Spark records how each partition was derived (its lineage), so if a machine dies, it **recomputes just the lost partitions** from their inputs rather than restarting the job. This is how it survives failures at scale → [[architecture/04-distributed-systems/README|distributed systems]].

## The shuffle — where jobs go to die

The single most important performance concept. **A shuffle moves data across the network to regroup it** — required by `groupBy`, `join`, and `distinct`, because rows that must be combined are scattered across machines.

Shuffles are slow: network I/O, disk spills, serialisation. So the craft of Spark performance is **minimising and taming shuffles**:

- **Data skew** — if one key has 90% of the rows (one huge customer), one machine gets 90% of the work while 99 sit idle. **The number-one Spark performance problem**, and it's why partition-key choice matters → [[architecture/04-distributed-systems/13-partitioning|partitioning]]
- **Broadcast joins** — if one side of a join is small, ship it to every machine instead of shuffling both. A huge speedup, and Spark does it automatically below a size threshold
- **Partition count** — too few underuses the cluster; too many drowns in overhead

**"Why is my Spark job slow?" is almost always a shuffle or a skew.**

## When you actually need this — the honest question

**This is the section most tutorials skip, and it matters most.**

Distributed processing is expensive: a cluster to run and pay for, more complex code, harder debugging, and the shuffle tax. **You should reach for it only when the data genuinely doesn't fit on one machine** — and one machine is bigger than you think:

- A cloud VM with **1–2 TB of RAM** is routine and cheap by the hour
- **DuckDB** and **Polars** process tens to hundreds of GB on a single node, fast, with no cluster, no JVM, no shuffle → [[data-engineering/02-warehouses-lakes-and-lakehouses|DuckDB]]
- A **cloud warehouse** (BigQuery, Snowflake) handles enormous analytical queries without you managing any cluster at all

**The ["Big Data is Dead"](https://motherduck.com/blog/big-data-is-dead/) argument:** the median company's "big data" fits comfortably on one machine, and reaching for Spark by reflex buys you a distributed system's complexity for a single-machine problem. **Measure your data size first.** Under ~100 GB, a single-node tool is almost certainly faster to build, cheaper to run, and easier to debug.

**Use Spark/distributed processing when:** the data is genuinely terabyte-plus, you're already invested in the Spark ecosystem, or you need Spark's specific streaming or ML-at-scale features.

## The landscape

| | For |
|---|---|
| **Spark** | The default for genuinely large distributed processing. Batch and streaming |
| **Databricks** | Managed Spark, plus the lakehouse. The commercial home of Spark |
| **DuckDB / Polars** | **Single-node, and the right first answer for most workloads** |
| **Dask** | Distributed Python/pandas — familiar API, smaller ecosystem |
| **Flink** | Streaming-first, if real-time is the point → [[data-engineering/03-batch-and-streaming\|streaming]] |
| **Ray** | Distributed Python for ML/compute, big in [[ai-ml/README\|ML]] training |
| **Trino / Presto** | Distributed SQL query engine over lakes — query without moving data |

## Key insight

**MapReduce's model — split, process in parallel, shuffle to regroup, combine — is still exactly how distributed processing works, and the shuffle is still where the cost and the bugs live.** Spark made it fast by staying in memory and fault-tolerant by tracking lineage, but the genuinely important skill is knowing *when not to reach for it*: most datasets fit on one large machine, where DuckDB or a warehouse is simpler, cheaper and faster than a cluster. Measure the data before you distribute it.

## Related
- [[data-engineering/02-warehouses-lakes-and-lakehouses|warehouses and lakes]] — DuckDB, and the single-node case
- [[data-engineering/03-batch-and-streaming|batch and streaming]] — Spark does both
- [[architecture/04-distributed-systems/13-partitioning|partitioning]] — the skew problem
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel computing]] — parallelism, one layer down

*Source: [reference] — Aug 2026.*
