# Functions

> **[Beginner]** · Naming a sequence of steps — the single most important idea in this course, and the one everything above it is built from.

A **function** is a named block of code you can run by writing its name. Everything else here is detail.

```python
def greet():
    print("Hello!")
    print("Welcome.")

greet()          # runs both lines
greet()          # again
```

You've already been using them. `print()` is a function. So is `len()`, `max()`, `append()`. Somebody wrote the code that turns a value into characters on your screen, and you get to write six letters instead.

**That's the entire idea: wrap up a piece of work, give it a name, and from then on think about the name instead of the work.**

## Why they matter more than they look

**Removing repetition.** If the same six lines appear in four places and the logic changes, you must find and fix four copies — and you will miss one. As a function, you change it once. This is **DRY** (Don't Repeat Yourself), and it's about *maintenance*, not typing.

**Naming intent.** `calculateTax(amount)` says what's happening. Eight lines of inline arithmetic makes the reader work it out, every time they pass.

**Making things testable.** A function with inputs and an output can be checked in isolation, which is what makes [[concepts/04-best-practices/04-testing-fundamentals|automated tests]] possible at all.

**Shrinking what you hold in your head.** This is the real one. Once `calculateTax` is written and works, you stop thinking about tax calculation and think about `calculateTax`. **The point of a function is to let you forget its contents** — and that forgetting is what allows a program larger than the few dozen lines a person can hold at once.

## Parameters and arguments

A function that always does exactly one thing is limited. **Parameters** let you pass data in:

```python
def greet(name):              # name is a PARAMETER
    print("Hello, " + name)

greet("Kingsley")             # "Kingsley" is an ARGUMENT
greet("Ada")
```

The terms: **parameter** is the placeholder in the definition, **argument** is the actual value passed. People use them interchangeably and it rarely matters.

Multiple parameters are positional by default — **order is the contract**:

```python
def create_user(name, email, age):
    ...

create_user("Ada", "ada@example.com", 36)      # order matters
create_user(email="ada@example.com", name="Ada", age=36)   # named: clearer, order-free
```

**Named arguments are worth using once you have three or more parameters.** `place_order(42, true, false, 3)` at the call site is unreadable — you have to open the definition to know what those mean.

Many languages support **default values**:

```python
def greet(name, greeting="Hello"):
    print(greeting + ", " + name)

greet("Ada")                    # Hello, Ada
greet("Ada", "Good morning")    # Good morning, Ada
```

## Return values

A function can hand a value back:

```python
def add(a, b):
    return a + b

result = add(3, 4)      # result is 7
```

`return` does two things: it **produces the value**, and it **exits the function immediately** — code after it doesn't run.

**Functions that return and functions that don't** are the fundamental split:

- **Returns a value** — `add`, `max`, `len`. You *use* the result: assign it, print it, pass it on
- **Returns nothing** (`void`, `None`, procedure) — `print`, `save_to_file`. You call it *for what it does*, not what it gives back

**The beginner mistake is calling a returning function and ignoring the result:**

```python
add(3, 4)                 # computed 7, discarded it, changed nothing
result = add(3, 4)        # ✓
```

This bites especially with strings and other immutable values: `text.upper()` **returns** an uppercased copy and leaves `text` untouched. `text = text.upper()` is what you meant.

**Every path must return.** If a function is declared to return a value, an `if` with no `else` can fall off the end and return nothing — which becomes a `null` somewhere else entirely, far from the cause. Most compilers and editors will warn you; take the warning seriously.

## What makes a good function

**Do one thing.** If you need "and" to describe it — *"it validates the input and saves it and sends an email"* — that's three functions. The test isn't line count; it's whether the name honestly covers everything inside.

**Name it as a verb.** `calculateTotal`, `sendEmail`, `isValid`. It's an action.

**Keep the parameter list short.** Beyond three or four, pass an object or split the function. A six-parameter function is usually two functions in a trenchcoat.

**Prefer returning over mutating.** A function that takes inputs and returns an output, changing nothing else, is trivially understandable and trivially testable. One that quietly modifies a global or its own arguments is neither.

That last property has a name — a **pure** function: same inputs, same output, no side effects. Not everything can be pure (something has to write the file), but **pushing the pure logic apart from the effects is one of the highest-return structural habits there is**. It's the core of [[concepts/03-design-patterns/README|a lot of design]] and the whole premise of functional programming.

**Watch the sharing trap.** Passing a list or object into a function passes a *reference* → [[foundations/programming-fundamentals/05-variables-and-types|note 05]]. Modifying it inside changes the caller's copy. Sometimes intended; frequently a surprise.

## Using other people's functions

You will write a small fraction of the code you use. The rest comes from **libraries** — collections of functions someone else wrote, tested, and maintains.

```python
import math
print(math.sqrt(16))            # 4.0

from math import sqrt           # import just the one
print(sqrt(16))
```

The vocabulary varies (module, package, library, crate, gem) but the shape is constant: **something is fetched, something is imported, then you call it.**

Beyond the standard library, a **package manager** fetches third-party code — `pip`, `npm`, `cargo`, `go get`, Maven. Two things to establish as habits immediately:

**Check before you write.** Date parsing, HTTP requests, CSV reading, JSON — all solved, thoroughly, by people who handled the edge cases you haven't thought of.

**Adding a dependency is a decision, not a free action.** You inherit its bugs, its security vulnerabilities, its maintenance status and its own dependencies. A three-line utility is not worth a package; an HTTP client absolutely is. This is what [[devops/12-sre-and-platform-engineering/04-devsecops|dependency scanning]] exists for, and why "most of your code is code you didn't write" is a security statement.

## Scope, and closures in one paragraph

Variables created inside a function are **local** — they exist while it runs and vanish after. That isolation is most of why functions are safe to reason about: a local can't be changed by anything outside → [[foundations/programming-fundamentals/05-variables-and-types|note 05]].

A function *can* usually see variables from the scope enclosing it, and in many languages it can **capture** them and keep them alive after that scope has ended. That's a **closure** — a function bundled with the environment it was created in. You don't need it yet; you'll meet it the first time a callback behaves strangely, and it'll make sense then.

## Related
- [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|recursion]] — functions calling themselves, and how calls actually work
- [[foundations/programming-fundamentals/11-planning-before-you-type|planning]] — deciding what your functions should be
- [[concepts/04-best-practices/04-testing-fundamentals|testing]] — what functions make possible
- [[concepts/04-best-practices/05-solid-principles|SOLID]] — "do one thing", scaled up
- [[foundations/software-engineering/01-what-software-engineering-is|abstraction]] — the habit this note is an instance of

*Source: [reference] — from the freeCodeCamp Introduction to Programming course, extended with purity, dependency judgement and closures.*
