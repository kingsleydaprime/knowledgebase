# Python Interview — The Language Round

**Python interviews test the data model and the gotchas**, not syntax. If you can explain *why* the mutable default bug happens, you've demonstrated the model that every other answer depends on.

From [[languages/06-python/README|the Python course]] — each question maps to a note.

---

### Q1. [Beginner→Intermediate] 🔥 What's wrong with `def f(x, items=[])`?

**Strong answer covers:** the default is evaluated **once, when `def` executes** — not per call. So one list is created at definition time and shared by every call, accumulating across them.

```python
def add(x, items=[]):
    items.append(x); return items
add(1)   # [1]
add(2)   # [1, 2]   ← the same list
add.__defaults__     # ([1, 2],) — it's an attribute of the function object
```

**Fix:** `items=None`, then `if items is None: items = []`.

**Details that matter:**
- The same trap catches `datetime.now()` as a default — frozen at import time
- `@dataclass` **rejects** a mutable default outright (`use default_factory`) — a rare case of Python protecting you → [[languages/06-python/05-classes-and-the-object-model|note 05]]

**The senior point:** this isn't a wart, it's a consequence of `def` being an executable statement that builds a function *object*. **Everything in Python is an object**, and defaults are just attributes → [[languages/06-python/02-the-data-model|note 02]].

---

### Q2. [Beginner→Intermediate] 🔥 `is` vs `==`.

**Strong answer covers:** `==` calls `__eq__` (equality); `is` compares identity. **Use `is` for `None`, `True`, `False` and sentinels — nothing else.**

**The demonstration that shows you understand it:**
```python
a = int("257"); b = int("257"); a is b     # False
a = int("256"); b = int("256"); a is b     # True  ← small-int cache (-5..256)
```
And in a *script* (but not the REPL), `a = 257; b = 257; a is b` is **True** — because the compiler folds equal constants within one code object.

**The senior point:** both behaviours are **unspecified implementation details** that differ between CPython versions and other interpreters. Code depending on them is broken by definition. Being able to name *both* mechanisms — the cache and constant folding — is what separates this from trivia → [[languages/06-python/19-practice-exercises-solutions|exercise 2]].

---

### Q3. [Intermediate] 🔥 Explain the GIL. Does it make threads useless?

**Strong answer covers:** one lock must be held to execute Python bytecode, so **only one thread runs Python at a time per process.** It exists because CPython uses reference counting, and making every refcount update atomic would be slow and error-prone.

**The crucial qualifier: the GIL is released during I/O.** So:

| Workload | Threads | Processes |
|---|---|---|
| **CPU-bound** | **No speedup — often slower** | True parallelism |
| **I/O-bound** | **Near-linear speedup** | Also works, more overhead |

**Measured, 4× a tight numeric loop on a 4-core machine:** serial 2.81 s, 4 threads **5.76 s**, 4 processes 0.98 s. Threads made it **twice as slow as serial** — contention on top of no parallelism.

**Details that matter:**
- NumPy, and well-behaved C extensions, **release the GIL** around heavy work — so "Python can't do parallel computation" is false; *pure* Python can't
- **PEP 703** — free-threaded builds (experimental in 3.13) remove it, at some single-threaded cost, and every race threads always had becomes real
- `asyncio` is a third option: one thread, cooperative, best for **many** concurrent I/O operations

**The senior point:** the right question is never "threads or processes" but **"what is this bound by?"** → [[languages/06-python/12-concurrency-and-the-gil|note 12]].

---

### Q4. [Intermediate] 🔥 Generators — what and why?

**Strong answer covers:** a function with `yield` returns an iterator. Calling it executes nothing; each `next()` runs to the next `yield` and **freezes the entire frame** — locals and instruction pointer — until asked again.

**Why it matters — memory:**
```python
sys.getsizeof([x*x for x in range(5_000_000)])   # 43,947,864 bytes
sys.getsizeof((x*x for x in range(5_000_000)))   #        208 bytes
```
**211,287×.** That's the difference between a script that runs and one the OOM killer terminates.

**The bug to raise unprompted:** a generator is consumed **once**. Iterating twice silently gives nothing the second time — and it shows up as an empty result far from the cause.

**The senior point:** generators compose into pipelines with nothing buffered between stages — Unix pipes as a language feature. The costs: no `len()`, no indexing, one pass, and exceptions surface where it's *consumed* rather than defined → [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]].

