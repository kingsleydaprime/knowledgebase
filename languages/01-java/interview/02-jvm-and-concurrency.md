# Java Interview — JVM & Concurrency

From [[languages/01-java/02-jvm-and-concurrency/README|02-jvm-and-concurrency/]]. **This is the round that matters most for a low-latency or systems role** — the questions where they find out whether you've operated a JVM or only written Java on one.

🔥 marks questions that come up constantly.

---

### Q1. [Intermediate] 🔥 Walk me through what happens to memory when I call `new`.

**Strong answer covers:** the object is allocated on the **heap**, almost always in the **TLAB** (Thread-Local Allocation Buffer) — a per-thread slice of Eden, so allocation is just a **pointer bump**, no locking. That's why allocation in Java is genuinely cheap; the cost is *reclamation*, not creation.

The reference lives on the thread's **stack** (or in a register). The object header carries mark word + class pointer (~12–16 bytes, so tiny objects have significant overhead).

**Detail worth adding:** the JIT may **scalar-replace** the object entirely if escape analysis proves it never leaves the method — the allocation disappears. That's why microbenchmarking allocation naively gives absurd results, and why you need JMH with blackholes.

---

### Q2. [Intermediate] 🔥 Explain generational GC and why it works.

**Strong answer covers:** the **weak generational hypothesis** — most objects die young. So split the heap: new objects go in **Eden**; a minor GC copies the few survivors to a **survivor space**, and after enough survivals they're **promoted** to the old generation. Minor GCs are frequent and cheap because they only touch the young generation, and their cost is proportional to *surviving* objects, not dead ones. Dead objects cost literally nothing to collect — you just don't copy them.

**The consequence that matters:** **allocation rate drives GC frequency; live-set size drives GC pause length.** Those are two different dials, and knowing which one your problem is on determines the fix.

**Detail worth adding:** the **card table** / remembered set tracks old→young references so a minor GC doesn't have to scan the whole old generation. That's why write barriers exist and why they cost you a little on every reference store.

---

### Q3. [Advanced] 🔥 Compare the collectors. Which would you pick for a low-latency service?

**Strong answer covers:**

| Collector | Optimises for | Pause behaviour |
|---|---|---|
| **Parallel** | throughput | long stop-the-world, scales with heap |
| **G1** | balanced, predictable-ish | region-based, pause *target* (not guarantee); default since 9 |
| **ZGC** | latency | **sub-millisecond**, concurrent, largely heap-size-independent |
| **Shenandoah** | latency | similar goals, concurrent evacuation |
| **Epsilon** | nothing (no-op) | for benchmarking/short-lived jobs — proves allocation behaviour |

**For low latency: ZGC**, and be ready to say why — it does marking and relocation concurrently using **coloured pointers and load barriers**, so pause times don't grow with heap size. The trade is throughput (barriers cost on every reference load) and higher memory use.

**The answer that scores highest:** *"the best GC tuning is allocating less."* No collector beats not creating the garbage. On a hot path that means object pooling or reuse, primitive arrays over boxed collections, and avoiding streams/lambdas that allocate per element. Then measure with **JFR**, not intuition. → [[project-ideas|the JMH + GC tuning study project]]

---

### Q4. [Intermediate] 🔥 What does `volatile` actually guarantee — and what doesn't it?

