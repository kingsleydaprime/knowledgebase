# Node Interview — Runtime & API

The language half of the same August 2026 interview. Where [[backend/interview/01-production-debugging|file 01]] tests diagnosis, this tests whether you understand what the runtime is doing underneath your `await`.

---

### Q1. 🔥 You `Promise.all` over 200 requests. What's wrong with that, and what are the alternatives?

**Four separate problems. Naming more than one is what scores.**

**1. Unbounded concurrency.** You've just fired 200 simultaneous outbound calls. That exhausts sockets, database connections, and file descriptors; it can overwhelm the downstream service (you *are* the thundering herd now); and it holds 200 in-flight responses in memory at once. The irony: you did this to be fast, and past a certain concurrency you get *slower* because of queueing on both sides.

**2. `Promise.all` is fail-fast, but it does not cancel.** It rejects as soon as *one* promise rejects — while the other 199 **keep running**. So you've returned an error to your caller while the work continues in the background, burning resources, still performing side effects, and potentially producing unhandled rejections. This is the subtlety they're testing.

**3. Tail latency.** You wait for the slowest of 200. If the downstream p99 is 1s, the chance that at least one of 200 calls hits it is ~87%. **Your typical response time becomes your dependency's p99.**

**4. No backpressure.** Nothing slows you down if the downstream is struggling.

**The alternatives, and when each is right:**

| Approach | Use when |
|---|---|
| **Bounded concurrency** (`p-limit`, `p-map` with `concurrency`) | **the default answer** — a sliding window keeps N in flight |
| **`Promise.allSettled`** | partial success is acceptable and you need every outcome |
| **Chunking** (batches of 10) | simplest, but has a barrier per batch — you wait for the slowest in each chunk, so a sliding window beats it |
| **A bulk/batch endpoint** | **the real fix if it exists** — 1 request instead of 200 |
| **`DataLoader`** | when the 200 calls are database loads → this is the [[backend/interview/01-production-debugging\|N+1]] fix |
| **A job queue** | when it doesn't have to be synchronous at all |
| **`Promise.any`** | you want the first success (hedged requests) |
| **Async iterators / streams** | very large sets — gives you real backpressure |

```js
import pLimit from 'p-limit';
const limit = pLimit(10);
const results = await Promise.allSettled(
  items.map(item => limit(() => fetchOne(item)))
);
// allSettled + a concurrency cap: bounded load, no fail-fast, every outcome visible
```

**Two details that lift this answer:**
- **Add an `AbortController`** so a failure or a timeout actually cancels the outstanding work rather than leaving it running.
- **You may already be bounded and not know it.** Node's HTTP agent has a `maxSockets` limit (`undici` has connection limits too), so 200 concurrent `fetch` calls to one host may just *queue at the agent*. Concurrency is capped, but the wait becomes invisible latency rather than an obvious error — which is exactly the "connection pool queueing" item from [[backend/interview/01-production-debugging|Q1 of file 01]].

---

### Q2. 🔥 `new Buffer()` vs `Buffer.alloc()` vs `Buffer.allocUnsafe()` vs `Buffer.from()`

**`new Buffer()` is deprecated (DEP0005) and must not be used.** Two genuinely serious reasons, and the second is the interesting one:

**1. `new Buffer(size)` returned uninitialised memory.** It handed you whatever was previously on the heap — potentially other requests' data, secrets, decrypted content. If you allocated a buffer and sent it without fully overwriting it, you leaked memory contents to a user. That's a real information-disclosure vulnerability class, not a theoretical one.

**2. Type-dependent behaviour — the API was a type-confusion trap.** `new Buffer(x)` did something completely different depending on `x`'s runtime type:
- `new Buffer(10)` → a 10-byte **uninitialised** buffer
- `new Buffer("10")` → a buffer containing the *characters* `"10"`
- `new Buffer([1,2,3])` → a buffer of those bytes

Now imagine `x` comes from `JSON.parse(userInput)`. An attacker sends `{"data": 5000}` where you expected a string, and your code allocates 5KB of uninitialised heap and returns it. **This caused real CVEs in widely-used packages.**

**The replacements, and why the split exists:**

| Function | Behaviour | Use when |
|---|---|---|
| **`Buffer.alloc(size[, fill])`** | allocates, **zero-filled** | default — safe, slightly slower |
| **`Buffer.allocUnsafe(size)`** | allocates, **uninitialised**, taken from an internal pool | hot path, and **you will fully overwrite it immediately** |
| **`Buffer.allocUnsafeSlow(size)`** | uninitialised, **not pooled** | you'll retain a small buffer long-term |
| **`Buffer.from(value)`** | from a string / array / ArrayBuffer / Buffer | converting existing data |

**The design lesson, which is the actual answer:** the API was split so that **the function name determines the behaviour, not the argument's type.** You can no longer accidentally allocate when you meant to convert. That's the same move as parameterised queries in SQL — *make the dangerous thing unrepresentable rather than trying to validate your way out of it.* → [[cybersecurity/interview/01-appsec-crypto-and-defence|the injection class]]

