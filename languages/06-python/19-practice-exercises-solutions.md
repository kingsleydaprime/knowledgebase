# Practice Exercises — Solutions

> **[Beginner → Advanced]** · Worked answers to [[languages/06-python/18-practice-exercises|note 18]]. **Try each first.**

**Every number in this file was measured**, on Python 3.14, not estimated. Yours will differ in magnitude and should match in shape — and where a result depends on how you run it, that's said explicitly.

---

## Part A — The data model

### 1. Break your own environment

`activate` prepends the venv's `bin/` to `$PATH`. That's the whole mechanism:

```bash
which python          # /usr/bin/python3
source .venv/bin/activate
which python          # /path/to/.venv/bin/python
echo $PATH            # .venv/bin is now first
```

There is no magic — `python` and `pip` resolve to different executables, and each venv has its own `site-packages`. That's why two versions of `requests` coexist without knowing about each other, and why `sudo pip install` is dangerous: it writes into the interpreter your OS depends on.

### 2. Make `is` lie to you

**Three results from equivalent code:**

```python
# 1) Interactive REPL, separate lines
>>> a = 257; b = 257     (entered on separate lines)
>>> a is b
False                    # ← two distinct objects
>>> a = 256 ... a is b
True                     # ← small-int cache

# 2) The same lines in a SCRIPT
a = 257
b = 257
print(a is b)            # True  ← different answer!

# 3) Forced at runtime
print(int("257") is int("257"))   # False
print(int("256") is int("256"))   # True
```

**Two separate mechanisms, and the exercise exists to show they're different:**

**The small-integer cache.** CPython pre-allocates objects for −5 to 256. Any expression producing 256 gets the same object. That's why `int("256") is int("256")` is `True`.

**Constant folding.** In a *script*, the whole module compiles as one code object, and the compiler interns equal constants within it — so both `257` literals become one object. **In the REPL each statement compiles separately**, so no sharing. Hence the same source giving different answers depending on how it's run.

**This is the argument for the rule.** Both behaviours are unspecified implementation details that have changed across versions and differ between CPython, PyPy and others. `is` compares identity; use it for `None`, `True`, `False`, and sentinels. Nothing else → [[languages/06-python/02-the-data-model|note 02]].

### 3. Catch the mutable default

```python
def add(item, basket=[]):
    basket.append(item); return basket

add(1); add(2); add(3)          # [1] [1,2] [1,2,3]
add.__defaults__                 # ([1, 2, 3],)
```

**`__defaults__` is the proof.** The default isn't re-created per call — it's an attribute of the *function object*, evaluated once when `def` executed. Every call mutates that one list.

```python
def add(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item); return basket
```

The same trap hides in `datetime.now()` as a default (frozen at import), and in any mutable or time-dependent default.

### 4. Defeat your own copy

All three "copies" are shallow — a new outer list, **the same inner objects**:

```python
grid = [[1,2],[3,4]]
for c in (grid.copy(), list(grid), grid[:]):
    c[0].append(99)
print(grid)     # [[1, 2, 99, 99, 99], [3, 4]]
```

`copy.deepcopy` fixes it and is slow — it walks the whole object graph, tracks already-copied objects to survive cycles, and can't copy file handles, sockets or locks. **That's why it isn't the default**, and why immutability is preferred where you can get it.

### 5. Trigger `UnboundLocalError`

```python
count = 0
def bump():
    count += 1        # UnboundLocalError
```

**The error fires on the read, and that's the whole lesson.** At *compile* time Python scans the function body, sees an assignment to `count`, and marks it local **for the entire function**. So `count += 1` reads a local that has never been assigned. Nothing about the module-level `count` is consulted.

The three fixes:

```python
def bump_global():
    global count; count += 1          # works; usually the wrong design

def bump_pure(count):
    return count + 1                  # ✓ preferred — no hidden state

class Counter:
    def __init__(self): self.count = 0
    def bump(self): self.count += 1    # ✓ when the state is genuinely long-lived
```

**Reach for `global` last.** It means the function's behaviour depends on state anything can change, so when it holds the wrong value the suspect list is the whole program.

### 6. Get `[2, 2, 2]`

```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]        # [2, 2, 2]

funcs = [lambda i=i: i for i in range(3)]
[f() for f in funcs]        # [0, 1, 2]
```

**Closures capture the variable, not its value.** All three lambdas reference the same `i`; by the time any is *called*, the loop has finished and `i` is 2.

The `i=i` fix works because default arguments are evaluated **at definition time** — the same mechanism that caused exercise 3, used deliberately.

