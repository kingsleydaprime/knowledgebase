# Build Your Own Redis

**[Intermediate]** — A natural follow-on from the HTTP server: the same socket handling, a much simpler protocol, and the focus moves to data structures, expiry and durability.

## What you're building

A server speaking the Redis protocol, holding data in memory, supporting the core commands, with expiry and persistence. By the end **the real `redis-cli` will connect to it and work** — that's the test that makes this satisfying.

**What you're deliberately not building:** Redis Cluster (sharding and slot migration), Lua scripting, modules, streams, or the full ~200-command surface. You want maybe 15 commands.

**Why this one:** it's the clearest possible demonstration that a famous piece of infrastructure is a hash map behind a socket. And unlike the HTTP server, the interesting problems are *after* the protocol — expiry, eviction, and the durability/performance tradeoff.

## What you need first

| You should know | Where |
|---|---|
| **Sockets and an accept loop** | [[build-your-own-shit/01-http-server\|guide 01]] — build that first |
| **Hash maps** — what they cost and why | [[foundations/dsa/04-data-structures/03-hash-maps\|dsa/03-hash-maps]] |
| **Event loops** — `epoll`/`kqueue` | [[foundations/os/08-io-models\|os/08]] |
| **`fsync` and durability** | [[foundations/os/07-filesystems-and-storage\|os/07]] — **the AOF milestone depends on this** |
| **Caching concepts** — TTL, eviction | [[architecture/02-building-blocks/02-caching\|caching]] |

**Do the HTTP server first.** It teaches the socket layer with easier debugging (text you can read in a browser), and this guide assumes it.

## The build order

### 1. RESP — the protocol

Redis's wire format, and it's refreshingly simple. Five types, each prefixed by one byte:

```
+OK\r\n                          simple string
-ERR unknown command\r\n         error
:1000\r\n                        integer
$5\r\nhello\r\n                  bulk string (length-prefixed)
$-1\r\n                          null bulk string
*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n  array
```

**Commands always arrive as an array of bulk strings.** `GET key` on the wire is:

```
*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n
```

Write a parser that turns bytes into a `Vec<String>`, and a serialiser for the reply types.

**Test:** feed it hand-written byte strings and check the parse. Then:

```bash
printf '*1\r\n$4\r\nPING\r\n' | nc localhost 6379
```

**Watch for:** bulk strings are **length-prefixed and binary-safe** — they may contain `\r\n`, NUL bytes, or arbitrary binary. Read exactly the stated number of bytes; don't scan for a delimiter. That's the key difference from HTTP parsing and it makes this *easier*, not harder.

Cap the array count and bulk length, or a malicious client declares a 4GB string and you allocate it.

### 2. PING, ECHO, and the command loop

Dispatch on the first array element (case-insensitively — `GET`, `get` and `Get` are all valid).

**Test — the milestone that matters:**

```bash
redis-cli -p 6379 ping
PONG
```

**Real `redis-cli` talking to your server.** If that works, your protocol handling is correct, and every later milestone gets tested through a proper client.

### 3. GET, SET, DEL, EXISTS

A hash map from string to string.

```
SET key value    → +OK
GET key          → $5\r\nvalue\r\n   (or $-1 for missing)
DEL key          → :1
EXISTS key       → :1 / :0
```

**Test:** `redis-cli set foo bar`, `redis-cli get foo`.

**Watch for:** keys and values are **binary-safe byte strings**, not text. Use a byte type (`Vec<u8>`, `[]byte`, `bytes`) rather than a UTF-8 string, or you'll corrupt binary values. This is a real bug in most first attempts.

### 4. Expiry

```
SET key value EX 60     set with a TTL
EXPIRE key 60
TTL key                 → seconds remaining, -1 no expiry, -2 doesn't exist
PERSIST key
```

**Test:** set a key with a 2-second TTL, confirm `GET` returns it, wait, confirm it's gone.

**Watch for — this is the first genuinely interesting design decision:**

**Lazy expiry** — check the timestamp on access, delete if expired. Simple, and a key nobody touches never gets freed.

**Active expiry** — periodically sample random keys and delete expired ones. Reclaims memory, costs CPU.

**Real Redis does both**, and its active cycle samples 20 random keys 10 times a second, repeating while more than 25% were expired. That algorithm is worth implementing — it's a nice example of a probabilistic approach beating an exhaustive one.

