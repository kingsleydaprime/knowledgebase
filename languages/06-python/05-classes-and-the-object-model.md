# Classes and the Object Model

> **[Intermediate]** · Dunder methods, properties, dataclasses, and why Python's OOP is a set of *protocols* rather than a set of *declarations*.

Python has classes, inheritance and polymorphism → [[foundations/programming-fundamentals/13-objects-and-classes|objects and classes]]. What makes it different from Java or C# is that **behaviour is opted into by implementing methods with specific names, not by declaring that you implement an interface.**

## The basics

```python
class Account:
    interest_rate = 0.02              # CLASS attribute — shared by all instances

    def __init__(self, owner, balance=0):
        self.owner = owner            # INSTANCE attributes
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    @classmethod
    def from_dict(cls, data):         # alternative constructor
        return cls(data["owner"], data["balance"])

    @staticmethod
    def validate(amount):             # namespaced function; no self/cls
        return amount > 0
```

**`self` is an ordinary parameter**, explicitly declared and explicitly passed by the interpreter. `account.deposit(50)` is sugar for `Account.deposit(account, 50)`. The explicitness is deliberate — *explicit is better than implicit*.

**The class-attribute trap**, which is the same mutable-default bug wearing a different hat:

```python
class Basket:
    items = []              # ✗ SHARED by every instance

    def add(self, item):
        self.items.append(item)     # mutates the class attribute
```

Put mutable state in `__init__`, always.

## Dunder methods — the protocols

Double-underscore methods hook your class into the language's syntax. **This is the core of Python's object model**: `len(x)` calls `x.__len__()`, `a + b` calls `a.__add__(b)`, `for i in x` calls `x.__iter__()`.

```python
class Money:
    def __init__(self, pence): self.pence = pence

    def __repr__(self):  return f"Money({self.pence})"      # for developers
    def __str__(self):   return f"£{self.pence / 100:.2f}"  # for users
    def __eq__(self, other): return self.pence == other.pence
    def __hash__(self):  return hash(self.pence)            # needed if __eq__ defined
    def __lt__(self, other): return self.pence < other.pence
    def __add__(self, other): return Money(self.pence + other.pence)
    def __len__(self): ...
    def __getitem__(self, key): ...        # enables x[key] AND iteration
    def __contains__(self, item): ...      # enables `in`
    def __call__(self, *args): ...         # makes the instance callable
```

**Always define `__repr__`.** It's what you see in the REPL, in a debugger, in a list, and in a log line. The default (`<__main__.Money object at 0x7f...>`) tells you nothing when you most need information.

**If you define `__eq__`, define `__hash__`** — otherwise Python sets `__hash__` to `None` and your objects can't go in sets or dict keys. Equal objects must hash equally.

**The consequence of protocols over declarations:** anything with `__iter__` is iterable, anything with `__len__` works with `len()`, and no base class or interface declaration is involved. This is **duck typing** with hooks, and it's why `collections.abc` types work with your classes without your classes knowing they exist.

## Properties

Computed attributes that look like plain ones:

```python
class Circle:
    def __init__(self, radius): self._radius = radius

    @property
    def radius(self): return self._radius

    @radius.setter
    def radius(self, value):
        if value <= 0: raise ValueError("radius must be positive")
        self._radius = value

    @property
    def area(self): return 3.14159 * self._radius ** 2      # read-only
```

```python
c.radius = 5      # runs the setter, validates
c.area            # computed; no parentheses
```

**This is why Python code doesn't have getters and setters everywhere.** In Java you write them upfront because turning a public field into a method later breaks callers. In Python you expose the attribute directly and *convert it to a property later if you ever need to* — the call sites don't change. Writing `get_radius()` in Python is importing a solution to a problem the language doesn't have.

## Privacy by convention

- `name` — public
- `_name` — internal. **Convention only**; nothing stops you, but you're on your own
- `__name` — name-mangled to `_ClassName__name`. Not privacy; it exists to stop subclasses *accidentally* colliding

Python's position is *we're all consenting adults here*. It trades enforcement for the ability to inspect and monkey-patch anything, which is why testing and debugging tools in Python can do things they can't elsewhere.

## Dataclasses

Most classes exist to hold data. `@dataclass` removes the boilerplate:

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float
    tags: list[str] = field(default_factory=list)    # ← NOT tags: list = []
```

You get `__init__`, `__repr__` and `__eq__` generated. Options worth knowing:

```python
@dataclass(frozen=True)    # immutable, and hashable — use this by default
@dataclass(slots=True)     # no __dict__: less memory, faster attribute access (3.10+)
@dataclass(kw_only=True)   # all fields keyword-only (3.10+)
```

**`field(default_factory=list)` is how you avoid the mutable-default bug** — the dataclass machinery calls the factory per instance. A bare `= []` is a runtime error, which is a rare case of Python protecting you from that mistake.

The alternatives: **`NamedTuple`** for immutable positional records, and **`pydantic`** when the data comes from *outside* your program and needs validating and parsing → [[backend/frameworks/python/01-fastapi/README|FastAPI]] is built on it.

## Inheritance and the MRO

Python has multiple inheritance, resolved by the **C3 linearisation** — the method resolution order:

```python
class C(A, B): ...
C.__mro__          # the exact order attribute lookup follows
```

`super()` doesn't mean "my parent" — it means **"the next class in the MRO"**, which in multiple inheritance is not necessarily a parent at all. Always call `super().__init__()` in a class designed to be inherited from.

**Prefer composition** → [[foundations/programming-fundamentals/13-objects-and-classes|note 13]]. Where you do want a contract, use `abc`:

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, data): ...       # subclass must implement or can't instantiate
```

Or, better for duck-typed code, a **`Protocol`** — structural typing, no inheritance required → [[languages/06-python/08-typing-and-type-hints|note 08]].

## Related
- [[languages/06-python/08-typing-and-type-hints|typing]] — Protocols and generics
- [[languages/06-python/07-decorators-and-context-managers|decorators]] — `@property` is one
- [[foundations/programming-fundamentals/13-objects-and-classes|objects and classes]] — the concepts, language-agnostic
- [[concepts/03-design-patterns/README|design patterns]] — many of which Python makes trivial or unnecessary

*Source: [reference] — from the Python data model documentation.*
