# Classification of Data Types

"Data type" isn't one axis — it's several independent questions being asked about a value at the same time. Two types can be different on one axis and identical on another. This note is about untangling those axes, because mixing them up is where most of the confusion ("but Python ints are objects, so how are they primitive?") comes from.

## Axis 1 — Primitive vs Composite

- **Primitive (built-in)**: the language provides it directly — int, float, bool, char. Not built out of other types.
- **Composite (compound / derived)**: built by combining primitives or other composites — arrays, structs, objects, strings (a string is really a sequence of chars), linked lists, trees.

This is the most basic split and the one people usually mean when they say "primitive types."

## Axis 2 — Value type vs Reference type

This is about what a variable actually *holds*.

- **Value type**: the variable holds the actual data. Assigning it to another variable copies the data. (`int`, `float`, `bool` in most languages.)
- **Reference type**: the variable holds a pointer/reference to where the data lives on the heap. Assigning it to another variable copies the *reference*, not the data — both variables now point at the same object.

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)  # [1, 2, 3, 4] — a and b are the same list, not two copies
```

This is the single biggest source of "why did my function change data I didn't pass by name" bugs. It has nothing to do with primitive vs composite directly — in Python, ints happen to be immutable objects (see Axis 3), which is why they don't exhibit this aliasing problem even though everything in Python is technically an object.

## Axis 3 — Mutable vs Immutable

- **Mutable**: the value can be changed in place after creation (lists, dicts, sets in Python; most objects in JS).
- **Immutable**: once created, the value cannot change — any "modification" actually creates a new value (ints, floats, strings, tuples in Python).

```python
s = "hello"
s += " world"   # this does NOT mutate the original string —
                # it creates a new string object and rebinds s to it
```

Immutability is why strings and tuples are safe to use as dict keys, and why mutable types (lists, dicts) are not — a hashable key can't change out from under the hash table (see [[03-hash-maps|hash-maps]]).

## Axis 4 — Static vs Dynamic typing

*When* is a variable's type checked/fixed?

- **Static**: at compile time. The variable itself has a declared type that can't change (`int x = 5;` in C — `x` is always an int).
- **Dynamic**: at runtime. The *value* carries its type, not the variable (`x = 5` in Python — `x` can be rebound to a string tomorrow).

## Axis 5 — Strong vs Weak typing

Independent from static/dynamic — this is about whether the language will silently coerce between types.

- **Strong**: operations between incompatible types raise an error rather than guessing (`"5" + 3` raises `TypeError` in Python).
- **Weak**: the language tries to coerce automatically (`"5" + 3` → `"53"` in JavaScript).

So a language can be dynamically *and* strongly typed (Python), or dynamically and weakly typed (JavaScript), or statically and strongly typed (Java) — the axes are independent.

## Putting it together

| Type | Primitive/Composite | Value/Reference | Mutable/Immutable |
|---|---|---|---|
| `int` (Python) | Primitive | Value-like (immutable, so aliasing is invisible) | Immutable |
| `str` (Python) | Composite (sequence of chars) | Reference, but immutable so behaves like a value | Immutable |
| `list` (Python) | Composite | Reference | Mutable |
| `dict` (Python) | Composite | Reference | Mutable |
| `struct` (C) | Composite | Value (copied on assignment unless you use a pointer) | Mutable |

## Gotchas

- **The mutable default argument trap** (Python): `def f(items=[]):` — that list is created *once*, at function definition time, and shared across every call that doesn't pass its own list. Always default to `None` and create the mutable object inside the function body.
- **"Is Python pass-by-reference or pass-by-value?"** — neither, cleanly. It's "pass by object reference": the reference itself is passed by value, so reassigning the parameter inside the function doesn't affect the caller, but mutating the object it points to does.
- Confusing immutability with "can't be reassigned" — a variable pointing to an immutable value can absolutely be rebound to a new value; what it can't do is change the value in place.

## Related
- [[02-data-types|data-types]]
- [[03-hash-maps|hash-maps]] — why keys must be hashable/immutable