### 5. Concurrency

Now serve many clients. Options:

- **Thread per connection** — simplest, and you now need a lock around the map
- **Event loop, single-threaded** — **what real Redis does**, and the reason it needs no locks at all

> **Single-threaded is the interesting choice here.** Redis was famously fast *because* it was single-threaded — no locks, no contention, no context switching, and every command is atomic by construction. All the work is memory access; the bottleneck is the network, not the CPU.

**Test:** several `redis-cli` sessions at once. `redis-benchmark -p 6379 -t set,get -n 10000`.

**Watch for:** with an event loop you need the per-connection buffer state from [[build-your-own-shit/01-http-server|the HTTP guide]] — a command may arrive across several reads. Pipelining makes this sharper: a client can send ten commands before reading any reply, so **parse and execute every complete command in the buffer, not just the first.**

### 6. More data types

Where it stops being a toy hash map:

```
LPUSH/RPUSH/LRANGE/LPOP     lists       — a deque
SADD/SMEMBERS/SISMEMBER     sets        — a hash set
HSET/HGET/HGETALL           hashes      — a nested map
ZADD/ZRANGE/ZRANGEBYSCORE   sorted sets — the interesting one
```

**Sorted sets are the one to implement properly.** They need ordering by score *and* O(1) lookup by member, so real Redis uses a **skip list plus a hash map** — the skip list for range queries, the map for membership.

A skip list is a genuinely elegant structure: probabilistic balancing, much simpler to implement than a red-black tree, and comparable performance. → [[foundations/dsa/04-data-structures/08-heaps|heaps]] and [[foundations/dsa/04-data-structures/05-trees/01-trees|trees]]

**Test:** `redis-cli zadd leaderboard 100 alice 200 bob`, then `zrange leaderboard 0 -1 withscores`.

