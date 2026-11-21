---
id: b6f77358-cb20-4067-8424-a349c5751b1a
---

# asyncio in Depth

[[languages/06-python/12-concurrency-and-the-gil|Note 12]] covered *why* asyncio exists and when to choose it. This is how to use it without producing the three bugs everyone produces: unawaited coroutines, unbounded concurrency, and swallowed exceptions.

## Coroutines don't run until awaited
<!-- bite: 0ed88672-a087-4010-8438-aa8fad796672 -->

```python
async def fetch(url): ...

fetch(url)              # ✗ creates a coroutine object. Nothing happens.
await fetch(url)        # ✓ runs it, waits for it
```

**A bare call does nothing** and emits `RuntimeWarning: coroutine was never awaited` — which is easy to miss in a noisy log. It's the single most common asyncio mistake.

## Concurrency needs tasks
<!-- bite: f5fc15f3-10b0-4c08-b8c6-280a18269a6e -->

```python
# ✗ SEQUENTIAL — each await completes before the next starts. 3 seconds.
a = await fetch(u1)
b = await fetch(u2)
c = await fetch(u3)

# ✓ CONCURRENT — all three in flight. ~1 second.
a, b, c = await asyncio.gather(fetch(u1), fetch(u2), fetch(u3))
```

**`await` means "wait here".** Writing `await` in sequence gives you async syntax with synchronous behaviour — the code looks modern and performs identically to blocking calls. `gather` (or `create_task`) is what actually overlaps them.

```python
task = asyncio.create_task(background_work())    # starts NOW, runs concurrently
result = await do_other_things()
await task                                        # collect it later
```

**Keep a reference to every task you create.** The event loop holds only a weak reference, so a task nobody references can be garbage-collected mid-flight and vanish silently. Store them in a set, or use a TaskGroup.

## Structured concurrency — `TaskGroup`
<!-- bite: 0ec21535-14aa-4717-9aad-0ecfa2ecdb8a -->

The modern way (3.11+), and it fixes `gather`'s failure modes:

```python
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch(u1))
    t2 = tg.create_task(fetch(u2))
# on exit: all tasks are done
results = t1.result(), t2.result()
```

**If any task raises, the others are cancelled and the errors surface as an `ExceptionGroup`.** Nothing leaks, nothing is silently dropped.

Compare `gather`'s defaults:

```python
await asyncio.gather(*coros)                          # first exception propagates,
                                                      # the REST KEEP RUNNING, unawaited
await asyncio.gather(*coros, return_exceptions=True)  # exceptions returned as results —
                                                      # you MUST inspect them or they vanish
```

**`return_exceptions=True` is where errors go to die.** If you don't check each result's type, a failed call looks like a successful one returning an odd value.

**Use `TaskGroup` for new code.** It's the same idea as a `with` block for concurrency: nothing outlives the scope.

## Timeouts
<!-- bite: 915fac0a-5921-40a1-9f1d-c250bdfb75f9 -->

**Every network call needs one.** Without it, one unresponsive server holds a task forever.

```python
async with asyncio.timeout(5):        # 3.11+
    data = await fetch(url)

# older equivalent
data = await asyncio.wait_for(fetch(url), timeout=5)
```

Both raise `TimeoutError` and cancel the inner operation.

## Cancellation
<!-- bite: ed3293bd-9674-4dff-8c8a-f08ed5f742c3 -->

Cancelling injects `CancelledError` at the task's next `await`:

```python
task.cancel()
try:
    await task
except asyncio.CancelledError:
    pass
```

**`CancelledError` inherits from `BaseException`, not `Exception`** (since 3.8) — deliberately, so `except Exception:` doesn't swallow it. If you catch it to clean up, **re-raise**:

```python
try:
    await work()
except asyncio.CancelledError:
    await cleanup()
    raise                     # ← or the task refuses to die
```

Shield something that must complete:

```python
await asyncio.shield(critical_write())
```

## Bounding concurrency
<!-- bite: dde40d48-09b5-4c44-b533-027536489fcc -->

`gather` over 10,000 URLs opens 10,000 connections, exhausts file descriptors, and gets you rate-limited or blocked.

```python
sem = asyncio.Semaphore(20)

async def fetch_limited(url):
    async with sem:
        return await client.get(url)

await asyncio.gather(*(fetch_limited(u) for u in urls))
```

**A semaphore is the standard answer**, and 20–100 is a sane starting range. This is the async version of a worker pool → [[architecture/02-building-blocks/index|building blocks]].

## Mixing with blocking code
<!-- bite: b8f9fb93-330d-4cbb-bbcd-3ca429825a3c -->

```python
result = await asyncio.to_thread(blocking_call, arg)     # 3.9+
```

Runs it in a threadpool so the loop stays free. **This is the correct escape hatch** when a library has no async version → [[backend/frameworks/fastapi/01-fastapi|FastAPI]] does it automatically for `def` handlers.

Going the other way — calling async from sync — is `asyncio.run(main())`, and **only once, at the top of your program.** Calling it inside a running loop raises.

## Async iterators and context managers
<!-- bite: 473c5bd4-17d2-491f-92cd-c725921a2eb9 -->

```python
async for row in cursor:              # __aiter__ / __anext__
    ...

async with session.get(url) as resp:  # __aenter__ / __aexit__
    ...

async def stream():
    for chunk in source:
        yield chunk                   # an async generator
```

Same protocols as [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]] and [[languages/06-python/07-decorators-and-context-managers|note 07]], with `a` prefixes.

## Debugging
<!-- bite: 36f1b140-9a1e-4fdc-9f81-61b35cad4e5f -->

```python
asyncio.run(main(), debug=True)       # warns on slow callbacks and un-awaited coroutines
```

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**The symptom of a blocking call is that everything gets slow at once**, with no error. Debug mode logs any callback taking over 100 ms, which usually points straight at it.

## What has no async version
<!-- bite: b42ea3d4-a978-4133-ba1e-49d0ed09b5d7 -->

**Async file I/O barely exists.** The OS has no good non-blocking interface for regular files, so `aiofiles` uses a threadpool underneath — it isn't faster, it just stops blocking the loop. Disk I/O is usually fast enough that `to_thread` is fine → [[os/08-io-models|I/O models]].

**Async is for network I/O.** For files, for CPU work, and for anything else, it's the wrong tool.

## The rules
<!-- bite: a6414714-b3a6-4e94-ab49-cab6633bf72b -->

1. **`TaskGroup` over `gather`** for new code
2. **A timeout on every network call**
3. **A semaphore on every fan-out**
4. **Keep a reference to every task**
5. **Re-raise `CancelledError`**
6. **One blocking call ruins everything** — `to_thread` or use an async library
7. **`asyncio.run` once**, at the top

## Related
<!-- bite: 6604f6f5-a815-4297-8640-a38d38ac279e -->
- [[languages/06-python/12-concurrency-and-the-gil|concurrency and the GIL]] — the prerequisite
- [[backend/frameworks/fastapi/01-fastapi|FastAPI]] — asyncio in production
- [[os/08-io-models|I/O models]] — epoll, and what the loop sits on
- [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime models]] — the cross-language comparison

## About this lesson
<!-- bite: ba197921-8cb9-4da1-af8b-80cc05440832 -->

**Level:** Advanced. **Covers:** Tasks, gather, cancellation, timeouts and structured concurrency — the parts you need past a single `await`.

*Source: [reference] — from the asyncio documentation; roadmap.sh-cross-referenced.*
