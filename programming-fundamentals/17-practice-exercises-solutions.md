# Practice Exercises — Solutions

> **[Beginner]** · Worked answers to [[foundations/programming-fundamentals/16-practice-exercises|note 16]]. **Try each first.**

These explain *why*, not just *what*. Where an exercise has no single right answer, the solution says so and gives you the thing to judge against instead.

Code is Python for brevity. The reasoning is language-independent.

---

## Part A — The model

### 1. Be the compiler for a person

The two failures nearly everyone hits:

**Empty list.** "Take the first number" has no answer. You must *decide*: return nothing, return an error, or refuse the input. There's no default — that's the lesson.

**All-negatives.** The instinctive opening is *"start with largest = 0"*, which returns `0` for `[-5, -2]` — a number that isn't in the list. **Start with the first element instead**, which forces you to handle the empty case explicitly and is why the two failures are really one.

```
1. If the list is empty, report "no values" and stop.
2. Let `largest` be the FIRST item.
3. For each remaining item:
      if item > largest, set largest = item
4. Report largest.
```

The general move: **make every implicit step explicit, and every "obviously" is a step you skipped.**

### 2. One program, three languages

What differs: type declarations (Java yes, Python no), statement terminators, block delimiters (braces vs indentation), print syntax, entry point (Java needs `main`, Python doesn't).

What doesn't: read input → convert to a number → test remainder against zero → branch → output. **That's the program**, and it's identical everywhere.

If the third language took much longer than the second, it was probably the *toolchain*, not the language — which is its own useful finding.

### 3. Break it four ways

| Break | Typical message | Line reported |
|---|---|---|
| Missing `)` | `SyntaxError: unexpected EOF` / `'(' was never closed` | **Often the line after, or the last line of the file** |
| Misspelled name | `NameError: name 'x' is not defined` | Correct line — **and only at runtime** |
| Missing quote | `SyntaxError: unterminated string literal` | Correct line, usually |
| Missing `:` | `SyntaxError: expected ':'` | Correct line |

**The unclosed bracket is the one that misreports**, and the reason is mechanical: the parser doesn't know you *meant* to close it. It keeps consuming tokens as part of the unfinished expression until it meets something that cannot possibly continue — which may be lines later. **So when a syntax error points at a line that looks fine, look up.**

The misspelled name is different in kind: it's not a syntax error at all. The program is grammatically valid, so it runs until execution reaches that line. In a compiled or statically typed language it would have been caught before running — that's the trade in [[foundations/programming-fundamentals/02-languages-and-the-translation-problem|note 02]].

### 4. Check five things

| | Answer | The surprise |
|---|---|---|
| `"hello"[1:3]` | `"el"` | End index **excluded** |
| `7 / 2` | `3.5` in Python; **`3` in Java/C/Go** | Integer division truncates in most languages |
| `[1,2,3][5]` | `IndexError` | In **C**, no error — you read whatever memory is there |
| `if []:` | falsy | Empty collections are false |
| `0.1 + 0.2` | `0.30000000000000004` | Not equal to `0.3` |

**The point isn't the answers — it's that checking took ninety seconds.** Each of these has cost somebody a debugging session.

---

## Part B — The building blocks

### 5. Make a variable change without touching it

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)            # [1, 2, 3, 4]   ← changed

x = 5
y = x
y += 1
print(x)            # 5              ← unchanged

c = a.copy()        # or list(a) / a[:]
c.append(9)
print(a)            # unaffected ✓

nested = [[1, 2], [3, 4]]
shallow = nested.copy()
shallow[0].append(99)
print(nested)       # [[1, 2, 99], [3, 4]]  ← the fix FAILED
```

**The one rule: assignment binds a name to an object; it never copies.** You notice only when the object is mutable.

The shallow copy makes a new *outer* list holding **the same inner objects**. Fix with `copy.deepcopy()`, and understand that deep copying is expensive and can't handle everything — which is why immutability is preferred where possible.

### 6. Lose money to a float

```python
0.10 + 0.20 == 0.30        # False
sum([0.10] * 100)          # 9.999999999999998
```

Binary floating point cannot represent 0.1 exactly, any more than decimal can represent ⅓. Each addition compounds a tiny error.

**The correct fix — integer minor units:**

```python
total_pence = 0
for _ in range(100):
    total_pence += 10          # exact integer arithmetic