**Watch for:** each type needs its own commands to reject wrong-type keys — `LPUSH` on a string key must return `WRONGTYPE`, not corrupt it. That means values are a tagged union of types, which is the same shape as [[foundations/compilers/09-bytecode-and-virtual-machines|a VM's value type]].

### 7. Persistence

Two mechanisms, and the contrast between them is the lesson.

**RDB — point-in-time snapshot.** Serialise the whole dataset to a file periodically.

Real Redis `fork()`s and lets the child write the snapshot while the parent keeps serving — **copy-on-write means the child sees a frozen view for free.** That's a beautiful use of the OS primitive, and it has a real cost: if the parent takes heavy writes during the save, COW can approach a full memory copy. → [[foundations/os/04-virtual-memory|copy-on-write]]

**AOF — append-only log.** Append every write command to a file; replay it on startup.

```
*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n
```

The log is just RESP commands, so **replay is your existing command loop reading from a file instead of a socket** — a very satisfying reuse.

**Test:** write data, kill the server with `kill -9`, restart, confirm the data is there.

**Watch for — this is the durability milestone:**

```
appendfsync always     fsync every write    — slowest, safest
appendfsync everysec   fsync once a second  — the default; up to 1s of loss
appendfsync no         let the OS decide    — fastest, unbounded loss
```

**`write()` returning does not mean durable.** Without `fsync`, a `kill -9` loses nothing (the OS still has the buffer) but a power cut loses everything written since the last flush. Implementing all three modes and measuring the throughput difference is the most instructive part of this whole guide. → [[foundations/os/07-filesystems-and-storage|fsync]]

AOF grows forever, so real Redis **rewrites** it periodically — dumps current state as a minimal command set. Worth implementing; it's the same idea as log compaction.

### 8. Replication (optional)

```
REPLICAOF host port
```

The replica connects to the primary, requests a snapshot, then receives a live command stream.

**Test:** two instances, write to the primary, read from the replica.

**Watch for:** replication is **asynchronous** — the primary doesn't wait for replicas, so a failover can lose the last writes. That's not a bug, it's the CAP tradeoff made concrete. → [[architecture/04-distributed-systems/05-replication|Replication]]

## Per-language toolkit

| Milestone | C | C++ | Rust | Go | Python | JS/Node |
|---|---|---|---|---|---|---|
| **Sockets** | `<sys/socket.h>` | asio | `std::net` / **tokio** | `net` | `socket`/`asyncio` | `net` |
| **RESP parse** | by hand | by hand | by hand; `nom` | by hand; `bufio` | by hand | by hand |
| **Hash map** | write one, or `uthash` | `unordered_map` | `HashMap` | `map` | `dict` | `Map` |
| **Sorted set** | skip list by hand | `std::map` + map | `BTreeMap` + map | `btree` pkg | `sortedcontainers` | by hand |
| **Event loop** | `epoll` | asio | tokio | goroutines | `asyncio` | built in |
| **Persistence** | `write`/`fsync` | `fstream`+`fsync` | `File::sync_all` | `f.Sync()` | `os.fsync` | `fs.fsyncSync` |

**Language notes:**

**Go** — goroutines make the concurrent version trivial, which means you skip the event-loop lesson. Consider single-threaded with an explicit loop to learn what Redis actually does.

**Rust** — a good fit; the value type is a natural enum, and single-threaded means no `Arc<Mutex<>>` anywhere. → [[languages/03-rust/06-structs-enums-and-pattern-matching|enums]]

**C** — closest to real Redis (which is C), and you'll write your own hash map and skip list, which is the point.

**Python** — fastest to working; `dict` is your store and `asyncio` your loop. Excellent for understanding the protocol and expiry without fighting anything.

## The parts that will bite you

**Keys and values are binary, not text.** Use byte types throughout.

**Pipelining.** Clients send multiple commands before reading. Process every complete command in your buffer.

**Inline commands.** `redis-cli` mostly sends RESP arrays, but a raw `PING\r\n` typed into `nc` is also valid ("inline command" format). Support it or your `nc` testing fails confusingly.

**Case-insensitive command names.**

**Wrong-type errors.** `LPUSH` on a string key is `WRONGTYPE`, not a crash.

**Expiry on read.** A key past its TTL must be invisible even if the active cycle hasn't reached it.

**`fsync` is not `write`.** The whole durability milestone hinges on this.

**Integer replies vs bulk strings.** `DEL` returns `:1`; `GET` returns `$3\r\nfoo\r\n`. Sending the wrong reply type confuses clients in ways that look like data corruption.

## How to know it works

**The real client is the test:**

```bash
redis-cli -p 6379 ping
redis-cli -p 6379 set foo bar
redis-cli -p 6379 get foo
redis-cli -p 6379 --scan
redis-benchmark -p 6379 -t set,get -n 100000 -q
```

**`redis-benchmark` is a genuinely good stress test** — it pipelines, opens many connections, and will find your buffer bugs immediately.

Durability:

```bash
redis-cli set persisted yes
kill -9 <pid>            # hard kill, no cleanup
# restart
redis-cli get persisted  # must return "yes"
```

Compare behaviour against real Redis for edge cases — `GET` on a missing key, `TTL` on a key with no expiry, `LPUSH` on a string. Matching the real error strings is a good discipline.

**Fuzz the RESP parser.** It's untrusted input, and malformed length prefixes are the obvious attack.

## Where to stop

**Stop after persistence (milestone 7).** You'll have learned:

- That a famous database is a hash map, a socket, and a log
- Why single-threaded can be *faster* — no locks, no contention, no context switches
- The real difference between `write` and `fsync`, measured
- Why an append-only log plus periodic compaction is such a common design
- How copy-on-write makes fork-based snapshotting nearly free
- What a skip list is, and why it beats a balanced tree for this

**Real Redis additionally has:** Cluster with hash-slot sharding and resharding, Sentinel for failover, Lua scripting, modules, streams with consumer groups, pub/sub, transactions with `WATCH`, eight eviction policies, and a decade of memory-layout optimisation (ziplists, intsets, embedded strings) that makes small objects dramatically cheaper.

**If you want to go further:** implement **eviction** (`maxmemory` with LRU or LFU — Redis's approximate LRU sampling is another nice probabilistic algorithm), or **pub/sub**, which is small and teaches you fan-out. Replication is the natural bridge into [[architecture/04-distributed-systems/README|distributed systems]].

---

## Related
- [[build-your-own-shit/01-http-server|Build Your Own HTTP Server]] — do this first
- [[foundations/os/07-filesystems-and-storage|Filesystems and Storage]] — the `fsync` milestone
- [[foundations/os/08-io-models|I/O Models]] — the event loop
- [[architecture/02-building-blocks/02-caching|Caching]] — what you're building, conceptually
- [[build-your-own-shit/README|build-your-own-shit]]