**The pooling detail, if they push:** `allocUnsafe` serves allocations smaller than `Buffer.poolSize >>> 1` (4KB by default) from a pre-allocated 8KB pool — that's why it's fast. The catch: a small buffer sliced from the pool **keeps the whole 8KB chunk alive**. Retain many small `allocUnsafe` buffers long-term and you have a memory leak that looks inexplicable. That's what `allocUnsafeSlow` is for.

---

### Q3. 🔥 Explain the event loop. Why does it matter for latency?

**Strong answer covers the phases** — timers (`setTimeout`/`setInterval`) → pending callbacks → poll (I/O) → check (`setImmediate`) → close callbacks — with **microtasks (promises, `queueMicrotask`) drained between every phase and after every callback**, and `process.nextTick` draining *before* promises.

**The consequence that matters:** JavaScript runs on **one** thread. Any synchronous work blocks the entire loop, so *every* pending request waits. This is why Node's characteristic production failure is a **p99 spike with a healthy-looking p50 and low CPU** — a burst of requests all queued behind one blocking operation.

**The trap worth naming:** an infinite microtask chain **starves the loop entirely** — microtasks are drained to exhaustion before the loop advances, so a promise that recursively resolves will hang your server with no I/O ever progressing. `process.nextTick` recursion does the same thing, harder.

**What to do about CPU-bound work:** `worker_threads` for computation (real threads, message passing), `cluster` or multiple containers for scaling across cores, or move it out of the request path entirely into a queue. Note the distinction — **`worker_threads` is for CPU work, not for I/O**; I/O is already off-thread via libuv's thread pool.

**The libuv detail:** file system operations, DNS lookups (`dns.lookup`), and some crypto run on libuv's thread pool, default size **4**, tunable with `UV_THREADPOOL_SIZE`. Network I/O does *not* — that's epoll/kqueue. So a service doing heavy `fs` or `pbkdf2` work can be bottlenecked on 4 threads while the event loop looks idle. Genuinely obscure, genuinely useful.

---

### Q4. Why do streams exist, and when would you reach for one?

**Strong answer covers:** streams process data **incrementally with backpressure**, so memory use is bounded by the buffer rather than by the data size. `fs.readFile` on a 2GB file allocates 2GB; a read stream piped to a write stream uses a few hundred KB.

**Backpressure is the point.** `.pipe()` (or better, `stream.pipeline`) wires the consumer's readiness back to the producer — when the destination's buffer fills, the source pauses. Write a manual `.on('data')` handler that never checks `.write()`'s return value and you've thrown that away; memory grows without limit.

**Use `pipeline`, not `pipe`:**
```js
const { pipeline } = require('node:stream/promises');
await pipeline(readable, transform, writable);
// pipe() does NOT forward errors or destroy the remaining streams —
// it leaks file descriptors on failure. pipeline() cleans up properly.
```

**Where it shows up:** file upload/download, CSV/NDJSON processing, proxying responses, compression. If you ever wrote `JSON.parse(await readFile(...))` on a large file, that's both a memory spike **and** an event-loop block — the two failure modes from Q3 in one line.

---

### Q5. How do you handle errors properly in Node?

**Strong answer covers the four channels, because they behave differently:**
- **Synchronous** — `try/catch`.
- **Promises / async-await** — `try/catch` around `await`, or `.catch()`. **An async function that throws returns a rejected promise; if nothing awaits it, that's an unhandled rejection — which terminates the process by default since Node 15.**
- **Callbacks** — error-first convention. A `throw` inside a callback does *not* propagate to the caller's `try/catch`; the stack is gone.
- **EventEmitters** — an `'error'` event with **no listener throws**. Every stream and socket needs an error handler.

**The policy points:**
- **`uncaughtException` is for logging and a graceful shutdown, not for recovery.** After it fires the process is in an undefined state — log, flush, exit, let the supervisor restart you. "Catch it and keep going" is how you get corrupted state.
- **Distinguish operational errors** (a downstream timed out — expected, handle it) **from programmer errors** (a `TypeError` — a bug; crash and fix it). Trying to recover from bugs hides them.
- **Preserve the cause** when wrapping: `new AppError('...', { cause: err })`. Losing the original stack makes the incident unreadable at 3am.
- **`Error.captureStackTrace`** and `AsyncLocalStorage` for request-scoped context (correlation IDs across async boundaries) — the latter is how you get a trace ID into every log line without threading it through every function.

→ [[backend/01-nodejs/02-nodejs-errorhandler|the error handler note]]

## Related
- [[backend/interview/01-production-debugging|Production Debugging]] — the other half of this interview
- [[foundations/networking/09-sockets-and-the-network-api|Sockets & the Network API]] — the event loop from the OS side: `epoll`, C10K, why blocking costs what it costs
- [[foundations/os/interview/01-processes-memory-and-io|OS: blocking vs non-blocking vs async I/O]]
