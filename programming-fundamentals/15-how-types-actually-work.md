# How Types Actually Work

> **[Beginner → Intermediate]** · What a type *is* underneath the bits, and the five independent questions hiding inside the phrase "data type". The note that explains **why** the rules in [[foundations/programming-fundamentals/05-variables-and-types|note 05]] are the way they are.

[[foundations/programming-fundamentals/05-variables-and-types|Note 05]] gave you the working knowledge: here are the types, here's the reference-vs-value trap, convert at the boundary. That's enough to write correct code, and if you're mid-course you can keep going.

This note is the layer under it, and it's here at the end deliberately — it makes far more sense once you've met [[foundations/programming-fundamentals/07-collections|collections]], [[foundations/programming-fundamentals/13-objects-and-classes|objects]] and [[foundations/programming-fundamentals/14-programming-paradigms|paradigms]], because the distinctions below are exactly what separate those ideas.

## The same bits mean different things

Memory holds no types. It holds bytes, and a byte is eight bits with no opinion about what it represents. **A type is the instruction for how to read them.**

Take these 32 bits:

```
01000001 01000001 01000001 01000001
```

- Read as a **32-bit signed integer**: `1094795585`
- Read as an **IEEE-754 float**: `12.078431`
- Read as **four ASCII characters**: `"AAAA"`
- Read as **four booleans**, or a colour, or a tiny bitmap: also all valid

**Nothing in the bits chooses between these.** The type does, and it's the only thing that does. That's the whole idea, and it's why "a type tells the machine how many bits to set aside and what they mean" is a complete definition rather than a slogan.

This has a consequence you can feel. In C you can force the machine to reinterpret bits as the wrong type — **type punning** — and get a number that computes fine and means nothing. No crash, no error, just silent nonsense. The type system exists to make that require deliberate effort.

### Why fixed sizes matter

Because an `int32` is *always* 4 bytes, a hundred of them in a row occupy a predictable 400 bytes, and the address of element `i` is `base + i * 4`. One multiply, one add, no searching.

**That is the entire reason array indexing is instant**, and it only works because the type pins down the size in advance. Variable-sized elements would mean walking from the start to find anything. This is where this course hands off to [[foundations/dsa/04-data-structures/01-arrays|arrays]] in DSA — the performance story there is built directly on the fact established here.

### What the type system buys

1. **Allocation** — the compiler knows how much memory to reserve, and where each field of a struct begins.
2. **Legality** — it knows which operations make sense. Multiplying two numbers is meaningful; multiplying two booleans isn't.
3. **Early mistakes** — adding a string to a number gets caught before it ships, in languages that check.

## "Data type" is five questions, not one

Here's the thing that clears up most confusion: **"data type" isn't one axis.** It's five independent questions asked about a value at once, and two types can differ on one while being identical on another.

Mixing them up is the source of nearly every muddle in this area — "but Python ints are objects, so how can they be primitive?" is two different axes being collided.

### Axis 1 — Primitive vs composite

- **Primitive** — provided directly by the language, not built from other types: `int`, `float`, `bool`, `char`.
- **Composite** — built by combining others: arrays, structs, objects, and strings (a string is a sequence of characters).

The most basic split, and what people usually mean by "primitive types".

### Axis 2 — Value vs reference

About what the variable actually *holds*. This is the axis behind the box metaphor breaking in note 05:

- **Value type** — the variable holds the data itself. Assignment copies the data.
- **Reference type** — the variable holds a *pointer* to where the data lives. Assignment copies the pointer, so both names now refer to one object.

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)        # [1, 2, 3, 4] — one list, two names
```

Note 05 called this the root of "why did that change?" bugs. The reason it happens is that copying a large object on every assignment would be ruinously slow, so languages copy the reference and let you ask for a real copy when you want one.

**This is independent of Axis 1.** In Python *everything* is technically a reference to an object, including integers — but integers are immutable (Axis 3), so the aliasing is impossible to observe and they behave exactly like value types. Two axes, one apparent contradiction, no actual conflict.

### Axis 3 — Mutable vs immutable

- **Mutable** — can be changed in place after creation: lists, dicts, sets, most objects.
- **Immutable** — cannot. Any "modification" builds a new value and rebinds the name.

```python
s = "hello"
s += " world"    # does NOT modify the original string —
                 # it builds a new one and points s at it
