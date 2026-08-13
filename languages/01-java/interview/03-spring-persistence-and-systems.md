# Java Interview — Spring, Persistence & Applied Systems

From [[languages/01-java/04-persistence/README|04-persistence/]], [[languages/01-java/05-web-and-api/README|05-web-and-api/]], [[languages/01-java/06-applied-systems/README|06-applied-systems/]]. The "have you shipped and operated this" round — and the one where your real projects ([[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|direct-debit-sandbox]], [[projects/record-id-generator-java/learning/01-java-fundamentals|record-id-generator]]) are your best material.

---

### Q1. [Intermediate] 🔥 What is dependency injection actually for, and why constructor injection?

**Strong answer covers:** DI inverts who constructs collaborators — the class declares what it needs, the container supplies it. The real payoff isn't decoupling as an abstract virtue: it's that **you can substitute a fake in a test without a mocking framework rewriting bytecode**, and that construction order and lifecycle are handled in one place.

**Why constructor over field injection:**
- Dependencies can be `final` → immutable, thread-safe.
- The object is **never in a partially-constructed state** — with `@Autowired` fields, it exists before its dependencies are set.
- You can instantiate it in a plain unit test with `new`, no Spring context.
- **A constructor with eight parameters is honest feedback that the class does too much.** Field injection hides that pain, which is precisely the argument against it.

---

### Q2. [Intermediate] 🔥 Explain the N+1 query problem and how you'd fix it.

**Strong answer covers:** you fetch N parents, then lazily access a collection on each, issuing one query per parent — 1 + N queries. It usually appears when the entity is serialised or iterated *outside* the transaction that loaded it.

**Fixes, in order of preference:** a `JOIN FETCH` in JPQL or an `@EntityGraph` for the specific use case; batch fetching (`@BatchSize` / `hibernate.default_batch_fetch_size`) to turn N queries into N/batch; or a **projection/DTO query** that selects exactly what you need. Blanket `FetchType.EAGER` is not a fix — it just moves the problem and drags the whole object graph into every query.

**How you'd catch it:** turn on SQL logging in tests and assert query counts (datasource-proxy / Hibernate statistics). It's invisible until production data volumes, and by then it's a Sev-2. Naming the *detection* method is what separates this answer from a textbook one.

---

### Q3. [Intermediate] Lazy vs eager loading, and what is `LazyInitializationException` really telling you?

**Strong answer covers:** lazy defers loading a relation until accessed, via a proxy. `LazyInitializationException` means you touched that proxy **after the persistence context closed** — usually in a controller or serialiser, outside the `@Transactional` boundary.

**The insight, not the workaround:** it's telling you that **your transaction boundary and your data requirements disagree**. The right fix is to decide up front what the use case needs and fetch it explicitly (entity graph or DTO projection). `OpenSessionInView` "fixes" it by keeping the session open through view rendering — which is why it's on by default in Spring Boot and why most experienced teams turn it off: it hides N+1s and holds connections for the whole request.

---

### Q4. [Intermediate] 🔥 How does `@Transactional` work, and what are the two ways it silently doesn't?

**Strong answer covers:** Spring wraps the bean in a **proxy** that begins a transaction before the method and commits/rolls back after.

**The two classic silent failures — this is the whole question:**
1. **Self-invocation.** Calling `this.otherTransactionalMethod()` bypasses the proxy entirely, so no transaction. You must go through the proxy (inject self, or refactor into another bean).
2. **Non-public methods** aren't proxied by default.

**Also worth naming:** by default it rolls back on **unchecked** exceptions only — a checked exception commits unless you set `rollbackFor`. That one has caused real financial bugs.

**Propagation:** `REQUIRED` (default, join or create), `REQUIRES_NEW` (suspend and start a new one — the way to make an audit log survive a rollback), `MANDATORY`, `NEVER`.

---

### Q5. [Intermediate→Advanced] 🔥 Two users buy the last item simultaneously. How do you prevent overselling?

**Strong answer covers the three approaches and their tradeoffs:**

1. **Optimistic locking** (`@Version`) — read, modify, and on write check the version hasn't changed; if it has, fail and retry. Best when conflicts are rare. No locks held, scales well; the caller must handle `OptimisticLockException`.
2. **Pessimistic locking** (`SELECT ... FOR UPDATE`) — take a row lock for the duration. Correct under high contention, but holds a lock across the transaction and invites deadlocks if lock ordering is inconsistent.
3. **An atomic conditional update** — `UPDATE stock SET qty = qty - 1 WHERE id = ? AND qty > 0` and check the affected-row count. Often the best answer: one statement, no read-then-write race, no lock held across a round trip.