This is the bug behind every "all my buttons do the last thing" in callback-heavy code → [[languages/06-python/04-functions-and-scope|note 04]].

---

## Part B — Idioms

### 7. Break a set with a bad class

```python
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
    def __eq__(self, o): return (self.x, self.y) == (o.x, o.y)

{Point(1,2)}      # TypeError: unhashable type: 'Point'
```

**Defining `__eq__` sets `__hash__` to `None`.** Deliberate: a hash table requires that equal objects hash equally, and Python cannot infer your equality rule. Rather than let you insert objects that would go missing in their own set, it refuses.

```python
    def __hash__(self): return hash((self.x, self.y))

len({Point(1,2), Point(1,2)})     # 1 — equal objects collapse ✓
```

**The contract: equal ⟹ equal hashes.** The converse needn't hold (collisions are fine). And **hash on immutable state only** — mutating a field after insertion makes the object unfindable in its own set → [[languages/06-python/05-classes-and-the-object-model|note 05]].

`@dataclass(frozen=True)` generates both correctly and is the right default.

### 8. Get Python to protect you, once

```
ValueError: mutable default <class 'list'> for field items is not allowed:
use default_factory
```

**Verbatim, and it names the fix.** The dataclass decorator can catch this because it *inspects the class body at decoration time* and can see the default is a list. A plain `def` has no such hook — by the time the function object exists, the damage is already an attribute of it.

```python
@dataclass
class Cart:
    items: list = field(default_factory=list)     # called per instance
```

**A rare case of Python catching the mutable-default class of bug for you.** Exercise 3 is the general case, and nothing protects you there.

### 9. Measure what laziness buys

```python
import sys
sys.getsizeof([x*x for x in range(5_000_000)])    # 43,947,864 bytes
sys.getsizeof((x*x for x in range(5_000_000)))    #        208 bytes
```

**211,287×**, and both `sum()` to the same value.

The list materialises five million integer objects. The generator holds a frame and a position. `sys.getsizeof` on the list undercounts (it measures the pointer array, not the ints), so the real gap is larger still — measure process RSS for the honest figure.

**This is the difference between a script that runs and one the OOM killer terminates** → [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]].

### 10. Consume a generator twice

```python
def lines(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip()

g = lines("data.txt")
sum(1 for _ in g)      # 100
list(g)                # []   ← exhausted
```

**A generator is an iterator, and an iterator is consumed once.** The frame ran to completion; there's nothing to rewind.

Two fixes, and the choice matters:

```python
data = list(lines(path))          # materialise — fine if it fits in memory

class Lines:                       # re-iterable: a NEW generator each time
    def __init__(self, path): self.path = path
    def __iter__(self): return lines(self.path)
```

A list is iterable and gives a fresh iterator per loop; that's the distinction the protocol draws, and it's why `for` over a list twice works and over a generator twice doesn't.

### 11. Ruin a traceback

```python
def log_calls(func):
    def wrapper(*a, **kw): return func(*a, **kw)
    return wrapper
```

Without `@wraps`: `func.__name__` is `"wrapper"`, `__doc__` is `None`, `help()` shows `wrapper(*a, **kw)`, and every decorated function in the traceback is called `wrapper`.

With `@functools.wraps(func)`: name, docstring, module, annotations and `__wrapped__` are copied across.

**In a codebase with several decorated functions, the un-wrapped version makes a traceback nearly useless** — every frame has the same name. It's one line and there's no reason to skip it → [[languages/06-python/07-decorators-and-context-managers|note 07]].

### 12. A context manager that survives an exception

```python
@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")
```

Remove `try/finally` and an exception in the body propagates **through the `yield`**, so the code after it never runs and nothing prints — exactly when you most wanted the timing.

**That's the entire value of `with`:** teardown that happens on the failure path, not only the happy one. Same reason `open()` is used this way, and the same reason [[languages/05-cpp/03-classes-and-raii|RAII]] exists.

### 13. Let a type checker find a real bug

No single answer. **What to look for:** on an unannotated script, mypy in default mode is quiet — most findings appear once you add annotations, which is the incremental-adoption story working as designed.

The genuinely valuable class is `Item "None" of "X | None" has no attribute "y"` — a function that can return `None` whose caller doesn't check. **That's a real crash caught statically in a dynamic language**, and it's the single strongest argument for note 08.

If mypy found nothing, add `--strict` to one module and try again.

---

## Part C — Real Python

### 14. Lose a file to `"w"`

```python
with open("important.txt", "w") as f:      # ← truncated ALREADY
    raise RuntimeError("crash")            # original gone, nothing written
```