print(f"£{total_pence / 100:.2f}")     # £10.00 — convert only to DISPLAY
```

Or `decimal.Decimal("0.10")`, which is slower but exact for decimal fractions.

**Why rounding at the end is not the fix:** it hides this instance and leaves the class of bug in place. With enough operations the error exceeds your rounding precision, and you get a discrepancy nobody can reproduce. Financial systems use integers or decimals for exactly this reason → [[foundations/numerical-methods/02-floating-point-and-error|floating point]].

### 7. FizzBuzz, then FizzBuzz differently

```python
# version 1
for n in range(1, 101):
    if n % 15 == 0:   print("FizzBuzz")
    elif n % 3 == 0:  print("Fizz")
    elif n % 5 == 0:  print("Buzz")
    else:             print(n)
```

Note `% 15` must come **first** — order matters in an `elif` chain → [[foundations/programming-fundamentals/06-control-flow|note 06]].

```python
# version 2 — rules as data
RULES = [(3, "Fizz"), (5, "Buzz")]          # add (7, "Bazz") — done

for n in range(1, 101):
    out = "".join(word for divisor, word in RULES if n % divisor == 0)
    print(out or n)
```

**Why this matters more than it looks:** version 1 needs a new branch *and* a new combined case for every rule added — 4 rules means 15 combinations. Version 2 needs one tuple. **The combinatorial explosion vanishes because the rules became data instead of control flow**, and `"".join(...)` handles combinations for free.

This is the same instinct as configuration over code, [[foundations/programming-fundamentals/14-programming-paradigms|declarative over imperative]], and data-driven design in [[game-development/07-tools-and-production|games]].

### 8. Earn the four orders of magnitude

```python
import random, string, time

names = ["".join(random.choices(string.ascii_lowercase, k=8)) for _ in range(20_000)]
lookups = random.choices(names, k=5_000)

t = time.perf_counter()
for n in lookups: n in names              # list — O(n) scan
list_time = time.perf_counter() - t

name_set = set(names)
t = time.perf_counter()
for n in lookups: n in name_set           # set — O(1) hash
set_time = time.perf_counter() - t

print(f"list {list_time:.4f}s   set {set_time:.6f}s   ratio {list_time/set_time:.0f}x")
```

Typical: **500–2000×**. The list scans on average 10,000 entries per lookup; the set hashes once and jumps.

**The exact ratio doesn't matter — the shape does.** The list's cost grows with the collection; the set's doesn't. Double the data and the gap doubles → [[foundations/dsa/README|DSA]].

### 9. Refactor until each does one thing

```python
def parse_line(line):        # "ada,90" -> ("ada", 90) or None
def read_scores(path):       # path -> {name: [scores]}
def average(scores):         # [90, 80] -> 85.0
def grade(avg):              # 85.0 -> "B"
def format_report(rows):     # rows -> str
def main(path):              # wires them together
```

**The test that matters: `grade(85.0)` is now testable with no file, no I/O and no setup.** In the 40-line version, testing the grade boundaries required a file on disk. That's the practical payoff — not aesthetics.

Note `main` is the only function that knows about all the others, and the only one with side effects. **Pure logic in the middle, effects at the edge** → [[foundations/programming-fundamentals/14-programming-paradigms|note 14]].

### 10. Hunt the off-by-one

```python
def last_n(items, n):
    if n <= 0:
        return []                    # a DECISION, not an accident
    return items[-n:]
```

Behaviour: `n=0` → `[]`; `n=1` → last item; `n=len` → everything; `n>len` → everything (no error); empty list → `[]`.

**The trap:** without the guard, `items[-0:]` is `items[0:]` — **the whole list**, because `-0 == 0`. So `last_n(x, 0)` silently returns everything. No error, wrong answer: a [[foundations/programming-fundamentals/10-errors-and-debugging|logic error]], the expensive kind.

Returning everything for `n > len` is defensible; raising is also defensible. **Deciding is the exercise.**

---

## Part C — Depth

### 11. Overflow the stack

`factorial(100_000)` → `RecursionError: maximum recursion depth exceeded`.

**What ran out: stack frames**, not memory generally. Each call pushes a frame holding `n` and a return address; 100,000 nested calls exceed the limit (~1,000 in Python by default) → [[foundations/programming-fundamentals/09-recursion-and-the-call-stack|note 09]].

```python
def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

