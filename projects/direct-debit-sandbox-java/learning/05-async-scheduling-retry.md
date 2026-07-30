# Direct Debit Sandbox — Async, Scheduling & Retry

Split out from the original single-file `learning.md`. Covers `@Async` background work, how
async callbacks work in this project, the retry state machine (FAILED → RETRYING → EXHAUSTED),
`@Scheduled`/`@EnableScheduling`, and `fixedDelay` vs `fixedRate`. See also
`06-business-domain-flow.md` for how retries fit into the subscription/mandate flow.

---

## 20. Async: doing work in the background

When a merchant subscribes, this project needs to fire a callback to the merchant's server. But the merchant should get a response immediately — they shouldn't have to wait.

The solution is `@Async`:

```java
@Async("callbackExecutor")
public void fireCallbacks(SubscriptionRecord record) {
    Thread.sleep(2000);      // wait 2 seconds (simulating processing time)
    firePreapprovalCallback(record);
    Thread.sleep(5000);      // wait 5 more seconds
    fireTransactionCallback(record);
}
```

`@Async` tells Spring: "don't run this on the HTTP request thread — put it in the background thread pool named callbackExecutor and continue immediately."

The thread pool is configured in [AsyncConfig.java](src/main/java/com/itc/direct_debit_sandbox/config/AsyncConfig.java):

```java
executor.setCorePoolSize(5);    // always keep 5 threads ready
executor.setMaxPoolSize(10);    // grow up to 10 under load
executor.setQueueCapacity(100); // queue up to 100 tasks waiting for a thread
```

Without this, every subscription would block for 7 seconds before the merchant got a response.

Note: `Thread.sleep()` pauses the current thread. It takes **milliseconds** as input. `Thread.sleep(2000)` = wait 2 seconds.

---


---

## 27. How async callbacks work in this project

The real ITC API processes debits with mobile networks asynchronously. The sandbox mimics this by using Java threads.

Key files:
- [CallbackService.java](src/main/java/com/itc/direct_debit_sandbox/callbacks/CallbackService.java) — fires the callbacks
- [AsyncConfig.java](src/main/java/com/itc/direct_debit_sandbox/config/AsyncConfig.java) — configures the thread pool
- [SandboxConfig.java](src/main/java/com/itc/direct_debit_sandbox/config/SandboxConfig.java) — holds delay values (2000ms, 5000ms)

The delays are configurable in `application.properties`:
```properties
sandbox.callback-delay-preapproval=2000
sandbox.callback-delay-transaction=5000
```

`@ConfigurationProperties` in `SandboxConfig` reads these values and makes them available as Java fields.

The thread pool prevents the sandbox from creating unlimited threads. If 100 subscriptions come in at once, 10 threads handle callbacks while the rest wait in a queue of 100 slots.

---


---

## 56. The retry state machine: FAILED → RETRYING → EXHAUSTED

When a subscription debit fails (response code ≠ `"01"`), the transaction isn't just left at `FAILED`. It enters a state machine that the `RetryScheduler` drives forward.

**States on `TransactionRecord.status`:**

| Status | Meaning |
|---|---|
| `PROCESSING` | Initial state — callback fired, result not yet known |
| `SUCCESS` | Debit succeeded |
| `FAILED` | Debit failed. If `retriesUsed < maxRetries`, the scheduler will pick it up. |
| `RETRYING` | Scheduler has picked up this record and is currently firing the next attempt. Manual trigger-debit is blocked. |
| `EXHAUSTED` | All retry attempts consumed without success. Terminal — scheduler will never touch it again. |

**Why `RETRYING` is needed:**

Without it, there is a race condition: the scheduler fires a retry and then a merchant simultaneously calls `trigger-debit`. Two callbacks fire at the same time for the same reference, producing duplicate transactions. The `RETRYING` status closes that window — `triggerDebit()` in `LifecycleService` checks for both `PROCESSING` and `RETRYING` and rejects the call.

**How `EXHAUSTED` works:**

`getAllFailedTransactions()` in the store filters by `"FAILED"` status AND `retriesUsed < maxRetries`. An `EXHAUSTED` transaction has `status = "EXHAUSTED"`, so the `"FAILED"` filter excludes it — it will never be picked up again.