**Detail worth adding:** state the isolation level you're assuming. Under `READ_COMMITTED` (the Postgres/Oracle default) a naive read-then-write is a lost-update race; `REPEATABLE_READ` (MySQL's default) changes the behaviour. Saying "it depends on the isolation level, and here's how" is the senior answer. → [[architecture/04-distributed-systems/10-distributed-transactions|isolation levels]]

---

### Q6. [Intermediate] 🔥 How do you make an operation idempotent, and why does it matter?

**Strong answer covers:** the client supplies a unique **idempotency key**; the server stores it with the result on first execution, and on a retry returns the stored result instead of re-executing. The key insert must be in the same transaction as the effect (or use a unique constraint) or you've just moved the race.

**Why it matters:** a network failure after the server processed the request is **indistinguishable** from one before. The client must retry; the server must make retrying safe. This is the practical form of "exactly-once delivery is impossible" — you get at-least-once delivery plus an idempotent receiver.

**You've built this** — [[projects/direct-debit-sandbox-java/learning/01-java-fundamentals|the direct-debit sandbox]] and [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|id generation & idempotency]]. Payments is exactly the domain where this is non-negotiable, so lead with the real example. → [[architecture/04-distributed-systems/10-distributed-transactions|distributed transactions]]

---

### Q7. [Intermediate] What guarantees does a message queue give you, and what does "at-least-once" force you to build?

**Strong answer covers:** most brokers (RabbitMQ, Kafka) give **at-least-once** with acknowledgements — the broker redelivers if you don't ack, so a consumer that crashes after processing but before acking sees the message twice. At-most-once loses messages. Exactly-once is only ever achieved as *effectively-once*: at-least-once delivery plus an idempotent consumer, or transactional/atomic commit within one system.

**Therefore:** **consumers must be idempotent.** Same lesson as Q6, one layer out.

**Operational details worth adding:** dead-letter queues for poison messages, prefetch/QoS to stop one consumer hoarding, and the ordering caveat — ordering only holds per queue/partition, so any parallelism gives it up. → [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|messaging with RabbitMQ]]

---

### Q8. [Intermediate] How do you generate IDs in a distributed system?

**Strong answer covers the tradeoffs:**
- **Auto-increment** — compact and ordered, but requires a single coordinator and leaks volume information.
- **UUIDv4** — no coordination, but 128 bits and **random**, which is terrible as a clustered primary key: random inserts fragment the B-tree and destroy write locality.
- **UUIDv7 / ULID / Snowflake** — time-ordered prefix plus randomness/node id. No coordination *and* good index locality. **This is usually the right answer now.**

**Detail worth adding:** Snowflake-style schemes need node-id assignment and are sensitive to clock skew (a backwards clock can produce duplicates). And "sortable by ID" is a genuinely useful property you lose with v4 — pagination and range scans get much cheaper with it. → [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|id generation]]

---

### Q9. [Intermediate] How do you keep a Java container image small and starting fast?

**Strong answer covers:** **multi-stage build** — build with the full JDK, copy only the artifact into a JRE (or `jlink`-trimmed runtime) image. Layer the image so dependencies are cached separately from application classes (Jib and Spring Boot's layered jars both do this), so a code change doesn't re-push 200 MB of dependencies.

**The container-awareness point:** modern JVMs respect cgroup limits, but **verify** — a JVM that sees the host's CPU count instead of the container's will size its GC threads and common `ForkJoinPool` wrongly. Set `-XX:MaxRAMPercentage` rather than a fixed `-Xmx` so the heap tracks the container limit.

**For startup:** CDS/AppCDS, or GraalVM native image if startup dominates (with the caveat that reflection needs configuration and peak throughput is lower). → [[languages/01-java/06-applied-systems/04-docker-for-java-apps|docker for java apps]]

---

### Q10. [Intermediate] 🔥 How would you test this properly?

**Strong answer covers the pyramid with a real opinion:** many fast unit tests with no Spring context (constructor injection makes this trivial), fewer integration tests with **Testcontainers** against a real Postgres/RabbitMQ rather than H2 — because H2 isn't the database you deploy on, and the bugs you care about are dialect-, isolation-, and constraint-specific. A thin layer of end-to-end tests.

**What to say about mocks:** mock what you don't own (external APIs), use the real thing for what you do (your database). Over-mocking produces tests that pass while the system is broken, because they assert your assumptions rather than reality.

**Be honest if it applies:** "my Java projects shipped without tests and adding a Testcontainers suite is on my list" is a *stronger* answer than pretending otherwise — it's in [[project-ideas|project-ideas]] as a 🟢 for exactly this reason. Interviewers trust calibrated self-assessment far more than polish.
