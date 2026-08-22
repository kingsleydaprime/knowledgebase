# Functions and Scope

> **[Beginner → Intermediate]** · Argument passing, `*args`/`**kwargs`, closures, and the LEGB rule that explains every `UnboundLocalError` you'll meet.

Functions in Python are objects → [[languages/06-python/02-the-data-model|note 02]]. Everything below follows from that.

## Arguments

Python has unusually rich argument handling, and it's worth knowing all of it because library APIs use all of it.

```python
def create(name, email, age=None, *tags, admin=False, **extra):
    ...
```

- `name`, `email` — **positional-or-keyword**
- `age=None` — **default**; makes the parameter optional
- `*tags` — collects extra positionals into a **tuple**
- `admin=False` — **keyword-only** (it follows `*args`), so it must be named at the call site
- `**extra` — collects extra keywords into a **dict**

At the call site, `*` and `**` unpack rather than collect:

```python
args = ["Ada", "ada@example.com"]
opts = {"age": 36, "admin": True}
create(*args, **opts)
```

**Two markers worth recognising in signatures you read:**

```python
def f(a, b, /, c, d, *, e, f):
```
Everything before `/` is **positional-only** (3.8+); everything after `*` is **keyword-only**. Positional-only lets a library rename parameters without breaking callers; keyword-only forces clarity at the call site — which is why `sorted(items, key=..., reverse=...)` won't accept bare positionals.

**Use keyword-only for boolean flags.** `place_order(items, True, False)` is unreadable at the call site; `place_order(items, express=True, gift=False)` is not.

## Passing semantics

The perennial "is Python pass-by-value or pass-by-reference?" question has an answer that's neither: **pass-by-assignment.** The parameter name is bound to the same object the caller passed.

```python
def modify(lst, num):
    lst.append(4)      # mutates the caller's list — same object
    num += 1           # rebinds the LOCAL name; caller's int untouched
```

Same rule as everywhere else in the language: **you can mutate what you're given; you cannot rebind the caller's name.**

**Which is why mutating an argument is a design decision, not an accident.** A function that quietly modifies what it was handed is a function whose call sites all need reading. Prefer returning a new value → [[foundations/programming-fundamentals/08-functions|functions]].

## Scope, and the LEGB rule

Python resolves a name by searching four scopes in order:

**L**ocal → **E**nclosing (containing functions) → **G**lobal (module) → **B**uilt-in

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        print(x)        # finds "enclosing" — E before G
    inner()
```

**The rule that causes the confusion: assigning to a name anywhere in a function makes it local for the whole function.**

```python
count = 0
def increment():
    count += 1          # UnboundLocalError
```

`count += 1` is an assignment, so `count` is local throughout `increment` — including on the right-hand side, where it hasn't been assigned yet. The error is thrown before anything runs.

The explicit fixes:

```python
def increment():
    global count        # rebind the module-level name
    count += 1

def make_counter():
    count = 0
    def inc():
        nonlocal count  # rebind the ENCLOSING function's name
        count += 1
    return inc
```

**Reaching for `global` is nearly always the wrong fix.** It says a function's behaviour depends on state anything can change. Pass it in and return it out, or use a class.

Note that **`if`, `for` and `while` do not create scope** — only functions, classes, modules and comprehensions do. A name bound inside a loop outlives it, which surprises people coming from C-family languages.

## Closures

A function that captures names from its enclosing scope, and keeps them alive after that scope has returned:

```python
def multiplier(n):
    def multiply(x):
        return x * n        # n is captured
    return multiply

double = multiplier(2)
double(5)                   # 10 — n is still 2, long after multiplier returned
```

This is what makes decorators work → [[languages/06-python/07-decorators-and-context-managers|note 07]].

**The late-binding trap**, which will catch you at least once:

```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]        # [2, 2, 2] — NOT [0, 1, 2]
```

Closures capture the **variable**, not its value at creation. By the time any lambda runs, `i` is 2. The fix binds the value at definition time via a default argument:

```python
funcs = [lambda i=i: i for i in range(3)]     # [0, 1, 2]
```

## Lambdas

Anonymous single-expression functions.

```python
sorted(users, key=lambda u: u.age)
```

**That's the legitimate use** — a throwaway passed to something else. Assigning a lambda to a name (`f = lambda x: x * 2`) is worse than `def` in every way: no name in tracebacks, no docstring, no annotations, and linters flag it.

## Docstrings and annotations

```python
def calculate_tax(amount: float, rate: float = 0.2) -> float:
    """Return the tax due on `amount` at `rate`.

    Raises:
        ValueError: if amount is negative.
    """
```

Annotations are **not enforced at runtime** — Python ignores them. They exist for readers, editors and type checkers → [[languages/06-python/08-typing-and-type-hints|note 08]]. Passing a string to `amount` above will happily run until something fails downstream.

## Related
- [[languages/06-python/07-decorators-and-context-managers|decorators]] — closures, applied
- [[languages/06-python/08-typing-and-type-hints|typing]] — making the annotations mean something
- [[languages/06-python/02-the-data-model|the data model]] — why passing behaves as it does
- [[foundations/programming-fundamentals/08-functions|functions]] — the language-agnostic version

*Source: [reference] — from the Python language reference.*
