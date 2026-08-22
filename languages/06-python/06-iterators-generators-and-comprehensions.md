# Iterators, Generators and Laziness

> **[Intermediate]** · The protocol behind every `for` loop, and how `yield` lets you process a file larger than your memory.

**Everything you can loop over implements one small protocol**, and understanding it turns a lot of Python from magic into mechanism.

## The iterator protocol

Two methods:

- **`__iter__()`** returns an *iterator* — makes something **iterable**
- **`__next__()`** returns the next item, or raises `StopIteration` — makes something an **iterator**

Every `for` loop is sugar for this:

```python
it = iter(items)              # calls items.__iter__()
while True:
    try:
        item = next(it)       # calls it.__next__()
    except StopIteration:
        break
    ...
```

**Iterables can be looped many times; iterators are consumed once.** A list is iterable and gives you a fresh iterator each time. A generator *is* an iterator — loop it twice and the second loop gets nothing:

```python
gen = (x for x in range(3))
list(gen)      # [0, 1, 2]
list(gen)      # []  ← already exhausted
```

**That is the single most common generator bug**, and it appears as an empty result far from the cause.

## Generators

A function containing `yield` returns a generator instead of running:

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1
```

Calling `countdown(3)` executes **nothing**. Each `next()` runs until the next `yield`, hands back the value, and **freezes the function's entire state** — locals, instruction pointer, everything — until asked again.

**Why this matters practically:** memory.

```python
def read_lines(path):
    with open(path) as f:
        for line in f:              # files are already lazy
            yield line.strip()

for line in read_lines("50gb.log"):  # constant memory
    process(line)
```

The list version builds all 50 GB in RAM. The generator holds one line. **This is the difference between a script that works and one that gets killed by the OOM killer**, and it's a one-word change.

`yield from` delegates to another iterable, which is how you compose them:

```python
def chain(a, b):
    yield from a
    yield from b
```

## Generator expressions

Comprehension syntax, lazy semantics:

```python
squares = [x**2 for x in range(1_000_000)]      # builds a list: ~40 MB
squares = (x**2 for x in range(1_000_000))      # generator: a few hundred bytes
```

Use them when feeding something that consumes once:

```python
total = sum(x.price for x in items)              # no parens needed as sole argument
any(u.is_admin for u in users)                   # short-circuits — stops at the first True
```

**`any` and `all` over a generator short-circuit**, so they stop reading as soon as the answer is decided. Over a list comprehension, you've already computed everything before checking.

## Pipelines

Generators compose into stages, each pulling from the last, with nothing buffered:

```python
lines    = (l.strip() for l in open("access.log"))
errors   = (l for l in lines if " 500 " in l)
parsed   = (parse(l) for l in errors)

for entry in parsed:      # nothing has been read until this line runs
    handle(entry)
```

**This is Unix pipes as a language feature**, and the same mental model applies → [[devops/01-linux/12-bash-scripting|bash scripting]].

## `itertools`

The standard library's lazy toolkit. The ones that earn their place:

```python
from itertools import chain, islice, groupby, count, cycle, tee, product, combinations

chain(a, b, c)                  # flatten iterables end to end
islice(gen, 10)                 # take the first 10 — slicing for iterators
islice(gen, 100, 110)           # skip 100, take 10
count(1)                        # infinite: 1, 2, 3, ...
cycle(["a", "b"])               # infinite repeat
product(a, b)                   # nested loops, flattened
combinations(items, 2)          # all pairs
groupby(sorted(x, key=f), key=f)  # ← MUST be sorted by the same key first
```

**`groupby` requires pre-sorted input** and will silently give wrong results otherwise — it groups *consecutive* equal keys, like Unix `uniq`. That's the documented behaviour and a reliable source of bugs.

`islice` is the answer to "how do I look at the first few items of a generator without consuming it all" — a plain `gen[:10]` doesn't work, because iterators aren't subscriptable.

## When not to be lazy

Laziness costs you things, and the trade is worth stating:

- **No `len()`**, no indexing, no slicing
- **One pass only** — need two, and you must materialise or `tee`
- **Deferred exceptions.** The error surfaces where the generator is *consumed*, not where it was defined, which makes tracebacks less obvious
- **Held resources.** A generator holding an open file keeps it open until exhausted or garbage-collected

**Materialise with `list()` when the data is small and you need it more than once.** Laziness is for large or infinite sequences, not a default virtue.

## Related
- [[languages/06-python/03-built-in-types-and-collections|built-in types]] — the eager versions
- [[languages/06-python/12-concurrency-and-the-gil|concurrency]] — `async` generators
- [[languages/06-python/07-decorators-and-context-managers|context managers]] — the `with` in `read_lines`
- [[foundations/dsa/01-iterations|iterations]] — the DSA view

*Source: [reference] — from the Python docs and `itertools`.*
