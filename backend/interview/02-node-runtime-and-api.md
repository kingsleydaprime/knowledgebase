---
id: 146f3754-fe3d-4366-8ce0-b2560a212aa5
kind: interview-bank
---

# Backend Interview Questions: Node Runtime and API

These questions check whether you know what Node is doing underneath your `await`. They're the language half of the same August 2026 interview as [[backend/interview/01-production-debugging|Production Debugging]].

## Concurrency and the event loop

### `Promise.all` over 200 requests
<!-- q: interview id="c41a7e92" level="intermediate" hot="2" pace="5" -->

Your code runs `Promise.all` over 200 outbound requests. What's wrong with that, and what would you do instead?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- It fires 200 calls at once with no limit, which uses up sockets, connections and memory, and can flatten the service you're calling. Past a point, it gets slower, not faster.
- `Promise.all` fails as soon as one promise fails, but it doesn't cancel the other 199. They keep running, and keep causing side effects, after you've already returned an error.
- You wait for the slowest of 200. If the service's p99 is 1 second, about 87% of your calls to `Promise.all` will hit at least one slow request, so your normal response time becomes their p99.
- Nothing slows you down when the downstream struggles: there's no backpressure.
- The default fix is a concurrency limit that keeps a fixed number in flight, such as `p-limit` or `p-map` with `concurrency`.
- It uses `Promise.allSettled` when partial success is fine and you need every outcome.
- It says the real fix, if one exists, is a bulk endpoint: 1 request instead of 200. Or `DataLoader` if the calls are database loads, or a job queue if it doesn't need to happen during the request.

**Follow-up:** You add a limit of 10 at a time, and one call fails. How do you stop the rest of the work?

**Detail worth adding:** Pass an `AbortController`'s signal into each call and abort it on failure or timeout, so outstanding work really stops. Also know that you may already be limited without realising: Node's HTTP agent (`maxSockets`) and `undici` cap connections per host, so 200 `fetch` calls may just queue at the agent. That wait shows up as unexplained latency, not an error.

```js
import pLimit from 'p-limit';
const limit = pLimit(10);
const results = await Promise.allSettled(
  items.map(item => limit(() => fetchOne(item)))
);
```

**Revise:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime and concurrency models]].

</details>

### Explain the event loop
<!-- q: interview id="2e8d53bf" level="intermediate" hot="2" pace="4" -->

Explain Node's event loop. Why does it matter for latency?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- The phases in order: timers (`setTimeout`, `setInterval`), pending callbacks, poll (I/O), check (`setImmediate`), close callbacks.
- Microtasks (promises, `queueMicrotask`) are drained between phases and after every callback, and `process.nextTick` runs before promises.
- Your JavaScript runs on one thread, so any synchronous work blocks every waiting request. That's Node's typical production failure: p99 spikes while p50 and CPU look fine.
- A chain of microtasks that never ends starves the loop completely, because microtasks are drained before the loop moves on. Recursive `nextTick` does the same, even harder.
- CPU-heavy work goes to `worker_threads`, to more processes (`cluster` or more containers), or out of the request into a queue.
- `worker_threads` are for CPU work, not I/O. I/O already happens off the main thread.

**Follow-up:** A service doing lots of password hashing with `pbkdf2` is slow, but its event loop looks idle. Why?

**Detail worth adding:** File system work, `dns.lookup` and some crypto (including `pbkdf2`) run on libuv's thread pool, which has only **4** threads by default (`UV_THREADPOOL_SIZE` changes it). Network I/O doesn't use that pool. So heavy hashing can queue on 4 threads while the event loop itself sits idle.

**Revise:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime and concurrency models]], [[networking/09-sockets-and-the-network-api|Sockets and the network API]].

</details>

### Why streams exist
<!-- q: interview id="a63f0d18" level="beginner" hot="0" pace="3" -->

Why do streams exist in Node, and when would you reach for one?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- Streams handle data a piece at a time, so memory stays at the size of the buffer, not the size of the data. `fs.readFile` on a 2 GB file takes 2 GB; a read stream piped to a write stream takes a few hundred KB.
- Backpressure is the point: when the destination is full, the source pauses.
- If you write your own `.on('data')` handler and ignore what `.write()` returns, you lose backpressure and memory grows without limit.
- It uses `stream.pipeline`, not `.pipe()`, because `.pipe()` doesn't pass errors on or close the other streams, so it leaks file handles when something fails.
- It names where streams show up: uploads and downloads, CSV or NDJSON processing, proxying, compression.