`open(..., "w")` truncates on *open*, before any write. The file is now zero bytes and the previous contents are unrecoverable.

The atomic version, and the ordering is load-bearing:

```python
fd, tmp = tempfile.mkstemp(dir=path.parent)   # same filesystem
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(data); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)                      # atomic
except BaseException:
    os.unlink(tmp); raise
```

**`os.replace` is atomic**, so a reader sees the old file or the new one, never a partial one. `fsync` before the rename matters: without it the rename can land while the data is still in the OS cache, and a power loss leaves an empty new file → [[databases/10-durability-and-recovery|durability]].

### 15. Circular import

```
ImportError: cannot import name 'thing_a' from partially initialized module 'a'
(most likely due to a circular import)
```

**"Partially initialised" is the mechanism.** Importing `a` starts executing it and registers it in `sys.modules` *immediately* — before it finishes. When `b` then imports `a`, it finds the half-built module, and `thing_a` isn't defined yet.

- **(a) Extract a third module** — the real fix. A cycle means the two share a concept that wants its own home
- **(b) Import inside the function** — defers to call time. Works; a pragmatic patch, not a design
- **(c) `import a` then `a.thing_a()`** — binds the module object; the attribute is looked up at call time. Works, and least invasive in existing code

**Use (a).** (b) and (c) make the symptom go away and leave the coupling → [[languages/06-python/10-modules-packages-and-imports|note 10]].

### 16. Hang your own program with a regex

Measured, `re.match(r"(a+)+$", "a"*n + "b")`:

| n | time |
|---|---|
| 15 | 0.008 s |
| 20 | 0.100 s |
| 25 | **3.04 s** |
| 28 | **23.0 s** |

**Roughly ×2 per additional character.** n=40 would take longer than a human lifetime.

`(a+)+` can split *k* a's among the groups in exponentially many ways. All match the a's; none matches the trailing `b`. So the engine tries **every partition** before concluding failure. **The near-miss is the worst case** — a string that fails fast is cheap; one that almost matches is catastrophic.

**Now assume that string came from a web form.** One request pins a CPU core for 23 seconds. That's ReDoS, and it has caused documented multi-hour outages at Cloudflare and Stack Overflow → [[languages/06-python/16-regular-expressions|note 16]].

Fixes: avoid nested quantifiers (`^a+$` here), cap input length, or use the `regex` module's timeout or Google's `re2` (linear by construction).

### 17. Prove the GIL exists

Measured, 4× a tight numeric loop, 4-core machine:

```
CPU-BOUND (4x)
  serial          2.81 s
  4 threads       5.76 s     ← SLOWER than serial
  4 processes     0.98 s     ← ~3x speedup

I/O-BOUND (4x sleep 1s)
  serial          4.00 s
  4 threads       1.00 s     ← 4x speedup
  4 processes     1.03 s
```

**Threads made CPU-bound work twice as slow as doing it serially.** Not merely "no speedup" — *worse*, because only one thread holds the GIL at a time and you've added contention and context-switching on top.

The same threads gave a clean 4× on I/O, because **the GIL is released during `sleep`, file reads and network calls.** A waiting thread isn't holding it.

**That flip is the whole rule:** threads are useless for computation and excellent for waiting. Processes get true parallelism at the cost of ~10s of ms startup and pickling every argument and result → [[languages/06-python/12-concurrency-and-the-gil|note 12]].

(On a free-threaded 3.13+/3.14 build, the threads row for CPU-bound changes. Everything else stays.)

### 18. Make async actually concurrent, then break it

Ten coroutines each awaiting 200 ms (measured):

```
sequential awaits            2.01 s   ← async syntax, synchronous behaviour
asyncio.gather               0.20 s   ← actually concurrent
gather + one time.sleep(2)   2.00 s   ← everything waits
```

**`await` means "wait here".** Ten sequential `await`s are ten round trips end to end — the code *looks* async and performs exactly like blocking code. `gather` (or a `TaskGroup`) is what puts them in flight together.

Then one `time.sleep(2)` inside a single coroutine freezes **every** task in the process. The event loop is one thread; a blocking call doesn't yield, so nothing else runs — including the nine requests that had nothing to do with it.

**That's the failure mode everyone ships**, and there's no error to tell you. Use `asyncio.sleep`, an async client, or `await asyncio.to_thread(blocking_fn)` → [[languages/06-python/17-asyncio-in-depth|note 17]].

## Related
- [[languages/06-python/18-practice-exercises|the exercises]]
- [[languages/06-python/README|the course]]

*Source: [reference] — all timings measured on Python 3.14, August 2026.*
