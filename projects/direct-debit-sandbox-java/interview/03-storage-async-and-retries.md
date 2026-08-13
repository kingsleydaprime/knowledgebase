# direct-debit-sandbox-java — Storage, Async & Retries

From [`../learning/04-data-storage-patterns.md`](../learning/04-data-storage-patterns.md) and
[`05-async-scheduling-retry.md`](../learning/05-async-scheduling-retry.md).

---

### Q1. [Beginner] 🔥 Why `ConcurrentHashMap` rather than `HashMap` for the store?

**Strong answer covers:** a web application is multi-threaded by definition — the servlet container
handles requests concurrently, plus a scheduler thread — so the store is genuinely shared mutable
state. A `HashMap` under concurrent mutation can corrupt its internal structure (historically an
infinite loop during resize), not merely lose an update. `ConcurrentHashMap` gives thread-safe reads
and writes with per-bin locking, so it doesn't serialise the whole map the way
`Collections.synchronizedMap` does.

**The limit to name:** it makes individual operations atomic, not sequences of them.
`get` then `put` is still a race; that's what `computeIfAbsent`, `putIfAbsent` and `compute` are
for.

---

### Q2. [Intermediate] 🔥 Explain secondary indexes here. Why not just stream and filter?

**Strong answer covers:** the primary map is `subscriptionId → SubscriptionRecord`, so lookup by ID
is O(1). Lookup by `referenceNo` via
`subscriptions.values().stream().filter(...).findFirst()` is **O(n)** — fine at 10 records, one
million reads per lookup at a million records. A secondary index is a second map
`referenceNo → subscriptionId`, making the lookup a **two-hop O(1)**.

**The cost, which you must state:** the index is now a second thing to keep in sync. Every create,
update and delete has to maintain it, and a missed update produces a dangling index entry pointing at
a record that no longer matches — a bug that's invisible until someone looks up by the indexed field.
That's exactly the trade a database makes for you, and doing it by hand is the argument for using a
database.

---

### Q3. [Intermediate] What's a composite map key and how did you build one?

**Strong answer covers:** the provision is keyed by `merchantId + productId` together, because
neither alone identifies it. Options: a delimited string (`merchantId + ":" + productId`), a record
with generated `equals`/`hashCode`, or a nested map. A **record** is the safest — a delimited string
breaks if either component can contain the delimiter, which is a silently-wrong collision rather
than an error.

---

### Q4. [Intermediate] 🔥 Explain `computeIfAbsent` for a one-to-many index.

**Strong answer covers:** for "all subscriptions belonging to a merchant" the index value is a
*list*, so every insert must either create the list or append to an existing one.
`map.computeIfAbsent(key, k -> new ArrayList<>()).add(value)` does the check-and-create **atomically**,
where `if (map.get(k) == null) map.put(k, new ArrayList<>())` is a check-then-act race in which two
threads can both create a list and one silently loses its entry.

**The remaining gotcha:** the *list itself* isn't thread-safe. Concurrent `add` calls on the same
key need a `CopyOnWriteArrayList` or synchronisation — `computeIfAbsent` protects the map, not the
value.

---

### Q5. [Intermediate] What does "data normalization — keeping your data lean" mean in an in-memory store?

**Strong answer covers:** store a fact once and reference it, rather than copying it into every
record that needs it. Copying the merchant's callback URL onto every subscription means a thousand
copies to update when it changes, and a guaranteed period where some are stale. The provision holds
it once; records reference `merchantId + productId` and resolve at callback time. Same reasoning as
normalising a relational schema — the difference between a map and a table doesn't change the
argument.

---

### Q6. [Intermediate] Why separate create from update in the store rather than one `save` method?

**Strong answer covers:** they have different preconditions and different failure modes. `create`
must fail if the ID already exists (otherwise a retry silently overwrites a live record); `update`
must fail if it doesn't (otherwise a typo'd ID silently creates a ghost record). A single `save`
that upserts cannot express either, so both bugs become impossible to detect at the store layer.

---

### Q7. [Intermediate] Explain fallback resolution — trying one source then another.

**Strong answer covers:** the callback URL resolves from the provision for `merchantId + productId`,
falling back to another source (a request-supplied value or a system default) when absent. The
discipline: a fallback chain must be **one function** with an explicit order, not null checks
scattered across call sites, or different code paths will disagree about precedence — and that
disagreement is invisible until one path takes a fallback the other wouldn't have.

---

### Q8. [Beginner] Why `UUID` for IDs, and what's the alternative?

**Strong answer covers:** `UUID.randomUUID()` needs no coordination — no counter, no database
round-trip, no collision risk in practice — so any node can mint an ID immediately. The costs: 36
characters, not human-quotable, and random values are poor clustered-index keys in a real database
(the exact problem the sibling `record-id-generator-java` project fixed with a `BIGINT
AUTO_INCREMENT` PK). For an in-memory sandbox those costs are irrelevant, which is why it's right
*here* and would need revisiting on a real datastore.