The loop reuses **one** frame. Nothing accumulates.

Note `factorial(100)` works fine recursively and produces a 158-digit number — Python integers grow arbitrarily. In Java or C that would have overflowed silently long before.

### 12. Make exponential linear

```python
from functools import cache

@cache
def fib(n):
    return n if n <= 1 else fib(n-1) + fib(n-2)
```

Naive `fib(30)` ≈ 0.3–1 s and makes **1.3 million calls**. Cached: microseconds. `fib(100)` is instant cached and would take longer than the universe naively.

`fib(25)` is computed **75,025 times** in the naive version — once for each path that reaches it. That redundancy *is* the exponential.

**Two cautions:** arguments must be hashable, and an unbounded cache on a long-running process is a memory leak — `@lru_cache(maxsize=...)` when the input space is large.

### 13. Find a bug by bisection

A good log looks like:

```
1. Output wrong (total 340, expected 285). Bug is somewhere in 100 lines.
2. HYPOTHESIS: data is correct on load. Print after read_scores → correct. ✓ (bug is downstream)
3. HYPOTHESIS: averages correct. Print averages → "ada": 113.3 WRONG.  (bug is in read_scores..average)
4. Print raw scores for ada → [90, 80, 170]. 170 isn't in the file.
5. HYPOTHESIS: parse_line mis-splits. Check line 3 → "ada,80,90" — three fields.
6. FOUND: parse_line assumes exactly 2 fields, silently concatenates.
```

**Six checks for 100 lines.** Each halves the space and each tests one stated belief.

Reading top-to-bottom is O(n) and re-reads code you already believe. Bisection is O(log n) and **doesn't care how well you understand the code** — which is why it works on someone else's codebase → [[git/09-investigating-history|git bisect]] is the same algorithm over commits.

### 14. Plan first

No single answer; the number is the finding.

**Typical result: 1–2 restructures when planned, 4–8 when not.** The unplanned version usually discovers the PIN-attempt counter needs to live outside the loop *after* writing the loop, and that quitting needs to break out of two levels.

**If planning made no difference, the problem was too small** — which is also a valid finding, and exactly what [[foundations/programming-fundamentals/11-planning-before-you-type|note 11]] says about calibration. Try it again on something with 5+ branches.

### 15. Model something with invariants

```python
class BankAccount:
    def __init__(self, owner, opening=0):
        if opening < 0:
            raise ValueError("opening balance cannot be negative")
        self._owner = owner
        self._balance = opening

    @property
    def balance(self):              # read-only: no setter
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
```

**In Python you can still break it:** `acct._balance = -500` works. The underscore is convention, not enforcement.

**That's the honest answer to the exercise.** Python trades enforcement for introspectability. Java's `private` genuinely prevents it; Rust's ownership and visibility rules do too. Knowing *which* your language gives you is the point — and in Python the defence is that `_balance` announces intent, and code reviews and linters enforce it socially rather than mechanically → [[foundations/programming-fundamentals/13-objects-and-classes|note 13]].

### 16. The same problem, two paradigms

```python
# imperative
totals = {}
for order in orders:
    totals[order["customer"]] = totals.get(order["customer"], 0) + order["value"]

# declarative
from itertools import groupby
totals = {c: sum(o["value"] for o in g)
          for c, g in groupby(sorted(orders, key=lambda o: o["customer"]),
                              key=lambda o: o["customer"])}
```

**No correct answer, and anyone who tells you otherwise is selling something.**

Arguments for imperative: obvious, debuggable line by line, one pass, no sort required, and a junior reads it instantly.
Arguments for declarative: no mutable accumulator, expresses *what* rather than *how*, composes into a pipeline.

**Here the imperative version is genuinely better** — `groupby` needs pre-sorted input (a real trap → [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]]), which adds an O(n log n) sort for no benefit. A `defaultdict(int)` version is cleaner still.

**The lesson isn't "declarative good".** It's that you should be able to write both and pick deliberately → [[foundations/programming-fundamentals/14-programming-paradigms|note 14]].

## Related
- [[foundations/programming-fundamentals/16-practice-exercises|the exercises]]
- [[foundations/programming-fundamentals/README|the course]]

*Source: [reference] — written Aug 2026.*