```

Immutability is why strings and tuples work as dictionary keys and lists don't: a key that could change after being stored would break the structure that indexed it. It's also why the string loop in [[foundations/dsa/04-data-structures/01-arrays|arrays]] is accidentally O(n²) — every `+=` copies the whole string.

**Immutable is not the same as "can't be reassigned."** A name pointing at an immutable value can be pointed somewhere else freely; what it can't do is change the value in place. `const`/`final` restrict the *name*; immutability restricts the *value*. A `const` list in JavaScript can still have items pushed onto it.

### Axis 4 — Static vs dynamic typing

*When* is the type settled and checked?

- **Static** (C, Java, Go, Rust, TypeScript) — at compile time. The **variable** has a type, fixed before the program runs.
- **Dynamic** (Python, JavaScript, Ruby) — at runtime. The **value** carries its type; a variable can hold an int now and a string later.

The tradeoff is a real engineering decision, not a matter of taste: static catches a whole class of errors before shipping and gives editors the information for reliable autocomplete and refactoring, at the cost of ceremony and some flexibility. Dynamic is faster to write and more flexible, and defers those errors to runtime — which means to your users, unless your tests find them first. It's a large part of why TypeScript exists, and why big Python codebases adopt type hints.

### Axis 5 — Strong vs weak typing

Whether the language silently coerces between types when they don't match.

- **Strong** (Python) — mismatched operations raise an error rather than guessing.
- **Weak** (JavaScript, C) — the language converts automatically and continues.

Note 05's `"5" + 3` producing `"53"` in JavaScript is exactly this axis. Python raises a `TypeError` on the same expression. Neither is a bug; they're different answers to "should I guess what the programmer meant?"

### The axes really are independent

The combination that surprises people:

| Language | Static/Dynamic | Strong/Weak |
|---|---|---|
| **Python** | Dynamic | Strong |
| **JavaScript** | Dynamic | Weak |
| **Java** | Static | Strong |
| **C** | Static | Weak — casts let you reinterpret almost anything |

"Dynamically typed" and "weakly typed" get used interchangeably in casual conversation and mean genuinely different things. Python is as dynamic as JavaScript and far stricter about coercion.

## Putting it together

| Type | Primitive/Composite | Value/Reference | Mutable/Immutable |
|---|---|---|---|
| `int` (Python) | Primitive | Reference, but immutable so it behaves like a value | Immutable |
| `str` (Python) | Composite — a sequence of chars | Reference, immutable | Immutable |
| `list` (Python) | Composite | Reference | **Mutable** |
| `dict` (Python) | Composite | Reference | **Mutable** |
| `int` (Java/C) | Primitive | **Value** — genuinely copied | n/a |
| `struct` (C) | Composite | **Value** — copied on assignment unless you use a pointer | Mutable |

Reading across a row is how you predict a type's behaviour without memorising rules per language.

## Gotchas

- **The mutable default argument trap.** In Python, `def f(items=[]):` creates that list **once**, at definition time, and shares it across every call that doesn't pass its own. The list accumulates across calls and it looks like the language is haunted. Default to `None` and build the object inside the function.
- **"Is Python pass-by-reference or pass-by-value?"** Neither, cleanly — it's *pass by object reference*. The reference is passed by value, so **reassigning** a parameter inside a function doesn't affect the caller, but **mutating** the object it points to does. Both halves surprise people, in opposite directions.
- **Immutability is shallow.** A tuple can't be modified, but a tuple *containing a list* has a list you can freely change. "Immutable" applies to one level.
- **Equality vs identity.** `==` asks "same value?", `is` (Python) / `==` on objects (Java) asks "same object?". Reference types make these come apart, and small-integer caching means `a is b` can be `True` for `256` and `False` for `257`. Compare values with `==` unless you specifically mean identity.
- **Fixed-width types overflow and floats approximate** — both covered in [[foundations/programming-fundamentals/05-variables-and-types|note 05]], and both are direct consequences of the bit-level story above rather than separate curiosities.

## Related
- [[foundations/programming-fundamentals/05-variables-and-types|variables and types]] — the working version of this; read that first
- [[foundations/programming-fundamentals/07-collections|collections]] — where mutable vs immutable starts to bite daily
- [[foundations/programming-fundamentals/13-objects-and-classes|objects and classes]] — composite types you define yourself
- [[foundations/computer-architecture/02-data-representation|data representation]] — two's complement and IEEE-754 in full
- [[foundations/dsa/04-data-structures/01-arrays|arrays]] — where fixed-size types turn into O(1) indexing
- [[foundations/dsa/04-data-structures/03-hash-maps|hash maps]] — why keys must be immutable
- [[languages/README|languages]] — how individual languages answer axes 4 and 5

*Source: [reference] — consolidated from the type notes that previously sat in `foundations/dsa/`, where they were prerequisites rather than DSA material.*