---

### Q5. [Intermediate] Decorators — write one.

**Strong answer covers:** a function that takes a function and returns a replacement. `@d` is sugar for `f = d(f)`.

```python
import functools

def retry(times=3):
    def decorator(func):
        @functools.wraps(func)          # ← don't skip
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorator
```

**Three details that make it correct rather than nearly correct:** `*args/**kwargs` so it wraps any signature; **`return`** the result (forgetting it makes every decorated function return `None`); and **`@functools.wraps`**, without which every frame in your tracebacks is called `wrapper`.

**The senior point:** **decorators run at import time**, not call time — which is why `@app.route` registers a route when the module is imported, and why import order matters in web frameworks → [[languages/06-python/07-decorators-and-context-managers|note 07]].

---

### Q6. [Intermediate] EAFP vs LBYL — which and why?

**Strong answer covers:** *Easier to Ask Forgiveness than Permission* is the Pythonic default, and the reason is **correctness, not style**:

```python
if os.path.exists(path):        # ✗ TOCTOU — the file can vanish between these lines
    open(path)
```

The check-then-act version has a **race condition**. `try/except FileNotFoundError` has none, and it's faster on the success path. In a security context, time-of-check-to-time-of-use is an exploitable bug class → [[cybersecurity/06-attacks-and-threats/README|attacks]].

**The follow-up worth pre-empting — what's wrong with `except: pass`:** it catches `KeyboardInterrupt` and `SystemExit` (which sit outside `Exception` deliberately), swallows your own typos, and discards the evidence. If you must continue, `except Exception:` with `log.exception(...)` — which records the full traceback → [[languages/06-python/09-errors-and-exceptions|note 09]].

---

### Q7. [Intermediate] What do type hints actually do?

**Strong answer covers:** **nothing at runtime.** They're erased as far as execution is concerned — `calculate(  "100" )` on an `int` parameter runs happily. They exist for **static checkers, editors and readers**.

**The consequence:** data crossing a boundary — an API response, a form, a file — is unchecked whatever you annotated. **Validate at the boundary** with Pydantic, then the type is earned → [[backend/frameworks/python/01-fastapi/README|FastAPI]].

**Details that matter:** modern spellings (`list[str]`, `X | None`) over `List`/`Optional`; `Protocol` for structural typing, which fits duck-typed code far better than an ABC; `Any` disables checking and spreads — prefer `object` and narrow.

**The senior point, and the practical one:** adopt incrementally. **Turning on `--strict` across a large untyped codebase produces thousands of errors, nobody triages them, and the tool gets removed** — the same alert-fatigue failure as everywhere else → [[languages/06-python/08-typing-and-type-hints|note 08]].

---

### Q8. [Advanced] Why is Python slow, and what do you do about it?

**Strong answer covers** the four structural costs: every value is a **heap object** (a Python `int` is 28+ bytes behind a pointer, destroying cache locality), **dynamic dispatch** on every operation, **attribute lookup is a dict lookup**, and per-bytecode interpreter overhead. **10–100× slower than C on tight numeric loops** — and ~0× on I/O-bound work.

**The ordered response, which is the actual answer:**
1. **Fix the algorithm.** An O(n²) loop isn't rescued by a faster language
2. **Fix the I/O** — most "slow Python" in production is an N+1 query or serial network calls
3. **Use the built-ins** — they run in C; the interpreter loop is the cost
4. **Cache** — `@functools.cache`
5. **Move the hot loop out of Python** — NumPy/Polars vectorisation is the ecosystem's whole strategy, and it releases the GIL
6. **Change interpreter** — PyPy; and **upgrading CPython is the cheapest optimisation available** (3.11 was ~25% faster than 3.10)

**The senior point:** *"measure first"* — and naming the tool (`cProfile`, then `line_profiler` on the hot function) is what makes that more than a slogan → [[languages/06-python/14-performance-and-the-runtime|note 14]].

---

## Related
- [[languages/06-python/README|the Python course]]
- [[languages/06-python/18-practice-exercises|practice exercises]] — reproduce every gotcha above
- [[backend/frameworks/python/README|Python backends]] — the framework round
- [[languages/01-java/interview/README|Java interview prep]] — the contrast

*Source: [reference] — assembled Aug 2026; measurements from the course's own exercises.*
