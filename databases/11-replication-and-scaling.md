# Replication and Scaling

**[Advanced]** — Read replicas, failover, partitioning, and the order in which you should actually try things.

> **The distributed-systems theory is in [[architecture/04-distributed-systems/README|architecture/04-distributed-systems]]** — consensus, consistency models, CAP, partitioning strategies. **This note is the database-operator's view**: what the knobs do and what breaks.

## Scale up first

**The advice that saves the most time**, and it's unfashionable.

**Modern single machines are enormous.** 128 cores, several TB of RAM, NVMe at millions of IOPS. **A well-tuned Postgres on one big machine handles tens of thousands of transactions per second and terabytes of data.**

**Before distributing anything, check you've done the cheap things:**

1. **Add the missing index.** More outages have been fixed by one index than by any amount of sharding
2. **Fix the N+1 queries.** → [[databases/12-operating-a-database|ORMs]]
3. **Add a connection pooler.** Often a several-fold improvement on its own
4. **Cache what's hot** — Redis in front of expensive reads
5. **Tune the buffer pool, `work_mem`, `random_page_cost`**
6. **Buy a bigger machine.** Genuinely — an engineer-month costs more than a year of a larger instance

> **Distribution multiplies your failure modes.** Every sharded system has partial failures, cross-shard queries, rebalancing, and distributed transactions. **Exhaust vertical scaling first**, and when you do distribute, know exactly which limit forced it.

## Replication

**Copy the data to other machines.** The primary reason is **availability**; read scaling is a useful side effect.

**How the data is shipped:**

**Physical / WAL-based** — ship the write-ahead log; replicas replay it byte-for-byte. **Postgres streaming replication.**

*Exact copy, low overhead, and the replica must be the same major version and architecture.* **You cannot replicate a subset.**

**Logical** — ship row-level changes (`INSERT`/`UPDATE`/`DELETE`) rather than physical page changes. **Postgres logical replication, MySQL row-based binlog.**

*Cross-version, selective tables, and you can transform on the way.* **Higher overhead**, and it doesn't replicate DDL in Postgres.

**Statement-based** — ship the SQL. **Compact and dangerous**: `UPDATE t SET x = random()` produces different results on each replica. MySQL defaults to row-based now for exactly this reason.

### Synchronous vs asynchronous

| | Async | Sync |
|---|---|---|
| Commit waits for replica? | **no** | **yes** |
| Write latency | **low** | + network round trip |
| Data loss on primary failure | **possible** | none (to the sync replica) |
| Availability if replica dies | unaffected | **primary blocks** |

> **The trap with synchronous replication: if the sync replica goes down, your primary stops accepting writes.** You made durability stronger and availability weaker. **That's CAP, concretely.** → [[architecture/04-distributed-systems/02-theoretical-limits|CAP]]
>
> **The usual answer is quorum**: `synchronous_standby_names = 'ANY 1 (r1, r2, r3)'` — wait for *any one* of three. **You get durability without a single replica being a hard dependency.**

**Replication lag is the thing to monitor.** Async replicas are always behind — normally milliseconds, but a long transaction, a big write burst, or a slow replica can push it to minutes.

### Read replicas, and the consistency problem

**Routing reads to replicas scales reads.** It also introduces a real bug class:

```
POST /orders    → writes to primary
GET  /orders    → reads from replica → order isn't there yet
```

**"I saved it and it disappeared."** Read-your-writes violated by replication lag.

**The fixes, in order of preference:**

**Read from the primary after a write** for that user, for a few seconds. Simple and effective.

**Sticky routing** — a user who has written recently is pinned to the primary.

**Wait for the LSN** — record the WAL position of your write and require the replica to have reached it. **Precise, and it costs latency.**

**Accept staleness where it's genuinely fine** — analytics, dashboards, public content.

→ [[architecture/04-distributed-systems/04-consistency-models|Consistency Models]]

## Failover

**What happens when the primary dies**, and it's harder than it looks.

**Manual** — a human promotes a replica. Slow, and safe.

**Automatic** — Patroni, repmgr, or a managed service handles it. **Fast, and it introduces split-brain risk.**

> **Split brain: the old primary isn't dead, just unreachable.** Now two nodes accept writes, and the divergence must eventually be resolved by throwing some away.
>
> **Prevention requires fencing** — a quorum-based decision (Patroni uses etcd/Consul) plus **STONITH**: forcibly stop the old primary before promoting. **A failover system without fencing is a data-loss system that hasn't triggered yet.**

**What must be handled:** promoting a replica, repointing the application (a VIP, DNS, or a proxy like PgBouncer/HAProxy), re-syncing the old primary (`pg_rewind`), and re-pointing the other replicas.

**Test it.** **A failover system never exercised does not work.** Schedule failovers deliberately.

