# Concurrency and the GIL

> **[Advanced]** · Why threads don't speed up computation, when they still help enormously, and how to choose between threading, asyncio and multiprocessing.

## The GIL

CPython has a **Global Interpreter Lock**: a single mutex that must be held to execute Python bytecode. **Only one thread runs Python code at a time, per process**, no matter how many cores you have.

**Why it exists:** CPython manages memory by reference counting, and every object's refcount changes constantly. Making each one atomic or individually locked would be slow and error-prone. One global lock made the interpreter simple, fast for single-threaded code, and C extensions easy to write safely. It was the right call in 1992 and an increasingly awkward one since.

**What it actually costs you** — and the distinction is the whole note:

- **CPU-bound work gets no speedup from threads.** Four threads doing arithmetic on four cores run at roughly one core's throughput, plus contention
- **I/O-bound work is barely affected.** **The GIL is released during I/O** — file reads, network calls, `time.sleep`. A thread waiting on a socket isn't holding it

So the shape is: threads are useless for computation and excellent for waiting.

**It's also released by well-behaved C extensions.** NumPy releases the GIL around its heavy array operations, which is why NumPy-based code *does* scale across threads. "Python can't do parallel computation" is false; "*pure* Python can't" is true.

## The three models

| | **`threading`** | **`asyncio`** | **`multiprocessing`** |
|---|---|---|---|
| Parallel Python? | **No** (GIL) | No — one thread | **Yes** — separate interpreters |
| Good for | Blocking I/O | **Many** concurrent I/O ops | CPU-bound work |
| Switching | Pre-emptive, by the OS | **Cooperative**, at `await` | OS processes |
| Cost each | ~8 MB stack | ~KB | ~10s of MB + startup |
| Practical scale | hundreds | **tens of thousands** | one per core |
| Sharing data | Shared memory + locks | Shared, single-threaded | **IPC / pickling** |
| Hard part | Race conditions | One blocking call ruins it | Serialisation cost |

### `threading`
For blocking I/O with an existing synchronous library. Simple to bolt on; you inherit every classic concurrency bug — races, deadlocks, and shared mutable state → [[foundations/os/06-concurrency-primitives|concurrency primitives]].

```python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(fetch_url, urls))
```

**Use `concurrent.futures` rather than raw threads.** The pool handles lifecycle, and exceptions surface when you read the result instead of vanishing into a dead thread.

### `asyncio`
Cooperative concurrency on one thread, via an event loop.

```python
import asyncio, httpx

async def fetch(client, url):
    r = await client.get(url)
    return r.text

async def main(urls):
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(*(fetch(client, u) for u in urls))

asyncio.run(main(urls))
```

`await` marks a point where this coroutine may suspend and the loop runs something else. Because switches happen only at `await`, **you can reason about atomicity between them** — a real simplification over threads.

**The failure mode, and it's the one that bites everyone:**

```python
async def handler():
    data = requests.get(url)        # ✗ BLOCKING — freezes the ENTIRE event loop
    time.sleep(1)                   # ✗ same
```

One synchronous call stops every other task in the process. Async is all-or-nothing per call path: you need `httpx`/`aiohttp` not `requests`, `asyncpg`/async SQLAlchemy not `psycopg2`, `asyncio.sleep` not `time.sleep`. **This "function colour" problem — async functions can only be awaited by async functions — is the genuine cost of the model.**

If you must call something blocking:

```python
await asyncio.to_thread(blocking_function, arg)      # 3.9+
```

### `multiprocessing`
Separate processes, separate interpreters, **real parallelism**.

```python
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as ex:
    results = list(ex.map(heavy_computation, chunks))
```

The costs are real: arguments and results are **pickled** across the boundary (so they must be picklable, and large data is expensive to move), startup is tens of milliseconds, and nothing is shared by default.

**The rule: the work per task must dwarf the serialisation cost.** Parallelising something cheap across processes is reliably slower than doing it in one.

## Choosing

**Is the work CPU-bound?**
→ Yes: `multiprocessing`. Or NumPy/Polars, which release the GIL. Or push the hot part into C/Rust → [[languages/06-python/14-performance-and-the-runtime|note 14]]
→ No, it's I/O:
  - **Thousands of concurrent operations** → `asyncio`
  - **A few dozen, with existing sync libraries** → `ThreadPoolExecutor`
  - **A framework already chose** → follow it. FastAPI is async, Django is (mostly) sync

**And check first that you need concurrency at all.** A great deal of "we need async" is a database query missing an index.

## The GIL is going away

**PEP 703** was accepted, and Python 3.13 ships an **experimental free-threaded build** with no GIL. Python 3.14 continues that work toward it being officially supported, with the two builds coexisting for years.

The trade is honest: removing the GIL costs single-threaded performance (finer-grained locking isn't free) and requires C extensions to be updated for thread safety. The whole ecosystem has to move.

**What it changes:** `threading` becomes genuinely parallel for CPU-bound Python, and the multiprocessing tax disappears for a large class of work. **What it doesn't:** every race condition threads have always had is still there, and now they actually happen. → [[foundations/os/06-concurrency-primitives|concurrency primitives]] and [[foundations/computer-architecture/11-multicore-and-memory-models|memory models]] stop being optional reading.

For now: assume the GIL, treat free-threading as something to track rather than deploy.

## Related
- [[foundations/os/02-processes-and-threads|processes and threads]] — what's underneath
- [[foundations/os/06-concurrency-primitives|concurrency primitives]] — locks, and why they're hard
- [[backend/01-foundations/04-runtime-and-concurrency-models|runtime and concurrency models]] — the cross-language comparison
- [[languages/02-go/06-goroutines-and-channels|goroutines]] — the model Python doesn't have

*Source: [reference] — from CPython documentation, PEP 703, and the `asyncio`/`multiprocessing` docs.*