**Strong answer covers:** two things — **visibility** (a write is visible to other threads' subsequent reads; no caching in a register) and **ordering** (it's a memory barrier; reads/writes aren't reordered across it, establishing happens-before).

**What it does not give you: atomicity of compound operations.** `volatile int i; i++` is still a race, because `++` is read-modify-write — three operations, and another thread can interleave. Use `AtomicInteger` or a lock.

**The canonical use:** a `volatile boolean running` flag for stopping a thread. Without `volatile`, the JIT may hoist the read out of the loop and the thread never stops — a genuinely famous bug that only appears under optimisation, i.e. in production.

---

### Q5. [Advanced] 🔥 What is the Java Memory Model, and why does it exist?

**Strong answer covers:** the JMM defines when a write by one thread is guaranteed visible to another. It exists because **the compiler, JIT, and CPU all reorder operations** for performance, and without a specification you couldn't write correct concurrent code on any of them.

The core relation is **happens-before**. It's established by: program order within a thread; unlocking a monitor before locking it; a `volatile` write before a subsequent read of it; `Thread.start()` before the thread's code; the thread's code before `join()` returns; and final-field freeze at the end of a constructor.

**The key reframing:** without a happens-before edge, one thread's writes **may never become visible** to another — this isn't about timing or luck, it's that the JIT is *permitted* to keep the value in a register indefinitely. That's why "it works on my machine" concurrency bugs surface on different hardware, under load, or after the JIT warms up.

**Double-checked locking** is the classic story: it was broken without `volatile` because the reference could be published before the constructor's writes were visible, so another thread could see a non-null but partially-constructed object. Fixed in Java 5's revised JMM, but only with `volatile` on the field.

---

### Q6. [Intermediate] `synchronized` vs `ReentrantLock` — when do you need the lock?

**Strong answer covers:** `synchronized` is simpler and impossible to leak (the JVM releases on exit, including on exception). It's also had heavy JVM optimisation — biased locking (removed in 15+), lock elision, adaptive spinning.

**`ReentrantLock` when you need what `synchronized` can't do:** `tryLock()` (with timeout — the standard deadlock-avoidance move), interruptible acquisition, fairness policy, multiple `Condition` objects on one lock, or lock/unlock in different scopes. `ReadWriteLock`/`StampedLock` for read-heavy workloads.

**Rule to state:** default to `synchronized`; reach for `ReentrantLock` when you have a specific need — and always `unlock()` in a `finally`.

---

### Q7. [Advanced] What is false sharing and how do you fix it?

**Strong answer covers:** cache coherence works at **cache-line granularity** (64 bytes), not per-variable. Two threads writing *different* variables that happen to sit on the same cache line will invalidate each other's line constantly — the ping-pong destroys performance even though there's no logical contention at all.

**The fix:** pad so the hot variables land on separate lines. `@Contended` (with `-XX:-RestrictContended`) does it declaratively; historically people padded with dummy `long` fields.

**Why this question is asked:** it's a pure mechanical-sympathy probe. Knowing it signals you think about the memory hierarchy, which is the entire job in low-latency work. It's also exactly why the LMAX Disruptor pads its cursors.

---

### Q8. [Intermediate] 🔥 Explain the thread pool parameters. What happens when the queue fills?

**Strong answer covers:** `corePoolSize` (kept alive), `maximumPoolSize`, `keepAliveTime`, the `workQueue`, and the `RejectedExecutionHandler`.

**The behaviour people get wrong — say this explicitly:** new threads beyond core are created **only when the queue is full**, not when all core threads are busy. So with an **unbounded** queue (`LinkedBlockingQueue` with no capacity — what `Executors.newFixedThreadPool` gives you) the pool **never exceeds core size**, and instead the queue grows until you OOM. That's why `Executors` factory methods are discouraged and you construct `ThreadPoolExecutor` directly with a bounded queue.

**Rejection policies:** `AbortPolicy` (throws, the default), `CallerRunsPolicy` (runs on the submitting thread — a crude but effective **backpressure** mechanism, since the producer is now busy and can't submit more), `DiscardPolicy`, `DiscardOldestPolicy`.

**Sizing:** CPU-bound ≈ core count; I/O-bound higher, per Little's law — but with virtual threads, the whole "size a pool for I/O" problem mostly evaporates.

---

### Q9. [Intermediate→Advanced] 🔥 What are virtual threads and what problem do they solve?

**Strong answer covers:** lightweight threads scheduled by the JVM onto a small pool of carrier (platform) threads. When a virtual thread blocks on I/O, the JVM **unmounts** it from its carrier and runs something else — so blocking a virtual thread costs almost nothing.

**The problem solved:** you no longer choose between *readable* (blocking, sequential, debuggable, stack traces that make sense) and *scalable* (async/reactive, callback or `CompletableFuture` soup). Thread-per-request comes back, at a million threads. → [[foundations/networking/09-sockets-and-the-network-api|the same event-loop tradeoff, from the sockets side]]

**The caveats that show you've actually used them:**
- **`synchronized` used to pin** the virtual thread to its carrier (fixed in JDK 24; before that, use `ReentrantLock` in library code).
- Native calls also pin.
- **Pooling virtual threads is pointless** — create one per task; they're the cheap thing.
- **They don't help CPU-bound work.** They fix *blocking*, not compute.
- Thread-locals become expensive at a million threads → scoped values.

---

### Q10. [Advanced] How would you build a lock-free bounded queue, and why bother?

**Strong answer covers:** a ring buffer with `AtomicLong` producer/consumer cursors and CAS to claim a slot; capacity a power of two so the index is a mask rather than a modulo; pad the cursors to avoid **false sharing**; and busy-spin (or park) rather than block, so there's no context switch.

**Why bother:** locks mean context switches, and a context switch is microseconds — an eternity when your latency budget is sub-microsecond. Lock-free means a slow thread can't block others (though CAS retries under contention aren't free either — lock-free is not automatically faster, only *non-blocking*).

**Name the reference:** this is the LMAX **Disruptor**'s core, and it's a 🟡 project in [[project-ideas|project-ideas]]. Having built one is the single most credible thing you can say in this round.

---

### Q11. [Intermediate] 🔥 A service has good average latency but a terrible p99. Walk me through diagnosis.

**Strong answer covers a systematic list, not a guess:**
1. **GC pauses** — check GC logs / JFR. Is p99 ≈ a pause duration? Then it's allocation rate or live-set size.
2. **Lock contention** — JFR or async-profiler in lock mode; a hot `synchronized` block serialises everything.
3. **The network/transport layer** — [[foundations/networking/15-network-performance|RTO after tail loss, incast, bufferbloat]]. This one gets missed constantly because it's invisible to application profiling.
4. **Fan-out amplification** — if one request makes 100 downstream calls, you wait for the slowest; a 1% tail becomes a 63% chance of being hit.
5. **JIT deoptimisation / warmup**, cold caches, connection-pool exhaustion, a noisy neighbour.

**The framing that scores:** name your instrument for each hypothesis (JFR, async-profiler, `ss -tin`, distributed tracing) rather than listing causes. The interviewer is grading method, not recall.