## Partitioning and sharding

**Split the data across storage.** Two distinct things with confusingly similar names:

**Partitioning (within one database)** — one logical table, multiple physical tables, by range, list or hash.

**Genuinely useful and much less costly than sharding:**

- **Partition pruning** — the planner skips partitions the predicate excludes
- **`DROP PARTITION` for retention** — dropping last year's data is instant, versus a `DELETE` of a hundred million rows that bloats the table for days. **This alone justifies partitioning time-series tables**
- Smaller indexes per partition, and per-partition maintenance

**Costs:** the partition key must be in your queries (or you scan everything), unique constraints must include the partition key, and cross-partition joins are more expensive.

**Sharding (across machines)** — different rows on different servers.

**What you give up, and it's a lot:**

**Cross-shard joins** — either impossible, or a scatter-gather with an application-side merge.

**Cross-shard transactions** — need two-phase commit, which is slow and has its own failure modes. → [[architecture/04-distributed-systems/10-distributed-transactions|Distributed Transactions]]

**Global constraints** — a `UNIQUE` on email across shards requires coordination.

**Rebalancing** — adding a shard means moving data. **Consistent hashing** minimises movement. → [[architecture/04-distributed-systems/13-partitioning|Partitioning]]

**Hot shards** — one celebrity user, one popular tenant, and one shard carries the load.

> **Shard key choice is the decision you cannot easily reverse.** It determines which queries are cheap forever. **Pick one that appears in almost every query** — `tenant_id` in a multi-tenant application, `user_id` in a social product. **A shard key that isn't in your `WHERE` clause turns every query into a scatter-gather.**

**Alternatives worth considering first:** Citus (Postgres extension that shards for you), Vitess (MySQL), or a NewSQL database (CockroachDB, TiDB, Spanner) that handles distribution natively — **giving you distributed SQL with transactions, at the cost of higher latency per operation.**

## Connection pooling

**Underrated, and often the highest-leverage single change.**

**Postgres forks a process per connection**, each with its own memory. **A few hundred connections is a lot**; thousands will thrash the machine.

**Application connection pools help but don't solve it** — 20 app servers × 20 connections each = 400 connections.

**PgBouncer** sits in front and multiplexes:

| Mode | Behaviour |
|---|---|
| **Session** | connection held for the client session |
| **Transaction** | **connection returned after each transaction** — the useful one |
| Statement | returned after each statement; breaks transactions |

> **Transaction pooling lets 10,000 client connections share 50 server connections**, because most are idle at any moment. **The improvement is frequently several-fold.**
>
> **The catch: session state doesn't survive.** Prepared statements, `SET` variables, advisory locks, `LISTEN/NOTIFY` and temp tables break under transaction pooling, because you get a different backend each time. **Check your ORM and driver** — many need `prepareThreshold=0` or an equivalent.

**Rule of thumb:** `max_connections` around `2–4 × cores`, with a pooler in front. **More connections than that reduces throughput** — they contend rather than parallelise.

## Caching

**The other read-scaling lever.**

**Where to cache:** the database's own buffer pool (free, already there), the application layer (Redis/Memcached), or a CDN for anything public.

**Invalidation is the hard part**, and the strategies are:

**TTL** — simple, and serves stale data for up to the TTL.

**Write-through** — update the cache on write. Consistent, and it couples your write path to the cache.

**Explicit invalidation** — delete the key on write. **Correct until you miss one**, and you will.

**Change data capture** — invalidate from the replication stream. **Robust and more machinery** — Debezium is the standard tool.

**The failure modes worth naming:**

**Thundering herd / cache stampede** — a popular key expires and a thousand requests hit the database simultaneously. **Fix with a lock on regeneration, or probabilistic early expiry.**

**Cache penetration** — repeated requests for keys that don't exist bypass the cache entirely. **Cache the negative result.**

## The order to try things

**A rough escalation ladder**, and most systems never leave the first three rungs:

```
1. Indexes and query fixes         ← most problems die here
2. Connection pooling
3. Caching
4. Bigger machine
5. Read replicas
6. Partitioning (within one DB)
7. Sharding / distributed SQL      ← real complexity starts here
```

**Each step adds operational burden.** Stop as soon as the problem is solved, and **know which specific limit pushed you to the next rung** — "we're at 90% CPU on the largest instance available" is a reason; "we might need to scale someday" is not.

---

## Related
- [[architecture/04-distributed-systems/README|Distributed Systems]] — the theory: consensus, CAP, consistency
- [[databases/10-durability-and-recovery|Durability and Recovery]] — the WAL that replication ships
- [[databases/mysql-reference|MySQL Reference]] — §18, replication setup concretely
- [[databases/README|Databases map]]