**Related detail:** `UUID.fromString()` doubles as validation — it throws on a malformed ID, so
you can reject a bad path parameter without writing a regex.

---

### Q9. [Advanced] Deterministic fake data from a hash — what problem does that solve?

**Strong answer covers:** a sandbox needs plausible customer data (names, phone numbers, bank
details) that is **stable across calls** — the same account must return the same fake customer every
time, or an integrator's tests fail randomly. Hashing the input (account number, reference) and
deriving the fake values from the hash gives determinism with zero storage: the same input always
maps to the same output, different inputs to different ones, and nothing has to be persisted.

**Same idea, different project:** Arete's FNV-1a deterministic daily missions. Recognising it as one
pattern — *derive, don't store* — is the transferable insight.

---

### Q10. [Intermediate] 🔥 How does the async callback actually work, and why must it be async?

**Strong answer covers:** the caller gets a synchronous acknowledgement with a reference; the outcome
arrives later as a callback POST to the provisioned URL, dispatched off the request thread (`@Async`,
backed by a thread pool). It must be async because the caller shouldn't hold a connection while the
system talks to a third party — and because the outcome genuinely isn't known synchronously in a real
payments flow.

**Follow-ups worth pre-empting:** `@Async` requires `@EnableAsync` and only works through a Spring
proxy, so **calling an `@Async` method from within the same class does nothing** — the call bypasses
the proxy and runs synchronously, silently. That's the classic Spring async bug. Also: exceptions in
a `void` `@Async` method vanish unless an `AsyncUncaughtExceptionHandler` is configured.

---

### Q11. [Intermediate] 🔥 `fixedDelay` vs `fixedRate` on `@Scheduled` — which did you use and why does it matter?

**Strong answer covers:** `fixedRate` starts a run every N ms *regardless* of how long the previous
run took; `fixedDelay` waits N ms **after the previous run finishes**. If a run can exceed the
interval, `fixedRate` queues up overlapping executions and a slow run cascades into a pile-up.
`fixedDelay` is the safe default for a retry scheduler, where the work is variable and depends on
external HTTP calls. (Note that with the default single-threaded scheduler, `fixedRate` runs don't
literally overlap — they queue — which is arguably worse, because the backlog is invisible.)

---

### Q12. [Advanced] 🔥🔥 Walk me through the retry state machine: FAILED → RETRYING → EXHAUSTED.

**Strong answer covers the states first:**

| Status | Meaning |
|---|---|
| `PROCESSING` | Callback fired, result not yet known |
| `SUCCESS` | Debit succeeded |
| `FAILED` | Failed; eligible for retry while `retriesUsed < maxRetries` |
| `RETRYING` | The scheduler has picked it up and is firing an attempt now |
| `EXHAUSTED` | All attempts consumed. Terminal — the scheduler never touches it again |

**Then the two design points that make this a great answer:**

1. **Why `RETRYING` exists — it closes a race.** Without it, the scheduler can fire a retry at the
   same moment a merchant calls `trigger-debit` manually, producing two concurrent callbacks for one
   reference and duplicate transactions. `triggerDebit()` rejects the call when the status is
   `PROCESSING` **or** `RETRYING`, so the in-flight window is no longer open. That's an
   application-level lock expressed as a state, and naming it as such is the strong version.

2. **Why `EXHAUSTED` is "redundant but essential".** The scheduler's query already filters
   `status == FAILED AND retriesUsed < maxRetries`, so a fully-retried record would be excluded
   anyway. `EXHAUSTED` adds nothing to the filter — it exists for **human readability**: an operator
   looking at a record sees a terminal state directly instead of having to decode
   `retriesUsed == maxRetries`. Being able to say "this field is redundant for the machine and
   necessary for the human, and I added it deliberately" is a genuinely senior thing to articulate.

---

### Q13. [Advanced] How do you simulate a transient failure — one that fails then succeeds?

**Strong answer covers:** account suffixes `002` and `003` produce failures that *later* succeed, so
the retry path is actually exercised end to end. Without them, every simulated failure is permanent
and the retry machinery only ever demonstrates exhaustion — you'd never observe a successful retry,
which is the case integrators most need to see working. The general lesson: a fault-injection
mechanism needs to cover *recovery*, not just failure, or the recovery code is never tested.

---

### Q14. [Advanced] What are the limits of the in-memory store, and what changes with a real database?

**Strong answer covers:** everything is lost on restart, nothing scales beyond one instance (two
replicas have two divergent stores, and the retry scheduler would run twice), and there are no
transactions — a create plus two index updates can partially apply if something throws in between.

Moving to a database changes the design in specific ways worth naming: secondary indexes become real
indexes maintained by the engine rather than by hand (Q2's sync bug disappears); the multi-step
writes become one transaction; and the scheduler needs leader election or a row-level claim
(`UPDATE ... SET status='RETRYING' WHERE status='FAILED' AND ...`) so multiple instances don't
process the same record — which is the database version of exactly what the `RETRYING` state is
doing in memory today.
