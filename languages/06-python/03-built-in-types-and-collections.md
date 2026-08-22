# Built-in Types and Collections

> **[Beginner]** · `str`, `list`, `dict`, `set`, `tuple` — their costs, their idioms, and the `collections` types that are usually the better answer.

Python's built-in collections are unusually good, which is why idiomatic Python reaches for a plain `dict` where other languages would define a class. Knowing their costs is most of writing fast Python.

## Strings

Immutable sequences of Unicode code points. Every operation returns a new string.

```python
name = "Kingsley"
name.upper()          # returns a NEW string; name is unchanged
name[0]               # 'K'
name[-1]              # 'y'  — negative indexes count from the end
name[0:4]             # 'King'  — slice: start inclusive, stop exclusive
```

**f-strings are the only formatting you need** (3.6+):

```python
f"{name} has {len(name)} letters"
f"{value:.2f}"          # 2 decimal places
f"{value:,}"            # thousands separators
f"{name=}"              # 'name=Kingsley' — debugging shorthand (3.8+)
```

**The performance trap:** building a string by repeated `+=` in a loop is O(n²), because each step copies everything so far. Use `join`:

```python
"".join(pieces)         # ✓ one allocation
```

**`str` vs `bytes` is a real distinction, not a legacy wart.** `str` is text; `bytes` is binary. Files, sockets and hashes give you `bytes`, and you `.decode()` to get text or `.encode()` to go back. Python 3 refuses to guess, which is why porting Python 2 code hurts and why your code that works locally doesn't break on a server with a different locale.

## Lists

Dynamic arrays. Ordered, mutable, heterogeneous (though mixed types usually signal a design problem).

| Operation | Cost |
|---|---|
| `lst[i]`, `len(lst)` | **O(1)** |
| `append`, `pop()` from the end | **O(1)** amortised |
| `insert(0, x)`, `pop(0)` | **O(n)** — everything shifts |
| `x in lst` | **O(n)** — a full scan |
| `sort()` | O(n log n) — Timsort, and very fast on partly-sorted data |

**Two of those rows are where slow Python comes from.** `insert(0, x)` in a loop is quadratic — use `collections.deque`. And `x in lst` inside a loop over another list is O(n×m) — use a `set` → [[foundations/programming-fundamentals/07-collections|collections]].

**Slicing** works on any sequence and always produces a copy:

```python
lst[2:5]      # elements 2,3,4
lst[::2]      # every second element
lst[::-1]     # reversed (a copy)
lst[:]        # a shallow copy of the whole thing
```

## Tuples

Immutable sequences. Two genuinely different uses:

**A fixed record**, where position has meaning — `(x, y)`, `(name, age)`. This is the real use, and `NamedTuple` or a dataclass is usually clearer → [[languages/06-python/05-classes-and-the-object-model|note 05]].

**A hashable sequence**, so it can be a `dict` key or in a `set` — which lists cannot.

**Unpacking** is everywhere in idiomatic Python:

```python
x, y = point
first, *rest = items          # rest is a list
a, b = b, a                   # swap, no temp variable
for i, item in enumerate(items): ...
for k, v in mapping.items(): ...
```

## Dictionaries

Hash maps, and the single most important type in Python — objects, modules, classes and keyword arguments are all backed by them.

```python
prices = {"apple": 1.20, "bread": 2.50}
prices["apple"]                 # 1.20 — KeyError if missing
prices.get("milk")              # None if missing
prices.get("milk", 0)           # a default
prices.setdefault("milk", 0)    # get, inserting the default if absent
```

Insertion order is preserved (guaranteed since 3.7). Keys must be **hashable** — immutable, in practice.

**The idioms worth internalising:**

```python
{k: v for k, v in pairs if v > 0}                 # comprehension
merged = {**defaults, **overrides}                 # merge (or | in 3.9+)
for key, value in d.items(): ...                   # NOT for key in d: d[key]
```

## Sets

Unordered collections of unique hashable items. **O(1) membership**, and that's the reason to use them.

```python
seen = set()
if item not in seen:            # O(1) — vs O(n) for a list
    seen.add(item)

set(a) & set(b)                 # intersection
set(a) | set(b)                 # union
set(a) - set(b)                 # difference
list(dict.fromkeys(items))      # dedupe, PRESERVING order (set() does not)
```

That last line matters: `set()` deduplicates but discards order. `dict.fromkeys` keeps it, because dicts are ordered.

## Comprehensions

The most recognisable Python idiom, and it isn't only brevity — it's usually faster than the equivalent loop, because the append happens in C rather than through an attribute lookup per iteration.

```python
squares  = [x**2 for x in numbers]
evens    = [x for x in numbers if x % 2 == 0]
lookup   = {u.id: u for u in users}
unique   = {u.country for u in users}
lazy     = (x**2 for x in numbers)      # generator — computes on demand
```

**Where they stop being a good idea:** more than one `for` plus a condition, or a body that no longer fits on a line. A comprehension you have to decode is worse than the loop it replaced.

```python
# ✗ write the loop instead
[transform(y) for x in matrix for y in x if check(y) and other(y)]
```

## The `collections` module — usually the better answer

```python
from collections import Counter, defaultdict, deque, namedtuple

Counter(words).most_common(3)     # frequency counting, done
                                  # replaces the get(k,0)+1 pattern entirely

d = defaultdict(list)             # missing keys auto-create
d["group"].append(item)           # no setdefault, no KeyError

q = deque()                       # O(1) at BOTH ends
q.appendleft(x); q.popleft()      # this is your queue and your sliding window
deque(maxlen=100)                 # a bounded ring buffer, free
```

**`Counter` and `defaultdict` between them remove most of the fiddly dictionary code people write by hand**, and `deque` is the fix for every O(n) `list.pop(0)`.

Also worth knowing: `heapq` (priority queue on a plain list), `bisect` (binary search into a sorted list), `itertools` → [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]].

## Related
- [[languages/06-python/06-iterators-generators-and-comprehensions|iterators and generators]] — lazy versions of all of this
- [[languages/06-python/05-classes-and-the-object-model|classes]] — when a dict should have been a type
- [[foundations/dsa/README|DSA]] — why these costs are what they are
- [[foundations/programming-fundamentals/07-collections|collections]] — the language-agnostic version

*Source: [reference] — from the Python standard library documentation.*
