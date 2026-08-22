# Typing and Type Hints

> **[Intermediate]** · Gradual typing — optional, unenforced at runtime, and the single biggest quality change available to a Python codebase over about a thousand lines.

Python is dynamically typed, and past a certain size that stops being purely a benefit. Type hints (PEP 484, Python 3.5+) let you annotate without giving up the dynamism.

```python
def calculate_tax(amount: float, rate: float = 0.2) -> float:
    return amount * rate
```

**The interpreter ignores these completely.** `calculate_tax("100", 0.2)` runs and produces `"100100..."`. Annotations exist for **static checkers, editors and readers**.

That's a genuine design choice rather than a half-measure: adoption is incremental, so you can annotate the parts that benefit and leave a script alone.

## The syntax

```python
from typing import Optional, Union, Any, Callable, TypeVar, Protocol

x: int = 5
names: list[str] = []                    # 3.9+: built-ins are generic
lookup: dict[str, int] = {}
pair: tuple[int, str] = (1, "a")
maybe: str | None = None                 # 3.10+: replaces Optional[str]
either: int | str = 5                    # 3.10+: replaces Union[int, str]
handler: Callable[[int, str], bool] = f  # takes (int, str), returns bool
```

Older code uses `List[str]`, `Dict[str, int]`, `Optional[X]` and `Union[A, B]` from `typing`. **Prefer the modern spellings** — `list[str]`, `X | None` — unless you support Python < 3.10.

**`Optional[X]` means `X | None`, not "optional argument".** A parameter with a default is optional; one annotated `Optional` may be `None`. They're independent, and conflating them is the most common misreading of a signature.

## Why it pays

**It catches a real class of bug before running.** The most valuable is `None`:

```python
def find_user(id: int) -> User | None: ...

user = find_user(5)
print(user.name)          # mypy: Item "None" of "User | None" has no attribute "name"
```

That's the null-dereference bug, caught statically, in a dynamic language. In an untyped codebase it's found in production.

**Editor support transforms.** Autocomplete, go-to-definition and rename stop being guesses.

**They're documentation that can't rot**, because CI checks them.

**And they're how you read unfamiliar code fast.** A signature tells you what goes in and out without reading the body.

## The checkers

```bash
pip install mypy && mypy src/           # the reference implementation
pip install pyright                     # Microsoft's; powers VS Code's Pylance, faster
```

**How to adopt on an existing codebase** — the strategy matters more than the tool:

1. Start with `mypy` on **one module**, not the repo
2. Run in **non-strict** mode; unannotated code is simply skipped
3. Annotate **new code and anything you touch**
4. Turn on `disallow_untyped_defs` per-module as each becomes clean
5. Add it to [[devops/06-ci-cd/README|CI]] once it passes

**Do not turn on strict mode across a large untyped codebase.** You get thousands of errors, nobody triages them, and the tool gets removed — the same alert-fatigue failure as everywhere else → [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]].

## The features worth knowing

**`TypeVar` and generics** — relate types to each other:

```python
def first(items: list[T]) -> T: ...      # returns the SAME type it contains

# 3.12+ has cleaner syntax:
def first[T](items: list[T]) -> T: ...
```

**`Protocol` — structural typing, and the one that fits Python best:**

```python
class Closeable(Protocol):
    def close(self) -> None: ...

def cleanup(resource: Closeable) -> None:
    resource.close()
```

**Anything with a `close()` method satisfies this** — no inheritance, no registration. It's duck typing made checkable, and it's the right tool when you'd otherwise force an ABC on classes you don't own.

**`Literal`, `TypedDict`, `Final`, `NewType`:**

```python
def move(direction: Literal["up", "down"]) -> None: ...   # only these strings

class UserDict(TypedDict):        # a dict with known keys — great for JSON
    name: str
    age: int

MAX: Final = 100                  # reassignment is an error
UserId = NewType("UserId", int)   # an int you can't accidentally pass a plain int to
```

**`Any` disables checking** for that value and spreads silently through your code. Use `object` when you mean "anything" and want to be forced to narrow it.

## Narrowing

Checkers follow control flow, which is what makes `| None` ergonomic rather than annoying:

```python
def process(value: str | None) -> str:
    if value is None:
        return "default"
    return value.upper()          # here, the checker knows it's str
```

`isinstance()`, `is None`, truthiness checks and `assert` all narrow. **This is why `if x is None: return` early is better style than a big `else` block** — it narrows for the rest of the function.

## The honest limits

- **No runtime enforcement.** Data from an API, a file or a form is unchecked, whatever you annotated. Validate at the boundary — `pydantic` does this, and it's why FastAPI is built on it → [[backend/frameworks/python/01-fastapi/README|FastAPI]]
- **Dynamic idioms resist typing.** Heavy `getattr`, monkey-patching and metaclasses fight the checker
- **Third-party stubs vary.** Some libraries ship types; others need `types-requests`-style stub packages; some have nothing
- **Annotations can be wrong.** They're checked against each other, not against reality

**Where the value is:** libraries, shared modules, anything a team touches, anything long-lived. **Where it isn't:** a 40-line script.

## Related
- [[languages/06-python/05-classes-and-the-object-model|classes]] — Protocol vs ABC
- [[languages/06-python/13-testing-and-tooling|testing and tooling]] — mypy in CI
- [[foundations/programming-language-theory/04-type-systems-formally|type systems]] — the theory
- [[languages/03-rust/README|Rust]] — the other end of the spectrum

*Source: [reference] — from PEP 484 and successors, and the mypy documentation.*
