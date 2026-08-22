# The Data Model

> **[Beginner → Intermediate]** · Names, objects and references — the model that explains mutable defaults, surprise aliasing, and why `is` is not `==`.

Almost every Python surprise traces back to one sentence: **everything is an object, and a variable is a name bound to one.**

Not a box holding a value — a **label attached to an object that lives somewhere else.**

```python
a = [1, 2, 3]
b = a              # a second label on the SAME list
b.append(4)
print(a)           # [1, 2, 3, 4]
```

If you carry the box metaphor from [[foundations/programming-fundamentals/05-variables-and-types|programming fundamentals]], this is inexplicable. With labels it's obvious: there is one list and two names for it.

## Mutable and immutable

Every object is one or the other, and this single property determines the behaviour above.

| Immutable | Mutable |
|---|---|
| `int`, `float`, `bool`, `str`, `bytes` | `list`, `dict`, `set` |
| `tuple`, `frozenset` | `bytearray`, most of your own classes |
| `None` | |

**Immutable doesn't mean the name can't be rebound** — it means the *object* can't be changed:

```python
s = "hello"
s += " world"       # does NOT modify the string; creates a new one and rebinds s
```

So immutable types appear to behave like values, and mutable ones expose the sharing:

```python
x = 5
y = x
y += 1              # rebinds y to a NEW int; x is untouched
```

**One rule covers both cases:** assignment never copies. It binds a name. Whether you notice depends entirely on whether the object can be mutated in place.

## `is` versus `==`

- **`==`** asks *are these equal?* (calls `__eq__`)
- **`is`** asks *are these the same object?* (compares identity — effectively the memory address)

```python
a = [1, 2]
b = [1, 2]
a == b       # True  — equal contents
a is b       # False — two distinct lists
```

**Use `is` for exactly three things:** `None`, `True`, `False`. Everywhere else, use `==`.

```python
if value is None:      # ✓ correct and idiomatic
if value == None:      # ✗ works, but wrong — and breaks on classes with custom __eq__
```

**The trap that teaches this badly:** CPython caches small integers (−5 to 256) and interns some strings, so `a is b` is `True` for `a = 100; b = 100` and `False` for `a = 1000; b = 1000`. That's an implementation detail of one interpreter, not a language rule. Never write code that depends on it.

## The mutable default argument

**The single most famous Python gotcha**, and it follows directly from the model.

```python
def add_item(item, basket=[]):        # ✗ BROKEN
    basket.append(item)
    return basket

add_item("apple")     # ['apple']
add_item("bread")     # ['apple', 'bread']   ← the same list, again
```

**Default values are evaluated once, when the function is defined** — not on each call. So that one list is created at definition time and reused forever, accumulating across calls. It's a property of the function object itself, visible in `add_item.__defaults__`.

The fix, and it is the only correct one:

```python
def add_item(item, basket=None):      # ✓
    if basket is None:
        basket = []
    basket.append(item)
    return basket
```

**Never use a mutable object as a default argument.** Linters flag it; it is worth knowing *why* rather than just obeying.

## Copying

Since assignment shares, copying must be explicit — and there are two depths:

```python
import copy

shallow = original.copy()          # or list(original), original[:], {**d}
deep    = copy.deepcopy(original)
```

**Shallow copies one level.** A new outer list, containing *the same inner objects*:

```python
grid = [[1, 2], [3, 4]]
copy_ = grid.copy()
copy_[0].append(99)
print(grid)              # [[1, 2, 99], [3, 4]]  ← the inner list is shared
```

**Deep copy recurses** and gives a fully independent structure. It's slower and can't handle everything (open files, sockets), so reach for it deliberately rather than by default.

## Truthiness

Any object can be used in a boolean context. The falsy ones are:

`False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `()`, and any object whose `__bool__` returns `False` or whose `__len__` returns `0`.

```python
if items:              # ✓ Pythonic — "if there are any items"
if len(items) > 0:     # correct but noisy
```

**The trap:** `if items:` and `if items is not None:` differ exactly when `items` is an empty list. If "empty" and "absent" mean different things in your code — and they usually do — you must say which you mean:

```python
if items is not None:      # I care whether it exists
if items:                  # I care whether it has content
```

## `None`

Python's null. A singleton — there is exactly one `None` object, which is why `is None` is the correct test.

It carries the same ambiguity every null does: *not set*, *not found*, *not applicable* are three different things wearing one face. When it matters, prefer a sentinel or an explicit type:

```python
MISSING = object()                              # a unique sentinel
def get(key, default=MISSING): ...
```

→ [[languages/06-python/08-typing-and-type-hints|typing]] for `Optional[T]` and how a type checker turns "might be `None`" into an error you see before running.

## Everything really is an object

Functions, classes, modules and types are all objects with attributes, assignable to names and passable as arguments:

```python
def greet(): print("hi")

f = greet          # no parentheses — the function object itself
f()                # call it
greet.author = "K" # functions take attributes, because they're objects
```

**This uniformity is what makes decorators, first-class functions and most of Python's metaprogramming possible** — they're not special features, just consequences of the model. → [[languages/06-python/07-decorators-and-context-managers|note 07]].

## Related
- [[languages/06-python/03-built-in-types-and-collections|built-in types]] — the objects you'll use most
- [[languages/06-python/05-classes-and-the-object-model|classes]] — dunder methods and the protocols
- [[languages/06-python/08-typing-and-type-hints|typing]] — catching what dynamism lets through
- [[foundations/programming-fundamentals/05-variables-and-types|variables and types]] — the language-agnostic version
- [[foundations/os/05-memory-allocation|memory allocation]] — what "somewhere else" actually means

*Source: [reference] — from the Python language reference and the community's accumulated list of ways to be surprised.*
