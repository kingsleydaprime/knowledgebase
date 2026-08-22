# Performance and the Runtime

> **[Advanced]** · What CPython is actually doing, why it's slow, and the ordered list of things to try — measurement first.

## What CPython does with your code

1. **Parse** source into an AST
2. **Compile** to **bytecode** — cached in `__pycache__/*.pyc`
3. **Execute** the bytecode on a stack-based virtual machine

```python
import dis
dis.dis(lambda x: x + 1)
#   LOAD_FAST    x
#   LOAD_CONST   1
#   BINARY_OP    +
#   RETURN_VALUE
```

**The `.pyc` cache saves parsing, not execution.** Python is not "compiled" in the sense C is; the bytecode is still interpreted every run.

## Why it's slow

Four costs, and they're inherent to the design rather than fixable bugs:

**Everything is a heap object.** A C `int` is 4 bytes in a register. A Python `int` is a heap-allocated object with a refcount, a type pointer and arbitrary precision — **28+ bytes**, reached through a pointer. A list of a million ints is a million objects and a million pointer dereferences, which destroys cache locality → [[foundations/computer-architecture/09-caches-in-depth|caches]].

**Dynamic dispatch on every operation.** `a + b` must check both types at runtime and find the right `__add__`. The compiler cannot specialise it, because the types could be anything.

**Attribute lookup is a dict lookup.** `obj.method()` searches the instance dict, then the class, then the MRO.

**Interpreter overhead per bytecode** — decode, dispatch, manipulate the stack.

Together: **10–100× slower than C for tight numeric loops.** For I/O-bound work, ~0×, because you're waiting on the network either way.

## Measure first

**The overwhelmingly common mistake is optimising the wrong thing.** Python's runtime characteristics are unintuitive enough that guessing is worse than useless.

```python
import time
start = time.perf_counter()          # ✓ monotonic; NOT time.time()
...
print(f"{time.perf_counter() - start:.3f}s")
```

```bash
python -m cProfile -s cumtime script.py | head -30    # where the time goes
pip install line_profiler && kernprof -l -v script.py # per-LINE, on a @profile function
pip install memray && memray run script.py            # memory
python -m timeit -s "setup" "statement"               # micro-benchmarks, done right
```

**Profile before changing anything, and measure after.** "It should be faster" is a hypothesis → [[foundations/computer-architecture/12-performance|performance method]].

## The ordered list

### 1. Fix the algorithm
An O(n²) loop is not rescued by a faster language. `x in list` inside a loop → use a `set`. Repeated `list.pop(0)` → use `deque`. **This is where the big wins are and it's language-independent** → [[foundations/dsa/README|DSA]].

### 2. Fix the I/O
Most "slow Python" in real systems is N+1 queries, an unindexed column, or serial network calls that should be concurrent → [[databases/04-b-trees-and-indexes|indexes]], [[languages/06-python/12-concurrency-and-the-gil|concurrency]]. **Check this before touching the code.**

### 3. Use the right built-ins
Built-ins run in C. The interpreter loop is the expensive part, so **the goal is fewer Python-level operations**:

```python
"".join(pieces)                       # not += in a loop (O(n²))
sum(x.price for x in items)           # C-level loop
[f(x) for x in items]                 # faster than append in a loop
local_func = self.method              # hoist lookups out of hot loops
```

### 4. Cache
```python
@functools.cache
def expensive(n): ...
```
Free, if the arguments are hashable and the input space is bounded.

### 5. Move the hot loop out of Python
This is the real answer for numeric work, and it's the ecosystem's whole strategy:

- **NumPy / Polars** — vectorise. One array operation, one C loop, no interpreter overhead per element. **Often 10–100×**, and it also releases the GIL
- **Cython** — annotate Python with C types, compile
- **PyO3 / Rust** or a C extension — write the kernel in a fast language and call it → [[languages/03-rust/README|Rust]]
- **Numba** — JIT-compile numeric functions with a decorator

**The vectorisation shift is the mental one:**

```python
result = [a[i] * b[i] for i in range(len(a))]     # 1M interpreter iterations
result = a * b                                     # NumPy: one C loop
```

### 6. Change the interpreter
**PyPy** is a JIT and often several times faster on pure-Python workloads — but C-extension compatibility is imperfect, so it rarely suits the scientific stack.

**CPython is getting faster on its own.** 3.11 was ~25% faster than 3.10 (specialising adaptive interpreter, PEP 659), 3.12 continued it, 3.13 added an experimental JIT. **Upgrading Python is the cheapest optimisation available** and people forget it exists.

## Memory

```python
import sys
sys.getsizeof([])          # 56 bytes, empty
sys.getsizeof(0)           # 28 bytes for an int
```

Practical reductions:

```python
@dataclass(slots=True)     # no per-instance __dict__: less memory, faster attributes
class Point: x: float; y: float
```

**`__slots__` is the biggest easy win** when you have many instances of a small class — it removes the per-instance dictionary, often halving memory.

Then: **generators** instead of lists for large sequences → [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]]; `array` or NumPy instead of a list of numbers; process in chunks.

**Reference cycles need the cycle collector**, which runs periodically and can cause latency spikes in large heaps. `gc.freeze()` after startup helps, and `gc.disable()` is occasionally correct in short-lived processes — but only with measurement.

## Know when not to bother

**Python's slowness is irrelevant to most programs you'll write.** A script that runs for 2 seconds instead of 0.1 is fine. An API endpoint spending 200 ms in the database and 5 ms in Python is a database problem.

**Optimise when there's a number and a target** — a p99 latency, a batch window, a cost line. Otherwise you're trading readability, which is the thing you chose Python for, against a benefit nobody asked for.

## Related
- [[languages/06-python/12-concurrency-and-the-gil|concurrency and the GIL]] — the parallelism half
- [[foundations/computer-architecture/12-performance|performance method]] — how to measure anything
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel computing]] — where the numeric work actually goes
- [[foundations/compilers/11-jit-compilation|JIT compilation]] — what PyPy and 3.13 are doing
- [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] — vectorisation, hands-on

*Source: [reference] — from CPython internals documentation, PEP 659, and the profiling tools' own docs.*
