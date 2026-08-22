# Decorators and Context Managers

> **[Intermediate]** · The two idioms that appear in every real Python codebase, and both are simpler than their reputation.

## Decorators

A decorator is **a function that takes a function and returns a replacement.** That's all. The `@` syntax is sugar:

```python
@log_calls
def process(x): ...

# is exactly
def process(x): ...
process = log_calls(process)
```

Writing one:

```python
import functools

def log_calls(func):
    @functools.wraps(func)                      # ← don't skip this
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper
```

Three details that make it correct rather than nearly correct:

- **`*args, **kwargs`** so it wraps any signature
- **`return result`** — forgetting this makes every decorated function return `None`, and it's a maddening bug because the function itself is fine
- **`@functools.wraps(func)`** copies `__name__`, `__doc__` and `__wrapped__` onto the wrapper. Without it, every decorated function is named `wrapper` in tracebacks, docs and debuggers

**A decorator with arguments needs one more layer**, because `@retry(times=3)` is called *first*, and its return value is the decorator:

```python
def retry(times=3):
    def decorator(func):
        @functools.wraps(func)
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

**Decorators run at import time**, not call time. `@app.route("/users")` registers the route when the module is imported — which is why import order matters in web frameworks and why a route in a module nobody imports simply doesn't exist.

### The ones you'll meet

```python
@property @staticmethod @classmethod          # built-in, → note 05
@functools.cache                              # memoise (3.9+); lru_cache before that
@functools.singledispatch                     # dispatch on argument type
@dataclass                                    # → note 05
@pytest.fixture  @pytest.mark.parametrize     # → note 13
@app.get("/users")                            # FastAPI/Flask routing
```

**`@functools.cache` is the highest-value one-liner in the standard library.** It turns exponential recursion linear:

```python
@functools.cache
def fib(n):
    return n if n <= 1 else fib(n-1) + fib(n-2)
```

That's memoisation → [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|recursion]]. Two cautions: arguments must be hashable, and an unbounded cache on a long-running process is a memory leak — use `@lru_cache(maxsize=1000)` when the input space is large.

## Context managers

`with` guarantees that setup and teardown both happen, **even if the body raises**:

```python
with open("data.txt") as f:
    process(f)
# f is closed here — exception or not
```

Without it you need `try/finally` every time, and one forgotten `finally` leaks a file handle, a lock, or a database connection.

**Why "the file gets closed anyway" is not good enough:** CPython closes it when the last reference goes away, which usually happens promptly — but that's refcounting, an implementation detail. On PyPy it happens whenever the GC runs, which might be much later. Code that relies on it works locally and leaks in production.

### Writing one

The easy way:

```python
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield                                  # the with-body runs here
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")
```

**Everything before `yield` is setup; everything after is teardown.** The `try/finally` is what makes it exception-safe — without it, an exception in the body skips your cleanup entirely.

The class form, when you need state or to suppress exceptions:

```python
class Transaction:
    def __enter__(self):
        self.conn.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        return False        # False = re-raise; True = SUPPRESS the exception
```

**Returning `True` from `__exit__` swallows the exception.** Almost always wrong, and the mechanism behind `contextlib.suppress`.

### The useful ones

```python
from contextlib import suppress, nullcontext, ExitStack

with suppress(FileNotFoundError):
    os.remove(path)                    # try/except/pass, honestly

with open("a") as a, open("b") as b:   # several at once
    ...

with ExitStack() as stack:             # a variable number, not known upfront
    files = [stack.enter_context(open(p)) for p in paths]
```

Beyond files: `threading.Lock`, database transactions and sessions, `tempfile.TemporaryDirectory`, `unittest.mock.patch`, `torch.no_grad()`, changing directory, and any "set something, guarantee it's put back" pattern.

**The rule of thumb: if a resource must be released, or a global must be restored, it wants a context manager.** It's the Python answer to what [[languages/05-cpp/03-classes-and-raii|C++ calls RAII]] — with the scope stated explicitly rather than tied to an object's lifetime.

## Related
- [[languages/06-python/04-functions-and-scope|functions and scope]] — the closures decorators are built from
- [[languages/06-python/09-errors-and-exceptions|errors and exceptions]] — what `__exit__` receives
- [[languages/06-python/05-classes-and-the-object-model|classes]] — `@property` and the dunder protocols
- [[languages/05-cpp/03-classes-and-raii|RAII in C++]] — the same problem, solved by scope

*Source: [reference] — from `functools`, `contextlib` and the language reference.*