If the transaction were left at `FAILED` with `retriesUsed == maxRetries`, the filter's second condition (`retriesUsed < maxRetries` = false) would also exclude it. The `EXHAUSTED` status is redundant for filtering, but it is essential for **human readability** — looking at a record and knowing it is permanently terminal is much clearer than trying to decode `retriesUsed == maxRetries`.

The fields that track this:

```java
private int retriesUsed;  // how many retries have been fired so far
private int maxRetries;   // maximum retries allowed (from configuration)
```

---

## 57. @Scheduled and @EnableScheduling — periodic background tasks

Spring has a built-in scheduler that can run a method on a fixed interval with a single annotation.

**Step 1: enable scheduling on the application class**

```java
@SpringBootApplication
@EnableScheduling          // ← this activates the scheduler
public class DirectDebitSandboxApplication { ... }
```

Without `@EnableScheduling`, any `@Scheduled` annotations in the codebase are silently ignored — the methods never run, and there is no error message.

**Step 2: annotate the method**

```java
@Scheduled(fixedDelay = 30_000)    // run 30 seconds after the previous run finishes
public void processRetries() {
    // ...
}
```

The class must be a Spring-managed component (`@Component`, `@Service`, etc.) for `@Scheduled` to work. Spring creates the object and registers the schedule at startup.

The `30_000` uses Java's numeric literal underscores — you can put `_` anywhere in a number literal to improve readability. `30_000` is the same as `30000`, just easier to read.

See [RetryScheduler.java](src/main/java/com/itc/direct_debit_sandbox/subscriptions/lifecycle/RetryScheduler.java) and [DirectDebitSandboxApplication.java](src/main/java/com/itc/direct_debit_sandbox/DirectDebitSandboxApplication.java).

---

## 58. fixedDelay vs fixedRate in scheduling

`@Scheduled` has two main timing parameters that look similar but behave very differently under load.

**`fixedDelay`** — wait N milliseconds *after* the previous execution finishes, then run again.

```
Task starts → runs for 10s → finishes → wait 30s → starts again → ...
```

If a single run takes longer than expected (e.g., the database is slow), the next run simply waits. Tasks never pile up. This is what `RetryScheduler` uses because retries must not overlap.

**`fixedRate`** — start a new execution every N milliseconds, regardless of when the previous one finished.

```
t=0s: task starts → runs for 10s
t=30s: task starts → runs for 10s
t=60s: task starts → ...
```

If a run takes longer than the interval, Spring queues the next one and it starts immediately after. This can cause a pile-up if the task is consistently slow.

**Rule of thumb:**
- Use `fixedDelay` for recurring jobs where you want a cooldown between runs (polling, retries, cleanup jobs).
- Use `fixedRate` for time-sensitive heartbeats where you care about *how often* something runs, not how long it takes.

For `RetryScheduler`, `fixedDelay` is correct: after all retries in one pass are processed, wait 30 seconds before looking for more. This prevents two retry passes from running simultaneously.

---


---

## 61. Simulating transient failures with account suffixes 002 and 003

The `ScenarioEngine` originally supported deterministic outcomes — an account always succeeded or always failed based on its suffix. But real payment systems have *transient* failures: the first attempt fails (network blip, temporary lock), and the retry succeeds.

To test retry logic, you need an account that fails a specific number of times and then succeeds. The engine adds two new suffixes:

```java
case "002" -> attemptNumber >= 1 ? "01" : "101";
// Attempt 0 (first debit): fail (101 = insufficient funds)
// Attempt 1+ (first retry): succeed (01)

case "003" -> attemptNumber >= 2 ? "01" : "101";
// Attempts 0–1: fail
// Attempt 2+ (second retry): succeed
```

`attemptNumber` is passed into `fireTransactionCallback(record, attemptNumber)` by the `RetryScheduler`. The first callback (from the initial subscription) always calls with `attemptNumber = 0`. Each retry increments the number.

**Using these in tests:**

1. Provision the merchant with `retryAttempts >= 2` (for suffix 003) and `triggerDebitStatus: true`.
2. Subscribe with an account ending `002` or `003`.
3. Watch `/debug/store` — the transaction should go `FAILED → RETRYING → SUCCESS`.
4. How long to wait: the initial callback fires ~7s after subscribe; each retry fires 30s later (one per `RetryScheduler` cycle).

---