**Follow-up:** What goes wrong with `JSON.parse(await readFile(path))` when the file is 2 GB?

**Detail worth adding:** Two failures in one line. Memory spikes, because the whole file and then the whole parsed object sit in memory. And the event loop blocks, because `JSON.parse` is synchronous, so every other request waits until it finishes. Use a streaming parser over a read stream instead:

```js
const { pipeline } = require('node:stream/promises');
await pipeline(readable, transform, writable);
```

**Revise:** [[backend/06-cross-cutting/07-file-uploads|File uploads]].

</details>

## Memory and errors

### `new Buffer()` and its replacements
<!-- q: interview id="f915b6c2" level="intermediate" hot="1" pace="4" -->

What's the difference between `new Buffer()`, `Buffer.alloc()`, `Buffer.allocUnsafe()` and `Buffer.from()`, and why was the first one deprecated?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- `new Buffer()` is deprecated (DEP0005) and shouldn't be used.
- `new Buffer(size)` gave you uninitialised memory: whatever was there before, possibly other users' data or secrets. Send it without overwriting it fully and you've leaked it.
- It also behaved differently by the argument's type: a number allocated memory, a string copied characters. If the value came from user JSON, an attacker could send a number where you expected a string and get a block of old memory back. This caused real CVEs.
- `Buffer.alloc(size)` allocates zero-filled memory: the safe default.
- `Buffer.allocUnsafe(size)` skips the zeroing for speed, and is only for hot paths where you overwrite the whole buffer straight away.
- `Buffer.from(value)` converts data you already have: a string, an array, another buffer.
- The design lesson: the function's *name* now decides what happens, not the argument's type, the same idea as parameterised SQL queries. Make the dangerous thing impossible to do by accident.

**Follow-up:** Why is `allocUnsafe` fast, and how can it cause a memory leak?

**Detail worth adding:** Small `allocUnsafe` buffers (under half of `Buffer.poolSize`, so 4 KB by default) are cut from a shared 8 KB pool, which is why it's fast. But a small slice keeps its whole 8 KB chunk alive. Keep lots of small ones for a long time and memory grows for no obvious reason. `Buffer.allocUnsafeSlow` skips the pool for exactly that case.

**Revise:** [[cybersecurity/interview/01-appsec-crypto-and-defence|Security: the injection class]].

</details>

### Handling errors properly in Node
<!-- q: interview id="6b0e4fa7" level="intermediate" hot="0" pace="4" -->

How do you handle errors properly in a Node service?

<details><summary>Strong answer</summary>

**Strong answer covers:**

- Synchronous code: `try`/`catch`.
- Promises and `async`/`await`: `try`/`catch` around `await`, or `.catch()`. A rejected promise nobody handles crashes the process by default since Node 15.
- Callbacks: the error-first convention. A `throw` inside a callback doesn't reach the caller's `try`/`catch`.
- Event emitters, streams and sockets: an `'error'` event with no listener throws, so each one needs an error handler.
- `uncaughtException` is for logging and shutting down cleanly, not for carrying on. Log, flush, exit, and let the supervisor restart the process.
- It separates expected failures (a downstream timed out: handle it) from bugs (a `TypeError`: crash and fix it).
- It keeps the original error when wrapping one: `new AppError('…', { cause: err })`.

**Follow-up:** How do you get a request's trace ID into every log line without passing it through every function?

**Detail worth adding:** Use `AsyncLocalStorage`. Set the trace ID at the start of the request, and any code running later in that request (across every `await`) can read it, so the logger adds it to each line on its own.

**Revise:** [[backend/06-cross-cutting/03-error-handling|Error handling]], [[backend/frameworks/node/02-error-handling|Node: error handling]].

</details>

## Related

- [[backend/interview/01-production-debugging|Production debugging]]: the other half of this interview.
- [[networking/09-sockets-and-the-network-api|Sockets and the network API]]: the event loop from the operating system's side.
- [[os/interview/01-processes-memory-and-io|OS: blocking, non-blocking and async I/O]].
